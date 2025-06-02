from fastapi import WebSocket, WebSocketDisconnect
from models.classification import Classification
from classification.services.connection_manager import ConnectionManager
import cv2
import asyncio
import numpy as np
from classification.services.sorter import ClassificationService
from sessions.service import get_session
from datetime import datetime
from config import settings

manager = ConnectionManager()  

async def sorter_socket(
    websocket: WebSocket,
    session_id: str,
    classifier: ClassificationService,
    db,
):
    """WebSocket endpoint for real-time classification"""
    
    # Validate session exists and is active
    session = await get_session(db, session_id)
    if not session:
        await manager.close_connection(websocket, code=1008, reason="Session not found")
        return
    if session.status != "active":
        await manager.close_connection(websocket, code=1008, reason="Session is not active")
        return
    
    try:  
        # Connect with session metadata
        await manager.connect(websocket, metadata={
            "session_id": session_id,
            "seed_lot": session.seed_lot,
            "status": session.status
        })
        
        stream = stream_processing(classifier=classifier)
        async for results in stream:
            if not results:
                continue
                
            try:
                # Handle both single result and list of results
                if isinstance(results, list):
                    for result in results:
                        try:
                            # Convert Pydantic model to dict for JSON serialization
                            data = result.model_dump()
                            await manager.send_json(websocket, data)
                            
                            # Create SQLAlchemy model instance
                            db_classification = Classification(
                                seed_id=data["seed_id"],
                                classify=data["classification"],
                                is_sampled=data["is_sampled"],
                                image_path=data["image_path"],
                                session_id=session_id,
                                timestamp=datetime.now()
                            )
                            db.add(db_classification)
                        except WebSocketDisconnect:
                            print("Client disconnected during result processing")
                            raise
                        except Exception as e:
                            print(f"Error processing single result: {str(e)}")
                            continue
                else:
                    try:
                        # Convert Pydantic model to dict for JSON serialization
                        data = results.model_dump()
                        await manager.send_json(websocket, data)
                        
                        # Create SQLAlchemy model instance
                        db_classification = Classification(
                            seed_id=data["seed_id"],
                            classify=data["classification"],
                            is_sampled=data["is_sampled"],
                            image_path=data["image_path"],
                            session_id=session_id,
                            timestamp=datetime.now()
                        )
                        db.add(db_classification)
                    except WebSocketDisconnect:
                        print("Client disconnected during result processing")
                        raise
                    except Exception as e:
                        print(f"Error processing single result: {str(e)}")
                        continue
                
                try:
                    await db.commit()
                except Exception as e:
                    print(f"Error committing to database: {str(e)}")
                    await db.rollback()
                    continue
                    
            except WebSocketDisconnect:
                print("Client disconnected")
                break
            except Exception as e:
                print(f"Error processing results: {str(e)}")
                continue
        
    except WebSocketDisconnect:                                                   
        print("Client disconnected normally")
    except Exception as e:
        print(f"Error in sorter_socket: {str(e)}")
    finally:
        # Ensure we clean up properly
        await manager.close_connection(websocket)

def create_mock_frame():
    """Create a mock frame for testing"""
    # Create a frame with configured dimensions
    frame = np.zeros((settings.CAMERA_HEIGHT, settings.CAMERA_WIDTH, 3), dtype=np.uint8)
    for i in range(settings.CAMERA_HEIGHT):
        frame[i, :, 0] = int(255 * i / settings.CAMERA_HEIGHT)  # Red gradient
        frame[i, :, 1] = int(255 * (settings.CAMERA_HEIGHT - i) / settings.CAMERA_HEIGHT)  # Green gradient
        frame[i, :, 2] = 128  # Constant blue
    return frame

async def stream_processing(classifier: ClassificationService): 
    """Capture video stream from webcam and process frames for classification"""
    
    if settings.USE_MOCK_CAMERA:
        print("Using mock camera")
        while True:
            # Create a mock frame
            frame = create_mock_frame()
            _, buffer = cv2.imencode('.jpg', frame)
            await manager.broadcast_bytes(buffer.tobytes())
            await asyncio.sleep(1.0 / settings.CAMERA_FPS)  # Control FPS
            results = classifier.process_image(buffer.tobytes())
            yield results
    else:
        # Get camera device from environment variable
        camera_device = settings.CAMERA_DEVICE
        try:
            # Try to convert to integer if it's a number
            camera_index = int(camera_device)
            # On macOS, we use the default backend which will use AVFoundation
            cap = cv2.VideoCapture(camera_index)
        except ValueError:
            # If it's not a number, use it as a device path
            camera_index = camera_device
            cap = cv2.VideoCapture(camera_index)

        try:
            if not cap.isOpened():
                raise Exception(f"Failed to open camera at {camera_device}")
                
            # Set camera properties
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.CAMERA_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.CAMERA_HEIGHT)
            cap.set(cv2.CAP_PROP_FPS, settings.CAMERA_FPS)
                
            while True:                                                  
                ret, frame = cap.read()                                  
                if not ret:                                              
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)                  
                    continue                                             
                _, buffer = cv2.imencode('.jpg', frame)                  
                await manager.broadcast_bytes(buffer.tobytes())
                await asyncio.sleep(1.0 / settings.CAMERA_FPS)  # Control FPS
                results = classifier.process_image(buffer.tobytes())
                yield results     
                
        except Exception as e:
            cap.release()  # Release the camera resource
            raise Exception(f"Stream processing failed: {str(e)}")  # This will break the application
        finally:
            if cap.isOpened():
                cap.release()  # Ensure camera is released even if an error occurs
        
    
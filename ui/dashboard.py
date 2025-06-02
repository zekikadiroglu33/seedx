import streamlit as st
import requests
import matplotlib.pyplot as plt
import json
import asyncio
import websockets
import cv2
import numpy as np
from PIL import Image
import aiohttp
import asyncio
import os

# Get backend URLs from environment variables
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BASE_API_URL = f"{BACKEND_URL}/seedx"
WS_URL = f"ws://{BACKEND_URL.split('://')[1]}/seedx/classification"

async def create_session(seed_lot):
    """Create a new session and return the session ID"""
    response = requests.post(f"{BASE_API_URL}/session/start", json={"seed_lot": seed_lot})
    if response.status_code == 200:
        session_id = response.json()['id']
        st.success(f"Session created: {session_id}")
        return session_id
    else:
        st.error("Failed to create session")
        return None

async def stop_session(session_id):
    """Stop the current session and return the session data"""
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_API_URL}/session/{session_id}/stop") as response:
            if response.status == 200:
                return await response.json()
            else:
                st.error("Failed to stop session")
                return None

async def get_session_stats(session_id):
    """Get statistics for the current session"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_API_URL}/stats/{session_id}") as response:
            if response.status == 200:
                return await response.json()
            else:
                st.error("Failed to get session statistics")
                return None

async def display_session_stats(stats):
    """Display session statistics and charts"""
    if not stats:
        return

    st.header("Final Session Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Seeds", stats["total"])
        st.metric("Accepted Seeds", stats["accepted"])
        st.metric("Rejected Seeds", stats["rejected"])
        st.metric("Sampled Seeds", stats["sampled"])
    
    with col2:
        
        fig, ax = plt.subplots(figsize=(2, 2))  
        ax.pie([stats["accepted"], stats["rejected"]], 
            labels=["Accepted", "Rejected"], 
            autopct="%1.1f%%")
        st.pyplot(fig)

async def display_sampled_images(sampled_data):
    """Display sampled images from the session"""
    if not sampled_data:
        return
    print(f"Sampled data: {sampled_data}")
    st.header("Session Sampled Images")
    
    # Display accepted seeds
    if sampled_data.get("accepted"):
        st.subheader("Accepted Seeds")
        cols = st.columns(5)
        for idx, sample in enumerate(sampled_data["accepted"]):
            with cols[idx % 5]:
                try:
                    # Convert base64 to image
                    import base64
                    from io import BytesIO
                    image_data = base64.b64decode(sample["image"])
                    image = Image.open(BytesIO(image_data))
                    st.image(image, caption=f"Seed {sample['seed_id']}")
                except Exception as e:
                    st.error(f"Error displaying accepted seed {sample.get('seed_id', 'unknown')}: {str(e)}")
    
    # Display rejected seeds
    if sampled_data.get("rejected"):
        st.subheader("Rejected Seeds")
        cols = st.columns(5)
        for idx, sample in enumerate(sampled_data["rejected"]):
            with cols[idx % 5]:
                try:
                    # Convert base64 to image
                    import base64
                    from io import BytesIO
                    image_data = base64.b64decode(sample["image"])
                    image = Image.open(BytesIO(image_data))
                    st.image(image, caption=f"Seed {sample['seed_id']}")
                except Exception as e:
                    st.error(f"Error displaying rejected seed {sample.get('seed_id', 'unknown')}: {str(e)}")

async def stream_camera(stframe, session_id):
    """Stream camera feed and handle classification"""
    try:
        async with websockets.connect(f"{WS_URL}/{session_id}/classify") as websocket:
            st.success("Camera stream connected")
            while st.session_state.get('camera_active', False):
                try:
                    data = await websocket.recv()
                    
                    # Handle string data (JSON)
                    if isinstance(data, str):
                        try:
                            result = json.loads(data)
                            if "image" in result:
                                # If the image is base64 encoded
                                import base64
                                image_bytes = base64.b64decode(result["image"])
                                nparr = np.frombuffer(image_bytes, np.uint8)
                                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                                stframe.image(img)
                            continue
                        except json.JSONDecodeError:
                            st.error("Received invalid JSON data")
                            continue
                    
                    # Handle bytes data
                    elif isinstance(data, bytes):
                        nparr = np.frombuffer(data, np.uint8)
                        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        stframe.image(img)
                    else:
                        st.error(f"Unexpected data type: {type(data)}")
                        continue
                        
                except websockets.exceptions.ConnectionClosed:
                    st.warning("Connection lost")
                    break
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")
                    break
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
    
    st.warning("Camera stream stopped")
    st.session_state.camera_active = False

async def show_dashboard():
    st.title("Seed-X Sorting Machine Dashboard")
    
    # Sidebar for session management
    with st.sidebar:
        st.header("Session Management")
        seed_lot = st.text_input("Seed Lot ID")
        
        # Session creation
        if st.button("Create New Session"):
            session_id = await create_session(seed_lot)
            if session_id:
                st.session_state.current_session = session_id
        
        # Camera control
        if 'current_session' in st.session_state:
            st.subheader("Camera Control")
            if not st.session_state.get('camera_active', False):
                if st.button("Start Camera"):
                    st.session_state.camera_active = True
                    st.success("Camera started")
            else:
                if st.button("Stop Camera"):
                    st.session_state.camera_active = False
                    st.warning("Camera stopped")
            
            # Session control
            st.subheader("Session Control")
            if st.button("Stop Current Session"):
                st.session_state.camera_active = False  # Stop camera first
                session_data = await stop_session(st.session_state.current_session)
                
                if session_data:
                    # Get and display session statistics
                    stats = await get_session_stats(st.session_state.current_session)
                    await display_session_stats(stats)
                    del st.session_state.current_session

    # Main content area
    if 'current_session' in st.session_state:
        # Real-time classification view
        st.header("Real-time Classification")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            stframe = st.empty()
            if st.session_state.get('camera_active', False):
                await stream_camera(stframe, st.session_state.current_session)
            else:
                st.info("Click 'Start Camera' in the sidebar to begin streaming")
        
        with col2:
            st.subheader("Classification Result")
            result_placeholder = st.empty()
            if st.session_state.get('camera_active', False):
                async with websockets.connect(f"{WS_URL}/{st.session_state.current_session}/classify") as websocket:
                    while st.session_state.get('camera_active', False):
                        try:
                            data = await websocket.recv()
                            result = json.loads(data)
                            if result.get("classification"):
                                if result["classification"] == "accept":
                                    result_placeholder.success("ACCEPTED")
                                else:
                                    result_placeholder.error("REJECTED")
                        except websockets.exceptions.ConnectionClosed:
                            st.warning("Connection lost")
                            break
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                            break
            else:
                result_placeholder.info("Waiting for classification...")
    else:
        st.info("Create a new session to begin classification")

if __name__ == "__main__":
    asyncio.run(show_dashboard())
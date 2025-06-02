from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket, metadata: Optional[Dict[str, Any]] = None):
        """Connect a new WebSocket client with optional metadata"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_metadata[websocket] = {
            "connected_at": datetime.now(),
            "last_activity": datetime.now(),
            **(metadata or {})
        }
        
    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket client and clean up metadata"""
        try:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
            if websocket in self.connection_metadata:
                del self.connection_metadata[websocket]
        except Exception:
            # If the websocket is not in the list or has already been removed
            pass
            
    async def send_json(self, websocket: WebSocket, data: Any):
        """Send JSON data to a specific WebSocket client"""
        try:
            if websocket.client_state.value != 3:  # Check if connection is not closed
                await websocket.send_json(data)
                self.connection_metadata[websocket]["last_activity"] = datetime.now()
        except WebSocketDisconnect:
            self.disconnect(websocket)
            raise
        except Exception as e:
            self.disconnect(websocket)
            raise WebSocketDisconnect(code=1011, reason=str(e))
            
    async def broadcast_json(self, data: Any):
        """Broadcast JSON data to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await self.send_json(connection, data)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception:
                disconnected.append(connection)
                
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
            
    async def send_bytes(self, websocket: WebSocket, data: bytes):
        """Send binary data to a specific WebSocket client"""
        try:
            if websocket.client_state.value != 3:  # Check if connection is not closed
                await websocket.send_bytes(data)
                self.connection_metadata[websocket]["last_activity"] = datetime.now()
        except WebSocketDisconnect:
            self.disconnect(websocket)
            raise
        except Exception as e:
            self.disconnect(websocket)
            raise WebSocketDisconnect(code=1011, reason=str(e))
            
    async def broadcast_bytes(self, data: bytes):
        """Broadcast binary data to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await self.send_bytes(connection, data)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception:
                disconnected.append(connection)
                
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
            
    async def receive_json(self, websocket: WebSocket) -> Any:
        """Receive JSON data from a WebSocket client"""
        try:
            data = await websocket.receive_json()
            self.connection_metadata[websocket]["last_activity"] = datetime.now()
            return data
        except WebSocketDisconnect:
            self.disconnect(websocket)
            raise
        except Exception as e:
            self.disconnect(websocket)
            raise WebSocketDisconnect(code=1011, reason=str(e))
            
    async def receive_bytes(self, websocket: WebSocket) -> bytes:
        """Receive binary data from a WebSocket client"""
        try:
            data = await websocket.receive_bytes()
            self.connection_metadata[websocket]["last_activity"] = datetime.now()
            return data
        except WebSocketDisconnect:
            self.disconnect(websocket)
            raise
        except Exception as e:
            self.disconnect(websocket)
            raise WebSocketDisconnect(code=1011, reason=str(e))
            
    def get_active_connections_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)
        
    def get_connection_metadata(self, websocket: WebSocket) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific connection"""
        return self.connection_metadata.get(websocket)
        
    async def close_connection(self, websocket: WebSocket, code: int = 1000, reason: str = "Normal closure"):
        """Close a WebSocket connection gracefully"""
        try:
            if websocket.client_state.value != 3:  # Only close if not already closed
                await websocket.close(code=code, reason=reason)
        except Exception:
            pass  # Ignore errors during close
        finally:
            self.disconnect(websocket)
            
    async def ping_connections(self):
        """Ping all active connections to check their health"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json({"type": "ping"})
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception:
                disconnected.append(connection)
                
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
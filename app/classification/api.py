from datetime import datetime
from fastapi import APIRouter, Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from classification.services.stream_sorter import sorter_socket
from classification.services.sorter import ClassificationService
from db.database import get_db

classify = APIRouter(prefix="/classification", tags=["classification"])


@classify.websocket("/{session_id}/classify")
async def websocket_classify(websocket: WebSocket, session_id: str, db=Depends(get_db)):
    """WebSocket endpoint for real-time classification"""
    
    await sorter_socket(
        websocket=websocket,
        session_id=session_id,
        classifier=ClassificationService(),
        db=db
    )


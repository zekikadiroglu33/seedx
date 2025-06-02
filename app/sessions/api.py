from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from sessions.schema import CreateSession
from sessions.service import create_session, end_session, get_session
from db.database import get_db
from stats.service import get_sampled_images_by_sessionid



session = APIRouter(prefix="/session", tags=["session"])

@session.get("/")
def read_root(db = Depends(get_db)):
    # Use the database session
    return {"message": "Hello World"}

@session.post("/start")
async def start_session(session: CreateSession, db=Depends(get_db)):
    """Start a new sorting session"""
    session_response = await create_session(db, session)
    return session_response
    


@session.post("/{session_id}/stop")
async def stop_session(session_id: str, db=Depends(get_db)):
    """Stop an active session"""
    session = await end_session(db, session_id)
    
    # Get sampled data
    sampled_data = await get_sampled_images_by_sessionid(db, session_id)
    
    return JSONResponse({
        "status": "stopped",
        "sampled_data": [{"seed_id": s.seed_id, "path": s.image_path} for s in sampled_data]
    })

@session.get("/{session_id}")
async def get_session_by_id(session_id: str, db=Depends(get_db)):
    """Get session information by ID"""
    session = await get_session(db, session_id)
    return {
        "id": session.id,
        "seed_lot": session.seed_lot,
        "status": session.status,
        "end_time": session.end_time.isoformat() if session.end_time else None
    }
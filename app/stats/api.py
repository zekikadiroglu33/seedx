from fastapi import APIRouter, Depends
from datetime import datetime

from fastapi.responses import JSONResponse

from db.database import get_db
from stats.service import get_sampled_images_by_sessionid, get_stats_by_sessionid

stats = APIRouter(prefix="/stats", tags=["stats"])

@stats.get("/{session_id}")
async def get_session_stats(session_id: str, db=Depends(get_db)):
    """Get statistics for a specific session"""
    session = await get_stats_by_sessionid(db=db, session_id=session_id)
    print(f"Session stats for {session_id}: {session}")
    if not session:
        return JSONResponse({"error": "Session not found"}, status_code=404)
    return {
        "start_time": session["session"]["start_time"],
        "end_time": session["session"].get("end_time"),
        "duration_seconds": (session["session"].get("end_time") or datetime.now()) - session["session"]["start_time"],
        "accepted": session["accepted"],
        "rejected": session["rejected"],
        "sampled": session["sampled"],
        "total": session["total"],
    }

@stats.get("/sampled/{session_id}")
async def get_sampled_images(session_id: str, limit: int = 10, db=Depends(get_db)):
    """Get sampled images for a session"""
    sampled = await get_sampled_images_by_sessionid(
                        db=db,
                        session_id=session_id,
                        limit=limit
                        )
    return [{"seed_id": s.seed_id, "path": s.image_path} for s in sampled]
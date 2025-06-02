from sqlalchemy import func, select
from models.classification import Classification
from sessions.service import get_session


async def get_sampled_images_by_sessionid(db, session_id: str, limit: int = 10):
    try:
        if not session_id:
            raise ValueError("session_id cannot be None or empty")
            
        result = await db.execute(
            select(Classification)
            .filter(
                Classification.session_id == session_id,
                Classification.is_sampled == True
            )
            .limit(limit)
        )
        
        if result is None:
            raise ValueError("Query result is None")
            
        return result.scalars().all()
    except Exception as e:
        raise Exception(f"Error in get_sampled_images_by_sessionid: {str(e)}")

async def get_stats_by_sessionid(db, session_id: str):
    # try:
    if not session_id:
        raise ValueError("session_id cannot be None or empty")
        
    # Get counts
    total = (await db.execute(
        select(func.count(Classification.id))
        .filter(Classification.session_id == session_id)
    )).scalars().all()
    if total is None:
        raise ValueError("Total count query result is None")
        
    accepted = (await db.execute(
        select(func.count(Classification.id))
        .filter(
            Classification.session_id == session_id,
            Classification.classify == "accept"
        )
    )).scalars().all()
    if accepted is None:
        raise ValueError("Accepted count query result is None")
        
    sampled = (await db.execute(
        select(func.count(Classification.id))
        .filter(
            Classification.session_id == session_id,
            Classification.is_sampled == True
        )
    )).scalars().all()
    if sampled is None:
        raise ValueError("Sampled count query result is None")
    
    # Get session details
    session = await get_session(db, session_id)
    def to_dict(obj):
        return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}

    session_dict = to_dict(session)

    if session is None:
        raise ValueError("Session not found")
    
    return {
        "total": sum(total),
        "accepted": sum(accepted),
        "rejected": sum(total) - sum(accepted),
        "sampled": sum(sampled),
        "session": session_dict
    }
    # except Exception as e:
    #     raise Exception(f"Error in get_stats_by_sessionid: {str(e)}")
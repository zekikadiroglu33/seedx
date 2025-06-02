from datetime import datetime


from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError


from utils.session_id_provider import generate_session_id
from sessions.schema import CreateSession
from models.session import Session


async def get_session(db, session_id: str):
    try:
        result = await db.execute(select(Session).filter(Session.id == session_id))
        session = result.scalar_one_or_none()
        if session is None:
            raise Exception(f"Session with id {session_id} not found")
        return session
    except SQLAlchemyError as e:
        raise Exception(f"Database error while getting session: {str(e)}")

async def create_session(db, session: CreateSession):
    session_id = generate_session_id()
    try:
        db_session = Session(
            id=session_id,
            seed_lot=session.seed_lot,
            status=session.status,
            end_time=None
            )
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
        
        # Convert SQLAlchemy model to dictionary
        session_dict = {
            "id": db_session.id,
            "seed_lot": db_session.seed_lot,
            "status": db_session.status,
            "end_time": db_session.end_time.isoformat() if db_session.end_time else None
        }
        return session_dict
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Database error while creating session: {str(e)}")


async def end_session(db, session_id: str):
    try:
        session = await get_session(db, session_id)
        if session is None:
            raise f"Session with id {session_id} not found"
        session.end_time = datetime.now()
        await db.commit()
        await db.refresh(session)
        return session
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Database error while ending session: {str(e)}")


# def update_session(db, session_id: str, session_data: SessionUpdate):
#     try:
#         result = update_session(session_id, session_data)
#         if result is None:
#             raise SessionNotFoundError(f"Session with id {session_id} not found")
#         return result
#     except Exception as e:
#         raise Exception(f"Error while updating session: {str(e)}")

# def delete_session(self, session_id: int):
#     try:
#         result = delete_session(session_id)
#         if result is None:
#             raise SessionNotFoundError(f"Session with id {session_id} not found")
#         return result
#     except Exception as e:
#         raise Exception(f"Error while deleting session: {str(e)}")


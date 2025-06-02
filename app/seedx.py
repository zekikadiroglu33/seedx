from fastapi import APIRouter
from classification.api import classify
from sessions.api import session
from stats.api import stats

seedx_router = APIRouter()

seedx_router.include_router(classify)
seedx_router.include_router(session)
seedx_router.include_router(stats)

from datetime import datetime
from fastapi.datastructures import Default
from pydantic import BaseModel
from typing import Dict

class Status(BaseModel):
    accepted: int
    rejected: int
    sampled: int

class ActiveSession(BaseModel):
    session_id: str
    seed_lot: str
    start_time: datetime
    stats: Status

class CreateSession(BaseModel):
    seed_lot: str
    status: str = "active"

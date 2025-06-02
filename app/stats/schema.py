from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class Stats(BaseModel):
    accepted: int
    rejected: int
    sampled: int

class SeedLotSchema(BaseModel):
    seed_lot: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = Field(
        None, description="Duration in seconds calculated as end_time - start_time"
    )
    stats: Stats

    @staticmethod
    def calculate_duration(start_time: datetime, end_time: Optional[datetime]) -> int:
        return int((end_time or datetime.now() - start_time).total_seconds())

    def __init__(self, **data):
        super().__init__(**data)
        if self.end_time:
            self.duration_seconds = self.calculate_duration(self.start_time, self.end_time)
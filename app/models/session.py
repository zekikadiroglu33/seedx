from uuid import uuid4
from sqlalchemy import UUID, Column, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base



class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID, default=lambda: uuid4(), primary_key=True, index=True)
    seed_lot = Column(String, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, nullable=False)
    
    # Relationships
    classifications = relationship("Classification", back_populates="session")
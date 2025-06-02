
from sqlalchemy import UUID, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base



class Classification(Base):
    __tablename__ = "classifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    seed_id = Column(String, index=True)
    classify = Column(String)  
    is_sampled = Column(Boolean, default=False)
    image_path = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.now())
    
    # Foreign key to session
    session_id = Column(UUID, ForeignKey("sessions.id"))
    session = relationship("Session", back_populates="classifications")
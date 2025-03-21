from .base import Base, Column, Integer, String, ForeignKey, relationship
from sqlalchemy import DateTime
from datetime import datetime

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    log = Column(String(1000))
    event_type = Column(String(100))  # face_not_detected, hand_detected, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="logs")

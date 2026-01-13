from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from app.src.db.database import Base

class Notification(Base):
    __tablename__ = 'notifications'
    
    table_id = Column(Integer, primary_key=True, index=True)
    id = Column(Integer, ForeignKey('usertable.id'), nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
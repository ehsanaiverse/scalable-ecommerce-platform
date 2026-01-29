from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.src.db.database import Base

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default='usd')
    status = Column(String, default='pending') # pending, succeeded, failed, canceled
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship('Order', back_populates='payment')
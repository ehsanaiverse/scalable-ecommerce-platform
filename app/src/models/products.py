from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, relationship
from app.src.db.database import Base

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    
    
    
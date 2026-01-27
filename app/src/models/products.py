from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.src.db.database import Base

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    category_rel = relationship("Category", back_populates="products")

    
    
    
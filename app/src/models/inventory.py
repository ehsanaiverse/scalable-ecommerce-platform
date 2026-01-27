from sqlalchemy import Column, Integer, ForeignKey
from app.src.db.database import Base
class Inventory(Base):
    __tablename__ = "inventorytable"
    
    inventory_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    stock_quantity = Column(Integer, nullable=False)
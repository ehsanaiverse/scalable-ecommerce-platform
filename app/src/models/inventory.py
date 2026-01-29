from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint, UniqueConstraint
from app.src.db.database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        unique=True  
    )
    stock_quantity = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("stock_quantity >= 0", name="stock_quantity_non_negative"),
    )

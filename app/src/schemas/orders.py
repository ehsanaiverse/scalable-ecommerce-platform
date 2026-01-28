from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.src.schemas.products import ProductResponse

class OrderItemSchema(BaseModel):
    id: int
    product_id: int
    product: ProductResponse
    quantity: int
    price: float

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    pass 

class OrderOut(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    created_at: datetime
    items: List[OrderItemSchema] = []

    class Config:
        from_attributes = True

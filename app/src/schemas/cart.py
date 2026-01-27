from pydantic import BaseModel, Field
from typing import List, Optional
from app.src.schemas.products import ProductResponse

class CartItemBase(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemRead(BaseModel):
    item_id: int = Field(validation_alias='id')
    product_id: int
    product: ProductResponse
    quantity: int

    class Config:
        from_attributes = True

class CartRead(BaseModel):
    cart_id: int = Field(validation_alias='id')
    user_id: int
    items: List[CartItemRead] = []
    total_price: float = 0.0

    class Config:
        from_attributes = True

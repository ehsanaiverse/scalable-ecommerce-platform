from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: int

class ProductCreate(ProductBase):
    stock_quantity: int  # Used for initial inventory creation

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    image_path: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    image_path: str
    
    class Config:
        from_attributes = True

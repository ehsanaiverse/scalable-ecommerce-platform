from pydantic import BaseModel

class InventoryBase(BaseModel):
    stock_quantity: int

class InventoryUpdate(BaseModel):
    stock_quantity: int

class InventoryResponse(BaseModel):
    inventory_id: int
    product_id: int
    stock_quantity: int

    class Config:
        from_attributes = True

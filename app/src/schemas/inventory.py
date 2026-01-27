from pydantic import BaseModel

class InventoryBase(BaseModel):
    stock_quantity: int

class InventoryUpdate(InventoryBase):
    pass

class InventoryResponse(InventoryBase):
    inventory_id: int
    product_id: int

    class Config:
        from_attributes = True
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.src.schemas.inventory import InventoryUpdate as InventorySchema, InventoryResponse
from app.src.db.database import get_db
from app.src.core.security import required_role
from app.src.models.user import User
from app.src.models.inventory import Inventory
from app.src.models.products import Product
from app.src.utils.exceptions import UnauthorizedException

router = APIRouter(tags=['Inventory'])

@router.get(
    "/admin/inventory",
    response_model=list[InventoryResponse]
)
def get_inventory(
    db: Session = Depends(get_db),
    current_user: dict = Depends(required_role("admin"))
):
    inventory = db.query(Inventory).all()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory is empty")
    return inventory


@router.put('/admin/inventory/{product_id}', response_model=InventorySchema)
def update_inventory(
    product_id: int, 
    inventory: InventorySchema, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(required_role("admin"))
):
    existing_inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not existing_inventory:
        
         raise HTTPException(status_code=404, detail="Inventory record not found")
    
    existing_inventory.stock_quantity = inventory.stock_quantity
    db.commit()
    db.refresh(existing_inventory)
    return existing_inventory

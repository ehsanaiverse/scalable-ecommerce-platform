from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.src.db.database import get_db
from app.src.core.security import get_current_user
from app.src.models.orders import Order, OrderItem
from app.src.models.cart import Cart, CartItem
from app.src.models.products import Product
from app.src.schemas.orders import OrderOut, OrderCreate

router = APIRouter(prefix="/orders", tags=["Orders"])



@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def place_order(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == current_user['id']).first()
    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )

    # Calculate total and prepare order items
    total_price = 0.0
    order_items_data = []

    for cart_item in cart.items:
        item_total = cart_item.product.price * cart_item.quantity
        total_price += item_total
        
        order_items_data.append({
            "product_id": cart_item.product_id,
            "quantity": cart_item.quantity,
            "price": cart_item.product.price
        })

    # Create Order
    new_order = Order(
        user_id=current_user['id'],
        total_price=total_price,
        status="pending"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Create OrderItems
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item_data["product_id"],
            quantity=item_data["quantity"],
            price=item_data["price"]
        )
        db.add(order_item)
    
    # Clear Cart
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    
    db.commit()
    db.refresh(new_order) 
    
    return new_order




@router.get("/", response_model=List[OrderOut])
def get_orders(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    orders = db.query(Order).filter(Order.user_id == current_user['id']).order_by(Order.created_at.desc()).all()
    return orders




@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user['id']).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order

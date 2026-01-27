from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.src.db.database import get_db
from app.src.core.security import get_current_user
from app.src.models.cart import Cart, CartItem
from app.src.models.products import Product
from app.src.schemas.cart import CartRead, CartItemCreate, CartItemUpdate

router = APIRouter(prefix="/cart", tags=['Cart'])

def get_or_create_cart(db: Session, user_id: int):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart



@router.get('/', response_model=CartRead)
def get_cart(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == current_user['id']).first()

    if not cart:
        return {'id': 0, 'user_id': current_user['id'], 'items': [], 'total_price': 0.0}
    
    total_price = sum(item.quantity * item.product.price for item in cart.items)
    return {'id': cart.id, 'user_id': cart.user_id, 'items': cart.items, 'total_price': total_price}



@router.post('/items', response_model=CartRead)
def add_item_to_cart(item_in: CartItemCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    cart = get_or_create_cart(db, current_user['id'])
    
    product = db.query(Product).filter(Product.id == item_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == item_in.product_id).first()
    if cart_item:
        cart_item.quantity += item_in.quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=item_in.product_id, quantity=item_in.quantity)
        db.add(cart_item)
    
    db.commit()
    db.refresh(cart)
    
    total_price = sum(item.quantity * item.product.price for item in cart.items)
    return {'id': cart.id, 'user_id': cart.user_id, 'items': cart.items, 'total_price': total_price}



@router.put('/items/{item_id}', response_model=CartRead)
def update_item_quantity(item_id: int, item_in: CartItemUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == current_user['id']).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
        
    cart_item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
        
    if item_in.quantity <= 0:
        db.delete(cart_item)
    else:
        cart_item.quantity = item_in.quantity
        
    db.commit()
    db.refresh(cart)
    
    total_price = sum(item.quantity * item.product.price for item in cart.items)
    return {'id': cart.id, 'user_id': cart.user_id, 'items': cart.items, 'total_price': total_price}



@router.delete('/items/{item_id}', response_model=CartRead)
def remove_item_from_cart(item_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == current_user['id']).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
        
    cart_item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
        
    db.delete(cart_item)
    db.commit()
    db.refresh(cart)
    
    total_price = sum(item.quantity * item.product.price for item in cart.items)
    return {'id': cart.id, 'user_id': cart.user_id, 'items': cart.items, 'total_price': total_price}



@router.delete('/')
def clear_cart(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == current_user['id']).first()
    if cart:
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        db.commit()
    return {'message': 'Cart cleared successfully'}

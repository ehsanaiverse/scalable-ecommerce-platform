from fastapi import FastAPI, status, HTTPException
from sqlalchemy.orm import Session
from app.src.models.orders import Order
from app.src.models.payments import Payment
import stripe

def create_payment_intent(db: Session, order_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    if Order.status != 'pending':
        raise HTTPException(status_code=400, detail="Order already paid or canceled")
    
    intent = stripe.PaymentIntent.create(
        order_id = order.id,
        amount = int(order.total_price * 100), # int is used to remove the decimal 
        currency = "usd",
        metadata = {"order_id": order.id}
    )
    
    payment = Payment(
        order_id = order.id,
        amount = order.total_price,
        currency = "usd",
        status = 'pending'
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    return intent.client_secret
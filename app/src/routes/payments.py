from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.src.db.database import get_db
from app.src.schemas.payments import CreatePaymentIntent
from app.src.models.orders import Order
from app.src.models.payments import Payment

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/create-intent")
def create_payment_intent(
    payload: CreatePaymentIntent,
    db: Session = Depends(get_db)
):
    # 1. Get the order
    order = db.query(Order).filter(Order.id == payload.order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # 2. Check if payment already exists
    existing_payment = (
        db.query(Payment)
        .filter(Payment.order_id == order.id)
        .first()
    )

    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order already paid"
        )

    # 3. Create payment
    new_payment = Payment(
        order_id=order.id,
        amount=order.total_price,
        currency=payload.currency
    )

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return {
        "message": "Payment created successfully",
        "payment_id": new_payment.id
    }

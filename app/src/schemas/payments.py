from pydantic import BaseModel

class CreatePaymentIntent(BaseModel):
    order_id: int
    currency: str = "usd"

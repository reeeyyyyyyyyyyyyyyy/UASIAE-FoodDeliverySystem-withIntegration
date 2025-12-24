from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from strawberry.fastapi import GraphQLRouter
from pydantic import BaseModel
from .database import engine, Base, get_db
from .models import Payment  # <-- GANTI JADI PAYMENT
from .schema import schema

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Payment Service")

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

class PaymentRequest(BaseModel):
    orderId: int
    userId: int
    amount: float
    status: str
    externalRefId: str = None

@app.post("/payments/log")
def log_payment(request: PaymentRequest, db: Session = Depends(get_db)):
    new_payment = Payment( # <-- Pakai class Payment
        order_id=request.orderId,
        user_id=request.userId,
        amount=request.amount,
        status=request.status,
        external_ref_id=request.externalRefId
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return {"message": "Payment logged", "id": new_payment.id}
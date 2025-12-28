from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from pydantic import BaseModel
import requests
from .database import engine, Base
from .schema import schema

# Create Tables
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

ORDER_SERVICE_URL = "http://order-service:8000"

class PaymentRequest(BaseModel):
    order_id: int
    payment_id: int
    payment_method: str = "E-Wallet"

@app.post("/payments/simulate")
def simulate_payment(req: PaymentRequest):
    # 1. (Optional) Verify payment_id validity if we had a real provider
    
    # 2. Call Order Service to update status to PAID or PREPARING
    # Using PREPARING to simulate immediate restaurant acceptance or just PAID
    new_status = "PAID"
    
    try:
        res = requests.put(
            f"{ORDER_SERVICE_URL}/internal/orders/{req.order_id}/status",
            json={"status": new_status}
        )
        if res.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to update order status")
            
        return {"status": "success", "message": "Payment successful", "data": {"transaction_id": "TRX-SIMULATED"}}
        
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Failed to connect to Order Service")
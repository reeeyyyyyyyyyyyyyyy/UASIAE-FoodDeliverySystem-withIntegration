from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .database import engine, Base, get_db
from .models import Order
from .schema import schema

# Buat tabel
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Order Service")

# --- TAMBAHAN UNTUK INTEGRASI (Internal API) ---

class OrderStatusUpdate(BaseModel):
    status: str

# 1. Endpoint untuk Payment Service mengecek Order
@app.get("/internal/orders/{order_id}")
def get_order_internal(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "id": order.id,
        "status": order.status,
        "total_price": float(order.total_price),
        "user_id": order.user_id
    }

# 2. Endpoint untuk Payment Service meng-update status jadi PAID/PREPARING
@app.put("/internal/orders/{order_id}/status")
def update_order_status_internal(order_id: int, update: OrderStatusUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = update.status
    db.commit()
    return {"message": "Status updated successfully", "new_status": order.status}

# ... (kode sebelumnya) ...

# 3. Endpoint Get Order by Status (Untuk Driver cari order PAID)
@app.get("/internal/orders/status/{status}")
def get_orders_by_status_internal(status: str, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.status == status).all()
    return [
        {
            "id": o.id,
            "restaurant_id": o.restaurant_id,
            "address_id": o.address_id,
            "total_price": float(o.total_price),
            "status": o.status
        } for o in orders
    ]

class AssignDriverRequest(BaseModel):
    driver_id: int

# 4. Endpoint Assign Driver (Saat Driver Accept Order)
@app.put("/internal/orders/{order_id}/assign-driver")
def assign_driver_internal(order_id: int, req: AssignDriverRequest, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.driver_id = req.driver_id
    order.status = "ON_DELIVERY" # Update status jadi sedang diantar
    db.commit()
    return {"message": "Driver assigned"}

# -----------------------------------------------

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
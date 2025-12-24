from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from strawberry.fastapi import GraphQLRouter
from pydantic import BaseModel
from typing import List
from .database import engine, Base, get_db
from .models import Order, OrderItem
from .schema import schema, process_payment_with_doswallet

# Buat tabel otomatis
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Order Service")

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

# --- Pydantic Models (Untuk REST API Input) ---
class OrderItemRequest(BaseModel):
    menuId: int
    name: str
    price: float
    quantity: int

class CreateOrderRequest(BaseModel):
    userId: int
    restaurantId: int
    addressId: int
    items: List[OrderItemRequest]

# --- REST ENDPOINTS (Legacy Frontend Support) ---

@app.post("/orders")
async def create_order_rest(request: CreateOrderRequest, db: Session = Depends(get_db)):
    """
    Endpoint ini dipanggil oleh Frontend React saat checkout.
    """
    # 1. Hitung Total
    total_amount = sum(item.price * item.quantity for item in request.items)
    
    # 2. Integrasi Pembayaran (Async Call)
    payment_result = await process_payment_with_doswallet(request.userId, total_amount)
    
    status = "PAID" if payment_result.get("success") else "CANCELLED"

    # 3. Simpan Order
    new_order = Order(
        user_id=request.userId, 
        restaurant_id=request.restaurantId,
        address_id=request.addressId,
        total_price=total_amount, 
        status=status
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # 4. Simpan Items
    for item in request.items:
        new_item = OrderItem(
            order_id=new_order.id, 
            menu_item_id=item.menuId, 
            menu_item_name=item.name, 
            price=item.price, 
            quantity=item.quantity
        )
        db.add(new_item)
    db.commit()

    # 5. Return JSON format Frontend
    return {
        "id": new_order.id,
        "userId": new_order.user_id,
        "restaurantId": new_order.restaurant_id,
        "addressId": new_order.address_id,
        "totalPrice": float(new_order.total_price),
        "status": new_order.status
    }

@app.get("/orders")
def get_my_orders(user_id: int, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()
    
    result = []
    for o in orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == o.id).all()
        result.append({
            "id": o.id,
            "restaurantId": o.restaurant_id,
            "addressId": o.address_id,
            "totalPrice": float(o.total_price),
            "status": o.status,
            "createdAt": str(o.created_at),
            "items": [
                {
                    "menuId": i.menu_item_id,
                    "name": i.menu_item_name,
                    "price": float(i.price),
                    "quantity": i.quantity
                } for i in items
            ]
        })
    return result

@app.get("/")
def root():
    return {"message": "Order Service is running"}
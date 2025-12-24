from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from strawberry.fastapi import GraphQLRouter
from typing import List
from pydantic import BaseModel
from .database import engine, Base, get_db, SessionLocal
from .models import Restaurant, MenuItem
from .schema import schema

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Restaurant Service")

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- INTERNAL API (INTEGRASI) ---

# 1. Endpoint untuk Cek Ketersediaan & Harga Menu (Dipanggil Order Service)
@app.get("/internal/menu-items/{item_id}")
def get_menu_item_internal(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    return {
        "id": item.id,
        "name": item.name,
        "price": float(item.price),
        "stock": item.stock,
        "is_available": item.is_available,
        "restaurant_id": item.restaurant_id
    }

# Model untuk payload pengurangan stok
class StockUpdateItem(BaseModel):
    menu_item_id: int
    quantity: int

# 2. Endpoint untuk Kurangi Stok (Dipanggil Order Service saat Create Order)
@app.post("/internal/menu-items/reduce-stock")
def reduce_stock_internal(items: List[StockUpdateItem], db: Session = Depends(get_db)):
    for item_req in items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_req.menu_item_id).first()
        
        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu {item_req.menu_item_id} not found")
        
        if menu_item.stock < item_req.quantity:
            raise HTTPException(status_code=400, detail=f"Stock not enough for {menu_item.name}")
        
        # Kurangi Stok
        menu_item.stock -= item_req.quantity
    
    db.commit()
    return {"message": "Stock updated successfully"}
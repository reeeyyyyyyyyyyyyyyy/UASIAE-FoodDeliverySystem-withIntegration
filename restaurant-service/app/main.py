from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from strawberry.fastapi import GraphQLRouter
from .database import engine, Base, get_db
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

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/restaurants")
def get_restaurants(db: Session = Depends(get_db)):
    restaurants = db.query(Restaurant).all()
    result = []
    for r in restaurants:
        menus = db.query(MenuItem).filter(MenuItem.restaurant_id == r.id).all()
        result.append({
            "id": r.id,
            "name": r.name,
            "address": r.address,
            "cuisineType": r.cuisine_type,
            "isOpen": r.is_open,
            "imageUrl": r.image_url,
            "menus": [
                {
                    "id": m.id,
                    "name": m.name,
                    "description": m.description,
                    "price": float(m.price),
                    "stock": m.stock,
                    "imageUrl": m.image_url,
                    "isAvailable": m.is_available,
                    "category": m.category
                } for m in menus
            ]
        })
    return result

@app.get("/restaurants/{restaurant_id}")
def get_restaurant_detail(restaurant_id: int, db: Session = Depends(get_db)):
    r = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    menus = db.query(MenuItem).filter(MenuItem.restaurant_id == r.id).all()
    return {
        "id": r.id,
        "name": r.name,
        "address": r.address,
        "cuisineType": r.cuisine_type,
        "isOpen": r.is_open,
        "imageUrl": r.image_url,
        "menus": [
            {
                "id": m.id,
                "name": m.name,
                "description": m.description,
                "price": float(m.price),
                "stock": m.stock,
                "imageUrl": m.image_url,
                "isAvailable": m.is_available,
                "category": m.category
            } for m in menus
        ]
    }

@app.get("/")
def root():
    return {"message": "Restaurant Service is running"}
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from strawberry.fastapi import GraphQLRouter
from .database import engine, Base, get_db, SessionLocal
from .models import Driver
from .schema import schema

# Buat tabel otomatis jika belum ada
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Driver Service")

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

@app.get("/drivers")
def get_drivers(db: Session = Depends(get_db)):
    drivers = db.query(Driver).all()
    return [
        {
            "id": d.id,
            "userId": d.user_id,
            "vehicleType": d.vehicle_type,
            "vehicleNumber": d.vehicle_number,
            "isAvailable": d.is_available,
            "isOnJob": d.is_on_job,
            "totalEarnings": float(d.total_earnings)
        } for d in drivers
    ]

@app.get("/drivers/{driver_id}")
def get_driver(driver_id: int, db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        return {"error": "Driver not found"}
    
    return {
        "id": driver.id,
        "userId": driver.user_id,
        "vehicleType": driver.vehicle_type,
        "vehicleNumber": driver.vehicle_number,
        "isAvailable": driver.is_available,
        "isOnJob": driver.is_on_job,
        "totalEarnings": float(driver.total_earnings)
    }

@app.get("/")
def root():
    return {"message": "Driver Service is running"}
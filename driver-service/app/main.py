from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from .database import engine, Base
from .schema import schema

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

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from .database import get_db
from . import models
from pydantic import BaseModel

@app.get("/drivers/admin/all")
def get_all_drivers_admin(db: Session = Depends(get_db)):
    drivers = db.query(models.Driver).all()
    # Frontend expects "name". Since we don't have it (it's in User Service), 
    # we'll map it temporarily to prevent crash or blank.
    # Ideally, we should fetch from User Service.
    results = []
    for d in drivers:
        results.append({
            "id": d.id,
            "user_id": d.user_id,
            "name": f"Driver User {d.user_id}", # Placeholder
            "vehicle_type": d.vehicle_type,
            "vehicle_number": d.vehicle_number,
            "is_available": d.is_available,
            "is_on_job": d.is_on_job,
            "total_earnings": d.total_earnings,
            "created_at": d.created_at,
            "phone": "08123456789", # Placeholder
            "active_orders": 0 # Placeholder
        })
    return {"status": "success", "data": results}

@app.get("/drivers/admin/salaries")
def get_driver_salaries(db: Session = Depends(get_db)):
    salaries = db.query(models.DriverSalary).all()
    # Ideally join with Driver name
    return {"status": "success", "data": salaries}

class EarningRequest(BaseModel):
    user_id: int
    amount: float
    order_id: int

@app.post("/internal/drivers/earnings")
def add_driver_earning(req: EarningRequest, db: Session = Depends(get_db)):
    # 1. Update Total Earnings in Driver Table
    driver = db.query(models.Driver).filter(models.Driver.user_id == req.user_id).first()
    if not driver:
        # Create if not exists (Auto-register driver on first job)
        driver = models.Driver(
            user_id=req.user_id, 
            vehicle_type="Unknown", 
            vehicle_number="Unknown", 
            total_earnings=0
        )
        db.add(driver)
        db.commit()
    
    driver.total_earnings += req.amount
    
    # 2. Record in Salary History
    salary_record = models.DriverSalary(
        driver_id=driver.id,
        amount=req.amount,
        status="PAID", # Asumsi langsung masuk wallet/paid
        period=func.current_date() # Simply record date
    )
    db.add(salary_record)
    
    db.commit()
    db.add(salary_record)
    
    db.commit()
    return {"status": "success", "message": "Earning recorded"}

@app.post("/drivers/admin/salaries/mark-as-paid/{salary_id}")
def mark_salary_as_paid(salary_id: int, db: Session = Depends(get_db)):
    salary = db.query(models.DriverSalary).filter(models.DriverSalary.id == salary_id).first()
    if not salary:
        # If not found in salary table, maybe it's a request to pay out *all* for a driver?
        # But the URL implies specific ID. Let's assume salary_id.
        # Frontend likely sends salary_id or driver_id?
        # User says: POST .../mark-as-paid/1 404. ID 1 likely salary ID.
        raise HTTPException(status_code=404, detail="Salary record not found")
    
    salary.status = "TRANSFERRED" # Or "PAID_OUT"
    db.commit()
    return {"status": "success", "message": "Marked as paid"}

@app.post("/drivers/reset-data")
def reset_driver_data(db: Session = Depends(get_db)):
    # Reset Earnings and Job Status
    db.query(models.Driver).update({
        models.Driver.total_earnings: 0,
        models.Driver.is_on_job: False,
        models.Driver.is_available: True
    })
    
    # Clear Salary History
    db.query(models.DriverSalary).delete()
    
    db.commit()
    return {"status": "success", "message": "Driver data reset"}
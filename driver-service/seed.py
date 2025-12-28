from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Driver, DriverSalary
import os
import random
from datetime import datetime, timedelta

# Database Connection
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:root@driver_db:3306/driver_service_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_data():
    db = SessionLocal()
    
    # Check if data exists
    if db.query(Driver).first():
        print("Driver data already seeded.")
        return

    print("Seeding Driver data...")
    
    # Create Drivers
    drivers_data = [
        {"user_id": 2, "vehicle_type": "Motorcycle", "vehicle_number": "D 1234 ABC", "is_available": True, "total_earnings": 150000},
        {"user_id": 3, "vehicle_type": "Motorcycle", "vehicle_number": "B 5678 DEF", "is_available": True, "total_earnings": 250000},
        {"user_id": 4, "vehicle_type": "Car", "vehicle_number": "F 9012 GHI", "is_available": True, "total_earnings": 0},
    ]

    drivers = []
    for d_data in drivers_data:
        driver = Driver(**d_data)
        db.add(driver)
        drivers.append(driver)
    
    db.commit()
    
    # Create Salaries
    curr_month = datetime.utcnow().month
    curr_year = datetime.utcnow().year
    
    for driver in drivers:
        if driver.total_earnings > 0:
            salary = DriverSalary(
                driver_id=driver.id,
                month=curr_month,
                year=curr_year,
                base_salary=1000000,
                commission=driver.total_earnings,
                total_orders=random.randint(5, 20),
                total_earnings=1000000 + driver.total_earnings,
                status="UNPAID",
                created_at=datetime.utcnow()
            )
            db.add(salary)
            
            # Add some history paid salaries
            paid_salary = DriverSalary(
                driver_id=driver.id,
                month=curr_month - 1 if curr_month > 1 else 12,
                year=curr_year if curr_month > 1 else curr_year - 1,
                base_salary=1000000,
                commission=random.randint(50000, 200000),
                total_orders=random.randint(5, 20),
                total_earnings=1150000,
                status="PAID",
                created_at=datetime.utcnow() - timedelta(days=30)
            )
            db.add(paid_salary)

    db.commit()
    print("Driver data seeded successfully!")
    db.close()

if __name__ == "__main__":
    seed_data()

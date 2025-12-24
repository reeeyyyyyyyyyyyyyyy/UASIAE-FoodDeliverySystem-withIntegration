from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Link ke tabel Users
    vehicle_type = Column(String(50), nullable=False)  # Sesuai SQL
    vehicle_number = Column(String(50), nullable=False)  # Sesuai SQL (bukan vehicle_plate)
    is_available = Column(Boolean, default=True)  # Sesuai SQL
    is_on_job = Column(Boolean, default=False)  # Dari SQL
    total_earnings = Column(Numeric(10, 2), default=0.00)  # Dari SQL
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class DeliveryTask(Base):
    __tablename__ = "delivery_tasks"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="ASSIGNED")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class DriverSalary(Base):
    __tablename__ = "driver_salaries"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    base_salary = Column(Numeric(10, 2), nullable=False)
    commission = Column(Numeric(10, 2), default=0.00)
    total_orders = Column(Integer, default=0)
    total_earnings = Column(Numeric(10, 2), default=0.00)
    status = Column(String(50), default="PENDING")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
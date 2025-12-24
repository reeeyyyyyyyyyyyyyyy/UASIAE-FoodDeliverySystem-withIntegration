from sqlalchemy import Column, Integer, String, DateTime, DECIMAL
from sqlalchemy.sql import func
from .database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(50), default="PENDING")
    payment_method = Column(String(50), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
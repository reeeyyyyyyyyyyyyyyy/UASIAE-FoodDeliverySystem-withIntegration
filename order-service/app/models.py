from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    restaurant_id = Column(Integer, nullable=False)
    address_id = Column(Integer, nullable=False)
    status = Column(String(50), default="PENDING_PAYMENT")
    total_price = Column(DECIMAL(10, 2), nullable=False)
    payment_id = Column(Integer, nullable=True)
    driver_id = Column(Integer, nullable=True)
    estimated_delivery_time = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    menu_item_id = Column(Integer, nullable=False)
    menu_item_name = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(DECIMAL(10, 2), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="items")
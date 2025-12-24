from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class UserRole(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"
    DRIVER = "DRIVER"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)  # Sesuai dengan SQL: phone
    role = Column(SQLEnum(UserRole), default=UserRole.CUSTOMER)
    
    # Kolom timestamps dari SQL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relasi ke Address
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")

class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    label = Column(String(100), nullable=False)
    full_address = Column(Text, nullable=False)
    latitude = Column(String(20), nullable=True)  # Sesuai DB
    longitude = Column(String(20), nullable=True)  # Sesuai DB
    is_default = Column(Integer, default=0)  # Tinyint di SQL

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("User", back_populates="addresses")
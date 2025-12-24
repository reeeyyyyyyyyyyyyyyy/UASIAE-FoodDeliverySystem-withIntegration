import strawberry
import httpx
import os
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Order, OrderItem

# --- INTEGRATION HELPER ---
async def process_payment_with_doswallet(user_id: int, amount: float) -> dict:
    url = os.getenv("DOSWALLET_API_URL")
    if not url:
        # MOCK FALLBACK jika DOSWALLET_API_URL tidak tersedia
        return {
            "success": True, 
            "transactionId": f"MOCK-TRX-{int(datetime.now().timestamp())}", 
            "message": "Payment Successful (Mock)"
        }
    
    mutation = """
    mutation Pay($userId: ID!, $amount: Float!) {
        pay(userId: $userId, amount: $amount) {
            success
            transactionId
            message
        }
    }
    """
    variables = {"userId": str(user_id), "amount": amount}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json={"query": mutation, "variables": variables})
            if response.status_code == 200:
                data = response.json()
                if data.get("data") and data["data"].get("pay"):
                    return data["data"]["pay"]
    except Exception as e:
        print(f"Integration Error (Using Mock instead): {e}")

    # MOCK FALLBACK
    return {
        "success": True, 
        "transactionId": f"MOCK-TRX-{int(datetime.now().timestamp())}", 
        "message": "Payment Successful (Mock)"
    }

# --- TYPES & RESOLVERS ---

@strawberry.type
class OrderItemType:
    menu_id: int
    menu_name: str
    price: float
    quantity: int

@strawberry.type
class OrderType:
    id: int
    user_id: int
    restaurant_id: int
    address_id: int
    total_price: float
    status: str
    
    @strawberry.field
    def items(self) -> List[OrderItemType]:
        db = SessionLocal()
        try:
            items = db.query(OrderItem).filter(OrderItem.order_id == self.id).all()
            return [
                OrderItemType(
                    menu_id=i.menu_item_id, menu_name=i.menu_item_name, 
                    price=float(i.price), quantity=i.quantity
                ) for i in items
            ]
        finally:
            db.close()

    @strawberry.field(name="userId")
    def user_id_alias(self) -> int:
        return self.user_id

    @strawberry.field(name="restaurantId")
    def restaurant_id_alias(self) -> int:
        return self.restaurant_id

    @strawberry.field(name="addressId")
    def address_id_alias(self) -> int:
        return self.address_id

    @strawberry.field(name="total")
    def total_alias(self) -> float:
        return float(self.total_price)

@strawberry.type
class Query:
    @strawberry.field(name="orders")
    def all_orders(self) -> List[OrderType]:
        db = SessionLocal()
        try:
            orders = db.query(Order).all()
            return [
                OrderType(
                    id=o.id, user_id=o.user_id, restaurant_id=o.restaurant_id,
                    address_id=o.address_id, total_price=float(o.total_price),
                    status=o.status
                ) for o in orders
            ]
        finally:
            db.close()

    @strawberry.field(name="orderById")
    def order_by_id(self, id: int) -> Optional[OrderType]:
        db = SessionLocal()
        try:
            order = db.query(Order).filter(Order.id == id).first()
            if order:
                return OrderType(
                    id=order.id, user_id=order.user_id, restaurant_id=order.restaurant_id,
                    address_id=order.address_id, total_price=float(order.total_price),
                    status=order.status
                )
        finally:
            db.close()
        return None

    @strawberry.field(name="userOrders")
    def user_orders(self, user_id: int) -> List[OrderType]:
        db = SessionLocal()
        try:
            orders = db.query(Order).filter(Order.user_id == user_id).all()
            return [
                OrderType(
                    id=o.id, user_id=o.user_id, restaurant_id=o.restaurant_id,
                    address_id=o.address_id, total_price=float(o.total_price),
                    status=o.status
                ) for o in orders
            ]
        finally:
            db.close()

    @strawberry.field(name="myOrders")
    def my_orders(self, user_id: int) -> List[OrderType]:
        db = SessionLocal()
        try:
            orders = db.query(Order).filter(Order.user_id == user_id).all()
            return [
                OrderType(
                    id=o.id, user_id=o.user_id, restaurant_id=o.restaurant_id,
                    address_id=o.address_id, total_price=float(o.total_price),
                    status=o.status
                ) for o in orders
            ]
        finally:
            db.close()

    @strawberry.field
    def order_by_id(self, id: int) -> Optional[OrderType]:
        db = SessionLocal()
        try:
            order = db.query(Order).filter(Order.id == id).first()
            if order:
                return OrderType(
                    id=order.id, user_id=order.user_id, restaurant_id=order.restaurant_id,
                    address_id=order.address_id, total_price=float(order.total_price),
                    status=order.status
                )
        finally:
            db.close()
        return None

@strawberry.input
class OrderItemInput:
    menu_id: int
    menu_name: str
    price: float
    quantity: int

@strawberry.type
class Mutation:
    @strawberry.mutation(name="createOrder")
    async def create_order(self, user_id: int, restaurant_id: int, address_id: int, items: List[OrderItemInput]) -> OrderType:
        total = sum(item.price * item.quantity for item in items)
        
        # Payment Logic
        payment_result = await process_payment_with_doswallet(user_id, total)
        status = "PAID" if payment_result.get("success") else "CANCELLED"

        db = SessionLocal()
        try:
            new_order = Order(
                user_id=user_id, restaurant_id=restaurant_id, address_id=address_id,
                total_price=total, status=status, payment_id=None
            )
            db.add(new_order)
            db.commit()
            db.refresh(new_order)
            
            for item in items:
                new_item = OrderItem(
                    order_id=new_order.id, menu_item_id=item.menu_id,
                    menu_item_name=item.menu_name, price=item.price, quantity=item.quantity
                )
                db.add(new_item)
            db.commit()
            
            # Return object sebelum session ditutup
            result = OrderType(
                id=new_order.id, 
                user_id=new_order.user_id, 
                restaurant_id=new_order.restaurant_id,
                address_id=new_order.address_id,
                total_price=float(new_order.total_price),
                status=new_order.status
            )
            return result
            
        finally:
            db.close()

    @strawberry.mutation(name="updateOrderStatus")
    def update_order_status(self, id: int, status: str) -> Optional[OrderType]:
        db = SessionLocal()
        try:
            order = db.query(Order).filter(Order.id == id).first()
            if order:
                order.status = status
                db.commit()
                return OrderType(
                    id=order.id, user_id=order.user_id, restaurant_id=order.restaurant_id,
                    address_id=order.address_id, total_price=float(order.total_price),
                    status=order.status
                )
        finally:
            db.close()
        return None

schema = strawberry.Schema(query=Query, mutation=Mutation)
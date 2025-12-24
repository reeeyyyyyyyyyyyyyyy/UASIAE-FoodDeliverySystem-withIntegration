import strawberry
from typing import List, Optional
from .database import SessionLocal
from .models import Payment

@strawberry.type
class PaymentType:
    id: int
    order_id: int
    user_id: int
    amount: float
    status: str
    payment_method: Optional[str]

@strawberry.type
class Query:
    @strawberry.field(name="payments")
    def all_payments(self) -> List[PaymentType]:
        db = SessionLocal()
        try:
            payments = db.query(Payment).all()
            return [
                PaymentType(
                    id=p.id, order_id=p.order_id, user_id=p.user_id,
                    amount=float(p.amount), status=p.status, payment_method=p.payment_method
                ) for p in payments
            ]
        finally:
            db.close()

    @strawberry.field(name="paymentById")
    def payment_by_id(self, id: int) -> Optional[PaymentType]:
        db = SessionLocal()
        try:
            payment = db.query(Payment).filter(Payment.id == id).first()
            if payment:
                return PaymentType(
                    id=payment.id, order_id=payment.order_id, user_id=payment.user_id,
                    amount=float(payment.amount), status=payment.status, payment_method=payment.payment_method
                )
        finally:
            db.close()
        return None

    @strawberry.field(name="paymentByOrder")
    def payment_by_order(self, order_id: int) -> Optional[PaymentType]:
        db = SessionLocal()
        try:
            payment = db.query(Payment).filter(Payment.order_id == order_id).first()
            if payment:
                return PaymentType(
                    id=payment.id, order_id=payment.order_id, user_id=payment.user_id,
                    amount=float(payment.amount), status=payment.status, payment_method=payment.payment_method
                )
        finally:
            db.close()
        return None

    @strawberry.field(name="userPayments")
    def user_payments(self, user_id: int) -> List[PaymentType]:
        db = SessionLocal()
        try:
            payments = db.query(Payment).filter(Payment.user_id == user_id).all()
            return [
                PaymentType(
                    id=p.id, order_id=p.order_id, user_id=p.user_id,
                    amount=float(p.amount), status=p.status, payment_method=p.payment_method
                ) for p in payments
            ]
        finally:
            db.close()

    @strawberry.field(name="paymentHistory")
    def payment_history(self, user_id: Optional[int] = None) -> List[PaymentType]:
        db = SessionLocal()
        try:
            query = db.query(Payment)
            if user_id:
                query = query.filter(Payment.user_id == user_id)
            payments = query.all()
            return [
                PaymentType(
                    id=p.id, order_id=p.order_id, user_id=p.user_id,
                    amount=float(p.amount), status=p.status, payment_method=p.payment_method
                ) for p in payments
            ]
        finally:
            db.close()

@strawberry.type
class Mutation:
    @strawberry.mutation(name="createPayment")
    def create_payment(self, order_id: int, user_id: int, amount: float, payment_method: Optional[str] = None) -> Optional[PaymentType]:
        db = SessionLocal()
        try:
            payment = Payment(
                order_id=order_id,
                user_id=user_id,
                amount=amount,
                status="PENDING",
                payment_method=payment_method
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)
            return PaymentType(
                id=payment.id, order_id=payment.order_id, user_id=payment.user_id,
                amount=float(payment.amount), status=payment.status, payment_method=payment.payment_method
            )
        finally:
            db.close()
        return None

    @strawberry.mutation(name="updatePaymentStatus")
    def update_payment_status(self, payment_id: int, status: str) -> Optional[PaymentType]:
        db = SessionLocal()
        try:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if payment:
                payment.status = status
                db.commit()
                return PaymentType(
                    id=payment.id, order_id=payment.order_id, user_id=payment.user_id,
                    amount=float(payment.amount), status=payment.status, payment_method=payment.payment_method
                )
        finally:
            db.close()
        return None

schema = strawberry.Schema(query=Query, mutation=Mutation)
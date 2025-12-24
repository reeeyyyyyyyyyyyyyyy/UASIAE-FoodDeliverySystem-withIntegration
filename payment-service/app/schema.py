import strawberry
from typing import List, Optional
from strawberry.types import Info
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Payment
from jose import jwt
import os
import requests # Library untuk nembak API Order Service

# --- CONFIG ---
SECRET_KEY = os.getenv("SECRET_KEY", "kunci_rahasia_project_ini_harus_sama_semua")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ORDER_SERVICE_URL = "http://order-service:8000" # URL Docker Internal

def get_current_user_id(info: Info) -> int:
    request = info.context.get("request")
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise Exception("Authorization header missing")
    try:
        scheme, token = auth_header.split()
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload.get("id"))
    except Exception:
        raise Exception("Invalid or expired token")

# --- TYPES ---
@strawberry.type
class PaymentType:
    id: int
    order_id: int
    user_id: int
    amount: float
    status: str
    payment_method: Optional[str]
    created_at: str

# --- RESOLVERS ---
@strawberry.type
class Query:
    @strawberry.field
    def payment_history(self, info: Info) -> List[PaymentType]:
        user_id = get_current_user_id(info)
        db = SessionLocal()
        payments = db.query(Payment).filter(Payment.user_id == user_id).all()
        db.close()
        return [
            PaymentType(
                id=p.id, order_id=p.order_id, user_id=p.user_id,
                amount=float(p.amount), status=p.status,
                payment_method=p.payment_method, created_at=str(p.created_at)
            ) for p in payments
        ]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def process_payment(
        self, info: Info, order_id: int, amount: float, payment_method: str
    ) -> PaymentType:
        
        user_id = get_current_user_id(info)
        
        # --- LANGKAH 1: Validasi ke Order Service (INTEGRASI) ---
        try:
            # Nembak endpoint internal yang baru kita buat di Order Service
            response = requests.get(f"{ORDER_SERVICE_URL}/internal/orders/{order_id}")
            
            if response.status_code == 404:
                raise Exception("Order Not Found in Order Service")
            
            order_data = response.json()
            
            # Cek Status: Jika bukan PENDING_PAYMENT, tolak!
            if order_data['status'] != 'PENDING_PAYMENT':
                raise Exception(f"Payment Failed: Order status is already {order_data['status']}")
            
            # Cek User: Pastikan yang bayar adalah pemilik order
            if order_data['user_id'] != user_id:
                raise Exception("Unauthorized: This order belongs to another user")

            # Cek Amount: (Opsional) Validasi jumlah bayar
            # if order_data['total_price'] != amount: ...

        except requests.exceptions.ConnectionError:
            raise Exception("Failed to connect to Order Service")
        
        # --- LANGKAH 2: Proses Pembayaran Lokal ---
        db = SessionLocal()
        try:
            # Cek double payment di lokal juga (Double Protection)
            existing = db.query(Payment).filter(
                Payment.order_id == order_id, Payment.status == "SUCCESS"
            ).first()
            if existing:
                raise Exception("Order already paid (Recorded in Payment DB)")

            new_payment = Payment(
                order_id=order_id, user_id=user_id, amount=amount,
                payment_method=payment_method, status="SUCCESS" # Anggap sukses
            )
            db.add(new_payment)
            db.commit()
            db.refresh(new_payment)
            
            # --- LANGKAH 3: Update Status di Order Service (CALLBACK) ---
            # Beritahu Order Service bahwa ini sudah lunas -> Ubah status jadi 'PREPARING' atau 'PAID'
            requests.put(
                f"{ORDER_SERVICE_URL}/internal/orders/{order_id}/status",
                json={"status": "PAID"} # Atau 'PREPARING'
            )
            
            return PaymentType(
                id=new_payment.id, order_id=new_payment.order_id,
                user_id=new_payment.user_id, amount=float(new_payment.amount),
                status=new_payment.status, payment_method=new_payment.payment_method,
                created_at=str(new_payment.created_at)
            )
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

schema = strawberry.Schema(query=Query, mutation=Mutation)
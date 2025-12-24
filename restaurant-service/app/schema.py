import strawberry
from typing import List, Optional
from strawberry.types import Info
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Restaurant, MenuItem
from jose import jwt, JWTError
import os

# --- KONFIGURASI AUTH ---
SECRET_KEY = os.getenv("SECRET_KEY", "kunci_rahasia_project_ini_harus_sama_semua")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def get_current_user(info: Info):
    """
    Validasi Token dan return data user (id & role)
    """
    request = info.context.get("request")
    if not request:
        raise Exception("Request context not found")

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise Exception("Authorization header missing")

    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise Exception("Invalid authentication scheme")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload # Berisi {'id': ..., 'role': ..., 'sub': ...}
        
    except (ValueError, JWTError):
        raise Exception("Invalid or expired token")

# --- TYPES (Sama seperti sebelumnya) ---

@strawberry.type
class MenuItemType:
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    category: Optional[str]
    imageUrl: Optional[str]
    isAvailable: bool

@strawberry.type
class RestaurantType:
    id: int
    name: str
    address: str
    isOpen: bool
    category: Optional[str] 
    imageUrl: Optional[str]

    @strawberry.field
    def menus(self) -> List[MenuItemType]:
        db = SessionLocal()
        menus = db.query(MenuItem).filter(MenuItem.restaurant_id == self.id).all()
        db.close()
        return [
            MenuItemType(
                id=m.id, 
                name=m.name, 
                description=m.description, 
                price=float(m.price),
                stock=m.stock,
                category=m.category,
                imageUrl=m.image_url, 
                isAvailable=bool(m.is_available)
            ) for m in menus
        ]

# --- RESOLVERS ---

@strawberry.type
class Query:
    # PUBLIC: Tidak perlu cek token/role
    @strawberry.field
    def restaurants(self) -> List[RestaurantType]:
        db = SessionLocal()
        restaurants_db = db.query(Restaurant).all()
        db.close()
        return [
            RestaurantType(
                id=r.id, 
                name=r.name, 
                address=r.address, 
                isOpen=bool(r.is_open),
                category=r.cuisine_type, 
                imageUrl=r.image_url
            ) for r in restaurants_db
        ]

    # PUBLIC: Tidak perlu cek token/role
    @strawberry.field
    def restaurant(self, id: int) -> Optional[RestaurantType]:
        db = SessionLocal()
        r = db.query(Restaurant).filter(Restaurant.id == id).first()
        db.close()
        if r:
            return RestaurantType(
                id=r.id, 
                name=r.name, 
                address=r.address, 
                isOpen=bool(r.is_open),
                category=r.cuisine_type,
                imageUrl=r.image_url
            )
        return None

# --- MUTATIONS (PROTECTED ADMIN) ---

@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_restaurant(
        self, 
        info: Info, # Butuh info untuk baca header
        name: str, 
        address: str, 
        category: str, 
        image_url: str = None
    ) -> RestaurantType:
        
        # 1. CEK AUTH & ROLE
        user = get_current_user(info)
        
        # Pastikan role di token adalah ADMIN (Case insensitive)
        if user.get("role", "").upper() != "ADMIN":
            raise Exception("Unauthorized: Only Admins can add restaurants")

        # 2. PROSES TAMBAH DATA
        db = SessionLocal()
        try:
            new_resto = Restaurant(
                name=name, 
                address=address, 
                cuisine_type=category, 
                is_open=True, 
                image_url=image_url
            )
            db.add(new_resto)
            db.commit()
            db.refresh(new_resto)
            
            return RestaurantType(
                id=new_resto.id, 
                name=new_resto.name, 
                address=new_resto.address, 
                isOpen=new_resto.is_open,
                category=new_resto.cuisine_type,
                imageUrl=new_resto.image_url
            )
        finally:
            db.close()

schema = strawberry.Schema(query=Query, mutation=Mutation)
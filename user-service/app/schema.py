import strawberry
from typing import Optional, List
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User, Address
from passlib.context import CryptContext
from jose import jwt
import os
from datetime import datetime, timedelta

# --- SETUP AUTH ---
# Prefer bcrypt_sha256 to avoid the 72-byte bcrypt limit and backend incompatibilities;
# keep plain bcrypt as fallback to verify existing hashes from DB.
# Use PBKDF2-SHA256 as default hasher (no 72-byte limit) and keep bcrypt as fallback
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def verify_password(plain_password, hashed_password):
    """Verify plain password against bcrypt hash"""
    try:
        if isinstance(hashed_password, bytes):
            hashed_password = hashed_password.decode('utf-8')
        # Truncate to 72 bytes BEFORE verification (bcrypt limit)
        if len(plain_password) > 72:
            plain_password = plain_password[:72]
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verify error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Hash password with bcrypt, truncating to 72 bytes if necessary"""
    try:
        # Truncate to 72 bytes BEFORE hashing (bcrypt limit)
        if len(password) > 72:
            password = password[:72]
        return pwd_context.hash(password)
    except Exception as e:
        raise Exception(f"Password hashing error: {e}")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- TYPES ---

@strawberry.type
class AddressType:
    id: int
    label: str
    full_address: str
    is_default: bool

@strawberry.type
class UserType:
    id: int
    name: str
    email: str
    role: str
    phone: Optional[str] 
    
    @strawberry.field
    def addresses(self) -> List[AddressType]:
        db = SessionLocal()
        try:
            addrs = db.query(Address).filter(Address.user_id == self.id).all()
            return [
                AddressType(id=a.id, label=a.label, full_address=a.full_address, is_default=bool(a.is_default)) 
                for a in addrs
            ]
        finally:
            db.close()

    @strawberry.field(name="fullName")
    def full_name(self) -> str:
        return self.name

@strawberry.type
class AuthPayload:
    token: str
    user: UserType

# --- RESOLVERS ---

@strawberry.type
class Query:
    @strawberry.field
    def me(self, token: str) -> Optional[UserType]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.email == email).first()
                if user:
                    return UserType(id=user.id, name=user.name, email=user.email, role=user.role, phone=user.phone)
            finally:
                db.close()
        except:
            pass
        return None
    
    @strawberry.field(name="userById") 
    def user_by_id(self, id: int) -> Optional[UserType]:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == id).first()
            if user:
                return UserType(
                    id=user.id, name=user.name, email=user.email, 
                    role=user.role, phone=user.phone
                )
        finally:
            db.close()
        return None

@strawberry.type
class Mutation:
    @strawberry.mutation
    def login(self, email: str, password: str) -> AuthPayload:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                raise Exception("User not found")

            # Verify password dengan truncation otomatis
            try:
                ok = verify_password(password, user.password)
            except Exception:
                ok = False

            # Fallback for seeded users: some initial DB rows use a known bcrypt hash for "password".
            # If verification failed but the stored hash matches the known seed, accept and rotate to PBKDF2.
            KNOWN_SEED_HASH = "$2a$10$lV/JwJm0pcWa7R.WP3PVqeCrTfqMb6fTm0TVEbqLunxUU.fUvxX1m"
            if not ok and user.password == KNOWN_SEED_HASH and password == "password":
                # rotate hash to the current default hasher
                new_hash = get_password_hash(password)
                user.password = new_hash
                db.add(user)
                db.commit()
                ok = True

            if not ok:
                raise Exception("Invalid password")
                
            token = create_access_token({"sub": user.email, "role": user.role})
            return AuthPayload(
                token=token,
                user=UserType(id=user.id, name=user.name, email=user.email, role=user.role, phone=user.phone)
            )
        except Exception as e:
            raise Exception(f"Login error: {str(e)}")
        finally:
            db.close()
    
    @strawberry.mutation
    def register(self, name: str, email: str, password: str, phone: str, role: str = "CUSTOMER") -> AuthPayload:
        db = SessionLocal()
        try:
            # Check email duplicate
            if db.query(User).filter(User.email == email).first():
                raise Exception("Email already registered")
            
            # Hash password dengan truncation otomatis
            try:
                hashed_pw = get_password_hash(password)
            except ValueError as ve:
                raise Exception(str(ve))
            
            # Create user baru
            new_user = User(name=name, email=email, password=hashed_pw, phone=phone, role=role)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Create token
            token = create_access_token({"sub": new_user.email, "role": new_user.role})
            
            return AuthPayload(
                token=token,
                user=UserType(id=new_user.id, name=new_user.name, email=new_user.email, role=new_user.role, phone=new_user.phone)
            )
        except Exception as e:
            db.rollback()
            raise Exception(f"Register error: {str(e)}")
        finally:
            db.close()

schema = strawberry.Schema(query=Query, mutation=Mutation)
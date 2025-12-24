from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import models, database, schema

# --- Init Database ---
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="User Service")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REST API MODELS (Untuk Frontend Lama) ---
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "CUSTOMER"
    phone: str = None

# --- REST ENDPOINTS (Legacy Support) ---

@app.post("/auth/login")
def login_rest(req: LoginRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user or not schema.verify_password(req.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    token = schema.create_access_token({"sub": str(user.id), "role": user.role})
    
    return {
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }

@app.post("/auth/register")
def register_rest(req: RegisterRequest, db: Session = Depends(database.get_db)):
    existing = db.query(models.User).filter(models.User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already used")
    
    hashed = schema.get_password_hash(req.password)
    new_user = models.User(
        name=req.name, 
        email=req.email, 
        password=hashed, 
        role=req.role,
        phone=req.phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = schema.create_access_token({"sub": str(new_user.id), "role": new_user.role})
    
    return {
        "token": token,
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role
        }
    }

@app.get("/users/me")
def get_me(token: str = None):
    return {"message": "User profile"}

# --- GRAPHQL ENDPOINT (New Requirement) ---
graphql_app = GraphQLRouter(schema.schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "User Service Running (REST + GraphQL)"}
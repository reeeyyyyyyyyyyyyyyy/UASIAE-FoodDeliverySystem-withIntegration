import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Perbaikan: Tambahkan pool_size, max_overflow, pool_recycle untuk robust connection
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,  # Recycle connection setiap 1 jam
    pool_pre_ping=True,  # Test connection sebelum dipakai
    connect_args={"connect_timeout": 30},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency Injection untuk FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
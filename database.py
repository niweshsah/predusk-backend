"""
Database Configuration and Session Management
Handles SQLAlchemy engine, session creation, and connection pooling
"""
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:niweshsah@localhost:5433/me_api_db"
)

# Convert postgres:// to postgresql:// for SQLAlchemy compatibility (Render uses postgres://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,
    max_overflow=10,
    echo=False  # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI routes
    Provides a database session and ensures it's closed after use
    
    Usage:
        @app.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    Should be called on application startup
    """
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def check_db_connection() -> bool:
    """
    Check if database connection is healthy
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1")) 
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

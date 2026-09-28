import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Load environment variables
load_dotenv()


# Get database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured in the .env file"
    )


# Create database engine
try:
    engine = create_engine(
        DATABASE_URL,
        echo=True
    )

    # Test database connection
    with engine.connect() as connection:
        print("Database connection successful")

except Exception as e:
    raise RuntimeError(
        f"Database connection failed: {e}"
    )


# Create database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for SQLAlchemy models
Base = declarative_base()


# Database dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
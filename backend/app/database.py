from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# check_same_thread=False lets FastAPI use SQLite from different threads
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Every table class in models.py inherits from this."""
    pass


def get_db():
    """FastAPI dependency: gives one session per request, then closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
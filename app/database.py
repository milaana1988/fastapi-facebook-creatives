import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.schemas import settings


db_url = settings.db_url

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    db_url
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    Yields a database session.

    The session is automatically closed when the generator is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.settings.settings import app_settings

Base = declarative_base()

engine = create_engine(app_settings.pg_connect_string)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency injection for the db, yields a session
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def fetch_connection():
    return SessionLocal()

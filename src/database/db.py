from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
DATABASE_URL = "postgresql://root:passwd@localhost:5432/financer"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency injection for the db, yields a session
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

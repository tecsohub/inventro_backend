from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Handle both PostgreSQL and SQLite
if settings.database_url.startswith("postgresql"):
    eng = create_engine(settings.database_url)
else:
    eng = create_engine(settings.database_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=eng)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def create_tables():
    Base.metadata.create_all(bind=eng)

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import os

# Check if we are connecting to Cloud SQL based on environment variable
IS_CLOUD_SQL = os.getenv("IS_CLOUD_SQL", "false").lower() == "true"

connector = None
getconn = None
db_url_prefix = None

if IS_CLOUD_SQL:
    try:
        # Use the Cloud SQL Python Connector
        from google.cloud.sql.connector import Connector

        # Cloud SQL Connection Details from environment variables
        INSTANCE_CONNECTION_NAME = os.environ["INSTANCE_CONNECTION_NAME"]  # e.g. 'project:region:instance'
        DB_USER = os.environ["DB_USER"]
        DB_PASS = os.environ.get("DB_PASS", "$$Harshit#9805$$").strip('\'"')
        DB_NAME = os.environ["DB_NAME"]
        DB_DRIVER = os.environ.get("DB_DRIVER", "psycopg2").strip('\'"')

        # Map driver name to SQLAlchemy dialect prefix
        if DB_DRIVER == "psycopg2":
            db_url_prefix = "postgresql+psycopg2://"
        elif DB_DRIVER == "pg8000":
            db_url_prefix = "postgresql+pg8000://"
        else:
            raise ValueError(f"Unsupported DB_DRIVER for Cloud SQL: {DB_DRIVER}")

        connector = Connector()

        def getconn():
            # The connector.connect method handles IAM Auth and secure connections
            conn = connector.connect(
                INSTANCE_CONNECTION_NAME, DB_DRIVER, user=DB_USER, password=DB_PASS, db=DB_NAME
            )
            return conn

    except ImportError:
        print("Warning: Google Cloud SQL connector not available. Falling back to local database.")
        IS_CLOUD_SQL = False

if IS_CLOUD_SQL and connector and getconn and db_url_prefix:
    engine = create_engine(db_url_prefix, creator=getconn)
else:
    # Fallback to original logic for local/other databases (e.g., SQLite)
    if settings.database_url.startswith("sqlite"):
        # SQLite requires connect_args for check_same_thread
        engine = create_engine(
            settings.database_url, connect_args={"check_same_thread": False}
        )
    else:
        # Other databases like local PostgreSQL, etc.
        engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)

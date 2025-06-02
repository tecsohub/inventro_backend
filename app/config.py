import os
from fastapi.security import OAuth2PasswordBearer
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Settings(BaseSettings):
    # Application settings
    app_name: str = "Inventory Management System"
    app_version: str = "1.0.0"
    app_description: str = "A simple inventory management system for managing products, employees, and managers."
    app_host: str = os.getenv("APP_HOST", "localhost")
    app_port: int = int(os.getenv("APP_PORT", 8000))
    # Database settings for postgres

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./inventory.db")  # Fallback for local
    # JWT Authentication
    SECRET_KEY: str = "IAMAUTH"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    class Config:
        env_file = ".env"

settings = Settings()
if not settings.SECRET_KEY:
    raise ValueError("SECRET KEY was not set in config. Fix it!")

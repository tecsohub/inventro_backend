from warnings import deprecated
from fastapi.security import OAuth2PasswordBearer
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./inventory.db"
    # JWT Authentication
    SECRET_KEY: str = "IAMAUTH"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    class Config:
        env_file = ".env"

settings = Settings()
if not settings.SECRET_KEY:
    raise ValueError("SECRET KEY was not set in config. Fix it!")

from datetime import timedelta
from datetime import datetime
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from jose import JWTError, ExpiredSignatureError
import jwt
from sqlalchemy.orm import Session

from app.config import settings, oauth2_scheme
from app.database import get_db
from app.models import Admin, Manager, Employee


def create_access_token(data: dict, expires_delta: Optional[timedelta]):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if role == "admin":
        user = db.query(Admin).filter(Admin.email == email).first()
    elif role == "manager":
        user = db.query(Manager).filter(Manager.email == email).first()
    elif role == "employee":
        user = db.query(Employee).filter(Employee.email == email).first()
    else:
        raise credentials_exception

    if user is None:
        raise credentials_exception
    return {"user": user, "role": role, "email": email, "id": user.id}

def roles_required(required_roles: List[str]):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for this role"
            )
        return current_user
    return role_checker

def is_email_unique(email: str, db: Session) -> bool:
    if (db.query(Manager).filter(Manager.email == email).first() or
        db.query(Employee).filter(Employee.email == email).first()):
        return False
    return True

import json
from datetime import timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import authenticate_user
from app.config import settings, pwd_context
from app.database import get_db
from app.models import Employee, Manager
from app.utils import create_access_token, is_email_unique
from app.validators import Token, EmployeeCreate, ManagerCreate

async def login_for_access_token_logic(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_data = await authenticate_user(form_data.username, form_data.password, db)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data["user"].email, "role": user_data["role"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def register_manager_logic(manager_data: ManagerCreate, db: Session = Depends(get_db)):
    if not is_email_unique(manager_data.email, db):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(manager_data.password)
    new_manager = Manager(
        email=manager_data.email,
        password=hashed_password,
        name=manager_data.name,
        company_name=manager_data.company_name,
        company_size=manager_data.company_size,
        is_verified=False,
        is_approved=False
    )
    db.add(new_manager)
    db.commit()
    db.refresh(new_manager)
    return json.dumps({"message": f"Manager {new_manager.name} registered successfully", "id": new_manager.id})

async def register_employee_logic(employee_data: EmployeeCreate, db: Session = Depends(get_db)):
    if not is_email_unique(employee_data.email, db):
        raise HTTPException(status_code=400, detail="Email already registered")

    manager = db.query(Manager).filter(Manager.id == employee_data.manager_id).first()
    if not manager:
        raise HTTPException(status_code=400, detail="Invalid manager_id: Manager does not exist")

    hashed_password = pwd_context.hash(employee_data.password)
    new_employee = Employee(
        email=employee_data.email,
        password=hashed_password,
        name=employee_data.name,
        role=employee_data.role,
        department=employee_data.department,
        phone=employee_data.phone,
        profile_picture=employee_data.profile_picture,
        manager_id=employee_data.manager_id,
        is_verified=False
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return {"message": f"Employee {new_employee.name} registered successfully", "employee_id": new_employee.id}

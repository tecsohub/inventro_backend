from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.controllers.auth import login_for_access_token_logic, register_employee_logic, register_manager_logic
from app.database import get_db
from app.utils import roles_required
from app.validators import EmployeeCreate, ManagerCreate, Token

router = APIRouter(tags=["Authentication"])

@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return await login_for_access_token_logic(form_data, db)

@router.post("/register/manager", status_code=status.HTTP_201_CREATED)
async def register_manager(manager_data: ManagerCreate, db: Session = Depends(get_db)):
    return await register_manager_logic(manager_data, db)

@router.post("/register/employee", status_code=status.HTTP_201_CREATED, dependencies=[Depends(roles_required(["manager"]))])
async def register_employee(employee_data: EmployeeCreate, db: Session = Depends(get_db)):
    return await register_employee_logic(employee_data, db)

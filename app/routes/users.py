from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils import get_current_user, roles_required
from app.validators import EmployeeCreate, ManagerCreate, Token

router = APIRouter(prefix="/user", tags=["User Management"])

@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    user = current_user["user"]
    role = current_user["role"]
    if role == "admin":
        return {"name": user.name, "email": user.email, "id": user.id}
    elif role == "manager":
        return {"name": user.name, "email": user.email, "company_name": user.company_name, "id": user.id}
    elif role == "employee":
        return user.to_dict()

# Employee-only endpoint
@router.get("/tasks")
async def employee_tasks(current_user: dict = Depends(roles_required("employee"))):
    return {"message": f"Welcome Employee {current_user['user'].name}, Dept: {current_user['user'].department}"}

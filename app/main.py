from datetime import timedelta
import json
from os import name
from re import U
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import authenticate_user
from app.config import settings, pwd_context
from app.database import get_db, create_tables
from app.models import Employee, Manager
from app.utils import create_access_token, get_current_user, is_email_unique, roles_required
from app.validators import EmployeeCreate, ManagerCreate, Token
from app.routes.auth import router as auth_router
from app.routes.companies import router as company_router
from app.routes.manager import router as manager_router
from app.routes.products import router as product_router
from app.routes.users import router as user_router


app = FastAPI()

create_tables()

# Admin-only endpoint
@app.get("/admin/dashboard")
async def admin_dashboard(current_user: dict = Depends(roles_required("admin"))):
    return {"message": f"Welcome Admin {current_user['user'].name}"}


app.include_router(auth_router)
app.include_router(company_router)
app.include_router(manager_router)
app.include_router(product_router)
app.include_router(user_router)

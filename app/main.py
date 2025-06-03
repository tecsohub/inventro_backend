from datetime import timedelta
import json
from os import name
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import authenticate_user
from app.config import settings, pwd_context
from app.database import get_db, create_tables
from app.models import Employee, Manager
from app.utils import create_access_token, get_current_user, is_email_unique, roles_required
from app.validators import EmployeeCreate, ManagerCreate, Token
from app.routes.products import router as product_router

app = FastAPI()

create_tables()

# Manager registration endpoint
@app.post("/register/manager", status_code=status.HTTP_201_CREATED)
async def register_manager(manager_data: ManagerCreate, db: Session = Depends(get_db)):
    # Check email uniqueness
    if not is_email_unique(manager_data.email, db):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password
    hashed_password = pwd_context.hash(manager_data.password)

    # Create new manager
    new_manager = Manager(
        email=manager_data.email,
        password=hashed_password,
        name=manager_data.name,
        company_name=manager_data.company_name,
        company_size=manager_data.company_size,
        is_verified=False,  # Default value
        is_approved=False   # Default value
    )

    # Save to database
    db.add(new_manager)
    db.commit()
    db.refresh(new_manager)

    return json.dumps({"message": f"Manager {new_manager.name} registered successfully", "id": new_manager.id})

# Employee registration endpoint
@app.post("/register/employee", status_code=status.HTTP_201_CREATED, dependencies=[Depends(roles_required("manager"))])
async def register_employee(employee_data: EmployeeCreate, db: Session = Depends(get_db)):
    # Check email uniqueness
    if not is_email_unique(employee_data.email, db):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Verify manager exists
    manager = db.query(Manager).filter(Manager.id == employee_data.manager_id).first()
    if not manager:
        raise HTTPException(status_code=400, detail="Invalid manager_id: Manager does not exist")

    # Hash the password
    hashed_password = pwd_context.hash(employee_data.password)

    # Create new employee
    new_employee = Employee(
        email=employee_data.email,
        password=hashed_password,
        name=employee_data.name,
        role=employee_data.role,
        department=employee_data.department,
        phone=employee_data.phone,
        profile_picture=employee_data.profile_picture,
        manager_id=employee_data.manager_id,
        is_verified=False  # Default value
    )

    # Save to database
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return {"message": f"Employee {new_employee.name} registered successfully", "employee_id": new_employee.id}

@app.get("/employees", response_model=list[EmployeeCreate], dependencies=[Depends(roles_required("manager"))])
async def list_employees(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """ List all employees under the current manager. """
    employees = db.query(Employee).filter(Employee.manager_id == current_user["user"].id).all()
    return employees

@app.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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

# Admin-only endpoint
@app.get("/admin/dashboard")
async def admin_dashboard(current_user: dict = Depends(roles_required("admin"))):
    return {"message": f"Welcome Admin {current_user['user'].name}"}

# Manager-only endpoint
@app.get("/manager/inventory")
async def manager_inventory(current_user: dict = Depends(roles_required("manager"))):
    return {"message": f"Welcome Manager {current_user['user'].name}, Company: {current_user['user'].company_name}"}

# Employee-only endpoint
@app.get("/employee/tasks")
async def employee_tasks(current_user: dict = Depends(roles_required("employee"))):
    return {"message": f"Welcome Employee {current_user['user'].name}, Dept: {current_user['user'].department}"}

@app.get("/user/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    user = current_user["user"]
    role = current_user["role"]
    if role == "admin":
        return {"name": user.name, "email": user.email, "id": user.id}
    elif role == "manager":
        return {"name": user.name, "email": user.email, "company_name": user.company_name, "id": user.id}
    elif role == "employee":
        return {"name": user.name, "email": user.email, "department": user.department, "id": user.id}


app.include_router(product_router)

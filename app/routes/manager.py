from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.controllers.manager import list_employees_logic
from app.controllers.products import get_products
from app.database import get_db
from app.utils import roles_required, get_current_user
from app.validators import EmployeeRead

# Manager-only endpoints
router = APIRouter(prefix="/manager", tags=["Manager Operations"])

@router.get("/employees", response_model=list[EmployeeRead], dependencies=[Depends(roles_required(["manager"]))])
async def list_employees(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return await list_employees_logic(current_user, db)

@router.get("/inventory")
async def manager_inventory(db: Session = Depends(get_db), current_user: dict = Depends(roles_required(["manager"]))):
    return get_products(db, company_id=current_user["user"].company_id)

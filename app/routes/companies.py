from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.controllers.companies import create_company_logic, get_company_logic, get_companies_logic
from app.database import get_db
from app.utils import get_current_user, roles_required # Assuming roles_required can be used if needed
from app.validators import CompanyCreate, CompanyRead

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.post("/", response_model=CompanyRead, status_code=status.HTTP_201_CREATED) # Or allow managers to create their first company
async def create_company(
    company_in: CompanyCreate,
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_user) # Optional: if creator info needs to be logged or for specific role checks
):
    """
    Create a new company.
    For the described flow (manager creates company then registers), this endpoint is open
    For simplicity, let's assume anyone handles company creation.
    """
    return create_company_logic(db, company_in)

@router.get("/{company_id}", response_model=CompanyRead) # Managers might need to see their company details
async def read_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific company by ID.
    """
    user_obj = current_user['user']
    if current_user['role'] == 'manager':
        if user_obj.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this company")
    elif current_user['role'] == 'employee':
        if user_obj.manager.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this company")
    return get_company_logic(db, company_id)

@router.get("/", response_model=List[CompanyRead], dependencies=[Depends(roles_required(["admin"]))]) # Listing all companies usually for admin
async def list_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
    # current_user: dict = Depends(get_current_user) # If non-admins can list some companies
):
    """
    List all companies. Typically an admin function.
    If managers/users need to search for companies (e.g., before registration),
    this might need different access controls or be an open endpoint.
    """
    return get_companies_logic(db, skip=skip, limit=limit)

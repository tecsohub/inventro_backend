from typing import List, Optional
import random
import string

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Company
from app.validators import CompanyCreate

def generate_company_id(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_company_logic(db: Session, company_in: CompanyCreate) -> Company:
    # Check if company with the same name already exists (optional, based on business rules)
    existing_company = db.query(Company).filter(Company.name == company_in.name).first()
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company with name '{company_in.name}' already exists.",
        )

    company_data = company_in.model_dump()
    company_data["id"] = generate_company_id()
    company = Company(**company_data)
    try:
        db.add(company)
        db.commit()
        db.refresh(company)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating company: {e.orig}",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating company: {str(e)}",
        )
    return company

def get_company_logic(db: Session, company_id: int) -> Optional[Company]:
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company

def get_companies_logic(db: Session, skip: int = 0, limit: int = 100) -> List[Company]:
    return db.query(Company).offset(skip).limit(limit).all()

def get_employees_and_managers_logic(db: Session, company_id: int) -> int:
    company = get_company_logic(db, company_id)
    return {
        "employees": company.number_of_employees if company else 0,
        "managers": company.number_of_managers if company else 0,
    }

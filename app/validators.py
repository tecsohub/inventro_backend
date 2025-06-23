from datetime import datetime
from pydantic import BaseModel, EmailStr  # Ensure EmailStr is imported
from typing import Optional, List

class Token(BaseModel):
    access_token: str
    token_type: str

# Company Pydantic Models
class CompanyBase(BaseModel):
    name: str
    size: int

class CompanyCreate(CompanyBase):
    pass

class CompanyRead(CompanyBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Manager registration request model
class ManagerCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    company_id: int  # Added
    phone: str | None = None
    profile_picture: str | None = None

# Employee registration request model
class EmployeeCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str | None = None
    department: str | None = None
    phone: str | None = None
    profile_picture: str | None = None
    manager_id: int  # Foreign key to Manager

class EmployeeRead(BaseModel):
    email: EmailStr
    name: str
    role: str | None = None
    department: str | None = None
    phone: str | None = None
    profile_picture: str | None = None
    manager_id: int  # Foreign key to Manager

class _ProductBase(BaseModel):
    part_number: str
    description: Optional[str] = None
    location: Optional[str] = None
    quantity: int
    batch_number: int
    expiry_date: datetime
    company_id: int  # Added


class ProductCreate(_ProductBase):
    pass

class ProductUpdate(BaseModel):
    description: Optional[str] = None
    location: Optional[str] = None
    quantity: Optional[int] = None
    batch_number: Optional[int] = None
    expiry_date: Optional[datetime] = None

class ProductRead(_ProductBase):
    id: int
    updated_on: datetime

    class Config:
        from_attributes = True

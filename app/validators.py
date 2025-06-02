from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

from pydantic import BaseModel, EmailStr

# Manager registration request model
class ManagerCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    company_name: str
    company_size: int
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

class _ProductBase(BaseModel):
    part_number: str
    description: Optional[str] = None
    location: Optional[str] = None
    quantity: int
    batch_number: int
    expiry_date: datetime
    manager_id: int  # Foreign key to Manager


class ProductCreate(BaseModel):
    part_number: str
    description: Optional[str] = None
    location: Optional[str] = None
    quantity: int
    batch_number: int
    expiry_date: datetime

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

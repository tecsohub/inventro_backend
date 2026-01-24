from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field, field_validator  # Ensure EmailStr is imported
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
    company_id: str  # Added
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
    company_id: str  # Added


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


# New Product Models
class NewProductBase(BaseModel):
    product_name: str
    product_type: str
    location: Optional[str] = None
    serial_number: Optional[str] = None
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    expiry: Optional[datetime] = None
    condition: Optional[str] = None
    quantity: int = 0
    price: Optional[Decimal] = None
    payment_status: Optional[str] = None
    receiver: Optional[str] = None
    receiver_contact: Optional[str] = None
    remark: Optional[str] = None
    company_id: str

    @field_validator('payment_status')
    @classmethod
    def validate_payment_status(cls, v):
        if v is not None and v not in ["Paid", "Pending", "Unpaid"]:
            raise ValueError('payment_status must be one of: Paid, Pending, Unpaid')
        return v


class NewProductCreate(NewProductBase):
    pass


class NewProductUpdate(BaseModel):
    product_name: Optional[str] = None
    product_type: Optional[str] = None
    location: Optional[str] = None
    serial_number: Optional[str] = None
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    expiry: Optional[datetime] = None
    condition: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[Decimal] = None
    payment_status: Optional[str] = None
    receiver: Optional[str] = None
    receiver_contact: Optional[str] = None
    remark: Optional[str] = None

    @field_validator('payment_status')
    @classmethod
    def validate_payment_status(cls, v):
        if v is not None and v not in ["Paid", "Pending", "Unpaid"]:
            raise ValueError('payment_status must be one of: Paid, Pending, Unpaid')
        return v


class NewProductRead(NewProductBase):
    id: int
    product_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# CSV Bulk Upload Models
class BulkUploadCreate(BaseModel):
    duplicate_action: str  # "skip" or "update"

    @field_validator('duplicate_action')
    @classmethod
    def validate_duplicate_action(cls, v):
        if v not in ["skip", "update"]:
            raise ValueError('duplicate_action must be either "skip" or "update"')
        return v


class BulkUploadRead(BaseModel):
    id: int
    filename: str
    upload_status: str
    total_records: int
    successful_records: int
    failed_records: int
    skipped_records: int
    updated_records: int
    error_details: Optional[str] = None
    duplicate_action: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# CSV Row validation for bulk upload
class CSVProductRow(BaseModel):
    product_name: str
    product_type: str
    location: Optional[str] = None
    serial_number: Optional[str] = None
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    expiry: Optional[str] = None  # Will be parsed to datetime
    condition: Optional[str] = None
    quantity: int = 0
    price: Optional[str] = None  # Will be parsed to Decimal
    payment_status: Optional[str] = None
    receiver: Optional[str] = None
    receiver_contact: Optional[str] = None
    remark: Optional[str] = None

    class Config:
        populate_by_name = True  # Allow both field names and aliases

    @field_validator('payment_status', mode='before')
    @classmethod
    def validate_payment_status(cls, v):
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        v_str = str(v).strip()
        if v_str and v_str not in ["Paid", "Pending", "Unpaid"]:
            raise ValueError('payment_status must be one of: Paid, Pending, Unpaid')
        return v_str if v_str else None

    @field_validator('quantity', mode='before')
    @classmethod
    def validate_quantity(cls, v):
        if isinstance(v, (int, float)):
            return int(v)
        if isinstance(v, str):
            try:
                return int(float(v))  # Handle string numbers with decimals
            except ValueError:
                raise ValueError('quantity must be a valid integer')
        return v

    @field_validator('price', mode='before')
    @classmethod
    def validate_price(cls, v):
        if v is None:
            return None
        # Convert any numeric type to string
        if isinstance(v, (int, float)):
            return str(v)
        return str(v) if v else None

    @field_validator('receiver_contact', mode='before')
    @classmethod
    def validate_receiver_contact(cls, v):
        if v is None:
            return None
        # Convert any numeric type to string (for phone numbers)
        if isinstance(v, (int, float)):
            return str(int(v))  # Remove decimal places for phone numbers

        # Handle string phone numbers with formatting
        v_str = str(v).strip()
        if not v_str:
            return None

        # Remove common phone number formatting characters
        cleaned = v_str.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')

        # Validate it's all digits
        if cleaned.isdigit():
            return cleaned

        return v_str  # Return original if not a valid phone format

    @field_validator('expiry', mode='before')
    @classmethod
    def validate_expiry(cls, v):
        if v is None:
            return None
        # Convert any type to string for date parsing
        return str(v) if v else None

    @field_validator('serial_number', 'batch_number', 'lot_number', mode='before')
    @classmethod
    def normalize_identifier(cls, v):
        # 1. Nulls stay null
        if v is None:
            return None

        # 2. Explicitly reject booleans (bool is a subclass of int)
        if isinstance(v, bool):
            raise ValueError('identifier fields cannot be boolean')

        # 3. Integers => string
        if isinstance(v, int):
            return str(v)

        # 4. Floats from Excel (e.g. 12345.0)
        if isinstance(v, float):
            if v.is_integer():
                return str(int(v))
            raise ValueError('identifier fields must not contain decimal values')

        # 5. Strings → stripped, empty collapsed to None
        if isinstance(v, str):
            v = v.strip()
            return v if v else None

        # 6. Anything else is invalid at the ingestion boundary
        raise ValueError(f'invalid type for identifier field: {type(v).__name__}')


# Audit Trail Models
class AuditTrailBase(BaseModel):
    product_id: int
    action_type: str  # "create", "update", "delete", "bulk_create", "bulk_update"
    changes: str  # JSON string
    changed_by: int
    company_id: str
    bulk_upload_id: Optional[int] = None


class AuditTrailRead(AuditTrailBase):
    id: int
    manager_name: Optional[str] = None
    product_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NewAuditTrailRead(AuditTrailBase):
    id: int
    product_unique_id: Optional[str] = None
    manager_name: Optional[str] = None
    product_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

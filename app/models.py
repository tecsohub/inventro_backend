from calendar import c
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(String(10), primary_key=True, index=True)  # Changed to String(10)
    name = Column(String)
    size = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    managers = relationship("Manager", back_populates="company", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="company", cascade="all, delete-orphan")
    new_products = relationship("NewProduct", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name}, size={self.size})>"

    @property
    def number_of_managers(self):
        return len(self.managers)

    @property
    def number_of_employees(self):
        return sum(manager.number_of_employees for manager in self.managers) if self.managers else 0

class Manager(Base):
    __tablename__ = "managers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String)
    is_verified = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    phone = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    otp = Column(String, nullable=True)
    otp_created_at = Column(DateTime, nullable=True)

    company_id = Column(String(10), ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="managers")

    employees = relationship("Employee", back_populates="manager")

    @property
    def number_of_employees(self):
        return len(self.employees)

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    staff_id = Column(String, nullable=True)  # Optional staff ID
    password = Column(String)
    name = Column(String)
    role = Column(String)
    department = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    manager_id = Column(Integer, ForeignKey("managers.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    token_expiry = Column(DateTime, nullable=True)

    manager = relationship("Manager", back_populates="employees")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "department": self.department,
            "phone": self.phone,
            "profile_picture": self.profile_picture,
            "is_verified": self.is_verified,
            "manager_id": self.manager_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "token_expiry": self.token_expiry.isoformat() if self.token_expiry else None,
        }

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    part_number = Column(String, unique=True, nullable=False)
    description = Column(String)
    location = Column(String)
    quantity = Column(Integer)
    batch_number = Column(Integer)
    updated_on = Column(DateTime(timezone=True), server_default=func.now())
    expiry_date = Column(DateTime(timezone=True))
    company_id = Column(String(10), ForeignKey("companies.id"), nullable=False)

    company = relationship("Company", back_populates="products")


class NewProduct(Base):
    __tablename__ = "new_products"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    product_type = Column(String, nullable=False)
    location = Column(String, nullable=True)
    serial_number = Column(String, nullable=True)
    batch_number = Column(String, nullable=True)
    lot_number = Column(String, nullable=True)
    expiry = Column(DateTime(timezone=True), nullable=True)
    condition = Column(String, nullable=True)
    quantity = Column(Integer, nullable=False, default=0)
    price = Column(Numeric(precision=10, scale=2), nullable=True)
    payment_status = Column(String, nullable=True)  # e.g., "Paid", "Pending", "Unpaid"
    receiver = Column(String, nullable=True)
    receiver_contact = Column(String, nullable=True)
    remark = Column(Text, nullable=True)

    # Derived ProductID from ProductName + ProductType + CompanyID
    product_id = Column(String, unique=True, nullable=False, index=True)

    company_id = Column(String(10), ForeignKey("companies.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    company = relationship("Company", back_populates="new_products")

    def __repr__(self):
        return f"<NewProduct(product_id={self.product_id}, name={self.product_name}, type={self.product_type})>"


class BulkUpload(Base):
    __tablename__ = "bulk_uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    upload_status = Column(String, default="processing")  # processing, completed, failed, partial
    total_records = Column(Integer, default=0)
    successful_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    skipped_records = Column(Integer, default=0)  # For duplicates when skip is chosen
    updated_records = Column(Integer, default=0)  # For duplicates when update is chosen
    error_details = Column(Text, nullable=True)  # JSON string of errors
    duplicate_action = Column(String, nullable=True)  # "skip", "update"

    uploaded_by = Column(Integer, ForeignKey("managers.id"), nullable=False)
    company_id = Column(String(10), ForeignKey("companies.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    manager = relationship("Manager")
    company = relationship("Company")

    def __repr__(self):
        return f"<BulkUpload(id={self.id}, filename={self.filename}, status={self.upload_status})>"


class AuditTrail(Base):
    """Audit trail for Product model - logs all changes (create, update, delete)"""
    __tablename__ = "audit_trail"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False, index=True)  # Reference to Product.id
    action_type = Column(String, nullable=False)  # "create", "update", "delete", "bulk_create", "bulk_update"
    changes = Column(Text, nullable=False)  # JSON string of all changes: {"field": {"old": x, "new": y}, ...}
    changed_by = Column(Integer, ForeignKey("managers.id"), nullable=False)
    company_id = Column(String(10), ForeignKey("companies.id"), nullable=False, index=True)
    bulk_upload_id = Column(Integer, ForeignKey("bulk_uploads.id"), nullable=True)  # Reference for bulk operations
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    manager = relationship("Manager")
    company = relationship("Company")
    bulk_upload = relationship("BulkUpload")

    def __repr__(self):
        return f"<AuditTrail(id={self.id}, product_id={self.product_id}, action={self.action_type})>"


class NewAuditTrail(Base):
    """Audit trail for NewProduct model - logs all changes (create, update, delete)"""
    __tablename__ = "new_audit_trail"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False, index=True)  # Reference to NewProduct.id
    product_unique_id = Column(String, nullable=True)  # Store the product_id string for reference
    action_type = Column(String, nullable=False)  # "create", "update", "delete", "bulk_create", "bulk_update"
    changes = Column(Text, nullable=False)  # JSON string of all changes: {"field": {"old": x, "new": y}, ...}
    changed_by = Column(Integer, ForeignKey("managers.id"), nullable=False)
    company_id = Column(String(10), ForeignKey("companies.id"), nullable=False, index=True)
    bulk_upload_id = Column(Integer, ForeignKey("bulk_uploads.id"), nullable=True)  # Reference for bulk operations
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    manager = relationship("Manager")
    company = relationship("Company")
    bulk_upload = relationship("BulkUpload")

    def __repr__(self):
        return f"<NewAuditTrail(id={self.id}, product_id={self.product_id}, action={self.action_type})>"

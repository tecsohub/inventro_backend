from calendar import c
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
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

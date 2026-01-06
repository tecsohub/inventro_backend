from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import Product, Company
from app.utils import get_current_user
from app.validators import ProductCreate, ProductUpdate
from app.controllers.audit import (
    log_product_create, log_product_update, log_product_delete, get_model_dict
)

def create_product(db: Session, product_in: ProductCreate, manager_id: Optional[int] = None) -> Product:
    # Ensure company exists
    company = db.query(Company).filter(Company.id == product_in.company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company with id {product_in.company_id} not found.",
        )
    product = Product(**product_in.model_dump())
    try:
        db.add(product)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating product: {e.orig}",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating product: {e}",
        )
    db.refresh(product)

    # Log audit trail
    if manager_id:
        log_product_create(db, product, manager_id)

    return product


def get_products(db: Session, company_id: Optional[int] = None) -> List[Product]:
    if company_id is None:
        # This case might be for admins, or needs further refinement
        # based on exact requirements for listing all products across all companies.
        return db.query(Product).all()
    return db.query(Product).filter(Product.company_id == company_id).all()


def get_product(db: Session, product_id: int, company_id: Optional[int] = None) -> Product:
    query = db.query(Product).filter(Product.id == product_id)
    if company_id is not None:
        query = query.filter(Product.company_id == company_id)

    product = query.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or not associated with your company")
    return product


def update_product(db: Session, product_id: int, update_in: ProductUpdate, company_id: Optional[int] = None, manager_id: Optional[int] = None) -> Product:
    product = get_product(db, product_id, company_id=company_id)

    # Capture old values before update for audit
    old_values = get_model_dict(product)

    for field, value in update_in.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    try:
        db.commit()
        db.refresh(product)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error product updation: {e.orig}",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating product: {e}",
        )

    # Log audit trail
    if manager_id:
        log_product_update(db, product, old_values, manager_id)

    return product


def delete_product(db: Session, product_id: int, company_id: Optional[int] = None, manager_id: Optional[int] = None) -> None:
    product = get_product(db, product_id, company_id=company_id)

    # Log audit trail before deletion
    if manager_id:
        log_product_delete(db, product, manager_id)

    try:
        db.delete(product)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error product deletion: {e.orig}",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting product: {e}",
        )

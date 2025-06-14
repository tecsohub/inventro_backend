from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# ────────────────────────────────────────────────────────────────────────────────
# NOTE:
#   • Replace the imports for `get_db`, `Base`, and `get_current_user` with the
#     ones used in YOUR project structure.
#   • This file bundles the Pydantic schemas, CRUD helpers, and the API router
#     for quick copy‑paste. Feel free to split them into separate modules.
# ────────────────────────────────────────────────────────────────────────────────

from app.database import get_db              # ⇦ your DB session dependency
from app.models import Product, Company                # ⇦ SQLAlchemy model shown above
from app.utils import get_current_user
from app.validators import ProductCreate, ProductUpdate  # ⇦ returns the current user

def create_product(db: Session, product_in: ProductCreate) -> Product:
    # Ensure company exists
    company = db.query(Company).filter(Company.id == product_in.company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company with id {product_in.company_id} not found.",
        )
    product = Product(**product_in.model_dump())  # ⇦ use model_dump() for Pydantic v2
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


def update_product(db: Session, product_id: int, update_in: ProductUpdate, company_id: Optional[int] = None) -> Product:
    product = get_product(db, product_id, company_id=company_id) # Pass company_id for scoped access
    # for field, value in update_in.dict(exclude_unset=True).items():
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
    return product


def delete_product(db: Session, product_id: int, company_id: Optional[int] = None) -> None:
    product = get_product(db, product_id, company_id=company_id) # Pass company_id for scoped access
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

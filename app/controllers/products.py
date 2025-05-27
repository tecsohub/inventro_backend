from typing import List

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
from app.models import Product                # ⇦ SQLAlchemy model shown above
from app.utils import get_current_user
from app.validators import ProductCreate, ProductUpdate  # ⇦ returns the current user

def create_product(db: Session, product_in: ProductCreate) -> Product:
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


def get_products(db: Session) -> List[Product]:
    return db.query(Product).all()


def get_product(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def update_product(db: Session, product_id: int, update_in: ProductUpdate) -> Product:
    product = get_product(db, product_id)
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
            detail=f"Error updating product: {e.orig}",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating product: {e}",
        )
    return product


def delete_product(db: Session, product_id: int) -> None:
    product = get_product(db, product_id)
    try:
        db.delete(product)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting product: {e.orig}",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting product: {e}",
        )

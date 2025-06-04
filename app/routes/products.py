from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# ────────────────────────────────────────────────────────────────────────────────

from app.controllers.products import create_product, delete_product, get_product, get_products, update_product
from app.database import get_db
from app.utils import get_current_user, roles_required
from app.validators import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])
@router.get("/", response_model=List[ProductRead], dependencies=[Depends(roles_required(["employee", "admin", "manager"]))])
def list_products(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """ List all products for the current user.
    If the user is a manager, only their products are returned.
    If the user is a regular user, products managed by their manager are returned.
    If the user is an admin, all products are returned.
    """
    if current_user['role'] == 'manager':
        # Managers can only see their own products
        return get_products(db, manager_id=current_user['id'])
    elif current_user['role'] == 'employee':
        # Users can see products, but not create or modify them
        return get_products(db, manager_id=current_user['manager_id'])
    elif current_user['role'] == 'admin':
        # Admins can see all products
        return get_products(db)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied for this role")


@router.get("/{product_id}", response_model=ProductRead, dependencies=[Depends(roles_required(["employee", "admin", "manager"]))])
def read_product(product_id: int, db: Session = Depends(get_db)):
    return get_product(db, product_id)

# ── CREATE (admin, manager) ─────────────────────────────────────────────────

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(roles_required(["admin", "manager"]))])
def create_new_product(product_in: ProductCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    product_in.manager_id = current_user['id']  # Set the manager_id from the current user
    return create_product(db, product_in)

# ── UPDATE (admin, manager) ─────────────────────────────────────────────────

@router.put("/{product_id}", response_model=ProductRead, dependencies=[Depends(roles_required(["admin", "manager"]))])
def update_existing_product(product_id: int, update_in: ProductUpdate, db: Session = Depends(get_db)):
    return update_product(db, product_id, update_in)

# ── DELETE (admin, manager) ─────────────────────────────────────────────────

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(roles_required(["admin", "manager"]))])
def remove_product(product_id: int, db: Session = Depends(get_db)):
    delete_product(db, product_id)
    return None

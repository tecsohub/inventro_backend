from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# ────────────────────────────────────────────────────────────────────────────────

from app.controllers.products import create_product, delete_product, get_product, get_products, update_product
from app.database import get_db
from app.models import Manager # Import Manager to access company_id
from app.utils import get_current_user, roles_required
from app.validators import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])
@router.get("/", response_model=List[ProductRead], dependencies=[Depends(roles_required(["employee", "admin", "manager"]))])
def list_products(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """ List all products.
    - Managers see products of their company.
    - Employees see products of the company their manager belongs to.
    - Admins see all products.
    """
    user_obj = current_user['user']
    if current_user['role'] == 'manager':
        return get_products(db, company_id=user_obj.company_id)
    elif current_user['role'] == 'employee':
        # Assuming employee object has manager relationship loaded, and manager has company_id
        if not user_obj.manager:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not associated with a manager")
        return get_products(db, company_id=user_obj.manager.company_id)
    elif current_user['role'] == 'admin':
        return get_products(db) # Admin sees all products
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied for this role")


@router.get("/{product_id}", response_model=ProductRead, dependencies=[Depends(roles_required(["employee", "admin", "manager"]))])
def read_product(product_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_obj = current_user['user']
    company_id_to_filter = None
    if current_user['role'] == 'manager':
        company_id_to_filter = user_obj.company_id
    elif current_user['role'] == 'employee':
        if not user_obj.manager:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not associated with a manager")
        company_id_to_filter = user_obj.manager.company_id
    # Admins can see any product, so no company_id_to_filter

    return get_product(db, product_id, company_id=company_id_to_filter)

# ── CREATE (admin, manager) ─────────────────────────────────────────────────

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(roles_required(["admin", "manager"]))])
def create_new_product(product_in: ProductCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_obj = current_user['user']
    if current_user['role'] == 'manager':
        # Managers can only create products for their own company
        product_in.company_id = user_obj.company_id
    elif current_user['role'] == 'admin':
        # Admins must specify company_id in the request.
        # The ProductCreate model already requires company_id.
        # Validation that the company_id exists is handled in create_product controller.
        pass
    else: # Should not happen due to roles_required
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")

    return create_product(db, product_in)

# ── UPDATE (admin, manager) ─────────────────────────────────────────────────

@router.put("/{product_id}", response_model=ProductRead, dependencies=[Depends(roles_required(["admin", "manager"]))])
def update_existing_product(product_id: int, update_in: ProductUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_obj = current_user['user']
    company_id_to_filter = None
    if current_user['role'] == 'manager':
        company_id_to_filter = user_obj.company_id
    # Admins can update any product, so no company_id_to_filter for them.
    # The get_product call within update_product will ensure manager can only update their company's product.
    return update_product(db, product_id, update_in, company_id=company_id_to_filter)

# ── DELETE (admin, manager) ─────────────────────────────────────────────────

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(roles_required(["admin", "manager"]))])
def remove_product(product_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_obj = current_user['user']
    company_id_to_filter = None
    if current_user['role'] == 'manager':
        company_id_to_filter = user_obj.company_id
    # Admins can delete any product.
    # The get_product call within delete_product will ensure manager can only delete their company's product.
    delete_product(db, product_id, company_id=company_id_to_filter)
    return None

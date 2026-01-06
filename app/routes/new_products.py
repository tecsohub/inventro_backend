from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.controllers.new_products import (
    create_new_product, get_new_product, get_new_products,
    update_new_product, delete_new_product,
    process_csv_bulk_upload, get_bulk_upload, get_bulk_uploads
)
from app.database import get_db
from app.models import Manager
from app.utils import get_current_user, roles_required
from app.validators import (
    NewProductCreate, NewProductRead, NewProductUpdate,
    BulkUploadCreate, BulkUploadRead
)

router = APIRouter(prefix="/new-products", tags=["New Products"])

# ── LIST NEW PRODUCTS ────────────────────────────────────────────────────────
@router.get("/", response_model=List[NewProductRead], dependencies=[Depends(roles_required(["employee", "admin", "manager"]))])
def list_new_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all new products.
    - Managers see products of their company.
    - Employees see products of the company their manager belongs to.
    - Admins see all products.
    """
    user_obj = current_user['user']
    if current_user['role'] == 'manager':
        return get_new_products(db, company_id=user_obj.company_id, skip=skip, limit=limit)
    elif current_user['role'] == 'employee':
        if not user_obj.manager:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not associated with a manager")
        return get_new_products(db, company_id=user_obj.manager.company_id, skip=skip, limit=limit)
    elif current_user['role'] == 'admin':
        return get_new_products(db, skip=skip, limit=limit)  # Admin sees all products
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied for this role")


# ── GET NEW PRODUCT ──────────────────────────────────────────────────────────
@router.get("/{product_id}", response_model=NewProductRead, dependencies=[Depends(roles_required(["employee", "admin", "manager"]))])
def read_new_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific new product by ID"""
    user_obj = current_user['user']
    company_id_to_filter = None

    if current_user['role'] == 'manager':
        company_id_to_filter = user_obj.company_id
    elif current_user['role'] == 'employee':
        if not user_obj.manager:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not associated with a manager")
        company_id_to_filter = user_obj.manager.company_id
    # Admins can see any product, so no company_id_to_filter

    return get_new_product(db, product_id, company_id=company_id_to_filter)


# ── CREATE NEW PRODUCT ──────────────────────────────────────────────────────
@router.post("/", response_model=NewProductRead, dependencies=[Depends(roles_required(["admin", "manager"]))])
def create_new_product_endpoint(
    product: NewProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new product (admin, manager only)"""
    user_obj = current_user['user']
    manager_id = None

    # Managers can only create products for their company
    if current_user['role'] == 'manager':
        if product.company_id != user_obj.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Managers can only create products for their own company"
            )
        manager_id = user_obj.id

    return create_new_product(db, product, manager_id=manager_id)


# ── UPDATE NEW PRODUCT ──────────────────────────────────────────────────────
@router.put("/{product_id}", response_model=NewProductRead, dependencies=[Depends(roles_required(["admin", "manager"]))])
def update_new_product_endpoint(
    product_id: int,
    product: NewProductUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a new product (admin, manager only)"""
    user_obj = current_user['user']
    company_id_to_filter = None
    manager_id = None

    # Managers can only update products of their company
    if current_user['role'] == 'manager':
        company_id_to_filter = user_obj.company_id
        manager_id = user_obj.id

    return update_new_product(db, product_id, product, company_id=company_id_to_filter, manager_id=manager_id)


# ── DELETE NEW PRODUCT ──────────────────────────────────────────────────────
@router.delete("/{product_id}", dependencies=[Depends(roles_required(["admin", "manager"]))])
def delete_new_product_endpoint(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a new product (admin, manager only)"""
    user_obj = current_user['user']
    company_id_to_filter = None
    manager_id = None

    # Managers can only delete products of their company
    if current_user['role'] == 'manager':
        company_id_to_filter = user_obj.company_id
        manager_id = user_obj.id

    success = delete_new_product(db, product_id, company_id=company_id_to_filter, manager_id=manager_id)
    if success:
        return {"message": "Product deleted successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete product")


# ── BULK UPLOAD CSV ─────────────────────────────────────────────────────────
@router.post("/bulk-upload", response_model=BulkUploadRead, dependencies=[Depends(roles_required(["manager"]))])
def bulk_upload_products(
    duplicate_action: str = Form(..., description="Action for duplicates: 'skip' or 'update'"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Bulk upload products from CSV file (managers only)"""
    user_obj = current_user['user']

    # Validate file type
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )

    # Validate file size (10MB limit)
    if file.size and file.size > 10 * 1024 * 1024:  # 10MB in bytes
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 10MB limit"
        )

    # Validate duplicate_action
    if duplicate_action not in ["skip", "update"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="duplicate_action must be either 'skip' or 'update'"
        )

    return process_csv_bulk_upload(
        db=db,
        file=file,
        manager_id=user_obj.id,
        company_id=user_obj.company_id,
        duplicate_action=duplicate_action
    )


# ── GET BULK UPLOAD STATUS ──────────────────────────────────────────────────
@router.get("/bulk-upload/{upload_id}", response_model=BulkUploadRead, dependencies=[Depends(roles_required(["manager", "admin"]))])
def get_bulk_upload_status(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get bulk upload status by ID"""
    user_obj = current_user['user']
    company_id_to_filter = None

    # Managers can only see uploads from their company
    if current_user['role'] == 'manager':
        company_id_to_filter = user_obj.company_id

    bulk_upload = get_bulk_upload(db, upload_id, company_id=company_id_to_filter)
    return BulkUploadRead.model_validate(bulk_upload)


# ── LIST BULK UPLOADS ───────────────────────────────────────────────────────
@router.get("/bulk-upload", response_model=List[BulkUploadRead], dependencies=[Depends(roles_required(["manager", "admin"]))])
def list_bulk_uploads(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all bulk uploads"""
    user_obj = current_user['user']
    company_id_to_filter = None

    # Managers can only see uploads from their company
    if current_user['role'] == 'manager':
        company_id_to_filter = user_obj.company_id

    bulk_uploads = get_bulk_uploads(db, company_id=company_id_to_filter, skip=skip, limit=limit)
    return [BulkUploadRead.model_validate(upload) for upload in bulk_uploads]

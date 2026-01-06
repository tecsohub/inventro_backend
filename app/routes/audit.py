"""
Audit Trail Routes
API endpoints for viewing audit logs (scoped by company)
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.controllers.audit import get_product_audit_logs, get_new_product_audit_logs
from app.database import get_db
from app.utils import get_current_user, roles_required
from app.validators import AuditTrailRead, NewAuditTrailRead

router = APIRouter(prefix="/audit", tags=["Audit Trail"])


# ── LIST PRODUCT AUDIT LOGS ────────────────────────────────────────────────────
@router.get("/products", response_model=List[AuditTrailRead], dependencies=[Depends(roles_required(["admin", "manager"]))])
def list_product_audit_logs(
    product_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List audit logs for Product model.
    - Managers see audit logs for their company only.
    - Admins see all audit logs.
    """
    user_obj = current_user['user']
    company_id_to_filter = None

    if current_user['role'] == 'manager':
        company_id_to_filter = user_obj.company_id

    return get_product_audit_logs(
        db,
        company_id=company_id_to_filter,
        product_id=product_id,
        skip=skip,
        limit=limit
    )


# ── GET PRODUCT AUDIT LOG BY PRODUCT ID ────────────────────────────────────────
@router.get("/products/{product_id}", response_model=List[AuditTrailRead], dependencies=[Depends(roles_required(["admin", "manager"]))])
def get_product_audit_log(
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get audit logs for a specific Product.
    - Managers see audit logs for their company only.
    - Admins see all audit logs.
    """
    user_obj = current_user['user']
    company_id_to_filter = None

    if current_user['role'] == 'manager':
        company_id_to_filter = user_obj.company_id

    return get_product_audit_logs(
        db,
        company_id=company_id_to_filter,
        product_id=product_id,
        skip=skip,
        limit=limit
    )


# ── LIST NEW PRODUCT AUDIT LOGS ────────────────────────────────────────────────
@router.get("/new-products", response_model=List[NewAuditTrailRead], dependencies=[Depends(roles_required(["admin", "manager"]))])
def list_new_product_audit_logs(
    product_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List audit logs for NewProduct model.
    - Managers see audit logs for their company only.
    - Admins see all audit logs.
    """
    user_obj = current_user['user']
    company_id_to_filter = None

    if current_user['role'] == 'manager':
        company_id_to_filter = user_obj.company_id

    return get_new_product_audit_logs(
        db,
        company_id=company_id_to_filter,
        product_id=product_id,
        skip=skip,
        limit=limit
    )


# ── GET NEW PRODUCT AUDIT LOG BY PRODUCT ID ────────────────────────────────────
@router.get("/new-products/{product_id}", response_model=List[NewAuditTrailRead], dependencies=[Depends(roles_required(["admin", "manager"]))])
def get_new_product_audit_log(
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get audit logs for a specific NewProduct.
    - Managers see audit logs for their company only.
    - Admins see all audit logs.
    """
    user_obj = current_user['user']
    company_id_to_filter = None

    if current_user['role'] == 'manager':
        company_id_to_filter = user_obj.company_id

    return get_new_product_audit_logs(
        db,
        company_id=company_id_to_filter,
        product_id=product_id,
        skip=skip,
        limit=limit
    )

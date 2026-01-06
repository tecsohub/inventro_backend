"""
Audit Trail Controller
Handles logging of all product changes (create, update, delete)
"""
import json
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Any, Dict

from sqlalchemy.orm import Session

from app.models import AuditTrail, NewAuditTrail, Product, NewProduct


def serialize_value(value: Any) -> Any:
    """Serialize a value for JSON storage"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def get_model_dict(model_instance) -> Dict[str, Any]:
    """Convert SQLAlchemy model to dict, excluding internal attributes"""
    result = {}
    for column in model_instance.__table__.columns:
        value = getattr(model_instance, column.name)
        result[column.name] = serialize_value(value)
    return result


def compute_changes(old_values: Dict[str, Any], new_values: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Compute the changes between old and new values"""
    changes = {}
    all_keys = set(old_values.keys()) | set(new_values.keys())

    for key in all_keys:
        old_val = serialize_value(old_values.get(key))
        new_val = serialize_value(new_values.get(key))

        if old_val != new_val:
            changes[key] = {"old": old_val, "new": new_val}

    return changes


# ─────────────────────────────────────────────────────────────────────────────
# Product Audit Trail Functions
# ─────────────────────────────────────────────────────────────────────────────

def log_product_create(
    db: Session,
    product: Product,
    manager_id: int,
    bulk_upload_id: Optional[int] = None
) -> AuditTrail:
    """Log product creation"""
    product_data = get_model_dict(product)

    # For create, all fields are "new"
    changes = {key: {"old": None, "new": value} for key, value in product_data.items()}

    action_type = "bulk_create" if bulk_upload_id else "create"

    audit = AuditTrail(
        product_id=product.id,
        action_type=action_type,
        changes=json.dumps(changes),
        changed_by=manager_id,
        company_id=product.company_id,
        bulk_upload_id=bulk_upload_id
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def log_product_update(
    db: Session,
    product: Product,
    old_values: Dict[str, Any],
    manager_id: int,
    bulk_upload_id: Optional[int] = None
) -> Optional[AuditTrail]:
    """Log product update"""
    new_values = get_model_dict(product)
    changes = compute_changes(old_values, new_values)

    # Only log if there are actual changes
    if not changes:
        return None

    action_type = "bulk_update" if bulk_upload_id else "update"

    audit = AuditTrail(
        product_id=product.id,
        action_type=action_type,
        changes=json.dumps(changes),
        changed_by=manager_id,
        company_id=product.company_id,
        bulk_upload_id=bulk_upload_id
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def log_product_delete(
    db: Session,
    product: Product,
    manager_id: int
) -> AuditTrail:
    """Log product deletion"""
    product_data = get_model_dict(product)

    # For delete, all fields become None
    changes = {key: {"old": value, "new": None} for key, value in product_data.items()}

    audit = AuditTrail(
        product_id=product.id,
        action_type="delete",
        changes=json.dumps(changes),
        changed_by=manager_id,
        company_id=product.company_id
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def get_product_audit_logs(
    db: Session,
    company_id: Optional[str] = None,
    product_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[AuditTrail]:
    """Get audit logs for products, optionally filtered by company and/or product"""
    query = db.query(AuditTrail).order_by(AuditTrail.created_at.desc())

    if company_id:
        query = query.filter(AuditTrail.company_id == company_id)
    if product_id:
        query = query.filter(AuditTrail.product_id == product_id)

    return query.offset(skip).limit(limit).all()


# ─────────────────────────────────────────────────────────────────────────────
# NewProduct Audit Trail Functions
# ─────────────────────────────────────────────────────────────────────────────

def log_new_product_create(
    db: Session,
    product: NewProduct,
    manager_id: int,
    bulk_upload_id: Optional[int] = None
) -> NewAuditTrail:
    """Log new product creation"""
    product_data = get_model_dict(product)

    # For create, all fields are "new"
    changes = {key: {"old": None, "new": value} for key, value in product_data.items()}

    action_type = "bulk_create" if bulk_upload_id else "create"

    audit = NewAuditTrail(
        product_id=product.id,
        product_unique_id=product.product_id,
        action_type=action_type,
        changes=json.dumps(changes),
        changed_by=manager_id,
        company_id=product.company_id,
        bulk_upload_id=bulk_upload_id
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def log_new_product_update(
    db: Session,
    product: NewProduct,
    old_values: Dict[str, Any],
    manager_id: int,
    bulk_upload_id: Optional[int] = None
) -> Optional[NewAuditTrail]:
    """Log new product update"""
    new_values = get_model_dict(product)
    changes = compute_changes(old_values, new_values)

    # Only log if there are actual changes
    if not changes:
        return None

    action_type = "bulk_update" if bulk_upload_id else "update"

    audit = NewAuditTrail(
        product_id=product.id,
        product_unique_id=product.product_id,
        action_type=action_type,
        changes=json.dumps(changes),
        changed_by=manager_id,
        company_id=product.company_id,
        bulk_upload_id=bulk_upload_id
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def log_new_product_delete(
    db: Session,
    product: NewProduct,
    manager_id: int
) -> NewAuditTrail:
    """Log new product deletion"""
    product_data = get_model_dict(product)

    # For delete, all fields become None
    changes = {key: {"old": value, "new": None} for key, value in product_data.items()}

    audit = NewAuditTrail(
        product_id=product.id,
        product_unique_id=product.product_id,
        action_type="delete",
        changes=json.dumps(changes),
        changed_by=manager_id,
        company_id=product.company_id
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def get_new_product_audit_logs(
    db: Session,
    company_id: Optional[str] = None,
    product_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[NewAuditTrail]:
    """Get audit logs for new products, optionally filtered by company and/or product"""
    query = db.query(NewAuditTrail).order_by(NewAuditTrail.created_at.desc())

    if company_id:
        query = query.filter(NewAuditTrail.company_id == company_id)
    if product_id:
        query = query.filter(NewAuditTrail.product_id == product_id)

    return query.offset(skip).limit(limit).all()

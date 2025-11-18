import json
import pandas as pd
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Optional, Dict, Any
from io import StringIO

from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import NewProduct, BulkUpload, Manager
from app.validators import NewProductCreate, NewProductUpdate, CSVProductRow, BulkUploadRead


def generate_product_id(product_name: str, product_type: str, company_id: str) -> str:
    """Generate unique product_id from ProductName + ProductType + CompanyID"""
    # Clean and format the components
    name_part = product_name.strip().replace(" ", "_").upper()
    type_part = product_type.strip().replace(" ", "_").upper()
    company_part = company_id.strip().upper()

    return f"{name_part}_{type_part}_{company_part}"


def create_new_product(db: Session, product_in: NewProductCreate) -> NewProduct:
    """Create a new product with generated product_id"""
    # Generate product_id
    product_id = generate_product_id(
        product_in.product_name,
        product_in.product_type,
        product_in.company_id
    )

    # Check if product_id already exists
    existing = db.query(NewProduct).filter(NewProduct.product_id == product_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with combination '{product_in.product_name}' + '{product_in.product_type}' already exists for this company"
        )

    product_data = product_in.model_dump()
    product_data["product_id"] = product_id

    product = NewProduct(**product_data)
    try:
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create product. Product may already exist."
        )


def get_new_product(db: Session, product_id: int, company_id: Optional[str] = None) -> NewProduct:
    """Get a new product by ID, optionally filtered by company"""
    query = db.query(NewProduct).filter(NewProduct.id == product_id)
    if company_id:
        query = query.filter(NewProduct.company_id == company_id)

    product = query.first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


def get_new_products(db: Session, company_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[NewProduct]:
    """Get all new products, optionally filtered by company"""
    query = db.query(NewProduct)
    if company_id:
        query = query.filter(NewProduct.company_id == company_id)

    return query.offset(skip).limit(limit).all()


def update_new_product(db: Session, product_id: int, product_in: NewProductUpdate, company_id: Optional[str] = None) -> NewProduct:
    """Update a new product"""
    product = get_new_product(db, product_id, company_id)

    update_data = product_in.model_dump(exclude_unset=True)

    # If product_name or product_type is being updated, regenerate product_id
    if "product_name" in update_data or "product_type" in update_data:
        new_name = update_data.get("product_name", product.product_name)
        new_type = update_data.get("product_type", product.product_type)
        new_product_id = generate_product_id(new_name, new_type, product.company_id)

        # Check if new product_id conflicts with existing products
        existing = db.query(NewProduct).filter(
            NewProduct.product_id == new_product_id,
            NewProduct.id != product_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with combination '{new_name}' + '{new_type}' already exists for this company"
            )

        update_data["product_id"] = new_product_id

    for field, value in update_data.items():
        setattr(product, field, value)

    try:
        db.commit()
        db.refresh(product)
        return product
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update product"
        )


def delete_new_product(db: Session, product_id: int, company_id: Optional[str] = None) -> bool:
    """Delete a new product"""
    product = get_new_product(db, product_id, company_id)

    db.delete(product)
    db.commit()
    return True


def parse_csv_date(date_str: str) -> Optional[datetime]:
    """Parse date string from CSV into datetime object"""
    if not date_str or date_str.strip() == "":
        return None

    date_str = date_str.strip()
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y/%m/%d"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unable to parse date: {date_str}")


def parse_csv_decimal(decimal_str: str) -> Optional[Decimal]:
    """Parse decimal string from CSV into Decimal object"""
    if not decimal_str or decimal_str.strip() == "":
        return None

    try:
        return Decimal(decimal_str.strip())
    except InvalidOperation:
        raise ValueError(f"Unable to parse decimal: {decimal_str}")


def process_csv_bulk_upload(
    db: Session,
    file: UploadFile,
    manager_id: int,
    company_id: str,
    duplicate_action: str
) -> BulkUploadRead:
    """Process CSV file for bulk product upload"""

    # Create bulk upload record
    bulk_upload = BulkUpload(
        filename=file.filename,
        upload_status="processing",
        duplicate_action=duplicate_action,
        uploaded_by=manager_id,
        company_id=company_id
    )
    db.add(bulk_upload)
    db.commit()
    db.refresh(bulk_upload)

    try:
        # Read CSV content
        content = file.file.read().decode('utf-8')
        csv_data = StringIO(content)

        # Load CSV into pandas DataFrame
        df = pd.read_csv(csv_data)

        # Map column names to lowercase (support both formats)
        column_mapping = {
            'ProductName': 'product_name',
            'ProductType': 'product_type',
            'Location': 'location',
            'SerialNumber': 'serial_number',
            'BatchNumber': 'batch_number',
            'LotNumber': 'lot_number',
            'Expiry': 'expiry',
            'Condition': 'condition',
            'Quantity': 'quantity',
            'Price': 'price',
            'PaymentStatus': 'payment_status',
            'Receiver': 'receiver',
            'ReceiverContact': 'receiver_contact',
            'Remark': 'remark'
        }

        # Normalize column names
        df.columns = [column_mapping.get(col, col.lower()) for col in df.columns]

        # Validate required columns
        required_columns = ['product_name', 'product_type', 'quantity']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        total_records = len(df)
        successful_records = 0
        failed_records = 0
        skipped_records = 0
        updated_records = 0
        errors = []

        # Process each row
        for index, row in df.iterrows():
            try:
                # Convert row to dict and handle NaN values
                row_dict = row.fillna("").to_dict()

                # Validate CSV row
                csv_row = CSVProductRow(**row_dict)

                # Convert to NewProduct data
                product_data = {
                    "product_name": csv_row.product_name,
                    "product_type": csv_row.product_type,
                    "location": csv_row.location if csv_row.location else None,
                    "serial_number": csv_row.serial_number if csv_row.serial_number else None,
                    "batch_number": csv_row.batch_number if csv_row.batch_number else None,
                    "lot_number": csv_row.lot_number if csv_row.lot_number else None,
                    "condition": csv_row.condition if csv_row.condition else None,
                    "quantity": csv_row.quantity,
                    "payment_status": csv_row.payment_status if csv_row.payment_status else None,
                    "receiver": csv_row.receiver if csv_row.receiver else None,
                    "receiver_contact": csv_row.receiver_contact if csv_row.receiver_contact else None,
                    "remark": csv_row.remark if csv_row.remark else None,
                    "company_id": company_id
                }

                # Parse date
                if csv_row.expiry:
                    try:
                        product_data["expiry"] = parse_csv_date(csv_row.expiry)
                    except ValueError as e:
                        errors.append(f"Row {index + 2}: {str(e)}")
                        failed_records += 1
                        continue

                # Parse price
                if csv_row.price:
                    try:
                        product_data["price"] = parse_csv_decimal(csv_row.price)
                    except ValueError as e:
                        errors.append(f"Row {index + 2}: {str(e)}")
                        failed_records += 1
                        continue

                # Generate product_id
                product_id = generate_product_id(
                    csv_row.product_name,
                    csv_row.product_type,
                    company_id
                )

                # Check if product already exists
                existing_product = db.query(NewProduct).filter(
                    NewProduct.product_id == product_id
                ).first()

                if existing_product:
                    if duplicate_action == "skip":
                        skipped_records += 1
                        continue
                    elif duplicate_action == "update":
                        # Update existing product
                        for field, value in product_data.items():
                            if field != "company_id":  # Don't update company_id
                                setattr(existing_product, field, value)
                        db.commit()
                        updated_records += 1
                        continue

                # Create new product
                product_data["product_id"] = product_id
                new_product = NewProduct(**product_data)
                db.add(new_product)
                db.commit()
                successful_records += 1

            except Exception as e:
                db.rollback()
                errors.append(f"Row {index + 2}: {str(e)}")
                failed_records += 1
                continue

        # Update bulk upload record
        bulk_upload.total_records = total_records
        bulk_upload.successful_records = successful_records
        bulk_upload.failed_records = failed_records
        bulk_upload.skipped_records = skipped_records
        bulk_upload.updated_records = updated_records

        if errors:
            bulk_upload.error_details = json.dumps(errors[:100])  # Limit errors stored

        if failed_records == 0:
            bulk_upload.upload_status = "completed"
        elif successful_records > 0 or updated_records > 0 or skipped_records > 0:
            bulk_upload.upload_status = "partial"
        else:
            bulk_upload.upload_status = "failed"

        db.commit()
        db.refresh(bulk_upload)

        return BulkUploadRead.model_validate(bulk_upload)

    except Exception as e:
        # Update bulk upload record with failure
        bulk_upload.upload_status = "failed"
        bulk_upload.error_details = json.dumps([str(e)])
        db.commit()
        db.refresh(bulk_upload)

        return BulkUploadRead.model_validate(bulk_upload)


def get_bulk_upload(db: Session, upload_id: int, company_id: Optional[str] = None) -> BulkUpload:
    """Get bulk upload record by ID"""
    query = db.query(BulkUpload).filter(BulkUpload.id == upload_id)
    if company_id:
        query = query.filter(BulkUpload.company_id == company_id)

    upload = query.first()
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bulk upload record not found"
        )
    return upload


def get_bulk_uploads(db: Session, company_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[BulkUpload]:
    """Get all bulk upload records, optionally filtered by company"""
    query = db.query(BulkUpload).order_by(BulkUpload.created_at.desc())
    if company_id:
        query = query.filter(BulkUpload.company_id == company_id)

    return query.offset(skip).limit(limit).all()

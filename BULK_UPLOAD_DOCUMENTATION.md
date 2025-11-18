# Bulk CSV Product Upload Feature

## Overview
This feature allows managers to bulk upload products using CSV files. The system supports duplicate handling, validation, and progress tracking.

## New API Endpoints

### 1. New Products Management
- `GET /new-products/` - List all new products (filtered by user role)
- `GET /new-products/{product_id}` - Get a specific product
- `POST /new-products/` - Create a single new product (admin/manager only)
- `PUT /new-products/{product_id}` - Update a product (admin/manager only)
- `DELETE /new-products/{product_id}` - Delete a product (admin/manager only)

### 2. Bulk Upload
- `POST /new-products/bulk-upload` - Upload CSV file for bulk product creation
- `GET /new-products/bulk-upload/{upload_id}` - Get bulk upload status
- `GET /new-products/bulk-upload` - List all bulk uploads

## CSV File Format

### Required Columns
- `product_name` (string, required)
- `product_type` (string, required)
- `quantity` (integer, required)

### Optional Columns
- `location` (string)
- `serial_number` (string)
- `batch_number` (string)
- `lot_number` (string)
- `expiry` (date, formats: YYYY-MM-DD, YYYY-MM-DD HH:MM:SS, MM/DD/YYYY, DD/MM/YYYY, YYYY/MM/DD)
- `condition` (string)
- `price` (decimal)
- `payment_status` (string, must be one of: "Paid", "Pending", "Unpaid")
- `receiver` (string)
- `receiver_contact` (string)
- `remark` (text)

### Sample CSV
```csv
product_name,product_type,location,serial_number,batch_number,lot_number,expiry,condition,quantity,price,payment_status,receiver,receiver_contact,remark
iPhone 14,Smartphone,Warehouse A,SN001,BATCH001,LOT001,2025-12-31,New,10,999.99,Paid,John Doe,+1234567890,Premium smartphone
Samsung Galaxy S23,Smartphone,Warehouse B,SN002,BATCH002,LOT002,2024-06-15,Refurbished,5,799.99,Pending,Jane Smith,+0987654321,Refurbished unit
```

## Product ID Generation
Products are automatically assigned a unique `product_id` based on the formula:
```
product_id = PRODUCTNAME_PRODUCTTYPE_COMPANYID
```

For example:
- Product Name: "iPhone 14"
- Product Type: "Smartphone"
- Company ID: "COMP001"
- Generated product_id: "IPHONE_14_SMARTPHONE_COMP001"

## Duplicate Handling
When uploading CSV files, managers can choose how to handle products that already exist:

### Skip Mode (`duplicate_action: "skip"`)
- Existing products are left unchanged
- New products are created
- Skipped products are counted in the response

### Update Mode (`duplicate_action: "update"`)
- Existing products are updated with new data from CSV
- New products are created
- Updated products are counted in the response

## Bulk Upload Process

### 1. File Upload
```bash
POST /new-products/bulk-upload
Content-Type: multipart/form-data

Form Data:
- file: products.csv (max 10MB)
- duplicate_action: "skip" or "update"
```

### 2. Processing
- File is validated (CSV format, size limit)
- Each row is parsed and validated
- Products are created/updated based on duplicate_action
- Progress is tracked in bulk_uploads table

### 3. Response
```json
{
  "id": 1,
  "filename": "products.csv",
  "upload_status": "completed", // or "partial", "failed"
  "total_records": 100,
  "successful_records": 95,
  "failed_records": 3,
  "skipped_records": 2,
  "updated_records": 0,
  "error_details": "[\"Row 5: Invalid date format\", \"Row 12: Missing required field\"]",
  "duplicate_action": "skip",
  "created_at": "2025-09-29T12:00:00Z",
  "updated_at": "2025-09-29T12:05:00Z"
}
```

## Validation Rules

### File Validation
- Must be CSV format (.csv extension)
- Maximum size: 10MB
- Must contain required columns: product_name, product_type, quantity

### Data Validation
- `product_name`: Non-empty string
- `product_type`: Non-empty string
- `quantity`: Valid integer (≥ 0)
- `price`: Valid decimal number (if provided)
- `expiry`: Valid date in supported formats (if provided)
- `payment_status`: Must be "Paid", "Pending", or "Unpaid" (if provided)

### Business Rules
- Product combinations (product_name + product_type) must be unique within a company
- Managers can only upload products for their own company
- All uploaded products are associated with the manager's company

## Error Handling

### Upload Errors
- Invalid file format → HTTP 400
- File too large → HTTP 400
- Invalid duplicate_action → HTTP 400
- Authentication/authorization errors → HTTP 401/403

### Processing Errors
Individual row errors are collected and returned in `error_details`:
- Invalid data types
- Missing required fields
- Date parsing failures
- Decimal parsing failures
- Business rule violations

## Security & Permissions

### Manager Permissions
- Upload CSV files for their company only
- View their company's bulk upload history
- Create/update/delete products for their company

### Employee Permissions
- View products from their manager's company
- Cannot upload or modify products

### Admin Permissions
- Full access to all products and bulk uploads
- Can manage products across all companies

## Database Schema

### NewProduct Table
- Contains the new product structure with extended fields
- Separate from the legacy `products` table
- Uses generated `product_id` as unique identifier

### BulkUpload Table
- Tracks all CSV upload operations
- Stores processing results and error details
- Links to manager who performed the upload

## API Examples

### Upload CSV File
```javascript
const formData = new FormData();
formData.append('file', csvFile);
formData.append('duplicate_action', 'skip');

const response = await fetch('/new-products/bulk-upload', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token
  },
  body: formData
});
```

### Check Upload Status
```javascript
const response = await fetch(`/new-products/bulk-upload/${uploadId}`, {
  headers: {
    'Authorization': 'Bearer ' + token
  }
});
```

### List Products
```javascript
const response = await fetch('/new-products/', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
});
```

## Frontend Integration Tips

1. **File Size Check**: Validate file size on frontend before upload
2. **Progress Indication**: Show upload progress and processing status
3. **Error Display**: Parse and display error_details in user-friendly format
4. **Duplicate Action**: Provide clear UI for choosing skip/update behavior
5. **Results Summary**: Display upload statistics (success/failed/skipped counts)

## Migration Notes

- New tables: `new_products`, `bulk_uploads`
- Legacy `products` table remains unchanged
- Both systems can coexist during transition
- Foreign key relationships maintained with existing `companies` and `managers` tables

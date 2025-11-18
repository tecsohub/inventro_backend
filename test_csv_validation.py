#!/usr/bin/env python3
"""
Test script to validate CSV processing with the updated validators
"""

import pandas as pd
from app.validators import CSVProductRow

def test_csv_validation():
    """Test the CSV validation with sample data"""

    # Sample data that mimics what pandas would read from CSV
    test_data = [
        {
            'ProductName': 'Test Product 1',
            'ProductType': 'Electronics',
            'Location': 'Warehouse A',
            'SerialNumber': 'SN001',
            'BatchNumber': 'BT001',
            'LotNumber': 'LT001',
            'Expiry': '2025-12-31',
            'Condition': 'New',
            'Quantity': 10,  # pandas will read this as int
            'Price': 299.99,  # pandas will read this as float
            'PaymentStatus': 'Paid',
            'Receiver': 'John Doe',
            'ReceiverContact': 1234567890,  # pandas will read phone as int
            'Remark': 'Test remark'
        },
        {
            'ProductName': 'Test Product 2',
            'ProductType': 'Books',
            'Location': '',  # Empty string
            'SerialNumber': '',
            'BatchNumber': '',
            'LotNumber': '',
            'Expiry': '',
            'Condition': 'Used',
            'Quantity': 5,
            'Price': '',  # Empty price
            'PaymentStatus': '',
            'Receiver': '',
            'ReceiverContact': '',  # Empty contact
            'Remark': ''
        }
    ]

    print("Testing CSV validation...")

    for i, row_data in enumerate(test_data, 1):
        try:
            print(f"\nTesting row {i}:")
            print(f"Data: {row_data}")

            # Validate with CSVProductRow
            csv_row = CSVProductRow(**row_data)
            print(f"✅ Validation successful!")
            print(f"   - product_name: {csv_row.product_name}")
            print(f"   - quantity: {csv_row.quantity} (type: {type(csv_row.quantity)})")
            print(f"   - price: {csv_row.price} (type: {type(csv_row.price)})")
            print(f"   - receiver_contact: {csv_row.receiver_contact} (type: {type(csv_row.receiver_contact)})")

        except Exception as e:
            print(f"❌ Validation failed: {e}")

def test_pandas_csv_reading():
    """Test reading the actual CSV file with pandas"""

    try:
        print("\n" + "="*50)
        print("Testing CSV file reading with pandas...")

        # Read the sample CSV file
        df = pd.read_csv('sample_products.csv')
        print(f"CSV loaded successfully with {len(df)} rows")

        print("\nColumn data types:")
        print(df.dtypes)

        print("\nFirst few rows:")
        print(df.head())

        # Test validation on actual CSV data
        print("\nTesting validation on CSV rows:")
        for index, row in df.head(3).iterrows():  # Test first 3 rows
            try:
                print(f"\nRow {index + 1}:")
                row_dict = row.fillna("").to_dict()
                print(f"Row data types: {[(k, type(v)) for k, v in row_dict.items()]}")

                csv_row = CSVProductRow(**row_dict)
                print(f"✅ Row {index + 1} validation successful!")

            except Exception as e:
                print(f"❌ Row {index + 1} validation failed: {e}")

    except FileNotFoundError:
        print("❌ sample_products.csv not found")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")

if __name__ == "__main__":
    test_csv_validation()
    test_pandas_csv_reading()

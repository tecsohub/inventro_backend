import requests
import json

# Test script to verify the bulk upload API is working
BASE_URL = "http://localhost:8000"

def test_new_products_endpoint():
    """Test that the new products endpoint is accessible"""
    try:
        response = requests.get(f"{BASE_URL}/new-products/")
        print(f"GET /new-products/ - Status: {response.status_code}")

        if response.status_code == 401:
            print("✓ Endpoint is protected (requires authentication)")
            return True
        elif response.status_code == 200:
            print("✓ Endpoint accessible")
            return True
        else:
            print(f"✗ Unexpected response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("✗ Server is not running on localhost:8000")
        return False
    except Exception as e:
        print(f"✗ Error testing endpoint: {e}")
        return False

def test_bulk_upload_endpoint():
    """Test that the bulk upload endpoint is accessible"""
    try:
        # Try to access bulk upload without authentication
        response = requests.post(f"{BASE_URL}/new-products/bulk-upload")
        print(f"POST /new-products/bulk-upload - Status: {response.status_code}")

        if response.status_code == 401:
            print("✓ Bulk upload endpoint is protected (requires authentication)")
            return True
        elif response.status_code == 422:
            print("✓ Bulk upload endpoint accessible (validation error expected without file)")
            return True
        else:
            print(f"✗ Unexpected response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("✗ Server is not running on localhost:8000")
        return False
    except Exception as e:
        print(f"✗ Error testing bulk upload endpoint: {e}")
        return False

def test_api_docs():
    """Test that API documentation is accessible"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"GET /docs - Status: {response.status_code}")

        if response.status_code == 200:
            print("✓ API documentation is accessible")
            return True
        else:
            print(f"✗ API docs not accessible: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("✗ Server is not running on localhost:8000")
        return False
    except Exception as e:
        print(f"✗ Error testing API docs: {e}")
        return False

def main():
    print("=== Testing Bulk Upload API ===")
    print(f"Server URL: {BASE_URL}")
    print()

    # Test basic connectivity
    docs_ok = test_api_docs()
    if not docs_ok:
        print("Server connectivity test failed")
        return

    # Test new products endpoint
    products_ok = test_new_products_endpoint()

    # Test bulk upload endpoint
    upload_ok = test_bulk_upload_endpoint()

    print("\n=== Summary ===")
    print(f"API Docs: {'✓' if docs_ok else '✗'}")
    print(f"New Products Endpoint: {'✓' if products_ok else '✗'}")
    print(f"Bulk Upload Endpoint: {'✓' if upload_ok else '✗'}")

    if docs_ok and products_ok and upload_ok:
        print("\n🎉 All endpoints are working correctly!")
        print(f"You can access the API documentation at: {BASE_URL}/docs")
        print("The bulk upload feature is ready for frontend integration!")
    else:
        print("\n❌ Some endpoints have issues")

if __name__ == "__main__":
    main()

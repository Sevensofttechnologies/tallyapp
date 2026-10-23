"""
Comprehensive CRUD Test Script
Tests all API endpoints for Application Starter Kit
"""

import httpx
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8002/api"

# Store tokens and IDs for testing
test_data = {
    "access_token": None,
    "user_id": None,
    "company_id": None,
    "second_user_id": None,
    "permission_id": None
}


def print_result(test_name: str, success: bool, response=None, error=None):
    """Print test result"""
    status = "[PASS]" if success else "[FAIL]"
    print(f"\n{status} - {test_name}")
    if response:
        print(f"   Status: {response.status_code}")
        try:
            data = response.json()
            if "data" in data:
                print(f"   Data: {json.dumps(data.get('data', {}), indent=2, default=str)[:500]}")
            if "message" in data:
                print(f"   Message: {data.get('message')}")
            if "error" in data:
                print(f"   Error: {data.get('error')}")
        except:
            print(f"   Response: {response.text[:200]}")
    if error:
        print(f"   Error: {error}")


def get_headers():
    """Get authorization headers"""
    if test_data["access_token"]:
        return {"Authorization": f"Bearer {test_data['access_token']}"}
    return {}


# ==================== AUTH TESTS ====================

def test_register_user():
    """Test user registration"""
    print("\n" + "="*60)
    print("AUTH TESTS")
    print("="*60)
    
    payload = {
        "email": f"admin_{datetime.now().strftime('%H%M%S')}@test.com",
        "password": "Test@123456",
        "first_name": "Admin",
        "last_name": "User",
        "phone": "9876543210"
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/auth/register", json=payload)
        success = response.status_code == 201
        if success:
            data = response.json()
            test_data["user_id"] = data.get("data", {}).get("id")
        print_result("Register User", success, response)
        return success
    except Exception as e:
        print_result("Register User", False, error=str(e))
        return False


def test_login_user():
    """Test user login"""
    payload = {
        "email": f"admin_{datetime.now().strftime('%H%M%S')}@test.com",
        "password": "Test@123456"
    }
    
    # First register
    reg_payload = {
        "email": payload["email"],
        "password": payload["password"],
        "first_name": "Login",
        "last_name": "Test",
        "phone": "9876543210"
    }
    httpx.post(f"{BASE_URL}/auth/register", json=reg_payload)
    
    try:
        response = httpx.post(f"{BASE_URL}/auth/login", json=payload)
        success = response.status_code == 200
        if success:
            data = response.json()
            test_data["access_token"] = data.get("data", {}).get("access_token")
            test_data["user_id"] = data.get("data", {}).get("user", {}).get("id")
        print_result("Login User", success, response)
        return success
    except Exception as e:
        print_result("Login User", False, error=str(e))
        return False


def test_get_current_user():
    """Test get current user"""
    try:
        response = httpx.get(f"{BASE_URL}/auth/me", headers=get_headers())
        success = response.status_code == 200
        print_result("Get Current User", success, response)
        return success
    except Exception as e:
        print_result("Get Current User", False, error=str(e))
        return False


def test_change_password():
    """Test change password"""
    payload = {
        "current_password": "Test@123456",
        "new_password": "NewTest@123456"
    }
    
    try:
        response = httpx.put(f"{BASE_URL}/auth/change-password", json=payload, headers=get_headers())
        success = response.status_code == 200
        print_result("Change Password", success, response)
        
        # Change back for further tests
        if success:
            payload2 = {
                "current_password": "NewTest@123456",
                "new_password": "Test@123456"
            }
            httpx.put(f"{BASE_URL}/auth/change-password", json=payload2, headers=get_headers())
        
        return success
    except Exception as e:
        print_result("Change Password", False, error=str(e))
        return False


# ==================== COMPANY TESTS ====================

def test_create_company():
    """Test create company"""
    print("\n" + "="*60)
    print("COMPANY TESTS")
    print("="*60)
    
    payload = {
        "name": f"Test Company {datetime.now().strftime('%H%M%S')}",
        "email": f"company_{datetime.now().strftime('%H%M%S')}@test.com",
        "phone": "9876543210",
        "address": "123 Test Street",
        "city": "Mumbai",
        "state": "Maharashtra",
        "country": "India",
        "zip_code": "400001",
        "website": "https://testcompany.com",
        "industry": "Technology"
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/companies", json=payload, headers=get_headers())
        success = response.status_code == 201
        if success:
            data = response.json()
            test_data["company_id"] = data.get("data", {}).get("id")
        print_result("Create Company", success, response)
        return success
    except Exception as e:
        print_result("Create Company", False, error=str(e))
        return False


def test_get_companies():
    """Test get all companies"""
    try:
        response = httpx.get(f"{BASE_URL}/companies", headers=get_headers())
        success = response.status_code == 200
        print_result("Get All Companies", success, response)
        return success
    except Exception as e:
        print_result("Get All Companies", False, error=str(e))
        return False


def test_get_company_by_id():
    """Test get company by ID"""
    if not test_data["company_id"]:
        print_result("Get Company By ID", False, error="No company ID available")
        return False
    
    try:
        response = httpx.get(f"{BASE_URL}/companies/{test_data['company_id']}", headers=get_headers())
        success = response.status_code == 200
        print_result("Get Company By ID", success, response)
        return success
    except Exception as e:
        print_result("Get Company By ID", False, error=str(e))
        return False


def test_update_company():
    """Test update company"""
    if not test_data["company_id"]:
        print_result("Update Company", False, error="No company ID available")
        return False
    
    payload = {
        "name": f"Updated Company {datetime.now().strftime('%H%M%S')}",
        "phone": "1234567890",
        "industry": "Software"
    }
    
    try:
        response = httpx.put(f"{BASE_URL}/companies/{test_data['company_id']}", json=payload, headers=get_headers())
        success = response.status_code == 200
        print_result("Update Company", success, response)
        return success
    except Exception as e:
        print_result("Update Company", False, error=str(e))
        return False


def test_select_company():
    """Test select company"""
    if not test_data["company_id"]:
        print_result("Select Company", False, error="No company ID available")
        return False
    
    try:
        response = httpx.post(f"{BASE_URL}/companies/select/{test_data['company_id']}", headers=get_headers())
        success = response.status_code == 200
        print_result("Select Company", success, response)
        return success
    except Exception as e:
        print_result("Select Company", False, error=str(e))
        return False


# ==================== USER TESTS ====================

def test_create_user_in_company():
    """Test create user in company"""
    print("\n" + "="*60)
    print("USER TESTS")
    print("="*60)
    
    if not test_data["company_id"]:
        print_result("Create User In Company", False, error="No company ID available")
        return False
    
    payload = {
        "email": f"user_{datetime.now().strftime('%H%M%S')}@test.com",
        "password": "User@123456",
        "first_name": "Test",
        "last_name": "User",
        "phone": "8765432109",
        "role": "user"
    }
    
    try:
        response = httpx.post(
            f"{BASE_URL}/companies/{test_data['company_id']}/users", 
            json=payload, 
            headers=get_headers()
        )
        success = response.status_code == 201
        if success:
            data = response.json()
            test_data["second_user_id"] = data.get("data", {}).get("id")
        print_result("Create User In Company", success, response)
        return success
    except Exception as e:
        print_result("Create User In Company", False, error=str(e))
        return False


def test_get_company_users():
    """Test get all users in company"""
    if not test_data["company_id"]:
        print_result("Get Company Users", False, error="No company ID available")
        return False
    
    try:
        response = httpx.get(
            f"{BASE_URL}/companies/{test_data['company_id']}/users", 
            headers=get_headers()
        )
        success = response.status_code == 200
        print_result("Get Company Users", success, response)
        return success
    except Exception as e:
        print_result("Get Company Users", False, error=str(e))
        return False


def test_get_user_by_id():
    """Test get user by ID"""
    if not test_data["company_id"] or not test_data["second_user_id"]:
        print_result("Get User By ID", False, error="No company or user ID available")
        return False
    
    try:
        response = httpx.get(
            f"{BASE_URL}/companies/{test_data['company_id']}/users/{test_data['second_user_id']}", 
            headers=get_headers()
        )
        success = response.status_code == 200
        print_result("Get User By ID", success, response)
        return success
    except Exception as e:
        print_result("Get User By ID", False, error=str(e))
        return False


def test_update_user():
    """Test update user"""
    if not test_data["company_id"] or not test_data["second_user_id"]:
        print_result("Update User", False, error="No company or user ID available")
        return False
    
    payload = {
        "first_name": "Updated",
        "last_name": "TestUser",
        "phone": "9999999999"
    }
    
    try:
        response = httpx.put(
            f"{BASE_URL}/companies/{test_data['company_id']}/users/{test_data['second_user_id']}", 
            json=payload, 
            headers=get_headers()
        )
        success = response.status_code == 200
        print_result("Update User", success, response)
        return success
    except Exception as e:
        print_result("Update User", False, error=str(e))
        return False


def test_update_user_role():
    """Test update user role"""
    if not test_data["company_id"] or not test_data["second_user_id"]:
        print_result("Update User Role", False, error="No company or user ID available")
        return False
    
    payload = {"role": "manager"}
    
    try:
        response = httpx.put(
            f"{BASE_URL}/companies/{test_data['company_id']}/users/{test_data['second_user_id']}/role", 
            json=payload, 
            headers=get_headers()
        )
        success = response.status_code == 200
        print_result("Update User Role", success, response)
        return success
    except Exception as e:
        print_result("Update User Role", False, error=str(e))
        return False


# ==================== PERMISSION TESTS ====================

def test_get_permissions():
    """Test get all permissions"""
    print("\n" + "="*60)
    print("PERMISSION TESTS")
    print("="*60)
    
    try:
        response = httpx.get(f"{BASE_URL}/permissions", headers=get_headers())
        success = response.status_code == 200
        print_result("Get All Permissions", success, response)
        return success
    except Exception as e:
        print_result("Get All Permissions", False, error=str(e))
        return False


def test_create_permission():
    """Test create permission"""
    payload = {
        "resource": "reports",
        "action": "read",
        "description": "Read reports permission"
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/permissions", json=payload, headers=get_headers())
        success = response.status_code == 201
        if success:
            data = response.json()
            test_data["permission_id"] = data.get("data", {}).get("id")
        print_result("Create Permission", success, response)
        return success
    except Exception as e:
        print_result("Create Permission", False, error=str(e))
        return False


def test_check_permission():
    """Test check permission"""
    payload = {
        "resource": "user",
        "action": "read",
        "company_id": test_data.get("company_id")
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/permissions/check", json=payload, headers=get_headers())
        success = response.status_code == 200
        print_result("Check Permission", success, response)
        return success
    except Exception as e:
        print_result("Check Permission", False, error=str(e))
        return False


def test_get_role_permissions():
    """Test get role permissions"""
    try:
        response = httpx.get(f"{BASE_URL}/permissions/role/admin", headers=get_headers())
        success = response.status_code == 200
        print_result("Get Role Permissions", success, response)
        return success
    except Exception as e:
        print_result("Get Role Permissions", False, error=str(e))
        return False


# ==================== DELETE TESTS ====================

def test_delete_user():
    """Test delete user"""
    print("\n" + "="*60)
    print("DELETE TESTS")
    print("="*60)
    
    if not test_data["company_id"] or not test_data["second_user_id"]:
        print_result("Delete User", False, error="No company or user ID available")
        return False
    
    try:
        response = httpx.delete(
            f"{BASE_URL}/companies/{test_data['company_id']}/users/{test_data['second_user_id']}", 
            headers=get_headers()
        )
        success = response.status_code == 200
        print_result("Delete User", success, response)
        return success
    except Exception as e:
        print_result("Delete User", False, error=str(e))
        return False


def test_delete_company():
    """Test delete company"""
    if not test_data["company_id"]:
        print_result("Delete Company", False, error="No company ID available")
        return False
    
    try:
        response = httpx.delete(f"{BASE_URL}/companies/{test_data['company_id']}", headers=get_headers())
        success = response.status_code == 200
        print_result("Delete Company", success, response)
        return success
    except Exception as e:
        print_result("Delete Company", False, error=str(e))
        return False


# ==================== HEALTH CHECK ====================

def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*60)
    print("HEALTH CHECK")
    print("="*60)
    
    try:
        response = httpx.get("http://127.0.0.1:8002/health")
        success = response.status_code == 200
        print_result("Health Check", success, response)
        return success
    except Exception as e:
        print_result("Health Check", False, error=str(e))
        return False


def test_root_endpoint():
    """Test root endpoint"""
    try:
        response = httpx.get("http://127.0.0.1:8002/")
        success = response.status_code == 200
        print_result("Root Endpoint", success, response)
        return success
    except Exception as e:
        print_result("Root Endpoint", False, error=str(e))
        return False


# ==================== RUN ALL TESTS ====================

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("APPLICATION STARTER KIT - CRUD TEST SUITE")
    print(f"   Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = {
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    # Health Check
    tests = [
        ("Health Check", test_health_check),
        ("Root Endpoint", test_root_endpoint),
        
        # Auth Tests
        ("Register User", test_register_user),
        ("Login User", test_login_user),
        ("Get Current User", test_get_current_user),
        ("Change Password", test_change_password),
        
        # Company Tests
        ("Create Company", test_create_company),
        ("Get All Companies", test_get_companies),
        ("Get Company By ID", test_get_company_by_id),
        ("Update Company", test_update_company),
        ("Select Company", test_select_company),
        
        # User Tests
        ("Create User In Company", test_create_user_in_company),
        ("Get Company Users", test_get_company_users),
        ("Get User By ID", test_get_user_by_id),
        ("Update User", test_update_user),
        ("Update User Role", test_update_user_role),
        
        # Permission Tests
        ("Get All Permissions", test_get_permissions),
        ("Create Permission", test_create_permission),
        ("Check Permission", test_check_permission),
        ("Get Role Permissions", test_get_role_permissions),
        
        # Delete Tests
        ("Delete User", test_delete_user),
        ("Delete Company", test_delete_company),
    ]
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            if success:
                results["passed"] += 1
            else:
                results["failed"] += 1
            results["tests"].append({"name": test_name, "passed": success})
        except Exception as e:
            results["failed"] += 1
            results["tests"].append({"name": test_name, "passed": False, "error": str(e)})
    
    # Print Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"   Total Tests: {len(tests)}")
    print(f"   Passed: {results['passed']}")
    print(f"   Failed: {results['failed']}")
    print(f"   Success Rate: {(results['passed']/len(tests))*100:.1f}%")
    print("="*60)
    
    if results["failed"] > 0:
        print("\nFailed Tests:")
        for test in results["tests"]:
            if not test["passed"]:
                print(f"   - {test['name']}")
    
    print(f"\n   Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    return results


if __name__ == "__main__":
    run_all_tests()

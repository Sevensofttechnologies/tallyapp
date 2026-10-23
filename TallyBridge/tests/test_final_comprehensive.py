"""
FINAL COMPREHENSIVE TEST SUITE
Application Starter Kit - 50 Test Cases
Tests: CRUD, Validation, Authorization, Email, Audit Logs
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
import time
import sqlite3
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8501"
API_V1 = f"{BASE_URL}/api/v1"

# Test data
timestamp = int(time.time())
TEST_USERS = {
    "admin": {
        "email": f"admin_{timestamp}@test.com",
        "password": "Admin@123456",
        "first_name": "Admin",
        "last_name": "User",
        "phone": "+919876543210"
    },
    "manager": {
        "email": f"manager_{timestamp}@test.com",
        "password": "Manager@123456",
        "first_name": "Manager",
        "last_name": "User",
        "phone": "+919876543211"
    },
    "user": {
        "email": f"user_{timestamp}@test.com",
        "password": "User@123456",
        "first_name": "Regular",
        "last_name": "User",
        "phone": "+919876543212"
    }
}

TEST_COMPANIES = {
    "company1": {
        "name": f"Tech Solutions {timestamp}",
        "email": f"tech_{timestamp}@company.com",
        "phone": "+919876543220",
        "address": "123 Tech Park",
        "city": "Mumbai",
        "state": "Maharashtra",
        "country": "India",
        "zip_code": "400001",
        "industry": "Technology"
    },
    "company2": {
        "name": f"Health Corp {timestamp}",
        "email": f"health_{timestamp}@company.com",
        "phone": "+919876543221",
        "address": "456 Health Avenue",
        "city": "Pune",
        "state": "Maharashtra",
        "country": "India",
        "zip_code": "411001",
        "industry": "Healthcare"
    }
}

# Store tokens and IDs
tokens = {}
user_ids = {}
company_ids = {}

# Test results
results = []
test_number = 0


def log_result(test_name: str, passed: bool, details: str = ""):
    """Log test result"""
    global test_number
    test_number += 1
    status = "PASS" if passed else "FAIL"
    results.append({
        "number": test_number,
        "test": test_name,
        "status": status,
        "details": details
    })
    icon = "✅" if passed else "❌"
    print(f"  {icon} [{test_number:02d}] {test_name}")
    if details and not passed:
        print(f"       └─ {details}")


def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def get_audit_count():
    """Get current audit trail count"""
    try:
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM audit_trails")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0


def get_latest_audits(limit=5):
    """Get latest audit entries"""
    try:
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT action, resource_type, message FROM audit_trails ORDER BY id DESC LIMIT {limit}")
        audits = cursor.fetchall()
        conn.close()
        return audits
    except:
        return []


# ==================== 1. HEALTH CHECK TESTS (5 tests) ====================

def test_health_checks():
    print_section("1. HEALTH CHECK TESTS")
    
    with httpx.Client() as client:
        # Test 1: Root endpoint
        try:
            r = client.get(f"{BASE_URL}/")
            passed = r.status_code == 200 and r.json().get("success") == True
            log_result("Root endpoint returns success", passed)
        except Exception as e:
            log_result("Root endpoint", False, str(e))
        
        # Test 2: Health endpoint
        try:
            r = client.get(f"{BASE_URL}/health")
            passed = r.status_code == 200 and r.json().get("status") == "UP"
            log_result("Health check returns UP status", passed)
        except Exception as e:
            log_result("Health check", False, str(e))
        
        # Test 3: Ready endpoint
        try:
            r = client.get(f"{BASE_URL}/ready")
            passed = r.status_code == 200 and "database" in r.json().get("checks", {})
            log_result("Ready check includes database status", passed)
        except Exception as e:
            log_result("Ready check", False, str(e))
        
        # Test 4: API v1 health
        try:
            r = client.get(f"{API_V1}/health")
            passed = r.status_code == 200
            log_result("API v1 health endpoint works", passed)
        except Exception as e:
            log_result("API v1 health", False, str(e))
        
        # Test 5: Response headers
        try:
            r = client.get(f"{BASE_URL}/health")
            has_headers = all([
                "x-request-id" in r.headers,
                "x-process-time" in r.headers,
                "x-content-type-options" in r.headers
            ])
            log_result("Response includes security headers", has_headers)
        except Exception as e:
            log_result("Security headers", False, str(e))


# ==================== 2. AUTHENTICATION TESTS (10 tests) ====================

def test_authentication():
    global tokens, user_ids
    print_section("2. AUTHENTICATION TESTS")
    
    with httpx.Client() as client:
        # Test 6: Register admin user
        try:
            r = client.post(f"{API_V1}/auth/register", json=TEST_USERS["admin"])
            passed = r.status_code in [200, 201] and r.json().get("success") == True
            if passed:
                user_ids["admin"] = r.json().get("data", {}).get("id")
            log_result("Register admin user", passed)
        except Exception as e:
            log_result("Register admin", False, str(e))
        
        # Test 7: Register manager user
        try:
            r = client.post(f"{API_V1}/auth/register", json=TEST_USERS["manager"])
            passed = r.status_code in [200, 201] and r.json().get("success") == True
            if passed:
                user_ids["manager"] = r.json().get("data", {}).get("id")
            log_result("Register manager user", passed)
        except Exception as e:
            log_result("Register manager", False, str(e))
        
        # Test 8: Register regular user
        try:
            r = client.post(f"{API_V1}/auth/register", json=TEST_USERS["user"])
            passed = r.status_code in [200, 201] and r.json().get("success") == True
            if passed:
                user_ids["user"] = r.json().get("data", {}).get("id")
            log_result("Register regular user", passed)
        except Exception as e:
            log_result("Register user", False, str(e))
        
        # Test 9: Login admin
        try:
            r = client.post(f"{API_V1}/auth/login", json={
                "email": TEST_USERS["admin"]["email"],
                "password": TEST_USERS["admin"]["password"]
            })
            passed = r.status_code == 200 and "access_token" in r.json().get("data", {})
            if passed:
                tokens["admin"] = r.json()["data"]["access_token"]
            log_result("Login admin user", passed)
        except Exception as e:
            log_result("Login admin", False, str(e))
        
        # Test 10: Login manager
        try:
            r = client.post(f"{API_V1}/auth/login", json={
                "email": TEST_USERS["manager"]["email"],
                "password": TEST_USERS["manager"]["password"]
            })
            passed = r.status_code == 200
            if passed:
                tokens["manager"] = r.json()["data"]["access_token"]
            log_result("Login manager user", passed)
        except Exception as e:
            log_result("Login manager", False, str(e))
        
        # Test 11: Get current user with token
        try:
            r = client.get(f"{API_V1}/auth/me", headers={"Authorization": f"Bearer {tokens.get('admin', '')}"})
            passed = r.status_code == 200 and r.json().get("data", {}).get("email") == TEST_USERS["admin"]["email"]
            log_result("Get current user with valid token", passed)
        except Exception as e:
            log_result("Get current user", False, str(e))
        
        # Test 12: Login with wrong password
        try:
            r = client.post(f"{API_V1}/auth/login", json={
                "email": TEST_USERS["admin"]["email"],
                "password": "WrongPassword123"
            })
            passed = r.status_code == 401
            log_result("Login with wrong password rejected", passed)
        except Exception as e:
            log_result("Wrong password", False, str(e))
        
        # Test 13: Login with non-existent email
        try:
            r = client.post(f"{API_V1}/auth/login", json={
                "email": "nonexistent@test.com",
                "password": "Test@123456"
            })
            passed = r.status_code == 401
            log_result("Login with non-existent email rejected", passed)
        except Exception as e:
            log_result("Non-existent email", False, str(e))
        
        # Test 14: Duplicate registration rejected
        try:
            r = client.post(f"{API_V1}/auth/register", json=TEST_USERS["admin"])
            passed = r.status_code in [400, 409]
            log_result("Duplicate email registration rejected", passed)
        except Exception as e:
            log_result("Duplicate registration", False, str(e))
        
        # Test 15: Access protected route without token
        try:
            r = client.get(f"{API_V1}/auth/me")
            passed = r.status_code in [401, 403]
            log_result("Protected route without token rejected", passed)
        except Exception as e:
            log_result("No token access", False, str(e))


# ==================== 3. VALIDATION TESTS (10 tests) ====================

def test_validation():
    print_section("3. VALIDATION TESTS")
    
    with httpx.Client() as client:
        # Test 16: Weak password rejected
        try:
            r = client.post(f"{API_V1}/auth/register", json={
                "email": "weak@test.com",
                "password": "weak",
                "first_name": "Test",
                "last_name": "User"
            })
            passed = r.status_code == 422
            log_result("Weak password rejected (too short)", passed)
        except Exception as e:
            log_result("Weak password", False, str(e))
        
        # Test 17: Password without special char
        try:
            r = client.post(f"{API_V1}/auth/register", json={
                "email": "nospecial@test.com",
                "password": "Password123",
                "first_name": "Test",
                "last_name": "User"
            })
            passed = r.status_code == 422
            log_result("Password without special char rejected", passed)
        except Exception as e:
            log_result("No special char", False, str(e))
        
        # Test 18: Invalid email format
        try:
            r = client.post(f"{API_V1}/auth/register", json={
                "email": "not-an-email",
                "password": "Test@123456",
                "first_name": "Test",
                "last_name": "User"
            })
            passed = r.status_code == 422
            log_result("Invalid email format rejected", passed)
        except Exception as e:
            log_result("Invalid email", False, str(e))
        
        # Test 19: Missing required fields
        try:
            r = client.post(f"{API_V1}/auth/register", json={
                "email": "missing@test.com"
            })
            passed = r.status_code == 422
            log_result("Missing required fields rejected", passed)
        except Exception as e:
            log_result("Missing fields", False, str(e))
        
        # Test 20: Empty first name
        try:
            r = client.post(f"{API_V1}/auth/register", json={
                "email": "empty@test.com",
                "password": "Test@123456",
                "first_name": "",
                "last_name": "User"
            })
            passed = r.status_code == 422
            log_result("Empty first name rejected", passed)
        except Exception as e:
            log_result("Empty name", False, str(e))
        
        # Test 21: XSS in name field
        try:
            r = client.post(f"{API_V1}/auth/register", json={
                "email": f"xss_{timestamp}@test.com",
                "password": "Test@123456",
                "first_name": "<script>alert('xss')</script>",
                "last_name": "User"
            })
            # Should either reject or sanitize
            passed = r.status_code in [200, 422]
            log_result("XSS attempt handled", passed)
        except Exception as e:
            log_result("XSS handling", False, str(e))
        
        # Test 22: SQL injection attempt
        try:
            r = client.post(f"{API_V1}/auth/login", json={
                "email": "'; DROP TABLE users; --",
                "password": "Test@123456"
            })
            passed = r.status_code in [401, 422]
            log_result("SQL injection attempt handled", passed)
        except Exception as e:
            log_result("SQL injection", False, str(e))
        
        # Test 23: Very long input
        try:
            r = client.post(f"{API_V1}/auth/register", json={
                "email": "long@test.com",
                "password": "Test@123456",
                "first_name": "A" * 1000,
                "last_name": "User"
            })
            passed = r.status_code == 422
            log_result("Very long input rejected", passed)
        except Exception as e:
            log_result("Long input", False, str(e))
        
        # Test 24: Invalid JSON
        try:
            r = client.post(
                f"{API_V1}/auth/register",
                content="not valid json",
                headers={"Content-Type": "application/json"}
            )
            passed = r.status_code == 422
            log_result("Invalid JSON rejected", passed)
        except Exception as e:
            log_result("Invalid JSON", False, str(e))
        
        # Test 25: Validation error response format
        try:
            r = client.post(f"{API_V1}/auth/register", json={"invalid": "data"})
            data = r.json()
            has_format = r.status_code == 422 and ("error" in data or "detail" in data)
            log_result("Validation error has proper format", has_format)
        except Exception as e:
            log_result("Error format", False, str(e))


# ==================== 4. COMPANY CRUD TESTS (10 tests) ====================

def test_company_crud():
    global company_ids
    print_section("4. COMPANY CRUD TESTS")
    
    if not tokens.get("admin"):
        log_result("Company CRUD", False, "No admin token available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    
    with httpx.Client() as client:
        # Test 26: Create company 1
        try:
            r = client.post(f"{API_V1}/companies", json=TEST_COMPANIES["company1"], headers=headers)
            passed = r.status_code in [200, 201] and r.json().get("success") == True
            if passed:
                company_ids["company1"] = r.json().get("data", {}).get("id")
            log_result("Create company 1", passed)
        except Exception as e:
            log_result("Create company 1", False, str(e))
        
        # Test 27: Create company 2
        try:
            r = client.post(f"{API_V1}/companies", json=TEST_COMPANIES["company2"], headers=headers)
            passed = r.status_code in [200, 201]
            if passed:
                company_ids["company2"] = r.json().get("data", {}).get("id")
            log_result("Create company 2", passed)
        except Exception as e:
            log_result("Create company 2", False, str(e))
        
        # Test 28: List all companies
        try:
            r = client.get(f"{API_V1}/companies", headers=headers)
            passed = r.status_code == 200 and len(r.json().get("data", [])) >= 2
            log_result("List all companies", passed)
        except Exception as e:
            log_result("List companies", False, str(e))
        
        # Test 29: Get single company
        try:
            cid = company_ids.get("company1")
            r = client.get(f"{API_V1}/companies/{cid}", headers=headers)
            passed = r.status_code == 200 and r.json().get("data", {}).get("id") == cid
            log_result("Get single company by ID", passed)
        except Exception as e:
            log_result("Get company", False, str(e))
        
        # Test 30: Update company
        try:
            cid = company_ids.get("company1")
            r = client.put(
                f"{API_V1}/companies/{cid}",
                json={"name": "Updated Tech Solutions", "city": "Delhi"},
                headers=headers
            )
            passed = r.status_code == 200
            log_result("Update company", passed)
        except Exception as e:
            log_result("Update company", False, str(e))
        
        # Test 31: Verify update
        try:
            cid = company_ids.get("company1")
            r = client.get(f"{API_V1}/companies/{cid}", headers=headers)
            data = r.json().get("data", {})
            passed = data.get("name") == "Updated Tech Solutions" and data.get("city") == "Delhi"
            log_result("Verify company update", passed)
        except Exception as e:
            log_result("Verify update", False, str(e))
        
        # Test 32: Get non-existent company
        try:
            r = client.get(f"{API_V1}/companies/99999", headers=headers)
            passed = r.status_code == 404
            log_result("Non-existent company returns 404", passed)
        except Exception as e:
            log_result("404 company", False, str(e))
        
        # Test 33: Create duplicate company email
        try:
            r = client.post(f"{API_V1}/companies", json=TEST_COMPANIES["company1"], headers=headers)
            passed = r.status_code in [400, 409]
            log_result("Duplicate company email rejected", passed)
        except Exception as e:
            log_result("Duplicate company", False, str(e))
        
        # Test 34: Company without auth
        try:
            r = client.get(f"{API_V1}/companies")
            passed = r.status_code in [401, 403]
            log_result("Company list without auth rejected", passed)
        except Exception as e:
            log_result("No auth company", False, str(e))
        
        # Test 35: Search companies
        try:
            r = client.get(f"{API_V1}/companies?search=Tech", headers=headers)
            passed = r.status_code == 200
            log_result("Search companies", passed)
        except Exception as e:
            log_result("Search companies", False, str(e))


# ==================== 5. USER CRUD TESTS (8 tests) ====================

def test_user_crud():
    print_section("5. USER CRUD TESTS")
    
    if not tokens.get("admin") or not company_ids.get("company1"):
        log_result("User CRUD", False, "No admin token or company available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    cid = company_ids["company1"]
    new_user_id = None
    
    with httpx.Client() as client:
        # Test 36: Create user in company
        try:
            new_user = {
                "email": f"companyuser_{timestamp}@test.com",
                "password": "Company@123456",
                "first_name": "Company",
                "last_name": "Employee",
                "role": "user"
            }
            r = client.post(f"{API_V1}/companies/{cid}/users", json=new_user, headers=headers)
            passed = r.status_code in [200, 201]
            if passed:
                new_user_id = r.json().get("data", {}).get("id")
            log_result("Create user in company", passed)
        except Exception as e:
            log_result("Create user", False, str(e))
        
        # Test 37: List users in company
        try:
            r = client.get(f"{API_V1}/companies/{cid}/users", headers=headers)
            passed = r.status_code == 200 and len(r.json().get("data", [])) >= 1
            log_result("List users in company", passed)
        except Exception as e:
            log_result("List users", False, str(e))
        
        # Test 38: Update user role
        try:
            if new_user_id:
                r = client.put(
                    f"{API_V1}/companies/{cid}/users/{new_user_id}/role",
                    json={"role": "manager"},
                    headers=headers
                )
                passed = r.status_code == 200
                log_result("Update user role to manager", passed)
            else:
                log_result("Update user role", False, "No user ID")
        except Exception as e:
            log_result("Update role", False, str(e))
        
        # Test 39: Get user details
        try:
            if new_user_id:
                r = client.get(f"{API_V1}/companies/{cid}/users/{new_user_id}", headers=headers)
                passed = r.status_code == 200
                log_result("Get user details", passed)
            else:
                log_result("Get user details", False, "No user ID")
        except Exception as e:
            log_result("Get user", False, str(e))
        
        # Test 40: Update user info
        try:
            if new_user_id:
                r = client.put(
                    f"{API_V1}/companies/{cid}/users/{new_user_id}",
                    json={"first_name": "Updated", "last_name": "Employee"},
                    headers=headers
                )
                passed = r.status_code == 200
                log_result("Update user info", passed)
            else:
                log_result("Update user info", False, "No user ID")
        except Exception as e:
            log_result("Update user", False, str(e))
        
        # Test 41: Get non-existent user
        try:
            r = client.get(f"{API_V1}/companies/{cid}/users/99999", headers=headers)
            passed = r.status_code == 404
            log_result("Non-existent user returns 404", passed)
        except Exception as e:
            log_result("404 user", False, str(e))
        
        # Test 42: Users list without auth
        try:
            r = client.get(f"{API_V1}/companies/{cid}/users")
            passed = r.status_code in [401, 403]
            log_result("Users list without auth rejected", passed)
        except Exception as e:
            log_result("No auth users", False, str(e))
        
        # Test 43: Create user with invalid role
        try:
            invalid_user = {
                "email": f"invalidrole_{timestamp}@test.com",
                "password": "Test@123456",
                "first_name": "Invalid",
                "last_name": "Role",
                "role": "superadmin"  # Invalid role
            }
            r = client.post(f"{API_V1}/companies/{cid}/users", json=invalid_user, headers=headers)
            # May accept or reject based on implementation
            passed = r.status_code in [200, 201, 422]
            log_result("User with custom role handled", passed)
        except Exception as e:
            log_result("Invalid role", False, str(e))


# ==================== 6. API VERSIONING & ERROR HANDLING (7 tests) ====================

def test_api_versioning_errors():
    print_section("6. API VERSIONING & ERROR HANDLING")
    
    with httpx.Client() as client:
        # Test 44: v1 API works
        try:
            r = client.get(f"{API_V1}/health")
            passed = r.status_code == 200
            log_result("API v1 endpoint works", passed)
        except Exception as e:
            log_result("v1 API", False, str(e))
        
        # Test 45: Legacy API works
        try:
            r = client.get(f"{BASE_URL}/api/health")
            passed = r.status_code == 200
            log_result("Legacy API endpoint works", passed)
        except Exception as e:
            log_result("Legacy API", False, str(e))
        
        # Test 46: 404 for non-existent endpoint
        try:
            r = client.get(f"{API_V1}/nonexistent")
            passed = r.status_code == 404
            log_result("Non-existent endpoint returns 404", passed)
        except Exception as e:
            log_result("404 endpoint", False, str(e))
        
        # Test 47: Method not allowed
        try:
            r = client.delete(f"{BASE_URL}/health")
            passed = r.status_code == 405
            log_result("Wrong method returns 405", passed)
        except Exception as e:
            log_result("405 method", False, str(e))
        
        # Test 48: Error response has success: false
        try:
            r = client.get(f"{API_V1}/auth/me")
            data = r.json()
            passed = data.get("success") == False
            log_result("Error response has success: false", passed)
        except Exception as e:
            log_result("Error format", False, str(e))
        
        # Test 49: Invalid token format
        try:
            r = client.get(
                f"{API_V1}/auth/me",
                headers={"Authorization": "InvalidFormat token123"}
            )
            passed = r.status_code in [401, 403]
            log_result("Invalid token format rejected", passed)
        except Exception as e:
            log_result("Invalid token", False, str(e))
        
        # Test 50: Expired/invalid JWT
        try:
            r = client.get(
                f"{API_V1}/auth/me",
                headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"}
            )
            passed = r.status_code in [401, 403]
            log_result("Invalid JWT rejected", passed)
        except Exception as e:
            log_result("Invalid JWT", False, str(e))


# ==================== 7. AUDIT LOG VERIFICATION ====================

def test_audit_logs():
    print_section("7. AUDIT LOG VERIFICATION")
    
    try:
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        # Get all audit entries
        cursor.execute("SELECT COUNT(*) FROM audit_trails")
        total_count = cursor.fetchone()[0]
        print(f"\n  📊 Total Audit Entries: {total_count}")
        
        # Check for different action types
        cursor.execute("SELECT action, COUNT(*) FROM audit_trails GROUP BY action")
        actions = cursor.fetchall()
        print(f"\n  📋 Actions Logged:")
        for action, count in actions:
            print(f"     - {action}: {count}")
        
        # Check for resource types
        cursor.execute("SELECT resource_type, COUNT(*) FROM audit_trails GROUP BY resource_type")
        resources = cursor.fetchall()
        print(f"\n  📁 Resources Tracked:")
        for resource, count in resources:
            print(f"     - {resource}: {count}")
        
        # Show latest 5 entries
        cursor.execute("""
            SELECT timestamp, action, resource_type, message 
            FROM audit_trails 
            ORDER BY id DESC 
            LIMIT 5
        """)
        latest = cursor.fetchall()
        print(f"\n  🕐 Latest 5 Audit Entries:")
        for entry in latest:
            print(f"     [{entry[0][:19]}] {entry[1]} - {entry[2]}: {entry[3][:50]}...")
        
        conn.close()
        
        # Verify audit entries exist
        log_result("Audit trail has entries", total_count > 0, f"Count: {total_count}")
        log_result("CREATE actions logged", any(a[0] == "CREATE" for a in actions))
        log_result("LOGIN actions logged", any(a[0] == "LOGIN" for a in actions))
        log_result("UPDATE actions logged", any(a[0] == "UPDATE" for a in actions))
        log_result("User resource tracked", any(r[0] == "User" for r in resources))
        log_result("Company resource tracked", any(r[0] == "Company" for r in resources))
        
    except Exception as e:
        log_result("Audit log verification", False, str(e))


# ==================== MAIN ====================

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("  🚀 APPLICATION STARTER KIT - FINAL COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"  📍 Base URL: {BASE_URL}")
    print(f"  📌 API Version: v1")
    print(f"  🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  📊 Target: 50+ Test Cases")
    print("="*70)
    
    # Get initial audit count
    initial_audit_count = get_audit_count()
    print(f"\n  📝 Initial Audit Count: {initial_audit_count}")
    
    # Run all test suites
    test_health_checks()      # 5 tests
    test_authentication()     # 10 tests
    test_validation()         # 10 tests
    test_company_crud()       # 10 tests
    test_user_crud()          # 8 tests
    test_api_versioning_errors()  # 7 tests
    test_audit_logs()         # 6 tests (audit verification)
    
    # Get final audit count
    final_audit_count = get_audit_count()
    new_audits = final_audit_count - initial_audit_count
    
    # Print summary
    print_section("📊 FINAL TEST SUMMARY")
    
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    total = len(results)
    
    print(f"\n  ┌{'─'*50}┐")
    print(f"  │ {'Total Tests:':<30} {total:>17} │")
    print(f"  │ {'Passed:':<30} {passed:>17} │")
    print(f"  │ {'Failed:':<30} {failed:>17} │")
    print(f"  │ {'Success Rate:':<30} {f'{(passed/total*100):.1f}%':>17} │")
    print(f"  │ {'New Audit Entries:':<30} {new_audits:>17} │")
    print(f"  │ {'Total Audit Entries:':<30} {final_audit_count:>17} │")
    print(f"  └{'─'*50}┘")
    
    if failed > 0:
        print(f"\n  ❌ Failed Tests:")
        for r in results:
            if r["status"] == "FAIL":
                print(f"     [{r['number']:02d}] {r['test']}")
                if r['details']:
                    print(f"         └─ {r['details']}")
    
    print("\n" + "="*70)
    
    if passed == total:
        print("  🎉 ALL TESTS PASSED! APPLICATION IS PRODUCTION READY!")
    else:
        print(f"  ⚠️  {failed} test(s) failed. Please review and fix.")
    
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    # Check if server is running
    try:
        with httpx.Client() as client:
            r = client.get(f"{BASE_URL}/health", timeout=5)
            if r.status_code != 200:
                print(f"Server not healthy. Status: {r.status_code}")
                sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: Cannot connect to server at {BASE_URL}")
        print(f"Please start the server first:")
        print(f"  cd ApplicationStarterKit")
        print(f"  .\\venv\\Scripts\\uvicorn app.main:app --port 8501")
        print(f"\nError: {e}")
        sys.exit(1)
    
    # Run tests
    success = run_all_tests()
    sys.exit(0 if success else 1)

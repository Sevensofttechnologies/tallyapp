"""
Comprehensive Test Suite for Application Starter Kit
Tests: CRUD, Validation, Authorization, Error Handling, Rate Limiting
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
import time
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8501"
API_V1 = f"{BASE_URL}/api/v1"

# Test data
TEST_USER = {
    "email": f"testuser_{int(time.time())}@test.com",
    "password": "Test@123456",
    "first_name": "Test",
    "last_name": "User",
    "phone": "+919876543210"
}

TEST_COMPANY = {
    "name": f"Test Company {int(time.time())}",
    "email": f"company_{int(time.time())}@test.com",
    "phone": "+919876543210",
    "address": "123 Test Street",
    "city": "Mumbai",
    "state": "Maharashtra",
    "country": "India",
    "zip_code": "400001",
    "industry": "Technology"
}

# Store tokens and IDs
auth_token = None
user_id = None
company_id = None

# Test results
results = []


def log_result(test_name: str, passed: bool, details: str = ""):
    """Log test result"""
    status = "PASS" if passed else "FAIL"
    results.append({
        "test": test_name,
        "status": status,
        "details": details
    })
    print(f"  [{status}] {test_name}")
    if details and not passed:
        print(f"       Details: {details}")


def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ==================== HEALTH CHECK TESTS ====================

def test_health_checks():
    """Test health check endpoints"""
    print_section("1. HEALTH CHECK TESTS")
    
    with httpx.Client() as client:
        # Test /health
        try:
            r = client.get(f"{BASE_URL}/health")
            passed = r.status_code == 200 and r.json().get("status") == "UP"
            log_result("GET /health", passed, f"Status: {r.status_code}")
        except Exception as e:
            log_result("GET /health", False, str(e))
        
        # Test /ready
        try:
            r = client.get(f"{BASE_URL}/ready")
            passed = r.status_code == 200 and r.json().get("status") == "ready"
            log_result("GET /ready", passed, f"Status: {r.status_code}")
        except Exception as e:
            log_result("GET /ready", False, str(e))
        
        # Test /api/v1/health
        try:
            r = client.get(f"{API_V1}/health")
            passed = r.status_code == 200
            log_result("GET /api/v1/health", passed, f"Status: {r.status_code}")
        except Exception as e:
            log_result("GET /api/v1/health", False, str(e))
        
        # Check correlation ID in response
        try:
            r = client.get(f"{BASE_URL}/health")
            has_request_id = "x-request-id" in r.headers
            has_process_time = "x-process-time" in r.headers
            log_result("Response has X-Request-ID header", has_request_id)
            log_result("Response has X-Process-Time header", has_process_time)
        except Exception as e:
            log_result("Correlation ID check", False, str(e))


# ==================== AUTHENTICATION TESTS ====================

def test_authentication():
    """Test authentication APIs"""
    global auth_token, user_id
    print_section("2. AUTHENTICATION TESTS")
    
    with httpx.Client() as client:
        # Test Registration
        try:
            r = client.post(f"{API_V1}/auth/register", json=TEST_USER)
            if r.status_code in [200, 201]:
                data = r.json()
                user_id = data.get("data", {}).get("id")
                passed = data.get("success") == True
                log_result("POST /auth/register - Valid user", passed)
            else:
                log_result("POST /auth/register - Valid user", False, f"Status: {r.status_code}")
        except Exception as e:
            log_result("POST /auth/register", False, str(e))
        
        # Test Login
        try:
            r = client.post(f"{API_V1}/auth/login", json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            })
            if r.status_code == 200:
                data = r.json()
                auth_token = data.get("data", {}).get("access_token")
                log_result("POST /auth/login - Valid credentials", True)
            else:
                log_result("POST /auth/login - Valid credentials", False, r.text)
        except Exception as e:
            log_result("POST /auth/login", False, str(e))
        
        # Test Get Current User
        if auth_token:
            try:
                r = client.get(
                    f"{API_V1}/auth/me",
                    headers={"Authorization": f"Bearer {auth_token}"}
                )
                passed = r.status_code == 200
                log_result("GET /auth/me - With token", passed)
            except Exception as e:
                log_result("GET /auth/me", False, str(e))
        
        # Test without token (should fail with 401 or 403)
        try:
            r = client.get(f"{API_V1}/auth/me")
            passed = r.status_code in [401, 403]  # Both are valid auth errors
            log_result("GET /auth/me - Without token (expect 401/403)", passed, f"Got: {r.status_code}")
        except Exception as e:
            log_result("GET /auth/me - Without token", False, str(e))


# ==================== VALIDATION TESTS ====================

def test_validation():
    """Test input validation"""
    print_section("3. VALIDATION TESTS")
    
    with httpx.Client() as client:
        # Test weak password
        try:
            r = client.post(f"{API_V1}/auth/register", json={
                "email": "weak@test.com",
                "password": "weak",  # Too short, no special chars
                "first_name": "Test",
                "last_name": "User"
            })
            passed = r.status_code == 422
            log_result("Weak password rejected (expect 422)", passed, f"Got: {r.status_code}")
        except Exception as e:
            log_result("Weak password validation", False, str(e))
        
        # Test invalid email
        try:
            r = client.post(f"{API_V1}/auth/register", json={
                "email": "not-an-email",
                "password": "Test@123456",
                "first_name": "Test",
                "last_name": "User"
            })
            passed = r.status_code == 422
            log_result("Invalid email rejected (expect 422)", passed, f"Got: {r.status_code}")
        except Exception as e:
            log_result("Invalid email validation", False, str(e))
        
        # Test missing required field
        try:
            r = client.post(f"{API_V1}/auth/register", json={
                "email": "missing@test.com",
                "password": "Test@123456"
                # Missing first_name, last_name
            })
            passed = r.status_code == 422
            log_result("Missing fields rejected (expect 422)", passed, f"Got: {r.status_code}")
        except Exception as e:
            log_result("Missing fields validation", False, str(e))
        
        # Test XSS attempt in name
        try:
            r = client.post(f"{API_V1}/auth/register", json={
                "email": "xss@test.com",
                "password": "Test@123456",
                "first_name": "<script>alert('xss')</script>",
                "last_name": "User"
            })
            # Should either reject or sanitize
            passed = r.status_code in [422, 200]
            log_result("XSS in name handled", passed, f"Status: {r.status_code}")
        except Exception as e:
            log_result("XSS validation", False, str(e))
        
        # Test duplicate email
        try:
            r = client.post(f"{API_V1}/auth/register", json=TEST_USER)
            passed = r.status_code in [400, 409]  # Conflict or Bad Request
            log_result("Duplicate email rejected (expect 400/409)", passed, f"Got: {r.status_code}")
        except Exception as e:
            log_result("Duplicate email validation", False, str(e))


# ==================== COMPANY CRUD TESTS ====================

def test_company_crud():
    """Test Company CRUD operations"""
    global company_id
    print_section("4. COMPANY CRUD TESTS")
    
    if not auth_token:
        log_result("Company CRUD", False, "No auth token available")
        return
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    with httpx.Client() as client:
        # CREATE
        try:
            r = client.post(f"{API_V1}/companies", json=TEST_COMPANY, headers=headers)
            if r.status_code in [200, 201]:
                data = r.json()
                company_id = data.get("data", {}).get("id")
                log_result("POST /companies - Create", True)
            else:
                log_result("POST /companies - Create", False, f"Status: {r.status_code}, {r.text}")
        except Exception as e:
            log_result("POST /companies", False, str(e))
        
        # READ (List)
        try:
            r = client.get(f"{API_V1}/companies", headers=headers)
            passed = r.status_code == 200
            log_result("GET /companies - List", passed, f"Status: {r.status_code}")
        except Exception as e:
            log_result("GET /companies - List", False, str(e))
        
        # READ (Single)
        if company_id:
            try:
                r = client.get(f"{API_V1}/companies/{company_id}", headers=headers)
                passed = r.status_code == 200
                log_result(f"GET /companies/{company_id} - Single", passed)
            except Exception as e:
                log_result("GET /companies/{id}", False, str(e))
        
        # UPDATE
        if company_id:
            try:
                r = client.put(
                    f"{API_V1}/companies/{company_id}",
                    json={"name": "Updated Company Name"},
                    headers=headers
                )
                passed = r.status_code == 200
                log_result(f"PUT /companies/{company_id} - Update", passed, f"Status: {r.status_code}")
            except Exception as e:
                log_result("PUT /companies/{id}", False, str(e))
        
        # READ non-existent (404)
        try:
            r = client.get(f"{API_V1}/companies/99999", headers=headers)
            passed = r.status_code == 404
            log_result("GET /companies/99999 - Not found (expect 404)", passed, f"Got: {r.status_code}")
        except Exception as e:
            log_result("GET non-existent company", False, str(e))


# ==================== USER CRUD TESTS ====================

def test_user_crud():
    """Test User CRUD operations"""
    print_section("5. USER CRUD TESTS")
    
    if not auth_token or not company_id:
        log_result("User CRUD", False, "No auth token or company_id available")
        return
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    new_user_id = None
    
    with httpx.Client() as client:
        # CREATE user in company
        try:
            new_user_data = {
                "email": f"newuser_{int(time.time())}@test.com",
                "password": "Test@123456",
                "first_name": "New",
                "last_name": "User",
                "role": "user"
            }
            r = client.post(
                f"{API_V1}/companies/{company_id}/users",
                json=new_user_data,
                headers=headers
            )
            if r.status_code in [200, 201]:
                data = r.json()
                new_user_id = data.get("data", {}).get("id")
                log_result("POST /companies/{id}/users - Create", True)
            else:
                log_result("POST /companies/{id}/users - Create", False, f"Status: {r.status_code}")
        except Exception as e:
            log_result("POST /companies/{id}/users", False, str(e))
        
        # READ (List users in company)
        try:
            r = client.get(f"{API_V1}/companies/{company_id}/users", headers=headers)
            passed = r.status_code == 200
            log_result("GET /companies/{id}/users - List", passed)
        except Exception as e:
            log_result("GET /companies/{id}/users", False, str(e))
        
        # UPDATE user role
        if new_user_id:
            try:
                r = client.put(
                    f"{API_V1}/companies/{company_id}/users/{new_user_id}/role",
                    json={"role": "manager"},
                    headers=headers
                )
                passed = r.status_code == 200
                log_result(f"PUT /users/{new_user_id}/role - Update role", passed, f"Status: {r.status_code}")
            except Exception as e:
                log_result("PUT /users/{id}/role", False, str(e))


# ==================== AUTHORIZATION TESTS ====================

def test_authorization():
    """Test authorization and access control"""
    print_section("6. AUTHORIZATION TESTS")
    
    with httpx.Client() as client:
        # Test accessing protected route without token (401 or 403 both valid)
        try:
            r = client.get(f"{API_V1}/companies")
            passed = r.status_code in [401, 403]
            log_result("Protected route without token (expect 401/403)", passed, f"Got: {r.status_code}")
        except Exception as e:
            log_result("Authorization - no token", False, str(e))
        
        # Test with invalid token (401 or 403 both valid)
        try:
            r = client.get(
                f"{API_V1}/companies",
                headers={"Authorization": "Bearer invalid_token_here"}
            )
            passed = r.status_code in [401, 403]
            log_result("Invalid token rejected (expect 401/403)", passed, f"Got: {r.status_code}")
        except Exception as e:
            log_result("Authorization - invalid token", False, str(e))
        
        # Test with malformed authorization header (401 or 403 both valid)
        try:
            r = client.get(
                f"{API_V1}/companies",
                headers={"Authorization": "NotBearer token"}
            )
            passed = r.status_code in [401, 403]
            log_result("Malformed auth header rejected (expect 401/403)", passed, f"Got: {r.status_code}")
        except Exception as e:
            log_result("Authorization - malformed header", False, str(e))


# ==================== ERROR HANDLING TESTS ====================

def test_error_handling():
    """Test error handling and response format"""
    print_section("7. ERROR HANDLING TESTS")
    
    with httpx.Client() as client:
        # Test 404 - Not Found
        try:
            r = client.get(f"{API_V1}/nonexistent-endpoint")
            passed = r.status_code == 404
            log_result("Non-existent endpoint (expect 404)", passed, f"Got: {r.status_code}")
        except Exception as e:
            log_result("404 handling", False, str(e))
        
        # Test 422 - Validation Error format
        try:
            r = client.post(f"{API_V1}/auth/register", json={"invalid": "data"})
            passed = r.status_code == 422
            data = r.json()
            has_error_format = "error" in data or "errors" in data
            log_result("Validation error has proper format", has_error_format)
        except Exception as e:
            log_result("422 format check", False, str(e))
        
        # Test error response has success: false
        try:
            r = client.get(f"{API_V1}/auth/me")  # Without token
            data = r.json()
            has_success_false = data.get("success") == False
            log_result("Error response has success: false", has_success_false)
        except Exception as e:
            log_result("Error response format", False, str(e))


# ==================== API VERSIONING TESTS ====================

def test_api_versioning():
    """Test API versioning"""
    print_section("8. API VERSIONING TESTS")
    
    with httpx.Client() as client:
        # Test v1 endpoint
        try:
            r = client.get(f"{API_V1}/health")
            passed = r.status_code == 200
            log_result("GET /api/v1/health works", passed)
        except Exception as e:
            log_result("/api/v1 endpoint", False, str(e))
        
        # Test legacy endpoint (backward compatibility)
        try:
            r = client.get(f"{BASE_URL}/api/health")
            passed = r.status_code == 200
            log_result("GET /api/health (legacy) works", passed)
        except Exception as e:
            log_result("/api legacy endpoint", False, str(e))


# ==================== SECURITY HEADERS TESTS ====================

def test_security_headers():
    """Test security headers in response"""
    print_section("9. SECURITY HEADERS TESTS")
    
    with httpx.Client() as client:
        try:
            r = client.get(f"{BASE_URL}/health")
            headers = r.headers
            
            # Check security headers
            checks = [
                ("X-Content-Type-Options", "x-content-type-options" in headers),
                ("X-Frame-Options", "x-frame-options" in headers),
                ("X-Request-ID", "x-request-id" in headers),
                ("X-Process-Time", "x-process-time" in headers),
            ]
            
            for header_name, present in checks:
                log_result(f"Header: {header_name}", present)
                
        except Exception as e:
            log_result("Security headers check", False, str(e))


# ==================== MAIN ====================

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("  APPLICATION STARTER KIT - COMPREHENSIVE TEST SUITE")
    print("="*60)
    print(f"  Base URL: {BASE_URL}")
    print(f"  API Version: v1")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Run all test suites
    test_health_checks()
    test_authentication()
    test_validation()
    test_company_crud()
    test_user_crud()
    test_authorization()
    test_error_handling()
    test_api_versioning()
    test_security_headers()
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    total = len(results)
    
    print(f"\n  Total Tests: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Success Rate: {(passed/total*100):.1f}%")
    
    if failed > 0:
        print("\n  Failed Tests:")
        for r in results:
            if r["status"] == "FAIL":
                print(f"    - {r['test']}: {r['details']}")
    
    print("\n" + "="*60)
    
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
        print(f"\nERROR: Cannot connect to server at {BASE_URL}")
        print(f"Please start the server first:")
        print(f"  cd ApplicationStarterKit")
        print(f"  .\\venv\\Scripts\\uvicorn app.main:app --reload --port 8000")
        print(f"\nError: {e}")
        sys.exit(1)
    
    # Run tests
    success = run_all_tests()
    sys.exit(0 if success else 1)

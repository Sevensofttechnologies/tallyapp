"""
Test JWT Authentication Flow
Tests the JWT middleware with TallyBridge tokens

Usage:
    python scripts/test_jwt_auth.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from jose import jwt

# Import auth module
from app.middleware.auth import verify_token, SECRET_KEY, ALGORITHM

def create_test_token(user_id: int, email: str, role: str, company_id: int = None, expires_delta: timedelta = None):
    """Create a test JWT token (simulating TallyBridge)"""
    if expires_delta is None:
        expires_delta = timedelta(hours=24)
    
    expire = datetime.utcnow() + expires_delta
    
    payload = {
        "sub": str(user_id),  # JWT requires sub to be string
        "user_id": user_id,
        "email": email,
        "role": role,
        "company_id": company_id,
        "exp": expire
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def test_valid_token():
    """Test with valid token"""
    print("\n" + "=" * 50)
    print("TEST 1: Valid Token")
    print("=" * 50)
    
    token = create_test_token(
        user_id=1,
        email="admin@example.com",
        role="admin",
        company_id=1
    )
    
    print(f"Token: {token[:50]}...")
    
    payload = verify_token(token)
    
    if payload:
        print("[PASS] Token verified successfully!")
        print(f"  - user_id: {payload.get('user_id')}")
        print(f"  - email: {payload.get('email')}")
        print(f"  - role: {payload.get('role')}")
        print(f"  - company_id: {payload.get('company_id')}")
        return True
    else:
        print("[FAIL] Token verification failed!")
        return False


def test_expired_token():
    """Test with expired token"""
    print("\n" + "=" * 50)
    print("TEST 2: Expired Token")
    print("=" * 50)
    
    token = create_test_token(
        user_id=1,
        email="admin@example.com",
        role="admin",
        expires_delta=timedelta(seconds=-10)  # Already expired
    )
    
    print(f"Token: {token[:50]}...")
    
    payload = verify_token(token)
    
    if payload is None:
        print("[PASS] Expired token correctly rejected!")
        return True
    else:
        print("[FAIL] Expired token should have been rejected!")
        return False


def test_invalid_token():
    """Test with invalid token"""
    print("\n" + "=" * 50)
    print("TEST 3: Invalid Token")
    print("=" * 50)
    
    invalid_token = "invalid.token.here"
    
    print(f"Token: {invalid_token}")
    
    payload = verify_token(invalid_token)
    
    if payload is None:
        print("[PASS] Invalid token correctly rejected!")
        return True
    else:
        print("[FAIL] Invalid token should have been rejected!")
        return False


def test_wrong_secret():
    """Test with token signed with wrong secret"""
    print("\n" + "=" * 50)
    print("TEST 4: Wrong Secret Key")
    print("=" * 50)
    
    wrong_secret = "wrong-secret-key"
    expire = datetime.utcnow() + timedelta(hours=1)
    
    payload = {
        "sub": 1,
        "email": "test@example.com",
        "role": "user",
        "exp": expire
    }
    
    token = jwt.encode(payload, wrong_secret, algorithm=ALGORITHM)
    
    print(f"Token: {token[:50]}...")
    
    result = verify_token(token)
    
    if result is None:
        print("[PASS] Token with wrong secret correctly rejected!")
        return True
    else:
        print("[FAIL] Token with wrong secret should have been rejected!")
        return False


def main():
    print("\n" + "=" * 60)
    print("TallyInsight - JWT Authentication Test")
    print("=" * 60)
    print(f"\nSECRET_KEY: {SECRET_KEY[:20]}...")
    print(f"ALGORITHM: {ALGORITHM}")
    
    results = []
    
    results.append(("Valid Token", test_valid_token()))
    results.append(("Expired Token", test_expired_token()))
    results.append(("Invalid Token", test_invalid_token()))
    results.append(("Wrong Secret", test_wrong_secret()))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll tests passed! JWT authentication is working correctly.")
    else:
        print("\nSome tests failed. Please check the implementation.")


if __name__ == "__main__":
    main()

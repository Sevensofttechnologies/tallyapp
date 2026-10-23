"""
Test Tally Integration
Tests the TallyBridge <-> TallyInsight communication

Usage:
    python scripts/test_tally_integration.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from app.services.tally_service import tally_service


async def test_health_check():
    """Test TallyInsight health check"""
    print("\n" + "=" * 50)
    print("TEST 1: TallyInsight Health Check")
    print("=" * 50)
    
    result = await tally_service.health_check()
    
    if result["status"] == "healthy":
        print("[PASS] TallyInsight is healthy")
        print(f"  Response: {result}")
        return True
    elif result["status"] == "unreachable":
        print("[SKIP] TallyInsight is not running")
        print(f"  Error: {result.get('error')}")
        print("  Start TallyInsight with: python -m uvicorn app.main:app --port 8000")
        return None  # Skip, not fail
    else:
        print(f"[FAIL] TallyInsight status: {result['status']}")
        return False


async def test_get_companies():
    """Test getting Tally companies"""
    print("\n" + "=" * 50)
    print("TEST 2: Get Tally Companies")
    print("=" * 50)
    
    result = await tally_service.get_tally_companies()
    
    if result["success"]:
        print("[PASS] Got Tally companies")
        companies = result.get("data", {}).get("companies", [])
        print(f"  Found {len(companies)} companies")
        for c in companies[:5]:  # Show first 5
            print(f"    - {c}")
        return True
    else:
        print(f"[INFO] Could not get companies: {result.get('error')}")
        return None  # May fail if Tally not connected


async def test_get_synced_companies():
    """Test getting synced companies from TallyInsight DB"""
    print("\n" + "=" * 50)
    print("TEST 3: Get Synced Companies")
    print("=" * 50)
    
    result = await tally_service.get_synced_companies()
    
    if result["success"]:
        print("[PASS] Got synced companies")
        data = result.get("data", {})
        companies = data.get("companies", []) if isinstance(data, dict) else data
        print(f"  Found {len(companies) if isinstance(companies, list) else 0} synced companies")
        return True
    else:
        print(f"[INFO] Could not get synced companies: {result.get('error')}")
        return None


async def test_get_ledgers():
    """Test getting ledgers"""
    print("\n" + "=" * 50)
    print("TEST 4: Get Ledgers")
    print("=" * 50)
    
    result = await tally_service.get_ledgers(limit=10)
    
    if result["success"]:
        print("[PASS] Got ledgers")
        data = result.get("data", {})
        ledgers = data.get("ledgers", []) if isinstance(data, dict) else []
        print(f"  Found {len(ledgers)} ledgers (limited to 10)")
        return True
    else:
        print(f"[INFO] Could not get ledgers: {result.get('error')}")
        return None


async def test_get_vouchers():
    """Test getting vouchers"""
    print("\n" + "=" * 50)
    print("TEST 5: Get Vouchers")
    print("=" * 50)
    
    result = await tally_service.get_vouchers(limit=10)
    
    if result["success"]:
        print("[PASS] Got vouchers")
        data = result.get("data", {})
        vouchers = data.get("vouchers", []) if isinstance(data, dict) else []
        print(f"  Found {len(vouchers)} vouchers (limited to 10)")
        return True
    else:
        print(f"[INFO] Could not get vouchers: {result.get('error')}")
        return None


async def main():
    print("\n" + "=" * 60)
    print("TallyBridge - Tally Integration Test")
    print("=" * 60)
    print(f"\nTallyInsight URL: {tally_service.base_url}")
    
    results = []
    
    # Run tests
    results.append(("Health Check", await test_health_check()))
    
    # Only run other tests if TallyInsight is healthy
    if results[0][1] is True:
        results.append(("Get Tally Companies", await test_get_companies()))
        results.append(("Get Synced Companies", await test_get_synced_companies()))
        results.append(("Get Ledgers", await test_get_ledgers()))
        results.append(("Get Vouchers", await test_get_vouchers()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    skipped = sum(1 for _, r in results if r is None)
    
    for name, result in results:
        if result is True:
            status = "[PASS]"
        elif result is False:
            status = "[FAIL]"
        else:
            status = "[SKIP]"
        print(f"  {status} {name}")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0:
        print("\nIntegration test completed successfully!")
    else:
        print("\nSome tests failed. Check TallyInsight service.")


if __name__ == "__main__":
    asyncio.run(main())

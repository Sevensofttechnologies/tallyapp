"""
tests/test_jwt_auth.py
======================
PART 1 tests for JWT authentication on TallyInsight.

Tests:
  1.  No token → 401
  2.  Expired token → 401
  3.  Wrong secret key → 401
  4.  Wrong algorithm → 401
  5.  Valid token → 200
  6.  GET /api/health open (no token needed) → 200
  7.  CORS preflight OPTIONS not blocked → 200
  8.  Non-admin gets 403 on admin-only route
  9.  Token without user_id / sub → 401
  10. Token with non-numeric user_id → 401
  11. Admin-only routes return 403 for normal user
  12. POST /api/data/query returns 404 when ENABLE_RAW_QUERY=false
  13. POST /api/data/query returns 403 for non-admin when ENABLE_RAW_QUERY=true

Run from the repo root:
    cd TallyInsightPlus-master
    python -m pytest tests/test_jwt_auth.py -v

The tests use FastAPI's TestClient and mock the database / tally service so
no real Tally or SQLite connection is required.
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from jose import jwt

# ---------------------------------------------------------------------------
# Ensure TallyInsight package is importable
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent
TALLY_INSIGHT_ROOT = REPO_ROOT / "TallyInsight"
sys.path.insert(0, str(TALLY_INSIGHT_ROOT))

# ---------------------------------------------------------------------------
# Constants — must match what the app uses
# ---------------------------------------------------------------------------
STRONG_SECRET = "test-secret-key-that-is-long-enough-for-validation-purposes-32chars"
ALGORITHM = "HS256"
WRONG_SECRET = "wrong-secret-key-that-is-long-enough-for-validation-purposes-32chars"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_token(
    user_id=1,
    email="user@example.com",
    role="user",
    company_id=None,
    exp_offset: int = 3600,
    secret: str = STRONG_SECRET,
    algorithm: str = ALGORITHM,
    include_user_id: bool = True,
    user_id_value=None,
) -> str:
    """Build a signed JWT for testing."""
    payload: dict = {
        "email": email,
        "role": role,
        "exp": int(time.time()) + exp_offset,
    }
    if include_user_id:
        payload["user_id"] = user_id_value if user_id_value is not None else user_id
    if company_id is not None:
        payload["company_id"] = company_id
    return jwt.encode(payload, secret, algorithm=algorithm)


def _admin_token() -> str:
    return _make_token(user_id=1, role="admin")


def _user_token() -> str:
    return _make_token(user_id=2, role="user")


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# App fixture — patch env vars before importing the app
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def app_client():
    """
    Create a TestClient for TallyInsight with:
    - A strong SECRET_KEY injected via env
    - database_service and tally_service mocked out
    - ENABLE_RAW_QUERY=false (default)
    """
    env_patch = {
        "SECRET_KEY": STRONG_SECRET,
        "JWT_SECRET_KEY": STRONG_SECRET,
        "ALGORITHM": ALGORITHM,
        "CORS_ORIGINS": "http://localhost:3000",
        "ENABLE_RAW_QUERY": "false",
        "HOST": "127.0.0.1",
    }

    with patch.dict(os.environ, env_patch, clear=False):
        # Remove any cached module state so config re-reads env
        for mod_name in list(sys.modules.keys()):
            if "TallyInsight" in mod_name or mod_name.startswith("app."):
                del sys.modules[mod_name]

        # Mock heavy services before importing the app
        db_mock = MagicMock()
        db_mock.connect = AsyncMock()
        db_mock.disconnect = AsyncMock()
        db_mock.ensure_company_config_table = AsyncMock()
        db_mock.fetch_all = AsyncMock(return_value=[])
        db_mock.fetch_one = AsyncMock(return_value=None)
        db_mock.execute = AsyncMock()
        db_mock.get_all_table_counts = AsyncMock(return_value={})
        db_mock.get_synced_companies = AsyncMock(return_value=[])
        db_mock.add_company_column_to_tables = AsyncMock(return_value={})

        tally_mock = MagicMock()
        tally_mock.get_open_companies = AsyncMock(return_value=[])
        tally_mock.get_company_info = AsyncMock(return_value={"name": ""})
        tally_mock.test_connection = AsyncMock(return_value={"connected": True})

        sched_mock = MagicMock()
        sched_mock.get_status = MagicMock(return_value={})
        sched_mock.update_schedule = MagicMock(return_value={})
        sched_mock.run_now = MagicMock(return_value={})

        sync_svc_mock = MagicMock()
        sync_svc_mock.get_incomplete_sync = MagicMock(return_value=None)
        sync_svc_mock.dismiss_incomplete_sync = MagicMock(return_value={})

        sync_queue_mock = MagicMock()
        sync_queue_mock.get_status = MagicMock(return_value={})
        sync_queue_mock.add_companies = MagicMock(return_value={})
        sync_queue_mock.start_processing = AsyncMock(return_value={})
        sync_queue_mock.cancel_queue = MagicMock(return_value={})
        sync_queue_mock.clear_queue = MagicMock(return_value={})

        with (
            patch("app.services.database_service.database_service", db_mock),
            patch("app.services.tally_service.tally_service", tally_mock),
            patch("app.services.scheduler_service.scheduler_service", sched_mock),
            patch("app.services.sync_service.sync_service", sync_svc_mock),
            patch("app.services.sync_queue_service.sync_queue_service", sync_queue_mock),
        ):
            from app.main import app
            with TestClient(app, raise_server_exceptions=False) as client:
                yield client


@pytest.fixture(scope="module")
def app_client_raw_query_enabled():
    """Same as app_client but with ENABLE_RAW_QUERY=true."""
    env_patch = {
        "SECRET_KEY": STRONG_SECRET,
        "JWT_SECRET_KEY": STRONG_SECRET,
        "ALGORITHM": ALGORITHM,
        "CORS_ORIGINS": "http://localhost:3000",
        "ENABLE_RAW_QUERY": "true",
        "HOST": "127.0.0.1",
    }

    with patch.dict(os.environ, env_patch, clear=False):
        for mod_name in list(sys.modules.keys()):
            if "TallyInsight" in mod_name or mod_name.startswith("app."):
                del sys.modules[mod_name]

        db_mock = MagicMock()
        db_mock.connect = AsyncMock()
        db_mock.disconnect = AsyncMock()
        db_mock.ensure_company_config_table = AsyncMock()
        db_mock.fetch_all = AsyncMock(return_value=[{"id": 1}])
        db_mock.fetch_one = AsyncMock(return_value=None)
        db_mock.execute = AsyncMock()
        db_mock.get_all_table_counts = AsyncMock(return_value={})
        db_mock.get_synced_companies = AsyncMock(return_value=[])

        tally_mock = MagicMock()
        tally_mock.get_open_companies = AsyncMock(return_value=[])
        tally_mock.get_company_info = AsyncMock(return_value={"name": ""})

        sched_mock = MagicMock()
        sched_mock.get_status = MagicMock(return_value={})

        sync_svc_mock = MagicMock()
        sync_svc_mock.get_incomplete_sync = MagicMock(return_value=None)

        sync_queue_mock = MagicMock()
        sync_queue_mock.get_status = MagicMock(return_value={})

        with (
            patch("app.services.database_service.database_service", db_mock),
            patch("app.services.tally_service.tally_service", tally_mock),
            patch("app.services.scheduler_service.scheduler_service", sched_mock),
            patch("app.services.sync_service.sync_service", sync_svc_mock),
            patch("app.services.sync_queue_service.sync_queue_service", sync_queue_mock),
        ):
            from app.main import app as app2
            with TestClient(app2, raise_server_exceptions=False) as client:
                yield client


# ---------------------------------------------------------------------------
# Test 1 — No token → 401
# ---------------------------------------------------------------------------

def test_no_token_returns_401(app_client):
    """Any protected route without a token must return 401."""
    resp = app_client.get("/api/sync/status")
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


# ---------------------------------------------------------------------------
# Test 2 — Expired token → 401
# ---------------------------------------------------------------------------

def test_expired_token_returns_401(app_client):
    """A token whose exp is in the past must be rejected with 401."""
    expired = _make_token(exp_offset=-3600)  # expired 1 hour ago
    resp = app_client.get("/api/sync/status", headers=_auth_header(expired))
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


# ---------------------------------------------------------------------------
# Test 3 — Wrong secret key → 401
# ---------------------------------------------------------------------------

def test_wrong_secret_returns_401(app_client):
    """A token signed with a different secret must be rejected with 401."""
    bad_token = _make_token(secret=WRONG_SECRET)
    resp = app_client.get("/api/sync/status", headers=_auth_header(bad_token))
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


# ---------------------------------------------------------------------------
# Test 4 — Wrong algorithm → 401
# ---------------------------------------------------------------------------

def test_wrong_algorithm_returns_401(app_client):
    """A token signed with RS256 (or any non-HS256 alg) must be rejected."""
    # We can't easily sign RS256 without a key pair, so we craft a token
    # with a different HS algorithm to simulate algorithm mismatch.
    bad_alg_token = _make_token(algorithm="HS512")
    resp = app_client.get("/api/sync/status", headers=_auth_header(bad_alg_token))
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


# ---------------------------------------------------------------------------
# Test 5 — Valid token → 200 (or non-401/403)
# ---------------------------------------------------------------------------

def test_valid_token_accepted(app_client):
    """A valid token must be accepted (not 401/403) on a protected route."""
    token = _admin_token()
    resp = app_client.get("/api/data/counts", headers=_auth_header(token))
    # We don't care about 500 from mocked DB, just that auth passed
    assert resp.status_code not in (401, 403), (
        f"Expected auth to pass, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 6 — GET /api/health open (no token needed)
# ---------------------------------------------------------------------------

def test_health_endpoint_open(app_client):
    """GET /api/health must be accessible without any token."""
    resp = app_client.get("/api/health")
    assert resp.status_code not in (401, 403), (
        f"Health endpoint should be open, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 7 — CORS preflight OPTIONS not blocked
# ---------------------------------------------------------------------------

def test_cors_preflight_not_blocked(app_client):
    """OPTIONS preflight to a protected route must not return 401/403."""
    resp = app_client.options(
        "/api/sync/status",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
    )
    # FastAPI/Starlette returns 200 for OPTIONS preflight via CORSMiddleware
    assert resp.status_code not in (401, 403), (
        f"CORS preflight should not be blocked, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 8 — Non-admin gets 403 on admin-only route
# ---------------------------------------------------------------------------

def test_non_admin_gets_403_on_admin_route(app_client):
    """A user with role='user' must get 403 on /api/logs/*."""
    token = _user_token()
    resp = app_client.get("/api/logs", headers=_auth_header(token))
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"


# ---------------------------------------------------------------------------
# Test 9 — Token without user_id / sub → 401
# ---------------------------------------------------------------------------

def test_token_without_user_id_returns_401(app_client):
    """A token that has no user_id and no sub claim must return 401."""
    no_uid_token = _make_token(include_user_id=False)
    resp = app_client.get("/api/sync/status", headers=_auth_header(no_uid_token))
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


# ---------------------------------------------------------------------------
# Test 10 — Token with non-numeric user_id → 401
# ---------------------------------------------------------------------------

def test_token_with_non_numeric_user_id_returns_401(app_client):
    """A token whose user_id is a string like 'abc' must return 401."""
    bad_uid_token = _make_token(user_id_value="not-a-number")
    resp = app_client.get("/api/sync/status", headers=_auth_header(bad_uid_token))
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


# ---------------------------------------------------------------------------
# Test 11 — Admin-only routes return 403 for normal user
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("method,path", [
    ("GET",  "/api/logs"),
    ("GET",  "/api/debug/status"),
    ("POST", "/api/audit/restore/1"),
])
def test_admin_routes_return_403_for_user(app_client, method, path):
    """Admin-only routes must return 403 for a user with role='user'."""
    token = _user_token()
    resp = app_client.request(method, path, headers=_auth_header(token))
    assert resp.status_code == 403, (
        f"{method} {path}: Expected 403, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 12 — POST /api/data/query returns 404 when ENABLE_RAW_QUERY=false
# ---------------------------------------------------------------------------

def test_raw_query_returns_404_when_disabled(app_client):
    """POST /api/data/query must return 404 when ENABLE_RAW_QUERY=false."""
    token = _admin_token()
    resp = app_client.post(
        "/api/data/query",
        json={"query": "SELECT 1"},
        headers=_auth_header(token),
    )
    assert resp.status_code == 404, (
        f"Expected 404 (feature disabled), got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 13 — POST /api/data/query returns 403 for non-admin when enabled
# ---------------------------------------------------------------------------

def test_raw_query_returns_403_for_non_admin_when_enabled(app_client_raw_query_enabled):
    """POST /api/data/query must return 403 for role='user' even when enabled."""
    token = _user_token()
    resp = app_client_raw_query_enabled.post(
        "/api/data/query",
        json={"query": "SELECT 1"},
        headers=_auth_header(token),
    )
    assert resp.status_code == 403, (
        f"Expected 403 for non-admin, got {resp.status_code}: {resp.text}"
    )

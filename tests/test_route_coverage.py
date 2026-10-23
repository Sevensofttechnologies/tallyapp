"""
tests/test_route_coverage.py
============================
Route-coverage test: every route registered on the TallyInsight app must
return 401 when called without a token, EXCEPT for an explicit allow-list of
intentionally-open paths.

This test will FAIL if someone later adds an unprotected API route, because
the new route will return something other than 401 and the assertion will
catch it.

Run from the repo root:
    cd TallyInsightPlus-master
    python -m pytest tests/test_route_coverage.py -v

Design notes
------------
* We enumerate routes via ``app.routes`` after the app is fully built.
* Path parameters (e.g. ``{table_name}``) are filled with dummy values so
  FastAPI can match the route and run its dependency chain.
* Static-file mounts and WebSocket routes are skipped (they don't carry JWT
  deps and are not API routes).
* The allow-list is intentionally narrow: only ``GET /api/health`` (the bare
  docker-healthcheck endpoint) plus the standard FastAPI docs/openapi paths
  and the static HTML pages served directly from main.py.
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from jose import jwt

# ---------------------------------------------------------------------------
# Ensure TallyInsight package is importable
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent
TALLY_INSIGHT_ROOT = REPO_ROOT / "TallyInsight"
sys.path.insert(0, str(TALLY_INSIGHT_ROOT))

STRONG_SECRET = "test-secret-key-that-is-long-enough-for-validation-purposes-32chars"
ALGORITHM = "HS256"

# ---------------------------------------------------------------------------
# Paths that are intentionally open (no JWT required).
# Everything NOT in this list must return 401 when called without a token.
# ---------------------------------------------------------------------------
OPEN_PATHS = {
    # Docker healthcheck — the only open API endpoint
    "/api/health",
    # FastAPI auto-generated docs (disabled in production but present in tests)
    "/docs",
    "/redoc",
    "/openapi.json",
    # Static HTML pages — auth is enforced client-side by JS
    "/",
    "/index.html",
    "/sync.html",
    "/dashboard.html",
    "/audit.html",
    "/old",
    "/voucher-report",
    "/voucher-report/",
    "/voucher-report/index.html",
    "/outstanding-report",
    "/outstanding-report/",
}

# Dummy values to substitute for path parameters so routes can be matched
PARAM_DEFAULTS = {
    "table_name": "ledger",
    "deleted_id": "1",
    "id": "1",
    "company_id": "1",
    "ledger_name": "test",
    "filename": "test.db",
}


def _fill_path(path_template: str) -> str:
    """Replace ``{param}`` placeholders with dummy values."""
    result = path_template
    for param, value in PARAM_DEFAULTS.items():
        result = result.replace(f"{{{param}}}", value)
    return result


# ---------------------------------------------------------------------------
# App fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def coverage_client():
    """TestClient with all heavy services mocked out."""
    env_patch = {
        "SECRET_KEY": STRONG_SECRET,
        "JWT_SECRET_KEY": STRONG_SECRET,
        "ALGORITHM": ALGORITHM,
        "CORS_ORIGINS": "http://localhost:3000",
        "ENABLE_RAW_QUERY": "false",
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
                yield client, app


# ---------------------------------------------------------------------------
# Helper: collect all (method, path) pairs from the app
# ---------------------------------------------------------------------------

def _collect_routes(app: FastAPI):
    """
    Walk app.routes and return a list of (method, path_template) tuples.
    Skips Mount routes (static files) and non-APIRoute entries.
    """
    routes = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        for method in route.methods or ["GET"]:
            routes.append((method.upper(), route.path))
    return routes


# ---------------------------------------------------------------------------
# The coverage test
# ---------------------------------------------------------------------------

def test_every_api_route_requires_jwt(coverage_client):
    """
    Call every registered route without a token.
    Routes NOT in OPEN_PATHS must return 401.
    Routes in OPEN_PATHS must NOT return 401 (they are intentionally open).

    This test fails if:
    - A new API route is added without JWT protection (returns non-401 without token)
    - An open route is accidentally protected (returns 401)
    """
    client, app = coverage_client
    routes = _collect_routes(app)

    assert routes, "No routes found — app may not have loaded correctly"

    failures = []

    for method, path_template in routes:
        filled_path = _fill_path(path_template)
        is_open = path_template in OPEN_PATHS or filled_path in OPEN_PATHS

        # Use an empty body for POST/PUT/PATCH to avoid 422 Unprocessable Entity
        kwargs = {}
        if method in ("POST", "PUT", "PATCH"):
            kwargs["json"] = {}

        resp = client.request(method, filled_path, **kwargs)

        if is_open:
            # Open routes must NOT be blocked by auth
            if resp.status_code == 401:
                failures.append(
                    f"OPEN route {method} {path_template} unexpectedly returned 401"
                )
        else:
            # Protected routes must return 401 without a token
            if resp.status_code != 401:
                failures.append(
                    f"UNPROTECTED route {method} {path_template} "
                    f"(filled: {filled_path}) returned {resp.status_code} "
                    f"instead of 401 — add JWT dependency!"
                )

    if failures:
        pytest.fail(
            f"{len(failures)} route(s) failed the coverage check:\n"
            + "\n".join(f"  • {f}" for f in failures)
        )

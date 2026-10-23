"""
tests/test_secret_validation.py
================================
Tests for:
1. TallyBridge config.py — _validate_secret_key() fail-fast logic
2. TallyInsight config.py — _validate_secret_key() fail-fast logic
3. scripts/check_env.py — detects matching / mismatching keys

Run from the repo root:
    cd TallyInsightPlus-master
    python -m pytest tests/test_secret_validation.py -v
"""

import hashlib
import importlib
import importlib.util
import os
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent  # TallyInsightPlus-master/

BRIDGE_CONFIG = REPO_ROOT / "TallyBridge" / "app" / "config.py"
INSIGHT_CONFIG = REPO_ROOT / "TallyInsight" / "app" / "config.py"


def _load_config_module(path: Path) -> ModuleType:
    """
    Load a config.py file as an isolated module (no side-effects from Settings()).
    We exec only the source up to (but not including) the `settings = Settings()` line
    so we can import _validate_secret_key without triggering the global instantiation.
    """
    source = path.read_text(encoding="utf-8")
    # Strip the last line `settings = Settings()` and `config = load_config()`
    # so the module-level singleton is never created during tests.
    lines = source.splitlines()
    safe_lines = [
        ln for ln in lines
        if not ln.strip().startswith("settings = Settings()")
        and not ln.strip().startswith("config = load_config()")
    ]
    safe_source = "\n".join(safe_lines)

    spec = importlib.util.spec_from_loader(f"_test_config_{path.parent.parent.name}", loader=None)
    mod = ModuleType(spec.name)
    mod.__file__ = str(path)
    exec(compile(safe_source, str(path), "exec"), mod.__dict__)  # noqa: S102
    return mod


def _bridge_validate(value: str) -> str:
    """Call TallyBridge's _validate_secret_key without triggering Settings()."""
    mod = _load_config_module(BRIDGE_CONFIG)
    return mod._validate_secret_key(value)  # type: ignore[attr-defined]


def _insight_validate(value: str) -> str:
    """Call TallyInsight's _validate_secret_key without triggering load_config().

    AuthConfig's class body calls _validate_secret_key(os.getenv(...)) at
    class-definition time, so we must supply a valid env var before exec-ing
    the module, then call the function directly with our test value.
    """
    _SENTINEL = "x" * 48  # strong enough to pass class-body validation
    with patch.dict(os.environ, {"JWT_SECRET_KEY": _SENTINEL}, clear=False):
        mod = _load_config_module(INSIGHT_CONFIG)
    return mod._validate_secret_key(value)  # type: ignore[attr-defined]


def _run_check_env(bridge_content: str, insight_content: str) -> int:
    """
    Write two temp .env files and run check_env.main().
    Returns the exit code (captured via SystemExit).
    """
    check_env_path = REPO_ROOT / "scripts" / "check_env.py"
    spec_source = check_env_path.read_text(encoding="utf-8")

    # Execute the module in an isolated namespace
    ns: dict = {}
    exec(compile(spec_source, str(check_env_path), "exec"), ns)  # noqa: S102

    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as bf:
        bf.write(bridge_content)
        bridge_file = bf.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as inf:
        inf.write(insight_content)
        insight_file = inf.name

    try:
        with patch("sys.argv", ["check_env.py", "--bridge", bridge_file, "--insight", insight_file]):
            try:
                ns["main"]()
                return 0
            except SystemExit as exc:
                return int(exc.code) if exc.code is not None else 0
    finally:
        os.unlink(bridge_file)
        os.unlink(insight_file)


# ---------------------------------------------------------------------------
# TallyBridge _validate_secret_key tests
# ---------------------------------------------------------------------------

class TestTallyBridgeValidation:
    def test_valid_key_passes(self):
        key = "a" * 48
        assert _bridge_validate(key) == key

    def test_placeholder_key_exits(self):
        with pytest.raises(SystemExit):
            _bridge_validate("your-secret-key-change-in-production")

    def test_another_placeholder_exits(self):
        with pytest.raises(SystemExit):
            _bridge_validate("tallybots-super-secret-key-change-in-production-2026")

    def test_short_key_exits(self):
        with pytest.raises(SystemExit):
            _bridge_validate("short")

    def test_exactly_32_chars_passes(self):
        key = "x" * 32
        assert _bridge_validate(key) == key

    def test_31_chars_exits(self):
        with pytest.raises(SystemExit):
            _bridge_validate("y" * 31)

    def test_empty_string_exits(self):
        with pytest.raises(SystemExit):
            _bridge_validate("")


# ---------------------------------------------------------------------------
# TallyInsight _validate_secret_key tests
# ---------------------------------------------------------------------------

class TestTallyInsightValidation:
    def test_valid_key_passes(self):
        key = "b" * 48
        assert _insight_validate(key) == key

    def test_placeholder_key_exits(self):
        with pytest.raises(SystemExit):
            _insight_validate("tallybots-super-secret-key-change-in-production-2026")

    def test_short_key_exits(self):
        with pytest.raises(SystemExit):
            _insight_validate("tooshort")

    def test_empty_string_exits(self):
        with pytest.raises(SystemExit):
            _insight_validate("")


# ---------------------------------------------------------------------------
# check_env.py tests
# ---------------------------------------------------------------------------

STRONG_KEY_A = "A" * 48
STRONG_KEY_B = "B" * 48


class TestCheckEnv:
    def test_matching_keys_exit_0(self):
        bridge = f"SECRET_KEY={STRONG_KEY_A}\n"
        insight = f"JWT_SECRET_KEY={STRONG_KEY_A}\n"
        assert _run_check_env(bridge, insight) == 0

    def test_mismatching_keys_exit_1(self):
        bridge = f"SECRET_KEY={STRONG_KEY_A}\n"
        insight = f"JWT_SECRET_KEY={STRONG_KEY_B}\n"
        assert _run_check_env(bridge, insight) == 1

    def test_insight_uses_secret_key_alias(self):
        """TallyInsight also accepts SECRET_KEY as alias."""
        bridge = f"SECRET_KEY={STRONG_KEY_A}\n"
        insight = f"SECRET_KEY={STRONG_KEY_A}\n"
        assert _run_check_env(bridge, insight) == 0

    def test_bridge_placeholder_exits_1(self):
        bridge = "SECRET_KEY=your-secret-key-change-in-production\n"
        insight = f"JWT_SECRET_KEY={STRONG_KEY_A}\n"
        assert _run_check_env(bridge, insight) == 1

    def test_insight_placeholder_exits_1(self):
        bridge = f"SECRET_KEY={STRONG_KEY_A}\n"
        insight = "JWT_SECRET_KEY=tallybots-super-secret-key-change-in-production-2026\n"
        assert _run_check_env(bridge, insight) == 1

    def test_bridge_missing_key_exits_1(self):
        bridge = "APP_NAME=TallyBridge\n"
        insight = f"JWT_SECRET_KEY={STRONG_KEY_A}\n"
        assert _run_check_env(bridge, insight) == 1

    def test_insight_missing_key_exits_1(self):
        bridge = f"SECRET_KEY={STRONG_KEY_A}\n"
        insight = "APP_NAME=TallyInsight\n"
        assert _run_check_env(bridge, insight) == 1

    def test_short_key_exits_1(self):
        bridge = "SECRET_KEY=tooshort\n"
        insight = f"JWT_SECRET_KEY={STRONG_KEY_A}\n"
        assert _run_check_env(bridge, insight) == 1
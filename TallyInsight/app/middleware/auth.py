"""
JWT Authentication Middleware for TallyInsight
Validates JWT tokens from TallyBridge

This middleware:
1. Extracts JWT token from Authorization header
2. Validates token using shared SECRET_KEY
3. Extracts user_id and company_id from token
4. Makes user info available to route handlers
"""

import logging
from typing import Optional
from datetime import datetime, timezone

from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel

# Use the validated config — avoids a second os.getenv with a different placeholder.
# config.auth.secret_key has already been validated (fail-fast) at import time.
from ..config import config as _app_config

SECRET_KEY: str = _app_config.auth.secret_key
ALGORITHM: str = _app_config.auth.algorithm

logger = logging.getLogger(__name__)


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None
    company_id: Optional[int] = None
    exp: Optional[datetime] = None


class CurrentUser(BaseModel):
    """Current authenticated user"""
    id: int
    email: str
    role: str
    company_id: Optional[int] = None


def _extract_user_id(payload: dict) -> int:
    """
    Extract and validate user_id from JWT payload.

    Reads ``sub`` first (standard JWT claim), then falls back to ``user_id``
    (TallyBridge legacy claim).  Raises HTTPException 401 if:
      - neither claim is present
      - the value cannot be converted to a positive integer
    """
    raw = payload.get("sub") or payload.get("user_id")
    if raw is None:
        raise HTTPException(
            status_code=401,
            detail="Token missing user identity (sub / user_id claim)"
        )
    try:
        uid = int(raw)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Token user_id is not a valid integer"
        )
    if uid <= 0:
        raise HTTPException(
            status_code=401,
            detail="Token user_id must be a positive integer"
        )
    return uid


class JWTBearer(HTTPBearer):
    """
    JWT Bearer token authentication.
    Use as dependency: Depends(jwt_bearer)
    """

    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)

        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authentication scheme. Use Bearer token."
                )

            token = credentials.credentials
            payload = verify_token(token)

            if not payload:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )

            # _extract_user_id raises 401 on missing / non-numeric user_id
            user_id = _extract_user_id(payload)

            # Store user info in request state for later use
            request.state.user = CurrentUser(
                id=user_id,
                email=payload.get("email", ""),
                role=payload.get("role", "user"),
                company_id=payload.get("company_id")
            )

            return token

        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )


def verify_token(token: str) -> Optional[dict]:
    """
    Verify JWT token and return payload.

    Returns the decoded payload dict if the token is valid and not expired,
    or None if verification fails for any reason.  Never raises — callers
    should treat None as an invalid token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # python-jose checks ``exp`` automatically, but we do an explicit
        # UTC-aware check as a belt-and-suspenders guard.
        exp = payload.get("exp")
        if exp is not None:
            exp_dt = datetime.fromtimestamp(exp, tz=timezone.utc)
            if datetime.now(tz=timezone.utc) > exp_dt:
                return None

        return payload

    except JWTError as exc:
        logger.debug("JWT verification failed: %s", exc)
        return None
    except Exception as exc:
        logger.warning("Unexpected token verification error: %s", exc)
        return None


async def get_current_user(request: Request) -> CurrentUser:
    """
    Get current authenticated user from request state.
    Use after JWTBearer dependency.

    Usage::

        @router.get("/endpoint")
        async def endpoint(
            _token: str = Depends(jwt_bearer),
            current_user: CurrentUser = Depends(get_current_user)
        ):
            ...
    """
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=401,
            detail="User not authenticated"
        )
    return request.state.user


def get_optional_user(request: Request) -> Optional[CurrentUser]:
    """
    Get current user if authenticated, None otherwise.
    Use for endpoints that work with or without auth.
    """
    if hasattr(request.state, "user"):
        return request.state.user
    return None


# ---------------------------------------------------------------------------
# Singleton dependency — import and use as Depends(jwt_bearer)
# ---------------------------------------------------------------------------
jwt_bearer = JWTBearer()


def require_auth():
    """
    Dependency that requires authentication.

    Usage::

        @router.get("/protected", dependencies=[Depends(require_auth())])
        async def protected_endpoint():
            pass
    """
    return Depends(jwt_bearer)


def require_role(allowed_roles: list):
    """
    Dependency that requires specific role(s).

    Usage::

        @router.get("/admin-only", dependencies=[Depends(require_role(["admin", "super_admin"]))])
        async def admin_endpoint():
            pass
    """
    async def role_checker(request: Request, token: str = Depends(jwt_bearer)):
        user = request.state.user
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return user

    return Depends(role_checker)


def get_company_filter(current_user: CurrentUser, company_param: Optional[str] = None) -> Optional[str]:
    """
    Get company name filter based on user's company_id or explicit parameter.

    For multi-tenant data isolation:
    - If company_param provided, use it (for admin users)
    - Otherwise, filter by user's company_id

    Usage in controller::

        company_filter = get_company_filter(current_user, company_param)
        if company_filter:
            query += " WHERE company_name = ?"
            params.append(company_filter)
    """
    if company_param:
        return company_param

    # In future, map company_id to company_name via TallyBridge API
    # For now, return None (no filter) - will be implemented in Phase 3
    return None

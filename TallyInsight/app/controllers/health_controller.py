"""
Health Controller
Handles health check API endpoints
"""

from fastapi import APIRouter, Depends

from ..middleware.auth import jwt_bearer
from ..services.health_service import health_service
from ..utils.logger import logger

router = APIRouter()

# JWT dependency list — used on sub-routes that expose internal detail
_jwt_dep = [Depends(jwt_bearer)]


@router.get("")
async def health_check():
    """Complete health check — intentionally open (docker healthcheck)"""
    return await health_service.check_all()


@router.get("/tally", dependencies=_jwt_dep)
async def tally_health():
    """Tally connection health check — requires JWT"""
    return await health_service.check_tally()


@router.get("/database", dependencies=_jwt_dep)
async def database_health():
    """Database health check — requires JWT"""
    return await health_service.check_database()

"""
Config Controller
Handles configuration API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends

from ..config import config, save_config, load_config, AppConfig
from ..middleware.auth import require_role
from ..services.tally_service import tally_service
from ..utils.logger import logger

router = APIRouter()

_admin_dep = [require_role(["admin", "super_admin"])]


@router.get("")
async def get_config():
    """Get current configuration"""
    return config.model_dump()


@router.put("", dependencies=_admin_dep)
async def update_config(new_config: dict):
    """Update configuration"""
    try:
        # Update config values
        if "tally" in new_config:
            for key, value in new_config["tally"].items():
                if hasattr(config.tally, key):
                    setattr(config.tally, key, value)
        
        if "database" in new_config:
            for key, value in new_config["database"].items():
                if hasattr(config.database, key):
                    setattr(config.database, key, value)
        
        if "sync" in new_config:
            for key, value in new_config["sync"].items():
                if hasattr(config.sync, key):
                    setattr(config.sync, key, value)
        
        # Save to file
        save_config(config)
        
        logger.info("Configuration updated")
        return {"status": "success", "message": "Configuration updated"}
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tally/test", dependencies=_admin_dep)
async def test_tally_connection():
    """Test Tally connection"""
    try:
        result = await tally_service.test_connection()
        return result
    except Exception as e:
        logger.error(f"Tally connection test failed: {e}")
        return {
            "connected": False,
            "error": str(e)
        }


@router.get("/tally/company")
async def get_company_info():
    """Get current company info from Tally"""
    try:
        result = await tally_service.get_company_info()
        return result
    except Exception as e:
        logger.error(f"Failed to get company info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

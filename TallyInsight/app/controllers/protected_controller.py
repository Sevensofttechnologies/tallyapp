"""
Protected Controller - Example of JWT Protected Routes
Demonstrates how to use JWT authentication middleware

Usage:
1. Get JWT token from TallyBridge login
2. Include in header: Authorization: Bearer <token>
3. Access protected endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Optional

from ..middleware.auth import (
    JWTBearer, 
    get_current_user, 
    CurrentUser,
    require_role
)
from ..services.database_service import database_service
from ..utils.logger import logger

router = APIRouter()


@router.get("/me")
async def get_current_user_info(
    token: str = Depends(JWTBearer()),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get current authenticated user info
    Requires: Valid JWT token
    """
    return {
        "success": True,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
            "company_id": current_user.company_id
        }
    }


@router.get("/my-companies")
async def get_user_companies(
    token: str = Depends(JWTBearer()),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get synced companies for current user
    Requires: Valid JWT token
    
    Returns companies from TallyInsight that match user's company_id
    """
    try:
        await database_service.connect()
        
        # Get all synced companies
        query = "SELECT * FROM company_config ORDER BY company_name"
        companies = await database_service.fetch_all(query)
        
        return {
            "success": True,
            "user_id": current_user.id,
            "companies": [dict(c) for c in companies] if companies else []
        }
    except Exception as e:
        logger.error(f"Error fetching companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await database_service.disconnect()


@router.get("/company/{company_name}/summary")
async def get_company_summary(
    company_name: str,
    token: str = Depends(JWTBearer()),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get summary for a specific company
    Requires: Valid JWT token
    """
    try:
        await database_service.connect()
        
        # Get company config
        company_query = "SELECT * FROM company_config WHERE company_name = ?"
        company = await database_service.fetch_one(company_query, [company_name])
        
        if not company:
            raise HTTPException(status_code=404, detail=f"Company '{company_name}' not found")
        
        # Get counts
        ledger_count = await database_service.fetch_one(
            "SELECT COUNT(*) as count FROM mst_ledger WHERE company_name = ?",
            [company_name]
        )
        
        voucher_count = await database_service.fetch_one(
            "SELECT COUNT(*) as count FROM trn_voucher WHERE company_name = ?",
            [company_name]
        )
        
        stock_count = await database_service.fetch_one(
            "SELECT COUNT(*) as count FROM mst_stock_item WHERE company_name = ?",
            [company_name]
        )
        
        return {
            "success": True,
            "company": dict(company),
            "summary": {
                "ledgers": ledger_count["count"] if ledger_count else 0,
                "vouchers": voucher_count["count"] if voucher_count else 0,
                "stock_items": stock_count["count"] if stock_count else 0
            },
            "accessed_by": {
                "user_id": current_user.id,
                "email": current_user.email
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching company summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await database_service.disconnect()


@router.get("/admin/stats")
async def get_admin_stats(
    request: Request,
    token: str = Depends(JWTBearer()),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get admin statistics (admin/super_admin only)
    Requires: Valid JWT token with admin role
    """
    # Check role
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    try:
        await database_service.connect()
        
        # Get overall stats
        stats = {}
        
        tables = ["company_config", "mst_ledger", "mst_stock_item", "trn_voucher", "audit_log"]
        for table in tables:
            count = await database_service.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
            stats[table] = count["count"] if count else 0
        
        return {
            "success": True,
            "stats": stats,
            "accessed_by": current_user.email
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching admin stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await database_service.disconnect()

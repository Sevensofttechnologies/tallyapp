"""
Reports Routes - Proxy to TallyInsight
Handles report API endpoints for vouchers, outstanding, and ledger reports
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..utils.dependencies import get_current_active_user as get_current_user, get_raw_token
from ..services.tally_service import tally_service

router = APIRouter(prefix="/reports", tags=["Reports"])


# ==================== VOUCHER REPORTS ====================

@router.get("/vouchers")
async def get_vouchers(
    voucher_type: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    company: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get vouchers with filters - proxies to TallyInsight"""
    result = await tally_service.get_vouchers(
        voucher_type=voucher_type,
        from_date=from_date,
        to_date=to_date,
        company=company,
        limit=limit,
        offset=offset,
        token=token,
    )
    return result


@router.get("/vouchers/{guid}")
async def get_voucher_details(
    guid: str,
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get voucher details by GUID - proxies to TallyInsight"""
    result = await tally_service.get_voucher_details(guid, token=token)
    return result


# ==================== OUTSTANDING REPORTS ====================

@router.get("/outstanding")
async def get_outstanding(
    type: str = Query(default="receivable", description="receivable or payable"),
    company: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get outstanding summary - proxies to TallyInsight"""
    result = await tally_service.get_outstanding(party_type=type, company=company, token=token)
    return result


@router.get("/outstanding/billwise")
async def get_outstanding_billwise(
    type: str = Query(default="receivable"),
    company: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=10, le=100),
    include_totals: bool = Query(default=True),
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get bill-wise outstanding - proxies to TallyInsight"""
    result = await tally_service.get_outstanding_billwise(
        type=type,
        company=company,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size,
        include_totals=include_totals,
        token=token,
    )
    return result


@router.get("/outstanding/ledgerwise")
async def get_outstanding_ledgerwise(
    type: str = Query(default="receivable"),
    company: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    include_totals: bool = Query(default=True),
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get ledger-wise outstanding - proxies to TallyInsight"""
    result = await tally_service.get_outstanding_ledgerwise(
        type=type,
        company=company,
        from_date=from_date,
        to_date=to_date,
        include_totals=include_totals,
        token=token,
    )
    return result


@router.get("/outstanding/ageing")
async def get_outstanding_ageing(
    type: str = Query(default="receivable"),
    company: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get ageing analysis - proxies to TallyInsight"""
    result = await tally_service.get_outstanding_ageing(type=type, company=company, token=token)
    return result


@router.get("/outstanding/group")
async def get_outstanding_group(
    type: str = Query(default="receivable"),
    company: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get group outstanding - proxies to TallyInsight"""
    result = await tally_service.get_outstanding_group(type=type, company=company, token=token)
    return result


# ==================== LEDGER REPORTS ====================

@router.get("/ledger/list")
async def get_ledger_list(
    company: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get list of all ledgers - proxies to TallyInsight"""
    result = await tally_service.get_ledger_list(company=company, token=token)
    return result


@router.get("/ledger/{ledger_name}")
async def get_ledger_transactions(
    ledger_name: str,
    company: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get ledger transactions - proxies to TallyInsight"""
    result = await tally_service.get_ledger_transactions(
        ledger_name=ledger_name,
        company=company,
        from_date=from_date,
        to_date=to_date,
        token=token,
    )
    return result


@router.get("/ledger/{ledger_name}/billwise")
async def get_ledger_billwise(
    ledger_name: str,
    company: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get ledger bill-wise pending bills - proxies to TallyInsight"""
    result = await tally_service.get_ledger_billwise(
        ledger_name=ledger_name,
        company=company,
        from_date=from_date,
        to_date=to_date,
        token=token,
    )
    return result

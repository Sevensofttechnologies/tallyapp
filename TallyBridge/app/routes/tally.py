"""
Tally Routes - API endpoints for Tally integration
Proxy endpoints that communicate with TallyInsight microservice

Endpoints:
- /api/v1/tally/health - Check TallyInsight service health
- /api/v1/tally/companies - Get Tally companies
- /api/v1/tally/sync - Trigger sync
- /api/v1/tally/ledgers - Get ledgers
- /api/v1/tally/vouchers - Get vouchers
- /api/v1/tally/stock-items - Get stock items
- /api/v1/tally/reports/* - Get reports
- /api/v1/tally/webhook/sync-complete - Webhook for sync completion
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from ..database import get_db
from ..models.user import User
from ..models.company import Company
from ..models.user_company import UserCompany
from ..services.tally_service import tally_service
from ..services.audit_service import create_audit_trail
from ..utils.dependencies import get_current_active_user as get_current_user, get_raw_token
from ..schemas.company import CompanyTallySync

router = APIRouter(prefix="/tally", tags=["Tally Integration"])


# ==================== HEALTH & STATUS ====================

@router.get("/health")
async def tally_health_check():
    """Check TallyInsight service health (open — no auth required)"""
    result = await tally_service.health_check()
    return result


@router.get("/status")
async def get_sync_status(
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get current sync status from TallyInsight"""
    result = await tally_service.get_sync_status(token=token)
    return result


# ==================== COMPANY OPERATIONS ====================

@router.get("/companies")
async def get_tally_companies(
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get list of companies available in Tally"""
    result = await tally_service.get_tally_companies(token=token)
    return result


@router.get("/synced-companies")
async def get_synced_companies(
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get list of already synced companies"""
    result = await tally_service.get_synced_companies(token=token)
    return result


@router.get("/company/details")
async def get_company_details(
    company: str = Query("", description="Company name (empty = active company)"),
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get complete company details from Tally including contact, address, statutory info"""
    result = await tally_service.get_company_details(company, token=token)
    return result


@router.get("/ledger/master")
async def get_ledger_master(
    company: str = Query("", description="Company name (empty = active company)"),
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get all ledger master data from Tally with 30 fields

    Returns all ledgers with:
    - Basic: guid, name, parent, alias, description, notes
    - Balance: opening, closing
    - Contact: mailing_name, address, state, country, pincode, email, mobile
    - Statutory: pan, gstin, gst_registration_type, gst_supply_type, gst_duty_head, tax_rate
    - Bank: account_holder, account_number, ifsc, swift, bank_name, branch
    - Settings: is_revenue, is_deemed_positive, credit_period
    """
    result = await tally_service.get_ledger_master(company, token=token)
    return result


@router.post("/sync")
async def trigger_sync(
    company_name: str = Query(..., description="Company name to sync"),
    sync_mode: str = Query("full", description="Sync mode: full or incremental"),
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
    db: Session = Depends(get_db)
):
    """Trigger sync for a specific company"""
    # Log sync request
    create_audit_trail(
        db=db,
        user_id=current_user.id,
        action="tally_sync_requested",
        resource_type="company",
        resource_id=None,
        details={"company_name": company_name, "sync_mode": sync_mode}
    )

    result = await tally_service.sync_company(company_name, sync_mode, token=token)
    return result


# ==================== WEBHOOK ====================

@router.post("/webhook/sync-complete")
async def sync_complete_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint called by TallyInsight when sync completes.
    Auto-creates company in TallyBridge if not exists.
    No auth required — called by TallyInsight internally.
    """
    try:
        payload = await request.json()

        company_name = payload.get("company_name")
        tally_guid = payload.get("tally_guid")
        tally_server = payload.get("tally_server", "localhost")
        tally_port = payload.get("tally_port", 9000)
        sync_status = payload.get("status", "completed")
        records_synced = payload.get("records_synced", 0)
        user_id = payload.get("user_id")  # User who triggered sync

        if not company_name:
            raise HTTPException(status_code=400, detail="company_name is required")

        # Check if company exists
        existing_company = db.query(Company).filter(
            Company.tally_guid == tally_guid
        ).first() if tally_guid else None

        if not existing_company:
            existing_company = db.query(Company).filter(
                Company.name == company_name
            ).first()

        if existing_company:
            # Update existing company with Tally info
            existing_company.tally_guid = tally_guid
            existing_company.tally_server = tally_server
            existing_company.tally_port = tally_port
            existing_company.last_sync_at = datetime.utcnow()
            existing_company.last_alter_id = payload.get("last_alter_id", 0)
            db.commit()

            # Log update
            create_audit_trail(
                db=db,
                user_id=user_id,
                action="company_tally_updated",
                resource_type="company",
                resource_id=existing_company.id,
                details={
                    "company_name": company_name,
                    "tally_guid": tally_guid,
                    "records_synced": records_synced
                }
            )

            return {
                "success": True,
                "message": "Company updated with Tally info",
                "company_id": existing_company.id,
                "action": "updated"
            }
        else:
            # Create new company
            # Generate default email from company name (required field)
            safe_name = company_name.lower().replace(" ", "_").replace(".", "")[:50]
            default_email = f"{safe_name}@tally.local"

            new_company = Company(
                name=company_name,
                email=default_email,  # Required field
                tally_guid=tally_guid,
                tally_server=tally_server,
                tally_port=tally_port,
                last_sync_at=datetime.utcnow(),
                last_alter_id=payload.get("last_alter_id", 0),
                status="active"
            )
            db.add(new_company)
            db.commit()
            db.refresh(new_company)

            # Link company to user if user_id provided
            if user_id:
                user_company = UserCompany(
                    user_id=user_id,
                    company_id=new_company.id,
                    role="admin",  # Creator gets admin role
                    is_default=True
                )
                db.add(user_company)
                db.commit()

            # Log creation
            create_audit_trail(
                db=db,
                user_id=user_id,
                action="company_created_from_tally",
                resource_type="company",
                resource_id=new_company.id,
                details={
                    "company_name": company_name,
                    "tally_guid": tally_guid,
                    "records_synced": records_synced
                }
            )

            return {
                "success": True,
                "message": "Company created from Tally sync",
                "company_id": new_company.id,
                "action": "created"
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DATA ENDPOINTS ====================

@router.get("/ledgers")
async def get_ledgers(
    company: Optional[str] = None,
    group: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get ledgers from TallyInsight"""
    result = await tally_service.get_ledgers(
        company=company,
        group=group,
        limit=limit,
        offset=offset,
        token=token,
    )
    return result


@router.get("/ledgers/{ledger_name}")
async def get_ledger_details(
    ledger_name: str,
    company: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get ledger details with transactions"""
    result = await tally_service.get_ledger_details(
        ledger_name=ledger_name,
        company=company,
        token=token,
    )
    return result


@router.get("/vouchers")
async def get_vouchers(
    company: Optional[str] = None,
    voucher_type: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get vouchers from TallyInsight"""
    result = await tally_service.get_vouchers(
        company=company,
        voucher_type=voucher_type,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
        token=token,
    )
    return result


@router.get("/stock-items")
async def get_stock_items(
    company: Optional[str] = None,
    group: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get stock items from TallyInsight"""
    result = await tally_service.get_stock_items(
        company=company,
        group=group,
        limit=limit,
        offset=offset,
        token=token,
    )
    return result


@router.get("/groups")
async def get_groups(
    company: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get account groups from TallyInsight"""
    result = await tally_service.get_groups(company=company, token=token)
    return result


# ==================== REPORTS ====================

@router.get("/reports/trial-balance")
async def get_trial_balance(
    company: Optional[str] = None,
    as_on_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get trial balance report"""
    result = await tally_service.get_trial_balance(
        company=company,
        as_on_date=as_on_date,
        token=token,
    )
    return result


@router.get("/reports/outstanding")
async def get_outstanding(
    company: Optional[str] = None,
    party_type: str = Query("receivable", description="receivable or payable"),
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get outstanding receivables/payables"""
    result = await tally_service.get_outstanding(
        company=company,
        party_type=party_type,
        token=token,
    )
    return result


@router.get("/reports/dashboard")
async def get_dashboard(
    company: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Get dashboard summary"""
    result = await tally_service.get_dashboard_summary(company=company, token=token)
    return result


# ==================== DELETE OPERATIONS ====================

@router.delete("/company/{company_name}")
async def delete_company(
    company_name: str,
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
    db: Session = Depends(get_db)
):
    """Delete a company from TallyInsight database"""
    # Log delete request
    create_audit_trail(
        db=db,
        user_id=current_user.id,
        action="tally_company_delete",
        resource_type="company",
        resource_id=None,
        details={"company_name": company_name}
    )

    result = await tally_service.delete_company(company_name, token=token)
    return result


# ==================== PDF EXPORT ====================

@router.get("/ledger-billwise/pdf")
async def get_ledger_billwise_pdf(
    ledger: str = Query(..., description="Ledger name"),
    company: Optional[str] = None,
    from_date: Optional[str] = Query(default=None, description="From date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(default=None, description="To date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Proxy to TallyInsight for Bill-wise PDF generation"""
    result = await tally_service.get_ledger_billwise_pdf(
        ledger=ledger,
        company=company,
        from_date=from_date,
        to_date=to_date,
        token=token,
    )
    return result


@router.get("/ledger-report/pdf")
async def get_ledger_report_pdf(
    ledger: str = Query(..., description="Ledger name"),
    company: Optional[str] = None,
    from_date: Optional[str] = Query(default=None, description="From date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(default=None, description="To date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_raw_token),
):
    """Proxy to TallyInsight for Ledger Report PDF generation"""
    result = await tally_service.get_ledger_report_pdf(
        ledger=ledger,
        company=company,
        from_date=from_date,
        to_date=to_date,
        token=token,
    )
    return result

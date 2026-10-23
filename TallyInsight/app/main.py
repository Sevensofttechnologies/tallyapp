"""
TallyInsight - Tally ERP Business Intelligence
Main Application Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from .config import config
from .utils.logger import setup_logger, logger
from .middleware.auth import jwt_bearer, require_role
from .controllers.sync_controller import router as sync_router
from .controllers.config_controller import router as config_router
from .controllers.health_controller import router as health_router
from .controllers.log_controller import router as log_router
from .controllers.debug_controller import router as debug_router
from .controllers.audit_controller import router as audit_router
# Separated controllers (from data_controller.py)
from .controllers.master_controller import router as master_router
from .controllers.voucher_controller import router as voucher_router
from .controllers.outstanding_controller import router as outstanding_router
from .controllers.ledger_controller import router as ledger_router
from .controllers.dashboard_controller import router as dashboard_router
# Protected routes (JWT auth required)
from .controllers.protected_controller import router as protected_router


# Setup logging
setup_logger(
    level=config.logging.level,
    log_file=config.logging.file,
    max_size=config.logging.max_size,
    backup_count=config.logging.backup_count,
    console=config.logging.console,
    colorize=config.logging.colorize
)

# ---------------------------------------------------------------------------
# Reusable dependency objects
# ---------------------------------------------------------------------------
_jwt_dep = [Depends(jwt_bearer)]
_admin_dep = [require_role(["admin", "super_admin"])]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("TallyInsight starting...")
    logger.info(f"API running on http://{config.api.host}:{config.api.port}")

    # Ensure company_config table exists on startup
    from .services.database_service import database_service
    await database_service.connect()
    await database_service.ensure_company_config_table()
    await database_service.disconnect()

    yield
    logger.info("TallyInsight shutting down...")


# Create FastAPI application
app = FastAPI(
    title="TallyInsight",
    description="Sync Tally ERP data to SQLite database",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware — origins come from env var CORS_ORIGINS (no wildcard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (includes voucher-report subfolder)
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
# Health — intentionally open (docker healthcheck depends on GET /api/health)
app.include_router(health_router, prefix="/api/health", tags=["Health"])

# Sync — JWT required
app.include_router(sync_router, prefix="/api/sync", tags=["Sync"],
                   dependencies=_jwt_dep)

# Config — JWT required; PUT /api/config and POST /api/config/tally/test are
# admin-only (enforced inside config_controller via require_role dependency).
app.include_router(config_router, prefix="/api/config", tags=["Config"],
                   dependencies=_jwt_dep)

# Logs — admin only
app.include_router(log_router, prefix="/api/logs", tags=["Logs"],
                   dependencies=_admin_dep)

# Debug — admin only
app.include_router(debug_router, prefix="/api/debug", tags=["Debug"],
                   dependencies=_admin_dep)

# Audit — JWT required; POST /api/audit/restore/{id} is admin-only
# (enforced inside audit_controller via require_role dependency).
app.include_router(audit_router, dependencies=_jwt_dep)

# Data controllers — JWT required
app.include_router(master_router, prefix="/api/data", tags=["Master Data"],
                   dependencies=_jwt_dep)
app.include_router(voucher_router, prefix="/api/data", tags=["Vouchers"],
                   dependencies=_jwt_dep)
app.include_router(outstanding_router, prefix="/api/data", tags=["Outstanding"],
                   dependencies=_jwt_dep)
app.include_router(ledger_router, prefix="/api/data", tags=["Ledger Reports"],
                   dependencies=_jwt_dep)
# dashboard_router includes POST /query which has its own require_role + ENABLE_RAW_QUERY gate
app.include_router(dashboard_router, prefix="/api/data", tags=["Dashboard"],
                   dependencies=_jwt_dep)

# Protected routes (already JWT-gated by design)
app.include_router(protected_router, prefix="/api/protected",
                   tags=["Protected (Auth Required)"],
                   dependencies=_jwt_dep)


# ---------------------------------------------------------------------------
# Static page routes (serve HTML — no auth required at HTTP level;
# the pages themselves will redirect to login if the JS token is missing)
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    """Serve the home/index page"""
    html_path = Path(__file__).parent.parent / "static" / "index.html"
    if html_path.exists():
        return FileResponse(str(html_path), media_type="text/html")
    return {"name": "TallyInsight", "version": "2.4.0", "docs": "/docs"}


@app.get("/index.html")
async def index_page():
    """Serve index page"""
    html_path = Path(__file__).parent.parent / "static" / "index.html"
    if html_path.exists():
        return FileResponse(str(html_path), media_type="text/html")
    return {"error": "Page not found"}


@app.get("/sync.html")
async def sync_page():
    """Serve sync page"""
    html_path = Path(__file__).parent.parent / "static" / "sync.html"
    if html_path.exists():
        return FileResponse(str(html_path), media_type="text/html")
    return {"error": "Page not found"}


@app.get("/dashboard.html")
async def dashboard_page():
    """Serve dashboard page"""
    html_path = Path(__file__).parent.parent / "static" / "dashboard.html"
    if html_path.exists():
        return FileResponse(str(html_path), media_type="text/html")
    return {"error": "Page not found"}


@app.get("/audit.html")
async def audit_page():
    """Serve audit page"""
    html_path = Path(__file__).parent.parent / "static" / "audit.html"
    if html_path.exists():
        return FileResponse(str(html_path), media_type="text/html")
    return {"error": "Page not found"}


@app.get("/old")
async def old_dashboard():
    """Serve old dashboard (index.html)"""
    html_path = Path(__file__).parent.parent / "static" / "index.html"
    if html_path.exists():
        return FileResponse(str(html_path), media_type="text/html")
    return {"error": "Page not found"}


@app.get("/voucher-report")
@app.get("/voucher-report/")
@app.get("/voucher-report/index.html")
async def voucher_report_page():
    """Serve advanced voucher report page"""
    html_path = Path(__file__).parent.parent / "static" / "voucher-report" / "index.html"
    if html_path.exists():
        return FileResponse(str(html_path), media_type="text/html")
    return {"error": "Voucher Report page not found"}


@app.get("/outstanding-report")
@app.get("/outstanding-report/")
async def outstanding_report_page():
    """Serve outstanding report page"""
    html_path = Path(__file__).parent.parent / "static" / "outstanding-report" / "index.html"
    if html_path.exists():
        return FileResponse(str(html_path), media_type="text/html")
    return {"error": "Outstanding Report page not found"}


# ---------------------------------------------------------------------------
# Inline API routes — all require JWT except where noted
# ---------------------------------------------------------------------------

@app.get("/api/info", dependencies=_jwt_dep)
async def info():
    """System information"""
    return {
        "name": "TallyInsight",
        "version": "1.0.0",
        "tally": {
            "server": config.tally.server,
            "port": config.tally.port
        },
        "database": {
            "path": config.database.path
        }
    }


@app.post("/api/backup", dependencies=_jwt_dep)
async def create_backup():
    """Create database backup before full sync"""
    import shutil
    from datetime import datetime

    db_path = Path(config.database.path)
    if not db_path.exists():
        return {"status": "skipped", "message": "No database to backup"}

    # Create backups folder
    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(exist_ok=True)

    # Create backup with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"tally_backup_{timestamp}.db"

    try:
        shutil.copy2(db_path, backup_path)
        logger.info(f"Backup created: {backup_path}")

        # Keep only last 5 backups
        backups = sorted(backup_dir.glob("tally_backup_*.db"), reverse=True)
        for old_backup in backups[5:]:
            old_backup.unlink()
            logger.info(f"Deleted old backup: {old_backup}")

        return {
            "status": "success",
            "backup_path": str(backup_path),
            "message": f"Backup created successfully"
        }
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/backups", dependencies=_jwt_dep)
async def list_backups():
    """List all available backups"""
    db_path = Path(config.database.path)
    backup_dir = db_path.parent / "backups"

    if not backup_dir.exists():
        return {"backups": [], "count": 0}

    backups = []
    for backup_file in sorted(backup_dir.glob("tally_backup_*.db"), reverse=True):
        stat = backup_file.stat()
        # Parse timestamp from filename: tally_backup_20260107_110345.db
        filename = backup_file.stem
        try:
            timestamp_str = filename.replace("tally_backup_", "")
            from datetime import datetime
            timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            created_at = timestamp.isoformat()
        except Exception:
            created_at = None

        backups.append({
            "filename": backup_file.name,
            "path": str(backup_file),
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created_at": created_at
        })

    return {"backups": backups, "count": len(backups)}


@app.post("/api/backup/restore", dependencies=_admin_dep)
async def restore_backup(request: dict):
    """Restore database from a backup file (admin only)"""
    import shutil

    filename = request.get("filename")
    if not filename:
        return {"status": "error", "message": "Filename is required"}

    db_path = Path(config.database.path)
    backup_dir = db_path.parent / "backups"
    backup_path = backup_dir / filename

    if not backup_path.exists():
        return {"status": "error", "message": f"Backup file not found: {filename}"}

    try:
        # Create a backup of current database before restore
        if db_path.exists():
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pre_restore_backup = backup_dir / f"pre_restore_{timestamp}.db"
            shutil.copy2(db_path, pre_restore_backup)
            logger.info(f"Pre-restore backup created: {pre_restore_backup}")

        # Restore the backup
        shutil.copy2(backup_path, db_path)
        logger.info(f"Database restored from: {backup_path}")

        return {
            "status": "success",
            "message": f"Database restored from {filename}",
            "restored_from": str(backup_path)
        }
    except Exception as e:
        logger.error(f"Restore failed: {e}")
        return {"status": "error", "message": str(e)}


# ============== Schedule API ==============
from .services.scheduler_service import scheduler_service

@app.get("/api/schedule", dependencies=_jwt_dep)
async def get_schedule():
    """Get current schedule configuration"""
    return scheduler_service.get_status()


@app.post("/api/schedule", dependencies=_jwt_dep)
async def update_schedule(config: dict):
    """Update schedule configuration"""
    return scheduler_service.update_schedule(config)


@app.post("/api/schedule/run", dependencies=_jwt_dep)
async def run_scheduled_sync():
    """Trigger scheduled sync immediately"""
    return scheduler_service.run_now()


# ============== Crash Recovery API ==============
from .services.sync_service import sync_service as sync_svc

@app.get("/api/sync/incomplete", dependencies=_jwt_dep)
async def check_incomplete_sync():
    """Check for incomplete sync from previous crash"""
    incomplete = sync_svc.get_incomplete_sync()
    if incomplete:
        return {"has_incomplete": True, "sync_state": incomplete}
    return {"has_incomplete": False}


@app.post("/api/sync/incomplete/dismiss", dependencies=_jwt_dep)
async def dismiss_incomplete_sync():
    """Dismiss incomplete sync warning"""
    return sync_svc.dismiss_incomplete_sync()


# ============== Multi-Company API ==============
from .services.tally_service import tally_service
from .services.sync_queue_service import sync_queue_service

@app.get("/api/companies", dependencies=_jwt_dep)
async def get_open_companies():
    """Get list of all open companies in Tally"""
    companies = await tally_service.get_open_companies()
    return {"companies": companies, "count": len(companies)}


@app.get("/api/sync/queue", dependencies=_jwt_dep)
async def get_sync_queue_status():
    """Get sync queue status"""
    return sync_queue_service.get_status()


@app.post("/api/sync/queue", dependencies=_jwt_dep)
async def add_to_sync_queue(request: dict):
    """Add companies to sync queue"""
    companies = request.get("companies", [])
    sync_type = request.get("sync_type", "full")

    if not companies:
        return {"status": "error", "message": "No companies provided"}

    result = sync_queue_service.add_companies(companies, sync_type)
    return result


@app.post("/api/sync/queue/start", dependencies=_jwt_dep)
async def start_sync_queue():
    """Start processing sync queue"""
    return await sync_queue_service.start_processing()


@app.post("/api/sync/queue/cancel", dependencies=_jwt_dep)
async def cancel_sync_queue():
    """Cancel sync queue processing"""
    return sync_queue_service.cancel_queue()


@app.post("/api/sync/queue/clear", dependencies=_jwt_dep)
async def clear_sync_queue():
    """Clear sync queue"""
    return sync_queue_service.clear_queue()


@app.post("/api/db/migrate/company", dependencies=_admin_dep)
async def migrate_add_company_column():
    """Add _company column to all tables for multi-company support (admin only)"""
    from .services.database_service import database_service
    await database_service.connect()
    result = await database_service.add_company_column_to_tables()
    return result


@app.post("/api/config/date-range", dependencies=_jwt_dep)
async def update_date_range(request: dict):
    """Update sync date range"""
    from_date = request.get("from_date", "")
    to_date = request.get("to_date", "")

    if from_date:
        config.tally.from_date = from_date
    if to_date:
        config.tally.to_date = to_date

    return {
        "status": "success",
        "from_date": config.tally.from_date,
        "to_date": config.tally.to_date
    }


@app.get("/api/config/date-range", dependencies=_jwt_dep)
async def get_date_range():
    """Get current sync date range"""
    return {
        "from_date": config.tally.from_date,
        "to_date": config.tally.to_date
    }


@app.get("/api/synced-companies", dependencies=_jwt_dep)
async def get_synced_companies():
    """Get list of companies that have been synced (from config table)"""
    from .services.database_service import database_service
    try:
        await database_service.connect()

        # First try: Get from config table (Company Name value)
        config_result = await database_service.fetch_one(
            "SELECT value FROM config WHERE name = 'Company Name'"
        )
        companies = []
        if config_result and config_result.get('value'):
            company_name = config_result.get('value')
            if company_name and company_name != 'Unknown':
                companies.append(company_name)

        # Also try sync_history if company_name column exists
        try:
            history_result = await database_service.fetch_all(
                "SELECT DISTINCT company_name FROM sync_history WHERE status = 'completed' AND company_name IS NOT NULL AND company_name != '' ORDER BY company_name"
            )
            for row in history_result:
                if row.get('company_name') and row['company_name'] not in companies:
                    companies.append(row['company_name'])
        except Exception:
            pass  # Column might not exist yet

        await database_service.disconnect()
        return {"synced_companies": companies}
    except Exception as e:
        return {"synced_companies": [], "error": str(e)}

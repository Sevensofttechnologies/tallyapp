"""
Database Configuration and Session Management
Supports: SQLite, SQL Server, PostgreSQL, MySQL
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def get_engine_args(database_url: str) -> dict:
    """
    Get database-specific engine arguments
    
    Supported databases:
    - SQLite: sqlite:///./app.db
    - SQL Server: mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server
    - PostgreSQL: postgresql://user:pass@localhost/db
    - MySQL: mysql+pymysql://user:pass@localhost/db
    """
    engine_args = {}
    
    if database_url.startswith("sqlite"):
        # SQLite specific settings
        engine_args = {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }
        logger.info("Using SQLite database")
        
    elif database_url.startswith("mssql") or database_url.startswith("mssql+pyodbc"):
        # SQL Server specific settings
        engine_args = {
            "pool_pre_ping": True,
            "pool_size": 10,
            "max_overflow": 20,
            "pool_recycle": 300,
        }
        logger.info("Using SQL Server database")
        
    elif database_url.startswith("postgresql"):
        # PostgreSQL specific settings
        engine_args = {
            "pool_pre_ping": True,
            "pool_size": 10,
            "max_overflow": 20,
            "pool_recycle": 300,
        }
        logger.info("Using PostgreSQL database")
        
    elif database_url.startswith("mysql"):
        # MySQL specific settings
        engine_args = {
            "pool_pre_ping": True,
            "pool_size": 10,
            "max_overflow": 20,
            "pool_recycle": 300,
        }
        logger.info("Using MySQL database")
        
    else:
        logger.warning(f"Unknown database type: {database_url}")
    
    return engine_args


# Get engine arguments based on database type
engine_args = get_engine_args(settings.DATABASE_URL)

# Create database engine
engine = create_engine(settings.DATABASE_URL, **engine_args)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """
    Database session dependency
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    Call this on application startup
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")


def get_db_info() -> dict:
    """
    Get database connection information
    """
    db_url = settings.DATABASE_URL
    
    if db_url.startswith("sqlite"):
        db_type = "SQLite"
    elif db_url.startswith("mssql"):
        db_type = "SQL Server"
    elif db_url.startswith("postgresql"):
        db_type = "PostgreSQL"
    elif db_url.startswith("mysql"):
        db_type = "MySQL"
    else:
        db_type = "Unknown"
    
    return {
        "type": db_type,
        "connected": True,
        "pool_size": engine_args.get("pool_size", "N/A"),
    }

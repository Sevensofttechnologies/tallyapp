"""
Complete CRUD Test Script
Sarv Models che CRUD Operations Test Karnyasathi Script

Tests:
1. User - Create, Read, Update, Delete
2. Company - Create, Read, Update, Delete
3. UserCompany - Create, Read, Update, Delete
4. Permission - Create, Read, Update, Delete
5. RolePermission - Create, Read, Update, Delete
6. AuditTrail - Create, Read
7. Log - Create, Read

Run: python tests/test_crud_complete.py
"""

import sys
import os
from datetime import datetime
from colorama import init, Fore, Style

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User, Company, UserCompany, Permission, RolePermission, AuditTrail, Log

# Initialize colorama for colored output
init()

# Test database (use separate test db to avoid affecting production)
TEST_DB_URL = "sqlite:///./test_crud.db"

# Create engine and session
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Test counters
tests_passed = 0
tests_failed = 0
test_results = []


def print_header(text):
    """Print section header"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Style.RESET_ALL}")


def print_success(text):
    """Print success message"""
    global tests_passed
    tests_passed += 1
    print(f"  {Fore.GREEN}[PASS] {text}{Style.RESET_ALL}")
    test_results.append(("PASS", text))


def print_error(text, error=None):
    """Print error message"""
    global tests_failed
    tests_failed += 1
    print(f"  {Fore.RED}[FAIL] {text}{Style.RESET_ALL}")
    if error:
        print(f"    {Fore.RED}Error: {error}{Style.RESET_ALL}")
    test_results.append(("FAIL", text))


def print_info(text):
    """Print info message"""
    print(f"  {Fore.YELLOW}[INFO] {text}{Style.RESET_ALL}")


def setup_database():
    """Create all tables"""
    print_header("DATABASE SETUP")
    try:
        Base.metadata.create_all(bind=engine)
        print_success("Database tables created successfully")
        return True
    except Exception as e:
        print_error("Failed to create database tables", str(e))
        return False


def cleanup_database():
    """Drop all tables"""
    print_header("DATABASE CLEANUP")
    try:
        Base.metadata.drop_all(bind=engine)
        print_success("Database tables dropped successfully")
        
        # Delete test database file
        if os.path.exists("test_crud.db"):
            os.remove("test_crud.db")
            print_success("Test database file deleted")
        return True
    except Exception as e:
        print_error("Failed to cleanup database", str(e))
        return False


# ============================================================
# USER CRUD TESTS
# ============================================================
def test_user_crud():
    """Test User model CRUD operations"""
    print_header("USER CRUD TESTS")
    db = SessionLocal()
    user_id = None
    
    try:
        # CREATE
        print_info("Testing CREATE...")
        user = User(
            email="test@example.com",
            password_hash="hashed_password_123",
            first_name="Test",
            last_name="User",
            phone="9876543210",
            role="user",
            is_active=True,
            is_verified=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id
        
        if user.id:
            print_success(f"CREATE: User created with ID={user.id}")
        else:
            print_error("CREATE: Failed to create user")
        
        # READ
        print_info("Testing READ...")
        fetched_user = db.query(User).filter(User.id == user_id).first()
        if fetched_user and fetched_user.email == "test@example.com":
            print_success(f"READ: User fetched - {fetched_user.email}")
        else:
            print_error("READ: Failed to fetch user")
        
        # READ ALL
        all_users = db.query(User).all()
        print_success(f"READ ALL: Found {len(all_users)} user(s)")
        
        # UPDATE
        print_info("Testing UPDATE...")
        fetched_user.first_name = "Updated"
        fetched_user.phone = "1234567890"
        db.commit()
        db.refresh(fetched_user)
        
        if fetched_user.first_name == "Updated":
            print_success(f"UPDATE: User updated - first_name='{fetched_user.first_name}'")
        else:
            print_error("UPDATE: Failed to update user")
        
        # DELETE
        print_info("Testing DELETE...")
        db.delete(fetched_user)
        db.commit()
        
        deleted_user = db.query(User).filter(User.id == user_id).first()
        if deleted_user is None:
            print_success("DELETE: User deleted successfully")
        else:
            print_error("DELETE: Failed to delete user")
            
    except Exception as e:
        print_error(f"User CRUD test failed", str(e))
        db.rollback()
    finally:
        db.close()


# ============================================================
# COMPANY CRUD TESTS
# ============================================================
def test_company_crud():
    """Test Company model CRUD operations"""
    print_header("COMPANY CRUD TESTS")
    db = SessionLocal()
    company_id = None
    
    try:
        # CREATE
        print_info("Testing CREATE...")
        company = Company(
            name="Test Company Pvt Ltd",
            email="company@test.com",
            phone="9876543210",
            address="123 Test Street",
            city="Pune",
            state="Maharashtra",
            country="India",
            zip_code="411001",
            website="https://testcompany.com",
            industry="Technology",
            company_size="50-100",
            status="active"
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        company_id = company.id
        
        if company.id:
            print_success(f"CREATE: Company created with ID={company.id}")
        else:
            print_error("CREATE: Failed to create company")
        
        # READ
        print_info("Testing READ...")
        fetched_company = db.query(Company).filter(Company.id == company_id).first()
        if fetched_company and fetched_company.name == "Test Company Pvt Ltd":
            print_success(f"READ: Company fetched - {fetched_company.name}")
        else:
            print_error("READ: Failed to fetch company")
        
        # READ ALL
        all_companies = db.query(Company).all()
        print_success(f"READ ALL: Found {len(all_companies)} company(ies)")
        
        # UPDATE
        print_info("Testing UPDATE...")
        fetched_company.name = "Updated Company Name"
        fetched_company.city = "Mumbai"
        db.commit()
        db.refresh(fetched_company)
        
        if fetched_company.name == "Updated Company Name":
            print_success(f"UPDATE: Company updated - name='{fetched_company.name}'")
        else:
            print_error("UPDATE: Failed to update company")
        
        # DELETE
        print_info("Testing DELETE...")
        db.delete(fetched_company)
        db.commit()
        
        deleted_company = db.query(Company).filter(Company.id == company_id).first()
        if deleted_company is None:
            print_success("DELETE: Company deleted successfully")
        else:
            print_error("DELETE: Failed to delete company")
            
    except Exception as e:
        print_error(f"Company CRUD test failed", str(e))
        db.rollback()
    finally:
        db.close()


# ============================================================
# PERMISSION CRUD TESTS
# ============================================================
def test_permission_crud():
    """Test Permission model CRUD operations"""
    print_header("PERMISSION CRUD TESTS")
    db = SessionLocal()
    permission_id = None
    
    try:
        # CREATE
        print_info("Testing CREATE...")
        permission = Permission(
            resource="user",
            action="create",
            description="Permission to create users"
        )
        db.add(permission)
        db.commit()
        db.refresh(permission)
        permission_id = permission.id
        
        if permission.id:
            print_success(f"CREATE: Permission created with ID={permission.id}")
        else:
            print_error("CREATE: Failed to create permission")
        
        # READ
        print_info("Testing READ...")
        fetched_permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if fetched_permission and fetched_permission.resource == "user":
            print_success(f"READ: Permission fetched - {fetched_permission.resource}:{fetched_permission.action}")
        else:
            print_error("READ: Failed to fetch permission")
        
        # READ ALL
        all_permissions = db.query(Permission).all()
        print_success(f"READ ALL: Found {len(all_permissions)} permission(s)")
        
        # UPDATE
        print_info("Testing UPDATE...")
        fetched_permission.description = "Updated description"
        db.commit()
        db.refresh(fetched_permission)
        
        if fetched_permission.description == "Updated description":
            print_success(f"UPDATE: Permission updated - description='{fetched_permission.description}'")
        else:
            print_error("UPDATE: Failed to update permission")
        
        # DELETE
        print_info("Testing DELETE...")
        db.delete(fetched_permission)
        db.commit()
        
        deleted_permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if deleted_permission is None:
            print_success("DELETE: Permission deleted successfully")
        else:
            print_error("DELETE: Failed to delete permission")
            
    except Exception as e:
        print_error(f"Permission CRUD test failed", str(e))
        db.rollback()
    finally:
        db.close()


# ============================================================
# USER-COMPANY RELATIONSHIP TESTS
# ============================================================
def test_user_company_crud():
    """Test UserCompany relationship CRUD operations"""
    print_header("USER-COMPANY RELATIONSHIP TESTS")
    db = SessionLocal()
    
    try:
        # First create a user and company
        print_info("Creating test user and company...")
        
        user = User(
            email="relation_test@example.com",
            password_hash="hashed_password",
            first_name="Relation",
            last_name="Test",
            role="admin"
        )
        db.add(user)
        
        company = Company(
            name="Relation Test Company",
            email="relation@company.com",
            status="active"
        )
        db.add(company)
        db.commit()
        db.refresh(user)
        db.refresh(company)
        
        print_success(f"Created User ID={user.id} and Company ID={company.id}")
        
        # CREATE UserCompany relationship
        print_info("Testing CREATE relationship...")
        from app.models.user_company import UserCompany
        
        user_company = UserCompany(
            user_id=user.id,
            company_id=company.id,
            role="admin",
            is_primary=True
        )
        db.add(user_company)
        db.commit()
        db.refresh(user_company)
        
        if user_company.id:
            print_success(f"CREATE: UserCompany relationship created with ID={user_company.id}")
        else:
            print_error("CREATE: Failed to create relationship")
        
        # READ
        print_info("Testing READ relationship...")
        fetched_uc = db.query(UserCompany).filter(
            UserCompany.user_id == user.id,
            UserCompany.company_id == company.id
        ).first()
        
        if fetched_uc:
            print_success(f"READ: Relationship fetched - User {fetched_uc.user_id} -> Company {fetched_uc.company_id}")
        else:
            print_error("READ: Failed to fetch relationship")
        
        # UPDATE
        print_info("Testing UPDATE relationship...")
        fetched_uc.role = "manager"
        fetched_uc.is_primary = False
        db.commit()
        db.refresh(fetched_uc)
        
        if fetched_uc.role == "manager":
            print_success(f"UPDATE: Relationship updated - role='{fetched_uc.role}'")
        else:
            print_error("UPDATE: Failed to update relationship")
        
        # DELETE
        print_info("Testing DELETE relationship...")
        db.delete(fetched_uc)
        db.commit()
        
        deleted_uc = db.query(UserCompany).filter(
            UserCompany.user_id == user.id,
            UserCompany.company_id == company.id
        ).first()
        
        if deleted_uc is None:
            print_success("DELETE: Relationship deleted successfully")
        else:
            print_error("DELETE: Failed to delete relationship")
        
        # Cleanup
        db.delete(user)
        db.delete(company)
        db.commit()
        print_success("Cleanup: Test user and company deleted")
            
    except Exception as e:
        print_error(f"UserCompany CRUD test failed", str(e))
        db.rollback()
    finally:
        db.close()


# ============================================================
# ROLE PERMISSION TESTS
# ============================================================
def test_role_permission_crud():
    """Test RolePermission model CRUD operations"""
    print_header("ROLE PERMISSION CRUD TESTS")
    db = SessionLocal()
    
    try:
        # First create a permission and company
        print_info("Creating test permission and company...")
        
        permission = Permission(
            resource="test_resource",
            action="test_action",
            description="Test permission"
        )
        db.add(permission)
        
        company = Company(
            name="Role Test Company",
            email="roletest@company.com",
            status="active"
        )
        db.add(company)
        db.commit()
        db.refresh(permission)
        db.refresh(company)
        
        print_success(f"Created Permission ID={permission.id} and Company ID={company.id}")
        
        # CREATE RolePermission
        print_info("Testing CREATE...")
        role_permission = RolePermission(
            permission_id=permission.id,
            role="admin",
            company_id=company.id,
            granted=True
        )
        db.add(role_permission)
        db.commit()
        db.refresh(role_permission)
        
        if role_permission.id:
            print_success(f"CREATE: RolePermission created with ID={role_permission.id}")
        else:
            print_error("CREATE: Failed to create role permission")
        
        # READ
        print_info("Testing READ...")
        fetched_rp = db.query(RolePermission).filter(RolePermission.id == role_permission.id).first()
        if fetched_rp and fetched_rp.role == "admin":
            print_success(f"READ: RolePermission fetched - role='{fetched_rp.role}'")
        else:
            print_error("READ: Failed to fetch role permission")
        
        # UPDATE
        print_info("Testing UPDATE...")
        fetched_rp.granted = False
        db.commit()
        db.refresh(fetched_rp)
        
        if fetched_rp.granted == False:
            print_success(f"UPDATE: RolePermission updated - granted={fetched_rp.granted}")
        else:
            print_error("UPDATE: Failed to update role permission")
        
        # DELETE
        print_info("Testing DELETE...")
        db.delete(fetched_rp)
        db.commit()
        
        deleted_rp = db.query(RolePermission).filter(RolePermission.id == role_permission.id).first()
        if deleted_rp is None:
            print_success("DELETE: RolePermission deleted successfully")
        else:
            print_error("DELETE: Failed to delete role permission")
        
        # Cleanup
        db.delete(permission)
        db.delete(company)
        db.commit()
        print_success("Cleanup: Test permission and company deleted")
            
    except Exception as e:
        print_error(f"RolePermission CRUD test failed", str(e))
        db.rollback()
    finally:
        db.close()


# ============================================================
# AUDIT TRAIL TESTS
# ============================================================
def test_audit_trail_crud():
    """Test AuditTrail model CRUD operations"""
    print_header("AUDIT TRAIL CRUD TESTS")
    db = SessionLocal()
    
    try:
        # CREATE
        print_info("Testing CREATE...")
        audit = AuditTrail(
            user_id=None,
            user_email="test@example.com",
            action="CREATE",
            resource_type="user",
            resource_id=1,
            old_values=None,
            new_values={"email": "test@example.com", "first_name": "Test"},
            ip_address="127.0.0.1",
            user_agent="Test Script",
            status="SUCCESS",
            message="User created successfully"
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        
        if audit.id:
            print_success(f"CREATE: AuditTrail created with ID={audit.id}")
        else:
            print_error("CREATE: Failed to create audit trail")
        
        # READ
        print_info("Testing READ...")
        fetched_audit = db.query(AuditTrail).filter(AuditTrail.id == audit.id).first()
        if fetched_audit and fetched_audit.action == "CREATE":
            print_success(f"READ: AuditTrail fetched - action='{fetched_audit.action}'")
        else:
            print_error("READ: Failed to fetch audit trail")
        
        # READ ALL
        all_audits = db.query(AuditTrail).all()
        print_success(f"READ ALL: Found {len(all_audits)} audit record(s)")
        
        # Note: Audit trails are typically not updated or deleted
        print_info("Note: Audit trails are immutable (no UPDATE/DELETE tests)")
        
        # DELETE (for cleanup only)
        db.delete(fetched_audit)
        db.commit()
        print_success("Cleanup: Test audit record deleted")
            
    except Exception as e:
        print_error(f"AuditTrail CRUD test failed", str(e))
        db.rollback()
    finally:
        db.close()


# ============================================================
# LOG TESTS
# ============================================================
def test_log_crud():
    """Test Log model CRUD operations"""
    print_header("LOG CRUD TESTS")
    db = SessionLocal()
    
    try:
        # CREATE
        print_info("Testing CREATE...")
        log = Log(
            level="INFO",
            category="AUTH",
            action="LOGIN",
            user_id=None,
            user_email="test@example.com",
            ip_address="127.0.0.1",
            details={"browser": "Chrome", "os": "Windows"},
            status="SUCCESS",
            message="User logged in successfully"
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        
        if log.id:
            print_success(f"CREATE: Log created with ID={log.id}")
        else:
            print_error("CREATE: Failed to create log")
        
        # READ
        print_info("Testing READ...")
        fetched_log = db.query(Log).filter(Log.id == log.id).first()
        if fetched_log and fetched_log.level == "INFO":
            print_success(f"READ: Log fetched - level='{fetched_log.level}', action='{fetched_log.action}'")
        else:
            print_error("READ: Failed to fetch log")
        
        # READ ALL
        all_logs = db.query(Log).all()
        print_success(f"READ ALL: Found {len(all_logs)} log record(s)")
        
        # Note: Logs are typically not updated or deleted
        print_info("Note: Logs are immutable (no UPDATE/DELETE tests)")
        
        # DELETE (for cleanup only)
        db.delete(fetched_log)
        db.commit()
        print_success("Cleanup: Test log record deleted")
            
    except Exception as e:
        print_error(f"Log CRUD test failed", str(e))
        db.rollback()
    finally:
        db.close()


# ============================================================
# DATABASE VERIFICATION
# ============================================================
def verify_database_tables():
    """Verify all tables exist in database"""
    print_header("DATABASE TABLE VERIFICATION")
    db = SessionLocal()
    
    expected_tables = [
        "users",
        "companies", 
        "user_companies",
        "permissions",
        "role_permissions",
        "audit_trails",
        "logs",
        "password_reset_tokens"
    ]
    
    try:
        # Get all table names
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        existing_tables = [row[0] for row in result.fetchall()]
        
        print_info(f"Found {len(existing_tables)} tables in database")
        
        for table in expected_tables:
            if table in existing_tables:
                print_success(f"Table '{table}' exists")
            else:
                print_error(f"Table '{table}' NOT FOUND")
        
    except Exception as e:
        print_error(f"Database verification failed", str(e))
    finally:
        db.close()


# ============================================================
# MAIN TEST RUNNER
# ============================================================
def run_all_tests():
    """Run all CRUD tests"""
    print(f"\n{Fore.MAGENTA}{'#'*60}")
    print(f"#  COMPLETE CRUD TEST SUITE")
    print(f"#  Sarv Models che CRUD Operations Test")
    print(f"#  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*60}{Style.RESET_ALL}")
    
    # Setup
    if not setup_database():
        print(f"\n{Fore.RED}Setup failed! Exiting...{Style.RESET_ALL}")
        return
    
    # Verify tables
    verify_database_tables()
    
    # Run all CRUD tests
    test_user_crud()
    test_company_crud()
    test_permission_crud()
    test_user_company_crud()
    test_role_permission_crud()
    test_audit_trail_crud()
    test_log_crud()
    
    # Cleanup
    cleanup_database()
    
    # Print summary
    print_header("TEST SUMMARY")
    print(f"\n  {Fore.GREEN}Passed: {tests_passed}{Style.RESET_ALL}")
    print(f"  {Fore.RED}Failed: {tests_failed}{Style.RESET_ALL}")
    print(f"  Total Tests: {tests_passed + tests_failed}")
    
    # Pass rate
    total = tests_passed + tests_failed
    if total > 0:
        pass_rate = (tests_passed / total) * 100
        color = Fore.GREEN if pass_rate == 100 else (Fore.YELLOW if pass_rate >= 80 else Fore.RED)
        print(f"\n  {color}Pass Rate: {pass_rate:.1f}%{Style.RESET_ALL}")
    
    # Final status
    if tests_failed == 0:
        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"  ALL TESTS PASSED! Sarv Tests Yashasvi!")
        print(f"{'='*60}{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}{'='*60}")
        print(f"  SOME TESTS FAILED! Kahi Tests Ayashasvi!")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        # Show failed tests
        print(f"\n{Fore.RED}Failed Tests:{Style.RESET_ALL}")
        for status, test in test_results:
            if status == "FAIL":
                print(f"  - {test}")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Test suite failed: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()

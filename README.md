# TallyInsightPlus

**Enterprise-Grade Tally ERP Integration Platform**

A microservices-based platform that integrates **TallyBridge** (Multi-tenant SaaS Application) with **TallyInsight** (Tally ERP Sync Service) for seamless Tally Prime data access and reporting.

## ✨ Key Features

### 🔐 Authentication & Security
- JWT-based authentication with secure token management
- Role-based access control (Super Admin, Admin, User)
- Multi-tenant architecture with company-level isolation
- Content Security Policy (CSP) headers

### 📊 Reports Module
- **Voucher Report** - Sales, Purchase, Payment, Receipt, Journal, Contra
- **Outstanding Report** - Receivable/Payable with Ledger-wise, Bill-wise, Ageing tabs
- **Ledger Report** - Transaction history with Bill-wise breakdown

### 🔄 Tally Integration
- Real-time sync with Tally Prime (Port 9000)
- Incremental sync using AlterID tracking
- Multi-company support
- Automatic company creation on first sync

### 🎨 Modern UI
- Clean, responsive admin dashboard
- Professional sidebar navigation
- Interactive data tables with sorting & pagination
- Modal dialogs for detailed views
- Export to Excel functionality

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      TallyBots Platform                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐         ┌─────────────────┐            │
│  │   TallyBridge   │◄───────►│  TallyInsight   │            │
│  │   (Port 8501)   │   JWT   │   (Port 8000)   │            │
│  │                 │   Auth  │                 │            │
│  │ • Auth/Users    │         │ • Tally Sync    │            │
│  │ • Companies     │         │ • Data Storage  │            │
│  │ • Multi-tenant  │         │ • Reports       │            │
│  │ • Frontend      │         │ • APIs          │            │
│  └────────┬────────┘         └────────┬────────┘            │
│           │                           │                      │
│           ▼                           ▼                      │
│  ┌─────────────────┐         ┌─────────────────┐            │
│  │ tallybridge.db  │         │    tally.db     │            │
│  │ (Users, Cos)    │         │ (Tally Data)    │            │
│  └─────────────────┘         └─────────────────┘            │
│                                       │                      │
│                                       ▼                      │
│                              ┌─────────────────┐            │
│                              │   Tally ERP     │            │
│                              │  (Port 9000)    │            │
│                              └─────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
TallyBots/
├── TallyBridge/           # Main Application (FastAPI)
│   ├── app/
│   │   ├── routes/        # API endpoints
│   │   │   └── tally.py   # Tally integration routes
│   │   ├── services/
│   │   │   └── tally_service.py  # HTTP client for TallyInsight
│   │   ├── models/
│   │   └── schemas/
│   ├── frontend/          # HTML/JS frontend
│   │   ├── tally-sync.html
│   │   ├── tally-ledgers.html
│   │   ├── tally-vouchers.html
│   │   └── tally-reports.html
│   └── tests/
│
├── TallyInsight/          # Tally Sync Microservice (FastAPI)
│   ├── app/
│   │   ├── middleware/
│   │   │   └── auth.py    # JWT authentication
│   │   ├── controllers/
│   │   └── services/
│   └── static/
│
├── docker-compose.yml     # Docker orchestration
├── PROJECT_PLAN.md        # Detailed project plan
└── TASK_LIST.md           # Task tracking
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Tally ERP (running on port 9000)
- Docker (optional)

### Option 1: Run Locally

1. **Start TallyInsight** (Port 8000):
```bash
cd TallyInsight
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. **Start TallyBridge** (Port 8501):
```bash
cd TallyBridge
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8501 --reload
```

3. **Access the Application**:
- TallyBridge: http://localhost:8501
- TallyInsight: http://localhost:8000
- API Docs: http://localhost:8501/docs

### Option 2: Run with Docker

```bash
cd TallyBots
docker-compose up -d
```

## 🔐 Configuration

### Environment Variables

**TallyBridge (.env)**:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./tallybridge.db
TALLY_SERVICE_URL=http://localhost:8000
```

**TallyInsight (.env)**:
```env
SECRET_KEY=your-secret-key-here  # Must match TallyBridge
DATABASE_PATH=./tally.db
TALLY_SERVER=localhost
TALLY_PORT=9000
```

> ⚠️ **Important**: Both services must use the same `SECRET_KEY` for JWT authentication.

## 📡 API Endpoints

### TallyBridge Tally Routes (`/api/v1/tally/`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Check TallyInsight health |
| `/companies` | GET | Get Tally companies |
| `/synced-companies` | GET | Get synced companies |
| `/sync` | POST | Trigger company sync |
| `/ledgers` | GET | Get ledgers (paginated) |
| `/ledgers/{name}` | GET | Get ledger details |
| `/vouchers` | GET | Get vouchers (filtered) |
| `/stock-items` | GET | Get stock items |
| `/groups` | GET | Get account groups |
| `/reports/trial-balance` | GET | Trial balance report |
| `/reports/outstanding` | GET | Outstanding receivables/payables |
| `/reports/dashboard` | GET | Dashboard summary |
| `/webhook/sync-complete` | POST | Sync completion webhook |

### Authentication

All Tally endpoints (except `/health`) require JWT authentication:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8501/api/v1/tally/ledgers
```

## 🔄 Sync Flow

1. User logs into TallyBridge
2. User navigates to Tally Sync page
3. TallyBridge fetches companies from TallyInsight
4. User selects company and triggers sync
5. TallyInsight syncs data from Tally ERP
6. TallyInsight calls webhook to notify TallyBridge
7. TallyBridge auto-creates company record
8. User can now access Tally data through TallyBridge

## 🧪 Testing

```bash
# Run TallyBridge tests
cd TallyBridge
pytest tests/ -v

# Run TallyInsight tests
cd TallyInsight
pytest tests/ -v

# Test Tally integration
python scripts/test_tally_integration.py
```

## 📊 Database Schema

### TallyBridge - Companies Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | VARCHAR(255) | Company name |
| tally_guid | VARCHAR(100) | Tally company GUID |
| tally_server | VARCHAR(100) | Tally server address |
| tally_port | INTEGER | Tally port (default: 9000) |
| last_sync_at | DATETIME | Last sync timestamp |
| last_alter_id | INTEGER | Tally AlterID for incremental sync |

### TallyInsight - Key Tables

- `company_config` - Synced company configurations
- `mst_ledger` - Ledger masters
- `mst_stock_item` - Stock item masters
- `trn_voucher` - Voucher transactions
- `trn_accounting` - Accounting entries
- `audit_log` - Sync audit trail

## 🛠️ Development

### Adding New Tally Endpoints

1. Add method to `TallyBridge/app/services/tally_service.py`
2. Add route to `TallyBridge/app/routes/tally.py`
3. Add API function to `TallyBridge/frontend/js/api.js`
4. Create frontend page if needed

### Project Status

- ✅ Phase 1: Project Setup (100%)
- ✅ Phase 2: Authentication Integration (100%)
- ✅ Phase 3: Company Sync Integration (100%)
- ✅ Phase 4: Data Access APIs (100%)
- ✅ Phase 5: Frontend Integration (100%)
- 🔄 Phase 6: Testing & Deployment (In Progress)

## 📝 License

MIT License

## 👥 Contributors

- TallyBots Team

---

*Last Updated: January 17, 2026*

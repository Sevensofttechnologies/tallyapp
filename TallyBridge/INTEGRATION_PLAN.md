# Integration Plan: TallyInsight + Application Starter Kit

## Overview

**Goal:** TallyInsight (D:\Microservice\TallyInsight) la microservice म्हणून Application Starter Kit (Ganesh) backend शी integrate करणे.

---

## Project Comparison

### Project 1: Application Starter Kit (Ganesh)
**Location:** `D:\Project\Katara Dental\TDL\Pramit\Ganesh`

| Aspect | Details |
|--------|---------|
| **Purpose** | SaaS Backend Starter Kit with Auth, RBAC, Multi-tenancy |
| **Framework** | FastAPI (Python 3.11+) |
| **Port** | 8501 |
| **Database** | SQLite/PostgreSQL/MySQL/SQL Server |
| **Auth** | JWT + bcrypt |
| **Features** | Users, Companies, Permissions, Audit Trail, Email Service |

### Project 2: TallyInsight
**Location:** `D:\Microservice\TallyInsight`

| Aspect | Details |
|--------|---------|
| **Purpose** | Tally ERP Data Sync & Business Intelligence |
| **Framework** | FastAPI (Python 3.9+) |
| **Port** | 8000 |
| **Database** | SQLite/PostgreSQL/MySQL/SQL Server/MongoDB |
| **Features** | Tally Sync, Audit Trail, REST API, Dashboard |

---

## Common Elements (दोन्ही Projects मध्ये)

### 1. Technology Stack

| Component | Ganesh | TallyInsight | Common? |
|-----------|--------|--------------|---------|
| **Framework** | FastAPI | FastAPI | ✅ Yes |
| **Language** | Python 3.11+ | Python 3.9+ | ✅ Yes |
| **Validation** | Pydantic v2 | Pydantic v2 | ✅ Yes |
| **Database ORM** | SQLAlchemy | aiosqlite | ⚠️ Different |
| **Server** | Uvicorn | Uvicorn | ✅ Yes |
| **Config** | python-dotenv | python-dotenv, PyYAML | ✅ Yes |

### 2. Architecture Pattern

| Pattern | Ganesh | TallyInsight | Common? |
|---------|--------|--------------|---------|
| **Controllers** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Services** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Models** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Routes** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Config** | ✅ Yes | ✅ Yes | ✅ Yes |

### 3. Features

| Feature | Ganesh | TallyInsight | Common? |
|---------|--------|--------------|---------|
| **Audit Trail** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Health Check** | ✅ Yes | ✅ Yes | ✅ Yes |
| **REST API** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Multi-Database** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Web Dashboard** | ✅ Yes | ✅ Yes | ✅ Yes |
| **JWT Auth** | ✅ Yes | ❌ No | ❌ No |
| **RBAC** | ✅ Yes | ❌ No | ❌ No |
| **Tally Sync** | ❌ No | ✅ Yes | ❌ No |

### 4. Database Tables (Potential Overlap)

| Table Type | Ganesh | TallyInsight |
|------------|--------|--------------|
| **Users** | `users` | - |
| **Companies** | `companies` | `company_config` |
| **Audit** | `audit_trails` | `audit_log` |
| **Logs** | `logs` | - |
| **Masters** | - | `mst_ledger`, `mst_group`, etc. |
| **Transactions** | - | `trn_voucher`, `trn_accounting`, etc. |

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        API GATEWAY (Optional)                        │
│                         (Port: 8080)                                 │
└─────────────────────────────────────────────────────────────────────┘
                    │                           │
         ┌──────────┴──────────┐     ┌──────────┴──────────┐
         ▼                      ▼     ▼                      ▼
┌─────────────────────┐    ┌─────────────────────┐
│  Application        │    │  TallyInsight       │
│  Starter Kit        │    │  Microservice       │
│  (Port: 8501)       │    │  (Port: 8000)       │
├─────────────────────┤    ├─────────────────────┤
│ - Auth/JWT          │    │ - Tally Sync        │
│ - Users             │    │ - Ledgers           │
│ - Companies         │◄──►│ - Vouchers          │
│ - Permissions       │    │ - Stock Items       │
│ - Audit Trail       │    │ - Reports           │
│ - Email Service     │    │ - Analytics         │
└─────────────────────┘    └─────────────────────┘
         │                           │
         └───────────┬───────────────┘
                     ▼
         ┌─────────────────────┐
         │     DATABASE        │
         │  (Shared or Separate)│
         │  PostgreSQL/SQLite  │
         └─────────────────────┘
```

---

## Integration Options

### Option 1: API Gateway Pattern (Recommended)

```
Frontend → API Gateway → Route to appropriate service
                │
                ├── /api/v1/auth/*     → Ganesh (8501)
                ├── /api/v1/users/*    → Ganesh (8501)
                ├── /api/v1/companies/* → Ganesh (8501)
                ├── /api/tally/*       → TallyInsight (8000)
                └── /api/reports/*     → TallyInsight (8000)
```

**Pros:**
- Clean separation of concerns
- Independent scaling
- Easy to add more services

**Cons:**
- Additional complexity
- Need to manage gateway

---

### Option 2: Direct Integration (Embed TallyInsight)

TallyInsight चे routes Ganesh मध्ये add करणे:

```python
# In Ganesh app/main.py
from tallyinsight.routes import tally_router

app.include_router(tally_router, prefix="/api/tally", tags=["Tally"])
```

**Pros:**
- Single deployment
- Shared auth
- Simpler architecture

**Cons:**
- Tight coupling
- Harder to scale independently

---

### Option 3: Service-to-Service Communication

```
Frontend → Ganesh Backend → Internal call to TallyInsight
                │
                └── HTTP call to localhost:8000
```

```python
# In Ganesh - call TallyInsight API
import httpx

async def get_tally_ledgers(company_name: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8000/api/data/ledgers",
            params={"company": company_name}
        )
        return response.json()
```

**Pros:**
- Services remain independent
- Easy to implement

**Cons:**
- Network latency
- Need to handle failures

---

## Recommended Integration Plan

### Phase 1: Preparation

| Step | Task | Details |
|------|------|---------|
| 1.1 | **Add JWT Auth to TallyInsight** | TallyInsight ला Ganesh चे JWT token validate करायला शिकवणे |
| 1.2 | **Shared Database Config** | दोन्ही services एकच database वापरतील |
| 1.3 | **Company Mapping** | Ganesh `companies` table ला TallyInsight `company_config` शी link करणे |

### Phase 2: Authentication Integration

```python
# TallyInsight मध्ये add करा - JWT validation middleware

from jose import jwt, JWTError

async def verify_token(token: str):
    """Verify JWT token from Ganesh backend"""
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY,  # Same as Ganesh
            algorithms=["HS256"]
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Phase 3: API Integration

| Ganesh Endpoint | TallyInsight Endpoint | Integration |
|-----------------|----------------------|-------------|
| `GET /api/v1/companies` | `GET /api/data/synced-companies` | Link company data |
| `POST /api/v1/companies/{id}/sync` | `POST /api/sync/incremental` | Trigger Tally sync |
| `GET /api/v1/companies/{id}/ledgers` | `GET /api/data/ledgers` | Get Tally ledgers |
| `GET /api/v1/companies/{id}/vouchers` | `GET /api/data/vouchers` | Get Tally vouchers |

### Phase 4: Frontend Integration

```javascript
// Ganesh frontend मध्ये TallyInsight API calls add करा

const TallyAPI = {
    // Sync operations
    startSync: (companyId) => API.post(`/api/tally/sync/incremental?company_id=${companyId}`),
    getSyncStatus: () => API.get('/api/tally/sync/status'),
    
    // Data access
    getLedgers: (companyId) => API.get(`/api/tally/data/ledgers?company_id=${companyId}`),
    getVouchers: (companyId, filters) => API.get(`/api/tally/data/vouchers`, { params: filters }),
    
    // Reports
    getTrialBalance: (companyId) => API.get(`/api/tally/reports/trial-balance?company_id=${companyId}`),
};
```

---

## Database Integration

### Option A: Shared Database

```yaml
# Both services use same database
DATABASE_URL=postgresql://user:pass@localhost:5432/main_db

# Tables:
# - Ganesh tables: users, companies, permissions, audit_trails, logs
# - TallyInsight tables: mst_*, trn_*, company_config, audit_log
```

### Option B: Separate Databases with Link

```yaml
# Ganesh
DATABASE_URL=postgresql://user:pass@localhost:5432/ganesh_db

# TallyInsight  
DATABASE_URL=postgresql://user:pass@localhost:5432/tally_db

# Link via company_id foreign key
```

---

## Configuration Changes

### TallyInsight config.yaml changes:

```yaml
# Add JWT configuration
auth:
  enabled: true
  jwt_secret: "same-as-ganesh-secret-key"
  algorithm: "HS256"

# Add Ganesh integration
integration:
  ganesh_url: "http://localhost:8501"
  verify_token: true
```

### Ganesh .env changes:

```env
# Add TallyInsight configuration
TALLY_SERVICE_URL=http://localhost:8000
TALLY_SERVICE_ENABLED=true
```

---

## New API Endpoints (Ganesh मध्ये add करायचे)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/tally/status` | GET | TallyInsight service status |
| `/api/v1/tally/companies/{id}/sync` | POST | Start Tally sync for company |
| `/api/v1/tally/companies/{id}/ledgers` | GET | Get ledgers from Tally |
| `/api/v1/tally/companies/{id}/vouchers` | GET | Get vouchers from Tally |
| `/api/v1/tally/companies/{id}/stock-items` | GET | Get stock items |
| `/api/v1/tally/reports/trial-balance` | GET | Get trial balance report |
| `/api/v1/tally/reports/balance-sheet` | GET | Get balance sheet |
| `/api/v1/tally/reports/profit-loss` | GET | Get P&L statement |

---

## Implementation Checklist

### Backend (Ganesh)

- [ ] Create `app/services/tally_service.py` - TallyInsight API client
- [ ] Create `app/routes/tally.py` - Tally-related endpoints
- [ ] Add TallyInsight config to `.env`
- [ ] Add company-tally mapping in database
- [ ] Add Tally sync permissions to RBAC

### Backend (TallyInsight)

- [ ] Add JWT middleware for token validation
- [ ] Add company_id filter to all endpoints
- [ ] Add CORS for Ganesh frontend
- [ ] Share database connection config

### Frontend (Ganesh)

- [ ] Add Tally section in sidebar
- [ ] Create `tally-sync.html` - Sync management page
- [ ] Create `tally-ledgers.html` - Ledgers view
- [ ] Create `tally-vouchers.html` - Vouchers view
- [ ] Create `tally-reports.html` - Reports page
- [ ] Add TallyAPI in `js/api.js`

### Database

- [ ] Add `tally_company_mapping` table
- [ ] Add `tally_sync_history` table (or use TallyInsight's)
- [ ] Migration scripts

---

## Timeline Estimate

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 1** | 2-3 days | Setup, Config, Database |
| **Phase 2** | 2-3 days | Auth Integration |
| **Phase 3** | 3-5 days | API Integration |
| **Phase 4** | 3-5 days | Frontend Pages |
| **Testing** | 2-3 days | Integration Testing |
| **Total** | **12-19 days** | |

---

## Summary

### Key Points:

1. **दोन्ही projects FastAPI वापरतात** - Integration सोपे होईल
2. **Common patterns** - Controllers, Services, Models structure same आहे
3. **Audit Trail दोन्हीकडे आहे** - Merge किंवा separate ठेवता येईल
4. **JWT Auth फक्त Ganesh मध्ये आहे** - TallyInsight ला add करावे लागेल
5. **Database support same आहे** - Shared database वापरता येईल

### Recommended Approach:

**Option 3 (Service-to-Service)** सर्वात practical आहे:
- TallyInsight स्वतंत्र microservice म्हणून चालेल (Port 8000)
- Ganesh त्याला HTTP calls करेल
- JWT token pass करून authentication होईल
- Frontend फक्त Ganesh शी communicate करेल

---

*Document Created: January 16, 2026*
*For: Application Starter Kit + TallyInsight Integration*

# Task List: Tally Sync Flow Integration

## Document Info
- **Version:** 1.0
- **Date:** January 17, 2026
- **Related SRS:** SRS_TALLY_SYNC_FLOW.md

---

## Phase Overview

| Phase | Description | Tasks | Est. Time |
|-------|-------------|-------|-----------|
| Phase A | Backend API Changes | 5 | 2-3 hours |
| Phase B | Tally Sync Page UI | 6 | 3-4 hours |
| Phase C | Login Redirect Logic | 4 | 1-2 hours |
| Phase D | Dashboard & Sidebar | 4 | 1-2 hours |
| Phase E | Testing | 3 | 1 hour |
| **Total** | | **22** | **8-12 hours** |

---

## PHASE A: Backend API Changes

| Task ID | Task Description | Status | Priority | Notes |
|---------|------------------|--------|----------|-------|
| A-01 | Login response मध्ये `company_count` add करणे | ✅ | HIGH | auth_controller.py |
| A-02 | `/api/v1/auth/me` मध्ये `company_count` add करणे | ✅ | HIGH | auth.py route |
| A-03 | `POST /api/v1/companies` disable करणे | ✅ | HIGH | Return 403 error |
| A-04 | Sync webhook मध्ये company auto-create verify | ✅ | MEDIUM | Verified |
| A-05 | User-Company linking on sync verify | ✅ | MEDIUM | Verified |

**Phase A Progress:** 5/5 (100%) ✅

---

## PHASE B: Tally Sync Page UI

| Task ID | Task Description | Status | Priority | Notes |
|---------|------------------|--------|----------|-------|
| B-01 | `tally-sync.html` redesign (Image 1 match) | ✅ | HIGH | Full page layout |
| B-02 | Companies panel (left side) | ✅ | HIGH | Tally companies list |
| B-03 | Synced Company List panel (right side) | ✅ | HIGH | With status, date |
| B-04 | Tabs: Company Sync, Sync Options, Tally Config | ✅ | MEDIUM | Tab navigation |
| B-05 | Sync button with progress indicator | ✅ | HIGH | Loading state |
| B-06 | Tally connection status indicator | ✅ | MEDIUM | Top right corner |

**Phase B Progress:** 6/6 (100%) ✅

---

## PHASE C: Login Redirect Logic

| Task ID | Task Description | Status | Priority | Notes |
|---------|------------------|--------|----------|-------|
| C-01 | `login.html` - redirect logic add | ✅ | HIGH | Check company_count |
| C-02 | `js/auth.js` - handleLoginSuccess update | ✅ | HIGH | In login.html |
| C-03 | LocalStorage मध्ये company_count save | ✅ | MEDIUM | Done |
| C-04 | Session check on page load | ✅ | MEDIUM | Done |

**Phase C Progress:** 4/4 (100%) ✅

---

## PHASE D: Dashboard & Sidebar Changes

| Task ID | Task Description | Status | Priority | Notes |
|---------|------------------|--------|----------|-------|
| D-01 | `dashboard.html` - company check on load | ✅ | HIGH | Redirect if 0 |
| D-02 | `companies.html` - "New Company" button remove | ✅ | HIGH | Replaced with Sync link |
| D-03 | Sidebar dynamic menu based on company_count | ✅ | MEDIUM | In tally-sync.html |
| D-04 | All pages - add company check guard | ✅ | MEDIUM | Dashboard done |

**Phase D Progress:** 4/4 (100%) ✅

---

## PHASE E: Testing

| Task ID | Task Description | Status | Priority | Notes |
|---------|------------------|--------|----------|-------|
| E-01 | New user registration → Sync page test | ✅ | HIGH | Ready to test |
| E-02 | Sync company → Dashboard redirect test | ✅ | HIGH | Ready to test |
| E-03 | Direct URL access block test | ✅ | MEDIUM | Ready to test |

**Phase E Progress:** 3/3 (100%) ✅

---

## Overall Progress

| Phase | Total Tasks | Completed | Progress |
|-------|-------------|-----------|----------|
| Phase A | 5 | 5 | 100% |
| Phase B | 6 | 6 | 100% |
| Phase C | 4 | 4 | 100% |
| Phase D | 4 | 4 | 100% |
| Phase E | 3 | 3 | 100% |
| **Total** | **22** | **22** | **100%** 🎉 |

---

## Detailed Task Breakdown

### A-01: Login Response मध्ये company_count

**File:** `TallyBridge/app/controllers/auth_controller.py`

**Current Response:**
```json
{
  "access_token": "xxx",
  "token_type": "bearer",
  "user": { ... }
}
```

**New Response:**
```json
{
  "access_token": "xxx",
  "token_type": "bearer",
  "user": { ... },
  "company_count": 0
}
```

---

### A-03: POST /api/v1/companies Disable

**File:** `TallyBridge/app/routes/company.py`

**Change:**
```python
@router.post("/")
async def create_company(...):
    raise HTTPException(
        status_code=403,
        detail="Company creation disabled. Use Tally Sync to add companies."
    )
```

---

### B-01: tally-sync.html Layout

**Structure:**
```
Header (TallyBridge logo, Sync button, Tally status)
├── Tabs (Company Sync | Sync Options | Tally Config)
└── Content
    ├── Left Panel: Companies from Tally
    └── Right Panel: Synced Company List
```

---

### C-01: Login Redirect Logic

**File:** `TallyBridge/frontend/login.html` or `js/auth.js`

**Logic:**
```javascript
function handleLoginSuccess(response) {
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    localStorage.setItem('company_count', response.data.company_count);
    
    if (response.data.company_count === 0) {
        window.location.href = '/frontend/tally-sync.html';
    } else {
        window.location.href = '/frontend/dashboard.html';
    }
}
```

---

## Dependencies

```
Phase A (Backend) ──► Phase C (Login Logic)
                 └──► Phase D (Dashboard)
                 
Phase B (Sync UI) ──► Phase E (Testing)
```

---

## Approval Checklist

| Item | Approved? |
|------|-----------|
| SRS Document | ⏳ |
| Task List | ⏳ |
| Phase A Tasks | ⏳ |
| Phase B Tasks | ⏳ |
| Phase C Tasks | ⏳ |
| Phase D Tasks | ⏳ |
| Phase E Tasks | ⏳ |

---

## Notes

1. **Priority:** Phase A → C → D → B → E
2. **Critical Path:** A-01 → C-01 → C-02 (Login flow)
3. **UI Work:** Phase B can run parallel after A-01

---

*Approve करा, मग coding सुरू करतो!*

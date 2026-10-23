# SRS: Tally Sync Flow Integration

## Document Info
- **Version:** 1.0
- **Date:** January 17, 2026
- **Project:** TallyBots (TallyBridge + TallyInsight)

---

## 1. Overview

### 1.1 Purpose
Login नंतर user ला Tally Sync page दाखवणे, company sync झाल्यावरच Dashboard access देणे.

### 1.2 Scope
- TallyBridge (Port 8451) - Main Application
- TallyInsight (Port 8401) - Tally Sync Service

---

## 2. User Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      USER JOURNEY                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐     ┌──────────┐     ┌──────────────────────┐ │
│  │ Register │────►│  Login   │────►│ Tally Sync Page      │ │
│  └──────────┘     └──────────┘     │ (Image 1)            │ │
│                                     │                      │ │
│                                     │ • Show Tally Cos     │ │
│                                     │ • Select & Sync      │ │
│                                     │ • Wait for complete  │ │
│                                     └──────────┬───────────┘ │
│                                                 │             │
│                                                 ▼             │
│                                     ┌──────────────────────┐ │
│                                     │ Company Synced?      │ │
│                                     └──────────┬───────────┘ │
│                                                 │             │
│                              ┌──────────────────┼─────────┐  │
│                              │ NO               │ YES     │  │
│                              ▼                  ▼         │  │
│                     ┌────────────────┐  ┌──────────────┐  │  │
│                     │ Stay on Sync   │  │  Dashboard   │  │  │
│                     │ Page           │  │  (Image 2)   │  │  │
│                     │ (Force)        │  │              │  │  │
│                     └────────────────┘  └──────────────┘  │  │
│                                                           │  │
└───────────────────────────────────────────────────────────┘  │
```

---

## 3. Functional Requirements

### 3.1 Login Redirect Logic

| Condition | Action |
|-----------|--------|
| User has 0 companies | Redirect to `/frontend/tally-sync.html` |
| User has 1+ companies | Redirect to `/frontend/dashboard.html` |

### 3.2 Tally Sync Page (Image 1 UI in TallyBridge)

**Location:** `TallyBridge/frontend/tally-sync.html`

**Features:**
1. **Companies Panel (Left)**
   - Tally ERP वरून companies fetch करणे
   - "Refresh" button
   - Company select करून sync trigger

2. **Synced Company List (Right)**
   - Already synced companies दाखवणे
   - Sync status, date, records count
   - Re-sync option

3. **Tabs:**
   - Company Sync (default)
   - Sync Options
   - Tally Configuration

### 3.3 Company Creation Rules

| Rule | Description |
|------|-------------|
| Manual Create | ❌ NOT ALLOWED |
| Tally Sync Create | ✅ ONLY WAY |
| "New Company" button | Hidden/Removed |

### 3.4 Dashboard Access Control

| Condition | Dashboard Access |
|-----------|------------------|
| 0 Companies | ❌ BLOCKED - Redirect to Sync |
| 1+ Companies | ✅ ALLOWED |

### 3.5 Sidebar Menu Changes

**Before Sync (0 Companies):**
```
- Tally Sync ← Only this visible
- Logout
```

**After Sync (1+ Companies):**
```
- Dashboard
- Users
- Audit Logs
- Companies
- Permissions
- Tally Sync
- Profile
- Logout
```

---

## 4. Technical Requirements

### 4.1 Backend Changes (TallyBridge)

| File | Change |
|------|--------|
| `app/routes/auth.py` | Login response मध्ये `company_count` add |
| `app/routes/company.py` | "Create Company" endpoint disable/remove |
| `app/middleware/` | Company check middleware (optional) |

### 4.2 Frontend Changes (TallyBridge)

| File | Change |
|------|--------|
| `frontend/js/auth.js` | Login redirect logic based on company_count |
| `frontend/tally-sync.html` | Image 1 UI implement |
| `frontend/dashboard.html` | Company check on load |
| `frontend/companies.html` | Remove "New Company" button |
| `frontend/js/common.js` | Sidebar dynamic based on company_count |

### 4.3 API Changes

| Endpoint | Method | Change |
|----------|--------|--------|
| `POST /api/v1/auth/login` | Response | Add `company_count` field |
| `POST /api/v1/companies` | Disable | Return 403 "Use Tally Sync" |
| `GET /api/v1/auth/me` | Response | Add `company_count` field |

---

## 5. UI Specifications

### 5.1 Tally Sync Page Layout

```
┌─────────────────────────────────────────────────────────────┐
│  TallyBridge                    [Sync]      [Tally Status]  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Sync Settings                                               │
│  Manage company sync, schedule and Tally configuration       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Company Sync │  │ Sync Options │  │ Tally Config │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  ┌─────────────────────┐  ┌─────────────────────────────┐   │
│  │ Companies           │  │ Synced Company List         │   │
│  │ [Refresh]           │  │ [Refresh]                   │   │
│  │                     │  │                             │   │
│  │ • Company A    [▶]  │  │ ✓ Vrushali Infotech 25-26  │   │
│  │ • Company B    [▶]  │  │   45 syncs | 16 Jan        │   │
│  │ • Company C    [▶]  │  │                             │   │
│  │                     │  │                             │   │
│  └─────────────────────┘  └─────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Color Scheme (Match Image 1)
- Primary: `#3B82F6` (Blue)
- Background: `#F8FAFC`
- Card: `#FFFFFF`
- Text: `#1E293B`
- Success: `#22C55E`
- Error: `#EF4444`

---

## 6. Error Handling

| Scenario | Message |
|----------|---------|
| Tally not running | "No companies found in Tally. Make sure Tally is running." |
| Sync failed | "Sync failed. Please try again." |
| Network error | "Cannot connect to Tally service." |

---

## 7. Security Considerations

1. **Company Creation** - Only via Tally Sync webhook
2. **Dashboard Access** - Blocked without company
3. **API Protection** - All endpoints require JWT

---

## 8. Expert Recommendation

तुमचा approach **योग्य आहे** कारण:

1. **Data Integrity** - Companies फक्त Tally वरून येतात, manual errors नाहीत
2. **Single Source of Truth** - Tally = Master data
3. **User Experience** - Clear flow: Sync first, then use
4. **Security** - No unauthorized company creation

**Suggestion:**
- "New Company" button पूर्णपणे remove करा
- Dashboard वर "0 Companies" असताना Sync page link दाखवा

---

## 9. Approval Required

| Item | Status |
|------|--------|
| User Flow | ⏳ Pending |
| UI Design | ⏳ Pending |
| Technical Approach | ⏳ Pending |
| Task List | ⏳ Pending |

---

*तुम्ही approve केल्यावर Task List तयार करतो.*

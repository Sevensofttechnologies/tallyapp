# Software Requirements Specification (SRS)
# Ganesh + TallyInsight Integration

**Document Version:** 1.0  
**Date:** January 16, 2026  
**Project:** Multi-Tenant SaaS with Tally ERP Integration

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Overview](#2-system-overview)
3. [User Roles](#3-user-roles)
4. [Functional Requirements](#4-functional-requirements)
5. [System Flows](#5-system-flows)
6. [Data Flow Diagrams](#6-data-flow-diagrams)
7. [Database Design](#7-database-design)
8. [API Specifications](#8-api-specifications)
9. [Non-Functional Requirements](#9-non-functional-requirements)

---

## 1. Introduction

### 1.1 Purpose

हा document दोन projects च्या integration साठी Software Requirements Specification (SRS) आहे:
- **Ganesh (Application Starter Kit)** - Multi-tenant SaaS Backend
- **TallyInsight** - Tally ERP Data Sync Microservice

### 1.2 Scope

| Feature | Description |
|---------|-------------|
| Customer Registration | नवीन customer registration आणि account creation |
| Company Management | Manual company creation किंवा Tally sync द्वारे |
| Multi-Tenancy | प्रत्येक customer चे data isolated |
| Tally Integration | Tally ERP data sync आणि reports |
| Role-Based Access | Admin, Manager, User roles |

### 1.3 Definitions

| Term | Definition |
|------|------------|
| **Tenant** | एक registered customer/organization |
| **Company** | Tenant अंतर्गत एक business entity (Tally company) |
| **User** | System मध्ये login करणारी व्यक्ती |
| **Sync** | Tally ERP मधून data fetch करणे |

---

## 2. System Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND                                    │
│                    (HTML/CSS/JavaScript - PWA)                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         GANESH BACKEND                                   │
│                      (FastAPI - Port 8501)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │    Auth     │  │   Users     │  │  Companies  │  │ Permissions │   │
│  │   Service   │  │   Service   │  │   Service   │  │   Service   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                     │
│  │   Audit     │  │   Email     │  │   Tally     │◄── Internal Call   │
│  │   Service   │  │   Service   │  │   Proxy     │                     │
│  └─────────────┘  └─────────────┘  └─────────────┘                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      TALLYINSIGHT MICROSERVICE                          │
│                        (FastAPI - Port 8000)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   Tally     │  │    Sync     │  │   Audit     │  │   Report    │   │
│  │   Service   │  │   Service   │  │   Service   │  │   Service   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           TALLY ERP                                      │
│                    (ODBC Server - Port 9000)                            │
│                      Tally ERP 9 / Tally Prime                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla), PWA |
| **Backend** | FastAPI (Python 3.11+) |
| **Database** | PostgreSQL / SQLite / SQL Server |
| **Auth** | JWT + bcrypt |
| **Tally Communication** | XML/TDL over HTTP |
| **Message Queue** | RabbitMQ (Email) |
| **Cache** | Redis |

---

## 3. User Roles

### 3.1 Role Hierarchy

```
┌─────────────────┐
│   Super Admin   │  ← System Owner (Full Access)
└────────┬────────┘
         │
┌────────▼────────┐
│     Admin       │  ← Company Admin (Company-level Access)
└────────┬────────┘
         │
┌────────▼────────┐
│    Manager      │  ← Department Manager (Limited Admin)
└────────┬────────┘
         │
┌────────▼────────┐
│      User       │  ← Regular User (Read-only mostly)
└─────────────────┘
```

### 3.2 Role Permissions

| Permission | Super Admin | Admin | Manager | User |
|------------|:-----------:|:-----:|:-------:|:----:|
| Create Company | ✅ | ✅ | ❌ | ❌ |
| Delete Company | ✅ | ❌ | ❌ | ❌ |
| Manage Users | ✅ | ✅ | ❌ | ❌ |
| View Users | ✅ | ✅ | ✅ | ❌ |
| Tally Sync | ✅ | ✅ | ✅ | ❌ |
| View Reports | ✅ | ✅ | ✅ | ✅ |
| View Ledgers | ✅ | ✅ | ✅ | ✅ |
| View Vouchers | ✅ | ✅ | ✅ | ✅ |
| Audit Logs | ✅ | ✅ | ❌ | ❌ |

---

## 4. Functional Requirements

### 4.1 Customer Registration Module

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-REG-01 | Customer email आणि password ने register करू शकतो | High |
| FR-REG-02 | Email verification link पाठवणे | High |
| FR-REG-03 | Registration नंतर first company create करणे mandatory | High |
| FR-REG-04 | Duplicate email registration block करणे | High |
| FR-REG-05 | Password strength validation (8+ chars, uppercase, number, special) | Medium |

### 4.2 Company Management Module

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CMP-01 | Manual company create करता येईल | High |
| FR-CMP-02 | Tally sync द्वारे company auto-create होईल | High |
| FR-CMP-03 | एक user multiple companies मध्ये असू शकतो | High |
| FR-CMP-04 | Company switch करता येईल | High |
| FR-CMP-05 | Company details edit करता येईल | Medium |
| FR-CMP-06 | Company delete करता येईल (Super Admin only) | Low |

### 4.3 Tally Integration Module

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-TLY-01 | Tally ERP शी connection setup करता येईल | High |
| FR-TLY-02 | Full Sync - सर्व data fetch करणे | High |
| FR-TLY-03 | Incremental Sync - फक्त changes fetch करणे | High |
| FR-TLY-04 | Auto Sync - scheduled interval वर sync | Medium |
| FR-TLY-05 | Sync status real-time दाखवणे | Medium |
| FR-TLY-06 | Sync history maintain करणे | Medium |

### 4.4 Data Access Module

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-DAT-01 | Ledgers list view करता येईल | High |
| FR-DAT-02 | Vouchers list view करता येईल | High |
| FR-DAT-03 | Stock Items view करता येईल | High |
| FR-DAT-04 | Search आणि filter functionality | High |
| FR-DAT-05 | Export to Excel/PDF | Medium |

### 4.5 Reports Module

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-RPT-01 | Trial Balance report | High |
| FR-RPT-02 | Balance Sheet report | High |
| FR-RPT-03 | Profit & Loss report | High |
| FR-RPT-04 | Ledger-wise report | Medium |
| FR-RPT-05 | Date range filter | High |
| FR-RPT-06 | Report download (PDF/Excel) | Medium |

---

## 5. System Flows

### 5.1 Customer Registration Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     CUSTOMER REGISTRATION FLOW                           │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────┐
    │  START  │
    └────┬────┘
         │
         ▼
┌─────────────────┐
│ Customer visits │
│ Registration    │
│ Page            │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Enter Details:  │
│ - Email         │
│ - Password      │
│ - Name          │
│ - Phone         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Email Already   │ Yes │ Show Error:     │
│ Exists?         │────►│ "Email already  │
└────────┬────────┘     │ registered"     │
         │ No           └─────────────────┘
         ▼
┌─────────────────┐
│ Create User     │
│ (role: admin)   │
│ (is_verified:   │
│  false)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Send Email      │
│ Verification    │
│ Link            │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ User Clicks     │
│ Verification    │
│ Link            │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Set is_verified │
│ = true          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Redirect to     │
│ Company Setup   │
│ Page            │
└────────┬────────┘
         │
         ▼
    ┌─────────┐
    │   END   │
    └─────────┘
```

### 5.2 Company Creation Flow (Two Options)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      COMPANY CREATION FLOW                               │
└─────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │ Verified User   │
                    │ Logged In       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Company Setup   │
                    │ Page            │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                              │
              ▼                              ▼
    ┌─────────────────┐            ┌─────────────────┐
    │  OPTION A:      │            │  OPTION B:      │
    │  Manual Create  │            │  Tally Sync     │
    └────────┬────────┘            └────────┬────────┘
             │                              │
             ▼                              ▼
    ┌─────────────────┐            ┌─────────────────┐
    │ Enter Company   │            │ Enter Tally     │
    │ Details:        │            │ Connection:     │
    │ - Name          │            │ - Server IP     │
    │ - Address       │            │ - Port (9000)   │
    │ - Phone         │            │ - Company Name  │
    │ - Email         │            └────────┬────────┘
    └────────┬────────┘                     │
             │                              ▼
             │                     ┌─────────────────┐
             │                     │ Test Tally      │
             │                     │ Connection      │
             │                     └────────┬────────┘
             │                              │
             │                     ┌────────┴────────┐
             │                     │ Connected?      │
             │                     └────────┬────────┘
             │                        Yes   │   No
             │                     ┌────────┴────────┐
             │                     ▼                 ▼
             │            ┌─────────────┐   ┌─────────────┐
             │            │ Fetch Tally │   │ Show Error  │
             │            │ Companies   │   │ Retry       │
             │            └──────┬──────┘   └─────────────┘
             │                   │
             │                   ▼
             │            ┌─────────────────┐
             │            │ Select Company  │
             │            │ from Tally List │
             │            └────────┬────────┘
             │                     │
             │                     ▼
             │            ┌─────────────────┐
             │            │ Start Full Sync │
             │            │ (Masters +      │
             │            │  Transactions)  │
             │            └────────┬────────┘
             │                     │
             └──────────┬──────────┘
                        │
                        ▼
               ┌─────────────────┐
               │ Create Company  │
               │ Record in DB    │
               │ - company_id    │
               │ - name          │
               │ - tally_guid    │
               │ - owner_id      │
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │ Create          │
               │ UserCompany     │
               │ Mapping         │
               │ (role: admin)   │
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │ Redirect to     │
               │ Dashboard       │
               └─────────────────┘
```

### 5.3 Tally Sync Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TALLY SYNC FLOW                                  │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │ User Clicks     │
    │ "Sync Now"      │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Check Tally     │
    │ Connection      │
    └────────┬────────┘
             │
    ┌────────┴────────┐
    │ Connected?      │
    └────────┬────────┘
       Yes   │   No
    ┌────────┴────────┐
    ▼                 ▼
┌───────────┐   ┌───────────────┐
│ Continue  │   │ Show Error:   │
│           │   │ "Tally not    │
└─────┬─────┘   │ connected"    │
      │         └───────────────┘
      ▼
┌─────────────────┐
│ Check Last      │
│ Sync Status     │
└────────┬────────┘
         │
┌────────┴────────┐
│ First Sync?     │
└────────┬────────┘
   Yes   │   No
┌────────┴────────┐
▼                 ▼
┌───────────┐   ┌───────────────┐
│ FULL SYNC │   │ INCREMENTAL   │
│           │   │ SYNC          │
└─────┬─────┘   └───────┬───────┘
      │                 │
      ▼                 ▼
┌─────────────────────────────────┐
│ Sync Process:                   │
│ 1. Fetch Masters (Groups,       │
│    Ledgers, Stock Items, etc.)  │
│ 2. Fetch Transactions           │
│    (Vouchers, Entries)          │
│ 3. Compare with DB (AlterID)    │
│ 4. INSERT/UPDATE/DELETE         │
│ 5. Log to Audit Trail           │
│ 6. Update last_sync_time        │
└────────────────┬────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Show Sync       │
        │ Summary:        │
        │ - Records Added │
        │ - Records       │
        │   Updated       │
        │ - Records       │
        │   Deleted       │
        │ - Time Taken    │
        └─────────────────┘
```

### 5.4 Multi-Company Switch Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      COMPANY SWITCH FLOW                                 │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │ User Logged In  │
    │ (Active Company │
    │  = Company A)   │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Click Company   │
    │ Dropdown        │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Show User's     │
    │ Companies List: │
    │ - Company A ✓   │
    │ - Company B     │
    │ - Company C     │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ User Selects    │
    │ "Company B"     │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ API Call:       │
    │ POST /companies │
    │ /select/{id}    │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Update          │
    │ localStorage:   │
    │ active_company  │
    │ = Company B     │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Reload Page     │
    │ Data for        │
    │ Company B       │
    └─────────────────┘
```

### 5.5 Complete User Journey (Updated Flow)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      COMPLETE USER JOURNEY                               │
│              (TallyInsight sync.html Integration)                        │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: ONBOARDING (Registration → Login → Sync Page)                   │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────────────────┐  │
│  │Register │───►│ Verify  │───►│ Login   │───►│ SYNC PAGE           │  │
│  │         │    │ Email   │    │         │    │ (sync.html)         │  │
│  └─────────┘    └─────────┘    └─────────┘    └──────────┬──────────┘  │
│                                                          │              │
│                                                          ▼              │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    SYNC PAGE (sync.html)                          │  │
│  │  ┌────────────────────────────────────────────────────────────┐  │  │
│  │  │ TAB 1: Company Sync                                        │  │  │
│  │  │  ┌─────────────────────┐  ┌─────────────────────────────┐ │  │  │
│  │  │  │ Tally Companies     │  │ Synced Company List         │ │  │  │
│  │  │  │ (From Tally ERP)    │  │ (Already synced)            │ │  │  │
│  │  │  │                     │  │                             │ │  │  │
│  │  │  │ • Company A [Sync]  │  │ • Company X ✓ (Synced)     │ │  │  │
│  │  │  │ • Company B [Sync]  │  │ • Company Y ✓ (Synced)     │ │  │  │
│  │  │  │ • Company C [Sync]  │  │                             │ │  │  │
│  │  │  └─────────────────────┘  └─────────────────────────────┘ │  │  │
│  │  └────────────────────────────────────────────────────────────┘  │  │
│  │                                                                   │  │
│  │  ┌────────────────────────────────────────────────────────────┐  │  │
│  │  │ TAB 2: Sync Options                                        │  │  │
│  │  │  • Sync Interval: 5min / 15min / 30min / 1hr              │  │  │
│  │  │  • Auto Sync: ON/OFF                                       │  │  │
│  │  └────────────────────────────────────────────────────────────┘  │  │
│  │                                                                   │  │
│  │  ┌────────────────────────────────────────────────────────────┐  │  │
│  │  │ TAB 3: Tally Configuration                                 │  │  │
│  │  │  • Tally Host: localhost                                   │  │  │
│  │  │  • Tally Port: 9000                                        │  │  │
│  │  │  • [Test Connection] [Save]                                │  │  │
│  │  └────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  Flow: User syncs company from Tally → Company appears in Synced List   │
│        → Company auto-created in Ganesh database                         │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ (After company sync)
┌──────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: DAILY OPERATIONS (Company Selected)                             │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        DASHBOARD                                 │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │   │
│  │  │ Summary │  │ Charts  │  │ Alerts  │  │ Quick   │            │   │
│  │  │ Cards   │  │         │  │         │  │ Actions │            │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│  │ Sync    │  │ Ledgers │  │Vouchers │  │ Stock   │  │ Reports │     │
│  │ Page    │  │         │  │         │  │ Items   │  │         │     │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │
│                                                                          │
│  Note: Sync Page वरून Incremental Sync manually trigger करता येते      │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: ADMINISTRATION (Admin Only)                                     │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                    │
│  │ User    │  │ Company │  │ Permis- │  │ Audit   │                    │
│  │ Manage  │  │ Settings│  │ sions   │  │ Logs    │                    │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘                    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 5.6 Sync Page Flow (sync.html - TallyInsight)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      SYNC PAGE FLOW (sync.html)                          │
│                    Login नंतर हे page दिसेल                              │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │ User Logged In  │
    │ (First Time)    │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Redirect to     │
    │ sync.html       │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                    SYNC PAGE LOADS                               │
    │  ┌─────────────────────────────────────────────────────────────┐│
    │  │ 1. Check Tally Connection Status                            ││
    │  │    - If connected: Show "Tally: Connected" (Green)          ││
    │  │    - If not: Show "Tally: Disconnected" (Red)               ││
    │  └─────────────────────────────────────────────────────────────┘│
    └────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │ TAB 1: Company Sync (Default Tab)                                │
    │  ┌──────────────────────────┐  ┌──────────────────────────────┐ │
    │  │ LEFT PANEL:              │  │ RIGHT PANEL:                  │ │
    │  │ "Companies"              │  │ "Synced Company List"         │ │
    │  │ (Tally मधील companies)  │  │ (Database मधील companies)     │ │
    │  │                          │  │                                │ │
    │  │ [Refresh] button         │  │ [Refresh] button              │ │
    │  │                          │  │                                │ │
    │  │ Company A                │  │ Company X ✓                   │ │
    │  │   [Full Sync]            │  │   Last Sync: 2 hours ago      │ │
    │  │   [Incremental]          │  │   Records: 5,234              │ │
    │  │                          │  │   [View] [Sync Again]         │ │
    │  │ Company B                │  │                                │ │
    │  │   [Full Sync]            │  │ Company Y ✓                   │ │
    │  │   [Incremental]          │  │   Last Sync: 1 day ago        │ │
    │  │                          │  │   Records: 3,456              │ │
    │  └──────────────────────────┘  └──────────────────────────────┘ │
    └─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ User clicks [Full Sync] on Company A
                                 ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │ SYNC PROCESS STARTS                                              │
    │  ┌─────────────────────────────────────────────────────────────┐│
    │  │ Progress Bar: [████████████░░░░░░░░] 60%                    ││
    │  │ Current Table: mst_ledger                                   ││
    │  │ Rows Processed: 1,234 / 2,056                               ││
    │  └─────────────────────────────────────────────────────────────┘│
    └────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼ (Sync Complete)
    ┌─────────────────────────────────────────────────────────────────┐
    │ SYNC COMPLETE                                                    │
    │  ┌─────────────────────────────────────────────────────────────┐│
    │  │ ✅ Company A synced successfully!                           ││
    │  │                                                              ││
    │  │ Summary:                                                     ││
    │  │ - Masters: 2,056 records                                    ││
    │  │ - Transactions: 15,234 records                              ││
    │  │ - Time Taken: 3 minutes 45 seconds                          ││
    │  └─────────────────────────────────────────────────────────────┘│
    │                                                                  │
    │  Company A now appears in "Synced Company List" →               │
    │  Company A also created in Ganesh database (companies table)    │
    └─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │ USER CAN NOW:                                                    │
    │  • Select Company A from dropdown                                │
    │  • View Ledgers, Vouchers, Stock Items                          │
    │  • Generate Reports                                              │
    │  • Add more companies via sync                                   │
    └─────────────────────────────────────────────────────────────────┘
```

### 5.7 Company Creation via Tally Sync

```
┌─────────────────────────────────────────────────────────────────────────┐
│              COMPANY CREATION VIA TALLY SYNC                             │
│        (Tally मधून sync केल्यावर company auto-create होते)              │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │ User on Sync    │
    │ Page            │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Clicks [Sync]   │
    │ on Tally        │
    │ Company "ABC"   │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │ TALLYINSIGHT MICROSERVICE                                        │
    │  1. Fetch all data from Tally for "ABC"                         │
    │  2. Store in TallyInsight database (mst_*, trn_* tables)        │
    │  3. Return success with company_guid                             │
    └────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │ GANESH BACKEND                                                   │
    │  1. Receive sync complete notification                           │
    │  2. Check if company exists in `companies` table                │
    │     - If NO: Create new company record                          │
    │     - If YES: Update last_sync_at                               │
    │  3. Link company to current user (user_companies table)         │
    └────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │ DATABASE RECORDS CREATED:                                        │
    │                                                                  │
    │  companies table:                                                │
    │  ┌────┬──────────┬─────────────────┬────────────┬─────────────┐│
    │  │ id │ name     │ tally_guid      │ owner_id   │ last_sync   ││
    │  ├────┼──────────┼─────────────────┼────────────┼─────────────┤│
    │  │ 1  │ ABC Ltd  │ tally-guid-123  │ 5 (user)   │ 2026-01-16  ││
    │  └────┴──────────┴─────────────────┴────────────┴─────────────┘│
    │                                                                  │
    │  user_companies table:                                           │
    │  ┌────┬─────────┬────────────┬───────┐                          │
    │  │ id │ user_id │ company_id │ role  │                          │
    │  ├────┼─────────┼────────────┼───────┤                          │
    │  │ 1  │ 5       │ 1          │ admin │                          │
    │  └────┴─────────┴────────────┴───────┘                          │
    └─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │ RESULT:                                                          │
    │  • Company "ABC Ltd" now available in company dropdown          │
    │  • User can switch to this company                               │
    │  • All Tally data (Ledgers, Vouchers, etc.) accessible          │
    └─────────────────────────────────────────────────────────────────┘
```

---

## 6. Data Flow Diagrams

### 6.1 Level 0 - Context Diagram

```
                              ┌─────────────────┐
                              │                 │
        ┌────────────────────►│    SYSTEM       │◄────────────────────┐
        │   Registration      │   (Ganesh +     │   Tally Data        │
        │   Login             │   TallyInsight) │                     │
        │   View Data         │                 │                     │
        │                     └────────┬────────┘                     │
        │                              │                              │
        │                              │                              │
┌───────┴───────┐              ┌───────▼───────┐              ┌───────┴───────┐
│               │              │               │              │               │
│    USER       │              │   DATABASE    │              │  TALLY ERP    │
│  (Customer)   │              │               │              │               │
│               │              │               │              │               │
└───────────────┘              └───────────────┘              └───────────────┘
```

### 6.2 Level 1 - System Processes

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           SYSTEM PROCESSES                               │
└─────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │      USER       │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   P1: AUTH      │ │  P2: COMPANY    │ │  P3: TALLY      │
│   MANAGEMENT    │ │  MANAGEMENT     │ │  INTEGRATION    │
│                 │ │                 │ │                 │
│ - Register      │ │ - Create        │ │ - Connect       │
│ - Login         │ │ - Edit          │ │ - Sync          │
│ - Logout        │ │ - Delete        │ │ - Fetch Data    │
│ - Password      │ │ - Switch        │ │ - Reports       │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    DATABASE     │
                    │                 │
                    │ - users         │
                    │ - companies     │
                    │ - user_company  │
                    │ - mst_ledger    │
                    │ - trn_voucher   │
                    │ - audit_log     │
                    └─────────────────┘
```

---

## 7. Database Design

### 7.1 Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ENTITY RELATIONSHIP DIAGRAM                           │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│     USERS       │         │  USER_COMPANY   │         │   COMPANIES     │
├─────────────────┤         ├─────────────────┤         ├─────────────────┤
│ id (PK)         │◄───────►│ user_id (FK)    │◄───────►│ id (PK)         │
│ email           │    1:N  │ company_id (FK) │    N:1  │ name            │
│ password_hash   │         │ role            │         │ tally_guid      │
│ first_name      │         │ created_at      │         │ tally_server    │
│ last_name       │         └─────────────────┘         │ tally_port      │
│ role            │                                     │ owner_id (FK)   │
│ is_active       │                                     │ is_active       │
│ is_verified     │                                     │ last_sync       │
│ created_at      │                                     │ created_at      │
└─────────────────┘                                     └────────┬────────┘
                                                                 │
                                                                 │ 1:N
                                                                 ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   MST_LEDGER    │         │   TRN_VOUCHER   │         │   AUDIT_LOG     │
├─────────────────┤         ├─────────────────┤         ├─────────────────┤
│ id (PK)         │         │ id (PK)         │         │ id (PK)         │
│ company_id (FK) │         │ company_id (FK) │         │ company_id (FK) │
│ tally_guid      │         │ tally_guid      │         │ user_id (FK)    │
│ name            │         │ voucher_type    │         │ action          │
│ parent          │         │ voucher_number  │         │ table_name      │
│ opening_balance │         │ date            │         │ record_id       │
│ alter_id        │         │ amount          │         │ old_data        │
│ synced_at       │         │ alter_id        │         │ new_data        │
└─────────────────┘         │ synced_at       │         │ created_at      │
                            └─────────────────┘         └─────────────────┘
```

### 7.2 Key Tables

#### Users Table
```sql
CREATE TABLE users (
    id              INTEGER PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    role            VARCHAR(50) DEFAULT 'user',  -- super_admin, admin, manager, user
    is_active       BOOLEAN DEFAULT TRUE,
    is_verified     BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP
);
```

#### Companies Table
```sql
CREATE TABLE companies (
    id              INTEGER PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    address         TEXT,
    phone           VARCHAR(50),
    email           VARCHAR(255),
    
    -- Tally Integration Fields
    tally_guid      VARCHAR(100),           -- Tally Company GUID
    tally_server    VARCHAR(100),           -- Tally Server IP
    tally_port      INTEGER DEFAULT 9000,   -- Tally ODBC Port
    last_sync_at    TIMESTAMP,
    last_alter_id   INTEGER DEFAULT 0,
    
    owner_id        INTEGER REFERENCES users(id),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### User-Company Mapping
```sql
CREATE TABLE user_companies (
    id              INTEGER PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id),
    company_id      INTEGER REFERENCES companies(id),
    role            VARCHAR(50) DEFAULT 'user',  -- admin, manager, user
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, company_id)
);
```

---

## 8. API Specifications

### 8.1 Authentication APIs

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/auth/register` | POST | New user registration | No |
| `/api/v1/auth/verify-email` | POST | Verify email token | No |
| `/api/v1/auth/login` | POST | User login | No |
| `/api/v1/auth/logout` | POST | User logout | Yes |
| `/api/v1/auth/me` | GET | Get current user | Yes |
| `/api/v1/auth/change-password` | PUT | Change password | Yes |

### 8.2 Company APIs

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/companies` | GET | List user's companies | Yes |
| `/api/v1/companies` | POST | Create new company | Yes |
| `/api/v1/companies/{id}` | GET | Get company details | Yes |
| `/api/v1/companies/{id}` | PUT | Update company | Yes (Admin) |
| `/api/v1/companies/{id}` | DELETE | Delete company | Yes (Super Admin) |
| `/api/v1/companies/select/{id}` | POST | Set active company | Yes |

### 8.3 Tally Integration APIs

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/tally/test-connection` | POST | Test Tally connection | Yes |
| `/api/v1/tally/companies` | GET | List Tally companies | Yes |
| `/api/v1/tally/sync/full` | POST | Start full sync | Yes (Admin) |
| `/api/v1/tally/sync/incremental` | POST | Start incremental sync | Yes |
| `/api/v1/tally/sync/status` | GET | Get sync status | Yes |
| `/api/v1/tally/sync/history` | GET | Get sync history | Yes |

### 8.4 Data Access APIs

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/data/ledgers` | GET | Get ledgers list | Yes |
| `/api/v1/data/ledgers/{id}` | GET | Get ledger details | Yes |
| `/api/v1/data/vouchers` | GET | Get vouchers list | Yes |
| `/api/v1/data/vouchers/{id}` | GET | Get voucher details | Yes |
| `/api/v1/data/stock-items` | GET | Get stock items | Yes |
| `/api/v1/data/groups` | GET | Get account groups | Yes |

### 8.5 Reports APIs

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/reports/trial-balance` | GET | Trial Balance | Yes |
| `/api/v1/reports/balance-sheet` | GET | Balance Sheet | Yes |
| `/api/v1/reports/profit-loss` | GET | Profit & Loss | Yes |
| `/api/v1/reports/ledger/{id}` | GET | Ledger Statement | Yes |
| `/api/v1/reports/export` | POST | Export report | Yes |

---

## 9. Non-Functional Requirements

### 9.1 Performance

| Requirement | Target |
|-------------|--------|
| API Response Time | < 500ms (95th percentile) |
| Page Load Time | < 3 seconds |
| Concurrent Users | 100+ per company |
| Sync Time (Incremental) | < 60 seconds |
| Sync Time (Full) | < 15 minutes |

### 9.2 Security

| Requirement | Implementation |
|-------------|----------------|
| Authentication | JWT with 24-hour expiry |
| Password Storage | bcrypt with salt |
| Data Encryption | HTTPS (TLS 1.3) |
| SQL Injection | Parameterized queries |
| XSS Protection | Input sanitization |
| CORS | Configured origins only |

### 9.3 Scalability

| Aspect | Approach |
|--------|----------|
| Database | PostgreSQL with connection pooling |
| Caching | Redis for session/frequent data |
| File Storage | S3-compatible storage |
| Load Balancing | Nginx reverse proxy |

### 9.4 Availability

| Requirement | Target |
|-------------|--------|
| Uptime | 99.5% |
| Backup Frequency | Daily |
| Recovery Time | < 4 hours |

---

## 10. Appendix

### 10.1 Glossary

| Term | Definition |
|------|------------|
| **GUID** | Globally Unique Identifier (Tally record ID) |
| **AlterID** | Tally's change tracking number |
| **Voucher** | Tally transaction record |
| **Ledger** | Tally account record |
| **JWT** | JSON Web Token for authentication |
| **RBAC** | Role-Based Access Control |

### 10.2 References

- Ganesh Project: `D:\Project\Katara Dental\TDL\Pramit\Ganesh`
- TallyInsight Project: `D:\Microservice\TallyInsight`
- Tally ODBC Documentation: Tally Solutions

---

*Document Created: January 16, 2026*  
*Author: Development Team*  
*Version: 1.0*

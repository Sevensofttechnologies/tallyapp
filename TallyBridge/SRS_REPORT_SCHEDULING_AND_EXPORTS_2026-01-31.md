# Software Requirements Specification (SRS)
# Report Scheduling + Large Export Jobs + SMTP Settings (Global)

**Document Version:** 1.0  
**Date:** January 31, 2026  
**Project:** TallyBridge + TallyInsight Reports (Exports + Scheduling + Auto Email)

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Goals and Scope](#2-goals-and-scope)
3. [User Roles](#3-user-roles)
4. [Assumptions and Constraints](#4-assumptions-and-constraints)
5. [Functional Requirements](#5-functional-requirements)
6. [System Flows](#6-system-flows)
7. [API Specifications](#7-api-specifications)
8. [Database Design](#8-database-design)
9. [Security Requirements](#9-security-requirements)
10. [Non-Functional Requirements](#10-non-functional-requirements)
11. [Operational Requirements](#11-operational-requirements)
12. [Out of Scope](#12-out-of-scope)

---

## 1. Introduction

### 1.1 Purpose
हा SRS document खालील features define करतो:

- Large reports साठी **reliable exports** (CSV / XLSX / PDF)
- XLSX/PDF साठी **Background Jobs** (Redis-backed queue + status)
- **Admin UI** मधून SMTP provider configuration (DB मध्ये encrypted storage)
- **Global scheduling** (hourly/daily/weekly/monthly) + timezone aware
- Scheduled reports साठी **auto email delivery** (10,000+ schedules scale)

### 1.2 Definitions

| Term | Definition |
|------|------------|
| **Export Job** | Report generate करून file तयार करणारा background task |
| **Schedule** | वेळापत्रक (hourly/daily/weekly/monthly) अनुसार report auto-run |
| **Run** | एक schedule execution instance |
| **Queue** | Background tasks process करण्यासाठी job queue |
| **Redis** | Queue + job status/progress store |
| **Local Disk Storage** | Report output files temporarily server disk वर ठेवणे |
| **Global Timezone** | Users worldwide, schedule user timezone वर based |
| **Party / Customer (Tally)** | Tenant च्या आतला Tally party/ledger (Sundry Debtor/Creditor/Party Ledger) |

---

## 2. Goals and Scope

### 2.1 Goals

- UI data load वेळ कमी करणे (server-side pagination + summary-first)
- Exports timeout कमी/avoid करणे:
  - CSV: streaming preferred
  - XLSX/PDF: background job preferred
- Scheduling + email delivery 10k+ customers scale वर reliable ठेवणे

### 2.2 In Scope

- Report listing APIs: pagination, filtering, sorting
- Export APIs: immediate CSV streaming (where feasible), job-based XLSX/PDF
- SMTP settings admin module (encrypted DB storage)
- Scheduler service + worker services
- Audit logs for runs + export jobs

---

## 3. User Roles

| Role | Capabilities |
|------|--------------|
| **Super Admin** | System-wide settings (SMTP defaults), view all tenants |
| **Admin** | Tenant-level SMTP config (optional override), schedule create/edit |
| **User** | Reports view, manual export, schedule view (permission-based) |

---

## 4. Assumptions and Constraints

### 4.1 Assumptions

- Storage: **Local disk OK** initially
- Redis available for queue + status
- Users worldwide; schedules must be timezone-aware

### 4.2 Constraints

- SQLite queries/report generation can be heavy for 10,000+ rows
- XLSX/PDF generation is CPU + memory heavy; direct request/response may timeout

---

## 5. Functional Requirements

### 5.1 Report UI Performance

- **FR-UI-01:** Reports endpoints must support `page` + `page_size`
- **FR-UI-02:** UI should fetch summary/totals first, then paginated rows
- **FR-UI-03:** For large datasets, UI should avoid loading all rows at once
- **FR-UI-04:** Filters (company/date/search) must be supported server-side

### 5.2 Manual Exports (User Initiated)

- **FR-EX-01:** CSV exports should support streaming for large datasets
- **FR-EX-02:** XLSX/PDF exports should be job-based for large datasets
- **FR-EX-03:** Export job must return `job_id` immediately
- **FR-EX-04:** User should be able to download generated file after job completes

### 5.2A Manual “Send Email” (Send Now) - Per Report

- **FR-EMAIL-UI-01:** Reports page वर `PDF / CSV / XLSX` export buttons च्या शेजारी **`Email` button** असावा
- **FR-EMAIL-UI-02:** `Email` button click केल्यावर dialog/popup:
  - `To Email` (user manually type करू शकतो)
  - optional: `CC` / `BCC`
  - `Format` (CSV/XLSX/PDF)
  - `Send` action
- **FR-EMAIL-UI-03:** User ने type केलेल्या email वर **तोच report** पाठवला पाहिजे:
  - current report प्रकार (उदा. Outstanding/Ledger)
  - current tab (ledgerwise/billwise etc.)
  - current filters (company, date, search, page params)
- **FR-EMAIL-UI-04:** “Send Email” feature **सगळ्या reports** साठी generic असावा (report-specific hardcoding टाळणे)

### 5.2B Manual “Send Email” - Party/Customer (Tally) Support

- **FR-EMAIL-PARTY-01:** “Customer” चा अर्थ: **tenant च्या आतला party/ledger**
- **FR-EMAIL-PARTY-02:** UI मध्ये (optional) party select + email auto-fill असू शकतो:
  - party_name/ledger_name -> default email
  - user manually override करू शकतो
- **FR-EMAIL-PARTY-03:** Party email mapping **tenant-scoped** असावी

### 5.2C Email Delivery Rules (Manual)

- **FR-EMAIL-RULE-01:** Report छोटा असेल तर attachment म्हणून पाठवणे
- **FR-EMAIL-RULE-02:** Report मोठा असेल (size/row threshold) तर:
  - background job ने file generate
  - email मध्ये **download link** (token protected) पाठवणे
- **FR-EMAIL-RULE-03:** Email send action साठी audit trail mandatory

### 5.2D Final Rules (Clarified)

- **FR-EMAIL-FINAL-01 (Ledger Report):** Ledger report हा **single-ledger report** आहे. त्यामुळे:
  - `party_email_directory` mapping **ledger_name/party_name** वर आधारित असावा
  - ledger select केल्यावर email **auto-fill** (available असल्यास)
  - email missing असेल तर user **manual type** करेल
  - `To` + `CC` + `BCC` fields **always** available असावेत
  - UI मध्ये internal/party modes (Mode A/Mode B) **नकोत**
- **FR-EMAIL-FINAL-02 (Outstanding Report):** Outstanding report हा **internal-only** आहे:
  - बाहेर (party/customer ला) पाठवणे **allowed नाही**
  - Party-specific “Mode B / separate ledger sathi outstanding” **नको**

### 5.3 SMTP Provider Admin Menu

- **FR-SMTP-01:** Admin UI मध्ये स्वतंत्र menu: “Email Settings / SMTP”
- **FR-SMTP-02:** SMTP settings fields:
  - `host`, `port`, `username`, `password/app_password`
  - `use_tls`, `use_ssl`
  - `from_email`, `from_name`
  - optional: `reply_to`, `test_recipient`
- **FR-SMTP-03:** “Send Test Email” feature must be available
- **FR-SMTP-04:** SMTP settings DB मध्ये **encrypted** store करणे
- **FR-SMTP-05:** Each tenant can save own SMTP settings; system may also have defaults

### 5.4 Scheduling (Hourly/Daily/Weekly/Monthly)

- **FR-SCH-01:** Users can create schedule with:
  - report type (Outstanding / Ledger / etc.)
  - filters (company, as-on date rules, etc.)
  - format (CSV/XLSX/PDF)
  - frequency: hourly/daily/weekly/monthly
  - timezone (IANA tz, e.g. `Asia/Kolkata`, `America/New_York`)
  - recipients list
- **FR-SCH-02:** System must support **global timezone** behavior:
  - schedules run at user timezone time
  - server stores schedule in canonical format
- **FR-SCH-03:** Schedule runs must be idempotent (no duplicate emails)

### 5.5 Auto Email Delivery

- **FR-EM-01:** Schedule run triggers export job generation
- **FR-EM-02:** After export completes, email is sent to recipients
- **FR-EM-03:** Email must include either:
  - attachment (if size under threshold), OR
  - download link (local storage + signed token)
- **FR-EM-04:** Failed email/send must retry with backoff
- **FR-EM-05:** Failures must be visible in audit UI/logs

---

## 6. System Flows

### 6.1 Manual Export Flow (XLSX/PDF Job)

1. UI -> `POST /exports/jobs` with report params
2. API returns `{ job_id, status: queued }`
3. Worker generates report file -> stores to local disk
4. Worker updates Redis job status -> `done` + file path
5. UI polls `GET /exports/jobs/{job_id}` until `done`
6. UI downloads via `GET /exports/jobs/{job_id}/download`

### 6.2 Scheduled Email Flow

1. Scheduler scans DB for due schedules
2. Scheduler creates a `schedule_run` record
3. Scheduler enqueues `GenerateReportJob(run_id)`
4. Worker generates report + stores file
5. Worker enqueues `SendEmailJob(run_id)`
6. Email worker sends email
7. Run status updated to `sent` or `failed`

---

## 7. API Specifications (Proposed)

### 7.1 SMTP Settings

- `GET /api/v1/admin/email-settings`
- `PUT /api/v1/admin/email-settings`
- `POST /api/v1/admin/email-settings/test`

### 7.2 Export Jobs

- `POST /api/v1/exports/jobs`
  - body: report type + filters + format
  - response: `job_id`

- `GET /api/v1/exports/jobs/{job_id}`
  - response: status/progress/error

- `GET /api/v1/exports/jobs/{job_id}/download`
  - returns file stream

### 7.4 Manual Send Email (Proposed)

- `POST /api/v1/reports/send-email`
  - body:
    - `report_type`
    - `report_params_json` (current filters/tab)
    - `format` (csv/xlsx/pdf)
    - `to_email` (+ optional cc/bcc)
    - optional: `party_name` (for audit / mapping)
  - response:
    - `job_id` (if background generation needed) OR immediate `sent` status

### 7.3 Scheduling

- `POST /api/v1/schedules`
- `GET /api/v1/schedules`
- `PUT /api/v1/schedules/{schedule_id}`
- `DELETE /api/v1/schedules/{schedule_id}`

- `GET /api/v1/schedules/{schedule_id}/runs`

---

## 8. Database Design (Proposed)

### 8.1 `email_settings`

- `tenant_id`
- `smtp_host`
- `smtp_port`
- `smtp_user`
- `smtp_password_encrypted`
- `use_tls`
- `use_ssl`
- `from_email`
- `from_name`
- `updated_at`

### 8.1A `party_email_directory` (Proposed)

- `tenant_id`
- `company_name` (optional, if mapping differs per company)
- `party_name` (ledger name)
- `email`
- `is_primary`
- `updated_at`

### 8.2 `report_schedules`

- `schedule_id`
- `tenant_id`
- `created_by_user_id`
- `report_type`
- `report_params_json`
- `format`
- `frequency`
- `timezone`
- `start_at`
- `enabled`
- `created_at`, `updated_at`

### 8.3 `schedule_runs`

- `run_id`
- `schedule_id`
- `tenant_id`
- `planned_at_utc`
- `status`
- `attempt_count`
- `result_file_path`
- `error_message`
- `created_at`, `updated_at`

### 8.4 `export_jobs`

- `job_id`
- `tenant_id`
- `created_by_user_id` (nullable for schedules)
- `job_type` (manual/scheduled)
- `report_type`
- `params_json`
- `status`
- `progress`
- `result_file_path`
- `error_message`
- timestamps

### 8.5 `email_audit` (Manual + Scheduled)

- `tenant_id`
- `sent_by_user_id` (nullable for scheduled)
- `source` (manual/scheduled)
- `report_type`
- `report_params_json`
- `to_email`, `cc`, `bcc`
- `format`
- `attachment_used` (bool)
- `download_link_used` (bool)
- `result_file_path` (if applicable)
- `status` (sent/failed)
- `error_message`
- timestamps

---

## 9. Security Requirements

- **SEC-01:** SMTP password must be encrypted at rest (KMS/FERNET key from env)
- **SEC-02:** Download endpoint must validate auth + tenant ownership
- **SEC-03:** Scheduled jobs must run under tenant context
- **SEC-04:** Logs must not print SMTP password

---

## 10. Non-Functional Requirements

- **NFR-01:** System must handle 10,000+ schedules reliably
- **NFR-02:** Horizontal scale: add worker instances to increase throughput
- **NFR-03:** Retries with exponential backoff
- **NFR-04:** Idempotency: schedule_id + planned_at unique
- **NFR-05:** Observability: metrics + audit logs

---

## 11. Operational Requirements

- Redis required for:
  - queue
  - job status/progress
  - distributed locks (optional)

- Local disk storage requirements:
  - cleanup job (TTL-based delete)
  - sufficient space monitoring

---

## 12. Out of Scope

- Multi-region deployments
- S3/MinIO migration (planned later)
- UI design details (covered in separate UI SRS)

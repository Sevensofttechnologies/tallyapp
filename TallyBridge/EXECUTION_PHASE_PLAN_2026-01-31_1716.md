# Execution Phase Plan (Pending)

**Created:** 2026-01-31 17:16 IST  
**Status:** Completion: Pending

---

## Final Rules (Clarified)

### Ledger Report

- Ledger report हा **single-ledger report** आहे.
- `party_email_directory` mapping **ledger_name/party_name** वर आधारित असावा.
- ledger select केल्यावर email **auto-fill** (available असल्यास).
- email missing असेल तर user **manual type** करेल.
- `To` + `CC` + `BCC` fields **always** available असावेत.
- UI मध्ये internal/party modes (Mode A/Mode B) **नकोत**.

### Outstanding Report

- Outstanding report हा **internal-only** आहे.
- बाहेर (party/customer ला) पाठवणे **allowed नाही**.
- Party-specific “Mode B / separate ledger sathi outstanding” **नको**.

---

## Phase-wise Task List

### Phase 0 — Finalize Scope + Defaults (Design Freeze)

- Email dialog UX finalize (To/CC/BCC + format + send)
- “Outstanding internal-only” enforcement rules finalize
- thresholds finalize:
  - attachment max size (e.g. 8–15 MB)
  - link-only rules (recommended for XLSX/PDF)
- outstanding internal recipients source finalize:
  - typed each time OR saved internal distribution list

### Phase 1 — DB + Security Foundations

- DB tables/migrations:
  - `email_settings` (encrypted password)
  - `party_email_directory`
  - `export_jobs`
  - `email_audit`
  - `report_schedules`, `schedule_runs`
- Encryption key management via env
- AuthZ rules (Admin vs User permissions)

### Phase 2 — Export Job Framework (Backend) + Local File Storage

- `POST /exports/jobs` create job
- Redis-backed queue + worker skeleton
- local disk storage layout + cleanup policy (TTL)
- `GET /exports/jobs/{id}` status
- `GET /exports/jobs/{id}/download` secured download

### Phase 3 — SMTP Admin Module (Backend + UI)

- Admin APIs: get/update settings, send test email
- Admin UI page + validations

### Phase 4 — Email Sending Service + Audit (Manual + Scheduled compatible)

- Email sender utility (TLS/SSL, from_name, reply_to)
- attachment vs link logic
- `email_audit` writes for every attempt
- retry strategy (scheduled), manual error surface

### Phase 5 — Manual “Send Email” UI (Ledger + Outstanding rules)

- Ledger Report:
  - Email button + dialog
  - `party_email_directory` auto-fill by ledger_name
  - manual type fallback, CC/BCC
- Outstanding Report:
  - Email button allowed पण **internal-only**
  - no party directory usage

### Phase 6 — Scheduling Engine (Timezone-aware) + Runs UI

- Scheduler service (scan due schedules, create runs)
- worker jobs: generate report -> send email
- idempotency guarantees + retries
- schedules UI + runs history

### Phase 7 — Validation / Smoke Tests

- curl-based checklist:
  - export job create → poll → download
  - smtp test
  - manual email ledger/outstanding rules
  - scheduled run execution

---

## Approvals Needed (Before Implementation)

- A) Outstanding internal recipients:
  - Option 1: user types To/CC/BCC each time
  - Option 2: tenant-level saved internal distribution list
- B) Manual send for CSV:
  - attachment allowed? OR link-only?

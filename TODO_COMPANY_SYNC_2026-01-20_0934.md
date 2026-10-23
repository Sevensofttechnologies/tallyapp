# TODO: Company Details Sync to Database

**Task ID:** COMPANY_SYNC_2026-01-20_0934  
**Created:** 20-Jan-2026 09:34 AM  
**SRS:** `srs/SRS_COMPANY_DETAILS_SYNC_2026-01-20.md`  
**Status:** In Progress  

---

## Completed Tasks

| # | Task | File | Status | Completed |
|---|------|------|--------|-----------|
| 1 | v1.6.0 Ledger Report Accounting Fix | Multiple | ✅ DONE | 19-Jan-2026 |
| 2 | PDF service created | `pdf_service.py`, `ledger_controller.py` | ✅ DONE | 19-Jan-2026 |
| 3 | SRS created and APPROVED | `SRS_COMPANY_DETAILS_SYNC_2026-01-20.md` | ✅ DONE | 20-Jan-2026 09:34 |

---

## Pending Tasks

| # | Task | File | Status | Notes |
|---|------|------|--------|-------|
| 4 | Add `mst_company` table schema | `TallyInsight/app/services/database_service.py` | ⏳ PENDING | Add in `_create_tables()` |
| 5 | Add XML request for company details | `TallyInsight/app/services/tally_service.py` | ⏳ PENDING | Use template from SRS |
| 6 | Add `sync_company_details()` method | `TallyInsight/app/services/sync_service.py` | ⏳ PENDING | Parse XML, save to DB |
| 7 | Update PDF endpoint to read from DB | `TallyInsight/app/controllers/ledger_controller.py` | ⏳ PENDING | Query `mst_company` |
| 8 | Test: Sync company details | - | ⏳ PENDING | Verify data in DB |
| 9 | Test: PDF export with company header | - | ⏳ PENDING | Check address, email, CIN |
| 10 | Push v1.7.0 with release notes | - | ⏳ PENDING | Git commit + tag |

---

## Files to Modify

| File | Change Type | Description |
|------|-------------|-------------|
| `TallyInsight/app/services/database_service.py` | MODIFY | Add `mst_company` table schema |
| `TallyInsight/app/services/tally_service.py` | MODIFY | Add XML request for company details |
| `TallyInsight/app/services/sync_service.py` | MODIFY | Add `sync_company_details()` method |
| `TallyInsight/app/controllers/ledger_controller.py` | MODIFY | PDF reads from `mst_company` |

---

## Key Logic: ALTER_ID

Tally मध्ये प्रत्येक record ला `ALTER_ID` असतो. जेव्हा record बदलतो तेव्हा ALTER_ID वाढतो.

```
Sync Logic:
1. Fetch current ALTER_ID from Tally
2. Compare with mst_company.alter_id
3. If changed → UPDATE record
4. If same → Skip
```

---

## Progress Log

| Date | Time | Action | Status |
|------|------|--------|--------|
| 20-Jan-2026 | 09:28 | SRS created | ✅ |
| 20-Jan-2026 | 09:32 | ALTER_ID logic added to SRS | ✅ |
| 20-Jan-2026 | 09:34 | SRS APPROVED | ✅ |
| 20-Jan-2026 | 09:34 | TODO list created | ✅ |
| | | Step 4: Add mst_company table | ⏳ |

---

**Next Step:** Step 4 - Add `mst_company` table in `database_service.py`

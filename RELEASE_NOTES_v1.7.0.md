# Release Notes - v1.7.0

**Release Date:** 20-Jan-2026  
**Tag:** v1.7.0

---

## 🎯 Highlights

1. **Company Details Sync** - Sync company info from Tally to database for offline PDF export
2. **Opening Balance Fix** - Correct calculation based on selected date range
3. **Documentation** - Ledger Report logic documentation added

---

## ✨ New Features

### 1. Company Details Sync (`mst_company` table)
- New `mst_company` table stores company details from Tally
- Syncs: Name, Address, State, Pincode, Email, Mobile, GSTIN, PAN, CIN
- Uses ALTER_ID for change detection (only updates when changed in Tally)
- Enables PDF export with company header even when Tally is offline

**Files Changed:**
- `TallyInsight/app/services/database_service.py` - Added mst_company table schema
- `TallyInsight/app/services/sync_service.py` - Added `_sync_company_details()` method
- `TallyInsight/app/controllers/ledger_controller.py` - PDF reads company info from mst_company

### 2. Ledger Report Documentation
- Comprehensive documentation for Opening/Closing Balance logic
- Period-wise examples (day, week, month, quarter, year, multi-year)
- IsDeemedPositive logic explained
- Testing checklist included

**File Added:**
- `docs/LEDGER_REPORT_LOGIC.md`

---

## 🐛 Bug Fixes

### 1. Opening Balance Calculation Fix
**Issue:** Opening Balance was showing incorrect value when date range selected

**Root Cause:** 
- Opening Balance was taken directly from `mst_ledger.opening_balance`
- Should be: `Base Opening + SUM(transactions BEFORE from_date)`

**Fix:**
- Calculate Opening Balance based on selected date range
- Pre-period transactions now included in opening calculation
- Same fix applied to both Ledger Report API and PDF export

**Example:**
```
Ledger: SILICONVEINS PVT LTD
Base Opening: ₹2,124.00
Transactions before 01-Apr-2025: ₹2,124.00 (Debit)

Before Fix: Opening = ₹2,124.00 ❌
After Fix:  Opening = ₹0.00 ✅ (matches Tally)
```

**Files Changed:**
- `TallyInsight/app/controllers/ledger_controller.py`
  - `get_ledger_report()` - Opening Balance calculation
  - `get_ledger_report_pdf()` - Same fix for PDF

---

## 📁 Files Changed

| File | Change Type |
|------|-------------|
| `TallyInsight/app/services/database_service.py` | Modified - mst_company table |
| `TallyInsight/app/services/sync_service.py` | Modified - sync_company_details() |
| `TallyInsight/app/controllers/ledger_controller.py` | Modified - Opening Balance fix |
| `docs/LEDGER_REPORT_LOGIC.md` | Added - Documentation |
| `srs/SRS_COMPANY_DETAILS_SYNC_2026-01-20.md` | Added - SRS document |

---

## 🧪 Testing

### Ledger Report Testing Checklist

| Test Case | from_date | to_date | Status |
|-----------|-----------|---------|--------|
| Full FY | 01-Apr-2025 | 31-Mar-2026 | ✅ |
| Single Day | 14-Apr-2025 | 14-Apr-2025 | ✅ |
| One Week | 14-Apr-2025 | 20-Apr-2025 | ✅ |
| One Month | 01-May-2025 | 31-May-2025 | ✅ |
| Multi-Year | 01-Apr-2021 | 31-Mar-2026 | ✅ |

### PDF Export Testing
- Company header displays correctly ✅
- Opening/Closing Balance matches Tally ✅

---

## 🔄 Upgrade Notes

1. **Database Migration:** Run sync after upgrade to create `mst_company` table
2. **Fresh Sync Recommended:** For correct Opening Balance values

---

## 📋 Dependencies

No new dependencies added.

---

## 🔜 Next Version (v1.8.0 Planned)

- Bill-wise Outstanding Report
- Multi-company PDF export
- Dashboard enhancements

---

**Full Changelog:** v1.6.0...v1.7.0

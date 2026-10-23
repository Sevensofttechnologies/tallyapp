# TallyInsightPlus v1.6.0 - Ledger Report Accounting Fix

## Changelog
All notable changes to TallyInsightPlus will be documented in this file.

---

## [1.6.0] - 2026-01-19

### 🔧 Bug Fixes

#### Ledger Report - Correct Accounting Logic
- **Fixed Debit/Credit Display** for Sundry Debtors
  - Sales voucher now correctly shows in **Debit** column
  - Payment voucher now correctly shows in **Debit** column
  - Journal (Credit) voucher shows in **Credit** column
  - Based on `IsDeemedPositive` flag from parent group

- **Fixed Running Balance Calculation**
  - Formula: `Balance = Previous - Debit + Credit`
  - Matches Tally Prime display exactly

### 🚀 New Features

#### Footer Rows (Tally Style)
- **Current Total Row** - Shows sum of Debit and Credit columns
- **Closing Balance Row** - Shows final balance in Debit or Credit column

---

### 📁 Files Changed

| File | Changes |
|------|---------|
| `TallyInsight/app/controllers/ledger_controller.py` | Added `is_deemed_positive` check for correct debit/credit logic |
| `TallyBridge/frontend/js/reports/ledger.js` | Fixed running balance formula, added footer rows |

---

### 📋 POC Files Created

| File | Description |
|------|-------------|
| `poc/ledger_display/extract_data.py` | Extract ledger data from DB to JSON |
| `poc/ledger_display/data.json` | Extracted transaction data |
| `poc/ledger_display/ledger_report.html` | POC HTML with correct accounting logic |
| `poc/ledger_display/ledger_report_v2.html` | POC v2 with Tally PDF style |
| `srs/SRS_LEDGER_DISPLAY_POC_2026-01-19.md` | SRS document for POC |

---

### 🔍 Technical Details

#### Accounting Logic (IsDeemedPositive)

For **Sundry Debtors** (IsDeemedPositive = 1):
| Voucher Type | DB Amount | Display Column |
|--------------|-----------|----------------|
| Sales | Negative | **Debit** |
| Payment | Negative | **Debit** |
| Receipt | Positive | **Credit** |
| Journal (Cr) | Positive | **Credit** |

For **Sundry Creditors** (IsDeemedPositive = 0):
| Voucher Type | DB Amount | Display Column |
|--------------|-----------|----------------|
| Purchase | Positive | **Credit** |
| Payment | Negative | **Debit** |
| Receipt | Positive | **Credit** |

#### Running Balance Formula
```
Balance = Opening Balance - Debit + Credit
```

#### Closing Balance
```
Closing = Opening + Credit - Debit
If Negative → Show in Debit column
If Positive → Show in Credit column
```

---

### 📊 Test Results

| Test | Result |
|------|--------|
| Sales in Debit column | ✅ Working |
| Payment in Debit column | ✅ Working |
| Running Balance correct | ✅ Working |
| Current Total row | ✅ Working |
| Closing Balance row | ✅ Working |
| Closing Balance position | ✅ Debit/Credit column based on sign |

---

## Tags
- `v1.6.0` - Ledger Report Accounting Fix + Footer Rows

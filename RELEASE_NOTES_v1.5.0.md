# TallyInsightPlus v1.5.0 - Ledger Master & List UI

## Changelog
All notable changes to TallyInsightPlus will be documented in this file.

---

## [1.5.0] - 2026-01-19

### 🚀 New Features

#### Ledger Master API
- **30 Field Extraction** from Tally Prime via TDL XML
  - Basic: guid, name, parent, alias, description, notes
  - Balance: opening_balance, closing_balance
  - Contact: mailing_name, address, state, country, pincode, email, mobile
  - Statutory: pan, gstin, gst_registration_type, gst_supply_type, gst_duty_head, tax_rate
  - Bank: account_holder, account_number, ifsc, swift, bank_name, branch
  - Settings: is_revenue, is_deemed_positive, credit_period

- **New API Endpoints**
  - `GET /api/sync/ledger/master` (TallyInsight - Port 8401)
  - `GET /api/v1/tally/ledger/master` (TallyBridge - Port 8451)

#### Ledger List UI
- **New Ledger List Tab** in Reports > Ledger page
  - DataTable with 7 columns: Name, Parent, GSTIN, Mobile, Email, Opening, Closing
  - Supports 3800+ ledgers with smooth scrolling
  
- **Category Tabs**
  - All Ledgers - Shows all ledgers
  - Sundry Debtors - Filters by parent "Sundry Debtors"
  - Sundry Creditors - Filters by parent "Sundry Creditors"

- **Search & Filter**
  - Real-time search across name, parent, GSTIN, mobile, email
  - Column sorting (click headers)
  
- **Click-to-View**
  - Click any ledger row → Opens Transactions tab with that ledger selected

---

### 📁 Files Changed

| File | Changes |
|------|---------|
| `TallyInsight/app/services/tally_service.py` | Added `get_ledger_master()`, `_parse_ledger_master_response()`, `_format_ledger()` |
| `TallyInsight/app/controllers/sync_controller.py` | Added `/api/sync/ledger/master` endpoint |
| `TallyBridge/app/services/tally_service.py` | Added proxy `get_ledger_master()` method |
| `TallyBridge/app/routes/tally.py` | Added `/api/v1/tally/ledger/master` route |
| `TallyBridge/frontend/reports/ledger.html` | Added Ledger List view with category tabs |
| `TallyBridge/frontend/js/reports/ledger.js` | Added `loadLedgerMaster()`, `renderLedgerListTable()`, `filterLedgerList()`, `switchLedgerCategory()` |

---

### 📋 New Files

| File | Description |
|------|-------------|
| `poc/ledger_master/test_ledger_master.py` | POC script for Ledger Master extraction |
| `poc/ledger_master/show_sample.py` | Sample data viewer |
| `srs/SRS_LEDGER_LIST_UI_2026-01-19_1231.md` | SRS document |
| `todo/LEDGER_MASTER_IMPL_2026-01-19_1216.md` | Implementation TODO |
| `todo/LEDGER_LIST_UI_2026-01-19_1231.md` | UI TODO |

---

### 🔧 Technical Details

- **TDL XML Request** for fetching all ledger fields
- **UTF-16 Encoding** for Tally communication
- **120 second timeout** for large data requests
- **Structured JSON response** with categorized fields

---

### 📊 Test Results

| Test | Result |
|------|--------|
| TallyInsight API | ✅ 3811 ledgers fetched |
| TallyBridge API | ✅ Proxy working |
| Ledger List UI | ✅ All tabs working |
| Search/Filter | ✅ Real-time filtering |
| Row Click | ✅ Opens transactions |

---

## Tags
- `v1.5.0` - Ledger Master API and Ledger List UI

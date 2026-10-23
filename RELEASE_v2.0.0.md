# Release Notes - v2.0.0

**Release Date:** January 24, 2026  
**Tag:** v2.0.0  
**Commit:** 814a776

---

## 🎯 Major Feature: Outstanding Reports - 100% Tally Match

This is a **MAJOR RELEASE** that fixes the Outstanding Reports (Bills Receivable and Bills Payable) to achieve 100% accuracy with Tally ERP.

---

## ✨ What's Fixed

### Outstanding Reports - Complete Overhaul

**Problem:**
- Bills Receivable and Bills Payable reports were not matching Tally
- Fully settled bills were appearing in reports
- Incorrect deduplication logic causing wrong totals
- Misunderstanding of database sign convention

**Solution:**
- ✅ Fixed deduplication logic with `billtype` in partition
- ✅ Corrected database sign convention understanding
- ✅ Removed unnecessary negation from query
- ✅ Settled bills (net = 0) now correctly excluded
- ✅ 100% match with Tally Bills Receivable and Bills Payable reports

---

## 🎉 Verification Results

### Bills Receivable Report
- **Parties:** 17/17 ✅ EXACT MATCH
- **Total Amount:** ₹11,39,259.30 ✅ EXACT MATCH
- **All Party Amounts:** Exact match ✅

### Bills Payable Report
- **Parties:** 10/10 ✅ EXACT MATCH
- **Total Amount:** ₹10,39,029.00 ✅ EXACT MATCH
- **All Party Amounts:** Exact match ✅

**Test Company:** Vrushali Infotech Pvt Ltd. 25-26  
**Test Period:** 01-Apr-2025 to 31-Mar-2026

---

## 🔧 Technical Changes

### 1. Database Sign Convention (Critical Discovery)

**Corrected Understanding:**
```
Database Storage:
- Negative (-) = Dr (Receivable - आम्हाला मिळायचे)
- Positive (+) = Cr (Payable - आम्ही द्यायचे)

Both opening_balance and trn_bill.amount use SAME convention!
NO negation needed in query!
```

### 2. Deduplication Logic Fix

**Previous (Incorrect):**
```sql
PARTITION BY party_name, bill_no, bill_date, amount
```

**New (Correct):**
```sql
PARTITION BY party_name, bill_no, billtype, bill_date, amount
```

**Why Critical:**
- Same bill can have multiple entries with same date and amount but different `billtype`
- Example: SANJEEVANI VIPL/25-26/002
  - New Ref (Receipt): +2,000 (02-Apr)
  - Agst Ref (Receipt): +2,000 (02-Apr)
- Without `billtype` in partition, these were treated as duplicates!
- This caused incorrect net balance calculation

### 3. Settled Bills Exclusion

**Logic:**
```sql
-- Calculate net balance for each bill
SUM(amount) as pending_amount

-- Exclude fully settled bills
HAVING ABS(pending_amount) > 0.01
```

**Example - Atharva VIPL/25-26/005 (Fully Settled):**
```
New Ref (Receipt): +1,186 (Cr)
Agst Ref (Receipt): +2,000 (Cr)
Agst Ref (Sales): -3,186 (Dr)
Net: +1,186 + 2,000 - 3,186 = 0 → Excluded ✅
```

### 4. Report Filtering

**Receivable (Dr bills):**
```sql
WHERE pending_amount < 0  -- Negative = Dr
```

**Payable (Cr bills):**
```sql
WHERE pending_amount > 0  -- Positive = Cr
```

---

## 📝 Code Changes

### Modified Files

#### 1. `TallyInsight/app/controllers/outstanding_controller.py`

**Lines 319-328:** Added `billtype` to opening bills query
```python
SELECT 
    o.ledger as party_name,
    o.name as bill_no,
    o.bill_date,
    CASE WHEN o.bill_credit_period > 0 THEN o.bill_credit_period ELSE 1 END as bill_credit_period,
    o.opening_balance as amount,  -- Use as-is (NO negation)
    'Opening' as source,
    o._company,
    0 as alterid,
    'Opening' as billtype  -- NEW: Added billtype
```

**Lines 338-347:** Added `billtype` to transaction bills query
```python
SELECT 
    b.ledger as party_name,
    b.name as bill_no,
    v.date as bill_date,
    CASE WHEN b.bill_credit_period > 0 THEN b.bill_credit_period ELSE 1 END as bill_credit_period,
    b.amount as amount,  -- Use as-is (NO negation needed)
    v.voucher_type as source,
    b._company,
    b.alterid,
    b.billtype  -- NEW: Added billtype
```

**Lines 354-372:** Fixed deduplication partition
```python
deduped_bills AS (
    SELECT 
        party_name,
        bill_no,
        bill_date,
        bill_credit_period,
        amount,
        source,
        _company,
        alterid,
        billtype,
        ROW_NUMBER() OVER (
            PARTITION BY party_name, bill_no, billtype, bill_date, amount  -- FIXED: Added billtype
            ORDER BY alterid DESC
        ) as rn
    FROM all_bills
)
```

**Lines 368-383:** Removed incorrect bill_types_check filter
```python
bill_totals AS (
    -- Calculate net balance for each bill
    -- CRITICAL: Tally checks total Dr vs total Cr for each bill
    -- Bills with net = 0 (fully settled) are excluded by HAVING clause
    SELECT
        d.party_name,
        d.bill_no,
        MIN(d.bill_date) as bill_date,
        MAX(d.bill_credit_period) as bill_credit_period,
        SUM(d.amount) as pending_amount,
        GROUP_CONCAT(DISTINCT d.source) as source,
        d._company
    FROM deduped_bills d
    WHERE d.rn = 1 AND 1=1  -- Removed incorrect bill_types_check join
    GROUP BY d.party_name, d.bill_no, d.bill_date, d.bill_credit_period, d._company
    HAVING ABS(SUM(d.amount)) > 0.01  -- Exclude settled bills
)
```

#### 2. `TallyInsight/OUTSTANDING_REPORTS_DOCUMENTATION.md` (NEW FILE)

**Complete technical documentation including:**
- Database tables and fields (`mst_opening_bill_allocation`, `trn_bill`, `trn_voucher`, `mst_ledger`)
- Sign convention explanation
- Query logic with CTEs
- Complete SQL query with comments
- Real examples (Atharva, SANJEEVANI, SYNCAXIS, Aerocircle)
- Deduplication key learning
- Settled bills logic
- Verification results

---

## 📊 Files Changed

**2 files changed, 710 insertions(+), 33 deletions(-)**

### Modified:
1. `TallyInsight/app/controllers/outstanding_controller.py` - Core logic fix

### New:
2. `TallyInsight/OUTSTANDING_REPORTS_DOCUMENTATION.md` - Complete documentation

---

## 🧪 Testing

### Test Cases Verified:

1. ✅ **Atharva VIPL/25-26/005** - Net = 0 (correctly excluded)
2. ✅ **SANJEEVANI VIPL/25-26/002** - Net = 0 (correctly excluded)
3. ✅ **SYNCAXIS** - Both Receivable and Payable bills (correctly separated)
4. ✅ **Aerocircle** - Both Dr and Cr bills (correctly separated)
5. ✅ **Deduplication** - Multiple billtype entries with same date/amount (correctly handled)
6. ✅ **MAYUR** - Pure Agst Ref bill (correctly included)

### Comparison with Tally:

**Bills Receivable:**
- All 17 parties match exactly
- All amounts match exactly
- Total matches exactly: ₹11,39,259.30

**Bills Payable:**
- All 10 parties match exactly
- All amounts match exactly
- Total matches exactly: ₹10,39,029.00

---

## 🔄 Upgrade Notes

### For Users:

1. **Pull latest code:**
   ```bash
   git pull origin master
   ```

2. **Restart TallyInsight server:**
   ```bash
   cd TallyInsight
   uvicorn app.main:app --reload --port 8451
   ```

3. **Restart TallyBridge server:**
   ```bash
   cd TallyBridge
   python app/main.py
   ```

4. **Verify Outstanding Reports:**
   - Navigate to Reports → Outstanding → Receivable
   - Navigate to Reports → Outstanding → Payable
   - Compare with Tally Bills Receivable and Bills Payable reports

### No Database Changes Required
- All changes are in SQL query logic only
- No schema modifications
- No data migration needed

---

## 🐛 Known Issues

None reported.

---

## 📚 Key Learnings

### 1. Database Sign Convention
- Both `mst_opening_bill_allocation.opening_balance` and `trn_bill.amount` use SAME sign convention
- Negative = Dr (Receivable), Positive = Cr (Payable)
- NO negation needed in query!

### 2. Deduplication Partition
- Must include `billtype` to handle same bill with different types
- Same date + same amount + different billtype = different entries
- Critical for accurate net balance calculation

### 3. Tally's Logic
- Tally only checks net Dr vs Cr balance for each bill
- If net = 0, bill is settled and excluded
- Bill types (New Ref, Agst Ref) are for summing, not filtering

---

## 📌 Previous Release

**v1.9.0** - Bill-wise Report Tally Arrangement and PDF Export (January 21, 2026)

---

## 🔗 Links

- **Repository:** https://github.com/ganeshchavan786/TallyInsightPlus
- **Tag:** https://github.com/ganeshchavan786/TallyInsightPlus/releases/tag/v2.0.0
- **Commit:** https://github.com/ganeshchavan786/TallyInsightPlus/commit/814a776
- **Documentation:** TallyInsight/OUTSTANDING_REPORTS_DOCUMENTATION.md

---

## 👥 Contributors

- Ganesh Chavan (@ganeshchavan786)
- AI Assistant (Cascade/Windsurf)

---

## 🎉 Conclusion

This release represents a **major milestone** in achieving 100% accuracy with Tally ERP for Outstanding Reports. The fix involved deep understanding of database sign conventions, proper deduplication logic, and Tally's bill settlement logic.

**Status:** ✅ Production Ready - 100% Tally Match Verified

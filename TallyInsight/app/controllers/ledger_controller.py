"""
Ledger Controller
Handles ledger report API endpoints (Ledger Report, Ledger Billwise)

================================================================================
DEVELOPER NOTES
================================================================================
File: ledger_controller.py
Purpose: Handle ledger statement and bill-wise report queries
Prefix: /api/data

BUSINESS LOGIC:
---------------
1. Ledger Report (/ledger-report):
   - Shows ledger statement like Tally's Ledger Vouchers
   - Columns: date, voucher_type, voucher_no, particulars, debit, credit, balance
   - Running balance calculated: opening + cumulative transactions
   - Used in: Ledger statement page
   
2. Ledger Bill-wise (/ledger-billwise):
   - Shows pending bills for a specific ledger (party)
   - Columns: bill_name, bill_date, voucher_type, opening, pending
   - On Account = Bills Total - Ledger Opening Balance
   - Used in: Bill-wise tab in Voucher Report page

CALCULATION FORMULAS:
---------------------
- Running Balance = Opening Balance + SUM(Debit) - SUM(Credit)
- On Account = Total of all bills - Ledger's opening balance
- Pending = Original bill amount - Payments received

TALLY CONCEPTS:
---------------
- Ledger Statement: Chronological list of all transactions
- Bill-wise: Tracks individual invoices and their payments
- On Account: Amount not allocated to any specific bill

IMPORTANT:
----------
- Debit = Positive amount (we receive/asset increases)
- Credit = Negative amount (we pay/liability increases)
- For Sundry Debtors: Debit = Sales, Credit = Receipt
- For Sundry Creditors: Credit = Purchase, Debit = Payment

DEPENDENCIES:
-------------
- mst_ledger: Ledger master with opening balance
- trn_accounting: Transaction entries
- trn_bill: Bill allocations
- trn_voucher: Voucher headers for date/type
================================================================================
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import Response
from typing import Optional

from ..services.database_service import database_service
from ..services.pdf_service import pdf_service
from ..utils.logger import logger

router = APIRouter()


@router.get("/ledger-report")
async def get_ledger_report(
    ledger: str = Query(..., description="Ledger name"),
    company: Optional[str] = None,
    from_date: Optional[str] = Query(default=None, description="From date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(default=None, description="To date (YYYY-MM-DD)")
):
    """Get ledger report with transactions like Tally"""
    try:
        await database_service.connect()
        
        # Get ledger info with parent group's is_deemedpositive
        ledger_query = """
            SELECT l.opening_balance, l.parent, COALESCE(g.is_deemedpositive, 0) as is_deemed_positive
            FROM mst_ledger l
            LEFT JOIN mst_group g ON l.parent = g.name AND l._company = g._company
            WHERE l.name = ?
        """
        ledger_params = [ledger]
        if company:
            ledger_query += " AND l._company = ?"
            ledger_params.append(company)
        
        ledger_result = await database_service.fetch_all(ledger_query, tuple(ledger_params))
        if not ledger_result:
            return {"ledger": ledger, "opening_balance": 0, "transactions": [], "error": "Ledger not found"}
        
        base_opening_balance = ledger_result[0]['opening_balance'] or 0
        is_deemed_positive = ledger_result[0]['is_deemed_positive'] or 0
        
        # Calculate Opening Balance for selected date range
        # Opening = Base Opening + SUM(all transactions BEFORE from_date)
        opening_balance = base_opening_balance
        
        if from_date:
            # Get sum of transactions before from_date
            pre_txn_query = """
                SELECT COALESCE(SUM(a.amount), 0) as pre_total
                FROM trn_accounting a
                JOIN trn_voucher v ON a.guid = v.guid
                WHERE a.ledger = ? AND v.date < ?
            """
            pre_params = [ledger, from_date]
            if company:
                pre_txn_query += " AND a._company = ?"
                pre_params.append(company)
            
            pre_result = await database_service.fetch_all(pre_txn_query, tuple(pre_params))
            pre_total = pre_result[0]['pre_total'] if pre_result else 0
            
            # For IsDeemedPositive (Sundry Debtors): 
            #   - Debit (Sales) stored as negative → increases balance
            #   - Credit (Receipt) stored as positive → decreases balance
            #   - So: opening = base + pre_total (because pre_total is already negative for debits)
            # For non-IsDeemedPositive (Sundry Creditors):
            #   - Credit (Purchase) stored as negative → increases balance
            #   - Debit (Payment) stored as positive → decreases balance
            if is_deemed_positive:
                opening_balance = base_opening_balance + (pre_total or 0)
            else:
                opening_balance = base_opening_balance - (pre_total or 0)
        
        # Get transactions from trn_accounting
        # For IsDeemedPositive groups (Sundry Debtors, Assets):
        #   - Negative amount in DB = Debit (Party Dr)
        #   - Positive amount in DB = Credit (Party Cr)
        # For IsDeemedPositive = 0 (Sundry Creditors, Liabilities):
        #   - Positive amount in DB = Credit
        #   - Negative amount in DB = Debit
        if is_deemed_positive:
            debit_case = "CASE WHEN a.amount < 0 THEN ABS(a.amount) ELSE 0 END"
            credit_case = "CASE WHEN a.amount > 0 THEN a.amount ELSE 0 END"
        else:
            debit_case = "CASE WHEN a.amount > 0 THEN a.amount ELSE 0 END"
            credit_case = "CASE WHEN a.amount < 0 THEN ABS(a.amount) ELSE 0 END"
        
        txn_query = f"""
            SELECT 
                v.date,
                v.voucher_type,
                v.voucher_number as voucher_no,
                a.amount,
                {debit_case} as debit,
                {credit_case} as credit,
                v.narration,
                v.party_name as particulars
            FROM trn_accounting a
            JOIN trn_voucher v ON a.guid = v.guid
            WHERE a.ledger = ?
        """
        params = [ledger]
        
        if company:
            txn_query += " AND a._company = ?"
            params.append(company)
        
        if from_date:
            txn_query += " AND v.date >= ?"
            params.append(from_date)
        
        if to_date:
            txn_query += " AND v.date <= ?"
            params.append(to_date)
        
        txn_query += " ORDER BY v.date, v.voucher_number"
        
        transactions = await database_service.fetch_all(txn_query, tuple(params))
        
        # Calculate totals
        total_debit = sum(t['debit'] or 0 for t in transactions)
        total_credit = sum(t['credit'] or 0 for t in transactions)
        # ============================================================
        # DEVELOPER NOTE: DO NOT CHANGE THIS FORMULA
        # Closing = Opening - Debit + Credit
        # For Sundry Debtors (IsDeemedPositive=1):
        #   - Debit = Receipt (पैसे मिळाले) → balance कमी होतो
        #   - Credit = Sales → balance वाढतो
        # Example: Opening=2124, Debit=2124, Credit=0 → Closing=0
        # ============================================================
        closing_balance = opening_balance - total_debit + total_credit
        
        return {
            "ledger": ledger,
            "opening_balance": opening_balance or 0,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "closing_balance": closing_balance,
            "transactions": [dict(t) for t in transactions]
        }
    except Exception as e:
        logger.error(f"Failed to get ledger report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ledger-billwise")
async def get_ledger_billwise(
    ledger: str = Query(..., description="Ledger name"),
    company: Optional[str] = None,
    from_date: Optional[str] = Query(default=None, description="From date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(default=None, description="To date (YYYY-MM-DD)")
):
    """Get pending bills for a specific ledger like Tally's Pending Bills view"""
    try:
        await database_service.connect()
        
        ref_date_sql = f"'{to_date}'" if to_date else "date('now')"
        
        # ============================================================
        # BILL CREDIT PERIOD LOGIC:
        # - bill_credit_period can be: "31-May-22" (date) or "45 Days" (days)
        # - If date format (contains '-' and no 'Days'): Due Date = that date directly
        # - If days format (contains 'Days'): Due Date = Bill Date + X days
        # - Extract number from "45 Days" using CAST after removing ' Days'
        # ============================================================
        query = f"""
            WITH all_bills AS (
                -- Opening bill allocations
                SELECT 
                    o.name as bill_no,
                    o.bill_date,
                    o.bill_credit_period as credit_period_raw,
                    o.opening_balance as amount,
                    o.opening_balance as opening_amount,
                    'Opening' as source,
                    o._company
                FROM mst_opening_bill_allocation o
                WHERE o.ledger = ? AND o.name != ''
                
                UNION ALL
                
                -- Transaction bills
                SELECT 
                    b.name as bill_no,
                    v.date as bill_date,
                    b.bill_credit_period as credit_period_raw,
                    CASE 
                        WHEN b.billtype = 'New Ref' THEN ABS(b.amount)
                        WHEN b.billtype = 'Agst Ref' THEN -ABS(b.amount)
                        ELSE 0 
                    END as amount,
                    CASE WHEN b.billtype = 'New Ref' THEN ABS(b.amount) ELSE 0 END as opening_amount,
                    v.voucher_type as source,
                    b._company
                FROM trn_bill b
                JOIN trn_voucher v ON b.guid = v.guid
                WHERE b.ledger = ? AND b.name != '' AND b.billtype IN ('New Ref', 'Agst Ref')
            )
            SELECT 
                bill_no,
                MIN(bill_date) as bill_date,
                MAX(credit_period_raw) as credit_period_raw,
                SUM(opening_amount) as opening_amount,
                SUM(amount) as pending_amount,
                -- Due Date Logic: If contains 'Days' -> Bill Date + X days, else use as date directly
                CASE 
                    WHEN MAX(credit_period_raw) LIKE '%Days%' THEN 
                        date(MIN(bill_date), '+' || CAST(REPLACE(REPLACE(MAX(credit_period_raw), ' Days', ''), ' ', '') AS INTEGER) || ' days')
                    WHEN MAX(credit_period_raw) LIKE '%-%' THEN 
                        -- Convert Tally date format (31-May-22) to ISO format (2022-05-31)
                        date(
                            '20' || SUBSTR(MAX(credit_period_raw), -2) || '-' ||
                            CASE SUBSTR(MAX(credit_period_raw), INSTR(MAX(credit_period_raw), '-') + 1, 3)
                                WHEN 'Jan' THEN '01' WHEN 'Feb' THEN '02' WHEN 'Mar' THEN '03'
                                WHEN 'Apr' THEN '04' WHEN 'May' THEN '05' WHEN 'Jun' THEN '06'
                                WHEN 'Jul' THEN '07' WHEN 'Aug' THEN '08' WHEN 'Sep' THEN '09'
                                WHEN 'Oct' THEN '10' WHEN 'Nov' THEN '11' WHEN 'Dec' THEN '12'
                                ELSE '01'
                            END || '-' ||
                            SUBSTR('0' || SUBSTR(MAX(credit_period_raw), 1, INSTR(MAX(credit_period_raw), '-') - 1), -2)
                        )
                    ELSE MIN(bill_date)
                END as due_date,
                CAST(julianday({ref_date_sql}) - julianday(
                    CASE 
                        WHEN MAX(credit_period_raw) LIKE '%Days%' THEN 
                            date(MIN(bill_date), '+' || CAST(REPLACE(REPLACE(MAX(credit_period_raw), ' Days', ''), ' ', '') AS INTEGER) || ' days')
                        WHEN MAX(credit_period_raw) LIKE '%-%' THEN 
                            date(
                                '20' || SUBSTR(MAX(credit_period_raw), -2) || '-' ||
                                CASE SUBSTR(MAX(credit_period_raw), INSTR(MAX(credit_period_raw), '-') + 1, 3)
                                    WHEN 'Jan' THEN '01' WHEN 'Feb' THEN '02' WHEN 'Mar' THEN '03'
                                    WHEN 'Apr' THEN '04' WHEN 'May' THEN '05' WHEN 'Jun' THEN '06'
                                    WHEN 'Jul' THEN '07' WHEN 'Aug' THEN '08' WHEN 'Sep' THEN '09'
                                    WHEN 'Oct' THEN '10' WHEN 'Nov' THEN '11' WHEN 'Dec' THEN '12'
                                    ELSE '01'
                                END || '-' ||
                                SUBSTR('0' || SUBSTR(MAX(credit_period_raw), 1, INSTR(MAX(credit_period_raw), '-') - 1), -2)
                            )
                        ELSE MIN(bill_date)
                    END
                ) AS INTEGER) as overdue_days,
                GROUP_CONCAT(DISTINCT source) as source
            FROM all_bills
            WHERE 1=1
        """
        params = [ledger, ledger]
        
        if company:
            query += " AND _company = ?"
            params.append(company)
        
        query += " GROUP BY bill_no HAVING pending_amount != 0 ORDER BY bill_date"
        
        bills = await database_service.fetch_all(query, tuple(params))
        
        # Calculate bills sub total (Opening Amount and Pending Amount)
        bills_total_opening = sum(b['opening_amount'] or 0 for b in bills)
        bills_total_pending = sum(b['pending_amount'] or 0 for b in bills)
        
        # ============================================================
        # ON ACCOUNT LOGIC:
        # On Account = Vouchers where billtype = 'On Account'
        # These are payments/receipts NOT linked to any specific bill
        # ============================================================
        on_account_query = """
            SELECT 
                v.date as voucher_date,
                v.voucher_number as voucher_no,
                v.voucher_type,
                ABS(b.amount) as amount
            FROM trn_bill b
            JOIN trn_voucher v ON b.guid = v.guid
            WHERE b.ledger = ? AND b.billtype = 'On Account'
        """
        on_account_params = [ledger]
        if company:
            on_account_query += " AND b._company = ?"
            on_account_params.append(company)
        on_account_query += " ORDER BY v.date"
        
        on_account_vouchers = await database_service.fetch_all(on_account_query, tuple(on_account_params))
        
        # Calculate On Account total
        on_account_total = sum(v['amount'] or 0 for v in on_account_vouchers)
        
        # Grand Total = Bills Sub Total + On Account
        grand_total_opening = bills_total_opening + on_account_total
        grand_total_pending = bills_total_pending + on_account_total
        
        return {
            "ledger": ledger,
            "bills": [dict(b) for b in bills],
            "bills_sub_total_opening": bills_total_opening,
            "bills_sub_total_pending": bills_total_pending,
            "on_account_vouchers": [dict(v) for v in on_account_vouchers],
            "on_account_total": on_account_total,
            "grand_total_opening": grand_total_opening,
            "grand_total_pending": grand_total_pending,
            "total_bills": len(bills)
        }
    except Exception as e:
        logger.error(f"Failed to get ledger billwise: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ledger-billwise/pdf")
async def get_ledger_billwise_pdf(
    ledger: str = Query(..., description="Ledger name"),
    company: Optional[str] = None,
    from_date: Optional[str] = Query(default=None, description="From date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(default=None, description="To date (YYYY-MM-DD)")
):
    """Generate Bill-wise PDF matching Tally format"""
    try:
        await database_service.connect()
        
        # Get billwise data using existing function logic
        ref_date_sql = f"'{to_date}'" if to_date else "date('now')"
        
        query = f"""
            WITH all_bills AS (
                SELECT 
                    o.name as bill_no,
                    o.bill_date,
                    o.bill_credit_period as credit_period_raw,
                    o.opening_balance as amount,
                    o.opening_balance as opening_amount,
                    'Opening' as source,
                    o._company
                FROM mst_opening_bill_allocation o
                WHERE o.ledger = ? AND o.name != ''
                
                UNION ALL
                
                SELECT 
                    b.name as bill_no,
                    v.date as bill_date,
                    b.bill_credit_period as credit_period_raw,
                    CASE 
                        WHEN b.billtype = 'New Ref' THEN ABS(b.amount)
                        WHEN b.billtype = 'Agst Ref' THEN -ABS(b.amount)
                        ELSE 0 
                    END as amount,
                    CASE WHEN b.billtype = 'New Ref' THEN ABS(b.amount) ELSE 0 END as opening_amount,
                    v.voucher_type as source,
                    b._company
                FROM trn_bill b
                JOIN trn_voucher v ON b.guid = v.guid
                WHERE b.ledger = ? AND b.name != '' AND b.billtype IN ('New Ref', 'Agst Ref')
            )
            SELECT 
                bill_no,
                MIN(bill_date) as bill_date,
                MAX(credit_period_raw) as credit_period_raw,
                SUM(opening_amount) as opening_amount,
                SUM(amount) as pending_amount,
                CASE 
                    WHEN MAX(credit_period_raw) LIKE '%Days%' THEN 
                        date(MIN(bill_date), '+' || CAST(REPLACE(REPLACE(MAX(credit_period_raw), ' Days', ''), ' ', '') AS INTEGER) || ' days')
                    WHEN MAX(credit_period_raw) LIKE '%-%' THEN 
                        date(
                            '20' || SUBSTR(MAX(credit_period_raw), -2) || '-' ||
                            CASE SUBSTR(MAX(credit_period_raw), INSTR(MAX(credit_period_raw), '-') + 1, 3)
                                WHEN 'Jan' THEN '01' WHEN 'Feb' THEN '02' WHEN 'Mar' THEN '03'
                                WHEN 'Apr' THEN '04' WHEN 'May' THEN '05' WHEN 'Jun' THEN '06'
                                WHEN 'Jul' THEN '07' WHEN 'Aug' THEN '08' WHEN 'Sep' THEN '09'
                                WHEN 'Oct' THEN '10' WHEN 'Nov' THEN '11' WHEN 'Dec' THEN '12'
                                ELSE '01'
                            END || '-' ||
                            SUBSTR('0' || SUBSTR(MAX(credit_period_raw), 1, INSTR(MAX(credit_period_raw), '-') - 1), -2)
                        )
                    ELSE MIN(bill_date)
                END as due_date,
                CAST(julianday({ref_date_sql}) - julianday(
                    CASE 
                        WHEN MAX(credit_period_raw) LIKE '%Days%' THEN 
                            date(MIN(bill_date), '+' || CAST(REPLACE(REPLACE(MAX(credit_period_raw), ' Days', ''), ' ', '') AS INTEGER) || ' days')
                        WHEN MAX(credit_period_raw) LIKE '%-%' THEN 
                            date(
                                '20' || SUBSTR(MAX(credit_period_raw), -2) || '-' ||
                                CASE SUBSTR(MAX(credit_period_raw), INSTR(MAX(credit_period_raw), '-') + 1, 3)
                                    WHEN 'Jan' THEN '01' WHEN 'Feb' THEN '02' WHEN 'Mar' THEN '03'
                                    WHEN 'Apr' THEN '04' WHEN 'May' THEN '05' WHEN 'Jun' THEN '06'
                                    WHEN 'Jul' THEN '07' WHEN 'Aug' THEN '08' WHEN 'Sep' THEN '09'
                                    WHEN 'Oct' THEN '10' WHEN 'Nov' THEN '11' WHEN 'Dec' THEN '12'
                                    ELSE '01'
                                END || '-' ||
                                SUBSTR('0' || SUBSTR(MAX(credit_period_raw), 1, INSTR(MAX(credit_period_raw), '-') - 1), -2)
                            )
                        ELSE MIN(bill_date)
                    END
                ) AS INTEGER) as overdue_days
            FROM all_bills
            WHERE 1=1
        """
        params = [ledger, ledger]
        
        if company:
            query += " AND _company = ?"
            params.append(company)
        
        query += " GROUP BY bill_no HAVING pending_amount != 0 ORDER BY bill_date"
        
        bills = await database_service.fetch_all(query, tuple(params))
        
        # Calculate totals
        bills_total_opening = sum(b['opening_amount'] or 0 for b in bills)
        bills_total_pending = sum(b['pending_amount'] or 0 for b in bills)
        
        # On Account vouchers
        on_account_query = """
            SELECT 
                v.date as voucher_date,
                v.voucher_number as voucher_no,
                v.voucher_type,
                ABS(b.amount) as amount
            FROM trn_bill b
            JOIN trn_voucher v ON b.guid = v.guid
            WHERE b.ledger = ? AND b.billtype = 'On Account'
        """
        on_account_params = [ledger]
        if company:
            on_account_query += " AND b._company = ?"
            on_account_params.append(company)
        on_account_query += " ORDER BY v.date"
        
        on_account_vouchers = await database_service.fetch_all(on_account_query, tuple(on_account_params))
        on_account_total = sum(v['amount'] or 0 for v in on_account_vouchers)
        
        grand_total_opening = bills_total_opening + on_account_total
        grand_total_pending = bills_total_pending + on_account_total
        
        # Get company info
        company_query = "SELECT name, address, state, pincode, email, cin FROM mst_company WHERE _company = ?"
        company_result = await database_service.fetch_all(company_query, (company,))
        
        if company_result:
            c = company_result[0]
            company_address = c['address'] or ''
            if c['state']:
                company_address += f"\n{c['state']}"
            if c['pincode']:
                company_address += f" - {c['pincode']}"
            company_info = {
                "name": c['name'] or company,
                "address": company_address,
                "cin": c['cin'] or "",
                "email": c['email'] or ""
            }
        else:
            company_info = {"name": company, "address": "", "cin": "", "email": ""}
        
        ledger_info = {"name": ledger}
        
        # Generate PDF
        from ..services.pdf_service import pdf_service
        pdf_bytes = pdf_service.generate_billwise_pdf(
            company_info=company_info,
            ledger_info=ledger_info,
            bills=[dict(b) for b in bills],
            bills_sub_total_opening=bills_total_opening,
            bills_sub_total_pending=bills_total_pending,
            on_account_vouchers=[dict(v) for v in on_account_vouchers],
            on_account_total=on_account_total,
            grand_total_opening=grand_total_opening,
            grand_total_pending=grand_total_pending,
            from_date=from_date,
            to_date=to_date
        )
        
        # Return PDF response
        from fastapi.responses import Response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Billwise_{ledger.replace(' ', '_')}.pdf"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to generate billwise PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ledger-report/pdf")
async def get_ledger_report_pdf(
    ledger: str = Query(..., description="Ledger name"),
    company: Optional[str] = None,
    from_date: Optional[str] = Query(default=None, description="From date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(default=None, description="To date (YYYY-MM-DD)")
):
    """Generate Ledger Report PDF matching Tally format"""
    try:
        await database_service.connect()
        
        # Get ledger info with parent group's is_deemedpositive
        ledger_query = """
            SELECT l.name, l.opening_balance, l.parent, l.mailing_address, l.mailing_state, l.mailing_pincode,
                   COALESCE(g.is_deemedpositive, 0) as is_deemed_positive
            FROM mst_ledger l
            LEFT JOIN mst_group g ON l.parent = g.name AND l._company = g._company
            WHERE l.name = ?
        """
        ledger_params = [ledger]
        if company:
            ledger_query += " AND l._company = ?"
            ledger_params.append(company)
        
        ledger_result = await database_service.fetch_all(ledger_query, tuple(ledger_params))
        if not ledger_result:
            raise HTTPException(status_code=404, detail="Ledger not found")
        
        ledger_data = ledger_result[0]
        base_opening_balance = ledger_data['opening_balance'] or 0
        is_deemed_positive = ledger_data['is_deemed_positive'] or 0
        
        # Calculate Opening Balance for selected date range
        # Opening = Base Opening + SUM(all transactions BEFORE from_date)
        opening_balance = base_opening_balance
        
        if from_date:
            pre_txn_query = """
                SELECT COALESCE(SUM(a.amount), 0) as pre_total
                FROM trn_accounting a
                JOIN trn_voucher v ON a.guid = v.guid
                WHERE a.ledger = ? AND v.date < ?
            """
            pre_params = [ledger, from_date]
            if company:
                pre_txn_query += " AND a._company = ?"
                pre_params.append(company)
            
            pre_result = await database_service.fetch_all(pre_txn_query, tuple(pre_params))
            pre_total = pre_result[0]['pre_total'] if pre_result else 0
            
            if is_deemed_positive:
                opening_balance = base_opening_balance + (pre_total or 0)
            else:
                opening_balance = base_opening_balance - (pre_total or 0)
        
        # Get company info from mst_company table (synced from Tally)
        company_query = "SELECT name, address, state, pincode, email, cin FROM mst_company WHERE _company = ?"
        company_result = await database_service.fetch_all(company_query, (company,))
        
        if company_result:
            c = company_result[0]
            company_address = c['address'] or ''
            if c['state']:
                company_address += f"\n{c['state']}"
            if c['pincode']:
                company_address += f" - {c['pincode']}"
            company_info = {
                "name": c['name'] or company,
                "address": company_address,
                "cin": c['cin'] or "",
                "email": c['email'] or ""
            }
        else:
            # Fallback if company not synced yet
            company_info = {
                "name": company or "Company",
                "address": "",
                "cin": "",
                "email": ""
            }
        
        # Ledger info for PDF header
        ledger_address = ledger_data.get('mailing_address') or ''
        if ledger_data.get('mailing_state'):
            ledger_address += f"\n{ledger_data['mailing_state']}"
        if ledger_data.get('mailing_pincode'):
            ledger_address += f" - {ledger_data['mailing_pincode']}"
        
        ledger_info = {
            "name": ledger_data['name'],
            "address": ledger_address
        }
        
        # Get transactions
        txn_query = """
            SELECT 
                v.date,
                v.voucher_type,
                v.voucher_number as voucher_no,
                a.amount,
                v.party_name as particulars
            FROM trn_accounting a
            JOIN trn_voucher v ON a.guid = v.guid
            WHERE a.ledger = ?
        """
        params = [ledger]
        
        if company:
            txn_query += " AND a._company = ?"
            params.append(company)
        
        if from_date:
            txn_query += " AND v.date >= ?"
            params.append(from_date)
        
        if to_date:
            txn_query += " AND v.date <= ?"
            params.append(to_date)
        
        txn_query += " ORDER BY v.date, v.voucher_number"
        
        transactions = await database_service.fetch_all(txn_query, tuple(params))
        
        # Generate PDF
        pdf_bytes = pdf_service.generate_ledger_pdf(
            company_info=company_info,
            ledger_info=ledger_info,
            opening_balance=opening_balance,
            transactions=[dict(t) for t in transactions],
            is_deemed_positive=is_deemed_positive,
            from_date=from_date,
            to_date=to_date
        )
        
        # Return PDF response
        filename = f"Ledger_{ledger.replace(' ', '_')}_{from_date or 'all'}_{to_date or 'dates'}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate ledger PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

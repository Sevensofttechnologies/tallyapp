"""
PDF Generation Service
Generates Tally-style Ledger Report PDFs using FPDF2
"""
from fpdf import FPDF
from typing import List, Dict, Any, Optional
from io import BytesIO
from datetime import datetime

from ..utils.logger import logger


class LedgerPDF(FPDF):
    """Custom PDF class for Ledger Reports"""
    
    def __init__(self, company_info: Dict, ledger_info: Dict, date_range: str):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.company_info = company_info
        self.ledger_info = ledger_info
        self.date_range = date_range
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        """Page header with company and ledger info"""
        # Company Header
        self.set_font('Courier', 'B', 12)
        self.cell(0, 5, self.company_info.get('name', ''), align='C', new_x='LMARGIN', new_y='NEXT')
        
        self.set_font('Courier', '', 9)
        if self.company_info.get('address'):
            for line in self.company_info['address'].split('\n'):
                self.cell(0, 4, line.strip(), align='C', new_x='LMARGIN', new_y='NEXT')
        
        if self.company_info.get('cin'):
            self.cell(0, 4, f"CIN: {self.company_info['cin']}", align='C', new_x='LMARGIN', new_y='NEXT')
        
        if self.company_info.get('email'):
            self.cell(0, 4, f"E-Mail : {self.company_info['email']}", align='C', new_x='LMARGIN', new_y='NEXT')
        
        self.ln(3)
        
        # Ledger Header
        self.set_font('Courier', 'B', 11)
        self.cell(0, 5, self.ledger_info.get('name', ''), align='C', new_x='LMARGIN', new_y='NEXT')
        
        self.set_font('Courier', '', 9)
        self.cell(0, 4, 'Ledger Account', align='C', new_x='LMARGIN', new_y='NEXT')
        
        if self.ledger_info.get('address'):
            for line in self.ledger_info['address'].split('\n'):
                self.cell(0, 4, line.strip(), align='C', new_x='LMARGIN', new_y='NEXT')
        
        self.ln(3)
        
        # Date Range
        self.set_font('Courier', '', 9)
        self.cell(0, 4, self.date_range, align='C', new_x='LMARGIN', new_y='NEXT')
        
        self.ln(2)
        
        # Page number
        self.set_font('Courier', '', 8)
        self.cell(0, 4, f'Page {self.page_no()}', align='R', new_x='LMARGIN', new_y='NEXT')
        
        # Table Header
        self.set_font('Courier', '', 9)
        self.cell(25, 5, 'Date', border='B')
        self.cell(55, 5, 'Particulars', border='B')
        self.cell(25, 5, 'Vch Type', border='B')
        self.cell(30, 5, 'Vch No.', border='B')
        self.cell(25, 5, 'Debit', border='B', align='R')
        self.cell(25, 5, 'Credit', border='B', align='R')
        self.ln()
    
    def footer(self):
        """Page footer"""
        self.set_y(-15)
        self.set_font('Courier', '', 8)
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%d-%b-%Y %H:%M")}', align='C')


class BillwisePDF(FPDF):
    """Custom PDF class for Bill-wise Reports (Pending Bills)"""
    
    def __init__(self, company_info: Dict, ledger_info: Dict, date_range: str):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.company_info = company_info
        self.ledger_info = ledger_info
        self.date_range = date_range
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        """Page header with company and ledger info - Tally Bill-wise format"""
        # Company Header
        self.set_font('Courier', 'B', 12)
        self.cell(0, 5, self.company_info.get('name', ''), align='C', new_x='LMARGIN', new_y='NEXT')
        
        self.set_font('Courier', '', 9)
        if self.company_info.get('address'):
            for line in self.company_info['address'].split('\n'):
                self.cell(0, 4, line.strip(), align='C', new_x='LMARGIN', new_y='NEXT')
        
        if self.company_info.get('cin'):
            self.cell(0, 4, f"CIN: {self.company_info['cin']}", align='C', new_x='LMARGIN', new_y='NEXT')
        
        if self.company_info.get('email'):
            self.cell(0, 4, f"E-Mail : {self.company_info['email']}", align='C', new_x='LMARGIN', new_y='NEXT')
        
        self.ln(3)
        
        # Ledger Header
        self.set_font('Courier', 'B', 11)
        self.cell(0, 5, self.ledger_info.get('name', ''), align='C', new_x='LMARGIN', new_y='NEXT')
        
        self.set_font('Courier', '', 9)
        self.cell(0, 4, 'Bill-wise Details', align='C', new_x='LMARGIN', new_y='NEXT')
        
        # Date Range
        self.cell(0, 4, self.date_range, align='C', new_x='LMARGIN', new_y='NEXT')
        
        # Pending Bills subtitle
        self.set_font('Courier', 'B', 9)
        self.cell(0, 4, 'Pending Bills', align='C', new_x='LMARGIN', new_y='NEXT')
        
        self.ln(2)
        
        # Page number
        self.set_font('Courier', '', 8)
        self.cell(0, 4, f'Page {self.page_no()}', align='R', new_x='LMARGIN', new_y='NEXT')
        
        # Table Header - Bill-wise columns
        self.set_font('Courier', '', 9)
        self.cell(22, 5, 'Date', border='B')
        self.cell(40, 5, 'Ref. No.', border='B')
        self.cell(30, 5, 'Opening', border='B', align='R')
        self.cell(30, 5, 'Pending', border='B', align='R')
        self.cell(22, 5, 'Due on', border='B')
        self.cell(22, 5, 'Overdue', border='B', align='R')
        self.ln()
    
    def footer(self):
        """Page footer"""
        self.set_y(-15)
        self.set_font('Courier', '', 8)
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%d-%b-%Y %H:%M")}', align='C')


class PDFService:
    """Service for generating PDF reports"""
    
    def generate_ledger_pdf(
        self,
        company_info: Dict,
        ledger_info: Dict,
        opening_balance: float,
        transactions: List[Dict],
        is_deemed_positive: int,
        from_date: str = None,
        to_date: str = None
    ) -> bytes:
        """Generate Ledger Report PDF matching Tally format"""
        
        # Format date range
        if from_date and to_date:
            date_range = f"{self._format_date(from_date)} to {self._format_date(to_date)}"
        else:
            date_range = "All Dates"
        
        # Create PDF
        pdf = LedgerPDF(company_info, ledger_info, date_range)
        pdf.add_page()
        pdf.set_font('Courier', '', 9)
        
        # Opening Balance Row
        pdf.cell(25, 5, '')
        pdf.set_font('Courier', 'B', 9)
        pdf.cell(55, 5, 'Opening Balance')
        pdf.set_font('Courier', '', 9)
        pdf.cell(25, 5, '')
        pdf.cell(30, 5, '')
        
        if opening_balance >= 0:
            pdf.cell(25, 5, '', align='R')
            pdf.cell(25, 5, self._format_amount(opening_balance), align='R')
        else:
            pdf.cell(25, 5, self._format_amount(abs(opening_balance)), align='R')
            pdf.cell(25, 5, '', align='R')
        pdf.ln()
        
        # Transaction Rows
        balance = opening_balance
        total_debit = 0
        total_credit = 0
        
        for txn in transactions:
            amount = txn.get('amount', 0) or 0
            
            # Calculate debit/credit based on is_deemed_positive
            if is_deemed_positive:
                if amount < 0:
                    debit = abs(amount)
                    credit = 0
                else:
                    debit = 0
                    credit = amount
            else:
                if amount > 0:
                    debit = amount
                    credit = 0
                else:
                    debit = 0
                    credit = abs(amount)
            
            # Running balance
            balance = balance - debit + credit
            total_debit += debit
            total_credit += credit
            
            # By/To prefix
            prefix = 'To' if debit > 0 else 'By'
            date_str = self._format_date(txn.get('date', ''))
            
            pdf.cell(25, 5, f"{date_str} {prefix}")
            pdf.cell(55, 5, (txn.get('particulars', '') or '-')[:30])
            pdf.cell(25, 5, (txn.get('voucher_type', '') or '-')[:12])
            pdf.cell(30, 5, (txn.get('voucher_no', '') or '-')[:15])
            pdf.cell(25, 5, self._format_amount(debit) if debit > 0 else '', align='R')
            pdf.cell(25, 5, self._format_amount(credit) if credit > 0 else '', align='R')
            pdf.ln()
        
        # Subtotal line
        pdf.ln(2)
        pdf.set_draw_color(0, 0, 0)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(1)
        
        # Current Total Row
        pdf.set_font('Courier', 'B', 9)
        pdf.cell(135, 5, 'Current Total :', align='R')
        pdf.cell(25, 5, self._format_amount(total_debit), align='R')
        pdf.cell(25, 5, self._format_amount(total_credit), align='R')
        pdf.ln()
        
        # ============================================================
        # DEVELOPER NOTE: DO NOT CHANGE THIS FORMULA
        # Closing = Opening - Debit + Credit
        # For Sundry Debtors: Debit = Receipt (balance कमी), Credit = Sales (balance वाढतो)
        # Example: Opening=2124, Debit=2124, Credit=0 → Closing=0
        # ============================================================
        closing_balance = opening_balance - total_debit + total_credit
        closing_in_debit = closing_balance < 0
        
        pdf.cell(135, 5, 'Closing Balance :', align='R')
        if closing_in_debit:
            pdf.cell(25, 5, self._format_amount(abs(closing_balance)), align='R')
            pdf.cell(25, 5, '', align='R')
        else:
            pdf.cell(25, 5, '', align='R')
            pdf.cell(25, 5, self._format_amount(abs(closing_balance)), align='R')
        pdf.ln()
        
        # Bottom line
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        
        # Return PDF bytes
        return bytes(pdf.output())
    
    def generate_billwise_pdf(
        self,
        company_info: Dict,
        ledger_info: Dict,
        bills: List[Dict],
        bills_sub_total_opening: float,
        bills_sub_total_pending: float,
        on_account_vouchers: List[Dict],
        on_account_total: float,
        grand_total_opening: float,
        grand_total_pending: float,
        from_date: str = None,
        to_date: str = None
    ) -> bytes:
        """Generate Bill-wise PDF matching Tally format"""
        
        # Format date range
        if from_date and to_date:
            date_range = f"{self._format_date(from_date)} to {self._format_date(to_date)}"
        else:
            date_range = "All Dates"
        
        # Create PDF
        pdf = BillwisePDF(company_info, ledger_info, date_range)
        pdf.add_page()
        pdf.set_font('Courier', '', 9)
        
        # Bill Rows
        for bill in bills:
            date_str = self._format_date(bill.get('bill_date', ''))
            due_date_str = self._format_date(bill.get('due_date', '') or bill.get('bill_date', ''))
            opening_amt = bill.get('opening_amount', 0) or 0
            pending_amt = bill.get('pending_amount', 0) or 0
            overdue_days = bill.get('overdue_days', 0) or 0
            
            pdf.cell(22, 5, date_str)
            pdf.cell(40, 5, (bill.get('bill_no', '') or '-')[:20])
            pdf.cell(30, 5, f"{self._format_amount(opening_amt)} Dr", align='R')
            pdf.cell(30, 5, f"{self._format_amount(pending_amt)} Dr", align='R')
            pdf.cell(22, 5, due_date_str)
            pdf.cell(22, 5, str(overdue_days) if overdue_days > 0 else '', align='R')
            pdf.ln()
        
        # Sub Total Row
        pdf.ln(1)
        pdf.set_font('Courier', 'B', 9)
        pdf.cell(22, 5, '')
        pdf.cell(40, 5, 'Sub Total')
        pdf.cell(30, 5, f"{self._format_amount(bills_sub_total_opening)} Dr", align='R')
        pdf.cell(30, 5, f"{self._format_amount(bills_sub_total_pending)} Dr", align='R')
        pdf.cell(22, 5, '')
        pdf.cell(22, 5, '', align='R')
        pdf.ln()
        
        # On Account Section
        if on_account_vouchers or on_account_total > 0:
            pdf.set_font('Courier', '', 9)
            for voucher in on_account_vouchers:
                date_str = self._format_date(voucher.get('voucher_date', ''))
                voucher_desc = f"{voucher.get('voucher_type', '')} {voucher.get('voucher_no', '')}"
                amount = voucher.get('amount', 0) or 0
                
                pdf.cell(22, 5, date_str)
                pdf.cell(40, 5, 'On Account')
                pdf.cell(30, 5, f"{self._format_amount(amount)} Dr", align='R')
                pdf.cell(30, 5, f"{self._format_amount(amount)} Dr", align='R')
                pdf.cell(22, 5, '')
                pdf.cell(22, 5, '', align='R')
                pdf.ln()
        
        # Grand Total Row
        pdf.ln(1)
        pdf.set_draw_color(0, 0, 0)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(1)
        
        pdf.set_font('Courier', 'B', 9)
        pdf.cell(22, 5, '')
        pdf.cell(40, 5, '')
        pdf.cell(30, 5, f"{self._format_amount(grand_total_opening)} Dr", align='R')
        pdf.cell(30, 5, f"{self._format_amount(grand_total_pending)} Dr", align='R')
        pdf.cell(22, 5, '')
        pdf.cell(22, 5, '', align='R')
        pdf.ln()
        
        # Bottom line
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        
        # Return PDF bytes
        return bytes(pdf.output())
    
    def _format_date(self, date_str: str) -> str:
        """Format date to Tally style (d-Mon-yy)"""
        if not date_str:
            return ''
        try:
            if isinstance(date_str, str):
                date_obj = datetime.strptime(date_str[:10], '%Y-%m-%d')
            else:
                date_obj = date_str
            # Windows uses %#d, Linux/Mac uses %-d for no zero-padding
            return date_obj.strftime('%d-%b-%y')
        except:
            return str(date_str)[:10] if date_str else ''
    
    def _format_amount(self, amount: float) -> str:
        """Format amount with Indian number format"""
        if amount == 0:
            return ''
        try:
            return f"{amount:,.2f}"
        except:
            return str(amount)


# Global service instance
pdf_service = PDFService()

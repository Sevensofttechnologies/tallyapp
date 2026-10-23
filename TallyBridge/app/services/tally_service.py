"""
Tally Service - HTTP Client for TallyInsight Microservice
Handles communication between TallyBridge and TallyInsight

Features:
- Sync companies from Tally
- Fetch ledgers, vouchers, stock items
- Get reports (trial balance, P&L, balance sheet)
- Health check for TallyInsight service
"""

import os
import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..config import settings


class TallyService:
    """HTTP client for TallyInsight microservice"""
    
    def __init__(self):
        self.base_url = os.getenv("TALLY_SERVICE_URL", "http://localhost:8401")
        self.timeout = 30.0
    
    def _get_headers(self, token: str = None) -> Dict[str, str]:
        """Get request headers with optional auth token"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if TallyInsight service is running"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/health")
                if response.status_code == 200:
                    return {"status": "healthy", "data": response.json()}
                return {"status": "unhealthy", "error": f"Status {response.status_code}"}
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}
    
    # ==================== SYNC OPERATIONS ====================
    
    async def get_tally_companies(self, token: str = None) -> Dict[str, Any]:
        """Get list of companies from Tally via TallyInsight"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/companies",
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                data = response.json()
                # Extract company names from response
                companies = data.get("companies", [])
                company_names = [c.get("name", c) if isinstance(c, dict) else c for c in companies]
                return {"success": True, "companies": company_names, "data": data}
        except httpx.HTTPStatusError as e:
            return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def sync_company(
        self, 
        company_name: str, 
        sync_mode: str = "full",
        token: str = None
    ) -> Dict[str, Any]:
        """Trigger sync for a specific company"""
        try:
            # TallyInsight uses /api/sync/full or /api/sync/incremental with company as query param
            endpoint = "/api/sync/full" if sync_mode == "full" else "/api/sync/incremental"
            async with httpx.AsyncClient(timeout=300.0) as client:  # 5 min timeout for sync
                response = await client.post(
                    f"{self.base_url}{endpoint}",
                    params={"company": company_name},
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return {"success": True, "status": "started", "data": response.json()}
        except httpx.HTTPStatusError as e:
            return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_sync_status(self, token: str = None) -> Dict[str, Any]:
        """Get current sync status"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/sync/status",
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_synced_companies(self, token: str = None) -> Dict[str, Any]:
        """Get list of already synced companies from TallyInsight DB"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/synced-companies",
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                data = response.json()
                return {"success": True, "companies": data.get("companies", []), "data": data}
        except httpx.HTTPStatusError as e:
            return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== DATA FETCH OPERATIONS ====================
    
    async def get_ledgers(
        self, 
        company: str = None,
        group: str = None,
        limit: int = 100,
        offset: int = 0,
        token: str = None
    ) -> Dict[str, Any]:
        """Get ledgers from TallyInsight"""
        try:
            params = {"limit": limit, "offset": offset}
            if company:
                params["company"] = company
            if group:
                params["group"] = group
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/ledgers",
                    params=params,
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_ledger_details(
        self, 
        ledger_name: str,
        company: str = None,
        token: str = None
    ) -> Dict[str, Any]:
        """Get ledger details including transactions"""
        try:
            params = {"ledger": ledger_name}
            if company:
                params["company"] = company
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/ledger-report",
                    params=params,
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_vouchers(
        self,
        company: str = None,
        voucher_type: str = None,
        from_date: str = None,
        to_date: str = None,
        limit: int = 100,
        offset: int = 0,
        token: str = None
    ) -> Dict[str, Any]:
        """Get vouchers from TallyInsight"""
        try:
            params = {"limit": limit, "offset": offset}
            if company:
                params["company"] = company
            if voucher_type:
                params["voucher_type"] = voucher_type
            if from_date:
                params["from_date"] = from_date
            if to_date:
                params["to_date"] = to_date
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/vouchers",
                    params=params,
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_stock_items(
        self,
        company: str = None,
        group: str = None,
        limit: int = 100,
        offset: int = 0,
        token: str = None
    ) -> Dict[str, Any]:
        """Get stock items from TallyInsight"""
        try:
            params = {"limit": limit, "offset": offset}
            if company:
                params["company"] = company
            if group:
                params["group"] = group
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/stock-items",
                    params=params,
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_groups(
        self,
        company: str = None,
        token: str = None
    ) -> Dict[str, Any]:
        """Get account groups from TallyInsight"""
        try:
            params = {}
            if company:
                params["company"] = company
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/groups",
                    params=params,
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== REPORT OPERATIONS ====================
    
    async def get_trial_balance(
        self,
        company: str = None,
        as_on_date: str = None,
        token: str = None
    ) -> Dict[str, Any]:
        """Get trial balance report"""
        try:
            params = {}
            if company:
                params["company"] = company
            if as_on_date:
                params["as_on_date"] = as_on_date
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/trial-balance",
                    params=params,
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_outstanding(
        self,
        company: str = None,
        party_type: str = "receivable",  # receivable or payable
        token: str = None
    ) -> Dict[str, Any]:
        """Get outstanding receivables/payables"""
        try:
            params = {"type": party_type}
            if company:
                params["company"] = company
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/outstanding",
                    params=params,
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_dashboard_summary(
        self,
        company: str = None,
        token: str = None
    ) -> Dict[str, Any]:
        """Get dashboard summary data"""
        try:
            params = {}
            if company:
                params["company"] = company
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/dashboard",
                    params=params,
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_company(
        self,
        company_name: str,
        token: str = None
    ) -> Dict[str, Any]:
        """Delete a company from TallyInsight database"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(
                    f"{self.base_url}/api/data/company/{company_name}",
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== REPORT METHODS (NEW) ====================
    
    async def get_voucher_details(
        self,
        guid: str,
        token: str = None
    ) -> Dict[str, Any]:
        """Get voucher details by GUID"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/vouchers/{guid}/details",
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_outstanding_billwise(
        self,
        type: str = "receivable",
        company: str = None,
        from_date: str = None,
        to_date: str = None,
        page: int = 1,
        page_size: int = 50,
        include_totals: bool = True,
        token: str = None
    ) -> Dict[str, Any]:
        """Get bill-wise outstanding"""
        try:
            params = {"type": type, "page": page, "page_size": page_size, "include_totals": include_totals}
            if company:
                params["company"] = company
            if from_date:
                params["from_date"] = from_date
            if to_date:
                params["to_date"] = to_date
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/outstanding/billwise",
                    params=params,
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_outstanding_ledgerwise(
        self,
        type: str = "receivable",
        company: str = None,
        from_date: str = None,
        to_date: str = None,
        include_totals: bool = True,
        token: str = None
    ) -> Dict[str, Any]:
        """Get ledger-wise outstanding"""
        try:
            params = {"type": type, "include_totals": include_totals}
            if company:
                params["company"] = company
            if from_date:
                params["from_date"] = from_date
            if to_date:
                params["to_date"] = to_date
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/outstanding/ledgerwise",
                    params=params,
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_outstanding_ageing(
        self,
        type: str = "receivable",
        company: str = None,
        token: str = None
    ) -> Dict[str, Any]:
        """Get ageing analysis"""
        try:
            params = {"type": type}
            if company:
                params["company"] = company
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/outstanding/ageing",
                    params=params,
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_outstanding_group(
        self,
        type: str = "receivable",
        company: str = None,
        token: str = None
    ) -> Dict[str, Any]:
        """Get group outstanding"""
        try:
            params = {"type": type}
            if company:
                params["company"] = company
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/outstanding/group",
                    params=params,
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_ledger_list(
        self,
        company: str = None,
        token: str = None
    ) -> Dict[str, Any]:
        """Get list of all ledgers"""
        try:
            params = {}
            if company:
                params["company"] = company
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/ledgers",
                    params=params,
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_ledger_transactions(
        self,
        ledger_name: str,
        company: str = None,
        from_date: str = None,
        to_date: str = None,
        token: str = None
    ) -> Dict[str, Any]:
        """Get ledger transactions"""
        try:
            params = {"ledger": ledger_name}
            if company:
                params["company"] = company
            if from_date:
                params["from_date"] = from_date
            if to_date:
                params["to_date"] = to_date
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/ledger-report",
                    params=params,
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_ledger_billwise(
        self,
        ledger_name: str,
        company: str = None,
        from_date: str = None,
        to_date: str = None,
        token: str = None
    ) -> Dict[str, Any]:
        """Get ledger bill-wise pending bills"""
        try:
            params = {"ledger": ledger_name}
            if company:
                params["company"] = company
            if from_date:
                params["from_date"] = from_date
            if to_date:
                params["to_date"] = to_date
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/ledger-billwise",
                    params=params,
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_company_details(
        self,
        company: str = "",
        token: str = None
    ) -> Dict[str, Any]:
        """Get complete company details from Tally including contact, address, statutory info"""
        try:
            params = {}
            if company:
                params["company"] = company
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/sync/company/details",
                    params=params,
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_ledger_master(
        self,
        company: str = "",
        token: str = None
    ) -> Dict[str, Any]:
        """Get all ledger master data from Tally with 30 fields"""
        try:
            params = {}
            if company:
                params["company"] = company
            
            async with httpx.AsyncClient(timeout=120.0) as client:  # 2 min timeout for large data
                response = await client.get(
                    f"{self.base_url}/api/sync/ledger/master",
                    params=params,
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}", "total": 0, "ledgers": []}
        except Exception as e:
            return {"error": str(e), "total": 0, "ledgers": []}
    
    async def get_ledger_billwise_pdf(
        self,
        ledger: str,
        company: str = None,
        from_date: str = None,
        to_date: str = None,
        token: str = None
    ):
        """Get Bill-wise PDF from TallyInsight"""
        from fastapi.responses import Response
        try:
            params = {"ledger": ledger}
            if company:
                params["company"] = company
            if from_date:
                params["from_date"] = from_date
            if to_date:
                params["to_date"] = to_date
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/ledger-billwise/pdf",
                    params=params,
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                
                # Return PDF response
                return Response(
                    content=response.content,
                    media_type="application/pdf",
                    headers={"Content-Disposition": response.headers.get("Content-Disposition", "attachment; filename=billwise_report.pdf")}
                )
        except httpx.HTTPStatusError as e:
            from fastapi import HTTPException
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_ledger_report_pdf(
        self,
        ledger: str,
        company: str = None,
        from_date: str = None,
        to_date: str = None,
        token: str = None
    ):
        """Get Ledger Report PDF from TallyInsight"""
        from fastapi.responses import Response
        try:
            params = {"ledger": ledger}
            if company:
                params["company"] = company
            if from_date:
                params["from_date"] = from_date
            if to_date:
                params["to_date"] = to_date
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/data/ledger-report/pdf",
                    params=params,
                    headers=self._get_headers(token)
                )
                response.raise_for_status()
                
                # Return PDF response
                return Response(
                    content=response.content,
                    media_type="application/pdf",
                    headers={"Content-Disposition": response.headers.get("Content-Disposition", "attachment; filename=ledger_report.pdf")}
                )
        except httpx.HTTPStatusError as e:
            from fastapi import HTTPException
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=str(e))


# Singleton instance
tally_service = TallyService()

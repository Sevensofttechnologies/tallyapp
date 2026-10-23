"""
Unit Tests for Tally Service
Tests the TallyService HTTP client

Usage:
    pytest tests/test_tally_service.py -v
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.tally_service import TallyService, tally_service


class TestTallyService:
    """Test cases for TallyService"""
    
    @pytest.fixture
    def service(self):
        """Create a TallyService instance"""
        return TallyService()
    
    def test_init(self, service):
        """Test service initialization"""
        assert service.base_url == "http://localhost:8000"
        assert service.timeout == 30.0
    
    def test_get_headers_without_token(self, service):
        """Test headers without auth token"""
        headers = service._get_headers()
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        assert "Authorization" not in headers
    
    def test_get_headers_with_token(self, service):
        """Test headers with auth token"""
        headers = service._get_headers(token="test-token-123")
        assert headers["Authorization"] == "Bearer test-token-123"
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, service):
        """Test successful health check"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy"}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_client_instance
            
            result = await service.health_check()
            
            assert result["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_health_check_unreachable(self, service):
        """Test health check when service is unreachable"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(side_effect=Exception("Connection refused"))
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_client_instance
            
            result = await service.health_check()
            
            assert result["status"] == "unreachable"
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_get_tally_companies_success(self, service):
        """Test getting Tally companies"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"companies": ["Company A", "Company B"]}
            mock_response.raise_for_status = MagicMock()
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_client_instance
            
            result = await service.get_tally_companies()
            
            assert result["success"] is True
            assert "data" in result
    
    @pytest.mark.asyncio
    async def test_sync_company(self, service):
        """Test triggering company sync"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "started", "company": "Test Co"}
            mock_response.raise_for_status = MagicMock()
            
            mock_client_instance = AsyncMock()
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_client_instance
            
            result = await service.sync_company("Test Co", "full")
            
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_get_ledgers(self, service):
        """Test getting ledgers"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "ledgers": [
                    {"name": "Cash", "group": "Cash-in-Hand"},
                    {"name": "Bank", "group": "Bank Accounts"}
                ]
            }
            mock_response.raise_for_status = MagicMock()
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_client_instance
            
            result = await service.get_ledgers(limit=10)
            
            assert result["success"] is True
            assert "data" in result
    
    @pytest.mark.asyncio
    async def test_get_vouchers_with_filters(self, service):
        """Test getting vouchers with filters"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"vouchers": []}
            mock_response.raise_for_status = MagicMock()
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_client_instance
            
            result = await service.get_vouchers(
                company="Test Co",
                voucher_type="Sales",
                from_date="2025-04-01",
                to_date="2026-03-31"
            )
            
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_get_trial_balance(self, service):
        """Test getting trial balance"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "total_debit": 1000000,
                "total_credit": 1000000
            }
            mock_response.raise_for_status = MagicMock()
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_client_instance
            
            result = await service.get_trial_balance()
            
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """Test error handling for failed requests"""
        import httpx
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_response.raise_for_status = MagicMock(
                side_effect=httpx.HTTPStatusError("Error", request=MagicMock(), response=mock_response)
            )
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_client_instance
            
            result = await service.get_ledgers()
            
            assert result["success"] is False
            assert "error" in result


class TestTallySingleton:
    """Test singleton instance"""
    
    def test_singleton_exists(self):
        """Test that singleton instance exists"""
        assert tally_service is not None
        assert isinstance(tally_service, TallyService)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

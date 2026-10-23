"""
Helper Functions
"""

from datetime import datetime
from typing import Any, Optional
from math import ceil


def success_response(data: Any, message: str = "Success") -> dict:
    """Create success response"""
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }


def error_response(error: str, details: Optional[dict] = None) -> dict:
    """Create error response"""
    response = {
        "success": False,
        "error": error,
        "timestamp": datetime.utcnow().isoformat()
    }
    if details:
        response["details"] = details
    return response


def paginate(query, page: int = 1, per_page: int = 10):
    """Paginate database query"""
    page = max(1, page)
    per_page = min(max(1, per_page), 100)
    
    total = query.count()
    pages = ceil(total / per_page) if total > 0 else 1
    offset = (page - 1) * per_page
    
    items = query.offset(offset).limit(per_page).all()
    
    pagination = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages
    }
    
    return items, pagination

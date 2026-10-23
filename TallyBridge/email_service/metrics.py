"""
Metrics collection for email service
Simple counter-based metrics
"""

from typing import Dict
from datetime import datetime
import threading
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Simple metrics collector"""
    
    def __init__(self):
        self._counters: Dict[str, int] = {
            'email_received_total': 0,
            'email_sent_total': 0,
            'email_failed_total': 0,
            'email_retry_total': 0,
        }
        self._lock = threading.Lock()
        self._start_time = datetime.utcnow()
    
    def increment(self, metric_name: str, value: int = 1):
        """Increment a counter"""
        with self._lock:
            if metric_name not in self._counters:
                self._counters[metric_name] = 0
            self._counters[metric_name] += value
    
    def get(self, metric_name: str) -> int:
        """Get counter value"""
        with self._lock:
            return self._counters.get(metric_name, 0)
    
    def get_all(self) -> Dict[str, int]:
        """Get all metrics"""
        with self._lock:
            return dict(self._counters)
    
    def reset(self):
        """Reset all counters"""
        with self._lock:
            for key in self._counters:
                self._counters[key] = 0
    
    def get_stats(self) -> dict:
        """Get statistics summary"""
        with self._lock:
            total_received = self._counters.get('email_received_total', 0)
            total_sent = self._counters.get('email_sent_total', 0)
            total_failed = self._counters.get('email_failed_total', 0)
            
            success_rate = (total_sent / total_received * 100) if total_received > 0 else 0
            
            return {
                'uptime_seconds': (datetime.utcnow() - self._start_time).total_seconds(),
                'total_received': total_received,
                'total_sent': total_sent,
                'total_failed': total_failed,
                'total_retries': self._counters.get('email_retry_total', 0),
                'success_rate_percent': round(success_rate, 2)
            }
    
    def log_stats(self):
        """Log current statistics"""
        stats = self.get_stats()
        logger.info(f"Email Service Stats: {stats}")


# Global metrics instance
metrics = MetricsCollector()

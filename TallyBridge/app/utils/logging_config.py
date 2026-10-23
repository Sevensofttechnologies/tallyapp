"""
Structured Logging Configuration
Industry Standard Logging with Correlation ID
"""

import logging
import json
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar

# Context variable for request ID (thread-safe)
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> Optional[str]:
    """Get current request ID from context"""
    return request_id_var.get()


def set_request_id(request_id: str) -> None:
    """Set request ID in context"""
    request_id_var.set(request_id)


def generate_request_id() -> str:
    """Generate unique request ID"""
    return str(uuid.uuid4())[:8]


class JSONFormatter(logging.Formatter):
    """
    JSON Log Formatter for structured logging
    Industry standard format for log aggregation (ELK, Splunk, etc.)
    """
    
    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add request ID if available
        request_id = get_request_id()
        if request_id:
            log_data["request_id"] = request_id
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if self.include_extra and hasattr(record, "__dict__"):
            extra_fields = {
                k: v for k, v in record.__dict__.items()
                if k not in {
                    "name", "msg", "args", "created", "filename", "funcName",
                    "levelname", "levelno", "lineno", "module", "msecs",
                    "pathname", "process", "processName", "relativeCreated",
                    "stack_info", "exc_info", "exc_text", "thread", "threadName",
                    "message", "taskName"
                }
            }
            if extra_fields:
                log_data["extra"] = extra_fields
        
        return json.dumps(log_data, default=str)


class ColoredFormatter(logging.Formatter):
    """
    Colored console formatter for development
    """
    
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        
        request_id = get_request_id()
        request_id_str = f"[{request_id}] " if request_id else ""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        formatted = (
            f"{color}{timestamp} | {record.levelname:8} | "
            f"{request_id_str}{record.name} | {record.getMessage()}{self.RESET}"
        )
        
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


def setup_logging(
    level: str = "INFO",
    json_format: bool = False,
    log_file: Optional[str] = None
) -> None:
    """
    Setup application logging
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON format (for production)
        log_file: Optional log file path
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    if json_format:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ColoredFormatter())
    
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


class AppLogger:
    """
    Application logger wrapper with context support
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def _log(self, level: int, message: str, **kwargs):
        extra = kwargs.pop("extra", {})
        self.logger.log(level, message, extra=extra, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        self.logger.exception(message, **kwargs)


def get_logger(name: str) -> AppLogger:
    """Get application logger instance"""
    return AppLogger(name)

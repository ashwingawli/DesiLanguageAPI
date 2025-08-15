"""
Logging utilities for DesiLanguage API
"""
import logging
import sys
from datetime import datetime
from typing import Optional
import json


class TimestampFormatter(logging.Formatter):
    """Custom formatter that includes precise timestamps and request information"""
    
    def format(self, record):
        # Add timestamp with milliseconds
        record.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Create structured log format
        if hasattr(record, 'request_id'):
            # API request log
            log_data = {
                "timestamp": record.timestamp,
                "level": record.levelname,
                "request_id": getattr(record, 'request_id', None),
                "method": getattr(record, 'method', None),
                "url": getattr(record, 'url', None),
                "status_code": getattr(record, 'status_code', None),
                "duration_ms": getattr(record, 'duration_ms', None),
                "client_ip": getattr(record, 'client_ip', None),
                "user_agent": getattr(record, 'user_agent', None),
                "message": record.getMessage()
            }
            return json.dumps(log_data, indent=None)
        else:
            # Regular application log
            return f"[{record.timestamp}] {record.levelname:8} | {record.name:20} | {record.getMessage()}"


def setup_logger(name: str = "desi_language", level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with timestamp formatting
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Custom formatter
    formatter = TimestampFormatter()
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def get_api_logger() -> logging.Logger:
    """Get the main API logger"""
    return setup_logger("desi_language.api", "INFO")


def get_request_logger() -> logging.Logger:
    """Get the request logging logger"""
    return setup_logger("desi_language.requests", "INFO")


# Global logger instances
api_logger = get_api_logger()
request_logger = get_request_logger()
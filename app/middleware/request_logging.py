"""
Request logging middleware for FastAPI
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from app.utils.logger import request_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all API requests with timestamps, duration, and request details
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> StarletteResponse:
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]
        
        # Record start time
        start_time = time.time()
        
        # Extract request information
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log incoming request
        request_logger.info(
            f"Incoming request: {method} {url}",
            extra={
                "request_id": request_id,
                "method": method,
                "url": url,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "phase": "start"
            }
        )
        
        try:
            # Process request
            response: Response = await call_next(request)
            
            # Calculate duration
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            # Log successful response
            request_logger.info(
                f"Request completed: {method} {url} - {response.status_code} ({duration_ms}ms)",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "url": url,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "phase": "complete"
                }
            )
            
            # Add request tracking headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms}ms"
            
            return response
            
        except Exception as e:
            # Calculate duration for error cases
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            # Log error
            request_logger.error(
                f"Request failed: {method} {url} - Error: {str(e)} ({duration_ms}ms)",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "url": url,
                    "status_code": 500,
                    "duration_ms": duration_ms,
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "error": str(e),
                    "phase": "error"
                }
            )
            
            # Re-raise the exception
            raise


class APIMetricsMiddleware(BaseHTTPMiddleware):
    """
    Additional middleware to collect API metrics and performance data
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.request_count = 0
        self.total_duration = 0.0
        
    async def dispatch(self, request: Request, call_next: Callable) -> StarletteResponse:
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Update metrics
            self.request_count += 1
            self.total_duration += duration
            
            # Log performance metrics every 100 requests
            if self.request_count % 100 == 0:
                avg_duration = self.total_duration / self.request_count
                request_logger.info(
                    f"Performance metrics: {self.request_count} requests, avg duration: {avg_duration:.3f}s",
                    extra={
                        "request_id": "metrics",
                        "phase": "metrics",
                        "total_requests": self.request_count,
                        "average_duration_ms": round(avg_duration * 1000, 2)
                    }
                )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            self.request_count += 1
            self.total_duration += duration
            raise
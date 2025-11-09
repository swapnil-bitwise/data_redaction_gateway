"""
Timing middleware for request processing time tracking.
"""
import time
import logging
from fastapi import Request

from ...policy import get_policy_loader

logger = logging.getLogger(__name__)

# Import database metrics for automatic logging
try:
    from ...observability.metrics_db import get_metrics_db
    DB_METRICS_ENABLED = True
except ImportError:
    DB_METRICS_ENABLED = False
    logger.warning("Database metrics not available")


async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers and log metrics to database."""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # Convert to ms
    response.headers["X-Process-Time-Ms"] = str(process_time)
    
    # Add policy headers
    policy_loader = get_policy_loader()
    response.headers["X-Redaction-Policy"] = "PII-PCI-Redaction"
    response.headers["X-Policy-Version"] = policy_loader.get_policy_version()
    
    # Automatically log metrics to database (non-blocking, best effort)
    # Skip redaction endpoints as they log detailed metrics themselves
    if DB_METRICS_ENABLED and not request.url.path.startswith("/api/v1/redact"):
        try:
            db = get_metrics_db()
            success = 200 <= response.status_code < 400
            
            # Log the request metric
            db.log_request(
                endpoint=str(request.url.path),
                method=request.method,
                success=success,
                status_code=response.status_code,
                latency_ms=process_time,
                processing_time_ms=process_time,
                request_id=response.headers.get("X-Request-ID", None)
            )
        except Exception as e:
            # Don't fail the request if metrics logging fails
            logger.debug(f"Failed to log metrics to database: {e}")
    
    return response


__all__ = ["add_process_time_header"]
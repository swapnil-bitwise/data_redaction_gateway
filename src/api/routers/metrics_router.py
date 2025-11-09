"""
FastAPI router for metrics tracking and aggregation endpoints.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends, status
from pydantic import BaseModel, Field

from ..observability.metrics_db import get_metrics_db, MetricsDatabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metrics", tags=["Metrics & Analytics"])


# Pydantic models for request/response
class MetricLogRequest(BaseModel):
    """Request model for logging a metric."""
    endpoint: Optional[str] = Field(None, description="API endpoint path")
    method: Optional[str] = Field(None, description="HTTP method")
    success: bool = Field(True, description="Whether request was successful")
    status_code: Optional[int] = Field(None, description="HTTP status code")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    latency_ms: Optional[float] = Field(None, description="Total request latency in ms")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in ms")
    redaction_count: int = Field(0, description="Number of redactions performed")
    rules_triggered: Optional[List[str]] = Field(None, description="Rule IDs triggered")
    llm_judge_called: bool = Field(False, description="Whether LLM judge was invoked")
    llm_response_time_ms: Optional[float] = Field(None, description="LLM response time in ms")
    redaction_quality: Optional[str] = Field(None, description="Quality assessment")
    confidence_score: Optional[float] = Field(None, description="Confidence score from LLM")
    data_size_bytes: Optional[int] = Field(None, description="Size of data processed")
    cache_hit: bool = Field(False, description="Whether cache was hit")
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MetricLogResponse(BaseModel):
    """Response model for metric logging."""
    success: bool
    metric_id: Optional[int] = None
    message: str


class AggregatedMetricsResponse(BaseModel):
    """Response model for aggregated metrics."""
    timestamp: datetime
    aggregation_period: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    llm_calls: int
    under_redacted_count: int
    over_redacted_count: int
    good_redaction_count: int
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    total_redactions: int
    cache_hit_rate: float
    error_rate: float


class TimeSeriesDataPoint(BaseModel):
    """Single time-series data point."""
    timestamp: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    llm_calls: int
    under_redacted: int
    over_redacted: int
    good_redaction: int


class RedactionQualitySummary(BaseModel):
    """Summary of redaction quality."""
    good: int
    under_redacted: int
    over_redacted: int
    total_evaluated: int
    good_percentage: float
    under_redacted_percentage: float
    over_redacted_percentage: float


def get_db() -> MetricsDatabase:
    """Dependency to get metrics database instance."""
    return get_metrics_db()


@router.post("/log", response_model=MetricLogResponse, status_code=status.HTTP_201_CREATED)
async def log_metric(
    metric_data: MetricLogRequest,
    db: MetricsDatabase = Depends(get_db)
):
    """
    Log a single request metric to the database.
    
    This endpoint is called by the gateway to persist metrics for each request.
    """
    try:
        metric_id = db.log_request(
            endpoint=metric_data.endpoint,
            method=metric_data.method,
            success=metric_data.success,
            status_code=metric_data.status_code,
            error_message=metric_data.error_message,
            latency_ms=metric_data.latency_ms,
            processing_time_ms=metric_data.processing_time_ms,
            redaction_count=metric_data.redaction_count,
            rules_triggered=metric_data.rules_triggered,
            llm_judge_called=metric_data.llm_judge_called,
            llm_response_time_ms=metric_data.llm_response_time_ms,
            redaction_quality=metric_data.redaction_quality,
            confidence_score=metric_data.confidence_score,
            data_size_bytes=metric_data.data_size_bytes,
            cache_hit=metric_data.cache_hit,
            request_id=metric_data.request_id,
            metadata=metric_data.metadata
        )
        
        if metric_id:
            return MetricLogResponse(
                success=True,
                metric_id=metric_id,
                message="Metric logged successfully"
            )
        else:
            return MetricLogResponse(
                success=False,
                message="Failed to log metric"
            )
    except Exception as e:
        logger.error(f"Error logging metric: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log metric: {str(e)}"
        )


@router.get("/aggregated", response_model=AggregatedMetricsResponse)
async def get_aggregated_metrics(
    start_time: Optional[datetime] = Query(None, description="Start time for metrics"),
    end_time: Optional[datetime] = Query(None, description="End time for metrics"),
    period: str = Query("hour", description="Aggregation period (minute/hour/day)"),
    db: MetricsDatabase = Depends(get_db)
):
    """
    Get aggregated metrics for a time range.
    
    Query Parameters:
    - start_time: Start of time range (defaults to 1 hour ago)
    - end_time: End of time range (defaults to now)
    - period: Aggregation granularity (minute/hour/day)
    """
    try:
        # Default time range: last hour
        if end_time is None:
            end_time = datetime.utcnow()
        if start_time is None:
            start_time = end_time - timedelta(hours=1)
        
        # Validate period
        if period not in ['minute', 'hour', 'day']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid period. Must be 'minute', 'hour', or 'day'"
            )
        
        metrics = db.get_aggregated_metrics(start_time, end_time, period)
        
        if not metrics:
            # Return empty metrics if no data
            return AggregatedMetricsResponse(
                timestamp=end_time,
                aggregation_period=period,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                success_rate=0.0,
                llm_calls=0,
                under_redacted_count=0,
                over_redacted_count=0,
                good_redaction_count=0,
                avg_latency_ms=0.0,
                p95_latency_ms=0.0,
                p99_latency_ms=0.0,
                total_redactions=0,
                cache_hit_rate=0.0,
                error_rate=0.0
            )
        
        # Take first (and only) aggregated result
        metric = metrics[0]
        success_rate = (metric['successful_requests'] / metric['total_requests'] * 100) if metric['total_requests'] > 0 else 0.0
        
        return AggregatedMetricsResponse(
            timestamp=metric['timestamp'],
            aggregation_period=metric['aggregation_period'],
            total_requests=metric['total_requests'],
            successful_requests=metric['successful_requests'],
            failed_requests=metric['failed_requests'],
            success_rate=success_rate,
            llm_calls=metric['llm_calls'],
            under_redacted_count=metric['under_redacted_count'],
            over_redacted_count=metric['over_redacted_count'],
            good_redaction_count=metric['good_redaction_count'],
            avg_latency_ms=metric['avg_latency_ms'],
            p95_latency_ms=metric['p95_latency_ms'],
            p99_latency_ms=metric['p99_latency_ms'],
            total_redactions=metric['total_redactions'],
            cache_hit_rate=metric['cache_hit_rate'],
            error_rate=metric['error_rate']
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting aggregated metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get aggregated metrics: {str(e)}"
        )


@router.get("/timeseries", response_model=List[TimeSeriesDataPoint])
async def get_time_series_metrics(
    start_time: Optional[datetime] = Query(None, description="Start time"),
    end_time: Optional[datetime] = Query(None, description="End time"),
    interval_minutes: int = Query(5, ge=1, le=1440, description="Time interval in minutes"),
    db: MetricsDatabase = Depends(get_db)
):
    """
    Get time-series metrics for visualization.
    
    Query Parameters:
    - start_time: Start of time range (defaults to 1 hour ago)
    - end_time: End of time range (defaults to now)
    - interval_minutes: Time interval for grouping (1-1440 minutes)
    """
    try:
        # Default time range: last hour
        if end_time is None:
            end_time = datetime.utcnow()
        if start_time is None:
            start_time = end_time - timedelta(hours=1)
        
        time_series = db.get_time_series_metrics(start_time, end_time, interval_minutes)
        
        return [TimeSeriesDataPoint(**point) for point in time_series]
    except Exception as e:
        logger.error(f"Error getting time-series metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get time-series metrics: {str(e)}"
        )


@router.get("/redaction-quality", response_model=RedactionQualitySummary)
async def get_redaction_quality_summary(
    start_time: Optional[datetime] = Query(None, description="Start time"),
    end_time: Optional[datetime] = Query(None, description="End time"),
    db: MetricsDatabase = Depends(get_db)
):
    """
    Get summary of redaction quality from LLM judge evaluations.
    
    Query Parameters:
    - start_time: Start of time range (defaults to 24 hours ago)
    - end_time: End of time range (defaults to now)
    """
    try:
        # Default time range: last 24 hours
        if end_time is None:
            end_time = datetime.utcnow()
        if start_time is None:
            start_time = end_time - timedelta(hours=24)
        
        quality_data = db.get_redaction_quality_summary(start_time, end_time)
        
        total = quality_data['total_evaluated']
        
        return RedactionQualitySummary(
            good=quality_data['good'],
            under_redacted=quality_data['under_redacted'],
            over_redacted=quality_data['over_redacted'],
            total_evaluated=total,
            good_percentage=(quality_data['good'] / total * 100) if total > 0 else 0.0,
            under_redacted_percentage=(quality_data['under_redacted'] / total * 100) if total > 0 else 0.0,
            over_redacted_percentage=(quality_data['over_redacted'] / total * 100) if total > 0 else 0.0
        )
    except Exception as e:
        logger.error(f"Error getting redaction quality summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get redaction quality summary: {str(e)}"
        )


@router.get("/health")
async def metrics_health_check():
    """Health check for metrics system."""
    try:
        db = get_metrics_db()
        # Try a simple query to verify database is accessible
        with db.get_session() as session:
            session.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "database": "connected",
            "db_path": db.db_path
        }
    except Exception as e:
        logger.error(f"Metrics health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }

"""
Database persistence layer for metrics tracking.
Stores LLM judge evaluations and gateway performance metrics.
"""
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os

logger = logging.getLogger(__name__)

Base = declarative_base()


class RequestMetric(Base):
    """Model for storing individual request metrics."""
    __tablename__ = 'request_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Request identification
    request_id = Column(String(64), nullable=True, index=True)
    endpoint = Column(String(255), nullable=True, index=True)
    method = Column(String(10), nullable=True)
    
    # Request outcome
    success = Column(Boolean, default=True, index=True)
    status_code = Column(Integer, nullable=True)
    error_message = Column(String(1000), nullable=True)
    
    # Performance metrics
    latency_ms = Column(Float, nullable=True)
    processing_time_ms = Column(Float, nullable=True)
    
    # Redaction metrics
    redaction_count = Column(Integer, default=0)
    rules_triggered = Column(JSON, nullable=True)  # List of rule IDs triggered
    
    # LLM Judge metrics
    llm_judge_called = Column(Boolean, default=False, index=True)
    llm_response_time_ms = Column(Float, nullable=True)
    redaction_quality = Column(String(50), nullable=True, index=True)  # 'good', 'under_redacted', 'over_redacted'
    confidence_score = Column(Float, nullable=True)
    
    # Additional metadata
    data_size_bytes = Column(Integer, nullable=True)
    cache_hit = Column(Boolean, default=False)
    extra_metadata = Column('metadata', JSON, nullable=True)  # Use column name override
    
    def __repr__(self):
        return f"<RequestMetric(id={self.id}, timestamp={self.timestamp}, success={self.success})>"


class AggregatedMetric(Base):
    """Model for storing pre-aggregated metrics for faster dashboard queries."""
    __tablename__ = 'aggregated_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    aggregation_period = Column(String(20), index=True)  # 'minute', 'hour', 'day'
    
    # Request counts
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    
    # LLM Judge metrics
    llm_calls = Column(Integer, default=0)
    under_redacted_count = Column(Integer, default=0)
    over_redacted_count = Column(Integer, default=0)
    good_redaction_count = Column(Integer, default=0)
    
    # Performance metrics
    avg_latency_ms = Column(Float, nullable=True)
    p95_latency_ms = Column(Float, nullable=True)
    p99_latency_ms = Column(Float, nullable=True)
    
    # Additional stats
    total_redactions = Column(Integer, default=0)
    cache_hit_rate = Column(Float, default=0.0)
    error_rate = Column(Float, default=0.0)
    
    def __repr__(self):
        return f"<AggregatedMetric(timestamp={self.timestamp}, period={self.aggregation_period})>"


class MetricsDatabase:
    """Database manager for metrics persistence."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Use default path in project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_dir = os.path.join(project_root, 'data')
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, 'metrics.db')
        
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
        logger.info(f"Metrics database initialized at: {db_path}")
    
    @contextmanager
    def get_session(self) -> Session:
        """Context manager for database sessions."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def log_request(
        self,
        endpoint: str = None,
        method: str = None,
        success: bool = True,
        status_code: int = None,
        error_message: str = None,
        latency_ms: float = None,
        processing_time_ms: float = None,
        redaction_count: int = 0,
        rules_triggered: List[str] = None,
        llm_judge_called: bool = False,
        llm_response_time_ms: float = None,
        redaction_quality: str = None,
        confidence_score: float = None,
        data_size_bytes: int = None,
        cache_hit: bool = False,
        request_id: str = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[int]:
        """
        Log a single request metric to database.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            success: Whether request was successful
            status_code: HTTP status code
            error_message: Error message if failed
            latency_ms: Total request latency
            processing_time_ms: Processing time
            redaction_count: Number of redactions performed
            rules_triggered: List of rule IDs that were triggered
            llm_judge_called: Whether LLM judge was invoked
            llm_response_time_ms: LLM response time
            redaction_quality: Quality assessment (good/under_redacted/over_redacted)
            confidence_score: Confidence score from LLM judge
            data_size_bytes: Size of data processed
            cache_hit: Whether cache was hit
            request_id: Unique request identifier
            metadata: Additional metadata
            
        Returns:
            ID of created record, or None if failed
        """
        try:
            with self.get_session() as session:
                metric = RequestMetric(
                    timestamp=datetime.utcnow(),
                    request_id=request_id,
                    endpoint=endpoint,
                    method=method,
                    success=success,
                    status_code=status_code,
                    error_message=error_message,
                    latency_ms=latency_ms,
                    processing_time_ms=processing_time_ms,
                    redaction_count=redaction_count,
                    rules_triggered=rules_triggered,
                    llm_judge_called=llm_judge_called,
                    llm_response_time_ms=llm_response_time_ms,
                    redaction_quality=redaction_quality,
                    confidence_score=confidence_score,
                    data_size_bytes=data_size_bytes,
                    cache_hit=cache_hit,
                    extra_metadata=metadata
                )
                session.add(metric)
                session.flush()
                return metric.id
        except Exception as e:
            logger.error(f"Failed to log request metric: {e}")
            return None
    
    def get_aggregated_metrics(
        self,
        start_time: datetime = None,
        end_time: datetime = None,
        aggregation_period: str = 'hour'
    ) -> List[Dict[str, Any]]:
        """
        Get aggregated metrics for a time range.
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            aggregation_period: Aggregation granularity (minute/hour/day)
            
        Returns:
            List of aggregated metric dictionaries
        """
        try:
            with self.get_session() as session:
                query = session.query(RequestMetric)
                
                if start_time:
                    query = query.filter(RequestMetric.timestamp >= start_time)
                if end_time:
                    query = query.filter(RequestMetric.timestamp <= end_time)
                
                metrics = query.all()
                
                # Aggregate the data
                total_requests = len(metrics)
                successful_requests = sum(1 for m in metrics if m.success)
                failed_requests = total_requests - successful_requests
                
                llm_calls = sum(1 for m in metrics if m.llm_judge_called)
                under_redacted = sum(1 for m in metrics if m.redaction_quality == 'under_redacted')
                over_redacted = sum(1 for m in metrics if m.redaction_quality == 'over_redacted')
                good_redaction = sum(1 for m in metrics if m.redaction_quality == 'good')
                
                latencies = [m.latency_ms for m in metrics if m.latency_ms is not None]
                avg_latency = sum(latencies) / len(latencies) if latencies else 0
                
                latencies_sorted = sorted(latencies)
                p95_latency = latencies_sorted[int(len(latencies_sorted) * 0.95)] if latencies_sorted else 0
                p99_latency = latencies_sorted[int(len(latencies_sorted) * 0.99)] if latencies_sorted else 0
                
                total_redactions = sum(m.redaction_count for m in metrics if m.redaction_count)
                cache_hits = sum(1 for m in metrics if m.cache_hit)
                cache_hit_rate = (cache_hits / total_requests * 100) if total_requests > 0 else 0
                error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
                
                return [{
                    'timestamp': end_time or datetime.utcnow(),
                    'aggregation_period': aggregation_period,
                    'total_requests': total_requests,
                    'successful_requests': successful_requests,
                    'failed_requests': failed_requests,
                    'llm_calls': llm_calls,
                    'under_redacted_count': under_redacted,
                    'over_redacted_count': over_redacted,
                    'good_redaction_count': good_redaction,
                    'avg_latency_ms': avg_latency,
                    'p95_latency_ms': p95_latency,
                    'p99_latency_ms': p99_latency,
                    'total_redactions': total_redactions,
                    'cache_hit_rate': cache_hit_rate,
                    'error_rate': error_rate
                }]
        except Exception as e:
            logger.error(f"Failed to get aggregated metrics: {e}")
            return []
    
    def get_time_series_metrics(
        self,
        start_time: datetime = None,
        end_time: datetime = None,
        interval_minutes: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get time-series metrics for visualization.
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            interval_minutes: Time interval for grouping
            
        Returns:
            List of time-series data points
        """
        try:
            with self.get_session() as session:
                query = session.query(RequestMetric)
                
                if start_time:
                    query = query.filter(RequestMetric.timestamp >= start_time)
                if end_time:
                    query = query.filter(RequestMetric.timestamp <= end_time)
                
                query = query.order_by(RequestMetric.timestamp)
                metrics = query.all()
                
                # Group by time intervals
                time_series = []
                if not metrics:
                    return time_series
                
                current_bucket_start = metrics[0].timestamp.replace(second=0, microsecond=0)
                current_bucket_data = []
                
                for metric in metrics:
                    # Check if we need to start a new bucket
                    if (metric.timestamp - current_bucket_start).total_seconds() >= interval_minutes * 60:
                        # Process current bucket
                        if current_bucket_data:
                            time_series.append(self._aggregate_bucket(current_bucket_start, current_bucket_data))
                        
                        # Start new bucket
                        current_bucket_start = metric.timestamp.replace(second=0, microsecond=0)
                        current_bucket_data = [metric]
                    else:
                        current_bucket_data.append(metric)
                
                # Process last bucket
                if current_bucket_data:
                    time_series.append(self._aggregate_bucket(current_bucket_start, current_bucket_data))
                
                return time_series
        except Exception as e:
            logger.error(f"Failed to get time-series metrics: {e}")
            return []
    
    def _aggregate_bucket(self, timestamp: datetime, metrics: List[RequestMetric]) -> Dict[str, Any]:
        """Aggregate metrics for a time bucket."""
        total = len(metrics)
        successful = sum(1 for m in metrics if m.success)
        failed = total - successful
        llm_calls = sum(1 for m in metrics if m.llm_judge_called)
        
        return {
            'timestamp': timestamp.isoformat(),
            'total_requests': total,
            'successful_requests': successful,
            'failed_requests': failed,
            'llm_calls': llm_calls,
            'under_redacted': sum(1 for m in metrics if m.redaction_quality == 'under_redacted'),
            'over_redacted': sum(1 for m in metrics if m.redaction_quality == 'over_redacted'),
            'good_redaction': sum(1 for m in metrics if m.redaction_quality == 'good'),
        }
    
    def get_redaction_quality_summary(
        self,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> Dict[str, int]:
        """
        Get summary of redaction quality metrics.
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            Dictionary with quality counts
        """
        try:
            with self.get_session() as session:
                query = session.query(RequestMetric)
                
                if start_time:
                    query = query.filter(RequestMetric.timestamp >= start_time)
                if end_time:
                    query = query.filter(RequestMetric.timestamp <= end_time)
                
                query = query.filter(RequestMetric.llm_judge_called == True)
                metrics = query.all()
                
                return {
                    'good': sum(1 for m in metrics if m.redaction_quality == 'good'),
                    'under_redacted': sum(1 for m in metrics if m.redaction_quality == 'under_redacted'),
                    'over_redacted': sum(1 for m in metrics if m.redaction_quality == 'over_redacted'),
                    'total_evaluated': len(metrics)
                }
        except Exception as e:
            logger.error(f"Failed to get redaction quality summary: {e}")
            return {'good': 0, 'under_redacted': 0, 'over_redacted': 0, 'total_evaluated': 0}


# Global database instance
_metrics_db = None


def get_metrics_db() -> MetricsDatabase:
    """Get or create global metrics database instance."""
    global _metrics_db
    if _metrics_db is None:
        _metrics_db = MetricsDatabase()
    return _metrics_db

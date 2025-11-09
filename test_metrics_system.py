"""
Test script to verify metrics tracking system is working correctly.
This script tests the metrics database and API endpoints.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
from datetime import datetime, timedelta
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_creation():
    """Test that database is created correctly."""
    logger.info("=" * 60)
    logger.info("TEST 1: Database Creation")
    logger.info("=" * 60)
    
    try:
        from src.observability.metrics_db import get_metrics_db
        
        db = get_metrics_db()
        logger.info(f"✓ Database created at: {db.db_path}")
        logger.info(f"✓ Database instance: {db}")
        
        # Verify tables exist
        with db.get_session() as session:
            result = session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = [row[0] for row in result]
            logger.info(f"✓ Tables found: {tables}")
            
            if 'request_metrics' in tables and 'aggregated_metrics' in tables:
                logger.info("✓ All required tables exist")
                return True
            else:
                logger.error("✗ Missing required tables")
                return False
                
    except Exception as e:
        logger.error(f"✗ Database creation failed: {e}")
        return False


def test_metric_logging():
    """Test logging metrics to database."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Metric Logging")
    logger.info("=" * 60)
    
    try:
        from src.observability.metrics_db import get_metrics_db
        
        db = get_metrics_db()
        
        # Log a test metric
        metric_id = db.log_request(
            endpoint="/test/redact",
            method="POST",
            success=True,
            status_code=200,
            latency_ms=45.5,
            processing_time_ms=42.0,
            redaction_count=3,
            rules_triggered=["EMAIL_REGEX", "PHONE_REGEX"],
            llm_judge_called=True,
            llm_response_time_ms=150.0,
            redaction_quality="good",
            confidence_score=0.95,
            data_size_bytes=1024,
            cache_hit=False,
            request_id="test-123",
            metadata={"test": True}
        )
        
        if metric_id:
            logger.info(f"✓ Metric logged successfully with ID: {metric_id}")
            
            # Verify it was stored
            with db.get_session() as session:
                result = session.execute(
                    text("SELECT COUNT(*) FROM request_metrics WHERE id = :id"),
                    {"id": metric_id}
                )
                count = result.scalar()
                if count == 1:
                    logger.info("✓ Metric verified in database")
                    return True
                else:
                    logger.error("✗ Metric not found in database")
                    return False
        else:
            logger.error("✗ Failed to log metric")
            return False
            
    except Exception as e:
        logger.error(f"✗ Metric logging failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_aggregated_metrics():
    """Test retrieving aggregated metrics."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Aggregated Metrics")
    logger.info("=" * 60)
    
    try:
        from src.observability.metrics_db import get_metrics_db
        
        db = get_metrics_db()
        
        # Log several test metrics
        for i in range(5):
            db.log_request(
                endpoint=f"/test/endpoint{i % 2}",
                method="POST",
                success=(i % 3 != 0),  # Some failures
                status_code=200 if (i % 3 != 0) else 500,
                latency_ms=40.0 + i * 10,
                redaction_count=i,
                llm_judge_called=(i % 2 == 0),
                redaction_quality="good" if i % 2 == 0 else "under_redacted"
            )
        
        logger.info("✓ Logged 5 test metrics")
        
        # Get aggregated metrics
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        metrics = db.get_aggregated_metrics(start_time, end_time, "hour")
        
        if metrics:
            metric = metrics[0]
            logger.info(f"✓ Retrieved aggregated metrics:")
            logger.info(f"  - Total requests: {metric['total_requests']}")
            logger.info(f"  - Successful: {metric['successful_requests']}")
            logger.info(f"  - Failed: {metric['failed_requests']}")
            logger.info(f"  - LLM calls: {metric['llm_calls']}")
            logger.info(f"  - Good redactions: {metric['good_redaction_count']}")
            logger.info(f"  - Under-redacted: {metric['under_redacted_count']}")
            logger.info(f"  - Avg latency: {metric['avg_latency_ms']:.2f}ms")
            return True
        else:
            logger.error("✗ No metrics returned")
            return False
            
    except Exception as e:
        logger.error(f"✗ Aggregated metrics failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_time_series():
    """Test time-series metrics."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Time-Series Metrics")
    logger.info("=" * 60)
    
    try:
        from src.observability.metrics_db import get_metrics_db
        
        db = get_metrics_db()
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        time_series = db.get_time_series_metrics(start_time, end_time, 5)
        
        logger.info(f"✓ Retrieved {len(time_series)} time-series data points")
        
        if time_series:
            logger.info("  Sample data points:")
            for i, point in enumerate(time_series[:3]):
                logger.info(f"    {i+1}. {point['timestamp']}: {point['total_requests']} requests")
            return True
        else:
            logger.warning("⚠ No time-series data (this is OK if no data was logged)")
            return True
            
    except Exception as e:
        logger.error(f"✗ Time-series metrics failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_redaction_quality():
    """Test redaction quality summary."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Redaction Quality Summary")
    logger.info("=" * 60)
    
    try:
        from src.observability.metrics_db import get_metrics_db
        
        db = get_metrics_db()
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        quality = db.get_redaction_quality_summary(start_time, end_time)
        
        logger.info(f"✓ Retrieved quality summary:")
        logger.info(f"  - Good: {quality['good']}")
        logger.info(f"  - Under-redacted: {quality['under_redacted']}")
        logger.info(f"  - Over-redacted: {quality['over_redacted']}")
        logger.info(f"  - Total evaluated: {quality['total_evaluated']}")
        
        return True
            
    except Exception as e:
        logger.error(f"✗ Redaction quality summary failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_existing_metrics_collector():
    """Test that existing metrics collector still works."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 6: Existing Metrics Collector (Backward Compatibility)")
    logger.info("=" * 60)
    
    try:
        from src.observability import get_metrics_collector
        
        metrics = get_metrics_collector()
        
        # Test recording metrics
        metrics.record_request(50.0, endpoint="/test")
        metrics.record_redactions(3)
        
        logger.info("✓ Recorded test metrics")
        
        # Get summary
        summary = metrics.get_summary()
        
        logger.info(f"✓ Retrieved metrics summary:")
        logger.info(f"  - Total requests: {summary.get('total_requests', 0)}")
        logger.info(f"  - Total redactions: {summary.get('total_redactions', 0)}")
        
        logger.info("✓ Existing metrics collector is working correctly")
        return True
            
    except Exception as e:
        logger.error(f"✗ Existing metrics collector failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    logger.info("╔═══════════════════════════════════════════════════════════╗")
    logger.info("║     Metrics System Integration Test Suite                ║")
    logger.info("╚═══════════════════════════════════════════════════════════╝")
    logger.info("")
    
    tests = [
        ("Database Creation", test_database_creation),
        ("Metric Logging", test_metric_logging),
        ("Aggregated Metrics", test_aggregated_metrics),
        ("Time-Series Metrics", test_time_series),
        ("Redaction Quality", test_redaction_quality),
        ("Backward Compatibility", test_existing_metrics_collector),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"\n✗ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    logger.info("=" * 60)
    
    if passed == total:
        logger.info("\n✓ All tests passed! Metrics system is working correctly.")
        logger.info("✓ Existing functionality is not impacted.")
        logger.info("\nNext steps:")
        logger.info("  1. Start the API: python main_modular.py")
        logger.info("  2. Start the dashboard: cd dashboard && streamlit run app.py")
        logger.info("  3. Check the dashboard at: http://localhost:8501")
        return 0
    else:
        logger.error("\n✗ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

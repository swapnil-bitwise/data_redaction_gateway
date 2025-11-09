"""
Generate sample metrics data for dashboard testing.

This script creates sample metrics in the database to populate the dashboard
with realistic data for demonstration and testing purposes.
"""
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.observability.metrics_db import get_metrics_db

# Sample data
ENDPOINTS = [
    "/api/v1/redact/text",
    "/api/v1/redact/json",
    "/api/v1/redact/stream",
    "/api/v1/validate",
    "/api/v1/health"
]

METHODS = ["GET", "POST", "PUT"]

REDACTION_QUALITIES = ["good", "under_redacted", "over_redacted"]

RULES = ["ssn", "credit_card", "email", "phone", "address", "name"]


def generate_sample_metrics(count: int = 100):
    """Generate sample metrics for the last 24 hours."""
    db = get_metrics_db()
    print(f"📊 Generating {count} sample metrics...")
    
    now = datetime.utcnow()
    
    for i in range(count):
        # Random time within last 24 hours
        hours_ago = random.uniform(0, 24)
        timestamp = now - timedelta(hours=hours_ago)
        
        # Random endpoint and method
        endpoint = random.choice(ENDPOINTS)
        method = random.choice(METHODS)
        
        # Success rate: 80% successful
        success = random.random() < 0.8
        status_code = random.choice([200, 201]) if success else random.choice([400, 401, 500, 503])
        
        # Latency: 10-500ms
        latency_ms = random.uniform(10, 500)
        processing_time_ms = latency_ms * random.uniform(0.7, 0.9)
        
        # Redaction data
        redaction_count = random.randint(0, 10)
        rules_triggered = random.sample(RULES, k=random.randint(1, 3)) if redaction_count > 0 else []
        
        # LLM judge: 30% of requests
        llm_judge_called = random.random() < 0.3
        llm_response_time_ms = random.uniform(100, 2000) if llm_judge_called else None
        
        # Redaction quality (only if LLM was called)
        if llm_judge_called:
            redaction_quality = random.choices(
                REDACTION_QUALITIES,
                weights=[0.7, 0.2, 0.1]  # 70% good, 20% under, 10% over
            )[0]
            confidence_score = random.uniform(0.6, 0.99)
        else:
            redaction_quality = None
            confidence_score = None
        
        # Data size
        data_size_bytes = random.randint(100, 10000)
        
        # Cache hit: 20%
        cache_hit = random.random() < 0.2
        
        # Error message for failures
        error_message = "Request validation failed" if not success else None
        
        # Log to database (timestamp is auto-generated)
        try:
            metric_id = db.log_request(
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
                request_id=f"sample-{i+1}"
            )
            
            if (i + 1) % 20 == 0:
                print(f"  ✓ Generated {i + 1}/{count} metrics...")
                
        except Exception as e:
            print(f"  ✗ Error generating metric {i+1}: {e}")
    
    print(f"\n✅ Successfully generated {count} sample metrics!")
    print(f"📍 Database location: {db.db_path}")
    print(f"\n🎯 Next steps:")
    print(f"  1. Ensure API is running: python main_modular.py")
    print(f"  2. Open dashboard: streamlit run dashboard/app.py")
    print(f"  3. View metrics at: http://localhost:8501")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate sample metrics data")
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of sample metrics to generate (default: 100)"
    )
    
    args = parser.parse_args()
    
    try:
        generate_sample_metrics(args.count)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

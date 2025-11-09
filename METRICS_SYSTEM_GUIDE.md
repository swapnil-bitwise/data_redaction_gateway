# Metrics Tracking & Visualization System - Complete Guide

## Overview
This comprehensive metrics system provides persistent storage and visualization of Data Redaction Gateway metrics, including LLM judge evaluations and performance analytics.

## Architecture

### Components

1. **SQLite Database** (`src/observability/metrics_db.py`)
   - Persistent storage for all metrics
   - Two tables: `request_metrics` and `aggregated_metrics`
   - Automatic schema creation
   - Thread-safe operations

2. **FastAPI Endpoints** (`src/api/routers/metrics.py`)
   - `/metrics/db/log` - Log individual request metrics
   - `/metrics/db/aggregated` - Get aggregated metrics
   - `/metrics/db/timeseries` - Get time-series data
   - `/metrics/db/redaction-quality` - Get quality summary
   - `/metrics/db/health` - Database health check

3. **Streamlit Dashboard** (`dashboard/app.py`)
   - Real-time visualization
   - Interactive time range selection
   - KPIs, charts, and quality analysis
   - Auto-refresh capability

## Installation

### 1. Install Dependencies

```bash
# Main application dependencies (includes SQLAlchemy)
pip install -r requirements.txt

# Dashboard dependencies
cd dashboard
pip install -r requirements.txt
cd ..
```

### 2. Verify Installation

```bash
python -c "import sqlalchemy; print('SQLAlchemy version:', sqlalchemy.__version__)"
python -c "import streamlit; print('Streamlit version:', streamlit.__version__)"
```

## Database Setup

### Automatic Initialization
The database is automatically created on first use at:
```
<project_root>/data/metrics.db
```

### Manual Initialization (Optional)
```python
from src.observability.metrics_db import get_metrics_db

# Initialize database
db = get_metrics_db()
print(f"Database initialized at: {db.db_path}")
```

### Database Schema

#### request_metrics Table
```sql
CREATE TABLE request_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME,
    request_id VARCHAR(64),
    endpoint VARCHAR(255),
    method VARCHAR(10),
    success BOOLEAN,
    status_code INTEGER,
    error_message VARCHAR(1000),
    latency_ms FLOAT,
    processing_time_ms FLOAT,
    redaction_count INTEGER,
    rules_triggered JSON,
    llm_judge_called BOOLEAN,
    llm_response_time_ms FLOAT,
    redaction_quality VARCHAR(50),  -- 'good', 'under_redacted', 'over_redacted'
    confidence_score FLOAT,
    data_size_bytes INTEGER,
    cache_hit BOOLEAN,
    metadata JSON
);
```

## API Usage

### Starting the API
```bash
# Standard uvicorn
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Or use the provided script
python main_modular.py
```

### Logging Metrics

#### Option 1: Via API Endpoint
```bash
curl -X POST "http://localhost:8000/metrics/db/log" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "endpoint": "/redact",
    "method": "POST",
    "success": true,
    "status_code": 200,
    "latency_ms": 45.2,
    "redaction_count": 3,
    "llm_judge_called": true,
    "redaction_quality": "good",
    "confidence_score": 0.95
  }'
```

#### Option 2: Via Python Client
```python
import requests

def log_request_metric(
    endpoint: str,
    success: bool,
    latency_ms: float,
    llm_judge_called: bool = False,
    redaction_quality: str = None
):
    """Log a request metric to the database."""
    url = "http://localhost:8000/metrics/db/log"
    headers = {"X-API-Key": "your-api-key"}
    
    data = {
        "endpoint": endpoint,
        "success": success,
        "latency_ms": latency_ms,
        "llm_judge_called": llm_judge_called,
        "redaction_quality": redaction_quality
    }
    
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# Example usage
log_request_metric(
    endpoint="/redact",
    success=True,
    latency_ms=42.5,
    llm_judge_called=True,
    redaction_quality="good"
)
```

### Querying Metrics

#### Get Aggregated Metrics
```bash
# Last hour
curl "http://localhost:8000/metrics/db/aggregated?period=hour" \
  -H "X-API-Key: your-api-key"

# Custom time range
curl "http://localhost:8000/metrics/db/aggregated?\
start_time=2025-11-09T00:00:00&\
end_time=2025-11-09T12:00:00&\
period=hour" \
  -H "X-API-Key: your-api-key"
```

#### Get Time-Series Data
```bash
# Last hour with 5-minute intervals
curl "http://localhost:8000/metrics/db/timeseries?interval_minutes=5" \
  -H "X-API-Key: your-api-key"
```

#### Get Redaction Quality Summary
```bash
# Last 24 hours
curl "http://localhost:8000/metrics/db/redaction-quality" \
  -H "X-API-Key: your-api-key"
```

## Dashboard Usage

### Starting the Dashboard

#### Method 1: PowerShell Script (Recommended for Windows)
```powershell
cd dashboard
.\run_dashboard.ps1
```

#### Method 2: Direct Command
```bash
cd dashboard
streamlit run app.py
```

The dashboard will open at: `http://localhost:8501`

### Dashboard Features

1. **Time Range Selection**
   - Predefined ranges: 15 min, 1 hour, 6 hours, 24 hours, 7 days
   - Custom date/time picker
   - Configurable interval granularity

2. **Key Performance Indicators (KPIs)**
   - Total Requests
   - Success Rate
   - Failed Requests
   - LLM Judge Calls
   - Average Latency

3. **Request Trends**
   - Time-series line charts
   - Total, successful, and failed requests
   - LLM judge invocations over time

4. **Redaction Quality Analysis**
   - Summary metrics
   - Pie chart distribution
   - Bar chart counts
   - Quality trend over time

5. **Auto-Refresh**
   - Configurable refresh interval (10-300 seconds)
   - Enable/disable in sidebar

### Configuration

#### Changing API URL
In the dashboard sidebar, update the "API Base URL" field:
- Default: `http://127.0.0.1:8000`
- For remote API: `http://your-server:8000`

#### Customizing Visualizations
Edit `dashboard/app.py` to:
- Add new charts
- Modify color schemes
- Change layout
- Add custom metrics

## Integration with Existing Code

### Non-Breaking Integration
The metrics system is designed to NOT impact existing functionality:

1. **Database logging is optional** - API continues to work even if database is unavailable
2. **Graceful degradation** - If SQLAlchemy is not installed, only database endpoints are disabled
3. **Backward compatible** - All existing `/metrics/*` endpoints remain unchanged
4. **Separate endpoints** - New endpoints use `/metrics/db/*` prefix

### Adding Metrics Logging to Your Code

#### Example: Logging from Redaction Endpoint
```python
from src.observability.metrics_db import get_metrics_db
import logging

logger = logging.getLogger(__name__)

async def redact_endpoint(request_data):
    start_time = time.time()
    
    try:
        # Your existing redaction logic
        result = perform_redaction(request_data)
        
        # Log to database (non-blocking, catches own exceptions)
        try:
            db = get_metrics_db()
            db.log_request(
                endpoint="/redact",
                method="POST",
                success=True,
                status_code=200,
                latency_ms=(time.time() - start_time) * 1000,
                redaction_count=len(result.redactions),
                rules_triggered=[r.rule_id for r in result.redactions]
            )
        except Exception as e:
            logger.warning(f"Failed to log metrics to database: {e}")
            # Continue normally - don't fail the request
        
        return result
        
    except Exception as e:
        # Log error to database
        try:
            db = get_metrics_db()
            db.log_request(
                endpoint="/redact",
                method="POST",
                success=False,
                status_code=500,
                error_message=str(e),
                latency_ms=(time.time() - start_time) * 1000
            )
        except:
            pass
        
        raise
```

#### Example: Logging LLM Judge Results
```python
async def evaluate_with_llm_judge(redacted_data, original_data):
    llm_start = time.time()
    
    # Your LLM judge logic
    evaluation = await llm_judge.evaluate(redacted_data, original_data)
    llm_time = (time.time() - llm_start) * 1000
    
    # Log to database
    try:
        db = get_metrics_db()
        db.log_request(
            endpoint="/redact",
            llm_judge_called=True,
            llm_response_time_ms=llm_time,
            redaction_quality=evaluation.quality,  # 'good', 'under_redacted', 'over_redacted'
            confidence_score=evaluation.confidence,
            metadata={
                'model': evaluation.model_used,
                'prompt_tokens': evaluation.tokens_used
            }
        )
    except Exception as e:
        logger.warning(f"Failed to log LLM judge metrics: {e}")
    
    return evaluation
```

## Testing

### Running Existing Tests
```bash
# Verify existing functionality is not broken
cd test_suite
pytest test_all_endpoints.py -v
```

### Testing Metrics Endpoints
```python
import requests

BASE_URL = "http://localhost:8000"
API_KEY = "your-api-key"
headers = {"X-API-Key": API_KEY}

# Test health check
response = requests.get(f"{BASE_URL}/metrics/db/health", headers=headers)
print("Health:", response.json())

# Test logging
metric = {
    "endpoint": "/test",
    "success": True,
    "latency_ms": 100.0,
    "redaction_count": 5
}
response = requests.post(f"{BASE_URL}/metrics/db/log", json=metric, headers=headers)
print("Log result:", response.json())

# Test aggregated metrics
response = requests.get(f"{BASE_URL}/metrics/db/aggregated", headers=headers)
print("Aggregated:", response.json())
```

## Troubleshooting

### Database Issues

#### Database Not Created
- Check write permissions in `<project_root>/data/` directory
- Verify SQLAlchemy is installed: `pip show sqlalchemy`
- Check logs for initialization errors

#### Database Locked
- SQLite doesn't handle high concurrency well
- Consider upgrading to PostgreSQL for production:
  ```python
  # Update connection string in metrics_db.py
  engine = create_engine('postgresql://user:pass@localhost/metrics')
  ```

### API Issues

#### Endpoints Return 503
- Verify SQLAlchemy is installed
- Check `DB_METRICS_ENABLED` flag in logs
- Install: `pip install sqlalchemy>=2.0.0`

#### Authentication Errors
- Ensure X-API-Key header is included
- Verify API key is valid
- Check security configuration

### Dashboard Issues

#### Cannot Connect to API
- Verify API is running: `curl http://localhost:8000/docs`
- Check API Base URL in dashboard sidebar
- Verify firewall/network settings

#### No Data Displayed
- Ensure metrics are being logged to database
- Check selected time range includes data
- Verify database path: `<project_root>/data/metrics.db`

#### Slow Performance
- Reduce time range or increase interval
- Disable auto-refresh for large datasets
- Add database indexes:
  ```sql
  CREATE INDEX idx_timestamp ON request_metrics(timestamp);
  CREATE INDEX idx_success ON request_metrics(success);
  CREATE INDEX idx_endpoint ON request_metrics(endpoint);
  ```

## Production Deployment

### Database Recommendations
1. **Use PostgreSQL** for production
2. **Enable connection pooling**
3. **Set up regular backups**
4. **Add monitoring**

### Performance Optimization
1. **Batch inserts** instead of individual logs
2. **Use async database operations**
3. **Implement write-through caching**
4. **Set up read replicas** for dashboard queries

### Security Considerations
1. **Secure database credentials**
2. **Enable SSL/TLS** for database connections
3. **Implement API authentication** for dashboard
4. **Set up audit logging**
5. **Restrict database access**

### Monitoring
1. **Track database size** and set up rotation
2. **Monitor query performance**
3. **Set up alerts** for database errors
4. **Track dashboard uptime**

## Data Retention

### Cleanup Old Data
```python
from src.observability.metrics_db import get_metrics_db
from datetime import datetime, timedelta

db = get_metrics_db()

# Delete records older than 30 days
with db.get_session() as session:
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    session.query(RequestMetric).filter(
        RequestMetric.timestamp < cutoff_date
    ).delete()
    session.commit()
```

### Scheduled Cleanup (Cron Job)
```bash
# Add to crontab for daily cleanup at 2 AM
0 2 * * * /usr/bin/python /path/to/cleanup_script.py
```

## Support & Contributing

### Getting Help
- Check API documentation: `http://localhost:8000/docs`
- Review logs in `logs/` directory
- Check database: `sqlite3 data/metrics.db`

### Contributing
1. Test changes don't break existing functionality
2. Add tests for new features
3. Update documentation
4. Follow existing code style

## Appendix

### Metrics Data Dictionary

| Field | Type | Description |
|-------|------|-------------|
| endpoint | String | API endpoint path (e.g., "/redact") |
| method | String | HTTP method (GET, POST, etc.) |
| success | Boolean | Request succeeded or failed |
| status_code | Integer | HTTP status code (200, 500, etc.) |
| latency_ms | Float | Total request latency in milliseconds |
| redaction_count | Integer | Number of redactions performed |
| llm_judge_called | Boolean | Whether LLM judge was invoked |
| redaction_quality | String | "good", "under_redacted", or "over_redacted" |
| confidence_score | Float | LLM confidence score (0.0-1.0) |

### Useful SQL Queries

```sql
-- Total requests per endpoint
SELECT endpoint, COUNT(*) as total
FROM request_metrics
GROUP BY endpoint
ORDER BY total DESC;

-- Success rate by endpoint
SELECT 
    endpoint,
    COUNT(*) as total,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
    ROUND(100.0 * SUM(CASE WHEN success THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM request_metrics
GROUP BY endpoint;

-- LLM judge quality distribution
SELECT 
    redaction_quality,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM request_metrics WHERE llm_judge_called = 1), 2) as percentage
FROM request_metrics
WHERE llm_judge_called = 1
GROUP BY redaction_quality;

-- Average latency by hour
SELECT 
    strftime('%Y-%m-%d %H:00', timestamp) as hour,
    AVG(latency_ms) as avg_latency,
    COUNT(*) as requests
FROM request_metrics
GROUP BY hour
ORDER BY hour DESC
LIMIT 24;
```

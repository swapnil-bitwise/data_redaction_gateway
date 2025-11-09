# Test Suite for PII/PCI Data Redaction Gateway

## Overview

Comprehensive test suite for all API endpoints using pytest. Tests include health checks, redaction with real data, policy management, cache operations, error handling, and performance benchmarks.

## Quick Start

### 1. Install Dependencies

```powershell
pip install pytest requests
```

### 2. Start the Server

```powershell
# In a separate terminal
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Run All Tests

```powershell
# From project root
pytest test_suite/ -v

# Or with more detailed output
pytest test_suite/ -v -s
```

## Test Structure

### Test Classes

#### 1. **TestHealthEndpoints**
- `test_root_endpoint()` - Tests `GET /`
- `test_health_check()` - Tests `GET /health`

**What it tests:**
- Service is running and operational
- Returns correct version and status information
- Health check includes uptime and cache stats

#### 2. **TestMetricsEndpoint**
- `test_get_metrics()` - Tests `GET /metrics`
- `test_metrics_requires_auth()` - Tests authentication

**What it tests:**
- Metrics collection (requests, redactions, latency)
- P95/P99 latency percentiles
- Cache hit rate and redaction coverage
- LLM judge fallback rate
- API key authentication requirement

#### 3. **TestRedactionEndpoint**
- `test_redact_chat_data()` - Tests with `test_chat.json`
- `test_redact_transaction_data()` - Tests with `test_transaction.json`
- `test_redact_order_data()` - Tests with `test_order.json`
- `test_redact_without_metadata()` - Tests without metadata
- `test_redact_requires_auth()` - Tests authentication

**What it tests:**
- PII/PCI detection and redaction
- Email, phone, credit card, name redaction
- Metadata inclusion (field, rule, action)
- LLM judge validation (when sampled)
- Processing time tracking
- API key authentication

**Test Data Used:**
- `input/test_chat.json` - Chat message with email, phone, name
- `input/test_transaction.json` - Transaction with PAN, CVV, IBAN, account
- `input/test_order.json` - Order with customer PII

#### 4. **TestDryRunEndpoint**
- `test_dry_run_redaction()` - Tests `POST /redact/dry-run`

**What it tests:**
- Before/after comparison
- Diff summary (redaction count, affected fields, triggered rules)
- No actual data modification

#### 5. **TestPolicyEndpoints**
- `test_get_policy()` - Tests `GET /policy`
- `test_reload_policy()` - Tests `POST /policy/reload`

**What it tests:**
- Policy retrieval (version, rules)
- Policy reload from YAML file
- Rules are loaded correctly

#### 6. **TestCacheEndpoints**
- `test_get_cache_stats()` - Tests `GET /cache/stats`
- `test_clear_cache()` - Tests `POST /cache/clear`

**What it tests:**
- Cache statistics (size, hit rate, TTL)
- Cache clearing functionality

#### 7. **TestErrorHandling**
- `test_invalid_endpoint()` - Tests 404 handling
- `test_invalid_api_key()` - Tests 403 for bad API key
- `test_malformed_json()` - Tests 422 for invalid request

**What it tests:**
- Proper HTTP status codes for errors
- API key validation
- Request body validation

#### 8. **TestPerformance**
- `test_redaction_latency()` - Tests single request latency
- `test_multiple_requests()` - Tests 5 sequential requests

**What it tests:**
- Redaction completes within 1 second
- Consistent performance across multiple requests
- Network vs processing time breakdown

## Running Tests

### Run All Tests
```powershell
pytest test_suite/ -v
```

### Run Specific Test Class
```powershell
pytest test_suite/test_api_endpoints.py::TestRedactionEndpoint -v
```

### Run Specific Test
```powershell
pytest test_suite/test_api_endpoints.py::TestRedactionEndpoint::test_redact_chat_data -v
```

### Run with Detailed Output (shows print statements)
```powershell
pytest test_suite/ -v -s
```

### Run and Stop on First Failure
```powershell
pytest test_suite/ -v -x
```

### Run with Coverage Report
```powershell
pytest test_suite/ --cov=src --cov-report=html
```

### Generate HTML Test Report
```powershell
pytest test_suite/ --html=test_suite/report.html --self-contained-html
```

## Output Examples

### Successful Test Output
```
test_suite/test_api_endpoints.py::TestHealthEndpoints::test_root_endpoint PASSED

=== Root Endpoint ===
Response: {
  "name": "PII/PCI Data Redaction Gateway",
  "version": "1.0.0",
  "environment": "development",
  "status": "operational"
}
```

### Redaction Test Output
```
test_suite/test_api_endpoints.py::TestRedactionEndpoint::test_redact_chat_data PASSED

=== Redact Chat Data ===
Original Data: {
  "user_id": "user-12345",
  "message": "Hi, my email is john.doe@example.com",
  "phone": "+1-555-123-4567"
}

Redacted Data: {
  "user_id": "user-12345",
  "message": "Hi, my email is j***@e****e.com",
  "phone": "***-***-***-4567"
}

Processing Time: 45.23ms
Policy Version: 1.4

Redactions Applied: 2
  - message: EMAIL_REGEX -> mask
  - phone: PHONE_REGEX -> mask

🎯 LLM Judge Result:
  - Coverage Complete: True
  - Over-Redacted: False
  - Under-Redacted: False
  - Confidence: 95.0%
  - Processing Time: 234.56ms
```

### Performance Test Output
```
test_suite/test_api_endpoints.py::TestPerformance::test_multiple_requests PASSED

=== Multiple Requests Test ===
Request 1: 45.23ms
Request 2: 42.18ms
Request 3: 43.67ms
Request 4: 44.01ms
Request 5: 43.92ms

Average Time: 43.80ms
```

## Test Configuration

### Base URL
```python
BASE_URL = "http://localhost:8000"
```

### API Key
```python
API_KEY = "dev-api-key-12345"
```

### Test Data Location
```python
TEST_DATA_DIR = Path(__file__).parent.parent / "input"
```

Files used:
- `input/test_chat.json`
- `input/test_transaction.json`
- `input/test_order.json`

## Expected Results

### Total Tests: 22

- **Health & Status**: 2 tests
- **Metrics**: 2 tests
- **Redaction**: 5 tests
- **Dry Run**: 1 test
- **Policy**: 2 tests
- **Cache**: 2 tests
- **Error Handling**: 3 tests
- **Performance**: 2 tests

### Expected Pass Rate: 100%

All tests should pass when:
- Server is running on `http://localhost:8000`
- API key `dev-api-key-12345` is configured
- Test data files exist in `input/` directory
- All dependencies are installed

## Troubleshooting

### Connection Error
**Problem**: `requests.exceptions.ConnectionError`

**Solution**:
```powershell
# Start the server first
uvicorn src.main:app --reload
```

### Authentication Failed
**Problem**: `403 Forbidden` on all authenticated endpoints

**Solution**: Check API key in test file matches config:
```python
API_KEY = "dev-api-key-12345"  # Must match config.yaml or .env
```

### Test Data Not Found
**Problem**: `FileNotFoundError: test_chat.json`

**Solution**: Ensure test data files exist:
```powershell
ls input/test_*.json
```

### Import Errors
**Problem**: `ModuleNotFoundError: No module named 'pytest'`

**Solution**:
```powershell
pip install pytest requests
```

### LLM Judge Tests Failing
**Problem**: Judge result is always `null`

**Note**: This is expected if `LLM_API_KEY` is not configured. The test will still pass as judge validation is optional. If you want judge results:
```powershell
$env:LLM_API_KEY="sk-proj-YOUR-KEY"
```

## Advanced Usage

### Run Only Fast Tests (exclude performance)
```powershell
pytest test_suite/ -v -k "not performance"
```

### Run Only Redaction Tests
```powershell
pytest test_suite/ -v -k "redact"
```

### Run with Parallel Execution (faster)
```powershell
pip install pytest-xdist
pytest test_suite/ -v -n auto
```

### Generate JUnit XML Report (for CI/CD)
```powershell
pytest test_suite/ --junitxml=test_suite/junit.xml
```

### Run Tests with Timeout
```powershell
pip install pytest-timeout
pytest test_suite/ -v --timeout=10
```

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run API Tests
  run: |
    uvicorn src.main:app --host 0.0.0.0 --port 8000 &
    sleep 5
    pytest test_suite/ -v --junitxml=test-results.xml
```

### Jenkins Example
```groovy
stage('API Tests') {
    steps {
        sh 'uvicorn src.main:app --host 0.0.0.0 --port 8000 &'
        sh 'sleep 5'
        sh 'pytest test_suite/ -v --junitxml=test-results.xml'
    }
}
```

## Test Maintenance

### Adding New Tests

1. Add test method to appropriate class:
```python
def test_new_feature(self):
    """Test description."""
    response = requests.get(f"{BASE_URL}/new-endpoint", headers=HEADERS)
    assert response.status_code == 200
```

2. Run new test:
```powershell
pytest test_suite/test_api_endpoints.py::TestClassName::test_new_feature -v
```

### Using Custom Test Data

1. Add new JSON file to `input/`:
```powershell
echo '{"email": "test@example.com"}' > input/test_custom.json
```

2. Load in test:
```python
test_file = TEST_DATA_DIR / "test_custom.json"
with open(test_file, 'r') as f:
    test_data = json.load(f)
```

## Summary

This test suite provides comprehensive coverage of all API endpoints with:
- ✅ Real test data from your existing JSON files
- ✅ Detailed input/output visibility
- ✅ Single command execution (`pytest test_suite/ -v`)
- ✅ Clear, readable output
- ✅ Performance benchmarks
- ✅ Error handling validation
- ✅ Authentication testing

Run with: `pytest test_suite/ -v -s` for full visibility into all test operations.

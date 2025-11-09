# Test Suite Quick Reference

## Run Tests - Single Command

```powershell
# From project root directory
pytest test_suite/ -v -s
```

Or use the convenience script:
```powershell
.\test_suite\run_tests.ps1
```

## What Gets Tested

✅ **19 Total Tests** covering:

1. **Health Checks** (2 tests)
   - Root endpoint status
   - Health check with uptime

2. **Metrics** (2 tests)
   - Get all metrics
   - Authentication required

3. **Redaction** (5 tests)
   - Chat data (test_chat.json)
   - Transaction data (test_transaction.json)
   - Order data (test_order.json)
   - Without metadata
   - Authentication required

4. **Dry Run** (1 test)
   - Before/after comparison

5. **Policy** (2 tests)
   - Get current policy
   - Reload policy

6. **Cache** (2 tests)
   - Get stats
   - Clear cache

7. **Errors** (3 tests)
   - Invalid endpoint (404)
   - Invalid API key (403)
   - Malformed JSON (422)

8. **Performance** (2 tests)
   - Single request latency
   - Multiple requests (5x)

## Prerequisites

1. **Server running**:
   ```powershell
   uvicorn src.main:app --reload
   ```

2. **Dependencies installed**:
   ```powershell
   pip install pytest requests
   ```

3. **Test data exists**:
   - `input/test_chat.json` ✓
   - `input/test_transaction.json` ✓
   - `input/test_order.json` ✓

## Common Commands

```powershell
# Run all tests with verbose output
pytest test_suite/ -v

# Run with detailed output (shows print statements)
pytest test_suite/ -v -s

# Run specific test class
pytest test_suite/test_api_endpoints.py::TestRedactionEndpoint -v

# Run specific test
pytest test_suite/test_api_endpoints.py::TestRedactionEndpoint::test_redact_chat_data -v

# Stop on first failure
pytest test_suite/ -v -x

# Run tests matching pattern
pytest test_suite/ -v -k "redact"

# Generate HTML report
pytest test_suite/ --html=test_suite/report.html --self-contained-html
```

## Expected Output

```
======================== test session starts =========================
test_suite/test_api_endpoints.py::TestHealthEndpoints::test_root_endpoint PASSED
test_suite/test_api_endpoints.py::TestHealthEndpoints::test_health_check PASSED
test_suite/test_api_endpoints.py::TestMetricsEndpoint::test_get_metrics PASSED
...
======================== 19 passed in 2.45s ==========================
```

## Output Includes

For each test, you'll see:
- **Input data** (original JSON)
- **Output data** (redacted JSON)
- **Redaction metadata** (fields, rules, actions)
- **Processing time**
- **LLM judge results** (if sampled)
- **Performance metrics**

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | Start server: `uvicorn src.main:app --reload` |
| 403 Forbidden | Check API key matches: `dev-api-key-12345` |
| File not found | Verify test data files exist in `input/` |
| Import error | Install: `pip install pytest requests` |

## Full Documentation

See `test_suite/README.md` for detailed documentation.

---
**Quick Start**: `pytest test_suite/ -v -s`

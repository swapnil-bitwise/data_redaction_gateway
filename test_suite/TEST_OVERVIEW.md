# Test Suite Overview

## 📁 Directory Structure

```
test_suite/
├── __init__.py                 # Package initialization
├── conftest.py                 # Pytest configuration
├── test_api_endpoints.py       # Main test file (19 tests)
├── run_tests.ps1              # Convenience runner script
├── README.md                   # Full documentation
└── QUICK_START.md             # Quick reference guide
```

## 📊 Test Coverage

### Total: 19 Tests

| Category | Tests | Description |
|----------|-------|-------------|
| Health | 2 | Root endpoint, health check |
| Metrics | 2 | Get metrics, authentication |
| Redaction | 5 | Chat, transaction, order data + auth |
| Dry Run | 1 | Before/after comparison |
| Policy | 2 | Get policy, reload |
| Cache | 2 | Stats, clear |
| Errors | 3 | 404, 403, 422 handling |
| Performance | 2 | Latency, multiple requests |

## 🎯 Endpoints Tested

✅ `GET /` - Root endpoint  
✅ `GET /health` - Health check  
✅ `GET /metrics` - Service metrics  
✅ `POST /redact` - Main redaction  
✅ `POST /redact/dry-run` - Dry run mode  
✅ `GET /policy` - Get current policy  
✅ `POST /policy/reload` - Reload policy  
✅ `GET /cache/stats` - Cache statistics  
✅ `POST /cache/clear` - Clear cache  

## 📝 Test Data Used

| File | Content | Fields Tested |
|------|---------|---------------|
| `test_chat.json` | Chat message | email, phone, name |
| `test_transaction.json` | Payment transaction | PAN, CVV, IBAN, account |
| `test_order.json` | Customer order | customer PII, payment |

## 🚀 Quick Commands

**Run all tests:**
```powershell
pytest test_suite/ -v -s
```

**Run with script:**
```powershell
.\test_suite\run_tests.ps1
```

**Run specific category:**
```powershell
# Redaction tests only
pytest test_suite/ -v -k "redact"

# Performance tests only
pytest test_suite/ -v -k "performance"
```

## 📈 What Gets Validated

### ✓ Functional Testing
- All endpoints return correct status codes
- Response bodies match expected schema
- PII/PCI data is properly redacted
- Metadata includes correct field paths, rules, actions
- Policy loading and reloading works
- Cache operations function correctly

### ✓ Security Testing
- API key authentication enforced
- Invalid keys rejected (403)
- No raw PII exposed in responses

### ✓ Error Handling
- 404 for non-existent endpoints
- 403 for authentication failures
- 422 for malformed requests

### ✓ Performance Testing
- Requests complete within 1 second
- Consistent performance across multiple requests
- Network vs processing time breakdown

### ✓ Integration Testing
- Real test data from JSON files
- LLM judge integration (when configured)
- Policy file loading
- Cache behavior

## 📋 Sample Output

### Successful Test
```
test_redact_chat_data PASSED

=== Redact Chat Data ===
Original: {"email": "john@example.com", "phone": "+1-555-123-4567"}
Redacted: {"email": "j***@e****e.com", "phone": "***-***-***-4567"}
Processing Time: 45.23ms
Redactions: 2 (EMAIL_REGEX, PHONE_REGEX)
```

### With LLM Judge
```
🎯 LLM Judge Result:
  - Coverage Complete: True
  - Confidence: 95.0%
  - Processing Time: 234.56ms
```

### Performance Test
```
=== Multiple Requests Test ===
Request 1: 45.23ms
Request 2: 42.18ms
Request 3: 43.67ms
Average: 43.80ms
```

## 🔧 Configuration

**Base URL**: `http://localhost:8000`  
**API Key**: `dev-api-key-12345`  
**Test Data**: `input/test_*.json`

## 📚 Documentation

- **Full Guide**: `test_suite/README.md`
- **Quick Start**: `test_suite/QUICK_START.md`
- **Test Code**: `test_suite/test_api_endpoints.py`

## ✅ Success Criteria

All 19 tests should pass when:
1. Server is running on port 8000
2. API key is configured correctly
3. Test data files exist
4. Dependencies are installed

Expected result:
```
======================== 19 passed in 2.45s ==========================
```

---

**Run Now**: `pytest test_suite/ -v -s`

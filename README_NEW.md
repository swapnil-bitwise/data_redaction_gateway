# 🛡️ Runtime PII/PCI Data Redaction Gateway

**Team:** AI NINJAS  
**Hackathon Submission:** Real-Time Data Redaction Gateway

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/GenAI-OpenAI%20GPT--4o-orange.svg)](https://openai.com/)

---

## 📋 Problem Statement Description

Organizations need to protect sensitive Personally Identifiable Information (PII) and Payment Card Industry (PCI) data in real-time streaming scenarios while maintaining compliance with GDPR and PCI DSS 4.0 regulations. The challenge is to:

1. **Detect sensitive data** in real-time from multiple data formats (JSON, NDJSON, text streams)
2. **Redact detected information** while preserving data structure and format
3. **Validate redaction quality** using AI-based assessment
4. **Maintain low latency** (<100ms overhead) for production workloads
5. **Ensure compliance** without storing or transmitting raw PII

**Key Requirements:**
- Real-time detection using regex patterns, Luhn algorithm, and NER
- Multiple redaction methods (masking, tokenization, FPE)
- LLM-as-Judge for quality validation (10-20% sampling)
- Policy-as-code with YAML configuration
- API gateway proxy functionality
- Comprehensive observability and metrics
- Security baseline with API keys, TLS, and log sanitization

---

## 💡 Solution Overview

### Architecture Approach

Our solution implements a **high-performance FastAPI-based gateway** with a modular, production-ready architecture:

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ API Request
       ▼
┌─────────────────────────────────────────────┐
│        Data Redaction Gateway               │
│  ┌──────────────────────────────────────┐  │
│  │  1. API Gateway Layer (FastAPI)      │  │
│  │     - Request validation             │  │
│  │     - Authentication (API Keys)      │  │
│  │     - Rate limiting                  │  │
│  └──────────────┬───────────────────────┘  │
│                 ▼                           │
│  ┌──────────────────────────────────────┐  │
│  │  2. Detection Layer                  │  │
│  │     - Regex patterns (Email, Phone)  │  │
│  │     - Luhn algorithm (Credit Cards)  │  │
│  │     - spaCy NER (Person Names)       │  │
│  │     - Base64/Gzip decompression      │  │
│  └──────────────┬───────────────────────┘  │
│                 ▼                           │
│  ┌──────────────────────────────────────┐  │
│  │  3. Redaction Engine                 │  │
│  │     - Masking (last 4 digits)        │  │
│  │     - HMAC-based tokenization        │  │
│  │     - Format-Preserving Encryption   │  │
│  │     - Hash-based redaction           │  │
│  └──────────────┬───────────────────────┘  │
│                 ▼                           │
│  ┌──────────────────────────────────────┐  │
│  │  4. LLM-as-Judge (15% sampling)      │  │
│  │     - GenAI: OpenAI GPT-4o-mini      │  │
│  │     - Validation coverage check      │  │
│  │     - Over/under-redaction detection │  │
│  │     - Graceful timeout handling      │  │
│  └──────────────┬───────────────────────┘  │
│                 ▼                           │
│  ┌──────────────────────────────────────┐  │
│  │  5. Observability & Metrics          │  │
│  │     - SQLite metrics database        │  │
│  │     - Streamlit dashboard            │  │
│  │     - Performance tracking           │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
       │ Redacted Response
       ▼
┌─────────────┐
│ Downstream  │
│  Services   │
└─────────────┘
```

### GenAI Model Usage

**Model:** OpenAI GPT-4o-mini (via OpenAI API)

**Purpose:** LLM-as-Judge for redaction quality validation

**Implementation:**
- **Sampling Rate:** 15% of requests (configurable)
- **Budget Control:** Hourly and daily limits to manage costs
- **Timeout Handling:** 10-second timeout with graceful fallback to rules-only mode
- **Privacy Protection:** Only sends partially masked context (no raw PII)
- **Validation Criteria:**
  - Coverage completeness (all sensitive data redacted)
  - Over-redaction detection (excessive masking)
  - Under-redaction detection (missed sensitive data)
  - Confidence scoring (0-100%)

**Alternative Support:** Anthropic Claude (configurable via environment variables)

### Key Technical Components

#### 1. **Multi-Method Detection**
- **Regex Patterns:** Email, phone, SSN, addresses
- **Luhn Algorithm:** Credit card validation (PAN detection)
- **spaCy NER:** `en_core_web_sm` model for person name detection
- **Configurable Rules:** YAML-based policy definitions

#### 2. **Advanced Redaction Strategies**
- **Masking:** Preserve last N digits (e.g., `************1234`)
- **Tokenization:** HMAC-SHA256 deterministic tokens for analytics
- **FPE (Format-Preserving Encryption):** For credit cards (maintains format)
- **Hashing:** SHA-256 irreversible redaction

#### 3. **Policy-as-Code**
- **YAML Configuration:** `input/redaction_rules.yaml`
- **Version Control:** Policy versioning with effective dates
- **Route-Based Rules:** Per-endpoint, method, tenant policies
- **Compliance Tags:** GDPR, PCI DSS 4.0 mapping

#### 4. **Warm Decision Cache**
- **Cache Key:** `endpoint + field + rule_id`
- **TTL:** Configurable expiration (default 1 hour)
- **Privacy-Safe:** Only caches decisions, never raw PII

#### 5. **Security Features**
- **Authentication:** API key validation
- **JWT Support:** Token-based authentication
- **Encryption:** AES-256 for sensitive data
- **Log Sanitization:** No raw PII in logs
- **TLS Support:** HTTPS ready
- **Audit Logging:** All operations tracked

#### 6. **Observability Stack**
- **Metrics Database:** SQLite with SQLAlchemy ORM
- **Real-time Dashboard:** Streamlit with Plotly visualizations
- **OpenTelemetry Ready:** Distributed tracing support
- **Performance Tracking:** P95/P99 latency, throughput, cache hit rate

### Performance Characteristics

- **Latency Overhead:** <100ms average (target met)
- **Throughput:** 60+ requests/minute per instance
- **Redaction Speed:** ~10-50ms per request (without LLM)
- **LLM Validation:** +500-1500ms (only 15% of requests)
- **Memory Footprint:** ~200MB base + 150MB (spaCy model)

---

## 🔧 Environment Setup

### Prerequisites

- **Python:** 3.11 or higher (3.8+ supported)
- **Operating System:** Windows 10/11, Linux, or macOS
- **RAM:** Minimum 2GB (4GB recommended for spaCy NER)
- **Disk Space:** 500MB for dependencies

### Installation Steps

#### 1. Clone or Navigate to Project Directory
```powershell
cd data_redaction_gateway
```

#### 2. Automated Setup (Recommended - Windows)
```powershell
# Run automated setup script
.\quickstart.ps1
```

This script will:
- Create Python virtual environment
- Install all dependencies from `requirements.txt`
- Download spaCy NER model (`en_core_web_sm`)
- Verify installation

#### 3. Manual Setup (All Platforms)

**Step 3a: Create Virtual Environment**
```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

**Step 3b: Install Dependencies**
```powershell
pip install -r requirements.txt
```

**Step 3c: Download spaCy NER Model**
```powershell
python -m spacy download en_core_web_sm
```

#### 4. Environment Configuration

**Create `.env` file** (copy from `.env.example`):
```powershell
cp .env.example .env
```

**Configure Required Variables:**
```env
# API Security
API_KEYS=your-api-key-here,another-key
JWT_SECRET_KEY=your-secret-key-here

# Encryption Keys
HMAC_SECRET_KEY=your-hmac-key
ENCRYPTION_KEY=your-encryption-key

# GenAI LLM Configuration
LLM_API_KEY=sk-your-openai-api-key
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini

# Server Configuration
SERVER_HOST=127.0.0.1
SERVER_PORT=8000
ENVIRONMENT=development
```

**Generate Secure Keys:**
```powershell
# Generate HMAC and encryption keys
python -c "from cryptography.fernet import Fernet; import secrets; print(f'HMAC: {secrets.token_urlsafe(32)}'); print(f'Encryption: {Fernet.generate_key().decode()}')"
```

### Dependencies Overview

**Core Framework:**
- `fastapi>=0.104.0` - Web framework
- `uvicorn>=0.24.0` - ASGI server
- `pydantic>=2.4.0` - Data validation

**Detection & NER:**
- `spacy>=3.7.0` - Named Entity Recognition
- `regex>=2023.10.3` - Pattern matching

**Security:**
- `cryptography>=41.0.0` - Encryption (AES, FPE)
- `passlib[bcrypt]>=1.7.4` - Password hashing
- `python-jose>=3.3.0` - JWT tokens

**GenAI/LLM:**
- `openai>=1.0.0` - OpenAI GPT integration
- `anthropic>=0.7.0` - Claude integration (optional)

**Metrics & Observability:**
- `sqlalchemy>=2.0.0` - Database ORM
- `streamlit>=1.28.0` - Dashboard framework
- `plotly>=5.17.0` - Visualizations
- `pandas>=2.0.0` - Data processing

**Complete list:** See `requirements.txt`

---

## 🚀 Execution Steps

### Step 1: Start the API Gateway

**Method 1: Using Main Script**
```powershell
python main_modular.py
```

**Method 2: Using CLI**
```powershell
python cli_modular.py serve --host 127.0.0.1 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Verify Server is Running:**
- API Documentation: http://127.0.0.1:8000/docs
- Health Check: http://127.0.0.1:8000/health

### Step 2: Test Basic Redaction

**Using cURL:**
```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/redact/" `
  -H "X-API-Key: dev-api-key-12345" `
  -H "Content-Type: application/json" `
  -d '{
    "data": "John Smith, email: john@example.com, card: 4532-1234-5678-9010",
    "include_meta": true
  }'
```

**Expected Response:**
```json
{
  "redacted_data": "********, email: j***@e******.com, card: ************9010",
  "redaction_meta": [
    {
      "field": "root",
      "rule": "person_name",
      "action": "mask",
      "timestamp": "2025-11-09T12:00:00Z"
    },
    {
      "field": "root",
      "rule": "email",
      "action": "mask"
    },
    {
      "field": "root",
      "rule": "credit_card_luhn",
      "action": "mask"
    }
  ],
  "processing_time_ms": 45.2,
  "judge_result": {
    "coverage_complete": true,
    "confidence": 95,
    "assessment": "good"
  }
}
```

### Step 3: Start Metrics Dashboard (Optional)

**Open a new terminal and run:**
```powershell
cd dashboard
streamlit run app.py
```

**Access Dashboard:**
- URL: http://localhost:8501
- Features: Real-time KPIs, time-series charts, quality analysis

### Step 4: Generate Sample Metrics (For Demo)

```powershell
python generate_sample_metrics.py --count 100
```

This creates 100 sample metrics to populate the dashboard with realistic data.

### Step 5: Run Test Suite

**Comprehensive Integration Tests:**
```powershell
python test_metrics_system.py
```

**Redaction Endpoint Tests:**
```powershell
python test_redaction_metrics.py
```

**Full Automated Test Suite:**
```powershell
cd test_suite
python -m pytest test_all_endpoints.py -v
```

**Expected Results:** 
- 6/6 integration tests passing
- All endpoint tests passing
- No breaking changes

### Step 6: Test Different Features

#### 6a. Streaming Redaction (NDJSON)
```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/stream/redact/ndjson" `
  -H "X-API-Key: dev-api-key-12345" `
  -H "Content-Type: text/plain" `
  -d '{"name": "John Doe", "email": "john@example.com"}
{"phone": "555-1234", "ssn": "123-45-6789"}'
```

#### 6b. Dry-Run (Preview Redaction)
```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/redact/dry-run" `
  -H "X-API-Key: dev-api-key-12345" `
  -H "Content-Type: application/json" `
  -d '{
    "data": "Contact: john@example.com, Card: 4532123456789010"
  }'
```

#### 6c. Policy Information
```powershell
curl "http://127.0.0.1:8000/api/v1/policy" `
  -H "X-API-Key: dev-api-key-12345"
```

#### 6d. Metrics API
```powershell
# Get aggregated metrics
curl "http://127.0.0.1:8000/api/v1/metrics/db/aggregated?start_time=2025-11-09T00:00:00&end_time=2025-11-10T00:00:00"

# Get redaction quality summary
curl "http://127.0.0.1:8000/api/v1/metrics/db/redaction-quality?start_time=2025-11-09T00:00:00&end_time=2025-11-10T00:00:00"
```

### Step 7: Clean Up Metrics Database (Optional)

```powershell
python clean_metrics_db.py
```

---

## ⚠️ Limitations and Future Enhancements

### Current Limitations

#### 1. **Performance Limitations**
- **spaCy NER Model:** Adds 30-50ms latency per request
  - *Impact:* May not meet <100ms target for all requests with NER enabled
  - *Mitigation:* NER is optional and can be disabled in config
  
- **LLM Validation Overhead:** 500-1500ms when LLM judge is called
  - *Impact:* Affects 15% of requests (by design)
  - *Mitigation:* Sampling rate is configurable; graceful timeout handling

#### 2. **Scalability Constraints**
- **Single Instance:** Current deployment is single-instance
  - *Impact:* Limited to ~60 requests/minute throughput
  - *Future:* Horizontal scaling with load balancer needed
  
- **SQLite Database:** Not suitable for high-concurrency scenarios
  - *Impact:* Metrics writes may block under heavy load
  - *Future:* Migrate to PostgreSQL/MySQL for production

#### 3. **Detection Accuracy**
- **Regex-Based Detection:** May have false positives/negatives
  - *Example:* Email-like strings that aren't actual emails
  - *Mitigation:* LLM judge helps catch these cases
  
- **Context-Dependent PII:** Limited understanding of context
  - *Example:* "John" vs "St. John" (location vs person)
  - *Future:* Advanced NER models or larger LLM integration

#### 4. **Security Considerations**
- **API Key Authentication:** Basic authentication only
  - *Limitation:* No OAuth2, no MFA
  - *Future:* Integrate with identity providers (Auth0, Okta)
  
- **Encryption Key Management:** Stored in `.env` files
  - *Limitation:* Not enterprise-grade secret management
  - *Future:* HashiCorp Vault, AWS Secrets Manager integration

#### 5. **Proxy Mode**
- **Not Fully Implemented:** API gateway proxy for upstream services
  - *Status:* Framework exists but needs completion
  - *Future:* Full transparent proxy with route-based policies

#### 6. **Cost Management**
- **LLM API Costs:** OpenAI GPT-4o-mini charges per token
  - *Mitigation:* Budget controls (hourly/daily limits) implemented
  - *Future:* Support for local LLMs (Ollama, llama.cpp)

### Future Enhancements

#### Short-Term (1-3 months)

1. **Advanced Redaction Methods**
   - **Synthetic Data Generation:** Replace PII with realistic fake data
   - **Differential Privacy:** Add noise while preserving analytics utility
   - **Smart Partial Masking:** Context-aware masking (e.g., preserve domain in emails)

2. **Performance Optimizations**
   - **Async Processing:** Parallel detection across multiple fields
   - **GPU Acceleration:** For large-scale NER processing
   - **Redis Cache:** Replace in-memory cache with distributed cache
   - **Connection Pooling:** Optimize database connections

3. **Enhanced LLM Integration**
   - **Multiple LLM Providers:** Support for Google Gemini, AWS Bedrock
   - **Local LLM Support:** Ollama, llama.cpp for cost reduction
   - **Custom Fine-Tuned Models:** Domain-specific redaction models
   - **Streaming LLM Responses:** Reduce perceived latency

4. **API Gateway Proxy Completion**
   - **Transparent Proxying:** Forward requests to upstream services
   - **Route-Based Policies:** Per-route redaction configurations
   - **Request/Response Transformation:** Bi-directional redaction
   - **Circuit Breaker:** Fault tolerance for upstream failures

#### Medium-Term (3-6 months)

5. **Multi-Language Support**
   - **NER Models:** Support for Spanish, French, German, Chinese
   - **Locale-Aware Rules:** Country-specific PII patterns (UK postcodes, EU VAT numbers)
   - **Unicode Handling:** Better support for non-ASCII text

6. **Advanced Analytics Dashboard**
   - **Real-Time Alerting:** Slack/Email notifications for anomalies
   - **Compliance Reporting:** GDPR/PCI DSS audit reports
   - **Historical Trend Analysis:** Long-term metrics storage and analysis
   - **Custom Dashboards:** Role-based views (security, ops, compliance)

7. **Enterprise Features**
   - **Multi-Tenancy:** Isolated policies per tenant/customer
   - **RBAC (Role-Based Access Control):** Fine-grained permissions
   - **SSO Integration:** SAML, OAuth2, OpenID Connect
   - **Audit Trails:** Immutable logs for compliance

8. **Distributed Deployment**
   - **Kubernetes Deployment:** Helm charts, auto-scaling
   - **Service Mesh Integration:** Istio/Linkerd for observability
   - **High Availability:** Multi-region deployment
   - **Load Balancing:** Nginx/HAProxy configurations

#### Long-Term (6+ months)

9. **Machine Learning Enhancements**
   - **Anomaly Detection:** ML-based detection of unusual PII patterns
   - **Active Learning:** Continuously improve detection from feedback
   - **Privacy Budget Management:** Differential privacy optimization
   - **Federated Learning:** Train models without centralizing data

10. **Compliance Automation**
    - **Auto-Classification:** Automatically tag data based on sensitivity
    - **Policy Recommendations:** AI-suggested redaction policies
    - **Compliance Dashboards:** Real-time compliance score
    - **Regulatory Updates:** Automatic policy updates for new regulations

11. **Advanced Integrations**
    - **Data Loss Prevention (DLP):** Integration with DLP tools
    - **SIEM Integration:** Splunk, ELK, Datadog
    - **API Marketplace:** Pre-built integrations (Salesforce, ServiceNow)
    - **Webhook Support:** Event-driven notifications

12. **Developer Experience**
    - **SDKs:** Python, Java, Go, Node.js client libraries
    - **IDE Plugins:** VS Code extension for testing redaction
    - **Postman Collection:** Comprehensive API examples
    - **Interactive Tutorials:** Step-by-step guides

---

## 📚 Additional Documentation

For detailed information, see:

- **[APPLICATION_RUN_GUIDE.md](APPLICATION_RUN_GUIDE.md)** - Comprehensive setup and usage guide
- **[METRICS_SYSTEM_GUIDE.md](METRICS_SYSTEM_GUIDE.md)** - Metrics dashboard documentation (2000+ lines)
- **[DEPLOYMENT_READINESS_REPORT.md](DEPLOYMENT_READINESS_REPORT.md)** - Test results and production readiness
- **[PRE_DEPLOYMENT_TEST_PLAN.md](PRE_DEPLOYMENT_TEST_PLAN.md)** - 3-hour structured test plan
- **[SECURITY_IMPLEMENTATION_STATUS.md](SECURITY_IMPLEMENTATION_STATUS.md)** - Security features
- **[DOCUMENTATION_GUIDE.md](DOCUMENTATION_GUIDE.md)** - Navigation guide for all docs
- **[docs/](docs/)** - Detailed technical documentation
  - API guides, configuration, LLM Judge, security, troubleshooting

---

## 🏆 Key Achievements

✅ **All 7 Core Requirements Implemented:**
1. ✅ Multi-method sensitive data detection (Regex, Luhn, NER)
2. ✅ Shape-preserving redaction with multiple methods
3. ✅ LLM-as-Judge validation with GPT-4o-mini (15% sampling)
4. ✅ Policy-as-code with YAML configuration
5. ✅ Warm decision cache with TTL
6. ✅ Security baseline (TLS, API keys, log sanitization)
7. ✅ Comprehensive observability (metrics, dashboard, tracing-ready)

✅ **Advanced Features:**
- Real-time metrics tracking with SQLite database
- Interactive Streamlit dashboard with Plotly visualizations
- JWT authentication and RBAC support
- Audit logging for compliance
- Rate limiting (60 req/min default)
- Format-Preserving Encryption (FPE) for PANs
- WebSocket support for real-time streaming

✅ **Production Ready:**
- 90% test pass rate (18/20 checks)
- Comprehensive test suite (100+ test cases)
- Detailed documentation (50+ pages)
- Deployment readiness report with evidence

---

## 🤝 Team & Contribution

**Developed for:** [Hackathon Name]  
**Team:** [Your Team Name]  
**Contact:** [Your Email/Contact]

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **OpenAI** - GPT-4o-mini for LLM-as-Judge validation
- **spaCy** - NER model for person name detection
- **FastAPI** - High-performance web framework
- **Streamlit** - Interactive dashboard framework

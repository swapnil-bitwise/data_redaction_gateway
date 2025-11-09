# 📚 Documentation Guide

**Quick reference for navigating project documentation**

---

## 🚀 Quick Start (5 minutes)

1. Read **[README.md](README.md)** - Project overview
2. Run the application using **[APPLICATION_RUN_GUIDE.md](APPLICATION_RUN_GUIDE.md)**
3. That's it! You're ready to go.

---

## 👥 Documentation by Audience

### For External Reviewers
1. **[README.md](README.md)** - What is this project?
2. **[DEPLOYMENT_READINESS_REPORT.md](DEPLOYMENT_READINESS_REPORT.md)** - Test results and evidence
3. **[APPLICATION_RUN_GUIDE.md](APPLICATION_RUN_GUIDE.md)** - How to run and verify
4. **[METRICS_SYSTEM_GUIDE.md](METRICS_SYSTEM_GUIDE.md)** - Metrics dashboard features

**Estimated Review Time:** 30-45 minutes

---

### For Developers
1. **[README.md](README.md)** - Architecture and features
2. **[APPLICATION_RUN_GUIDE.md](APPLICATION_RUN_GUIDE.md)** - Setup and configuration
3. **[SECURITY_IMPLEMENTATION_STATUS.md](SECURITY_IMPLEMENTATION_STATUS.md)** - Security features
4. **[docs/](docs/)** - Detailed technical documentation
   - [API endpoints](docs/api/)
   - [Configuration](docs/configuration/)
   - [LLM Judge](docs/llm_judge/)
   - [Security](docs/security/)

**Estimated Onboarding Time:** 1-2 hours

---

### For QA Teams
1. **[PRE_DEPLOYMENT_TEST_PLAN.md](PRE_DEPLOYMENT_TEST_PLAN.md)** - Structured test plan
2. **[DEPLOYMENT_READINESS_REPORT.md](DEPLOYMENT_READINESS_REPORT.md)** - Test results
3. **[test_suite/README.md](test_suite/README.md)** - Automated tests
4. **[APPLICATION_RUN_GUIDE.md](APPLICATION_RUN_GUIDE.md)** - Manual testing guide

**Test Execution Time:** 3 hours (following test plan)

---

## 📋 Essential Documentation Files

| File | Purpose | Audience |
|------|---------|----------|
| [README.md](README.md) | Project overview & quick start | Everyone |
| [APPLICATION_RUN_GUIDE.md](APPLICATION_RUN_GUIDE.md) | Complete setup & testing guide | Developers, QA |
| [METRICS_SYSTEM_GUIDE.md](METRICS_SYSTEM_GUIDE.md) | Metrics & dashboard documentation | Developers, Ops |
| [DEPLOYMENT_READINESS_REPORT.md](DEPLOYMENT_READINESS_REPORT.md) | Test results & evidence | Reviewers, QA |
| [PRE_DEPLOYMENT_TEST_PLAN.md](PRE_DEPLOYMENT_TEST_PLAN.md) | 3-hour test plan | QA |
| [SECURITY_IMPLEMENTATION_STATUS.md](SECURITY_IMPLEMENTATION_STATUS.md) | Security features | Security, DevOps |
| [dashboard/README.md](dashboard/README.md) | Dashboard usage guide | Ops, Developers |

---

## 📁 Documentation Structure

```
Root Documentation (Essential)
├── README.md                           ⭐ Start here
├── APPLICATION_RUN_GUIDE.md            🚀 How to run
├── METRICS_SYSTEM_GUIDE.md             📊 Metrics system
├── DEPLOYMENT_READINESS_REPORT.md      ✅ Test results
├── PRE_DEPLOYMENT_TEST_PLAN.md         📋 Test plan
└── SECURITY_IMPLEMENTATION_STATUS.md   🔐 Security

Dashboard Documentation
└── dashboard/README.md                 📊 Dashboard guide

Detailed Technical Docs
└── docs/
    ├── api/                            📚 API guides
    ├── configuration/                  ⚙️ Config guides
    ├── llm_judge/                      🤖 LLM Judge
    ├── security/                       🔐 Security
    ├── setup/                          🛠️ Setup
    └── archived/                       🗄️ Historical docs
```

---

## 🎯 Common Tasks

### Running the Application
```powershell
# Quick start
python main_modular.py

# Access API docs
http://localhost:8000/docs

# Start metrics dashboard
cd dashboard
streamlit run app.py
```
👉 See [APPLICATION_RUN_GUIDE.md](APPLICATION_RUN_GUIDE.md) for details

### Running Tests
```powershell
# Automated test suite
cd test_suite
python -m pytest test_all_endpoints.py -v

# Integration tests
python test_metrics_system.py
python test_redaction_metrics.py
```
👉 See [PRE_DEPLOYMENT_TEST_PLAN.md](PRE_DEPLOYMENT_TEST_PLAN.md) for full test plan

### Viewing Metrics
```powershell
# Generate sample data
python generate_sample_metrics.py --count 100

# Start dashboard
cd dashboard
streamlit run app.py

# Visit http://localhost:8501
```
👉 See [METRICS_SYSTEM_GUIDE.md](METRICS_SYSTEM_GUIDE.md) for comprehensive guide

---

## 🔍 Finding Specific Information

| Looking for... | Check this file |
|----------------|----------------|
| Project overview | [README.md](README.md) |
| How to run the app | [APPLICATION_RUN_GUIDE.md](APPLICATION_RUN_GUIDE.md) |
| API endpoints | [docs/api/API_ENDPOINTS_GUIDE.md](docs/api/API_ENDPOINTS_GUIDE.md) |
| Configuration | [docs/configuration/CONFIGURATION_GUIDE.md](docs/configuration/CONFIGURATION_GUIDE.md) |
| Security features | [SECURITY_IMPLEMENTATION_STATUS.md](SECURITY_IMPLEMENTATION_STATUS.md) |
| Test results | [DEPLOYMENT_READINESS_REPORT.md](DEPLOYMENT_READINESS_REPORT.md) |
| Metrics system | [METRICS_SYSTEM_GUIDE.md](METRICS_SYSTEM_GUIDE.md) |
| LLM Judge | [docs/llm_judge/](docs/llm_judge/) |
| Troubleshooting | [docs/setup/TROUBLESHOOTING.md](docs/setup/TROUBLESHOOTING.md) |

---

## 📝 Additional Resources

### Archived Documentation
Historical development files preserved in [docs/archived/](docs/archived/):
- Original problem statement
- Development status snapshots
- Implementation summaries
- TODO items for future work

**Note:** These are for reference only and may be outdated.

### Sample Data
Example inputs and configuration:
- [input/redaction_rules.yaml](input/redaction_rules.yaml) - Redaction rules
- [input/sample inputs and outputs.txt](input/sample%20inputs%20and%20outputs.txt) - Test data
- [config/config.yaml](config/config.yaml) - Main configuration

---

## ❓ Need Help?

1. **Check [APPLICATION_RUN_GUIDE.md](APPLICATION_RUN_GUIDE.md)** - Comprehensive guide with troubleshooting
2. **See [docs/setup/TROUBLESHOOTING.md](docs/setup/TROUBLESHOOTING.md)** - Common issues and solutions
3. **Review test examples** - [test_suite/](test_suite/) contains working examples

---

**Last Updated:** November 9, 2025  
**Project Status:** ✅ Production Ready

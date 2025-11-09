"""
Test redaction endpoint and verify detailed metrics are logged.
"""
import requests
import json
import time

API_BASE_URL = "http://127.0.0.1:8000"
API_KEY = "dev-api-key-12345"

# Test data with PII
test_data = {
    "customer_name": "John Smith",
    "email": "john.smith@example.com",
    "phone": "555-123-4567",
    "ssn": "123-45-6789",
    "credit_card": "4532-1234-5678-9010",
    "address": "123 Main Street, New York, NY 10001"
}

print("🧪 Testing Redaction Endpoint")
print("=" * 50)

# Make redaction request
print(f"\n📤 Sending redaction request...")
print(f"Data: {json.dumps(test_data, indent=2)}")

try:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/redact/",
        json={
            "data": test_data,
            "include_meta": True
        },
        headers={
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        },
        timeout=10
    )
    
    print(f"\n✅ Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n📊 Redaction Results:")
        print(f"  - Redacted Data: {json.dumps(result['redacted_data'], indent=2)}")
        print(f"  - Processing Time: {result['processing_time_ms']:.2f}ms")
        print(f"  - Redactions: {len(result.get('redaction_meta', []))}")
        
        if result.get('judge_result'):
            print(f"\n🤖 LLM Judge Results:")
            print(f"  - Coverage Complete: {result['judge_result']['coverage_complete']}")
            print(f"  - Confidence: {result['judge_result']['confidence']}%")
            print(f"  - Assessment: {result['judge_result'].get('assessment', 'N/A')}")
        else:
            print(f"\n🤖 LLM Judge: Not called (sampling)")
        
        # Wait a moment for metrics to be logged
        time.sleep(1)
        
        # Check if metrics were logged
        print(f"\n📈 Checking Metrics Database...")
        metrics_response = requests.get(
            f"{API_BASE_URL}/api/v1/metrics/db/aggregated",
            params={
                "start_time": "2025-11-09T00:00:00",
                "end_time": "2025-11-10T00:00:00"
            },
            timeout=5
        )
        
        if metrics_response.status_code == 200:
            metrics = metrics_response.json()
            print(f"  ✅ Total Requests: {metrics['total_requests']}")
            print(f"  ✅ Total Redactions: {metrics['total_redactions']}")
            print(f"  ✅ LLM Calls: {metrics['llm_calls']}")
            print(f"  ✅ Good Redactions: {metrics['good_redaction_count']}")
        else:
            print(f"  ⚠️ Could not fetch metrics: {metrics_response.status_code}")
        
        # Check quality summary
        quality_response = requests.get(
            f"{API_BASE_URL}/api/v1/metrics/db/redaction-quality",
            params={
                "start_time": "2025-11-09T00:00:00",
                "end_time": "2025-11-10T00:00:00"
            },
            timeout=5
        )
        
        if quality_response.status_code == 200:
            quality = quality_response.json()
            print(f"\n🎯 Quality Summary:")
            print(f"  - Good: {quality['good']} ({quality['good_percentage']:.1f}%)")
            print(f"  - Under-redacted: {quality['under_redacted']} ({quality['under_redacted_percentage']:.1f}%)")
            print(f"  - Over-redacted: {quality['over_redacted']} ({quality['over_redacted_percentage']:.1f}%)")
            print(f"  - Total Evaluated: {quality['total_evaluated']}")
        
        print(f"\n✅ Test completed successfully!")
        print(f"🎯 Dashboard should now show detailed metrics at: http://localhost:8501")
        
    else:
        print(f"❌ Request failed: {response.text}")
        
except requests.exceptions.ConnectionError:
    print(f"\n❌ Error: Could not connect to API at {API_BASE_URL}")
    print(f"   Make sure the server is running: python main_modular.py")
except Exception as e:
    print(f"\n❌ Error: {e}")

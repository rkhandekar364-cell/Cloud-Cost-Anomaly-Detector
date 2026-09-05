"""
Verification script for all 5 dashboard page API call bundles.
"""

import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000"

def get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    res = urllib.request.urlopen(req)
    return res.getcode(), json.loads(res.read())

def verify_pages():
    print("=== VERIFYING ALL 5 FRONTEND PAGE API BUNDLES OVER HTTP ===")

    # Page 1: Overview
    print("\n1. Overview Page Fetches:")
    for path in ["/api/data/summary", "/api/cost/daily-trend", "/api/cost/provider-breakdown", "/api/cost/service-breakdown", "/api/anomalies/summary", "/api/anomalies/top?limit=5", "/api/forecast/summary", "/api/insights"]:
        code, _ = get(path)
        print(f"   [OK] {path} -> {code}")

    # Page 2: Anomalies
    print("\n2. Anomalies Page Fetches:")
    for path in ["/api/anomalies?contamination=0.03", "/api/anomalies/0/analysis"]:
        code, _ = get(path)
        print(f"   [OK] {path} -> {code}")

    # Page 3: Forecast
    print("\n3. Forecast Page Fetches:")
    for path in ["/api/forecast/summary", "/api/forecast?days=30", "/api/cost/daily-trend", "/api/forecast/evaluation", "/api/forecast/services"]:
        code, _ = get(path)
        print(f"   [OK] {path} -> {code}")

    # Page 4: Cost Analysis
    print("\n4. Cost Analysis Page Fetches:")
    for path in ["/api/cost/service-breakdown", "/api/cost/provider-breakdown", "/api/cost/daily-trend", "/api/cost/drivers"]:
        code, _ = get(path)
        print(f"   [OK] {path} -> {code}")

    # Page 5: Recommendations
    print("\n5. Recommendations Page Fetches:")
    for path in ["/api/recommendations", "/api/cost/drivers", "/api/insights"]:
        code, _ = get(path)
        print(f"   [OK] {path} -> {code}")

    print("\nALL 5 PAGE FETCH BUNDLES VERIFIED WITH 200 OK! [OK]")

if __name__ == "__main__":
    verify_pages()

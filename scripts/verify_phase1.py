"""
Verification script for Phase 1 of Cloud Cost Anomaly Detector.
Tests dataset loading, validation service logic, cost service calculations, and all FastAPI endpoints.
"""

import sys
from pathlib import Path
import json

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.utils.dataset_loader import load_dataset, get_dataset_path
from app.services.validation_service import ValidationService
from app.services.cost_service import CostService
from fastapi.testclient import TestClient
from app.main import app

def run_tests():
    print("=== TEST 1: Dataset Loading ===")
    path = get_dataset_path()
    print(f"Dataset path: {path}")
    df = load_dataset()
    print(f"Dataset successfully loaded. Records: {len(df)}")
    assert len(df) >= 5000, f"Expected at least 5000 records, got {len(df)}"
    print("PASS: Dataset loaded successfully.\n")

    print("=== TEST 2: Data Validation Service ===")
    report = ValidationService.validate(df)
    print(f"Data Quality Score: {report['data_quality_score']}%")
    print(f"Overall Status: {report['overall_status']}")
    print(f"Passed Checks: {report['passed_checks']}/{len(report['details'])}")
    for detail in report['details']:
        print(f" - [{detail['status']}] {detail['check_name']}: {detail['message']}")
    assert report['data_quality_score'] > 80.0, "Quality score should be high for sample dataset"
    print("PASS: Validation service working as expected.\n")

    print("=== TEST 3: Cost Service Calculations ===")
    summary = CostService.get_summary(df)
    print("Summary:", json.dumps(summary, indent=2))
    assert summary['total_records'] == len(df)
    assert summary['number_of_cloud_providers'] == 3
    
    service_breakdown = CostService.get_service_breakdown(df)
    print(f"Services Count: {len(service_breakdown['breakdown'])}")
    
    provider_breakdown = CostService.get_provider_breakdown(df)
    print(f"Providers Count: {len(provider_breakdown['breakdown'])}")
    
    daily_trend = CostService.get_daily_trend(df)
    print(f"Daily Trend Days: {daily_trend['total_days']}")
    print("PASS: Cost service calculations verified.\n")

    print("=== TEST 4: FastAPI Endpoint Testing ===")
    client = TestClient(app)

    # 1. GET /
    res = client.get("/")
    assert res.status_code == 200
    print("GET / ->", res.json())

    # 2. GET /api/health
    res = client.get("/api/health")
    assert res.status_code == 200
    print("GET /api/health ->", res.json())

    # 3. POST /api/data/validate
    res = client.post("/api/data/validate")
    assert res.status_code == 200
    val_res = res.json()
    print("POST /api/data/validate -> Score:", val_res["data_quality_score"])

    # 4. GET /api/data/summary
    res = client.get("/api/data/summary")
    assert res.status_code == 200
    sum_res = res.json()
    print("GET /api/data/summary -> Total Spend: $", sum_res["total_cloud_spend"])

    # 5. GET /api/cost/service-breakdown
    res = client.get("/api/cost/service-breakdown")
    assert res.status_code == 200
    svc_res = res.json()
    print("GET /api/cost/service-breakdown -> Services:", len(svc_res["breakdown"]))

    # 6. GET /api/cost/provider-breakdown
    res = client.get("/api/cost/provider-breakdown")
    assert res.status_code == 200
    prv_res = res.json()
    print("GET /api/cost/provider-breakdown -> Providers:", len(prv_res["breakdown"]))

    # 7. GET /api/cost/daily-trend
    res = client.get("/api/cost/daily-trend")
    assert res.status_code == 200
    trd_res = res.json()
    print("GET /api/cost/daily-trend -> Days:", trd_res["total_days"])

    print("\nALL TESTS PASSED SUCCESSFULLY! [OK]")

if __name__ == "__main__":
    run_tests()

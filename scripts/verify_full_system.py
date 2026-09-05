"""
Full Backend Verification Script (Phases 1 to 4).
Tests all 15 FastAPI endpoints and business services.
"""

import sys
from pathlib import Path
import json

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

def run_backend_verification():
    client = TestClient(app)
    print("=== STARTING FULL BACKEND API VERIFICATION ===")

    endpoints = [
        ("/", 200, "Root Status"),
        ("/api/health", 200, "Health Check"),
        ("/api/data/summary", 200, "Dataset Summary"),
        ("/api/cost/service-breakdown", 200, "Service Breakdown"),
        ("/api/cost/provider-breakdown", 200, "Provider Breakdown"),
        ("/api/cost/daily-trend", 200, "Daily Trend"),
        ("/api/anomalies", 200, "Anomalies Detection"),
        ("/api/anomalies/summary", 200, "Anomalies Summary"),
        ("/api/anomalies/top", 200, "Top Anomalies"),
        ("/api/anomalies/0/analysis", 200, "Root Cause Analysis (ID 0)"),
        ("/api/forecast", 200, "Cost Forecast"),
        ("/api/forecast/summary", 200, "Forecast Summary"),
        ("/api/forecast/services", 200, "Service Forecasts"),
        ("/api/forecast/evaluation", 200, "Forecast Evaluation"),
        ("/api/recommendations", 200, "Cost Recommendations"),
        ("/api/cost/drivers", 200, "Cost Drivers"),
        ("/api/insights", 200, "Business Insights")
    ]

    for path, expected_status, name in endpoints:
        res = client.get(path)
        assert res.status_code == expected_status, f"{name} ({path}) failed with status {res.status_code}: {res.text}"
        print(f"[OK] {name:<30} -> {path:<32} Status: {res.status_code}")

    # Validate POST endpoint
    res_post = client.post("/api/data/validate")
    assert res_post.status_code == 200
    print(f"[OK] {'Data Validation':<30} -> {'POST /api/data/validate':<32} Status: {res_post.status_code}")

    # Check backtest metrics print
    eval_res = client.get("/api/forecast/evaluation").json()
    print("\n--- Forecast Evaluation Backtesting ---")
    print(f"Model: {eval_res['model_type']}")
    print(f"Training Days: {eval_res['training_days']}, Held Out Days: {eval_res['held_out_days']}")
    print(f"MAE: ${eval_res['mae']}, RMSE: ${eval_res['rmse']}, MAPE: {eval_res['mape']}%")

    print("\nALL 17 API ENDPOINTS VERIFIED SUCCESSFULLY! [OK]")

if __name__ == "__main__":
    run_backend_verification()

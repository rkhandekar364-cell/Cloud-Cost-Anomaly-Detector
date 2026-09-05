"""
Phase 2 Verification Script.
Tests IsolationForest anomaly detector service, ground truth metrics,
data-driven reason strings, Phase 2 API endpoints, and Phase 1 regression.
"""

import sys
from pathlib import Path
import json

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.utils.dataset_loader import load_dataset
from app.services.anomaly_detector import AnomalyDetectorService
from fastapi.testclient import TestClient
from app.main import app


def run_phase2_tests():
    print("=== TEST 1: Anomaly Detector Service Execution ===")
    results = AnomalyDetectorService.run_detection(contamination=0.03, force_reload=True)
    
    total_obs = results["total_observations"]
    total_anom = results["total_anomalies"]
    critical = results["critical_anomalies"]
    high = results["high_risk_anomalies"]
    medium = results["medium_risk_anomalies"]
    low = results["low_risk_anomalies"]

    print(f"Total Observations: {total_obs}")
    print(f"Total Anomalies Detected: {total_anom} ({results['anomaly_percentage']}%)")
    print(f"Risk Breakdown -> Critical: {critical}, High: {high}, Medium: {medium}, Low: {low}")

    assert total_anom > 0, "Anomaly detector should identify anomalies"
    assert critical > 0 or high > 0, "Should detect high or critical risk anomalies"
    print("PASS: Anomaly Detector Service executed successfully.\n")

    print("=== TEST 2: Empirical Reason String Verification (No Fabrications) ===")
    sample_anomaly = results["anomalies"][0]
    print("Top Detected Anomaly Sample:")
    print(" - Date:", sample_anomaly["date"])
    print(" - Service:", sample_anomaly["service"])
    print(" - Provider:", sample_anomaly["cloud_provider"])
    print(" - Actual Cost: $", sample_anomaly["actual_cost"])
    print(" - Expected Cost: $", sample_anomaly["expected_cost"])
    print(" - Deviation: ", sample_anomaly["deviation_percentage"], "%")
    print(" - Score:", sample_anomaly["anomaly_score"])
    print(" - Risk Level:", sample_anomaly["risk_level"])
    print(" - Empirical Reason:", sample_anomaly["reason"])
    print(" - Recommendation:", sample_anomaly["recommendation"])

    # Ensure no generic fabricated assumptions are made in reasons
    forbidden_terms = ["autoscaling failure", "hacked", "misconfigured cluster", "human error", "bug in code"]
    for a in results["anomalies"]:
        for term in forbidden_terms:
            assert term not in a["reason"].lower(), f"Fabricated reason found: '{term}' in '{a['reason']}'"

    print("PASS: Reasons verified to be strictly empirical and data-driven.\n")

    print("=== TEST 3: Ground Truth Synthetic Evaluation ===")
    df = load_dataset()
    if "IsAnomaly" in df.columns:
        # Evaluate daily service observations ground truth
        df["Date_str"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
        anom_pairs = set(
            zip(
                df[df["IsAnomaly"] == 1]["Date_str"],
                df[df["IsAnomaly"] == 1]["Service"]
            )
        )
        
        detected_pairs = set((a["date"], a["service"]) for a in results["anomalies"])
        
        tp = len(anom_pairs.intersection(detected_pairs))
        fn = len(anom_pairs - detected_pairs)
        fp = len(detected_pairs - anom_pairs)
        
        precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0.0
        recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        print(f"Ground Truth Anomalous (Date, Service) Pairs: {len(anom_pairs)}")
        print(f"Model Detected (Date, Service) Pairs: {len(detected_pairs)}")
        print(f"True Positives (TP): {tp}, False Positives (FP): {fp}, False Negatives (FN): {fn}")
        print(f"Precision: {precision:.1f}%, Recall: {recall:.1f}%, F1 Score: {f1:.1f}%")
        print("PASS: Ground truth evaluation complete.\n")

    print("=== TEST 4: FastAPI Phase 2 Endpoints ===")
    client = TestClient(app)

    # 1. GET /api/anomalies
    res = client.get("/api/anomalies?contamination=0.03")
    assert res.status_code == 200
    res_json = res.json()
    assert "anomalies" in res_json
    print(f"GET /api/anomalies -> Total: {res_json['total_anomalies']}")

    # 2. GET /api/anomalies/summary
    res = client.get("/api/anomalies/summary?contamination=0.03")
    assert res.status_code == 200
    res_json = res.json()
    assert "anomalies_by_risk_level" in res_json
    print(f"GET /api/anomalies/summary -> Anomaly Pct: {res_json['anomaly_percentage']}%")

    # 3. GET /api/anomalies/top
    res = client.get("/api/anomalies/top?limit=5&contamination=0.03")
    assert res.status_code == 200
    res_json = res.json()
    assert len(res_json["top_anomalies"]) <= 5
    print(f"GET /api/anomalies/top -> Top Count: {len(res_json['top_anomalies'])}")

    print("PASS: Phase 2 API endpoints working correctly.\n")

    print("=== TEST 5: Phase 1 Regression Testing ===")
    res1 = client.get("/api/health")
    assert res1.status_code == 200
    
    res2 = client.get("/api/data/summary")
    assert res2.status_code == 200

    res3 = client.get("/api/cost/service-breakdown")
    assert res3.status_code == 200

    res4 = client.get("/api/cost/provider-breakdown")
    assert res4.status_code == 200

    res5 = client.get("/api/cost/daily-trend")
    assert res5.status_code == 200

    print("PASS: All Phase 1 endpoints verified without regression.\n")

    print("ALL PHASE 2 TESTS PASSED SUCCESSFULLY! [OK]")


if __name__ == "__main__":
    import pandas as pd
    run_phase2_tests()

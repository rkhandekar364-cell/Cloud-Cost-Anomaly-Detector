# Pytest API Endpoints Test Suite
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app
from app.utils.dataset_loader import load_dataset

client = TestClient(app)


def test_root_status():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "version" in data


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["dataset_loaded"] is True
    assert data["record_count"] >= 5000


def test_data_validation():
    response = client.post("/api/data/validate")
    assert response.status_code == 200
    data = response.json()
    assert "data_quality_score" in data
    assert data["data_quality_score"] > 80.0
    assert data["overall_status"] == "HEALTHY"
    assert len(data["details"]) == 7


def test_data_summary():
    response = client.get("/api/data/summary")
    assert response.status_code == 200
    data = response.json()
    df = load_dataset()

    assert data["total_records"] == len(df)
    assert round(data["total_cloud_spend"], 2) == round(float(df["TotalCost"].sum()), 2)
    assert data["number_of_cloud_providers"] == int(df["CloudProvider"].nunique())
    assert data["number_of_services"] == int(df["Service"].nunique())


def test_service_breakdown():
    response = client.get("/api/cost/service-breakdown")
    assert response.status_code == 200
    data = response.json()
    assert "breakdown" in data
    assert len(data["breakdown"]) > 0
    total_pct = sum(item["percentage"] for item in data["breakdown"])
    assert 99.0 <= total_pct <= 101.0


def test_provider_breakdown():
    response = client.get("/api/cost/provider-breakdown")
    assert response.status_code == 200
    data = response.json()
    assert len(data["breakdown"]) == 3
    providers = [item["provider"] for item in data["breakdown"]]
    assert "AWS" in providers
    assert "Azure" in providers
    assert "GCP" in providers


def test_daily_trend():
    response = client.get("/api/cost/daily-trend")
    assert response.status_code == 200
    data = response.json()
    assert data["total_days"] >= 300
    assert len(data["trend"]) == data["total_days"]


def test_anomalies_detection():
    response = client.get("/api/anomalies?contamination=0.03")
    assert response.status_code == 200
    data = response.json()
    assert data["total_anomalies"] > 0
    assert data["critical_anomalies"] >= 0
    assert len(data["anomalies"]) == data["total_anomalies"]


def test_anomalies_summary():
    response = client.get("/api/anomalies/summary?contamination=0.03")
    assert response.status_code == 200
    data = response.json()
    assert "anomalies_by_risk_level" in data
    assert "anomalies_by_service" in data


def test_top_anomalies():
    response = client.get("/api/anomalies/top?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["top_anomalies"]) <= 5


def test_forecast():
    response = client.get("/api/forecast?days=30")
    assert response.status_code == 200
    data = response.json()
    assert data["forecast_days"] == 30
    assert len(data["forecast"]) == 30
    assert data["trend"] in ["increasing", "decreasing", "stable"]


def test_forecast_summary():
    response = client.get("/api/forecast/summary")
    assert response.status_code == 200
    data = response.json()
    assert "predicted_next_30_day_spend" in data
    assert "explanation" in data


def test_forecast_services():
    response = client.get("/api/forecast/services")
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    assert len(data["services"]) > 0


def test_forecast_evaluation():
    response = client.get("/api/forecast/evaluation")
    assert response.status_code == 200
    data = response.json()
    assert "mae" in data
    assert "rmse" in data
    assert "mape" in data
    assert data["held_out_days"] == 30


def test_anomaly_analysis():
    response = client.get("/api/anomalies/0/analysis")
    assert response.status_code == 200
    data = response.json()
    assert "anomaly" in data
    assert "root_cause" in data
    assert len(data["root_cause"]["contributing_factors"]) > 0


def test_anomaly_analysis_invalid_id():
    response = client.get("/api/anomalies/99999/analysis")
    assert response.status_code == 404


def test_recommendations():
    response = client.get("/api/recommendations")
    assert response.status_code == 200
    data = response.json()
    assert data["total_recommendations"] > 0
    assert len(data["recommendations"]) == data["total_recommendations"]


def test_cost_drivers():
    response = client.get("/api/cost/drivers")
    assert response.status_code == 200
    data = response.json()
    assert len(data["drivers"]) > 0
    assert data["drivers"][0]["rank"] == 1


def test_business_insights():
    response = client.get("/api/insights")
    assert response.status_code == 200
    data = response.json()
    assert data["insights_count"] > 0
    assert len(data["insights"]) == data["insights_count"]

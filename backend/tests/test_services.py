# Pytest Business Services Unit Test Suite
import sys
from pathlib import Path
import pandas as pd
import numpy as np

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.validation_service import ValidationService
from app.services.cost_service import CostService
from app.services.anomaly_detector import AnomalyDetectorService
from app.services.forecasting import HoltLinearForecaster, ForecastingService
from app.services.root_cause import RootCauseAnalysisService
from app.services.recommendations import RecommendationEngineService
from app.services.insights import BusinessInsightsService
from app.services.billing_normalizer import BillingNormalizerService


def test_validation_missing_columns():
    invalid_df = pd.DataFrame({"Date": ["2025-09-01"], "TotalCost": [100.0]})
    report = ValidationService.validate(invalid_df)
    assert report["overall_status"] == "CRITICAL"
    assert report["data_quality_score"] == 0.0
    assert report["failed_checks"] == 1


def test_validation_negative_costs():
    df = pd.DataFrame({
        "Date": ["2025-09-01"],
        "CloudProvider": ["AWS"],
        "Service": ["EC2"],
        "Region": ["us-east-1"],
        "Resource": ["i-123456"],
        "UsageType": ["BoxUsage"],
        "UsageQuantity": [10.0],
        "UnitCost": [0.1],
        "TotalCost": [-50.0]
    })
    report = ValidationService.validate(df)
    assert report["data_quality_score"] < 100.0
    neg_check = next(c for c in report["details"] if c["check_name"] == "negative_costs")
    assert neg_check["status"] == "FAILED"


def test_billing_normalizer_aws():
    aws_df = pd.DataFrame({
        "UsageStartDate": ["2026-01-01"],
        "lineItem/ProductCode": ["AmazonEC2"],
        "availabilityRegion": ["us-east-1"],
        "lineItem/UnblendedCost": [15.50]
    })
    norm_df, mappings, unmapped = BillingNormalizerService.normalize(aws_df)
    assert "Date" in norm_df.columns
    assert "Service" in norm_df.columns
    assert "TotalCost" in norm_df.columns
    assert norm_df["Service"].iloc[0] == "AmazonEC2"
    assert norm_df["TotalCost"].iloc[0] == 15.50
    assert len(mappings) >= 3


def test_billing_normalizer_missing_required():
    bad_df = pd.DataFrame({"Region": ["us-east-1"]})
    try:
        BillingNormalizerService.normalize(bad_df)
        assert False, "Should raise ValueError for missing required fields"
    except ValueError as e:
        assert "missing required minimum fields" in str(e)


def test_holt_linear_forecaster():
    series = np.array([10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0])
    model = HoltLinearForecaster(alpha=0.3, beta=0.1)
    model.fit(series)
    preds = model.predict(5)
    assert len(preds) == 5
    assert all(p > 0 for p in preds)
    assert preds[4] > preds[0]


def test_anomaly_detector_service():
    results = AnomalyDetectorService.run_detection(contamination=0.03, force_reload=True)
    assert results["total_observations"] > 0
    assert results["total_anomalies"] > 0
    for anomaly in results["anomalies"]:
        assert anomaly["actual_cost"] >= 0
        assert anomaly["risk_level"] in ["Critical", "High", "Medium", "Low"]
        assert len(anomaly["reason"]) > 0


def test_forecasting_backtest():
    eval_res = ForecastingService.evaluate_model(holdout_days=30, reload=True)
    assert eval_res["training_days"] > 0
    assert eval_res["held_out_days"] == 30
    assert eval_res["mae"] >= 0
    assert eval_res["rmse"] >= 0
    assert eval_res["mape"] >= 0


def test_root_cause_analysis():
    analysis = RootCauseAnalysisService.analyze_anomaly(anomaly_id=0)
    assert "anomaly" in analysis
    assert "root_cause" in analysis
    assert len(analysis["root_cause"]["summary"]) > 0


def test_recommendation_engine():
    recs = RecommendationEngineService.get_recommendations()
    assert recs["total_recommendations"] > 0
    for r in recs["recommendations"]:
        assert r["priority"] in ["Critical", "High", "Medium", "Low"]
        assert len(r["action"]) > 0


def test_business_insights():
    insights = BusinessInsightsService.get_insights()
    assert insights["insights_count"] == 6
    assert len(insights["insights"]) == 6

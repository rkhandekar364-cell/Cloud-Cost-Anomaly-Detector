"""
Test Suite Runner for Backend APIs and Services.
Executes test functions in test_api.py and test_services.py.
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from tests.test_api import (
    test_root_status,
    test_health_check,
    test_data_validation,
    test_data_summary,
    test_service_breakdown,
    test_provider_breakdown,
    test_daily_trend,
    test_anomalies_detection,
    test_anomalies_summary,
    test_top_anomalies,
    test_forecast,
    test_forecast_summary,
    test_forecast_services,
    test_forecast_evaluation,
    test_anomaly_analysis,
    test_anomaly_analysis_invalid_id,
    test_recommendations,
    test_cost_drivers,
    test_business_insights
)

from tests.test_services import (
    test_validation_missing_columns,
    test_validation_negative_costs,
    test_billing_normalizer_aws,
    test_billing_normalizer_missing_required,
    test_holt_linear_forecaster,
    test_anomaly_detector_service,
    test_forecasting_backtest,
    test_root_cause_analysis,
    test_recommendation_engine,
    test_business_insights as test_services_business_insights
)

def run_all():
    print("================ BACKEND TEST SUITE RUNNER ================")
    
    api_tests = [
        ("test_root_status", test_root_status),
        ("test_health_check", test_health_check),
        ("test_data_validation", test_data_validation),
        ("test_data_summary", test_data_summary),
        ("test_service_breakdown", test_service_breakdown),
        ("test_provider_breakdown", test_provider_breakdown),
        ("test_daily_trend", test_daily_trend),
        ("test_anomalies_detection", test_anomalies_detection),
        ("test_anomalies_summary", test_anomalies_summary),
        ("test_top_anomalies", test_top_anomalies),
        ("test_forecast", test_forecast),
        ("test_forecast_summary", test_forecast_summary),
        ("test_forecast_services", test_forecast_services),
        ("test_forecast_evaluation", test_forecast_evaluation),
        ("test_anomaly_analysis", test_anomaly_analysis),
        ("test_anomaly_analysis_invalid_id", test_anomaly_analysis_invalid_id),
        ("test_recommendations", test_recommendations),
        ("test_cost_drivers", test_cost_drivers),
        ("test_business_insights", test_business_insights)
    ]

    service_tests = [
        ("test_validation_missing_columns", test_validation_missing_columns),
        ("test_validation_negative_costs", test_validation_negative_costs),
        ("test_billing_normalizer_aws", test_billing_normalizer_aws),
        ("test_billing_normalizer_missing_required", test_billing_normalizer_missing_required),
        ("test_holt_linear_forecaster", test_holt_linear_forecaster),
        ("test_anomaly_detector_service", test_anomaly_detector_service),
        ("test_forecasting_backtest", test_forecasting_backtest),
        ("test_root_cause_analysis", test_root_cause_analysis),
        ("test_recommendation_engine", test_recommendation_engine),
        ("test_services_business_insights", test_services_business_insights)
    ]

    passed = 0
    failed = 0

    print("\n--- API Endpoints Tests ---")
    for name, func in api_tests:
        try:
            func()
            print(f" [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f" [FAIL] {name}: {e}")
            failed += 1

    print("\n--- Service Unit & Edge Case Tests ---")
    for name, func in service_tests:
        try:
            func()
            print(f" [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f" [FAIL] {name}: {e}")
            failed += 1

    print(f"\n================ TEST SUMMARY ================")
    print(f"Total Tests: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    assert failed == 0, f"{failed} test(s) failed!"
    print("\nALL BACKEND TESTS PASSED SUCCESSFULLY! [OK]")

if __name__ == "__main__":
    run_all()

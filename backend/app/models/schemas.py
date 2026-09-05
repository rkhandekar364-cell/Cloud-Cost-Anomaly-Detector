"""
Pydantic response models for API endpoints (Phases 1 to 6.5).
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# --- PHASE 1 SCHEMAS ---

class StatusResponse(BaseModel):
    status: str = Field(..., example="online")
    message: str = Field(..., example="Cloud Cost Anomaly Detector API is running")
    version: str = Field(..., example="1.0.0")


class HealthResponse(BaseModel):
    status: str = Field(..., example="healthy")
    dataset_loaded: bool = Field(...)
    record_count: int = Field(...)
    dataset_path: str = Field(...)


class ValidationDetail(BaseModel):
    check_name: str = Field(...)
    status: str = Field(...)
    message: str = Field(...)
    issue_count: int = Field(0)


class ValidationReport(BaseModel):
    data_quality_score: float = Field(...)
    total_records: int = Field(...)
    overall_status: str = Field(...)
    passed_checks: int = Field(...)
    failed_checks: int = Field(...)
    details: List[ValidationDetail] = Field(...)


class DateRange(BaseModel):
    min_date: str = Field(...)
    max_date: str = Field(...)


class SummaryResponse(BaseModel):
    total_records: int = Field(...)
    total_cloud_spend: float = Field(...)
    average_daily_spend: float = Field(...)
    number_of_cloud_providers: int = Field(...)
    number_of_services: int = Field(...)
    date_range: DateRange = Field(...)


class ServiceBreakdownItem(BaseModel):
    service: str = Field(...)
    total_cost: float = Field(...)
    percentage: float = Field(...)


class ServiceBreakdownResponse(BaseModel):
    breakdown: List[ServiceBreakdownItem] = Field(...)
    total_spend: float = Field(...)


class ProviderBreakdownItem(BaseModel):
    provider: str = Field(...)
    total_cost: float = Field(...)
    percentage: float = Field(...)


class ProviderBreakdownResponse(BaseModel):
    breakdown: List[ProviderBreakdownItem] = Field(...)
    total_spend: float = Field(...)


class DailyTrendItem(BaseModel):
    date: str = Field(...)
    total_cost: float = Field(...)


class DailyTrendResponse(BaseModel):
    trend: List[DailyTrendItem] = Field(...)
    total_days: int = Field(...)


# --- PHASE 2: ANOMALY DETECTION SCHEMAS ---

class AnomalyItem(BaseModel):
    date: str = Field(...)
    service: str = Field(...)
    cloud_provider: str = Field(...)
    region: str = Field(...)
    actual_cost: float = Field(...)
    expected_cost: float = Field(...)
    deviation_percentage: float = Field(...)
    anomaly_score: float = Field(...)
    risk_level: str = Field(...)
    reason: str = Field(...)
    recommendation: str = Field(...)


class AnomaliesResponse(BaseModel):
    total_observations: int = Field(...)
    total_anomalies: int = Field(...)
    critical_anomalies: int = Field(...)
    high_risk_anomalies: int = Field(...)
    medium_risk_anomalies: int = Field(...)
    low_risk_anomalies: int = Field(...)
    contamination_used: float = Field(...)
    anomalies: List[AnomalyItem] = Field(...)


class AnomaliesSummaryResponse(BaseModel):
    total_observations: int = Field(...)
    total_anomalies: int = Field(...)
    anomaly_percentage: float = Field(...)
    anomalies_by_service: Dict[str, int] = Field(...)
    anomalies_by_provider: Dict[str, int] = Field(...)
    anomalies_by_risk_level: Dict[str, int] = Field(...)


class TopAnomaliesResponse(BaseModel):
    total_anomalies: int = Field(...)
    top_anomalies: List[AnomalyItem] = Field(...)


# --- PHASE 3: FORECASTING SCHEMAS ---

class ForecastItem(BaseModel):
    date: str = Field(...)
    predicted_cost: float = Field(...)


class ForecastResponse(BaseModel):
    historical_days: int = Field(...)
    forecast_days: int = Field(...)
    forecast_total: float = Field(...)
    average_daily_forecast: float = Field(...)
    trend: str = Field(...)
    forecast: List[ForecastItem] = Field(...)


class ForecastSummaryResponse(BaseModel):
    current_period_spend: float = Field(...)
    previous_period_spend: float = Field(...)
    predicted_next_30_day_spend: float = Field(...)
    percentage_change: float = Field(...)
    spending_trend: str = Field(...)
    risk_interpretation: str = Field(...)
    explanation: str = Field(...)


class ServiceForecastItem(BaseModel):
    service: str = Field(...)
    status: str = Field(...)
    historical_days: int = Field(...)
    predicted_30_day_spend: float = Field(...)
    trend_percentage: Optional[float] = Field(None)
    message: str = Field(...)


class ServiceForecastResponse(BaseModel):
    total_services: int = Field(...)
    services: List[ServiceForecastItem] = Field(...)


class ForecastEvaluationResponse(BaseModel):
    training_days: int = Field(...)
    held_out_days: int = Field(...)
    mae: float = Field(...)
    rmse: float = Field(...)
    mape: float = Field(...)
    model_type: str = Field(...)
    limitations: str = Field(...)


# --- PHASE 4: ROOT CAUSE & RECOMMENDATION SCHEMAS ---

class ContributingFactor(BaseModel):
    rank: int = Field(...)
    dimension: str = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    impact_amount: float = Field(...)


class RootCauseDetail(BaseModel):
    summary: str = Field(...)
    contributing_factors: List[ContributingFactor] = Field(...)


class AnomalyAnalysisResponse(BaseModel):
    anomaly: AnomalyItem = Field(...)
    root_cause: RootCauseDetail = Field(...)


class RecommendationItem(BaseModel):
    service: str = Field(...)
    provider: str = Field(...)
    region: str = Field(...)
    priority: str = Field(...)
    category: str = Field(...)
    reason: str = Field(...)
    action: str = Field(...)


class RecommendationsResponse(BaseModel):
    total_recommendations: int = Field(...)
    critical: int = Field(...)
    high: int = Field(...)
    medium: int = Field(...)
    low: int = Field(...)
    recommendations: List[RecommendationItem] = Field(...)


class CostDriverItem(BaseModel):
    service: str = Field(...)
    cost_change: float = Field(...)
    recent_period_spend: float = Field(...)
    previous_period_spend: float = Field(...)
    contribution_percentage: float = Field(...)
    rank: int = Field(...)


class CostDriversResponse(BaseModel):
    drivers: List[CostDriverItem] = Field(...)


class BusinessInsightItem(BaseModel):
    id: str = Field(...)
    title: str = Field(...)
    evidence: str = Field(...)
    metric: str = Field(...)
    category: str = Field(...)


class BusinessInsightsResponse(BaseModel):
    insights_count: int = Field(...)
    insights: List[BusinessInsightItem] = Field(...)


# --- PHASE 6.5: DATA IMPORT SCHEMAS ---

class ColumnMappingItem(BaseModel):
    canonical_field: str = Field(...)
    source_column: str = Field(...)
    confidence: float = Field(...)


class UploadPreviewResponse(BaseModel):
    filename: str = Field(...)
    file_size_bytes: int = Field(...)
    total_records: int = Field(...)
    detected_columns: List[str] = Field(...)
    unmapped_columns: List[str] = Field(...)
    mappings: List[ColumnMappingItem] = Field(...)
    sample_records: List[Dict[str, Any]] = Field(...)
    data_quality: ValidationReport = Field(...)


class ActiveDatasetResponse(BaseModel):
    source: str = Field(..., example="demo")
    filename: str = Field(..., example="cloud_billing_sample.csv")
    record_count: int = Field(...)
    date_range: DateRange = Field(...)
    providers: int = Field(...)
    services: int = Field(...)
    data_quality_score: float = Field(...)


class ActivateDatasetRequest(BaseModel):
    filename: str = Field(..., example="uploaded_aws_billing.csv")

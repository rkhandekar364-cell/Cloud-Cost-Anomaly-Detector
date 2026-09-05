"""
FastAPI Router Endpoints (Phases 1 to 6.5).
Defines endpoints for status, health, validation, analytics, anomaly detection,
forecasting, root-cause analysis, recommendations, insights, and real data import.
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException, status, Query, Path as FastPath, UploadFile, File
from app.models.schemas import (
    StatusResponse,
    HealthResponse,
    ValidationReport,
    SummaryResponse,
    ServiceBreakdownResponse,
    ProviderBreakdownResponse,
    DailyTrendResponse,
    AnomaliesResponse,
    AnomaliesSummaryResponse,
    TopAnomaliesResponse,
    ForecastResponse,
    ForecastSummaryResponse,
    ServiceForecastResponse,
    ForecastEvaluationResponse,
    AnomalyAnalysisResponse,
    RecommendationsResponse,
    CostDriversResponse,
    BusinessInsightsResponse,
    UploadPreviewResponse,
    ActiveDatasetResponse,
    ActivateDatasetRequest
)
from app.utils.dataset_loader import (
    load_dataset,
    get_dataset_path,
    get_active_metadata,
    set_active_dataset,
    restore_demo_dataset,
    UPLOADS_DIR
)
from app.services.validation_service import ValidationService
from app.services.cost_service import CostService
from app.services.anomaly_detector import AnomalyDetectorService
from app.services.forecasting import ForecastingService
from app.services.root_cause import RootCauseAnalysisService
from app.services.recommendations import RecommendationEngineService
from app.services.insights import BusinessInsightsService
from app.services.billing_normalizer import BillingNormalizerService

router = APIRouter()


# --- PHASE 1: STATUS & ANALYTICS ---

@router.get("/", response_model=StatusResponse, tags=["Status"])
def get_root_status():
    """Basic API status check."""
    return StatusResponse(
        status="online",
        message="Cloud Cost Anomaly Detector API is running",
        version="1.0.0"
    )


@router.get("/api/health", response_model=HealthResponse, tags=["Status"])
def get_health():
    """Health check verifying dataset availability and record count."""
    try:
        df = load_dataset()
        return HealthResponse(
            status="healthy",
            dataset_loaded=True,
            record_count=len(df),
            dataset_path=str(get_dataset_path())
        )
    except Exception:
        return HealthResponse(
            status="degraded",
            dataset_loaded=False,
            record_count=0,
            dataset_path=str(get_dataset_path())
        )


@router.post("/api/data/validate", response_model=ValidationReport, tags=["Data Quality"])
def validate_dataset():
    """Run data quality and validation checks on current active dataset."""
    try:
        df = load_dataset()
        report = ValidationService.validate(df)
        return ValidationReport(**report)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute dataset validation: {str(e)}"
        )


@router.get("/api/data/summary", response_model=SummaryResponse, tags=["Analytics"])
def get_summary():
    """Return overall summary metrics of the active billing dataset."""
    try:
        df = load_dataset()
        summary = CostService.get_summary(df)
        return SummaryResponse(**summary)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate dataset summary: {str(e)}"
        )


@router.get("/api/cost/service-breakdown", response_model=ServiceBreakdownResponse, tags=["Analytics"])
def get_service_breakdown():
    """Return total cloud spend breakdown grouped by Service."""
    try:
        df = load_dataset()
        breakdown = CostService.get_service_breakdown(df)
        return ServiceBreakdownResponse(**breakdown)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate service breakdown: {str(e)}"
        )


@router.get("/api/cost/provider-breakdown", response_model=ProviderBreakdownResponse, tags=["Analytics"])
def get_provider_breakdown():
    """Return total cloud spend breakdown grouped by CloudProvider."""
    try:
        df = load_dataset()
        breakdown = CostService.get_provider_breakdown(df)
        return ProviderBreakdownResponse(**breakdown)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate provider breakdown: {str(e)}"
        )


@router.get("/api/cost/daily-trend", response_model=DailyTrendResponse, tags=["Analytics"])
def get_daily_trend():
    """Return daily cloud spending time-series trend."""
    try:
        df = load_dataset()
        trend = CostService.get_daily_trend(df)
        return DailyTrendResponse(**trend)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate daily spending trend: {str(e)}"
        )


# --- PHASE 2: AI ANOMALY DETECTION ---

@router.get("/api/anomalies", response_model=AnomaliesResponse, tags=["AI Anomaly Detection"])
def get_anomalies(
    contamination: float = Query(0.03, ge=0.01, le=0.15, description="IsolationForest contamination parameter")
):
    """Run machine-learning anomaly detection using IsolationForest."""
    try:
        results = AnomalyDetectorService.run_detection(contamination=contamination)
        return AnomaliesResponse(**results)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect cloud cost anomalies: {str(e)}"
        )


@router.get("/api/anomalies/summary", response_model=AnomaliesSummaryResponse, tags=["AI Anomaly Detection"])
def get_anomalies_summary(
    contamination: float = Query(0.03, ge=0.01, le=0.15, description="IsolationForest contamination parameter")
):
    """Return high-level summary metrics of detected anomalies."""
    try:
        results = AnomalyDetectorService.run_detection(contamination=contamination)
        return AnomaliesSummaryResponse(
            total_observations=results["total_observations"],
            total_anomalies=results["total_anomalies"],
            anomaly_percentage=results["anomaly_percentage"],
            anomalies_by_service=results["anomalies_by_service"],
            anomalies_by_provider=results["anomalies_by_provider"],
            anomalies_by_risk_level=results["anomalies_by_risk_level"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate anomaly summary: {str(e)}"
        )


@router.get("/api/anomalies/top", response_model=TopAnomaliesResponse, tags=["AI Anomaly Detection"])
def get_top_anomalies(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of top anomalies to return"),
    contamination: float = Query(0.03, ge=0.01, le=0.15, description="IsolationForest contamination parameter")
):
    """Return the top most significant cost anomalies ordered by severity."""
    try:
        results = AnomalyDetectorService.run_detection(contamination=contamination)
        top_list = results["anomalies"][:limit]
        return TopAnomaliesResponse(
            total_anomalies=len(results["anomalies"]),
            top_anomalies=top_list
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch top anomalies: {str(e)}"
        )


# --- PHASE 3: TIME-SERIES COST FORECASTING ---

@router.get("/api/forecast", response_model=ForecastResponse, tags=["Forecasting"])
def get_forecast(
    days: int = Query(30, ge=7, le=90, description="Forecast horizon in days")
):
    """Generate daily time-series forecast for total cloud spend."""
    try:
        results = ForecastingService.get_forecast(forecast_days=days)
        return ForecastResponse(**results)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate forecast: {str(e)}"
        )


@router.get("/api/forecast/summary", response_model=ForecastSummaryResponse, tags=["Forecasting"])
def get_forecast_summary():
    """Return executive summary of cost forecast, period comparisons, and trend interpretation."""
    try:
        results = ForecastingService.get_summary()
        return ForecastSummaryResponse(**results)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate forecast summary: {str(e)}"
        )


@router.get("/api/forecast/services", response_model=ServiceForecastResponse, tags=["Forecasting"])
def get_service_forecasts():
    """Return 30-day projected cost per cloud service (requiring >= 30 historical days)."""
    try:
        results = ForecastingService.get_service_forecasts()
        return ServiceForecastResponse(**results)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate service forecasts: {str(e)}"
        )


@router.get("/api/forecast/evaluation", response_model=ForecastEvaluationResponse, tags=["Forecasting"])
def get_forecast_evaluation():
    """Return 30-day holdout backtesting evaluation metrics (MAE, RMSE, MAPE)."""
    try:
        results = ForecastingService.evaluate_model(holdout_days=30)
        return ForecastEvaluationResponse(**results)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate forecast model: {str(e)}"
        )


# --- PHASE 4: ROOT CAUSE, RECOMMENDATIONS & INSIGHTS ---

@router.get("/api/anomalies/{anomaly_id}/analysis", response_model=AnomalyAnalysisResponse, tags=["Root Cause Analysis"])
def analyze_anomaly_root_cause(
    anomaly_id: int = FastPath(..., ge=0, description="Zero-based index of anomaly")
):
    """Perform evidence-based root-cause analysis for a specific anomaly."""
    try:
        analysis = RootCauseAnalysisService.analyze_anomaly(anomaly_id=anomaly_id)
        return AnomalyAnalysisResponse(**analysis)
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Anomaly ID {anomaly_id} not found."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze anomaly root cause: {str(e)}"
        )


@router.get("/api/recommendations", response_model=RecommendationsResponse, tags=["Optimization"])
def get_recommendations():
    """Return prioritized non-destructive cloud cost optimization recommendations."""
    try:
        results = RecommendationEngineService.get_recommendations()
        return RecommendationsResponse(**results)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch recommendations: {str(e)}"
        )


@router.get("/api/cost/drivers", response_model=CostDriversResponse, tags=["Optimization"])
def get_cost_drivers():
    """Return major service drivers contributing to spending changes."""
    try:
        results = BusinessInsightsService.get_cost_drivers()
        return CostDriversResponse(**results)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch cost drivers: {str(e)}"
        )


@router.get("/api/insights", response_model=BusinessInsightsResponse, tags=["Optimization"])
def get_business_insights():
    """Return numerical evidence-based executive business insights."""
    try:
        results = BusinessInsightsService.get_insights()
        return BusinessInsightsResponse(**results)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch business insights: {str(e)}"
        )


# --- PHASE 6.5: DATA IMPORT & ACTIVE DATASET MANAGEMENT ---

@router.post("/api/data/upload", response_model=UploadPreviewResponse, tags=["Data Import"])
async def upload_billing_file(file: UploadFile = File(...)):
    """
    Upload a cloud billing file (CSV, XLSX, XLS).
    Normalizes columns, calculates confidence mapping, and returns a preview without auto-activating.
    """
    filename = file.filename or "uploaded_billing_export.csv"
    contents = await file.read()

    # Validate file format
    ext = Path(filename).suffix.lower()
    if ext not in [".csv", ".xlsx", ".xls"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Only CSV, XLSX, and XLS files are supported."
        )

    try:
        df_raw = BillingNormalizerService.read_file(contents, filename)
        norm_df, mappings, unmapped = BillingNormalizerService.normalize(df_raw)

        # Save normalized dataframe safely to uploads directory
        safe_filename = f"normalized_{Path(filename).stem}.csv"
        saved_path = UPLOADS_DIR / safe_filename
        norm_df.to_csv(saved_path, index=False)

        val_report = ValidationService.validate(norm_df)
        sample_records = norm_df.head(5).to_dict(orient="records")

        return UploadPreviewResponse(
            filename=safe_filename,
            file_size_bytes=len(contents),
            total_records=len(norm_df),
            detected_columns=list(df_raw.columns),
            unmapped_columns=unmapped,
            mappings=mappings,
            sample_records=sample_records,
            data_quality=val_report
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse and normalize billing file: {str(e)}"
        )


@router.post("/api/data/activate", response_model=ActiveDatasetResponse, tags=["Data Import"])
def activate_dataset(payload: ActivateDatasetRequest):
    """Explicitly activate a validated uploaded dataset file across backend pipelines."""
    filepath = UPLOADS_DIR / payload.filename
    if not filepath.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Uploaded file '{payload.filename}' not found in upload directory."
        )

    try:
        set_active_dataset(
            source="uploaded",
            filepath=filepath,
            filename=payload.filename
        )
        meta = get_active_metadata()
        return ActiveDatasetResponse(**meta)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate dataset: {str(e)}"
        )


@router.get("/api/data/active", response_model=ActiveDatasetResponse, tags=["Data Import"])
def get_active_dataset_metadata():
    """Return metadata for the currently active dataset."""
    try:
        meta = get_active_metadata()
        return ActiveDatasetResponse(**meta)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch active dataset metadata: {str(e)}"
        )


@router.post("/api/data/restore-demo", response_model=ActiveDatasetResponse, tags=["Data Import"])
def restore_demo():
    """Restore the synthetic demo dataset as active across all backend pipelines."""
    try:
        restore_demo_dataset()
        meta = get_active_metadata()
        return ActiveDatasetResponse(**meta)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restore demo dataset: {str(e)}"
        )

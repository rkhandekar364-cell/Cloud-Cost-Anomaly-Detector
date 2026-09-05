"""
Dataset Loader & Active Dataset State Manager.
Manages authoritative active dataset state ('demo' vs 'uploaded').
Supports thread-safe cached dataset loading and dataset switching.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import pandas as pd
import threading

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DEMO_DATASET_PATH = BASE_DIR / "data" / "cloud_billing_sample.csv"
UPLOADS_DIR = BASE_DIR / "data" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Global Active State
_lock = threading.Lock()
_active_source: str = "demo"  # "demo" or "uploaded"
_active_path: Path = DEMO_DATASET_PATH
_active_filename: str = "cloud_billing_sample.csv"
_cached_df: Optional[pd.DataFrame] = None


def get_active_source() -> str:
    """Returns 'demo' or 'uploaded'."""
    return _active_source


def get_active_filename() -> str:
    """Returns filename of active dataset."""
    return _active_filename


def get_dataset_path() -> Path:
    """Returns absolute path to currently active CSV dataset."""
    return _active_path


def clear_all_service_caches():
    """Clears all cached predictions across ML, forecasting, and analytical services."""
    from app.services.anomaly_detector import AnomalyDetectorService
    from app.services.forecasting import ForecastingService
    
    AnomalyDetectorService._cache.clear()
    ForecastingService._cache.clear()


def set_active_dataset(source: str, filepath: Path, filename: str, df: Optional[pd.DataFrame] = None):
    """Activates a new dataset state and invalidates all service caches."""
    global _active_source, _active_path, _active_filename, _cached_df
    with _lock:
        _active_source = source
        _active_path = filepath
        _active_filename = filename
        _cached_df = df if df is not None else pd.read_csv(filepath)
        clear_all_service_caches()


def restore_demo_dataset():
    """Restores the synthetic demo dataset as active."""
    set_active_dataset("demo", DEMO_DATASET_PATH, "cloud_billing_sample.csv")


def load_dataset(reload: bool = False) -> pd.DataFrame:
    """
    Loads and caches the currently active cloud billing DataFrame.
    """
    global _cached_df
    with _lock:
        if _cached_df is not None and not reload:
            return _cached_df

        path = get_dataset_path()
        if not path.exists():
            raise FileNotFoundError(
                f"Active dataset not found at '{path}'."
            )

        df = pd.read_csv(path)
        _cached_df = df
        return _cached_df


def get_active_metadata() -> Dict[str, Any]:
    """Returns metadata for the currently active dataset."""
    df = load_dataset()
    from app.services.validation_service import ValidationService
    val_report = ValidationService.validate(df)

    min_date = str(df["Date"].min()) if "Date" in df.columns else "N/A"
    max_date = str(df["Date"].max()) if "Date" in df.columns else "N/A"

    return {
        "source": _active_source,
        "filename": _active_filename,
        "record_count": len(df),
        "date_range": {
            "min_date": min_date,
            "max_date": max_date
        },
        "providers": int(df["CloudProvider"].nunique()) if "CloudProvider" in df.columns else 1,
        "services": int(df["Service"].nunique()) if "Service" in df.columns else 1,
        "data_quality_score": val_report["data_quality_score"]
    }

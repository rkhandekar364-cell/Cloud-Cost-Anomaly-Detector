"""
Cloud Cost Forecasting Service.
Implements Holt's Linear Exponential Smoothing time-series forecasting,
service-level predictions, trend classification, and 30-day backtesting evaluation.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.utils.dataset_loader import load_dataset


class HoltLinearForecaster:
    """Holt's Linear Exponential Smoothing Model for time-series forecasting."""

    def __init__(self, alpha: float = 0.2, beta: float = 0.1):
        self.alpha = alpha
        self.beta = beta
        self.level: float = 0.0
        self.trend: float = 0.0

    def fit(self, series: np.ndarray):
        if len(series) < 2:
            self.level = series[0] if len(series) == 1 else 0.0
            self.trend = 0.0
            return

        # Initialize Level and Trend
        self.level = float(series[0])
        # Initial trend estimate based on initial window slope
        init_window = min(7, len(series) - 1)
        self.trend = float((series[init_window] - series[0]) / init_window)

        for val in series:
            prev_level = self.level
            prev_trend = self.trend
            self.level = self.alpha * float(val) + (1.0 - self.alpha) * (prev_level + prev_trend)
            self.trend = self.beta * (self.level - prev_level) + (1.0 - self.beta) * prev_trend

    def predict(self, steps: int) -> np.ndarray:
        h = np.arange(1, steps + 1)
        predictions = self.level + h * self.trend
        # Clamp negative forecasts to 0.0 (costs cannot be negative)
        return np.maximum(0.0, predictions)


class ForecastingService:
    """Service handling multi-cloud cost forecasting, service projections, and backtest evaluation."""

    _cache: Dict[str, Any] = {}

    @classmethod
    def get_forecast(cls, forecast_days: int = 30, reload: bool = False) -> Dict[str, Any]:
        cache_key = f"forecast_{forecast_days}"
        if not reload and cache_key in cls._cache:
            return cls._cache[cache_key]

        df_raw = load_dataset(reload=reload)
        if df_raw.empty:
            raise ValueError("Dataset is empty. Cannot generate forecast.")

        df = df_raw.copy()
        df["Date"] = pd.to_datetime(df["Date"])

        # 1. Daily Aggregation & Continuous Frequency Reindexing
        daily = df.groupby("Date")["TotalCost"].sum().reset_index()
        daily.sort_values(by="Date", inplace=True)
        daily.set_index("Date", inplace=True)

        full_idx = pd.date_range(start=daily.index.min(), end=daily.index.max(), freq="D")
        daily = daily.reindex(full_idx)
        daily["TotalCost"] = daily["TotalCost"].interpolate(method="linear").fillna(0.0)

        historical_series = daily["TotalCost"].values
        historical_days = len(historical_series)

        # 2. Fit Forecaster & Predict
        model = HoltLinearForecaster(alpha=0.25, beta=0.08)
        model.fit(historical_series)
        future_preds = model.predict(forecast_days)

        last_date = daily.index.max()
        future_dates = [last_date + timedelta(days=i + 1) for i in range(forecast_days)]

        forecast_list = [
            {
                "date": d.strftime("%Y-%m-%d"),
                "predicted_cost": round(float(pred), 2)
            }
            for d, pred in zip(future_dates, future_preds)
        ]

        forecast_total = round(float(np.sum(future_preds)), 2)
        avg_daily_forecast = round(float(np.mean(future_preds)), 2)

        # 3. Trend Classification & Percentage Change
        recent_window = min(30, historical_days)
        recent_30_avg = float(np.mean(historical_series[-recent_window:]))
        pct_change = ((avg_daily_forecast - recent_30_avg) / recent_30_avg * 100) if recent_30_avg > 0 else 0.0

        if pct_change >= 3.0:
            trend_str = "increasing"
        elif pct_change <= -3.0:
            trend_str = "decreasing"
        else:
            trend_str = "stable"

        result = {
            "historical_days": historical_days,
            "forecast_days": forecast_days,
            "forecast_total": forecast_total,
            "average_daily_forecast": avg_daily_forecast,
            "trend": trend_str,
            "forecast": forecast_list
        }

        cls._cache[cache_key] = result
        return result

    @classmethod
    def get_summary(cls, reload: bool = False) -> Dict[str, Any]:
        df_raw = load_dataset(reload=reload)
        df = df_raw.copy()
        df["Date"] = pd.to_datetime(df["Date"])
        daily = df.groupby("Date")["TotalCost"].sum().sort_index()

        total_days = len(daily)
        window = min(30, total_days // 2)

        current_period_spend = round(float(daily.iloc[-window:].sum()), 2)
        prev_period_spend = round(float(daily.iloc[-2 * window:-window].sum()), 2)

        forecast_res = cls.get_forecast(forecast_days=30, reload=reload)
        predicted_next_30 = forecast_res["forecast_total"]

        pct_change = (
            ((predicted_next_30 - current_period_spend) / current_period_spend * 100)
            if current_period_spend > 0 else 0.0
        )
        pct_change = round(pct_change, 2)

        trend = forecast_res["trend"]

        if trend == "increasing":
            risk = "High"
            explanation = (
                f"Cloud spending is projected to increase by {abs(pct_change)}% over the next 30 days "
                f"(${predicted_next_30:,.2f} projected vs ${current_period_spend:,.2f} current period)."
            )
        elif trend == "decreasing":
            risk = "Low"
            explanation = (
                f"Cloud spending is projected to decrease by {abs(pct_change)}% over the next 30 days "
                f"(${predicted_next_30:,.2f} projected vs ${current_period_spend:,.2f} current period)."
            )
        else:
            risk = "Low"
            explanation = (
                f"Projected spending is broadly stable compared with the recent baseline "
                f"(${predicted_next_30:,.2f} projected vs ${current_period_spend:,.2f} current period)."
            )

        return {
            "current_period_spend": current_period_spend,
            "previous_period_spend": prev_period_spend,
            "predicted_next_30_day_spend": predicted_next_30,
            "percentage_change": pct_change,
            "spending_trend": trend,
            "risk_interpretation": risk,
            "explanation": explanation
        }

    @classmethod
    def get_service_forecasts(cls, reload: bool = False) -> Dict[str, Any]:
        df_raw = load_dataset(reload=reload)
        df = df_raw.copy()
        df["Date"] = pd.to_datetime(df["Date"])

        services = df["Service"].unique()
        service_results = []

        for svc in services:
            svc_df = df[df["Service"] == svc].groupby("Date")["TotalCost"].sum().sort_index()
            obs_days = len(svc_df)

            if obs_days < 30:
                service_results.append({
                    "service": str(svc),
                    "status": "insufficient_data",
                    "historical_days": obs_days,
                    "predicted_30_day_spend": 0.0,
                    "message": f"Service requires at least 30 historical days of data (found {obs_days})."
                })
            else:
                full_idx = pd.date_range(start=svc_df.index.min(), end=svc_df.index.max(), freq="D")
                svc_daily = svc_df.reindex(full_idx).interpolate(method="linear").fillna(0.0)

                model = HoltLinearForecaster(alpha=0.25, beta=0.08)
                model.fit(svc_daily.values)
                svc_preds = model.predict(30)
                pred_30_total = round(float(np.sum(svc_preds)), 2)

                recent_30_avg = float(np.mean(svc_daily.values[-30:]))
                pred_avg = float(np.mean(svc_preds))
                pct = ((pred_avg - recent_30_avg) / recent_30_avg * 100) if recent_30_avg > 0 else 0.0

                service_results.append({
                    "service": str(svc),
                    "status": "available",
                    "historical_days": obs_days,
                    "predicted_30_day_spend": pred_30_total,
                    "trend_percentage": round(pct, 2),
                    "message": "30-day forecast generated successfully."
                })

        service_results.sort(key=lambda x: x["predicted_30_day_spend"], reverse=True)
        return {
            "total_services": len(services),
            "services": service_results
        }

    @classmethod
    def evaluate_model(cls, holdout_days: int = 30, reload: bool = False) -> Dict[str, Any]:
        df_raw = load_dataset(reload=reload)
        df = df_raw.copy()
        df["Date"] = pd.to_datetime(df["Date"])

        daily = df.groupby("Date")["TotalCost"].sum().sort_index()
        full_idx = pd.date_range(start=daily.index.min(), end=daily.index.max(), freq="D")
        daily = daily.reindex(full_idx).interpolate(method="linear").fillna(0.0)

        series = daily.values
        if len(series) <= holdout_days + 14:
            raise ValueError("Insufficient data to perform 30-day holdout backtesting.")

        train_series = series[:-holdout_days]
        test_series = series[-holdout_days:]

        model = HoltLinearForecaster(alpha=0.25, beta=0.08)
        model.fit(train_series)
        preds = model.predict(holdout_days)

        # Metrics
        mae = float(np.mean(np.abs(test_series - preds)))
        rmse = float(np.sqrt(np.mean((test_series - preds) ** 2)))
        
        # Avoid division by zero in MAPE
        nonzero_mask = test_series > 0.01
        if np.any(nonzero_mask):
            mape = float(np.mean(np.abs((test_series[nonzero_mask] - preds[nonzero_mask]) / test_series[nonzero_mask])) * 100)
        else:
            mape = 0.0

        return {
            "training_days": len(train_series),
            "held_out_days": holdout_days,
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "mape": round(mape, 2),
            "model_type": "Holt Exponential Smoothing (Additive Trend)",
            "limitations": (
                "Synthetic billing data contains step-changes and abrupt usage anomalies. "
                "Statistical time-series models smooth past trends and assume baseline continuity, "
                "which may underestimate sudden unannounced infrastructure scaling or architectural changes."
            )
        }

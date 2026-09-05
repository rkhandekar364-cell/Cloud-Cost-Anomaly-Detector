"""
Cost Drivers & Business Insights Service.
Calculates major spending drivers and numerical business insights derived from historical billing data.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
from app.utils.dataset_loader import load_dataset
from app.services.anomaly_detector import AnomalyDetectorService
from app.services.forecasting import ForecastingService


class BusinessInsightsService:
    """Service providing cost drivers analysis and numerical business insights."""

    @classmethod
    def get_cost_drivers(cls) -> Dict[str, Any]:
        df = load_dataset().copy()
        df["Date"] = pd.to_datetime(df["Date"])
        daily = df.groupby(["Date", "Service"])["TotalCost"].sum().reset_index()

        max_date = daily["Date"].max()
        cutoff_30 = max_date - pd.Timedelta(days=30)
        cutoff_60 = max_date - pd.Timedelta(days=60)

        recent_df = daily[daily["Date"] > cutoff_30]
        prev_df = daily[(daily["Date"] <= cutoff_30) & (daily["Date"] > cutoff_60)]

        recent_spend = recent_df.groupby("Service")["TotalCost"].sum()
        prev_spend = prev_df.groupby("Service")["TotalCost"].sum()

        services = list(set(recent_spend.index).union(set(prev_spend.index)))
        drivers = []

        total_abs_diff = 0.0
        for svc in services:
            r_cost = float(recent_spend.get(svc, 0.0))
            p_cost = float(prev_spend.get(svc, 0.0))
            diff = r_cost - p_cost
            total_abs_diff += abs(diff)

        for svc in services:
            r_cost = float(recent_spend.get(svc, 0.0))
            p_cost = float(prev_spend.get(svc, 0.0))
            diff = r_cost - p_cost
            contrib_pct = (abs(diff) / total_abs_diff * 100) if total_abs_diff > 0 else 0.0

            drivers.append({
                "service": str(svc),
                "cost_change": round(diff, 2),
                "recent_period_spend": round(r_cost, 2),
                "previous_period_spend": round(p_cost, 2),
                "contribution_percentage": round(contrib_pct, 2)
            })

        drivers.sort(key=lambda x: abs(x["cost_change"]), reverse=True)

        for idx, d in enumerate(drivers):
            d["rank"] = idx + 1

        return {"drivers": drivers}

    @classmethod
    def get_insights(cls) -> Dict[str, Any]:
        df = load_dataset().copy()
        total_spend = float(df["TotalCost"].sum())

        # 1. Largest spending service
        service_spend = df.groupby("Service")["TotalCost"].sum().sort_values(ascending=False)
        top_svc = service_spend.index[0]
        top_svc_spend = float(service_spend.iloc[0])
        top_svc_pct = (top_svc_spend / total_spend * 100) if total_spend > 0 else 0.0

        # 2. Fastest growing service
        drivers_res = cls.get_cost_drivers()
        drivers = drivers_res["drivers"]
        fastest_svc = drivers[0]["service"] if drivers else top_svc
        fastest_change = drivers[0]["cost_change"] if drivers else 0.0

        # 3. Largest cost anomaly
        anom_res = AnomalyDetectorService.run_detection(contamination=0.03)
        anomalies = anom_res["anomalies"]
        largest_anom = max(anomalies, key=lambda x: x["actual_cost"]) if anomalies else None

        # 4. Highest cost region
        region_spend = df.groupby("Region")["TotalCost"].sum().sort_values(ascending=False)
        top_region = region_spend.index[0]
        top_region_spend = float(region_spend.iloc[0])

        # 5. Highest risk provider
        prv_anom_counts = anom_res["anomalies_by_provider"]
        top_prv = max(prv_anom_counts, key=prv_anom_counts.get) if prv_anom_counts else "AWS"

        # 6. Projected spending trend
        forecast_res = ForecastingService.get_forecast(forecast_days=30)
        proj_spend = forecast_res["forecast_total"]

        insights_list = [
            {
                "id": "largest_service",
                "title": "Largest Spending Service",
                "evidence": f"{top_svc} is the largest spending service, accounting for {top_svc_pct:.1f}% of total cloud spend (${top_svc_spend:,.2f}).",
                "metric": f"${top_svc_spend:,.2f}",
                "category": "Cost Concentration"
            },
            {
                "id": "fastest_growing",
                "title": "Fastest-Growing Service Driver",
                "evidence": f"{fastest_svc} represents the largest 30-day net spending increase with a change of +${fastest_change:,.2f}.",
                "metric": f"+${fastest_change:,.2f}",
                "category": "Spending Velocity"
            },
            {
                "id": "largest_anomaly",
                "title": "Largest Cost Anomaly Detected",
                "evidence": f"Peak anomaly detected on {largest_anom['date']} for {largest_anom['service']} with actual cost of ${largest_anom['actual_cost']:,.2f} (+{largest_anom['deviation_percentage']}% above baseline)." if largest_anom else "No severe anomalies.",
                "metric": f"${largest_anom['actual_cost']:,.2f}" if largest_anom else "$0",
                "category": "Anomaly Detection"
            },
            {
                "id": "highest_cost_region",
                "title": "Highest Spending Region",
                "evidence": f"Region {top_region} incurred the highest cumulative expenditure across all providers at ${top_region_spend:,.2f}.",
                "metric": f"${top_region_spend:,.2f}",
                "category": "Geographic Allocation"
            },
            {
                "id": "highest_risk_provider",
                "title": "Highest Anomaly Concentration Provider",
                "evidence": f"Provider {top_prv} holds the highest number of detected anomalous observations ({prv_anom_counts.get(top_prv, 0)} anomalies).",
                "metric": f"{prv_anom_counts.get(top_prv, 0)} anomalies",
                "category": "Provider Risk"
            },
            {
                "id": "projected_spend",
                "title": "30-Day Forecast Horizon",
                "evidence": f"Total predicted cloud spending for the next 30 days is ${proj_spend:,.2f} (trend: {forecast_res['trend']}).",
                "metric": f"${proj_spend:,.2f}",
                "category": "Forecasting"
            }
        ]

        return {
            "insights_count": len(insights_list),
            "insights": insights_list
        }

"""
Cost Analysis Service.
Executes aggregation and analytical metrics on cloud billing data.
"""

from typing import Dict, Any, List
import pandas as pd


class CostService:
    """Service providing core cloud cost analytical calculations."""

    @staticmethod
    def get_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates dataset summary metrics."""
        total_records = len(df)
        total_spend = float(df["TotalCost"].sum())
        
        unique_days = df["Date"].nunique()
        avg_daily_spend = float(total_spend / unique_days) if unique_days > 0 else 0.0

        num_providers = int(df["CloudProvider"].nunique())
        num_services = int(df["Service"].nunique())
        
        min_date = str(df["Date"].min())
        max_date = str(df["Date"].max())

        return {
            "total_records": total_records,
            "total_cloud_spend": round(total_spend, 2),
            "average_daily_spend": round(avg_daily_spend, 2),
            "number_of_cloud_providers": num_providers,
            "number_of_services": num_services,
            "date_range": {
                "min_date": min_date,
                "max_date": max_date
            }
        }

    @staticmethod
    def get_service_breakdown(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates total spending breakdown grouped by Service."""
        total_spend = float(df["TotalCost"].sum())
        grouped = df.groupby("Service")["TotalCost"].sum().reset_index()
        grouped.sort_values(by="TotalCost", ascending=False, inplace=True)

        breakdown: List[Dict[str, Any]] = []
        for _, row in grouped.iterrows():
            cost = float(row["TotalCost"])
            pct = (cost / total_spend * 100) if total_spend > 0 else 0.0
            breakdown.append({
                "service": str(row["Service"]),
                "total_cost": round(cost, 2),
                "percentage": round(pct, 2)
            })

        return {
            "breakdown": breakdown,
            "total_spend": round(total_spend, 2)
        }

    @staticmethod
    def get_provider_breakdown(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates total spending breakdown grouped by CloudProvider."""
        total_spend = float(df["TotalCost"].sum())
        grouped = df.groupby("CloudProvider")["TotalCost"].sum().reset_index()
        grouped.sort_values(by="TotalCost", ascending=False, inplace=True)

        breakdown: List[Dict[str, Any]] = []
        for _, row in grouped.iterrows():
            cost = float(row["TotalCost"])
            pct = (cost / total_spend * 100) if total_spend > 0 else 0.0
            breakdown.append({
                "provider": str(row["CloudProvider"]),
                "total_cost": round(cost, 2),
                "percentage": round(pct, 2)
            })

        return {
            "breakdown": breakdown,
            "total_spend": round(total_spend, 2)
        }

    @staticmethod
    def get_daily_trend(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates daily total spend time series."""
        grouped = df.groupby("Date")["TotalCost"].sum().reset_index()
        grouped.sort_values(by="Date", ascending=True, inplace=True)

        trend: List[Dict[str, Any]] = []
        for _, row in grouped.iterrows():
            trend.append({
                "date": str(row["Date"]),
                "total_cost": round(float(row["TotalCost"]), 2)
            })

        return {
            "trend": trend,
            "total_days": len(trend)
        }

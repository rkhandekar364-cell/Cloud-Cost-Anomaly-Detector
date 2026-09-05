"""
Root Cause Analysis Service.
Performs empirical, evidence-based investigation on detected cloud cost anomalies.
"""

from typing import Dict, Any, List, Optional
from app.services.anomaly_detector import AnomalyDetectorService
from app.utils.dataset_loader import load_dataset
import pandas as pd


class RootCauseAnalysisService:
    """Service for investigating anomaly root causes using empirical billing metrics."""

    @classmethod
    def analyze_anomaly(cls, anomaly_id: int) -> Dict[str, Any]:
        results = AnomalyDetectorService.run_detection(contamination=0.03)
        anomalies = results["anomalies"]

        if anomaly_id < 0 or anomaly_id >= len(anomalies):
            raise IndexError(f"Anomaly ID {anomaly_id} out of range (total anomalies: {len(anomalies)}).")

        anomaly = anomalies[anomaly_id]
        
        # Load raw dataset for regional / service level contextual comparison
        df = load_dataset()
        df["Date_str"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

        anom_date = anomaly["date"]
        anom_service = anomaly["service"]
        anom_provider = anomaly["cloud_provider"]
        anom_region = anomaly["region"]

        # Filter date & service subset
        date_subset = df[df["Date_str"] == anom_date]
        total_date_spend = float(date_subset["TotalCost"].sum()) if not date_subset.empty else 1.0

        service_date_subset = date_subset[date_subset["Service"] == anom_service]
        service_date_spend = float(service_date_subset["TotalCost"].sum()) if not service_date_subset.empty else anomaly["actual_cost"]

        service_cost_share = (service_date_spend / total_date_spend * 100) if total_date_spend > 0 else 0.0

        # Region contribution for this service on this date
        region_date_subset = service_date_subset[service_date_subset["Region"] == anom_region]
        region_spend = float(region_date_subset["TotalCost"].sum()) if not region_date_subset.empty else service_date_spend
        region_share = (region_spend / service_date_spend * 100) if service_date_spend > 0 else 100.0

        # Build empirical ranked contributing factors
        factors = []
        rank = 1

        dev_pct = anomaly["deviation_percentage"]
        actual_cost = anomaly["actual_cost"]
        expected_cost = anomaly["expected_cost"]
        cost_diff = actual_cost - expected_cost

        # Factor 1: Service cost jump
        factors.append({
            "rank": rank,
            "dimension": "Service",
            "title": f"{anom_service} Spending Deviation",
            "description": f"{anom_service} spending increased by {dev_pct:.1f}% (${actual_cost:,.2f} vs expected baseline ${expected_cost:,.2f}).",
            "impact_amount": round(cost_diff, 2)
        })
        rank += 1

        # Factor 2: Regional share
        factors.append({
            "rank": rank,
            "dimension": "Region",
            "title": f"Regional Concentration ({anom_region})",
            "description": f"The region {anom_region} accounted for {region_share:.1f}% of the total {anom_service} spend on {anom_date}.",
            "impact_amount": round(region_spend, 2)
        })
        rank += 1

        # Factor 3: Multi-cloud share
        factors.append({
            "rank": rank,
            "dimension": "CloudProvider",
            "title": f"Provider Cost Weight ({anom_provider})",
            "description": f"{anom_service} under {anom_provider} represented {service_cost_share:.1f}% of total daily cloud spend on {anom_date}.",
            "impact_amount": round(service_date_spend, 2)
        })

        summary = (
            f"Anomaly investigation for {anom_service} ({anom_provider}, {anom_region}) on {anom_date}: "
            f"Cost increased by {dev_pct:.1f}% above baseline (+${cost_diff:,.2f}), primarily concentrated in {anom_region}."
        )

        return {
            "anomaly": anomaly,
            "root_cause": {
                "summary": summary,
                "contributing_factors": factors
            }
        }

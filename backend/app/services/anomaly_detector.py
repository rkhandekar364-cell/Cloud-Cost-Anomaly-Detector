"""
AI Cost Anomaly Detector Service.
Implements feature engineering, Scikit-Learn IsolationForest anomaly detection,
risk classification, and empirical data-driven explainability.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from app.utils.dataset_loader import load_dataset


class AnomalyDetectorService:
    """Service for training IsolationForest and returning explainable cloud cost anomalies."""

    _cache: Dict[float, Dict[str, Any]] = {}

    @classmethod
    def run_detection(cls, contamination: float = 0.03, force_reload: bool = False) -> Dict[str, Any]:
        """
        Runs feature engineering, model training, risk scoring, and reason generation.
        Caches results per contamination rate.
        """
        contamination = max(0.01, min(0.15, float(contamination)))
        
        if not force_reload and contamination in cls._cache:
            return cls._cache[contamination]

        df_raw = load_dataset(reload=force_reload)

        # Basic error checks
        required_cols = ["Date", "CloudProvider", "Service", "Region", "UsageQuantity", "UnitCost", "TotalCost"]
        missing = [c for c in required_cols if c not in df_raw.columns]
        if missing:
            raise ValueError(f"Dataset missing required columns for ML: {missing}")

        if df_raw.empty:
            raise ValueError("Dataset is empty. Cannot perform anomaly detection.")

        df = df_raw.copy()
        df["Date"] = pd.to_datetime(df["Date"])
        df.sort_values(by="Date", inplace=True)

        # 1. Service/Date Level Aggregation
        # Aggregating to (Date, CloudProvider, Service, Region) observations
        agg_df = df.groupby(["Date", "CloudProvider", "Service", "Region"]).agg(
            actual_cost=("TotalCost", "sum"),
            usage_quantity=("UsageQuantity", "sum"),
            unit_cost=("UnitCost", "mean")
        ).reset_index()

        # Daily total cloud spend across ALL services (for service_cost_share)
        daily_total_all = agg_df.groupby("Date")["actual_cost"].sum().reset_index().rename(
            columns={"actual_cost": "total_daily_spend"}
        )
        agg_df = pd.merge(agg_df, daily_total_all, on="Date", how="left")

        # 2. Feature Engineering per Service
        agg_df.sort_values(by=["Service", "Date"], inplace=True)

        # Rolling 7-day and 30-day baselines per service
        agg_df["rolling_7_day_cost"] = agg_df.groupby("Service")["actual_cost"].transform(
            lambda x: x.shift(1).rolling(window=7, min_periods=1).mean()
        )
        agg_df["rolling_30_day_cost"] = agg_df.groupby("Service")["actual_cost"].transform(
            lambda x: x.shift(1).rolling(window=30, min_periods=1).mean()
        )
        agg_df["rolling_7_day_usage"] = agg_df.groupby("Service")["usage_quantity"].transform(
            lambda x: x.shift(1).rolling(window=7, min_periods=1).mean()
        )
        agg_df["rolling_7_day_unit_cost"] = agg_df.groupby("Service")["unit_cost"].transform(
            lambda x: x.shift(1).rolling(window=7, min_periods=1).mean()
        )

        # Fill initial NaNs with current values for shift(1) start of series
        agg_df["rolling_7_day_cost"] = agg_df["rolling_7_day_cost"].fillna(agg_df["actual_cost"])
        agg_df["rolling_30_day_cost"] = agg_df["rolling_30_day_cost"].fillna(agg_df["actual_cost"])
        agg_df["rolling_7_day_usage"] = agg_df["rolling_7_day_usage"].fillna(agg_df["usage_quantity"])
        agg_df["rolling_7_day_unit_cost"] = agg_df["rolling_7_day_unit_cost"].fillna(agg_df["unit_cost"])

        # Cost and usage percentage changes vs 7-day baseline
        agg_df["cost_change_percentage"] = (
            (agg_df["actual_cost"] - agg_df["rolling_7_day_cost"]) /
            np.maximum(0.01, agg_df["rolling_7_day_cost"]) * 100
        )
        agg_df["usage_change_percentage"] = (
            (agg_df["usage_quantity"] - agg_df["rolling_7_day_usage"]) /
            np.maximum(0.01, agg_df["rolling_7_day_usage"]) * 100
        )
        agg_df["service_cost_share"] = (
            agg_df["actual_cost"] / np.maximum(0.01, agg_df["total_daily_spend"]) * 100
        )

        # Temporal features
        agg_df["day_of_week"] = agg_df["Date"].dt.dayofweek
        agg_df["day_of_month"] = agg_df["Date"].dt.day

        # 3. ML Model Feature Matrix
        feature_cols = [
            "actual_cost",
            "usage_quantity",
            "unit_cost",
            "rolling_7_day_cost",
            "rolling_30_day_cost",
            "cost_change_percentage",
            "usage_change_percentage",
            "service_cost_share",
            "day_of_week",
            "day_of_month"
        ]

        X = agg_df[feature_cols].copy()
        X.fillna(0, inplace=True)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # 4. Train IsolationForest
        model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=42
        )
        predictions = model.fit_predict(X_scaled)
        decision_scores = model.decision_function(X_scaled)

        # Add anomaly indicators and scores to DataFrame
        # Higher score = more anomalous (0 to 100 scale)
        # Decision function is positive for inliers, negative for outliers
        min_dec = decision_scores.min()
        max_dec = decision_scores.max()
        
        # Normalize decision function to 0-100 anomaly scale
        if max_dec > min_dec:
            anomaly_scores = ((max_dec - decision_scores) / (max_dec - min_dec)) * 100
        else:
            anomaly_scores = np.where(predictions == -1, 90.0, 10.0)

        agg_df["is_anomaly"] = predictions == -1
        agg_df["anomaly_score"] = np.round(anomaly_scores, 2)

        # Sort observations by Date
        agg_df.sort_values(by="Date", inplace=True)

        # 5. Build Anomaly Objects & Explainability
        anomalies_list: List[Dict[str, Any]] = []

        for _, row in agg_df[agg_df["is_anomaly"]].iterrows():
            date_str = row["Date"].strftime("%Y-%m-%d")
            service = str(row["Service"])
            provider = str(row["CloudProvider"])
            region = str(row["Region"])
            actual_cost = float(row["actual_cost"])
            expected_cost = float(row["rolling_7_day_cost"])
            
            # Avoid division by zero
            cost_diff = actual_cost - expected_cost
            dev_pct = (cost_diff / expected_cost * 100) if expected_cost > 0 else 0.0

            # Risk Level Classification
            if dev_pct >= 200.0 or (dev_pct >= 100.0 and cost_diff >= 100.0):
                risk_level = "Critical"
            elif dev_pct >= 100.0 or (dev_pct >= 50.0 and cost_diff >= 50.0):
                risk_level = "High"
            elif dev_pct >= 35.0 or row["anomaly_score"] >= 70.0:
                risk_level = "Medium"
            else:
                risk_level = "Low"

            # Pure Data-Driven Empirical Reason Generation
            reasons = []
            if dev_pct > 0:
                reasons.append(
                    f"{service} daily spend increased {round(dev_pct, 1)}% compared to its 7-day baseline (${actual_cost:,.2f} vs expected ${expected_cost:,.2f})"
                )
            elif dev_pct < 0:
                reasons.append(
                    f"{service} daily spend dropped {round(abs(dev_pct), 1)}% below baseline (${actual_cost:,.2f} vs expected ${expected_cost:,.2f})"
                )

            # Usage quantity factor
            usage_actual = float(row["usage_quantity"])
            usage_exp = float(row["rolling_7_day_usage"])
            usage_dev = ((usage_actual - usage_exp) / usage_exp * 100) if usage_exp > 0 else 0.0

            if abs(usage_dev) >= 20.0:
                if usage_dev > 0:
                    reasons.append(f"driven by a {round(usage_dev, 1)}% increase in usage quantity ({usage_actual:,.1f} vs expected {usage_exp:,.1f})")
                else:
                    reasons.append(f"driven by a {round(abs(usage_dev), 1)}% decrease in usage quantity ({usage_actual:,.1f} vs expected {usage_exp:,.1f})")

            # Unit cost factor
            unit_actual = float(row["unit_cost"])
            unit_exp = float(row["rolling_7_day_unit_cost"])
            unit_dev = ((unit_actual - unit_exp) / unit_exp * 100) if unit_exp > 0 else 0.0

            if abs(unit_dev) >= 20.0:
                if unit_dev > 0:
                    reasons.append(f"unit cost increased by {round(unit_dev, 1)}% (${unit_actual:,.4f} vs expected ${unit_exp:,.4f})")

            # Combine reason strings safely
            reason_str = ", ".join(reasons) + "."

            # Data-Driven Recommendation
            recommendations = {
                "EC2": f"Inspect EC2 compute workloads and instance types in {region} for unexpected heavy workloads, unattached high-spec instances, or non-terminated batch jobs.",
                "S3": f"Audit S3 storage usage in {region} for sudden uncompressed data ingestion or missing lifecycle retention policies.",
                "RDS": f"Review RDS database cluster in {region} for instance tier upgrades or provisioned IOPS modifications.",
                "Lambda": f"Inspect Lambda function execution logs in {region} for recursive invocation loops or error retry storms.",
                "EBS": f"Check provisioned EBS volume types and snapshot backups in {region}.",
                "Azure VM": f"Review Azure VM scale sets and sizing configurations in {region}.",
                "Azure Storage": f"Audit Azure Blob storage container ingestion rates in {region}.",
                "Compute Engine": f"Check GCP Compute Engine instance groups and worker node scaling in {region}.",
                "Cloud SQL": f"Review GCP Cloud SQL database sizing and storage auto-expansion in {region}."
            }
            rec_str = recommendations.get(
                service,
                f"Audit resource utilization and scaling rules for {service} in {region}."
            )

            anomalies_list.append({
                "date": date_str,
                "service": service,
                "cloud_provider": provider,
                "region": region,
                "actual_cost": round(actual_cost, 2),
                "expected_cost": round(expected_cost, 2),
                "deviation_percentage": round(dev_pct, 2),
                "anomaly_score": round(float(row["anomaly_score"]), 2),
                "risk_level": risk_level,
                "reason": reason_str,
                "recommendation": rec_str
            })

        # Sort anomalies by anomaly_score descending
        anomalies_list.sort(key=lambda x: x["anomaly_score"], reverse=True)

        # Risk level counts
        risk_counts = {
            "Critical": sum(1 for a in anomalies_list if a["risk_level"] == "Critical"),
            "High": sum(1 for a in anomalies_list if a["risk_level"] == "High"),
            "Medium": sum(1 for a in anomalies_list if a["risk_level"] == "Medium"),
            "Low": sum(1 for a in anomalies_list if a["risk_level"] == "Low")
        }

        # Service & Provider counts
        service_counts: Dict[str, int] = {}
        provider_counts: Dict[str, int] = {}

        for a in anomalies_list:
            svc = a["service"]
            prv = a["cloud_provider"]
            service_counts[svc] = service_counts.get(svc, 0) + 1
            provider_counts[prv] = provider_counts.get(prv, 0) + 1

        total_obs = len(agg_df)
        total_anom = len(anomalies_list)
        anom_pct = round((total_anom / total_obs * 100), 2) if total_obs > 0 else 0.0

        result = {
            "total_observations": total_obs,
            "total_anomalies": total_anom,
            "critical_anomalies": risk_counts["Critical"],
            "high_risk_anomalies": risk_counts["High"],
            "medium_risk_anomalies": risk_counts["Medium"],
            "low_risk_anomalies": risk_counts["Low"],
            "contamination_used": contamination,
            "anomaly_percentage": anom_pct,
            "anomalies_by_service": service_counts,
            "anomalies_by_provider": provider_counts,
            "anomalies_by_risk_level": risk_counts,
            "anomalies": anomalies_list
        }

        # Cache result
        cls._cache[contamination] = result
        return result

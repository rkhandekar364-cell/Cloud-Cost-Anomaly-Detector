"""
Recommendation Engine Service.
Generates prioritized, non-destructive cloud cost optimization recommendations.
"""

from typing import Dict, Any, List
from app.services.anomaly_detector import AnomalyDetectorService


class RecommendationEngineService:
    """Service to produce evidence-based recommendations derived from cost anomalies."""

    @classmethod
    def get_recommendations(cls) -> Dict[str, Any]:
        anomaly_results = AnomalyDetectorService.run_detection(contamination=0.03)
        anomalies = anomaly_results["anomalies"]

        recommendations_list: List[Dict[str, Any]] = []

        for a in anomalies:
            svc = a["service"]
            provider = a["cloud_provider"]
            region = a["region"]
            priority = a["risk_level"]
            actual = a["actual_cost"]
            expected = a["expected_cost"]
            dev_pct = a["deviation_percentage"]

            # Determine category based on service type & metrics
            if svc in ["EC2", "Azure VM", "Compute Engine"]:
                category = "Investigate usage spike"
                action = f"Review active compute workloads, instance sizing, and non-terminated instances in {region}."
            elif svc in ["S3", "Azure Storage", "EBS"]:
                category = "Review storage growth"
                action = f"Audit storage ingestion rates, uncompressed log dumps, and lifecycle archive rules in {region}."
            elif svc in ["RDS", "Cloud SQL"]:
                category = "Review database usage"
                action = f"Review database instance class sizing, multi-AZ configurations, and provisioned IOPS in {region}."
            elif svc == "Lambda":
                category = "Review serverless invocation growth"
                action = f"Inspect Lambda execution logs in {region} for recursive loops, infinite retries, or traffic surges."
            else:
                category = "Review unusually high resource consumption"
                action = f"Audit resource allocation and scaling policies for {svc} in {region}."

            reason = (
                f"{svc} spend in {region} rose {dev_pct:.1f}% above expected baseline "
                f"(${actual:,.2f} vs expected ${expected:,.2f})."
            )

            recommendations_list.append({
                "service": svc,
                "provider": provider,
                "region": region,
                "priority": priority,
                "category": category,
                "reason": reason,
                "action": action
            })

        # Count by priority
        counts = {
            "Critical": sum(1 for r in recommendations_list if r["priority"] == "Critical"),
            "High": sum(1 for r in recommendations_list if r["priority"] == "High"),
            "Medium": sum(1 for r in recommendations_list if r["priority"] == "Medium"),
            "Low": sum(1 for r in recommendations_list if r["priority"] == "Low")
        }

        return {
            "total_recommendations": len(recommendations_list),
            "critical": counts["Critical"],
            "high": counts["High"],
            "medium": counts["Medium"],
            "low": counts["Low"],
            "recommendations": recommendations_list
        }

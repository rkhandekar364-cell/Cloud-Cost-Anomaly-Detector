"""
Data Validation Service.
Provides a comprehensive and reusable validation engine for cloud billing datasets.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np

REQUIRED_COLUMNS = [
    "Date",
    "CloudProvider",
    "Service",
    "Region",
    "Resource",
    "UsageType",
    "UsageQuantity",
    "UnitCost",
    "TotalCost"
]


class ValidationService:
    """Service to execute quality checks on cloud billing dataset."""

    @staticmethod
    def validate(df: pd.DataFrame) -> Dict[str, Any]:
        details: List[Dict[str, Any]] = []
        total_records = len(df)
        penalty_score = 0.0

        # 1. Required Columns Check
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            details.append({
                "check_name": "required_columns",
                "status": "FAILED",
                "message": f"Missing required columns: {', '.join(missing_cols)}",
                "issue_count": len(missing_cols)
            })
            penalty_score += 50.0
            # If columns missing, return early
            return {
                "data_quality_score": 0.0,
                "total_records": total_records,
                "overall_status": "CRITICAL",
                "passed_checks": 0,
                "failed_checks": 1,
                "details": details
            }
        else:
            details.append({
                "check_name": "required_columns",
                "status": "PASSED",
                "message": "All required columns are present.",
                "issue_count": 0
            })

        # 2. Missing Values Check
        null_counts = df[REQUIRED_COLUMNS].isnull().sum().to_dict()
        total_nulls = sum(null_counts.values())
        if total_nulls > 0:
            null_cols_str = ", ".join([f"{k}: {v}" for k, v in null_counts.items() if v > 0])
            details.append({
                "check_name": "missing_values",
                "status": "WARNING",
                "message": f"Found {total_nulls} missing values across columns ({null_cols_str}).",
                "issue_count": int(total_nulls)
            })
            penalty_score += min(20.0, (total_nulls / total_records) * 100)
        else:
            details.append({
                "check_name": "missing_values",
                "status": "PASSED",
                "message": "No missing values found in dataset.",
                "issue_count": 0
            })

        # 3. Invalid Dates Check
        parsed_dates = pd.to_datetime(df["Date"], errors="coerce")
        invalid_dates_count = parsed_dates.isnull().sum()
        if invalid_dates_count > 0:
            details.append({
                "check_name": "invalid_dates",
                "status": "FAILED",
                "message": f"Found {invalid_dates_count} invalid date entries.",
                "issue_count": int(invalid_dates_count)
            })
            penalty_score += min(25.0, (invalid_dates_count / total_records) * 100)
        else:
            details.append({
                "check_name": "invalid_dates",
                "status": "PASSED",
                "message": "All dates are valid ISO-format dates.",
                "issue_count": 0
            })

        # 4. Negative Costs Check
        negative_costs = (df["TotalCost"] < 0) | (df["UsageQuantity"] < 0) | (df["UnitCost"] < 0)
        negative_count = negative_costs.sum()
        if negative_count > 0:
            details.append({
                "check_name": "negative_costs",
                "status": "FAILED",
                "message": f"Found {negative_count} records with negative costs or quantities.",
                "issue_count": int(negative_count)
            })
            penalty_score += min(25.0, (negative_count / total_records) * 100)
        else:
            details.append({
                "check_name": "negative_costs",
                "status": "PASSED",
                "message": "No negative cost or quantity values detected.",
                "issue_count": 0
            })

        # 5. Invalid Numerical Values Check (Inf, NaN, Non-numeric)
        num_cols = ["UsageQuantity", "UnitCost", "TotalCost"]
        invalid_num_count = 0
        for col in num_cols:
            invalid_mask = pd.to_numeric(df[col], errors="coerce").isna() | np.isinf(df[col])
            invalid_num_count += invalid_mask.sum()

        if invalid_num_count > 0:
            details.append({
                "check_name": "invalid_numerical_values",
                "status": "FAILED",
                "message": f"Found {invalid_num_count} invalid non-numeric/infinite values.",
                "issue_count": int(invalid_num_count)
            })
            penalty_score += min(20.0, (invalid_num_count / total_records) * 100)
        else:
            details.append({
                "check_name": "invalid_numerical_values",
                "status": "PASSED",
                "message": "All numerical fields contain valid numbers.",
                "issue_count": 0
            })

        # 6. Duplicate Rows Check
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            details.append({
                "check_name": "duplicate_rows",
                "status": "WARNING",
                "message": f"Found {duplicate_count} exact duplicate rows.",
                "issue_count": int(duplicate_count)
            })
            penalty_score += min(15.0, (duplicate_count / total_records) * 100)
        else:
            details.append({
                "check_name": "duplicate_rows",
                "status": "PASSED",
                "message": "No duplicate rows found.",
                "issue_count": 0
            })

        # 7. Suspicious TotalCost Calculations Check
        # TotalCost should equal UsageQuantity * UnitCost (with rounding tolerance)
        expected_total = df["UsageQuantity"] * df["UnitCost"]
        cost_diff = (df["TotalCost"] - expected_total).abs()
        # Allow tolerance of 0.05 for rounding differences
        suspicious_mask = cost_diff > 0.05
        suspicious_count = suspicious_mask.sum()

        if suspicious_count > 0:
            details.append({
                "check_name": "suspicious_total_cost",
                "status": "WARNING",
                "message": f"Found {suspicious_count} records where TotalCost differs from (UsageQuantity * UnitCost).",
                "issue_count": int(suspicious_count)
            })
            penalty_score += min(20.0, (suspicious_count / total_records) * 100)
        else:
            details.append({
                "check_name": "suspicious_total_cost",
                "status": "PASSED",
                "message": "TotalCost calculations match UsageQuantity * UnitCost for all records.",
                "issue_count": 0
            })

        # Calculate final quality score
        quality_score = max(0.0, min(100.0, 100.0 - penalty_score))
        quality_score = round(quality_score, 2)

        passed_count = sum(1 for d in details if d["status"] == "PASSED")
        failed_count = sum(1 for d in details if d["status"] in ["FAILED", "WARNING"])

        overall_status = "HEALTHY" if quality_score >= 90.0 else ("DEGRADED" if quality_score >= 70.0 else "UNHEALTHY")

        return {
            "data_quality_score": quality_score,
            "total_records": total_records,
            "overall_status": overall_status,
            "passed_checks": passed_count,
            "failed_checks": failed_count,
            "details": details
        }

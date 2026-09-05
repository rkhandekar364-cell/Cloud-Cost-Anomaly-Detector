"""
Billing Data Normalizer Service.
Normalizes provider-specific cloud billing export files (CSV, XLSX, XLS) into the canonical schema.
Performs semantic alias detection, maps column names, and generates mapping confidence scores.
"""

import io
import re
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
import numpy as np

CANONICAL_FIELDS = [
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

REQUIRED_MINIMUM_FIELDS = ["Date", "Service", "TotalCost"]

# Semantic Aliases dictionary (normalized string -> canonical field)
ALIASES = {
    "Date": [
        "date", "usagedate", "usage_date", "billingdate", "billing_date",
        "invoicedate", "invoice_date", "usagestartdate", "usage_start_date",
        "date_time", "time", "timestamp"
    ],
    "CloudProvider": [
        "cloudprovider", "cloud_provider", "provider", "cloud", "vendor",
        "provider_name", "providername"
    ],
    "Service": [
        "service", "servicename", "service_name", "product", "productname",
        "product_name", "productcode", "servicecode", "lineitem/productcode",
        "service_code", "product_code"
    ],
    "Region": [
        "region", "regionname", "region_name", "availabilityregion",
        "availability_region", "location", "regionid", "region_id", "zone"
    ],
    "Resource": [
        "resource", "resourceid", "resource_id", "resourcename",
        "resource_name", "instanceid", "instance_id", "lineitem/resourceid"
    ],
    "UsageType": [
        "usagetype", "usage_type", "operation", "usagetypename",
        "lineitem/usagetype", "usage_type_name"
    ],
    "UsageQuantity": [
        "usagequantity", "usage_quantity", "usageamount", "usage_amount",
        "quantity", "usage", "lineitem/usageamount"
    ],
    "UnitCost": [
        "unitcost", "unit_cost", "rate", "effectiverate", "effective_rate",
        "price", "blendedrate", "unblendedrate"
    ],
    "TotalCost": [
        "totalcost", "total_cost", "cost", "unblendedcost", "unblended_cost",
        "amortizedcost", "amortized_cost", "netcost", "net_cost", "amount",
        "lineitem/unblendedcost", "lineitem/blendedcost", "cost_in_usd"
    ]
}


def _clean_str(s: str) -> str:
    """Normalize string by converting to lowercase and stripping non-alphanumeric chars."""
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


class BillingNormalizerService:
    """Service to normalize uploaded cloud billing files into canonical schema."""

    @classmethod
    def read_file(cls, contents: bytes, filename: str) -> pd.DataFrame:
        """Reads file contents into a pandas DataFrame based on file extension."""
        fname_lower = filename.lower()
        if fname_lower.endswith('.csv'):
            # Try utf-8, fallback to latin-1
            try:
                return pd.read_csv(io.BytesIO(contents))
            except UnicodeDecodeError:
                return pd.read_csv(io.BytesIO(contents), encoding='latin-1')
        elif fname_lower.endswith(('.xlsx', '.xls')):
            return pd.read_excel(io.BytesIO(contents))
        else:
            raise ValueError("Unsupported file format. Only CSV, XLSX, and XLS files are supported.")

    @classmethod
    def normalize(cls, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict[str, Any]], List[str]]:
        """
        Normalizes DataFrame columns to canonical schema.
        Returns: (normalized_df, mapping_confidence_list, unmapped_columns_list)
        """
        source_columns = list(df.columns)
        mapped_dict: Dict[str, str] = {}  # canonical_field -> source_column
        confidence_list: List[Dict[str, Any]] = []
        used_source_cols = set()

        # Step 1: Attempt exact & alias matches for each canonical field
        for canonical_field, alias_list in ALIASES.items():
            best_col = None
            best_score = 0.0

            for col in source_columns:
                if col in used_source_cols:
                    continue

                col_clean = _clean_str(col)
                canon_clean = _clean_str(canonical_field)

                # Exact canonical match
                if col_clean == canon_clean:
                    best_col = col
                    best_score = 1.0
                    break

                # Alias match
                for alias in alias_list:
                    alias_clean = _clean_str(alias)
                    if col_clean == alias_clean:
                        if 0.95 > best_score:
                            best_col = col
                            best_score = 0.95
                    elif alias_clean in col_clean or col_clean in alias_clean:
                        if 0.85 > best_score:
                            best_col = col
                            best_score = 0.85

            if best_col and best_score >= 0.80:
                mapped_dict[canonical_field] = best_col
                used_source_cols.add(best_col)
                confidence_list.append({
                    "canonical_field": canonical_field,
                    "source_column": best_col,
                    "confidence": round(best_score, 2)
                })

        # Check required minimum fields
        missing_required = [req for req in REQUIRED_MINIMUM_FIELDS if req not in mapped_dict]
        if missing_required:
            raise ValueError(
                f"Cannot normalize dataset: missing required minimum fields: {', '.join(missing_required)}. "
                f"Dataset must contain columns recognizable as Date, Service, and TotalCost."
            )

        # Build normalized DataFrame
        norm_df = pd.DataFrame()

        # Map existing fields
        for canon, source in mapped_dict.items():
            norm_df[canon] = df[source]

        # Fill default values for unmapped optional canonical fields
        if "CloudProvider" not in norm_df.columns:
            norm_df["CloudProvider"] = "Unknown"
        if "Region" not in norm_df.columns:
            norm_df["Region"] = "global"
        if "Resource" not in norm_df.columns:
            norm_df["Resource"] = "unspecified"
        if "UsageType" not in norm_df.columns:
            norm_df["UsageType"] = "StandardUsage"
        if "UsageQuantity" not in norm_df.columns:
            norm_df["UsageQuantity"] = 1.0
        if "UnitCost" not in norm_df.columns:
            norm_df["UnitCost"] = norm_df["TotalCost"]

        # Reorder canonical columns
        norm_df = norm_df[CANONICAL_FIELDS].copy()

        # Format Date column
        norm_df["Date"] = pd.to_datetime(norm_df["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
        norm_df.dropna(subset=["Date", "Service", "TotalCost"], inplace=True)

        # Convert numerical fields safely
        norm_df["UsageQuantity"] = pd.to_numeric(norm_df["UsageQuantity"], errors="coerce").fillna(1.0).abs()
        norm_df["UnitCost"] = pd.to_numeric(norm_df["UnitCost"], errors="coerce").fillna(0.0).abs()
        norm_df["TotalCost"] = pd.to_numeric(norm_df["TotalCost"], errors="coerce").fillna(0.0).abs()

        # Unmapped columns list
        unmapped_columns = [col for col in source_columns if col not in used_source_cols]

        return norm_df, confidence_list, unmapped_columns

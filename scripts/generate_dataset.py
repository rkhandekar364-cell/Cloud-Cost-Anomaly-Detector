"""
Script to generate a realistic synthetic cloud billing dataset with injected cost anomalies.
Creates at least 5,000 records spanning ~12 months across AWS, Azure, and GCP.
Includes an optional 'IsAnomaly' ground-truth flag (0 or 1) for evaluation purposes.
"""

import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

def generate_billing_data(num_records: int = 5500, start_date_str: str = "2025-09-01") -> pd.DataFrame:
    random.seed(42)
    np.random.seed(42)
    
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    date_range = [start_date + timedelta(days=i) for i in range(365)]
    
    providers_services = {
        "AWS": {
            "services": ["EC2", "S3", "RDS", "Lambda", "EBS"],
            "regions": ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]
        },
        "Azure": {
            "services": ["Azure VM", "Azure Storage"],
            "regions": ["eastus", "westeurope", "southeastasia"]
        },
        "GCP": {
            "services": ["Compute Engine", "Cloud SQL"],
            "regions": ["us-central1", "europe-west1", "asia-east1"]
        }
    }

    resources_pool = {
        "EC2": ["i-0a8f9c1d2e3f4", "i-0b7e6d5c4b3a2", "i-0c9d8e7f6a5b4", "i-0d1e2f3a4b5c6"],
        "S3": ["prod-analytics-data-dump", "user-media-storage-bucket", "app-logs-archive"],
        "RDS": ["prod-db-cluster-primary", "analytics-read-replica"],
        "Lambda": ["auth-token-verifier", "image-resizer-worker", "event-processor"],
        "EBS": ["vol-0123456789abcdef0", "vol-0fe0d1c2b3a498765"],
        "Azure VM": ["vm-web-prod-01", "vm-api-prod-02"],
        "Azure Storage": ["stappprodlogs001", "stbackupdata002"],
        "Compute Engine": ["gcp-k8s-worker-1", "gcp-k8s-worker-2"],
        "Cloud SQL": ["gcp-main-postgres-db"]
    }

    service_specs = {
        "EC2": {"usage_type": "BoxUsage:t3.xlarge", "unit_cost": 0.1664, "qty_range": (18, 24)},
        "S3": {"usage_type": "StandardStorage-GB", "unit_cost": 0.023, "qty_range": (300, 1200)},
        "RDS": {"usage_type": "InstanceUsage:db.m5.large", "unit_cost": 0.38, "qty_range": (20, 24)},
        "Lambda": {"usage_type": "RequestCount", "unit_cost": 0.0000002, "qty_range": (100000, 800000)},
        "EBS": {"usage_type": "VolumeUsage.gp3", "unit_cost": 0.08, "qty_range": (100, 500)},
        "Azure VM": {"usage_type": "Standard_D4s_v3", "unit_cost": 0.192, "qty_range": (18, 24)},
        "Azure Storage": {"usage_type": "BlobStorage-GB", "unit_cost": 0.020, "qty_range": (400, 1500)},
        "Compute Engine": {"usage_type": "n2-standard-4", "unit_cost": 0.194, "qty_range": (18, 24)},
        "Cloud SQL": {"usage_type": "db-custom-2-7680", "unit_cost": 0.35, "qty_range": (20, 24)}
    }

    rows = []
    
    # Generate base records distributed over the 365 days
    records_per_day = num_records // 365
    for current_date in date_range:
        date_str = current_date.strftime("%Y-%m-%d")
        
        for _ in range(records_per_day + random.choice([0, 1, 2])):
            provider = random.choice(list(providers_services.keys()))
            service = random.choice(providers_services[provider]["services"])
            region = random.choice(providers_services[provider]["regions"])
            resource = random.choice(resources_pool[service])
            spec = service_specs[service]

            usage_qty = round(random.uniform(spec["qty_range"][0], spec["qty_range"][1]), 2)
            unit_cost = spec["unit_cost"]
            
            # Add slight variance to unit cost or quantity
            usage_qty *= random.uniform(0.95, 1.05)
            
            total_cost = round(usage_qty * unit_cost, 4)
            
            rows.append({
                "Date": date_str,
                "CloudProvider": provider,
                "Service": service,
                "Region": region,
                "Resource": resource,
                "UsageType": spec["usage_type"],
                "UsageQuantity": round(usage_qty, 2),
                "UnitCost": unit_cost,
                "TotalCost": total_cost,
                "IsAnomaly": 0
            })

    df = pd.DataFrame(rows)

    # --- INJECT REALISTIC ANOMALIES & MARK GROUND TRUTH ---
    
    # Anomaly 1: Sudden EC2 spending spike (unplanned GPU / heavy compute run)
    ec2_mask = (df["Resource"] == "i-0a8f9c1d2e3f4") & (df["Date"] >= "2025-11-10") & (df["Date"] <= "2025-11-17")
    df.loc[ec2_mask, "UsageType"] = "BoxUsage:p3.8xlarge"
    df.loc[ec2_mask, "UnitCost"] = 12.24
    df.loc[ec2_mask, "UsageQuantity"] = np.random.uniform(22.0, 24.0, size=ec2_mask.sum()).round(2)
    df.loc[ec2_mask, "TotalCost"] = (df.loc[ec2_mask, "UsageQuantity"] * df.loc[ec2_mask, "UnitCost"]).round(4)
    df.loc[ec2_mask, "IsAnomaly"] = 1

    # Anomaly 2: Unusually high S3 usage (massive uncompressed log dumps)
    s3_mask = (df["Resource"] == "prod-analytics-data-dump") & (df["Date"] >= "2026-02-01") & (df["Date"] <= "2026-02-08")
    df.loc[s3_mask, "UsageQuantity"] = np.random.uniform(45000.0, 65000.0, size=s3_mask.sum()).round(2)
    df.loc[s3_mask, "TotalCost"] = (df.loc[s3_mask, "UsageQuantity"] * df.loc[s3_mask, "UnitCost"]).round(4)
    df.loc[s3_mask, "IsAnomaly"] = 1

    # Anomaly 3: RDS cost increase (permanent DB instance class upgrade to multi-AZ r5.8xlarge)
    rds_mask = (df["Resource"] == "prod-db-cluster-primary") & (df["Date"] >= "2026-04-15")
    df.loc[rds_mask, "UsageType"] = "InstanceUsage:db.r5.8xlarge-MultiAZ"
    df.loc[rds_mask, "UnitCost"] = 7.68
    df.loc[rds_mask, "TotalCost"] = (df.loc[rds_mask, "UsageQuantity"] * df.loc[rds_mask, "UnitCost"]).round(4)
    df.loc[rds_mask, "IsAnomaly"] = 1

    # Anomaly 4: Unexpected Lambda usage (recursive invocation bug / traffic storm)
    lambda_mask = (df["Resource"] == "event-processor") & (df["Date"] >= "2026-06-05") & (df["Date"] <= "2026-06-08")
    df.loc[lambda_mask, "UsageQuantity"] = np.random.uniform(180000000.0, 250000000.0, size=lambda_mask.sum()).round(2)
    df.loc[lambda_mask, "TotalCost"] = (df.loc[lambda_mask, "UsageQuantity"] * df.loc[lambda_mask, "UnitCost"]).round(4)
    df.loc[lambda_mask, "IsAnomaly"] = 1

    # Anomaly 5: Temporary data-transfer-like spending spike (unthrottled data egress surge)
    egress_rows = []
    for d in ["2026-07-20", "2026-07-21", "2026-07-22", "2026-07-23"]:
        qty = round(random.uniform(20000, 35000), 2)
        unit = 0.09
        egress_rows.append({
            "Date": d,
            "CloudProvider": "AWS",
            "Service": "EC2",
            "Region": "us-east-1",
            "Resource": "i-0a8f9c1d2e3f4",
            "UsageType": "DataTransfer-Out-Bytes",
            "UsageQuantity": qty,
            "UnitCost": unit,
            "TotalCost": round(qty * unit, 4),
            "IsAnomaly": 1
        })
    df = pd.concat([df, pd.DataFrame(egress_rows)], ignore_index=True)

    # Sort by Date
    df.sort_values(by="Date", inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "cloud_billing_sample.csv"
    
    print("Generating synthetic cloud billing dataset...")
    dataset = generate_billing_data(num_records=5200)
    dataset.to_csv(csv_path, index=False)
    print(f"Dataset successfully created at {csv_path}")
    print(f"Total Records: {len(dataset)}")
    print(f"Ground Truth Anomalies: {dataset['IsAnomaly'].sum()}")
    print(f"Date Range: {dataset['Date'].min()} to {dataset['Date'].max()}")
    print(f"Total Spend: ${dataset['TotalCost'].sum():,.2f}")

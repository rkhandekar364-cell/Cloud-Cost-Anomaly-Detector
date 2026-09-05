# Cloud Cost Anomaly Detector ☁️💰

An enterprise-grade, portfolio-quality cloud cost monitoring platform designed to analyze multi-cloud billing telemetry, audit data quality, isolate spending anomalies using unsupervised Machine Learning (`IsolationForest`), forecast future expenditures, deliver empirical root-cause investigations, and present actionable optimization guidance through a React SaaS dashboard.

---

## 🎯 Overview & Real-World Problem

Organizations operating across AWS, Azure, and GCP regularly experience unexpected cost spikes caused by runaway compute jobs, storage over-provisioning, unthrottled data egress surges, or recursive serverless execution loops.

Traditional static threshold alerts trigger late or flood engineering teams with noise. The **Cloud Cost Anomaly Detector** solves this problem by integrating:
1. **Data Quality Audit Engine**: Automated 7-rule validation of incoming billing telemetries.
2. **Multi-Cloud Analytics**: Aggregated spending breakdowns by service, provider, and daily time-series.
3. **ML Anomaly Detection**: Unsupervised `IsolationForest` pipeline detecting multivariate spending novelties.
4. **Time-Series Cost Forecasting**: Holt Exponential Smoothing predicting 7-day and 30-day expenditure horizons with holdout backtesting evaluation.
5. **Empirical Root-Cause Analysis**: Zero-fabrication investigation linking anomalies to exact billing deltas and dimensional contributions.
6. **Cost Optimization Recommendations**: Non-destructive, prioritized investigation guidance.

---

## 🚀 Key Features

- **Multi-Cloud Billing Telemetry**: Supports AWS, Azure, and GCP services across multiple global regions.
- **7-Rule Validation Engine**: Verifies required schema, missing values, ISO dates, negative costs, non-numeric values, duplicates, and total cost calculation consistency to generate a 0–100% Data Quality Score.
- **Isolation Forest ML Pipeline**: Trains on 10 engineered features at `(Date, CloudProvider, Service, Region)` observation levels.
- **Risk Level Categorization**: Automatically groups anomalies into `Critical`, `High`, `Medium`, and `Low` risk tiers.
- **Time-Series Forecasting & Backtesting**: 30-day forward predictions with historical 30-day holdout validation (MAE, RMSE, MAPE).
- **Zero-Fabrication Root-Cause Analysis**: Derives ranked contributing factors strictly from empirical telemetry metrics.
- **Enterprise React Dashboard**: Information-dense dashboard built with Vite, Recharts, and Lucide icons featuring 5 interactive views: `Overview`, `Anomalies`, `Forecast`, `Cost Analysis`, and `Recommendations`.

---

## 🏗️ System Architecture

```
Billing Data Telemetry (CSV / Database)
         │
         ▼
  [Data Validation Engine] ─── (7 Quality Audit Checks & Score)
         │
         ▼
  [Cost Analytics Engine] ─── (Service & Provider Breakdown, Daily Trend)
         │
         ▼
  [Isolation Forest ML]   ─── (Feature Matrix, Outlier Scores, Risk Tiers)
         │
         ▼
  [Time-Series Forecaster] ── (Holt Exponential Smoothing & Backtesting)
         │
         ▼
  [Root-Cause Engine]     ─── (Dimensional Delta & Ranked Factor Analysis)
         │
         ▼
  [Recommendation Engine] ─── (Non-Destructive Prioritized Guidance)
         │
         ▼
  [Interactive React Dashboard] (Executive SaaS Views & Real API Data)
```

---

## 🤖 Machine Learning & Anomaly Detection

### Why Isolation Forest?
`IsolationForest` isolates anomalies by randomly selecting feature split points. Anomalies are rare and statistically distinct, requiring fewer tree splits to isolate compared to normal observations.

- **Unsupervised**: Operates without requiring prior historical labels.
- **Multivariate Feature Sensitivity**: Detects joint anomalies (e.g. moderate cost jump coupled with extreme unit cost shifts).
- **Service/Date Level Aggregation**: Feature matrices are built per `(Date, CloudProvider, Service, Region)` observation so large services (e.g. EC2) are evaluated relative to their own rolling baseline rather than penalized for being expensive.

### 10 Engineered Features
1. `actual_cost`: Daily spend for observation.
2. `usage_quantity`: Aggregated daily usage units.
3. `unit_cost`: Average unit price.
4. `rolling_7_day_cost`: 7-day rolling mean cost baseline per service.
5. `rolling_30_day_cost`: 30-day rolling mean cost baseline per service.
6. `cost_change_percentage`: Percent deviation vs 7-day baseline.
7. `usage_change_percentage`: Percent deviation in usage quantity vs 7-day baseline.
8. `service_cost_share`: Share of total daily multi-cloud spend represented by this service.
9. `day_of_week`: Day of week index (0–6).
10. `day_of_month`: Day of month index (1–31).

---

## 📈 Cost Forecasting & Backtesting

- **Method**: Holt's Linear Exponential Smoothing ($\alpha=0.25, \beta=0.08$) trained on continuous daily spend time series.
- **Trend Classification**: Automatically classifies spend trajectory as `increasing` ($\ge +3.0\%$), `decreasing` ($\le -3.0\%$), or `stable` based on predicted vs recent 30-day baselines.
- **Historical Backtesting**: Holds out the final 30 days of telemetry to calculate validation metrics:
  - **MAE (Mean Absolute Error)**: `$175.36`
  - **RMSE (Root Mean Squared Error)**: `$201.86`
  - **MAPE (Mean Absolute Percentage Error)**: `85.5%`

---

## 🛠️ Technology Stack

- **Frontend**: React 18, Vite, Recharts, Lucide Icons, Modern Vanilla CSS Design System.
- **Backend**: Python 3.10+, FastAPI, Uvicorn.
- **Data & ML**: Pandas, NumPy, Scikit-Learn (`IsolationForest`, `StandardScaler`).
- **Validation**: Pydantic v2.
- **Testing**: Pytest, FastAPI TestClient.
- **Containerization**: Docker, Docker Compose.

---

## 📂 Final Project Structure

```
Cloud-Cost-Anomaly-Detector/
│
├── backend/
│   ├── app/
│   │   ├── main.py                   # FastAPI app entrypoint & CORS middleware
│   │   ├── api/
│   │   │   └── endpoints.py          # 17 REST API endpoints
│   │   ├── services/
│   │   │   ├── validation_service.py # Data quality audit engine
│   │   │   ├── cost_service.py       # Cost aggregations
│   │   │   ├── anomaly_detector.py   # IsolationForest ML engine
│   │   │   ├── forecasting.py        # Holt Exponential Smoothing engine
│   │   │   ├── root_cause.py         # Empirical root-cause investigation
│   │   │   ├── recommendations.py    # Recommendation engine
│   │   │   └── insights.py           # Cost drivers & business insights
│   │   ├── models/
│   │   │   └── schemas.py            # Pydantic data schemas
│   │   └── utils/
│   │       └── dataset_loader.py     # Thread-safe dataset loader via pathlib
│   ├── tests/
│   │   ├── test_api.py               # API endpoints test suite
│   │   └── test_services.py          # Unit tests & edge cases
│   ├── Dockerfile
│   └── requirements.txt
│
├── data/
│   └── cloud_billing_sample.csv      # 5,466 synthetic billing records (12 months)
│
├── frontend/                         # React Enterprise SaaS Dashboard
│   ├── src/
│   │   ├── services/
│   │   │   └── api.js                # Centralized API service layer
│   │   ├── utils/
│   │   │   └── formatters.js         # Currency ($76.5K) & % formatters
│   │   ├── components/               # Sidebar, Header, KpiCards, Charts, Modal
│   │   ├── pages/                    # Overview, Anomalies, Forecast, CostAnalysis, Recommendations
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── .env.example
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── scripts/
│   ├── generate_dataset.py           # Synthetic dataset generator with ground-truth flags
│   └── run_tests.py                  # Backend test runner
│
├── notebooks/.gitkeep
├── screenshots/.gitkeep
├── docker-compose.yml                # Multi-container orchestration
├── LICENSE                           # MIT License
├── README.md
└── .gitignore
```

---

## ⚙️ Installation & Running Guide

### 1. Backend Setup
```bash
# Clone & navigate to project directory
cd Cloud-Cost-Anomaly-Detector

# Create virtual environment
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1 | Linux/macOS: source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Generate dataset (if needed)
python scripts/generate_dataset.py

# Run FastAPI backend server
PYTHONPATH=backend python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Backend Test Suite
```bash
# Run 27 backend tests
python scripts/run_tests.py
```

### 3. Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install npm packages
npm install

# Run Vite dev server
npm run dev
```

### 4. Docker Deployment
```bash
# Build and run containers using Docker Compose
docker-compose up --build
```
- **React Dashboard**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Backend Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Basic API status check |
| `GET` | `/api/health` | Health check & dataset record status |
| `POST` | `/api/data/validate` | Execute 7-rule data quality validation audit |
| `GET` | `/api/data/summary` | Overall billing metrics summary |
| `GET` | `/api/cost/service-breakdown` | Spending breakdown by cloud service |
| `GET` | `/api/cost/provider-breakdown` | Spending breakdown by cloud provider |
| `GET` | `/api/cost/daily-trend` | Daily spending time-series |
| `GET` | `/api/anomalies` | `IsolationForest` anomaly detection results |
| `GET` | `/api/anomalies/summary` | Anomaly count by risk tier |
| `GET` | `/api/anomalies/top` | Top $N$ anomalies ordered by severity |
| `GET` | `/api/forecast` | 30-day time-series cost forecast |
| `GET` | `/api/forecast/summary` | Executive forecast comparison & trend classification |
| `GET` | `/api/forecast/services` | Service-level 30-day spend projections |
| `GET` | `/api/forecast/evaluation` | 30-day holdout backtesting metrics (MAE, RMSE, MAPE) |
| `GET` | `/api/anomalies/{id}/analysis` | Empirical root-cause investigation & ranked factors |
| `GET` | `/api/recommendations` | Prioritized non-destructive action plan |
| `GET` | `/api/cost/drivers` | 30-day net cost drivers |
| `GET` | `/api/insights` | Numerical evidence-based business insights |

---

---

## 📥 Real Billing Data Import

Users can upload their own real cloud billing export files (CSV, XLSX, XLS) from AWS, Azure, or GCP:

1. **Export Billing Telemetry**: Export billing data from your cloud provider in CSV or Excel format.
2. **Upload Billing File**: Click **`DATA SOURCE`** in the top navigation bar and select **`Upload Billing File`**.
3. **Semantic Alias Mapping**: The system automatically normalizes provider-specific headers (`UnblendedCost`, `PreTaxCost`, `Product Name`, `InvoiceDate`) to canonical schema (`Date`, `CloudProvider`, `Service`, `Region`, `Resource`, `UsageType`, `UsageQuantity`, `UnitCost`, `TotalCost`).
4. **Validation & Quality Audit**: Evaluates dataset quality across 7 data quality rules (Score: 0–100%).
5. **Explicit Activation**: Review column mapping confidence scores and click **`[ USE THIS DATASET ]`**. All 5 dashboard views and ML/Forecasting pipelines immediately operate on the active dataset.
6. **Restore Demo Dataset**: Click **`[ RESTORE DEMO DATASET ]`** at any time to reactivate the synthetic baseline dataset.

> **Note**: No cloud API credentials, access keys, or secrets are required for file-based billing analysis.

---

## 🔒 Data Privacy & Security

- **Local Processing**: Uploaded billing files are stored safely in `data/uploads/` (excluded from Git via `.gitignore`).
- **No Secret Storage**: Do NOT upload files containing credentials, AWS access keys, passwords, or unrelated sensitive secrets.
- **Privacy Protections**: Telemetry rows and raw file contents are never exposed in system logs or error tracebacks.

---

## 📊 Dataset Disclaimer

The default dataset included in `data/cloud_billing_sample.csv` is a **reproducible synthetic dataset** generated for demonstration and development purposes. It contains 5,466 records spanning 12 months with realistic cloud provider/service cost relationships and injected synthetic anomalies. It is **not** real company financial data.

---

## ⚠️ Portfolio Limitations & Future Improvements

- **Portfolio Prototype**: Designed as an advanced portfolio engineering project demonstrating production-oriented FinOps design patterns. It is not intended for live production financial management without integration with official Cloud Billing APIs.
- **Future Improvements**:
  - Direct API integrations for AWS Cost Explorer, Azure Cost Management, and GCP Billing.
  - Automated Slack & Email webhook alert dispatching.
  - Resource remediation workflows via Terraform or Cloud SDKs.

---

## 📸 Screenshots

The `screenshots/` directory is prepared for the following application captures:
- `01-overview.png`: COST COMMAND CENTER — Spending Activity, Anomaly Pulse Matrix, Service Cost Map, Provider Comparison, Action Center, Top Cost Drivers.
- `02-anomalies.png`: ANOMALY MONITOR — Machine-learning risk severity table with Right Slide-Over Investigation Drawer.
- `03-forecast.png`: COST FORECAST — 30-Day Cost Outlook with `TODAY` line, horizon toggles, and backtesting metrics (MAE, RMSE, MAPE).
- `04-cost-analysis.png`: DATA EXPLORATION WORKSPACE — Service spending map, provider lanes, and ranked cost drivers.
- `05-recommendations.png`: COST OPTIMIZATION ACTIONS — Action board grouped by risk priority with top driver highlights.
- `06-data-source.png`: DATA SOURCE PANEL — Viewport-anchored active dataset switcher & smart column mapping confidence review.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).


# vitals.io

> **The financial health monitor for startups.**

Turn raw CSV financial data into investor-grade unit economics in seconds. No spreadsheets. No complex setup. Just instant clarity.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-e6c487?style=for-the-badge)](LICENSE)

---

## 🎯 The Problem

Most startup founders closely track **total revenue** and **monthly burn**, but few calculate whether they are actually **profitable per customer**.

A startup can post 30% month-over-month growth and still face insolvency within 6 months if acquiring a customer costs ₹50,000 while their lifetime value is only ₹10,000.

**vitals.io fixes this** by turning raw financial metrics into deterministic unit economics instantly.

---

## ✨ Features & Capabilities

Upload your financial CSV — sourced from Stripe, QuickBooks, Zoho Books, or custom spreadsheets — to immediately unlock key financial indicators:

| Metric | Calculation | What It Tells You |
|:-------|:------------|:------------------|
| **ARPA** | `MRR / Total Customers` | Average Revenue Per Account per month |
| **Gross Margin** | `(MRR - COGS) / MRR` | Efficiency of product delivery & hosting |
| **Churn Rate** | `Lost Customers / Total Customers` | Monthly rate of user attrition |
| **CAC** | `(Ad Spend + Sales Cost) / New Customers` | Fully loaded cost to acquire one customer |
| **LTV** | `(ARPA * Gross Margin %) / Churn Rate` | Estimated net revenue from one customer lifespan |
| **LTV:CAC Ratio** | `LTV / CAC` | Sustainability score (Healthy SaaS target is 3.0x+) |
| **Payback Period** | `CAC / Monthly Margin per Customer` | Months required to recover customer acquisition cost |
| **Health Score** | *Scoring Engine* (0.0 to 10.0) | Composite rating of unit economic health |

### Key Platform Highlights
- **Instant CSV Ingestion**: Smart fuzzy column matching automatically maps inconsistent CSV headers.
- **Interactive Scenario Simulator**: Model "what-if" situations (e.g., *reduce churn by 15%*, *increase CAC by 10%*).
- **Zero-Build Stack**: High-performance Server-Side Rendering via Jinja2 & Vanilla JS, avoiding heavy frontend build pipelines.
- **RESTful API**: Exposes JSON endpoints for programmatic engine consumption and Swagger documentation.

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11 or higher
- Git

### Local Installation & Execution

```bash
# 1. Clone repository
git clone https://github.com/rachts/vitals.io.git
cd vitals.io

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start dev server
uvicorn main:app --reload --port 8000
```

Once running, access the web UI at **[http://localhost:8000/](http://localhost:8000/)** and Swagger interactive API docs at **[http://localhost:8000/docs](http://localhost:8000/docs)**.

---

## 🏗 Architecture & Codebase Structure

```
vitals.io/
├── main.py                 # FastAPI backend & deterministic calculation engine
├── requirements.txt        # Python dependency manifest
├── templates/              # Jinja2 SSR frontend templates
│   ├── index.html          # Main landing page
│   ├── product.html        # Platform features overview
│   ├── solutions.html      # Industry solutions by business model
│   ├── economics.html      # Unit Economics Analyzer & Scenario Simulator
│   ├── api.html            # Interactive API documentation page
│   └── contact.html        # Platform inquiry & contact form
├── static/                 # Static assets (CSS, JS, media)
└── README.md               # Project documentation
```

### Tech Stack Rationale

| Component | Technology | Rationale |
|:----------|:-----------|:----------|
| **Backend Framework** | FastAPI (Python 3.11+) | Asynchronous execution, automatic OpenAPI generation, strong typing via Pydantic |
| **Templating** | Jinja2 Templates | Lightweight server-rendered pages without SPA bundle overhead |
| **Styling** | Tailwind CSS | Modern utility-first layout styling with sleek dark-mode aesthetics |
| **Visualizations** | Chart.js / Vanilla JS | Fast interactive client-side rendering for financial charts |
| **Validation** | Pydantic v2 | Strict schema validation for calculation payloads |

> **Design Philosophy**: High-speed, deterministic math served with dark-mode fintech aesthetics (inspired by *Mercury* and *Finera*). Big number typography, clear metric hierarchy, zero AI hallucinations.

---

## 📊 Calculation & Health Scoring Engine

The platform rates startup health on a **0.0 to 10.0** scale based on standard SaaS benchmarks:

| Metric Target | Healthy (No Penalty) | Caution (-1 to -2 Pts) | Critical (-3 to -4 Pts) |
|:--------------|:---------------------|:-----------------------|:------------------------|
| **LTV:CAC Ratio** | `≥ 3.0x` | `1.5x – 2.99x` (-2 pts) | `< 1.5x` (-4 pts) |
| **Payback Period**| `≤ 12 months` | `12.1 – 18 months` (-1 pt) | `> 18 months` (-3 pts) |
| **Monthly Churn** | `≤ 2.0%` | `2.1% – 5.0%` (-1 pt) | `> 5.0%` (-3 pts) |

```python
# Base score starts at 10.0 and applies cumulative deductions down to a 0.0 floor
health_score = max(0.0, min(10.0, score))
```

---

## 📂 CSV Header Auto-Detection

The calculation engine uses fuzzy header resolution to ingest CSV export files from common accounting/billing tools without manual data reformatting:

| Output Field | Supported Header Variants |
|:-------------|:--------------------------|
| `mrr` | `mrr`, `monthly_recurring_revenue`, `revenue`, `monthly_revenue`, `total_revenue`, `income` |
| `total_customers` | `customers`, `users`, `total_customers`, `active_customers`, `accounts`, `user_count` |
| `new_customers` | `new_customers`, `new_users`, `acquired`, `signups`, `acquisitions` |
| `churned_customers` | `churned`, `churn`, `cancellations`, `lost_customers`, `churn_count` |
| `ad_spend` | `ad_spend`, `marketing_spend`, `ads`, `paid_acquisition`, `marketing_cost` |
| `sales_cost` | `sales_salaries`, `sales_cost`, `team_cost`, `payroll_sales`, `sales_expense` |
| `cogs` | `cogs`, `cost_of_goods`, `infrastructure`, `hosting`, `delivery_cost`, `server_cost` |

### Sample CSV Input
```csv
date,mrr,total_customers,new_customers,churned_customers,ad_spend,sales_cost,cogs
2024-01-01,500000,500,100,25,200000,150000,50000
```

---

## 🔌 API Documentation

### 1. `POST /analyze`
Computes complete unit economics from financial raw metrics.

**Request Payload:**
```json
{
  "mrr": 500000,
  "total_customers": 500,
  "new_customers": 100,
  "churned_customers": 25,
  "ad_spend": 200000,
  "sales_cost": 150000,
  "cogs": 50000
}
```

**Response Payload:**
```json
{
  "arpa": 1000.0,
  "gross_margin_pct": 0.9,
  "churn_rate": 0.05,
  "ltv": 18000.0,
  "cac": 3500.0,
  "ltv_cac_ratio": 5.142857142857143,
  "payback": 3.888888888888889,
  "health_score": 9.0
}
```

### 2. `POST /predict/scenario`
Executes what-if scenario forecasting with relative metric adjustments.

**Request Payload:**
```json
{
  "mrr": 500000,
  "total_customers": 500,
  "new_customers": 100,
  "churned_customers": 25,
  "ad_spend": 200000,
  "sales_cost": 150000,
  "cogs": 50000,
  "churn_rate_adj": -0.20,
  "cac_adj": -0.10,
  "mrr_growth_adj": 0.15,
  "gross_margin_adj": 0.05
}
```

### 3. Utility & Health Endpoints
- `POST /predict/runway`: Calculates runway projection.
- `POST /predict/forecast`: Runs predictive growth model.
- `GET /predict/status`: Checks prediction engine operational status.
- `GET /health`: Infrastructure healthcheck endpoint.

---

## 🗺 Roadmap

- [x] Fast instant CSV ingestion with fuzzy header matching
- [x] Scenario simulator with metric adjustments
- [x] Open API endpoints with Swagger support
- [ ] Stripe API live sync integration
- [ ] QuickBooks & Zoho Books automated expense ingestion
- [ ] Cohort retention analysis (Enterprise vs. SMB split)
- [ ] Investor PDF report export
- [ ] Multi-currency conversion support (USD, EUR, GBP, INR)

---

## 👥 Hackathon & Team Info

Developed for **HackLabify V1.0** — *Startup Innovation Tracks*  
**Problem Statement #7**: Unit Economics Analyzer

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

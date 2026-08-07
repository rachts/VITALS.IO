from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import csv
import io

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/solutions", response_class=HTMLResponse)
async def solutions(request: Request):
    return templates.TemplateResponse(request=request, name="solutions.html")


@app.get("/product", response_class=HTMLResponse)
async def product(request: Request):
    return templates.TemplateResponse(request=request, name="product.html")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/economics", response_class=HTMLResponse)
async def economics(request: Request):
    return templates.TemplateResponse(request=request, name="economics.html")

@app.get("/api", response_class=HTMLResponse)
async def api_docs(request: Request):
    return templates.TemplateResponse(request=request, name="api.html")

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse(request=request, name="contact.html")

class AnalyzeRequest(BaseModel):
    mrr: float
    total_customers: int
    new_customers: int
    churned_customers: int
    ad_spend: float
    sales_cost: float
    cogs: float

class ScenarioRequest(BaseModel):
    mrr: float
    total_customers: int
    new_customers: int
    churned_customers: int
    ad_spend: float
    sales_cost: float
    cogs: float
    # Adjustments (e.g., -0.1 for 10% decrease)
    churn_rate_adj: float = 0.0
    cac_adj: float = 0.0
    mrr_growth_adj: float = 0.0
    gross_margin_adj: float = 0.0

class RunwayRequest(BaseModel):
    mrr: float
    total_customers: int
    new_customers: int
    churned_customers: int
    ad_spend: float
    sales_cost: float
    cogs: float
    cash_balance: float = 2000000  # default ₹20L runway

class ForecastRequest(BaseModel):
    mrr: float
    total_customers: int
    new_customers: int
    churned_customers: int
    ad_spend: float
    sales_cost: float
    cogs: float
    months: int = 12

def calculate_weighted_health_score(ltv_cac, payback, gross_margin, churn_rate):
    """Weighted composite health score (0-10)."""

    # LTV:CAC score (weight 50%)
    if ltv_cac is None or ltv_cac < 1:
        ltv_cac_score = 0
    elif ltv_cac < 3:
        ltv_cac_score = (ltv_cac - 1) / 2 * 5  # 1→3 maps to 0→5
    else:
        ltv_cac_score = min(5 + (ltv_cac - 3) / 2 * 5, 10)  # 3→5 maps to 5→10

    # Payback score (weight 30%)
    if payback is None or payback > 24:
        payback_score = 0
    elif payback > 18:
        payback_score = (24 - payback) / 6 * 5
    elif payback > 12:
        payback_score = 5 + (18 - payback) / 6 * 5
    else:
        payback_score = min(5 + (12 - payback) / 12 * 5, 10)

    # Gross margin score (weight 10%)
    if gross_margin < 0.4:
        margin_score = 0
    elif gross_margin < 0.6:
        margin_score = (gross_margin - 0.4) / 0.2 * 5
    else:
        margin_score = min(5 + (gross_margin - 0.6) / 0.4 * 5, 10)

    # Churn score (weight 10%)
    if churn_rate > 0.1:
        churn_score = 0
    elif churn_rate > 0.05:
        churn_score = (0.1 - churn_rate) / 0.05 * 5
    else:
        churn_score = min(5 + (0.05 - churn_rate) / 0.05 * 5, 10)

    # Weighted blend
    score = (
        ltv_cac_score * 0.50 +
        payback_score * 0.30 +
        margin_score * 0.10 +
        churn_score * 0.10
    )

    return round(max(0, min(10, score)), 1)

def calculate_metrics(arpa, gross_margin_pct, churn_rate, cac):
    ltv = (arpa * gross_margin_pct) / churn_rate if churn_rate > 0 else 0
    ltv_cac_ratio = ltv / cac if cac > 0 else 0
    margin_dollars = arpa * gross_margin_pct
    payback = cac / margin_dollars if margin_dollars > 0 else 0

    score = calculate_weighted_health_score(ltv_cac_ratio, payback, gross_margin_pct, churn_rate)
    return ltv, ltv_cac_ratio, payback, score

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    arpa = req.mrr / req.total_customers if req.total_customers > 0 else 0
    gross_margin_pct = (req.mrr - req.cogs) / req.mrr if req.mrr > 0 else 0
    churn_rate = req.churned_customers / req.total_customers if req.total_customers > 0 else 0
    total_acquisition_cost = req.ad_spend + req.sales_cost
    cac = total_acquisition_cost / req.new_customers if req.new_customers > 0 else 0
    
    ltv, ltv_cac_ratio, payback, score = calculate_metrics(arpa, gross_margin_pct, churn_rate, cac)
    
    return {
        "arpa": arpa,
        "gross_margin_pct": gross_margin_pct,
        "churn_rate": churn_rate,
        "ltv": ltv,
        "cac": cac,
        "ltv_cac_ratio": ltv_cac_ratio,
        "payback": payback,
        "health_score": score
    }

@app.post("/predict/scenario")
async def predict_scenario(req: ScenarioRequest):
    arpa = req.mrr / req.total_customers if req.total_customers > 0 else 0
    gross_margin_pct = (req.mrr - req.cogs) / req.mrr if req.mrr > 0 else 0
    churn_rate = req.churned_customers / req.total_customers if req.total_customers > 0 else 0
    total_acquisition_cost = req.ad_spend + req.sales_cost
    base_cac = total_acquisition_cost / req.new_customers if req.new_customers > 0 else 0
    
    # Adjustments
    adjusted_churn_rate = max(0, churn_rate * (1 + req.churn_rate_adj))
    adjusted_gross_margin = max(0, gross_margin_pct * (1 + req.gross_margin_adj))
    adjusted_cac = max(0, base_cac * (1 + req.cac_adj))
    
    adjusted_mrr = req.mrr * (1 + req.mrr_growth_adj)
    adjusted_arpa = adjusted_mrr / req.total_customers if req.total_customers > 0 else 0
    
    ltv, ltv_cac_ratio, payback, score = calculate_metrics(adjusted_arpa, adjusted_gross_margin, adjusted_churn_rate, adjusted_cac)
    
    return {
        "ltv": ltv,
        "cac": adjusted_cac,
        "ltv_cac_ratio": ltv_cac_ratio,
        "payback": payback,
        "churn_rate": adjusted_churn_rate,
        "gross_margin_pct": adjusted_gross_margin,
        "health_score": score
    }

@app.post("/predict/runway")
def predict_runway(req: RunwayRequest):
    monthly_burn = req.cogs + req.ad_spend + req.sales_cost
    monthly_revenue = req.mrr
    net_burn = max(monthly_burn - monthly_revenue, 1)  # prevent div by zero

    months_remaining = req.cash_balance / net_burn

    # Status
    status = "safe" if months_remaining > 12 else "warning" if months_remaining > 6 else "critical"

    # Projected cash trajectory
    projected = []
    balance = req.cash_balance
    for i in range(min(int(months_remaining) + 3, 24)):
        balance -= net_burn
        projected.append(round(balance, 2))

    return {
        "months_remaining": round(months_remaining, 1),
        "monthly_burn": monthly_burn,
        "monthly_revenue": monthly_revenue,
        "net_burn": net_burn,
        "status": status,
        "projected_cash": projected,
        "message": f"{int(months_remaining)} months of runway at current burn rate"
    }

@app.post("/predict/forecast")
def predict_forecast(req: ForecastRequest):
    # Calculate current growth rate from new vs total customers
    growth_rate = req.new_customers / max(req.total_customers, 1)

    # Calculate ARPU and gross margin
    arpu = req.mrr / max(req.total_customers, 1)
    gross_margin = (req.mrr - req.cogs) / max(req.mrr, 1)

    # Project MRR forward
    forecast = []
    current_mrr = req.mrr
    current_customers = req.total_customers

    for i in range(req.months):
        # Compound growth
        current_mrr = current_mrr * (1 + growth_rate)
        current_customers = int(current_customers * (1 + growth_rate))

        forecast.append({
            "month": i + 1,
            "mrr": round(current_mrr),
            "customers": current_customers,
            "revenue": round(current_mrr),
            "projected_arr": round(current_mrr * 12)
        })

    total_growth = (forecast[-1]["mrr"] / max(req.mrr, 1) - 1) * 100 if forecast else 0

    return {
        "forecast": forecast,
        "projected_arr": forecast[-1]["projected_arr"] if forecast else 0,
        "total_growth_pct": round(total_growth, 1),
        "growth_rate": round(growth_rate * 100, 1),
        "months_projected": req.months
    }

@app.get("/predict/status")
async def predict_status():
    return {"status": "operational"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

class AnalyzeDocsRequest(BaseModel):
    dataset_id: str
    timeframe: dict
    metrics: list

@app.post("/v1/economics/analyze")
async def analyze_docs(req: AnalyzeDocsRequest):
    # Dummy endpoint for the API docs "Try It" functionality
    return {
      "status": "success",
      "data": {
        "ltv_cac_ratio": 4.2,
        "blended_cac": 124.50,
        "margin_decay_rate": 0.015,
        "cohort_health_score": 92
      },
      "meta": {
        "processing_time_ms": 142
      }
    }

COLUMN_ALIASES = {
    "mrr": ["mrr", "monthly_recurring_revenue", "revenue", "monthly_revenue", "total_revenue", "income"],
    "total_customers": ["customers", "users", "total_customers", "active_customers", "accounts", "user_count"],
    "new_customers": ["new_customers", "new_users", "acquired", "signups", "acquisitions"],
    "churned_customers": ["churned_customers", "churned", "churn", "cancellations", "lost_customers", "churn_count"],
    "ad_spend": ["ad_spend", "marketing_spend", "ads", "paid_acquisition", "marketing_cost"],
    "sales_cost": ["sales_salaries", "sales_cost", "team_cost", "payroll_sales", "sales_expense"],
    "cogs": ["cogs", "cost_of_goods", "infrastructure", "hosting", "delivery_cost", "server_cost"]
}

def fuzzy_match_columns(headers):
    """Map CSV headers to standard field names."""
    headers_lower = [h.strip().lower().replace('"', '').replace("'", "") for h in headers]
    mapping = {}

    for standard, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in headers_lower:
                mapping[standard] = headers_lower.index(alias)
                break

    return mapping

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "File must be a CSV")

    contents = await file.read()
    text = contents.decode('utf-8')

    # Parse CSV
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)

    if len(rows) < 2:
        raise HTTPException(422, "CSV must have header row and at least one data row")

    headers = rows[0]
    col_map = fuzzy_match_columns(headers)

    # Check required columns
    required = ["mrr", "total_customers", "new_customers", "churned_customers", "ad_spend", "sales_cost", "cogs"]
    missing = [r for r in required if r not in col_map]

    if missing:
        raise HTTPException(422, f"Missing columns: {', '.join(missing)}")

    # Use last data row
    last_row = rows[-1]

    def get_val(field):
        idx = col_map[field]
        return float(last_row[idx]) if idx < len(last_row) else 0

    payload = {
        "mrr": get_val("mrr"),
        "total_customers": int(get_val("total_customers")),
        "new_customers": int(get_val("new_customers")),
        "churned_customers": int(get_val("churned_customers")),
        "ad_spend": get_val("ad_spend"),
        "sales_cost": get_val("sales_cost"),
        "cogs": get_val("cogs")
    }

    # Auto-analyze
    return await analyze(AnalyzeRequest(**payload))

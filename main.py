from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional

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

def calculate_metrics(arpa, gross_margin_pct, churn_rate, cac):
    ltv = (arpa * gross_margin_pct) / churn_rate if churn_rate > 0 else 0
    ltv_cac_ratio = ltv / cac if cac > 0 else 0
    margin_dollars = arpa * gross_margin_pct
    payback = cac / margin_dollars if margin_dollars > 0 else 0

    score = 10.0
    if ltv_cac_ratio >= 3.0:
        pass
    elif ltv_cac_ratio >= 1.5:
        score -= 2
    else:
        score -= 4
        
    if payback <= 12:
        pass
    elif payback <= 18:
        score -= 1
    else:
        score -= 3
        
    if churn_rate <= 0.02:
        pass
    elif churn_rate <= 0.05:
        score -= 1
    else:
        score -= 3
        
    score = max(0.0, min(10.0, score))
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
async def predict_runway():
    return {"status": "success", "runway_months": 24}

@app.post("/predict/forecast")
async def predict_forecast():
    return {"status": "success"}

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

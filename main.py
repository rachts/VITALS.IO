from fastapi import FastAPI, Request, UploadFile, File, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import csv
import io
import math
import os
import re

try:
    from dotenv import load_dotenv
    load_dotenv(".env.local")
except ImportError:
    pass


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="VITALS.IO API",
    description=(
        "Financial health intelligence for startups. "
        "Upload financial data and calculate investor-grade "
        "unit economics, runway, scenarios and forecasts."
    ),
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ============================================================
# CONSTANTS
# ============================================================

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_FORECAST_MONTHS = 60


# ============================================================
# PAGE ROUTES
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.get("/solutions", response_class=HTMLResponse)
async def solutions(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="solutions.html"
    )


@app.get("/product", response_class=HTMLResponse)
async def product(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="product.html"
    )


@app.get("/economics", response_class=HTMLResponse)
async def economics(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="economics.html",
        context={
            "MISTRAL_API_KEY": os.getenv("MISTRAL_API_KEY", ""),
            "SUPABASE_URL": os.getenv(
                "NEXT_PUBLIC_SUPABASE_URL",
                os.getenv("SUPABASE_URL", "")
            ),
            "SUPABASE_ANON_KEY": os.getenv(
                "SUPABASE_ANON_KEY",
                ""
            ),
        },
    )


@app.get("/api", response_class=HTMLResponse)
async def api_docs(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="api.html"
    )


@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="contact.html"
    )


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "SUPABASE_URL": os.getenv(
                "SUPABASE_URL",
                os.getenv("NEXT_PUBLIC_SUPABASE_URL", "")
            ),
            "SUPABASE_ANON_KEY": os.getenv(
                "SUPABASE_ANON_KEY",
                ""
            ),
        },
    )


@app.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="signup.html",
        context={
            "SUPABASE_URL": os.getenv(
                "SUPABASE_URL",
                os.getenv("NEXT_PUBLIC_SUPABASE_URL", "")
            ),
            "SUPABASE_ANON_KEY": os.getenv(
                "SUPABASE_ANON_KEY",
                ""
            ),
        },
    )


# ============================================================
# REQUEST MODELS
# ============================================================

class FinancialRequest(BaseModel):
    mrr: float = Field(ge=0)
    total_customers: int = Field(ge=0)
    new_customers: int = Field(ge=0)
    churned_customers: int = Field(ge=0)
    ad_spend: float = Field(ge=0)
    sales_cost: float = Field(ge=0)
    cogs: float = Field(ge=0)

    @field_validator("churned_customers")
    @classmethod
    def validate_churn(cls, value, info):
        total = info.data.get("total_customers")

        if total is not None and value > total:
            raise ValueError(
                "churned_customers cannot exceed total_customers"
            )

        return value


class AnalyzeRequest(FinancialRequest):
    pass


class ScenarioRequest(FinancialRequest):
    churn_rate_adj: float = 0.0
    cac_adj: float = 0.0
    mrr_growth_adj: float = 0.0
    gross_margin_adj: float = 0.0

    @field_validator(
        "churn_rate_adj",
        "cac_adj",
        "mrr_growth_adj",
        "gross_margin_adj",
    )
    @classmethod
    def validate_adjustment(cls, value):
        if not math.isfinite(value):
            raise ValueError("adjustments must be finite numbers")

        # Prevent accidental catastrophic scenario inputs.
        if value < -1:
            raise ValueError(
                "adjustments cannot reduce a metric by more than 100%"
            )

        return value


class RunwayRequest(FinancialRequest):
    cash_balance: float = Field(
        default=2_000_000,
        ge=0,
        description="Current available cash in INR"
    )


class ForecastRequest(FinancialRequest):
    months: int = Field(
        default=12,
        ge=1,
        le=MAX_FORECAST_MONTHS
    )


class AnalyzeDocsRequest(BaseModel):
    """
    API documentation request.

    This endpoint is intentionally metadata-only.
    Actual financial analysis is performed through /analyze.
    """
    dataset_id: str
    timeframe: dict
    metrics: list


# ============================================================
# CORE FINANCIAL CALCULATIONS
# ============================================================

def safe_round(value, digits=2):
    """
    Convert non-finite values into None instead of returning
    NaN/Infinity to the frontend.
    """
    if value is None:
        return None

    if not math.isfinite(value):
        return None

    return round(value, digits)


def calculate_weighted_health_score(
    ltv_cac,
    payback,
    gross_margin,
    churn_rate,
):
    """
    VITALS.IO composite startup health score.

    Score: 0-10

    Weighting:
        LTV:CAC  -> 50%
        Payback  -> 30%
        Margin   -> 10%
        Churn    -> 10%
    """

    # --------------------------------------------------------
    # LTV:CAC — 50%
    # --------------------------------------------------------

    if ltv_cac is None:
        ltv_cac_score = 0

    elif ltv_cac == float("inf") or ltv_cac >= 5:
        ltv_cac_score = 10

    elif ltv_cac < 1:
        ltv_cac_score = 0

    elif ltv_cac < 3:
        ltv_cac_score = ((ltv_cac - 1) / 2) * 5

    else:
        ltv_cac_score = min(
            5 + ((ltv_cac - 3) / 2) * 5,
            10
        )

    # --------------------------------------------------------
    # CAC PAYBACK — 30%
    # --------------------------------------------------------

    if payback is None or payback > 24:
        payback_score = 0

    elif payback > 18:
        payback_score = ((24 - payback) / 6) * 5

    elif payback > 12:
        payback_score = 5 + ((18 - payback) / 6) * 5

    else:
        payback_score = min(
            5 + ((12 - payback) / 12) * 5,
            10
        )

    # --------------------------------------------------------
    # GROSS MARGIN — 10%
    # --------------------------------------------------------

    gross_margin = max(0, min(1, gross_margin))

    if gross_margin < 0.40:
        margin_score = 0

    elif gross_margin < 0.60:
        margin_score = (
            (gross_margin - 0.40) / 0.20
        ) * 5

    else:
        margin_score = min(
            5 + ((gross_margin - 0.60) / 0.40) * 5,
            10
        )

    # --------------------------------------------------------
    # CHURN — 10%
    # --------------------------------------------------------

    churn_rate = max(0, min(1, churn_rate))

    if churn_rate > 0.10:
        churn_score = 0

    elif churn_rate > 0.05:
        churn_score = (
            (0.10 - churn_rate) / 0.05
        ) * 5

    else:
        churn_score = min(
            5 + ((0.05 - churn_rate) / 0.05) * 5,
            10
        )

    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

    score = (
        ltv_cac_score * 0.50
        + payback_score * 0.30
        + margin_score * 0.10
        + churn_score * 0.10
    )

    return round(
        max(0, min(10, score)),
        1
    )


def calculate_metrics(
    arpa,
    gross_margin_pct,
    churn_rate,
    cac,
):
    """
    Calculate the core unit economics used by VITALS.IO.
    """

    gross_margin_pct = max(
        0,
        min(1, gross_margin_pct)
    )

    churn_rate = max(
        0,
        min(1, churn_rate)
    )

    contribution_margin = (
        arpa * gross_margin_pct
    )

    # --------------------------------------------------------
    # LTV
    # --------------------------------------------------------

    if churn_rate > 0:
        ltv = (
            arpa * gross_margin_pct
        ) / churn_rate
    else:
        # No observed churn means traditional LTV formula
        # becomes undefined. Return 0 rather than infinity.
        ltv = 0

    # --------------------------------------------------------
    # LTV:CAC
    # --------------------------------------------------------

    if cac == 0:

        if ltv > 0:
            ltv_cac_ratio = float("inf")
        else:
            ltv_cac_ratio = 0

    else:
        ltv_cac_ratio = ltv / cac

    # --------------------------------------------------------
    # CAC PAYBACK
    # --------------------------------------------------------

    if contribution_margin > 0:
        payback = cac / contribution_margin
    else:
        payback = None

    score = calculate_weighted_health_score(
        ltv_cac_ratio,
        payback,
        gross_margin_pct,
        churn_rate,
    )

    return (
        ltv,
        ltv_cac_ratio,
        payback,
        score,
    )


# ============================================================
# FINANCIAL DIAGNOSIS
# ============================================================

def get_health_status(score):
    """
    Convert numeric health score into a product-friendly
    status for the VITALS.IO dashboard.
    """

    if score >= 8:
        return "excellent"

    if score >= 6:
        return "healthy"

    if score >= 4:
        return "watch"

    return "critical"


def generate_diagnosis(
    arpa,
    gross_margin_pct,
    churn_rate,
    cac,
    ltv,
    ltv_cac_ratio,
    payback,
    health_score,
):
    """
    Generate deterministic financial insights.

    These are intentionally rule-based so the product never
    fabricates financial conclusions.
    """

    strengths = []
    risks = []
    recommendations = []

    # --------------------------------------------------------
    # LTV:CAC
    # --------------------------------------------------------

    if ltv_cac_ratio == float("inf"):
        strengths.append(
            "Acquisition cost is currently zero, "
            "indicating strong organic acquisition."
        )

    elif ltv_cac_ratio >= 3:
        strengths.append(
            f"LTV:CAC is {ltv_cac_ratio:.1f}x, "
            "above the commonly targeted 3x threshold."
        )

    elif ltv_cac_ratio >= 1:
        risks.append(
            f"LTV:CAC is only {ltv_cac_ratio:.1f}x, "
            "leaving limited room for acquisition inefficiency."
        )

        recommendations.append(
            "Reduce CAC or increase customer lifetime value."
        )

    else:
        risks.append(
            "Customer acquisition is currently destroying "
            "more value than it creates."
        )

        recommendations.append(
            "Immediately review acquisition channels, "
            "pricing and retention."
        )

    # --------------------------------------------------------
    # GROSS MARGIN
    # --------------------------------------------------------

    if gross_margin_pct >= 0.70:
        strengths.append(
            f"Gross margin is {gross_margin_pct * 100:.1f}%, "
            "indicating strong contribution economics."
        )

    elif gross_margin_pct >= 0.50:
        strengths.append(
            f"Gross margin is {gross_margin_pct * 100:.1f}%."
        )

    else:
        risks.append(
            f"Gross margin is only "
            f"{gross_margin_pct * 100:.1f}%."
        )

        recommendations.append(
            "Investigate COGS, infrastructure and service "
            "delivery costs before scaling aggressively."
        )

    # --------------------------------------------------------
    # CHURN
    # --------------------------------------------------------

    if churn_rate <= 0.03:
        strengths.append(
            f"Monthly churn is low at "
            f"{churn_rate * 100:.1f}%."
        )

    elif churn_rate <= 0.05:
        strengths.append(
            f"Monthly churn is moderate at "
            f"{churn_rate * 100:.1f}%."
        )

    elif churn_rate <= 0.10:
        risks.append(
            f"Monthly churn is elevated at "
            f"{churn_rate * 100:.1f}%."
        )

        recommendations.append(
            "Prioritize retention and identify the highest-churn "
            "customer segments."
        )

    else:
        risks.append(
            f"Monthly churn is critically high at "
            f"{churn_rate * 100:.1f}%."
        )

        recommendations.append(
            "Retention should be addressed before increasing "
            "customer acquisition spend."
        )

    # --------------------------------------------------------
    # PAYBACK
    # --------------------------------------------------------

    if payback is None:
        risks.append(
            "CAC payback cannot be achieved with the "
            "current contribution margin."
        )

        recommendations.append(
            "Improve gross margin, pricing or acquisition "
            "efficiency."
        )

    elif payback <= 12:
        strengths.append(
            f"CAC payback is {payback:.1f} months."
        )

    elif payback <= 18:
        risks.append(
            f"CAC payback is {payback:.1f} months."
        )

        recommendations.append(
            "Work toward reducing CAC payback below 12 months."
        )

    else:
        risks.append(
            f"CAC payback is {payback:.1f} months, "
            "creating significant capital pressure."
        )

        recommendations.append(
            "Reduce acquisition spend or increase contribution "
            "margin before accelerating growth."
        )

    # --------------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------------

    status = get_health_status(health_score)

    if health_score >= 8:
        summary = (
            "Strong unit economics with attractive "
            "scaling potential."
        )

    elif health_score >= 6:
        summary = (
            "Healthy economics, but there are areas "
            "that should be monitored."
        )

    elif health_score >= 4:
        summary = (
            "The business has meaningful financial risks "
            "that should be addressed before aggressive scaling."
        )

    else:
        summary = (
            "Unit economics are currently under significant "
            "pressure and require corrective action."
        )

    return {
        "status": status,
        "summary": summary,
        "strengths": strengths,
        "risks": risks,
        "recommendations": recommendations,
    }


# ============================================================
# ANALYZE
# ============================================================

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):

    # --------------------------------------------------------
    # ARPA
    # --------------------------------------------------------

    arpa = (
        req.mrr / req.total_customers
        if req.total_customers > 0
        else 0
    )

    # --------------------------------------------------------
    # GROSS MARGIN
    # --------------------------------------------------------

    gross_margin_pct = (
        (req.mrr - req.cogs) / req.mrr
        if req.mrr > 0
        else 0
    )

    gross_margin_pct = max(
        0,
        min(1, gross_margin_pct)
    )

    # --------------------------------------------------------
    # CHURN
    # --------------------------------------------------------

    churn_rate = (
        req.churned_customers / req.total_customers
        if req.total_customers > 0
        else 0
    )

    # --------------------------------------------------------
    # CAC
    # --------------------------------------------------------

    total_acquisition_cost = (
        req.ad_spend + req.sales_cost
    )

    cac = (
        total_acquisition_cost / req.new_customers
        if req.new_customers > 0
        else 0
    )

    # --------------------------------------------------------
    # UNIT ECONOMICS
    # --------------------------------------------------------

    (
        ltv,
        ltv_cac_ratio,
        payback,
        health_score,
    ) = calculate_metrics(
        arpa,
        gross_margin_pct,
        churn_rate,
        cac,
    )

    # --------------------------------------------------------
    # DIAGNOSIS
    # --------------------------------------------------------

    diagnosis = generate_diagnosis(
        arpa=arpa,
        gross_margin_pct=gross_margin_pct,
        churn_rate=churn_rate,
        cac=cac,
        ltv=ltv,
        ltv_cac_ratio=ltv_cac_ratio,
        payback=payback,
        health_score=health_score,
    )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "arpa": safe_round(arpa),
        "gross_margin_pct": safe_round(gross_margin_pct),
        "churn_rate": safe_round(churn_rate),
        "ltv": safe_round(ltv),
        "cac": safe_round(cac),

        "ltv_cac_ratio": (
            None
            if ltv_cac_ratio == float("inf")
            else safe_round(ltv_cac_ratio)
        ),

        "payback": safe_round(payback),
        "health_score": health_score,

        "health_status": diagnosis["status"],

        "diagnosis": diagnosis,

        "inputs": {
            "mrr": safe_round(req.mrr),
            "total_customers": req.total_customers,
            "new_customers": req.new_customers,
            "churned_customers": req.churned_customers,
            "ad_spend": safe_round(req.ad_spend),
            "sales_cost": safe_round(req.sales_cost),
            "cogs": safe_round(req.cogs),
        },
    }


# ============================================================
# SCENARIO PLANNING
# ============================================================

@app.post("/predict/scenario")
async def predict_scenario(req: ScenarioRequest):

    base_arpa = (
        req.mrr / req.total_customers
        if req.total_customers > 0
        else 0
    )

    base_gross_margin = (
        (req.mrr - req.cogs) / req.mrr
        if req.mrr > 0
        else 0
    )

    base_gross_margin = max(
        0,
        min(1, base_gross_margin)
    )

    base_churn = (
        req.churned_customers / req.total_customers
        if req.total_customers > 0
        else 0
    )

    base_cac = (
        (req.ad_spend + req.sales_cost)
        / req.new_customers
        if req.new_customers > 0
        else 0
    )

    # --------------------------------------------------------
    # Apply scenario adjustments
    # --------------------------------------------------------

    adjusted_churn_rate = max(
        0,
        min(
            1,
            base_churn * (1 + req.churn_rate_adj)
        )
    )

    adjusted_gross_margin = max(
        0,
        min(
            1,
            base_gross_margin * (
                1 + req.gross_margin_adj
            )
        )
    )

    adjusted_cac = max(
        0,
        base_cac * (1 + req.cac_adj)
    )

    adjusted_mrr = max(
        0,
        req.mrr * (1 + req.mrr_growth_adj)
    )

    adjusted_arpa = (
        adjusted_mrr / req.total_customers
        if req.total_customers > 0
        else 0
    )

    (
        ltv,
        ltv_cac_ratio,
        payback,
        health_score,
    ) = calculate_metrics(
        adjusted_arpa,
        adjusted_gross_margin,
        adjusted_churn_rate,
        adjusted_cac,
    )

    diagnosis = generate_diagnosis(
        arpa=adjusted_arpa,
        gross_margin_pct=adjusted_gross_margin,
        churn_rate=adjusted_churn_rate,
        cac=adjusted_cac,
        ltv=ltv,
        ltv_cac_ratio=ltv_cac_ratio,
        payback=payback,
        health_score=health_score,
    )

    return {
        "ltv": safe_round(ltv),
        "cac": safe_round(adjusted_cac),

        "ltv_cac_ratio": (
            None
            if ltv_cac_ratio == float("inf")
            else safe_round(ltv_cac_ratio)
        ),

        "payback": safe_round(payback),
        "churn_rate": safe_round(adjusted_churn_rate),
        "gross_margin_pct": safe_round(
            adjusted_gross_margin
        ),

        "mrr": safe_round(adjusted_mrr),
        "arpa": safe_round(adjusted_arpa),

        "health_score": health_score,
        "health_status": diagnosis["status"],
        "diagnosis": diagnosis,

        "scenario": {
            "churn_rate_adj": req.churn_rate_adj,
            "cac_adj": req.cac_adj,
            "mrr_growth_adj": req.mrr_growth_adj,
            "gross_margin_adj": req.gross_margin_adj,
        },
    }


# ============================================================
# RUNWAY
# ============================================================

@app.post("/predict/runway")
async def predict_runway(req: RunwayRequest):

    monthly_burn = (
        req.cogs
        + req.ad_spend
        + req.sales_cost
    )

    monthly_revenue = req.mrr

    net_burn = (
        monthly_burn - monthly_revenue
    )

    # --------------------------------------------------------
    # PROFITABLE
    # --------------------------------------------------------

    if net_burn <= 0:

        return {
            "months_remaining": None,
            "monthly_burn": safe_round(monthly_burn),
            "monthly_revenue": safe_round(monthly_revenue),
            "net_burn": safe_round(net_burn),

            "status": "profitable",

            "projected_cash": [],

            "message": (
                "Cash flow positive — infinite runway "
                "at the current operating rate."
            ),
        }

    # --------------------------------------------------------
    # RUNWAY
    # --------------------------------------------------------

    months_remaining = (
        req.cash_balance / net_burn
    )

    if months_remaining > 18:
        runway_status = "safe"

    elif months_remaining > 12:
        runway_status = "healthy"

    elif months_remaining > 6:
        runway_status = "warning"

    else:
        runway_status = "critical"

    # --------------------------------------------------------
    # CASH PROJECTION
    # --------------------------------------------------------

    projected = []

    balance = req.cash_balance

    projection_months = min(
        max(int(math.ceil(months_remaining)), 1) + 3,
        24,
    )

    for month in range(1, projection_months + 1):

        balance -= net_burn

        projected.append({
            "month": month,
            "cash_balance": safe_round(balance),
        })

    # --------------------------------------------------------
    # MESSAGE
    # --------------------------------------------------------

    if months_remaining <= 6:
        message = (
            f"Only {months_remaining:.1f} months of runway "
            "remain. Immediate cost or funding action is recommended."
        )

    elif months_remaining <= 12:
        message = (
            f"{months_remaining:.1f} months of runway remain. "
            "Monitor burn closely."
        )

    else:
        message = (
            f"{months_remaining:.1f} months of runway "
            "at the current burn rate."
        )

    return {
        "months_remaining": safe_round(
            months_remaining,
            1
        ),

        "monthly_burn": safe_round(monthly_burn),
        "monthly_revenue": safe_round(monthly_revenue),
        "net_burn": safe_round(net_burn),

        "cash_balance": safe_round(
            req.cash_balance
        ),

        "status": runway_status,

        "projected_cash": projected,

        "message": message,
    }


# ============================================================
# FORECAST
# ============================================================

@app.post("/predict/forecast")
async def predict_forecast(req: ForecastRequest):

    if req.total_customers <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "total_customers must be greater than 0 "
                "for forecasting."
            ),
        )

    # Net customer growth is what actually matters.
    net_customer_growth = (
        req.new_customers
        - req.churned_customers
    )

    growth_rate = (
        net_customer_growth
        / req.total_customers
    )

    # Prevent mathematical collapse below -100%.
    growth_rate = max(
        -1,
        growth_rate
    )

    current_customers = req.total_customers
    current_arpa = (
        req.mrr / req.total_customers
        if req.total_customers > 0
        else 0
    )

    forecast = []

    for month in range(1, req.months + 1):

        current_customers = max(
            0,
            round(
                current_customers
                * (1 + growth_rate)
            )
        )

        current_mrr = (
            current_customers
            * current_arpa
        )

        forecast.append({
            "month": month,
            "mrr": round(current_mrr),
            "customers": current_customers,
            "revenue": round(current_mrr),
            "projected_arr": round(
                current_mrr * 12
            ),
        })

    # --------------------------------------------------------
    # TOTAL GROWTH
    # --------------------------------------------------------

    if req.mrr <= 0:
        total_growth = None
    else:
        total_growth = (
            forecast[-1]["mrr"] / req.mrr - 1
        ) * 100

    projected_arr = (
        forecast[-1]["projected_arr"]
        if forecast
        else 0
    )

    return {
        "forecast": forecast,

        "projected_arr": projected_arr,

        "total_growth_pct": (
            round(total_growth, 1)
            if total_growth is not None
            else None
        ),

        "growth_rate": round(
            growth_rate * 100,
            1
        ),

        "net_customer_growth": net_customer_growth,

        "months_projected": req.months,
    }


# ============================================================
# STATUS / HEALTH
# ============================================================

@app.get("/predict/status")
async def predict_status():
    return {
        "status": "operational",
        "service": "vitals-economic-engine",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "vitals.io",
    }


# ============================================================
# API DOCUMENTATION ENDPOINT
# ============================================================

@app.post("/v1/economics/analyze")
async def analyze_docs(req: AnalyzeDocsRequest):

    return {
        "status": "ready",
        "message": (
            "Use POST /analyze with financial data "
            "to calculate actual VITALS.IO metrics."
        ),
        "requested_dataset": req.dataset_id,
        "timeframe": req.timeframe,
        "available_metrics": [
            "arpa",
            "gross_margin_pct",
            "churn_rate",
            "cac",
            "ltv",
            "ltv_cac_ratio",
            "payback",
            "health_score",
            "runway",
            "forecast",
        ],
    }


# ============================================================
# CSV INGESTION
# ============================================================

COLUMN_ALIASES = {

    "mrr": [
        "mrr",
        "monthly_recurring_revenue",
        "monthly revenue",
        "revenue",
        "monthly_revenue",
        "total_revenue",
        "income",
    ],

    "total_customers": [
        "customers",
        "users",
        "total_customers",
        "total customers",
        "active_customers",
        "active customers",
        "accounts",
        "user_count",
    ],

    "new_customers": [
        "new_customers",
        "new customers",
        "new_users",
        "new users",
        "acquired",
        "signups",
        "sign ups",
        "acquisitions",
    ],

    "churned_customers": [
        "churned_customers",
        "churned customers",
        "churned",
        "churn",
        "cancellations",
        "lost_customers",
        "lost customers",
        "churn_count",
    ],

    "ad_spend": [
        "ad_spend",
        "ad spend",
        "marketing_spend",
        "marketing spend",
        "ads",
        "paid_acquisition",
        "paid acquisition",
        "marketing_cost",
        "marketing cost",
    ],

    "sales_cost": [
        "sales_salaries",
        "sales salaries",
        "sales_cost",
        "sales cost",
        "team_cost",
        "team cost",
        "payroll_sales",
        "sales_expense",
        "sales expense",
    ],

    "cogs": [
        "cogs",
        "cost_of_goods",
        "cost of goods",
        "infrastructure",
        "hosting",
        "delivery_cost",
        "delivery cost",
        "server_cost",
        "server cost",
    ],
}


def normalize_header(header: str) -> str:
    """
    Normalize CSV headers.

    Examples:
        'Monthly Recurring Revenue'
            -> 'monthly recurring revenue'

        'monthly_revenue'
            -> 'monthly revenue'
    """

    if header is None:
        return ""

    h = str(header)

    h = (
        h.strip()
        .lower()
        .replace('"', "")
        .replace("'", "")
    )

    h = re.sub(
        r"[_\-\s]+",
        " ",
        h
    )

    return h.strip()


def fuzzy_match_columns(headers):

    normalized_headers = [
        normalize_header(h)
        for h in headers
    ]

    mapping = {}

    for standard, aliases in COLUMN_ALIASES.items():

        normalized_aliases = [
            normalize_header(alias)
            for alias in aliases
        ]

        for alias in normalized_aliases:

            if alias in normalized_headers:

                mapping[standard] = (
                    normalized_headers.index(alias)
                )

                break

    return mapping


def sanitize_numeric_value(val: str) -> float:
    """
    Parse common financial CSV formats.

    Supports:
        ₹1,20,000
        $12,000
        €12,000
        12000
        "12000"
        N/A
        -
    """

    if val is None:
        return 0.0

    cleaned = (
        str(val)
        .strip()
        .replace('"', "")
        .replace("'", "")
    )

    # Handle parentheses as negative values.
    negative = (
        cleaned.startswith("(")
        and cleaned.endswith(")")
    )

    if negative:
        cleaned = cleaned[1:-1]

    # Remove currency symbols and commas.
    cleaned = re.sub(
        r"[₹$€£,]",
        "",
        cleaned
    )

    if cleaned == "":
        return 0.0

    if cleaned.lower() in (
        "n/a",
        "na",
        "-",
        "null",
        "none",
        "nan",
    ):
        return 0.0

    try:
        value = float(cleaned)

    except ValueError:
        raise ValueError(
            f"Cannot parse numeric value: '{val}'"
        )

    if negative:
        value *= -1

    return value


# ============================================================
# CSV UPLOAD
# ============================================================

@app.post("/upload")
async def upload_csv(
    request: Request,
    file: UploadFile = File(...),
):

    filename = file.filename or ""

    # --------------------------------------------------------
    # FILE TYPE
    # --------------------------------------------------------

    if not filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file.",
        )

    # --------------------------------------------------------
    # CONTENT LENGTH
    # --------------------------------------------------------

    content_length = request.headers.get(
        "content-length"
    )

    if content_length:

        try:

            if int(content_length) > MAX_FILE_SIZE:

                raise HTTPException(
                    status_code=(
                        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                    ),
                    detail=(
                        "File too large. "
                        "Maximum allowed size is 5MB."
                    ),
                )

        except ValueError:
            pass

    # --------------------------------------------------------
    # READ FILE
    # --------------------------------------------------------

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=(
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            ),
            detail=(
                "File too large. "
                "Maximum allowed size is 5MB."
            ),
        )

    # --------------------------------------------------------
    # DECODE
    # --------------------------------------------------------

    try:

        text = contents.decode("utf-8-sig")

    except UnicodeDecodeError:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "File encoding must be UTF-8."
            ),
        )

    # --------------------------------------------------------
    # PARSE CSV
    # --------------------------------------------------------

    try:

        reader = csv.reader(
            io.StringIO(text)
        )

        rows = list(reader)

    except Exception as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=f"Failed to parse CSV: {exc}",
        )

    # Remove empty rows.
    rows = [
        row
        for row in rows
        if any(
            str(cell).strip()
            for cell in row
        )
    ]

    if len(rows) < 2:

        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "CSV must contain a header row "
                "and at least one data row."
            ),
        )

    # --------------------------------------------------------
    # COLUMN DETECTION
    # --------------------------------------------------------

    headers = rows[0]

    col_map = fuzzy_match_columns(headers)

    required = [
        "mrr",
        "total_customers",
        "new_customers",
        "churned_customers",
        "ad_spend",
        "sales_cost",
        "cogs",
    ]

    missing = [
        field
        for field in required
        if field not in col_map
    ]

    if missing:

        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail={
                "message": "Missing required columns.",
                "missing": missing,
                "detected_columns": headers,
            },
        )

    # --------------------------------------------------------
    # LAST NON-EMPTY DATA ROW
    # --------------------------------------------------------

    last_row = rows[-1]

    def get_val(field):

        index = col_map[field]

        if index >= len(last_row):
            return 0.0

        return sanitize_numeric_value(
            last_row[index]
        )

    def get_int_val(field):

        raw = get_val(field)

        rounded = round(raw)

        if abs(raw - rounded) > 0.01:

            raise ValueError(
                f"Expected an integer for "
                f"'{field}', got {raw}"
            )

        return int(rounded)

    # --------------------------------------------------------
    # BUILD PAYLOAD
    # --------------------------------------------------------

    try:

        payload = {
            "mrr": get_val("mrr"),

            "total_customers": get_int_val(
                "total_customers"
            ),

            "new_customers": get_int_val(
                "new_customers"
            ),

            "churned_customers": get_int_val(
                "churned_customers"
            ),

            "ad_spend": get_val(
                "ad_spend"
            ),

            "sales_cost": get_val(
                "sales_cost"
            ),

            "cogs": get_val(
                "cogs"
            ),
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=f"Data parsing error: {exc}",
        )

    # --------------------------------------------------------
    # ANALYZE
    # --------------------------------------------------------

    try:

        analysis = await analyze(
            AnalyzeRequest(**payload)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                f"Invalid financial data: {exc}"
            ),
        )

    # --------------------------------------------------------
    # RETURN PRODUCT RESPONSE
    # --------------------------------------------------------

    return {
        "status": "success",

        "filename": filename,

        "rows_processed": len(rows) - 1,

        "detected_columns": {
            field: headers[index]
            for field, index in col_map.items()
        },

        "data": analysis,

        "meta": {
            "max_file_size_mb": 5,
            "analysis_type": "latest_period",
        },
    }
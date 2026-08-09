import math
import httpx
from fastapi import APIRouter, HTTPException, status, Depends, Request, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.schemas import (
    AnalyzeRequest, ScenarioRequest, RunwayRequest, ForecastRequest, AdvisorRequest
)
from app.services.calculator import (
    calculate_metrics, generate_diagnosis, get_health_status, safe_round
)
from app.services.csv_parser import parse_and_validate_csv
from app.core.config import settings

router = APIRouter()
security = HTTPBearer()

async def verify_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not settings.supabase_url or not settings.supabase_anon_key:
        # If Supabase is not configured, we'll allow it for demo purposes, 
        # but in production it should be strictly enforced.
        return None

    token = credentials.credentials
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{settings.supabase_url}/auth/v1/user",
            headers={
                "apikey": settings.supabase_anon_key,
                "Authorization": f"Bearer {token}"
            }
        )
        if res.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        return res.json()


@router.get("/health")
@router.head("/health")
async def health_check():
    if settings.supabase_url and settings.supabase_anon_key:
        try:
            # Ping Supabase REST API to check if the database is awake and connected
            async with httpx.AsyncClient() as client:
                res = await client.get(
                    f"{settings.supabase_url}/rest/v1/",
                    headers={"apikey": settings.supabase_anon_key},
                    timeout=5.0
                )
                res.raise_for_status()
            return {"status": "ok", "database": "connected"}
        except Exception:
            # Return 503 so UptimeRobot registers a failure if the DB is down or paused
            raise HTTPException(status_code=503, detail="Database connection failed")
    
    return {"status": "ok"}

@router.post("/analyze")
async def analyze(req: AnalyzeRequest):
    arpa = req.mrr / req.total_customers if req.total_customers > 0 else 0
    gross_margin_pct = (req.mrr - req.cogs) / req.mrr if req.mrr > 0 else 0
    churn_rate = req.churned_customers / req.total_customers if req.total_customers > 0 else 0
    cac = (req.ad_spend + req.sales_cost) / req.new_customers if req.new_customers > 0 else 0

    (ltv, ltv_cac_ratio, payback, health_score) = calculate_metrics(
        arpa, gross_margin_pct, churn_rate, cac
    )

    diagnosis = generate_diagnosis(
        arpa=arpa, gross_margin_pct=gross_margin_pct, churn_rate=churn_rate,
        cac=cac, ltv=ltv, ltv_cac_ratio=ltv_cac_ratio, payback=payback,
        health_score=health_score
    )

    return {
        "arpa": safe_round(arpa),
        "gross_margin_pct": safe_round(gross_margin_pct),
        "churn_rate": safe_round(churn_rate),
        "ltv": safe_round(ltv),
        "cac": safe_round(cac),
        "ltv_cac_ratio": None if ltv_cac_ratio == float("inf") else safe_round(ltv_cac_ratio),
        "payback": safe_round(payback),
        "health_score": health_score,
        "health_status": diagnosis["status"],
        "diagnosis": diagnosis,
        "inputs": req.model_dump(),
    }


@router.post("/predict/scenario")
async def predict_scenario(req: ScenarioRequest):
    base_arpa = req.mrr / req.total_customers if req.total_customers > 0 else 0
    base_gross_margin = max(0, min(1, (req.mrr - req.cogs) / req.mrr if req.mrr > 0 else 0))
    base_churn = req.churned_customers / req.total_customers if req.total_customers > 0 else 0
    base_cac = (req.ad_spend + req.sales_cost) / req.new_customers if req.new_customers > 0 else 0

    adjusted_churn_rate = max(0, min(1, base_churn * (1 + req.churn_rate_adj)))
    adjusted_gross_margin = max(0, min(1, base_gross_margin * (1 + req.gross_margin_adj)))
    adjusted_cac = max(0, base_cac * (1 + req.cac_adj))
    adjusted_mrr = max(0, req.mrr * (1 + req.mrr_growth_adj))
    adjusted_arpa = adjusted_mrr / req.total_customers if req.total_customers > 0 else 0

    (ltv, ltv_cac_ratio, payback, health_score) = calculate_metrics(
        adjusted_arpa, adjusted_gross_margin, adjusted_churn_rate, adjusted_cac
    )

    diagnosis = generate_diagnosis(
        arpa=adjusted_arpa, gross_margin_pct=adjusted_gross_margin,
        churn_rate=adjusted_churn_rate, cac=adjusted_cac, ltv=ltv,
        ltv_cac_ratio=ltv_cac_ratio, payback=payback, health_score=health_score
    )

    return {
        "ltv": safe_round(ltv),
        "cac": safe_round(adjusted_cac),
        "ltv_cac_ratio": None if ltv_cac_ratio == float("inf") else safe_round(ltv_cac_ratio),
        "payback": safe_round(payback),
        "churn_rate": safe_round(adjusted_churn_rate),
        "gross_margin_pct": safe_round(adjusted_gross_margin),
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


@router.post("/predict/runway")
async def predict_runway(req: RunwayRequest):
    monthly_burn = req.cogs + req.ad_spend + req.sales_cost + req.operating_expenses
    monthly_revenue = req.mrr
    net_burn = monthly_burn - monthly_revenue

    if net_burn <= 0:
        return {
            "months_remaining": None,
            "monthly_burn": safe_round(monthly_burn),
            "monthly_revenue": safe_round(monthly_revenue),
            "net_burn": safe_round(net_burn),
            "status": "profitable",
            "projected_cash": [],
            "message": "Cash flow positive — infinite runway at the current operating rate.",
        }

    months_remaining = req.cash_balance / net_burn
    if months_remaining > 18: runway_status = "safe"
    elif months_remaining > 12: runway_status = "healthy"
    elif months_remaining > 6: runway_status = "warning"
    else: runway_status = "critical"

    projected = []
    balance = req.cash_balance
    projection_months = min(max(int(math.ceil(months_remaining)), 1) + 3, 24)

    for month in range(1, projection_months + 1):
        balance -= net_burn
        projected.append({"month": month, "cash_balance": safe_round(balance)})

    return {
        "months_remaining": safe_round(months_remaining, 1),
        "monthly_burn": safe_round(monthly_burn),
        "monthly_revenue": safe_round(monthly_revenue),
        "net_burn": safe_round(net_burn),
        "status": runway_status,
        "projected_cash": projected,
        "message": f"Gross Burn Runway: At current burn, cash will last {safe_round(months_remaining, 1)} months.",
        "disclaimer": "Excludes salaries, rent, and operating expenses. Add those in advanced settings for true cash runway."
    }


@router.post("/predict/forecast")
async def predict_forecast(req: ForecastRequest):
    if req.total_customers <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="total_customers must be greater than 0 for forecasting."
        )

    net_customer_growth = req.new_customers - req.churned_customers
    growth_rate = max(-1, net_customer_growth / req.total_customers)
    
    # Introduce decay to growth rate so it doesn't exponentially explode forever
    # Assume growth rate degrades by a factor (e.g. 5% per month)
    decay_factor = 0.95

    current_customers = req.total_customers
    current_arpa = req.mrr / req.total_customers if req.total_customers > 0 else 0

    forecast = []
    for month in range(1, req.months + 1):
        current_growth = growth_rate * (decay_factor ** (month - 1))
        current_customers = max(0, round(current_customers * (1 + current_growth)))
        current_mrr = current_customers * current_arpa

        forecast.append({
            "month": month,
            "mrr": round(current_mrr),
            "customers": current_customers,
            "revenue": round(current_mrr),
            "projected_arr": round(current_mrr * 12),
        })

    if req.mrr <= 0:
        total_growth = None
    else:
        total_growth = (forecast[-1]["mrr"] / req.mrr - 1) * 100

    projected_arr = forecast[-1]["projected_arr"] if forecast else 0

    return {
        "months_projected": req.months,
        "total_growth_pct": safe_round(total_growth) if total_growth is not None else None,
        "projected_arr": projected_arr,
        "growth_rate": safe_round(growth_rate * 100, 1),
        "net_customer_growth": net_customer_growth,
        "forecast": forecast,
        "disclaimer": "Assumes current net growth rate continues, compounded with a 5% monthly decay factor (saturation)."
    }


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    MAX_FILE_SIZE = 5 * 1024 * 1024
    payload, headers, col_map, rows_processed = await parse_and_validate_csv(file, MAX_FILE_SIZE)
    
    # We call analyze locally to generate the initial response
    arpa = payload["mrr"] / payload["total_customers"] if payload["total_customers"] > 0 else 0
    gross_margin_pct = (payload["mrr"] - payload["cogs"]) / payload["mrr"] if payload["mrr"] > 0 else 0
    churn_rate = payload["churned_customers"] / payload["total_customers"] if payload["total_customers"] > 0 else 0
    cac = (payload["ad_spend"] + payload["sales_cost"]) / payload["new_customers"] if payload["new_customers"] > 0 else 0

    (ltv, ltv_cac_ratio, payback, health_score) = calculate_metrics(
        arpa, gross_margin_pct, churn_rate, cac
    )

    diagnosis = generate_diagnosis(
        arpa=arpa, gross_margin_pct=gross_margin_pct, churn_rate=churn_rate,
        cac=cac, ltv=ltv, ltv_cac_ratio=ltv_cac_ratio, payback=payback,
        health_score=health_score
    )

    analysis_data = {
        "arpa": safe_round(arpa),
        "gross_margin_pct": safe_round(gross_margin_pct),
        "churn_rate": safe_round(churn_rate),
        "ltv": safe_round(ltv),
        "cac": safe_round(cac),
        "ltv_cac_ratio": None if ltv_cac_ratio == float("inf") else safe_round(ltv_cac_ratio),
        "payback": safe_round(payback),
        "health_score": health_score,
        "health_status": diagnosis["status"],
        "diagnosis": diagnosis,
        "inputs": payload,
    }

    return {
        "status": "success",
        "filename": file.filename,
        "rows_processed": rows_processed,
        "detected_columns": {field: headers[index] for field, index in col_map.items()},
        "data": analysis_data,
        "meta": {"max_file_size_mb": 5, "analysis_type": "latest_period"},
    }


@router.post("/advisor")
async def advisor(req: AdvisorRequest, user=Depends(verify_user)):
    if not settings.mistral_api_key:
        raise HTTPException(status_code=500, detail="Mistral API not configured.")

    prompt = f"""
    You are an expert SaaS financial analyst. Review these metrics for a startup and provide exactly 3 actionable, specific insights.
    Format your response as a valid JSON array of strings. Do not use markdown.

    Metrics:
    - MRR: ${req.mrr}
    - Total Customers: {req.total_customers}
    - Net New Customers: {req.new_customers}
    - Churned Customers: {req.churned_customers}
    - CAC: ${req.cac}
    - LTV: ${req.ltv}
    - Gross Margin: {req.gross_margin_pct * 100}%
    """

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.mistral_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistral-small-latest",
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"}
                },
                timeout=10.0
            )
            res.raise_for_status()
            data = res.json()
            content = data["choices"][0]["message"]["content"]
            import json
            parsed = json.loads(content)
            
            # Mistral might wrap it in an object or array
            if isinstance(parsed, list):
                tips = parsed[:3]
            elif isinstance(parsed, dict) and "tips" in parsed:
                tips = parsed["tips"][:3]
            else:
                # fallback
                tips = list(parsed.values())[:3]
                
            return {"tips": tips, "source": "mistral"}
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Mistral API error: {str(e)}")

from pydantic import BaseModel, Field, field_validator
import math

MAX_FORECAST_MONTHS = 60

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
            raise ValueError("churned_customers cannot exceed total_customers")
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
        if value < -1:
            raise ValueError("adjustments cannot reduce a metric by more than 100%")
        return value

class RunwayRequest(FinancialRequest):
    cash_balance: float = Field(
        default=2_000_000,
        ge=0,
        description="Current available cash in INR"
    )
    operating_expenses: float = Field(
        default=0.0,
        ge=0,
        description="Monthly operating expenses (OpEx) excluding COGS and CAC"
    )

class ForecastRequest(FinancialRequest):
    months: int = Field(
        default=12,
        ge=1,
        le=MAX_FORECAST_MONTHS
    )

class AnalyzeDocsRequest(BaseModel):
    dataset_id: str
    timeframe: dict
    metrics: list

class AdvisorRequest(BaseModel):
    mrr: float
    total_customers: int
    new_customers: int
    churned_customers: int
    cac: float
    ltv: float
    gross_margin_pct: float

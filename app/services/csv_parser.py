import csv
import io
import re
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
from fastapi import UploadFile, HTTPException, status
from app.models.schemas import AnalyzeRequest
from app.services.calculator import calculate_metrics, generate_diagnosis, get_health_status

COLUMN_ALIASES = {
    "mrr": [
        "mrr", "monthly_recurring_revenue", "monthly revenue",
        "revenue", "monthly_revenue", "total_revenue", "income"
    ],
    "total_customers": [
        "customers", "users", "total_customers", "total customers",
        "active_customers", "active customers", "accounts", "user_count"
    ],
    "new_customers": [
        "new_customers", "new customers", "new_users", "new users",
        "acquired", "signups", "sign ups", "acquisitions"
    ],
    "churned_customers": [
        "churned_customers", "churned customers", "churned", "churn",
        "cancellations", "lost_customers", "lost customers", "churn_count"
    ],
    "ad_spend": [
        "ad_spend", "ad spend", "marketing_spend", "marketing spend",
        "ads", "paid_acquisition", "paid acquisition", "marketing_cost", "marketing cost"
    ],
    "sales_cost": [
        "sales_salaries", "sales salaries", "sales_cost", "sales cost",
        "team_cost", "team cost", "payroll_sales", "sales_expense", "sales expense"
    ],
    "cogs": [
        "cogs", "cost_of_goods", "cost of goods", "infrastructure",
        "hosting", "delivery_cost", "delivery cost", "server_cost", "server cost"
    ],
}

def normalize_header(header: str) -> str:
    if header is None:
        return ""
    h = str(header).strip().lower().replace('"', "").replace("'", "")
    h = re.sub(r"[_\-\s]+", " ", h)
    return h.strip()

def fuzzy_match_columns(headers):
    normalized_headers = [normalize_header(h) for h in headers]
    mapping = {}
    for standard, aliases in COLUMN_ALIASES.items():
        normalized_aliases = [normalize_header(alias) for alias in aliases]
        for alias in normalized_aliases:
            if alias in normalized_headers:
                mapping[standard] = normalized_headers.index(alias)
                break
    return mapping

def sanitize_numeric_value(val: str) -> float:
    if val is None:
        return 0.0
    cleaned = str(val).strip().replace('"', "").replace("'", "")
    negative = cleaned.startswith("(") and cleaned.endswith(")")
    if negative:
        cleaned = cleaned[1:-1]
    cleaned = re.sub(r"[₹$€£,]", "", cleaned)
    if cleaned == "":
        return 0.0
    if cleaned.lower() in ("n/a", "na", "-", "null", "none", "nan"):
        return 0.0
    try:
        value = float(cleaned)
    except ValueError:
        raise ValueError(f"Cannot parse numeric value: '{val}'")
    if negative:
        value *= -1
    return value

async def parse_and_validate_csv(file: UploadFile, max_size_bytes: int):
    # Read chunk to validate
    content = await file.read(2048)
    
    # File Type Validation (Optional: using magic if available)
    if MAGIC_AVAILABLE:
        try:
            mime = magic.from_buffer(content, mime=True)
            if mime not in ("text/csv", "text/plain", "application/csv"):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Please upload a valid CSV.")
        except Exception:
            pass # Fallback to extension check if magic fails

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are allowed.")
    
    # Reset pointer and read all
    await file.seek(0)
    contents = await file.read()
    if len(contents) > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum allowed size is 5MB."
        )

    try:
        text = contents.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File encoding must be UTF-8."
        )

    try:
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse CSV: {exc}",
        )

    rows = [row for row in rows if any(str(cell).strip() for cell in row)]
    if len(rows) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="CSV must contain a header row and at least one data row.",
        )

    headers = rows[0]
    col_map = fuzzy_match_columns(headers)
    required = ["mrr", "total_customers", "new_customers", "churned_customers", "ad_spend", "sales_cost", "cogs"]
    missing = [field for field in required if field not in col_map]

    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Missing required columns.",
                "missing": missing,
                "detected_columns": headers,
            },
        )

    last_row = rows[-1]

    def get_val(field):
        index = col_map[field]
        if index >= len(last_row): return 0.0
        return sanitize_numeric_value(last_row[index])

    def get_int_val(field):
        raw = get_val(field)
        rounded = round(raw)
        if abs(raw - rounded) > 0.01:
            raise ValueError(f"Expected an integer for '{field}', got {raw}")
        return int(rounded)

    try:
        payload = {
            "mrr": get_val("mrr"),
            "total_customers": get_int_val("total_customers"),
            "new_customers": get_int_val("new_customers"),
            "churned_customers": get_int_val("churned_customers"),
            "ad_spend": get_val("ad_spend"),
            "sales_cost": get_val("sales_cost"),
            "cogs": get_val("cogs"),
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Data parsing error: {exc}",
        )

    return payload, headers, col_map, len(rows) - 1

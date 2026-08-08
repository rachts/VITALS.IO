import sys
from main import fuzzy_match_columns, normalize_header, COLUMN_ALIASES

headers = ["date", "mrr", "total_customers", "new_customers", "churned_customers", "ad_spend", "sales_cost", "cogs"]

mapping = fuzzy_match_columns(headers)
print("Mapping:", mapping)

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
    if field not in mapping
]

print("Missing:", missing)

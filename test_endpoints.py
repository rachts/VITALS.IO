import requests
import json
import os
BASE_URL = "http://127.0.0.1:8000"
def test_status():
    res = requests.get(f"{BASE_URL}/predict/status")
    print("STATUS:", res.status_code)
def test_analyze():
    payload = {
        "mrr": 500000, "total_customers": 500, "new_customers": 100, 
        "churned_customers": 25, "ad_spend": 200000, "sales_cost": 150000, "cogs": 50000
    }
    res = requests.post(f"{BASE_URL}/analyze", json=payload)
    print("ANALYZE:", res.status_code)
def test_scenario():
    payload = {
        "mrr": 500000, "total_customers": 500, "new_customers": 100, 
        "churned_customers": 25, "ad_spend": 200000, "sales_cost": 150000, "cogs": 50000,
        "churn_rate_adj": -0.20, "cac_adj": -0.10, "mrr_growth_adj": 0.15, "gross_margin_adj": 0.05
    }
    res = requests.post(f"{BASE_URL}/predict/scenario", json=payload)
    print("SCENARIO:", res.status_code)
def test_runway():
    payload = {
        "mrr": 500000, "total_customers": 500, "new_customers": 100, 
        "churned_customers": 25, "ad_spend": 200000, "sales_cost": 150000, "cogs": 50000, "cash_balance": 2000000
    }
    res = requests.post(f"{BASE_URL}/predict/runway", json=payload)
    print("RUNWAY:", res.status_code)
def test_forecast():
    payload = {
        "mrr": 500000, "total_customers": 500, "new_customers": 100, 
        "churned_customers": 25, "ad_spend": 200000, "sales_cost": 150000, "cogs": 50000, "months": 12
    }
    res = requests.post(f"{BASE_URL}/predict/forecast", json=payload)
    print("FORECAST:", res.status_code)
def test_upload():
    with open("data/healthy_startup.csv", "rb") as f:
        res = requests.post(f"{BASE_URL}/upload", files={"file": f})
    print("UPLOAD:", res.status_code)
if __name__ == "__main__":
    try:
        test_status()
        test_analyze()
        test_scenario()
        test_runway()
        test_forecast()
        test_upload()
    except Exception as e:
        print("FAILED TO CONNECT OR ERROR:", e)

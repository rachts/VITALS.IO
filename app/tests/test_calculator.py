import pytest
from app.services.calculator import safe_round, calculate_metrics, calculate_weighted_health_score

def test_safe_round():
    assert safe_round(10.1234) == 10.12
    assert safe_round(None) is None
    assert safe_round(float('inf')) is None

def test_calculate_metrics():
    # Good scenario
    arpa = 1000
    gross_margin_pct = 0.80
    churn_rate = 0.05
    cac = 3000

    ltv, ltv_cac, payback, health = calculate_metrics(arpa, gross_margin_pct, churn_rate, cac)
    assert ltv == 16000.0 # 1000 * 0.8 / 0.05
    assert ltv_cac > 5.0
    assert payback == 3000 / (1000 * 0.8)

def test_calculate_weighted_health_score():
    # Perfect scenario
    score = calculate_weighted_health_score(10, 2, 0.9, 0.01)
    assert score > 9.0

    # Terrible scenario
    score = calculate_weighted_health_score(0.5, 24, 0.2, 0.15)
    assert score < 4.0

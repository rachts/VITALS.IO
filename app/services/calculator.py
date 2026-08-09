import math

def safe_round(value, digits=2):
    if value is None or not math.isfinite(value):
        return None
    return round(value, digits)

def calculate_weighted_health_score(ltv_cac, payback, gross_margin, churn_rate):
    # LTV:CAC — 50% (Sigmoid curve centered at 3)
    if ltv_cac is None or ltv_cac < 0:
        ltv_cac_score = 0
    else:
        # Logistic curve: scale 0-10, centered at 3
        # e.g., 3 -> 5, 1 -> 0.47, 5 -> 9.5
        ltv_cac_score = 10 / (1 + math.exp(-1.5 * (ltv_cac - 3)))

    # CAC PAYBACK — 30%
    if payback is None or payback > 24:
        payback_score = 0
    else:
        # Sigmoid centered at 12 months, reversed (lower is better)
        payback_score = 10 - (10 / (1 + math.exp(-0.3 * (payback - 12))))

    # GROSS MARGIN — 10%
    gross_margin = max(0, min(1, gross_margin))
    # Sigmoid centered at 50%
    margin_score = 10 / (1 + math.exp(-10 * (gross_margin - 0.50)))

    # CHURN — 10%
    churn_rate = max(0, min(1, churn_rate))
    # Sigmoid centered at 5% (0.05), reversed
    churn_score = 10 - (10 / (1 + math.exp(-40 * (churn_rate - 0.05))))

    score = (
        ltv_cac_score * 0.50
        + payback_score * 0.30
        + margin_score * 0.10
        + churn_score * 0.10
    )

    return round(max(0, min(10, score)), 1)


def calculate_metrics(arpa, gross_margin_pct, churn_rate, cac):
    gross_margin_pct = max(0, min(1, gross_margin_pct))
    churn_rate = max(0, min(1, churn_rate))
    contribution_margin = arpa * gross_margin_pct

    # LTV with zero division fix (cap lifetime at 24 months if churn is 0)
    if churn_rate == 0:
        ltv = contribution_margin * 24
    else:
        ltv = contribution_margin / churn_rate

    if cac == 0:
        ltv_cac_ratio = float("inf") if ltv > 0 else 0
    else:
        ltv_cac_ratio = ltv / cac

    if contribution_margin > 0:
        payback = cac / contribution_margin
    else:
        payback = None

    score = calculate_weighted_health_score(ltv_cac_ratio, payback, gross_margin_pct, churn_rate)

    return (ltv, ltv_cac_ratio, payback, score)

def get_health_status(score):
    if score >= 8: return "excellent"
    if score >= 6: return "healthy"
    if score >= 4: return "watch"
    return "critical"

def generate_diagnosis(arpa, gross_margin_pct, churn_rate, cac, ltv, ltv_cac_ratio, payback, health_score):
    strengths = []
    risks = []
    recommendations = []

    # LTV:CAC
    if ltv_cac_ratio == float("inf"):
        strengths.append("Acquisition cost is currently zero, indicating strong organic acquisition.")
    elif ltv_cac_ratio >= 3:
        strengths.append(f"LTV:CAC is {ltv_cac_ratio:.1f}x, above the commonly targeted 3x threshold.")
    elif ltv_cac_ratio >= 1:
        risks.append(f"LTV:CAC is only {ltv_cac_ratio:.1f}x, leaving limited room for acquisition inefficiency.")
        recommendations.append("Reduce CAC or increase customer lifetime value.")
    else:
        risks.append("Customer acquisition is currently destroying more value than it creates.")
        recommendations.append("Immediately review acquisition channels, pricing and retention.")

    # GROSS MARGIN
    if gross_margin_pct >= 0.70:
        strengths.append(f"Gross margin is {gross_margin_pct * 100:.1f}%, indicating strong contribution economics.")
    elif gross_margin_pct >= 0.50:
        strengths.append(f"Gross margin is {gross_margin_pct * 100:.1f}%.")
    else:
        risks.append(f"Gross margin is only {gross_margin_pct * 100:.1f}%.")
        recommendations.append("Investigate COGS, infrastructure and service delivery costs before scaling aggressively.")

    # CHURN
    if churn_rate <= 0.03:
        strengths.append(f"Monthly churn is low at {churn_rate * 100:.1f}%.")
    elif churn_rate <= 0.05:
        strengths.append(f"Monthly churn is moderate at {churn_rate * 100:.1f}%.")
    elif churn_rate <= 0.10:
        risks.append(f"Monthly churn is elevated at {churn_rate * 100:.1f}%.")
        recommendations.append("Prioritize retention and identify the highest-churn customer segments.")
    else:
        risks.append(f"Monthly churn is critically high at {churn_rate * 100:.1f}%.")
        recommendations.append("Retention should be addressed before increasing customer acquisition spend.")

    # PAYBACK
    if payback is None:
        risks.append("CAC payback cannot be achieved with the current contribution margin.")
        recommendations.append("Improve gross margin, pricing or acquisition efficiency.")
    elif payback <= 12:
        strengths.append(f"CAC payback is {payback:.1f} months.")
    elif payback <= 18:
        risks.append(f"CAC payback is {payback:.1f} months.")
        recommendations.append("Work toward reducing CAC payback below 12 months.")
    else:
        risks.append(f"CAC payback is {payback:.1f} months, creating significant capital pressure.")
        recommendations.append("Reduce acquisition spend or increase contribution margin before accelerating growth.")

    status = get_health_status(health_score)
    if health_score >= 8:
        summary = "Strong unit economics with attractive scaling potential."
    elif health_score >= 6:
        summary = "Healthy economics, but there are areas that should be monitored."
    elif health_score >= 4:
        summary = "The business has meaningful financial risks that should be addressed before aggressive scaling."
    else:
        summary = "Unit economics are currently under significant pressure and require corrective action."

    return {
        "status": status,
        "summary": summary,
        "strengths": strengths,
        "risks": risks,
        "recommendations": recommendations,
    }

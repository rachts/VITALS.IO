export const generateInsights = (data) => {
  const insights = [];
  
  // 1. LTV:CAC
  const ratio = data.ltv_cac_ratio || 0;
  if (ratio >= 3) {
    insights.push({
      severity: 'green',
      text: `Strong unit economics — LTV:CAC of ${ratio.toFixed(1)}x exceeds the 3.0x SaaS benchmark. Customer acquisition is efficient.`
    });
  } else if (ratio >= 1.5) {
    insights.push({
      severity: 'orange',
      text: `LTV:CAC of ${ratio.toFixed(1)}x is below the 3.0x benchmark. Focus on reducing CAC or improving retention.`
    });
  } else {
    insights.push({
      severity: 'red',
      text: `Critical: LTV:CAC of ${ratio.toFixed(1)}x means you're destroying value with each customer acquired. Immediate action required.`
    });
  }

  // 2. Churn
  const churn = (data.churn_rate || 0) * 100;
  if (churn <= 2) {
    insights.push({
      severity: 'green',
      text: `Excellent retention — monthly churn of ${churn.toFixed(1)}% is world-class for SaaS.`
    });
  } else if (churn <= 5) {
    insights.push({
      severity: 'orange',
      text: `Churn at ${churn.toFixed(1)}% is manageable but eroding LTV. A 1% reduction would add significant value.`
    });
  } else {
    insights.push({
      severity: 'red',
      text: `High churn (${churn.toFixed(1)}%) is your biggest risk. Customers are leaving faster than you can acquire them.`
    });
  }

  // 3. Payback
  const payback = data.payback || 0;
  if (payback <= 12) {
    insights.push({
      severity: 'green',
      text: `Payback period of ${payback.toFixed(1)} months is healthy — you recover CAC before most customers churn.`
    });
  } else {
    insights.push({
      severity: 'orange',
      text: `Payback of ${payback.toFixed(1)} months is long. Consider whether your pricing or sales cost can be optimized.`
    });
  }

  return insights;
};

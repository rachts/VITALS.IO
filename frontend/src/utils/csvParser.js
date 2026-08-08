export const COLUMN_ALIASES = {
  "mrr": ["mrr", "monthly_recurring_revenue", "revenue", "monthly_revenue", "total_revenue", "income"],
  "total_customers": ["customers", "users", "total_customers", "active_customers", "accounts", "user_count"],
  "new_customers": ["new_customers", "new_users", "acquired", "signups", "acquisitions"],
  "churned_customers": ["churned_customers", "churned", "churn", "cancellations", "lost_customers", "churn_count"],
  "ad_spend": ["ad_spend", "marketing_spend", "ads", "paid_acquisition", "marketing_cost"],
  "sales_cost": ["sales_salaries", "sales_cost", "team_cost", "payroll_sales", "sales_expense"],
  "cogs": ["cogs", "cost_of_goods", "infrastructure", "hosting", "delivery_cost", "server_cost"]
};

export const parseCSV = (csvText) => {
  const lines = csvText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
  if (lines.length < 2) throw new Error("CSV must have a header row and at least one data row");

  const headers = lines[0].split(',').map(h => h.trim().toLowerCase().replace(/["']/g, ''));
  const lastRow = lines[lines.length - 1].split(',').map(v => v.trim().replace(/["']/g, ''));
  
  const colMap = {};
  for (const [standard, aliases] of Object.entries(COLUMN_ALIASES)) {
    for (const alias of aliases) {
      if (headers.includes(alias)) {
        colMap[standard] = headers.indexOf(alias);
        break;
      }
    }
  }

  const rawData = {};
  for (const standard of Object.keys(COLUMN_ALIASES)) {
    const idx = colMap[standard];
    rawData[standard] = idx !== undefined && idx < lastRow.length ? (parseFloat(lastRow[idx]) || 0) : 0;
  }
  
  return { headers, colMap, rawData };
};

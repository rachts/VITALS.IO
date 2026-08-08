export const formatCurrency = (value) => {
  if (value === undefined || value === null) return '₹0';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(value);
};

export const formatPercent = (value) => {
  if (value === undefined || value === null) return '0%';
  return `${(value * 100).toFixed(1)}%`;
};

export const formatNumber = (value) => {
  if (value === undefined || value === null) return '0';
  return new Intl.NumberFormat('en-IN', {
    maximumFractionDigits: 1
  }).format(value);
};

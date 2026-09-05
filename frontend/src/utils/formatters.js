/**
 * Formatting Utility functions.
 */

export const formatCurrency = (val, compact = false) => {
  if (val === undefined || val === null || isNaN(val)) return '$0.00';
  
  if (compact) {
    if (Math.abs(val) >= 1000000) {
      return `$${(val / 1000000).toFixed(2)}M`;
    }
    if (Math.abs(val) >= 1000) {
      return `$${(val / 1000).toFixed(1)}K`;
    }
  }

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(val);
};

export const formatPercentage = (val) => {
  if (val === undefined || val === null || isNaN(val)) return '0.0%';
  const prefix = val > 0 ? '+' : '';
  return `${prefix}${val.toFixed(1)}%`;
};

export const formatNumber = (val) => {
  if (val === undefined || val === null || isNaN(val)) return '0';
  return new Intl.NumberFormat('en-US').format(val);
};

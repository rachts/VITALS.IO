import React from 'react';
import { motion } from 'framer-motion';
import { formatCurrency, formatPercent, formatNumber } from '../utils/formatters';

const MetricCard = ({ title, value, type = 'number', status = 'neutral', delta = null }) => {
  let displayValue = value;
  if (type === 'currency') displayValue = formatCurrency(value);
  if (type === 'percent') displayValue = formatPercent(value);
  if (type === 'ratio') displayValue = `${formatNumber(value)}x`;
  
  const statusColors = {
    healthy: 'bg-accent-success',
    caution: 'bg-accent-warn',
    critical: 'bg-red-500',
    neutral: 'bg-text-muted'
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-surface rounded-lg p-5 border border-border flex flex-col justify-between h-full"
    >
      <div className="flex justify-between items-start mb-2">
        <h4 className="text-text-muted uppercase text-[11px] tracking-wider font-semibold">{title}</h4>
        <div className={`w-2 h-2 rounded-full ${statusColors[status]}`} />
      </div>
      <div className="flex items-baseline gap-2">
        <span className="font-display text-3xl text-text-primary">{displayValue}</span>
        {delta !== null && (
          <span className={`text-sm ${delta > 0 ? 'text-accent-success' : 'text-accent-warn'}`}>
            {delta > 0 ? '↑' : '↓'} {Math.abs(delta).toFixed(1)}
          </span>
        )}
      </div>
    </motion.div>
  );
};

export default React.memo(MetricCard);

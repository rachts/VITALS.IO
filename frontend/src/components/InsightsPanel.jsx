import React, { useMemo } from 'react';
import { generateInsights } from '../utils/insights';

const InsightsPanel = ({ data }) => {
  const insights = useMemo(() => generateInsights(data), [data]);

  const colorMap = {
    green: 'bg-accent-success',
    orange: 'bg-accent-warn',
    red: 'bg-red-500'
  };

  return (
    <div className="bg-surface rounded-lg p-6 border-l-4 border-l-accent-primary border-y border-r border-border mt-6">
      <h4 className="text-text-primary font-display text-lg mb-4">Key Findings</h4>
      <div className="space-y-4">
        {insights.map((insight, idx) => (
          <div key={idx} className="flex gap-3">
            <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${colorMap[insight.severity]}`} />
            <p className="text-text-muted text-sm leading-relaxed">{insight.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default React.memo(InsightsPanel);

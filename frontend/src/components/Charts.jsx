import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';

export const UnitEconomicsChart = ({ ltv, cac }) => {
  const data = [
    { name: 'LTV', value: ltv, fill: '#00E5FF' },
    { name: 'CAC', value: cac, fill: '#7B61FF' }
  ];

  return (
    <div className="bg-surface rounded-lg p-5 border border-border h-full">
      <h4 className="text-text-muted uppercase text-[11px] tracking-wider font-semibold mb-6">Unit Economics Breakdown</h4>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
            <XAxis dataKey="name" tick={{ fill: '#5A6A8A', fontSize: 12 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: '#5A6A8A', fontSize: 12 }} axisLine={false} tickLine={false} tickFormatter={(val) => `₹${val/1000}k`} />
            <Tooltip 
              cursor={{ fill: '#121929' }}
              contentStyle={{ backgroundColor: '#0D1220', borderColor: '#1E2D45', color: '#F0F4FF' }}
              itemStyle={{ color: '#F0F4FF' }}
              formatter={(value) => [`₹${value.toLocaleString('en-IN')}`, '']}
            />
            <Bar dataKey="value" radius={[4, 4, 0, 0]} isAnimationActive={true} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export const HealthRadarChart = ({ data }) => {
  const ltvScore = Math.min((data.ltv_cac_ratio / 3) * 10, 10) || 0;
  const churnScore = Math.max(0, 10 - (data.churn_rate / 0.10 * 10)) || 0;
  const paybackScore = Math.max(0, 10 - (data.payback / 12 * 10)) || 0;

  const chartData = [
    { subject: 'LTV:CAC', A: ltvScore, fullMark: 10 },
    { subject: 'Churn', A: churnScore, fullMark: 10 },
    { subject: 'Payback', A: paybackScore, fullMark: 10 },
  ];

  return (
    <div className="bg-surface rounded-lg p-5 border border-border h-full flex flex-col">
      <h4 className="text-text-muted uppercase text-[11px] tracking-wider font-semibold mb-2">Health Breakdown</h4>
      <div className="flex-1 h-64">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
            <PolarGrid stroke="#1E2D45" />
            <PolarAngleAxis dataKey="subject" tick={{ fill: '#5A6A8A', fontSize: 11 }} />
            <PolarRadiusAxis angle={30} domain={[0, 10]} tick={false} axisLine={false} />
            <Radar name="Score" dataKey="A" stroke="#00E5FF" fill="#00E5FF" fillOpacity={0.2} isAnimationActive={true} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

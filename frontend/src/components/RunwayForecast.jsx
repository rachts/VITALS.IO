import React, { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { useApp } from '../context/AppContext';
import api from '../api/client';

const RunwayForecast = () => {
  const { rawData, runwayResult, setRunwayResult } = useApp();
  const [loading, setLoading] = useState(false);
  const [startingCash, setStartingCash] = useState(2000000); 

  const fetchRunway = async () => {
    setLoading(true);
    try {
      const payload = { ...rawData, cash_balance: startingCash };
      const res = await api.post('/predict/runway', payload);
      setRunwayResult(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (rawData) fetchRunway();
    // eslint-disable-next-line
  }, [rawData]);

  const handleUpdate = () => fetchRunway();

  if (!runwayResult && !loading) return <div className="text-text-muted">Loading...</div>;

  const chartData = runwayResult?.projected_cash?.map((val, idx) => ({ month: idx + 1, cash: val })) || [];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <div className="bg-surface rounded-lg p-6 border border-border lg:col-span-1">
        <h3 className="text-lg font-display text-text-primary mb-4">Cash Runway</h3>
        <label className="text-sm text-text-muted block mb-2">Starting Cash Balance (₹)</label>
        <input 
          type="number" 
          value={startingCash} 
          onChange={(e) => setStartingCash(Number(e.target.value))}
          className="w-full bg-elevated border border-border text-text-primary rounded px-3 py-2 mb-4 font-mono text-sm focus:outline-none focus:border-accent-primary"
        />
        <button 
          onClick={handleUpdate}
          className="w-full bg-elevated hover:bg-border text-accent-primary py-2 rounded transition-colors text-sm font-medium border border-border"
        >
          {loading ? 'Calculating...' : 'Recalculate'}
        </button>

        {runwayResult && (
          <div className="mt-8 pt-6 border-t border-border space-y-4">
            <div>
              <p className="text-xs text-text-muted uppercase tracking-wider font-semibold mb-1">Months Remaining</p>
              <p className={`font-display text-3xl ${runwayResult.months_remaining < 6 ? 'text-red-500' : 'text-text-primary'}`}>
                {runwayResult.months_remaining}
              </p>
            </div>
            <div>
              <p className="text-xs text-text-muted uppercase tracking-wider font-semibold mb-1">Monthly Burn</p>
              <p className="font-mono text-lg text-text-primary">₹{(runwayResult.net_burn || 0).toLocaleString('en-IN')}</p>
            </div>
          </div>
        )}
      </div>

      <div className="bg-surface rounded-lg p-6 border border-border lg:col-span-3 min-h-[400px]">
        {loading && !runwayResult ? (
          <div className="h-full flex items-center justify-center text-text-muted">Calculating trajectory...</div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorCash" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00E5FF" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#00E5FF" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="month" tick={{ fill: '#5A6A8A', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#5A6A8A', fontSize: 12 }} axisLine={false} tickLine={false} tickFormatter={(val) => `₹${val/1000}k`} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0D1220', borderColor: '#1E2D45', color: '#F0F4FF' }}
                itemStyle={{ color: '#F0F4FF' }}
                formatter={(value) => [`₹${value.toLocaleString('en-IN')}`, 'Cash']}
                labelFormatter={(label) => `Month ${label}`}
              />
              <ReferenceLine y={0} stroke="#FF453A" strokeDasharray="3 3" />
              <Area type="monotone" dataKey="cash" stroke="#00E5FF" fillOpacity={1} fill="url(#colorCash)" isAnimationActive={true} />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};

export default RunwayForecast;

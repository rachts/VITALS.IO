import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import api from '../api/client';
import MetricCard from './MetricCard';

const Slider = ({ label, value, min, max, step, onChange, format = (v) => v }) => (
  <div className="mb-6">
    <div className="flex justify-between items-center mb-2">
      <label className="text-sm text-text-muted">{label}</label>
      <span className="font-mono text-sm text-accent-primary">{format(value)}</span>
    </div>
    <input 
      type="range" min={min} max={max} step={step} value={value} 
      onChange={(e) => onChange(parseFloat(e.target.value))}
      className="w-full h-1 bg-elevated rounded-lg appearance-none cursor-pointer accent-accent-primary"
    />
  </div>
);

const ScenarioSimulator = () => {
  const { analysisResult, rawData, scenarioResult, setScenarioResult } = useApp();
  const [churnAdj, setChurnAdj] = useState(0);
  const [cacAdj, setCacAdj] = useState(0);
  const [mrrGrowth, setMrrGrowth] = useState(0);
  const [marginAdj, setMarginAdj] = useState(0);
  const [loading, setLoading] = useState(false);

  const runScenario = async () => {
    setLoading(true);
    try {
      const payload = {
        ...rawData,
        churn_rate_adj: churnAdj,
        cac_adj: cacAdj,
        mrr_growth_adj: mrrGrowth,
        gross_margin_adj: marginAdj
      };
      const res = await api.post('/predict/scenario', payload);
      setScenarioResult(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (rawData) runScenario();
    // eslint-disable-next-line
  }, []);

  const formatPct = (val) => `${val > 0 ? '+' : ''}${(val * 100).toFixed(0)}%`;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="bg-surface rounded-lg p-6 border border-border lg:col-span-1">
        <h3 className="text-lg font-display text-text-primary mb-1">Scenario Adjustments</h3>
        <p className="text-xs text-text-muted mb-6">Move sliders to see real-time impact.</p>
        
        <Slider label="Churn Rate" value={churnAdj} min={-0.5} max={0.5} step={0.05} onChange={setChurnAdj} format={formatPct} />
        <Slider label="CAC Adjustment" value={cacAdj} min={-0.5} max={0.5} step={0.05} onChange={setCacAdj} format={formatPct} />
        <Slider label="MRR Growth" value={mrrGrowth} min={-0.2} max={0.5} step={0.05} onChange={setMrrGrowth} format={formatPct} />
        <Slider label="Gross Margin" value={marginAdj} min={-0.2} max={0.2} step={0.05} onChange={setMarginAdj} format={formatPct} />
        
        <button 
          onClick={runScenario}
          className="w-full mt-4 bg-elevated hover:bg-border text-accent-primary py-2 rounded transition-colors text-sm font-medium border border-border"
        >
          {loading ? 'Calculating...' : 'Run Scenario'}
        </button>
      </div>

      <div className="lg:col-span-2 grid grid-cols-2 gap-4">
        {scenarioResult ? (
          <>
            <MetricCard 
              title="Simulated LTV" 
              value={scenarioResult.ltv} 
              type="currency" 
              delta={scenarioResult.ltv - (analysisResult?.ltv || 0)} 
            />
            <MetricCard 
              title="Simulated CAC" 
              value={scenarioResult.cac} 
              type="currency" 
              delta={scenarioResult.cac - (analysisResult?.cac || 0)} 
            />
            <MetricCard 
              title="Simulated LTV:CAC" 
              value={scenarioResult.ltv_cac_ratio} 
              type="ratio" 
              status={scenarioResult.ltv_cac_ratio >= 3 ? 'healthy' : scenarioResult.ltv_cac_ratio >= 1.5 ? 'caution' : 'critical'}
              delta={scenarioResult.ltv_cac_ratio - (analysisResult?.ltv_cac_ratio || 0)} 
            />
            <MetricCard 
              title="Simulated Health Score" 
              value={scenarioResult.health_score} 
              type="number" 
              status={scenarioResult.health_score >= 7 ? 'healthy' : scenarioResult.health_score >= 4 ? 'caution' : 'critical'}
              delta={scenarioResult.health_score - (analysisResult?.health_score || 0)} 
            />
          </>
        ) : (
          <div className="col-span-2 flex items-center justify-center text-text-muted h-full border border-dashed border-border rounded-lg">
            Loading scenario...
          </div>
        )}
      </div>
    </div>
  );
};

export default ScenarioSimulator;

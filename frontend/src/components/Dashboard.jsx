import React from 'react';
import { motion } from 'framer-motion';
import { useApp } from '../context/AppContext';
import MetricCard from './MetricCard';
import HealthScore from './HealthScore';
import { UnitEconomicsChart, HealthRadarChart } from './Charts';
import InsightsPanel from './InsightsPanel';
import ScenarioSimulator from './ScenarioSimulator';
import RunwayForecast from './RunwayForecast';

const Dashboard = () => {
  const { analysisResult, filename, setScreen, setRawData } = useApp();

  if (!analysisResult) return null;

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="p-8 max-w-7xl mx-auto pb-24"
    >
      <header className="flex justify-between items-end mb-8 border-b border-border pb-6">
        <div>
          <h1 className="font-display text-3xl text-text-primary mb-1">Financial Analysis</h1>
          <p className="text-text-muted text-sm font-mono flex items-center gap-2">
            Dataset: <span className="text-accent-primary">{filename}</span>
          </p>
        </div>
        <button 
          onClick={() => { setScreen('hero'); setRawData(null); }}
          className="text-text-muted hover:text-text-primary text-sm font-medium transition-colors"
        >
          Upload New File
        </button>
      </header>

      {/* Top Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <MetricCard title="Total MRR" value={analysisResult.mrr} type="currency" />
        <MetricCard title="ARPA" value={analysisResult.arpa} type="currency" />
        <MetricCard title="CAC" value={analysisResult.cac} type="currency" />
        <MetricCard title="Gross Margin" value={analysisResult.gross_margin} type="percent" />
      </div>

      {/* Main Analysis Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-12">
        <div className="lg:col-span-1 bg-surface border border-border rounded-lg overflow-hidden flex flex-col justify-center">
          <HealthScore score={analysisResult.health_score} />
        </div>
        <div className="lg:col-span-1 h-80">
          <UnitEconomicsChart ltv={analysisResult.ltv} cac={analysisResult.cac} />
        </div>
        <div className="lg:col-span-1 h-80">
          <HealthRadarChart data={analysisResult} />
        </div>
      </div>

      {/* Insights */}
      <div className="mb-12">
        <InsightsPanel data={analysisResult} />
      </div>

      {/* Simulators */}
      <div className="space-y-12">
        <section>
          <div className="mb-6 flex items-center gap-3">
            <div className="w-1.5 h-6 bg-accent-secondary rounded-full" />
            <h2 className="font-display text-2xl text-text-primary">Scenario Simulator</h2>
          </div>
          <ScenarioSimulator />
        </section>

        <section>
          <div className="mb-6 flex items-center gap-3">
            <div className="w-1.5 h-6 bg-accent-warn rounded-full" />
            <h2 className="font-display text-2xl text-text-primary">Runway Forecast</h2>
          </div>
          <RunwayForecast />
        </section>
      </div>
    </motion.div>
  );
};

export default Dashboard;

import React, { useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useApp } from './context/AppContext';
import Sidebar from './components/Sidebar';
import Hero from './components/Hero';
import Dashboard from './components/Dashboard';
import LoadingState from './components/LoadingState';
import ErrorState from './components/ErrorState';
import HelpPanel from './components/HelpPanel';
import api from './api/client';

const AppContent = () => {
  const { screen, isLoading, error, setScreen, setAnalysisResult, setRawData, setFilename } = useApp();

  // "D" for Demo hotkey
  useEffect(() => {
    const handleKeyDown = async (e) => {
      if (e.key === 'd' || e.key === 'D') {
        // Load demo data
        try {
          const demoData = {
            mrr: 1500000,
            total_customers: 300,
            new_customers: 20,
            churned_customers: 35, // High churn
            ad_spend: 300000,
            sales_cost: 200000,
            cogs: 400000
          };
          setRawData(demoData);
          setFilename('struggling_startup_demo.csv');
          
          const analysisRes = await api.post('/analyze', demoData);
          setAnalysisResult(analysisRes.data);
          setScreen('dashboard');
        } catch (err) {
          console.error("Demo data error:", err);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [setAnalysisResult, setRawData, setScreen, setFilename]);

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState />;

  return (
    <div className="flex bg-base min-h-screen text-text-primary">
      {screen === 'dashboard' && <Sidebar />}
      
      <main className={`flex-1 transition-all duration-300 ${screen === 'dashboard' ? 'ml-64' : 'ml-0'}`}>
        <AnimatePresence mode="wait">
          {screen === 'hero' ? (
            <motion.div
              key="hero"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <Hero />
            </motion.div>
          ) : (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Dashboard />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <HelpPanel />
    </div>
  );
};

export default AppContent;

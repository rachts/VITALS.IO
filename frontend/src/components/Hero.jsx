import React from 'react';
import { motion } from 'framer-motion';
import CSVUploader from './CSVUploader';
import ColumnMapModal from './ColumnMapModal';
import { useApp } from '../context/AppContext';

const Hero = () => {
  const { columnMap } = useApp();

  return (
    <div className="min-h-screen flex items-center justify-center relative p-6 ml-0">
      <div className="max-w-3xl w-full">
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-primary/10 border border-accent-primary/20 text-accent-primary text-xs font-mono mb-6">
            <span className="w-2 h-2 rounded-full bg-accent-primary animate-pulse" />
            ENGINE v2.0 ONLINE
          </div>
          <h1 className="font-display text-5xl md:text-7xl font-bold mb-6 tracking-tight text-text-primary leading-tight">
            Monitor Your <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent-primary to-accent-secondary">Financial Pulse</span>
          </h1>
          <p className="text-text-muted text-lg md:text-xl max-w-xl mx-auto">
            Upload your raw financial CSV data to automatically calculate ARPA, churn, LTV, CAC, and project your cash runway.
          </p>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        >
          <CSVUploader />
        </motion.div>
      </div>

      {columnMap && <ColumnMapModal />}
    </div>
  );
};

export default Hero;

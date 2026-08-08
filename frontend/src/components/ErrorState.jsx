import React from 'react';
import { AlertCircle } from 'lucide-react';
import { useApp } from '../context/AppContext';

const ErrorState = () => {
  const { error, setError, setScreen } = useApp();

  return (
    <div className="flex flex-col items-center justify-center min-h-[400px]">
      <div className="bg-surface border border-red-500/30 rounded-lg p-8 max-w-md text-center">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-text-primary text-lg mb-2">Analysis Failed</h3>
        <p className="text-text-muted text-sm mb-6">{error || "Could not connect to analysis engine. Make sure the FastAPI server is running at localhost:8000"}</p>
        <button 
          onClick={() => { setError(null); setScreen('hero'); }}
          className="px-4 py-2 bg-elevated hover:bg-border text-text-primary rounded transition-colors"
        >
          Try Again
        </button>
      </div>
    </div>
  );
};

export default ErrorState;

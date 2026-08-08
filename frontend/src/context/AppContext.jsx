import React, { createContext, useContext, useState } from 'react';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [screen, setScreen] = useState('hero'); // 'hero' | 'dashboard'
  const [rawData, setRawData] = useState(null);
  const [columnMap, setColumnMap] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [scenarioResult, setScenarioResult] = useState(null);
  const [runwayResult, setRunwayResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filename, setFilename] = useState('');
  const [apiStatus, setApiStatus] = useState('checking'); // 'checking' | 'online' | 'offline'

  const value = {
    screen, setScreen,
    rawData, setRawData,
    columnMap, setColumnMap,
    analysisResult, setAnalysisResult,
    scenarioResult, setScenarioResult,
    runwayResult, setRunwayResult,
    isLoading, setIsLoading,
    error, setError,
    filename, setFilename,
    apiStatus, setApiStatus
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

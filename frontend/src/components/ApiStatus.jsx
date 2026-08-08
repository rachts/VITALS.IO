import React, { useEffect } from 'react';
import { useApp } from '../context/AppContext';
import api from '../api/client';

const ApiStatus = () => {
  const { apiStatus, setApiStatus } = useApp();

  useEffect(() => {
    const checkStatus = async () => {
      try {
        await api.get('/health');
        setApiStatus('online');
      } catch (err) {
        setApiStatus('offline');
      }
    };
    checkStatus();
  }, [setApiStatus]);

  if (apiStatus === 'checking') return null;

  return (
    <div className="flex items-center gap-2">
      <div className={`w-2 h-2 rounded-full ${apiStatus === 'online' ? 'bg-accent-success' : 'bg-red-500'}`} />
      <span className="text-xs text-text-muted">
        {apiStatus === 'online' ? 'API Connected' : 'API Offline'}
      </span>
    </div>
  );
};

export default ApiStatus;

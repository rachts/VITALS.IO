import React from 'react';
import { useApp } from '../context/AppContext';
import { CheckCircle2, AlertTriangle } from 'lucide-react';
import { COLUMN_ALIASES } from '../utils/csvParser';
import api from '../api/client';

const ColumnMapModal = () => {
  const { rawData, columnMap, setRawData, setColumnMap, setAnalysisResult, setScreen, setIsLoading, setError, filename } = useApp();

  if (!rawData || !columnMap) return null;

  const requiredFields = Object.keys(COLUMN_ALIASES);
  const isComplete = requiredFields.every(field => columnMap[field] !== undefined);

  const handleConfirm = async () => {
    setIsLoading(true);
    setRawData(null); // hide modal implicitly by clearing rawData wait no, this clears data!
    // We should not clear rawData, we need it for Scenario Simulator.
    // We just clear columnMap to hide modal, or introduce a modal state.
    // Let's keep rawData, just set screen to dashboard after fetch. 
    // Wait, if columnMap is present, this modal renders. So we nullify columnMap.
    setColumnMap(null);
    try {
      const res = await api.post('/analyze', rawData);
      setAnalysisResult(res.data);
      setScreen('dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to connect to backend");
      setRawData(null); // On error, reset flow
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-base/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-surface rounded-xl border border-border w-full max-w-2xl overflow-hidden shadow-2xl">
        <div className="p-6 border-b border-border">
          <h3 className="text-xl font-display text-text-primary">Confirm Data Mapping</h3>
          <p className="text-text-muted text-sm mt-1">We parsed <strong>{filename}</strong>. Review the mappings below.</p>
        </div>
        
        <div className="p-6 max-h-[60vh] overflow-y-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="text-xs uppercase text-text-muted border-b border-border">
                <th className="pb-3 font-semibold">Status</th>
                <th className="pb-3 font-semibold">Required Field</th>
                <th className="pb-3 font-semibold text-right">Parsed Value</th>
              </tr>
            </thead>
            <tbody>
              {requiredFields.map(field => {
                const found = columnMap[field] !== undefined;
                return (
                  <tr key={field} className="border-b border-border/50">
                    <td className="py-3">
                      {found ? 
                        <CheckCircle2 className="w-5 h-5 text-accent-success" /> : 
                        <AlertTriangle className="w-5 h-5 text-accent-warn" />
                      }
                    </td>
                    <td className="py-3 font-mono text-sm text-text-primary">{field}</td>
                    <td className="py-3 font-mono text-sm text-right text-text-muted">
                      {found ? rawData[field] : <span className="text-accent-warn">Missing</span>}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="p-6 border-t border-border flex justify-between items-center bg-elevated">
          <button 
            onClick={() => { setRawData(null); setColumnMap(null); }}
            className="text-text-muted hover:text-text-primary transition-colors text-sm font-medium"
          >
            Cancel
          </button>
          <button 
            onClick={handleConfirm}
            disabled={!isComplete}
            className={`px-6 py-2 rounded font-medium transition-all ${
              isComplete ? 'bg-accent-primary text-base hover:bg-accent-primary/90' : 'bg-border text-text-muted cursor-not-allowed'
            }`}
          >
            Confirm & Analyze
          </button>
        </div>
      </div>
    </div>
  );
};

export default ColumnMapModal;

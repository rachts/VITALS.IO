import React, { useState } from 'react';
import { HelpCircle, X } from 'lucide-react';

const HelpPanel = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button 
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-12 h-12 bg-elevated border border-border rounded-full flex items-center justify-center text-text-muted hover:text-accent-primary hover:border-accent-primary transition-all z-40"
      >
        <HelpCircle className="w-6 h-6" />
      </button>

      {isOpen && (
        <div className="fixed inset-y-0 right-0 w-80 bg-surface border-l border-border shadow-2xl z-50 p-6 overflow-y-auto">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-text-primary font-display text-xl">Metrics Guide</h3>
            <button onClick={() => setIsOpen(false)} className="text-text-muted hover:text-text-primary">
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="space-y-6">
            <div>
              <h4 className="text-accent-primary font-bold mb-1">ARPA</h4>
              <p className="text-sm text-text-muted">Average Revenue Per Account. Total MRR divided by total active customers.</p>
            </div>
            <div>
              <h4 className="text-accent-primary font-bold mb-1">CAC</h4>
              <p className="text-sm text-text-muted">Customer Acquisition Cost. Total sales and marketing spend divided by new customers acquired.</p>
            </div>
            <div>
              <h4 className="text-accent-primary font-bold mb-1">LTV</h4>
              <p className="text-sm text-text-muted">Lifetime Value. The gross margin you expect to make from a customer over their entire relationship with you.</p>
            </div>
            <div>
              <h4 className="text-accent-primary font-bold mb-1">LTV:CAC Ratio</h4>
              <p className="text-sm text-text-muted">The gold standard SaaS metric. 3.0x is considered good. Below 1.0x means you lose money on every customer.</p>
            </div>
            <div>
              <h4 className="text-accent-primary font-bold mb-1">Payback Period</h4>
              <p className="text-sm text-text-muted">How many months it takes for a customer's gross margin to pay back their CAC. Under 12 months is ideal.</p>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default HelpPanel;

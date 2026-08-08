import React from 'react';
import { Activity, LayoutDashboard, Settings } from 'lucide-react';
import ApiStatus from './ApiStatus';

const Sidebar = () => {
  return (
    <aside className="w-64 bg-surface border-r border-border h-screen fixed top-0 left-0 flex flex-col pt-8 pb-6 px-4 z-30">
      <div className="flex items-center gap-3 px-2 mb-12">
        <div className="w-8 h-8 rounded bg-accent-primary/10 flex items-center justify-center">
          <Activity className="w-5 h-5 text-accent-primary" />
        </div>
        <span className="font-display font-bold text-xl tracking-wide text-text-primary">VITALS.IO</span>
      </div>

      <nav className="flex-1 space-y-2">
        <a href="#" className="flex items-center gap-3 px-3 py-2 bg-elevated text-accent-primary rounded-lg">
          <LayoutDashboard className="w-5 h-5" />
          <span className="font-medium text-sm">Dashboard</span>
        </a>
        <a href="#" className="flex items-center gap-3 px-3 py-2 text-text-muted hover:text-text-primary transition-colors rounded-lg">
          <Settings className="w-5 h-5" />
          <span className="font-medium text-sm">Settings</span>
        </a>
      </nav>
      
      <div className="mt-auto px-2">
        <ApiStatus />
      </div>
    </aside>
  );
};

export default Sidebar;

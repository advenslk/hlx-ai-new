import React from 'react';

interface NavbarProps {
  activeTab: 'simulator' | 'ai-lab' | 'knowledge' | 'analytics' | 'codebase';
  setActiveTab: (tab: 'simulator' | 'ai-lab' | 'knowledge' | 'analytics' | 'codebase') => void;
  onOpenNewTicketModal: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, onOpenNewTicketModal }) => {
  return (
    <header className="flex items-center justify-between gap-8 px-6 py-3.5 bg-slate-900 border-b border-slate-800 text-slate-100 shrink-0">
      {/* Zone 1: Brand Wordmark */}
      <div className="flex items-center gap-2.5 whitespace-nowrap shrink-0">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white text-base tracking-wider shadow-sm">
          HX
        </div>
        <span className="text-base font-bold tracking-tight text-white font-sans">
          HELZERX AI SUPPORT
        </span>
      </div>

      {/* Zone 2: Navigation Links (Single-Line Text Links) */}
      <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-300">
        <button
          onClick={() => setActiveTab('simulator')}
          className={`whitespace-nowrap shrink-0 transition-colors pb-0.5 ${
            activeTab === 'simulator'
              ? 'text-white border-b-2 border-indigo-500 font-semibold'
              : 'hover:text-white'
          }`}
        >
          Discord Simulator
        </button>
        <button
          onClick={() => setActiveTab('ai-lab')}
          className={`whitespace-nowrap shrink-0 transition-colors pb-0.5 ${
            activeTab === 'ai-lab'
              ? 'text-white border-b-2 border-indigo-500 font-semibold'
              : 'hover:text-white'
          }`}
        >
          AI Engine Diagnostics
        </button>
        <button
          onClick={() => setActiveTab('knowledge')}
          className={`whitespace-nowrap shrink-0 transition-colors pb-0.5 ${
            activeTab === 'knowledge'
              ? 'text-white border-b-2 border-indigo-500 font-semibold'
              : 'hover:text-white'
          }`}
        >
          Knowledge & RAG
        </button>
        <button
          onClick={() => setActiveTab('analytics')}
          className={`whitespace-nowrap shrink-0 transition-colors pb-0.5 ${
            activeTab === 'analytics'
              ? 'text-white border-b-2 border-indigo-500 font-semibold'
              : 'hover:text-white'
          }`}
        >
          Analytics & Logs
        </button>
        <button
          onClick={() => setActiveTab('codebase')}
          className={`whitespace-nowrap shrink-0 transition-colors pb-0.5 ${
            activeTab === 'codebase'
              ? 'text-white border-b-2 border-indigo-500 font-semibold'
              : 'hover:text-white'
          }`}
        >
          Codebase & Deploy
        </button>
      </nav>

      {/* Zone 3: Single Primary Action */}
      <div className="flex items-center gap-3 shrink-0">
        <button
          onClick={onOpenNewTicketModal}
          className="px-4 py-2 text-xs font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-500 transition-colors shadow-sm whitespace-nowrap shrink-0 cursor-pointer"
        >
          Open Ticket
        </button>
      </div>
    </header>
  );
};

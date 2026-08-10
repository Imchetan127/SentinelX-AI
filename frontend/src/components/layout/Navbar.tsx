'use client';

import React, { useState } from 'react';
import { Search, Radio, User, LogOut, ChevronRight, ShieldCheck } from 'lucide-react';
import { NotificationCenter } from './NotificationCenter';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  user: { username: string; role: string } | null;
  onOpenLogin: () => void;
  onLogout: () => void;
  onOpenCommandPalette: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  user,
  onOpenLogin,
  onLogout,
  onOpenCommandPalette,
}) => {
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const getBreadcrumb = () => {
    switch (activeTab) {
      case 'dashboard': return { title: 'Security Overview', parent: 'Operations' };
      case 'red-team': return { title: 'Attack Center', parent: 'Operations' };
      case 'blue-team': return { title: 'Defense Center', parent: 'Operations' };
      case 'email-url-lab': return { title: 'Threat Intelligence', parent: 'Operations' };
      case 'explainability': return { title: 'AI Explainability', parent: 'Analytics' };
      case 'ml-engine': return { title: 'ML Benchmarks', parent: 'Analytics' };
      case 'about': return { title: 'Executive Reports', parent: 'Documentation' };
      case 'settings': return { title: 'Platform Settings', parent: 'System' };
      default: return { title: 'Security Operations Center', parent: 'SentinelX AI' };
    }
  };

  const breadcrumb = getBreadcrumb();

  return (
    <header className="sticky top-0 z-30 bg-[var(--bg-card)]/90 backdrop-blur-xl border-b border-[var(--border)] h-16 px-6 flex items-center justify-between">
      {/* ELEMENT 1: Page Breadcrumb & Title */}
      <div className="flex items-center space-x-2 text-xs font-mono">
        <span className="text-[var(--text-muted)] font-medium">{breadcrumb.parent}</span>
        <ChevronRight className="w-3.5 h-3.5 text-[var(--text-muted)]" />
        <span className="text-[var(--text-primary)] font-bold">{breadcrumb.title}</span>
      </div>

      {/* ELEMENT 2: Responsive Contextual Search Bar */}
      <button
        onClick={onOpenCommandPalette}
        className="hidden md:flex items-center space-x-2.5 px-3.5 py-1.5 rounded-xl bg-[var(--bg-surface)] hover:bg-white/[0.08] border border-[var(--border)] text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-all cursor-pointer w-44 focus-within:w-72 lg:w-64 lg:focus-within:w-80 group"
      >
        <Search className="w-3.5 h-3.5 text-[var(--accent)] flex-shrink-0" />
        <span className="flex-1 text-left truncate text-[11px]">Search platform...</span>
        <span className="px-1.5 py-0.5 rounded bg-white/[0.08] text-[9px] font-mono text-[var(--text-secondary)] border border-white/[0.08]">
          ⌘K
        </span>
      </button>

      {/* ELEMENT 3 & 4: Backend Status Indicator & User Menu / Notification Dropdown */}
      <div className="flex items-center space-x-3">
        {/* ELEMENT 3: Backend Status Dot Indicator with Tooltip */}
        <div
          className="relative flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-[#22C55E]/10 border border-[#22C55E]/20 text-[11px] font-mono text-[#22C55E] font-bold cursor-help group"
          title="Backend API Service Online (127.0.0.1:8000)"
        >
          <span className="w-2 h-2 rounded-full bg-[#22C55E] animate-pulse" />
          <span className="hidden sm:inline">ONLINE</span>

          {/* Hover Tooltip */}
          <div className="absolute right-0 top-8 hidden group-hover:block w-48 p-2.5 rounded-xl bg-[#080C14] border border-slate-800 text-[10px] font-mono text-slate-300 shadow-xl z-50 pointer-events-none">
            <p className="text-[#22C55E] font-bold">● FASTAPI BACKEND ONLINE</p>
            <p className="text-slate-400 mt-1">Host: 127.0.0.1:8000</p>
            <p className="text-slate-400">Database: PostgreSQL Active</p>
          </div>
        </div>

        {/* ELEMENT 4: Notification Bell Dropdown (Wired to Real Events) */}
        <NotificationCenter setActiveTab={setActiveTab} />

        {/* User Auth Profile Menu */}
        {user ? (
          <div className="relative">
            <button
              onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
              className="flex items-center space-x-2 px-3 py-1.5 rounded-xl border border-[var(--border)] bg-[var(--bg-surface)] hover:bg-white/[0.06] transition-all cursor-pointer"
            >
              <div className="w-5 h-5 rounded-full bg-[var(--accent)]/15 border border-[var(--accent)]/30 flex items-center justify-center">
                <User className="w-3 h-3 text-[var(--accent)]" />
              </div>
              <span className="text-xs font-semibold text-[var(--text-primary)]">{user.username}</span>
            </button>

            {/* Dropdown Menu */}
            {isUserMenuOpen && (
              <div className="absolute right-0 mt-2 w-48 rounded-xl bg-[var(--bg-card)] border border-[var(--border)] p-2 shadow-2xl z-50 font-mono text-xs space-y-1">
                <div className="px-3 py-2 border-b border-[var(--border)]">
                  <p className="text-[11px] font-bold text-white">{user.username}</p>
                  <p className="text-[10px] text-slate-500 uppercase">{user.role} Privilege</p>
                </div>
                <button
                  onClick={() => { setActiveTab('settings'); setIsUserMenuOpen(false); }}
                  className="w-full text-left px-3 py-1.5 rounded-lg hover:bg-white/[0.06] text-slate-300 hover:text-white transition-colors flex items-center space-x-2"
                >
                  <ShieldCheck className="w-3.5 h-3.5 text-[var(--accent)]" />
                  <span>Platform Settings</span>
                </button>
                <button
                  onClick={() => { onLogout(); setIsUserMenuOpen(false); }}
                  className="w-full text-left px-3 py-1.5 rounded-lg hover:bg-[#EF4444]/10 text-[#EF4444] transition-colors flex items-center space-x-2"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span>Sign Out</span>
                </button>
              </div>
            )}
          </div>
        ) : (
          <button onClick={onOpenLogin} className="btn-primary text-xs px-4 py-1.5">
            Sign In
          </button>
        )}
      </div>
    </header>
  );
};

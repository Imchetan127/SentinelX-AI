'use client';

import React, { useState, useEffect } from 'react';
import {
  Shield,
  LayoutDashboard,
  Flame,
  ShieldAlert,
  Globe,
  Brain,
  Cpu,
  FileText,
  Settings,
  ChevronLeft,
  ChevronRight,
  Radio,
  Users
} from 'lucide-react';
import { motion } from 'framer-motion';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('sentinelx_sidebar_collapsed');
    if (saved !== null) {
      setCollapsed(saved === 'true');
    }
  }, []);

  const toggleCollapsed = () => {
    const nextState = !collapsed;
    setCollapsed(nextState);
    localStorage.setItem('sentinelx_sidebar_collapsed', String(nextState));
  };

  const navItems = [
    { id: 'dashboard', label: 'Security Overview', icon: LayoutDashboard, category: 'Operations' },
    { id: 'red-team', label: 'Attack Center', icon: Flame, category: 'Operations' },
    { id: 'blue-team', label: 'Defense Center', icon: ShieldAlert, category: 'Operations' },
    { id: 'email-url-lab', label: 'Threat Intelligence', icon: Globe, category: 'Operations' },
    { id: 'explainability', label: 'AI Explainability', icon: Brain, category: 'Analytics' },
    { id: 'ml-engine', label: 'ML Benchmarks', icon: Cpu, category: 'Analytics' },
    { id: 'about', label: 'Executive Reports', icon: FileText, category: 'Documentation' },
    { id: 'settings', label: 'Settings', icon: Settings, category: 'System' },
  ];

  return (
    <motion.aside
      initial={false}
      animate={{ width: collapsed ? 72 : 256 }}
      transition={{ duration: 0.25, ease: 'easeInOut' }}
      className="relative z-40 bg-[var(--bg-card)] border-r border-[var(--border)] flex flex-col justify-between select-none"
    >
      {/* Brand & Toggle Header */}
      <div>
        <div className="h-16 px-4 flex items-center justify-between border-b border-[var(--border)]">
          <button
            onClick={() => setActiveTab('dashboard')}
            className="flex items-center space-x-3 overflow-hidden text-left focus:outline-none group"
          >
            <div className="w-8 h-8 rounded-xl bg-[var(--accent)]/15 border border-[var(--accent)]/30 flex items-center justify-center group-hover:border-[var(--accent)] transition-all flex-shrink-0">
              <Shield className="w-4 h-4 text-[var(--accent)]" />
            </div>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.15 }}
                className="whitespace-nowrap"
              >
                <h1 className="text-sm font-bold text-[var(--text-primary)] tracking-tight">
                  Sentinel<span className="text-[var(--accent)]">X</span> AI
                </h1>
                <p className="text-[10px] font-mono text-[var(--text-secondary)]">SOC Platform v5.0</p>
              </motion.div>
            )}
          </button>

          <button
            onClick={toggleCollapsed}
            className="w-7 h-7 rounded-lg bg-[var(--bg-surface)] hover:bg-white/[0.08] text-[var(--text-secondary)] hover:text-[var(--text-primary)] flex items-center justify-center border border-[var(--border)] transition-colors cursor-pointer"
            title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {collapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1.5 overflow-y-auto max-h-[calc(100vh-140px)]">
          {navItems.map(item => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`relative w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer group ${
                  isActive
                    ? 'bg-[var(--accent)]/12 text-[var(--accent)] border border-[var(--accent)]/25 shadow-sm'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-surface)]'
                }`}
                title={collapsed ? item.label : undefined}
              >
                <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-[var(--accent)]' : 'text-slate-400 group-hover:text-white'}`} />
                {!collapsed && (
                  <span className="truncate tracking-tight">{item.label}</span>
                )}
                {isActive && (
                  <motion.div
                    layoutId="sidebarActivePill"
                    className="absolute right-2 w-1.5 h-1.5 rounded-full bg-[var(--accent)] shadow-sm"
                  />
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer System Status */}
      <div className="p-3 border-t border-[var(--border)] bg-[var(--bg-surface)]/50">
        <div className={`flex items-center ${collapsed ? 'justify-center' : 'space-x-2.5 px-2 py-1.5'}`}>
          <Radio className="w-3 h-3 text-[#22C55E] animate-pulse flex-shrink-0" />
          {!collapsed && (
            <div className="text-[10px] font-mono leading-tight truncate">
              <span className="text-[#22C55E] font-bold block">SYSTEM OPERATIONAL</span>
              <span className="text-[var(--text-muted)]">Enterprise v5.0</span>
            </div>
          )}
        </div>
      </div>
    </motion.aside>
  );
};

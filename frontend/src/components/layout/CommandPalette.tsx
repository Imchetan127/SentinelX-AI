'use client';

import React, { useEffect, useState } from 'react';
import { Search, Flame, ShieldAlert, Globe, Brain, FileText, Settings, LogOut, Command, Play, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  setActiveTab: (tab: string) => void;
  onRunPlaybook?: (vectorId: string) => void;
  onLogout: () => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  isOpen,
  onClose,
  setActiveTab,
  onRunPlaybook,
  onLogout,
}) => {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  const actions = [
    { id: 'dashboard', label: 'Go to Security Overview', category: 'Navigation', icon: Search, tab: 'dashboard' },
    { id: 'red-team', label: 'Go to Attack Center (Red Team)', category: 'Navigation', icon: Flame, tab: 'red-team' },
    { id: 'blue-team', label: 'Go to Defense Center (Blue Team)', category: 'Navigation', icon: ShieldAlert, tab: 'blue-team' },
    { id: 'email-url-lab', label: 'Go to Threat Intelligence Lab', category: 'Navigation', icon: Globe, tab: 'email-url-lab' },
    { id: 'explainability', label: 'Go to AI Explainability Center', category: 'Navigation', icon: Brain, tab: 'explainability' },
    { id: 'about', label: 'View Executive Reports & Team', category: 'Navigation', icon: FileText, tab: 'about' },
    { id: 'settings', label: 'Open Platform Settings', category: 'Navigation', icon: Settings, tab: 'settings' },
    { id: 'run-sqli', label: 'Run SQL Injection Attack Simulation', category: 'Quick Action', icon: Play, action: () => { setActiveTab('red-team'); if (onRunPlaybook) onRunPlaybook('sqli-auth-bypass'); } },
    { id: 'logout', label: 'Sign Out of SentinelX AI', category: 'System', icon: LogOut, action: onLogout },
  ];

  const filteredActions = actions.filter(
    a => a.label.toLowerCase().includes(query.toLowerCase()) || a.category.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
        else setQuery('');
      }
      if (!isOpen) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex(prev => (prev + 1) % (filteredActions.length || 1));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex(prev => (prev - 1 + filteredActions.length) % (filteredActions.length || 1));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (filteredActions[selectedIndex]) {
          handleExecute(filteredActions[selectedIndex]);
        }
      } else if (e.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, selectedIndex, filteredActions]);

  const handleExecute = (item: any) => {
    if (item.tab) {
      setActiveTab(item.tab);
    } else if (item.action) {
      item.action();
    }
    onClose();
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-[#000000]/60 z-50 flex items-start justify-center pt-24 backdrop-blur-sm px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.96, y: -10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.96, y: -10 }}
          transition={{ duration: 0.18, ease: 'easeOut' }}
          className="w-full max-w-xl bg-[var(--bg-card)] border border-[var(--border-hover)] rounded-2xl shadow-2xl overflow-hidden"
        >
          {/* Search Header */}
          <div className="p-4 border-b border-[var(--border)] flex items-center space-x-3 bg-[var(--bg-surface)]">
            <Search className="w-5 h-5 text-[var(--accent)] flex-shrink-0" />
            <input
              type="text"
              autoFocus
              value={query}
              onChange={e => { setQuery(e.target.value); setSelectedIndex(0); }}
              placeholder="Type a command or search platform (Ctrl + K)..."
              className="w-full bg-transparent border-none text-sm text-[var(--text-primary)] focus:outline-none font-sans placeholder-[var(--text-muted)]"
            />
            <span className="px-2 py-0.5 rounded bg-white/[0.08] text-[10px] font-mono text-[var(--text-secondary)] border border-white/[0.1]">
              ESC to exit
            </span>
          </div>

          {/* Action List */}
          <div className="max-h-80 overflow-y-auto p-2 space-y-1">
            {filteredActions.length > 0 ? (
              filteredActions.map((item, idx) => {
                const Icon = item.icon;
                const isSelected = selectedIndex === idx;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleExecute(item)}
                    onMouseEnter={() => setSelectedIndex(idx)}
                    className={`w-full flex items-center justify-between px-3.5 py-3 rounded-xl text-xs transition-colors cursor-pointer ${
                      isSelected ? 'bg-[var(--accent)]/15 text-[var(--text-primary)] border border-[var(--accent)]/30' : 'text-[var(--text-secondary)] hover:bg-white/[0.04]'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <Icon className={`w-4 h-4 ${isSelected ? 'text-[var(--accent)]' : 'text-slate-400'}`} />
                      <span className="font-medium text-left">{item.label}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-[10px] font-mono text-[var(--text-muted)] uppercase">{item.category}</span>
                      <ArrowRight className={`w-3.5 h-3.5 ${isSelected ? 'text-[var(--accent)]' : 'text-slate-600'}`} />
                    </div>
                  </button>
                );
              })
            ) : (
              <div className="p-8 text-center text-xs text-[var(--text-muted)] font-mono">
                No commands matching "{query}"
              </div>
            )}
          </div>

          {/* Footer Keyboard Hints */}
          <div className="p-3 border-t border-[var(--border)] bg-[var(--bg-surface)] flex items-center justify-between text-[11px] font-mono text-[var(--text-secondary)]">
            <div className="flex items-center space-x-3">
              <span>↑↓ Navigate</span>
              <span>↵ Execute</span>
            </div>
            <span>SentinelX AI SOC Search</span>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

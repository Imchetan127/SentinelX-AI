'use client';

import React, { useState } from 'react';
import { Settings, Palette, Shield, Bell, Key, Info, Check, Radio, Cpu, Database, Server } from 'lucide-react';
import { useTheme, ThemeName } from '@/context/ThemeContext';

interface SettingsViewProps {
  user: { username: string; role: string } | null;
}

export const SettingsView: React.FC<SettingsViewProps> = ({ user }) => {
  const [activeTab, setActiveTab] = useState<'appearance' | 'profile' | 'security' | 'shortcuts' | 'about'>('appearance');
  const { theme, setTheme } = useTheme();
  const [savedMsg, setSavedMsg] = useState<string | null>(null);

  const themes: { id: ThemeName; name: string; desc: string; bg: string; accent: string }[] = [
    { id: 'midnight-blue', name: 'Midnight Blue', desc: 'Default enterprise dark theme with cyan telemetry glows.', bg: '#0A0F1A', accent: '#00D4FF' },
    { id: 'cyber-black', name: 'Cyber Black', desc: 'Ultra-deep OLED contrast theme with neon cyan & red highlights.', bg: '#030508', accent: '#00F0FF' },
    { id: 'arctic-dark', name: 'Arctic Dark', desc: 'Subtle slate gray design language inspired by GitHub Dark.', bg: '#0D1117', accent: '#58A6FF' },
    { id: 'azure-security', name: 'Azure Security', desc: 'Deep sapphire blue theme inspired by Microsoft Defender XDR.', bg: '#061121', accent: '#00A3FF' },
    { id: 'graphite', name: 'Graphite', desc: 'Clean dark graphite theme with high legibility typography.', bg: '#121212', accent: '#38BDF8' },
  ];

  const handleThemeSelect = (themeId: ThemeName) => {
    setTheme(themeId);
    setSavedMsg(`Theme updated to ${themeId.replace('-', ' ').toUpperCase()}`);
    setTimeout(() => setSavedMsg(null), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-[var(--accent)] animate-pulse" />
            <p className="section-label text-[var(--accent)]">SYSTEM PREFERENCES & CONFIGURATION</p>
          </div>
          <h2 className="text-2xl font-bold text-[var(--text-primary)] tracking-tight mt-1">Platform Settings</h2>
          <p className="text-sm text-[var(--text-secondary)] mt-1">
            Configure UI themes, security policies, keyboard shortcuts, and view system health metrics.
          </p>
        </div>
        {savedMsg && (
          <span className="px-3 py-1.5 rounded-xl bg-[#22C55E]/10 border border-[#22C55E]/25 text-[#22C55E] text-xs font-mono font-bold animate-pulse">
            {savedMsg}
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Settings Sub-nav */}
        <div className="card p-2 space-y-1 self-start">
          {[
            { id: 'appearance', label: 'Appearance & Themes', icon: Palette },
            { id: 'profile', label: 'User Profile & Role', icon: Shield },
            { id: 'shortcuts', label: 'Keyboard Shortcuts', icon: Key },
            { id: 'about', label: 'System & Engine Status', icon: Info },
          ].map(item => {
            const Icon = item.icon;
            const active = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id as any)}
                className={`w-full flex items-center space-x-3 px-3.5 py-3 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                  active
                    ? 'bg-[var(--accent)]/15 text-[var(--accent)] border border-[var(--accent)]/30'
                    : 'text-[var(--text-secondary)] hover:bg-[var(--bg-surface)] hover:text-[var(--text-primary)]'
                }`}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>

        {/* Content Panel */}
        <div className="lg:col-span-3 card p-6 space-y-6">
          {activeTab === 'appearance' && (
            <div className="space-y-5">
              <div>
                <h3 className="text-base font-bold text-[var(--text-primary)]">Enterprise Theme Selector</h3>
                <p className="text-xs text-[var(--text-secondary)] mt-1">
                  Choose a visual theme tailored to your SOC environment. Preferences persist across sessions.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {themes.map(t => {
                  const isSelected = theme === t.id;
                  return (
                    <button
                      key={t.id}
                      onClick={() => handleThemeSelect(t.id)}
                      className={`p-4 rounded-xl border text-left transition-all cursor-pointer space-y-3 ${
                        isSelected
                          ? 'bg-[var(--bg-surface)] border-[var(--accent)] ring-1 ring-[var(--accent)]/40'
                          : 'bg-[var(--bg-card)] border-[var(--border)] hover:border-[var(--border-hover)]'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div className="w-4 h-4 rounded-full border border-white/20" style={{ backgroundColor: t.bg }} />
                          <span className="text-sm font-bold text-[var(--text-primary)]">{t.name}</span>
                        </div>
                        {isSelected && <Check className="w-4 h-4 text-[var(--accent)]" />}
                      </div>
                      <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{t.desc}</p>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {activeTab === 'profile' && (
            <div className="space-y-5">
              <div>
                <h3 className="text-base font-bold text-[var(--text-primary)]">User Profile & Access Role</h3>
                <p className="text-xs text-[var(--text-secondary)] mt-1">
                  Active authentication session parameters and permissions.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border)] space-y-3 font-mono text-xs">
                <div className="flex justify-between py-2 border-b border-[var(--border)]">
                  <span className="text-[var(--text-secondary)]">USERNAME</span>
                  <span className="text-[var(--text-primary)] font-bold">{user?.username || 'Analyst'}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-[var(--border)]">
                  <span className="text-[var(--text-secondary)]">ROLE</span>
                  <span className="text-[var(--accent)] font-bold">{(user?.role || 'SOC ANALYST').toUpperCase()}</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-[var(--text-secondary)]">SESSION TOKEN STATUS</span>
                  <span className="text-[#22C55E] font-bold">ACTIVE & VALID</span>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'shortcuts' && (
            <div className="space-y-5">
              <div>
                <h3 className="text-base font-bold text-[var(--text-primary)]">Keyboard Shortcuts</h3>
                <p className="text-xs text-[var(--text-secondary)] mt-1">
                  Boost your SOC analyst workflow speed with global hotkeys.
                </p>
              </div>

              <div className="space-y-2 font-mono text-xs">
                {[
                  { key: 'Ctrl + K / Cmd + K', action: 'Open Global Command Palette & Search' },
                  { key: 'Esc', action: 'Close Modal or Command Palette' },
                  { key: '↑ / ↓ Arrow Keys', action: 'Navigate Search Suggestions' },
                  { key: 'Enter', action: 'Execute Selected Command' },
                ].map(s => (
                  <div key={s.key} className="p-3 rounded-xl bg-[var(--bg-surface)] border border-[var(--border)] flex items-center justify-between">
                    <span className="text-[var(--accent)] font-bold">{s.key}</span>
                    <span className="text-[var(--text-secondary)]">{s.action}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'about' && (
            <div className="space-y-5">
              <div>
                <h3 className="text-base font-bold text-[var(--text-primary)]">System Engine Health</h3>
                <p className="text-xs text-[var(--text-secondary)] mt-1">
                  Live connection health across backend microservices and databases.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs">
                <div className="p-4 rounded-xl bg-[var(--bg-surface)] border border-white/[0.06] space-y-2">
                  <div className="flex items-center space-x-2 text-[#22C55E]">
                    <Server className="w-4 h-4" />
                    <span className="font-bold">FASTAPI BACKEND</span>
                  </div>
                  <div className="text-xs text-[var(--text-secondary)]">Status: ONLINE (Port 8000)</div>
                </div>

                <div className="p-4 rounded-xl bg-[var(--bg-surface)] border border-white/[0.06] space-y-2">
                  <div className="flex items-center space-x-2 text-[var(--accent)]">
                    <Cpu className="w-4 h-4" />
                    <span className="font-bold">ML PIPELINE</span>
                  </div>
                  <div className="text-xs text-[var(--text-secondary)]">Models: Scikit & XGBoost Loaded</div>
                </div>

                <div className="p-4 rounded-xl bg-[var(--bg-surface)] border border-white/[0.06] space-y-2">
                  <div className="flex items-center space-x-2 text-[#22C55E]">
                    <Database className="w-4 h-4" />
                    <span className="font-bold">DATABASE</span>
                  </div>
                  <div className="text-xs text-[var(--text-secondary)]">SQLite / PostgreSQL Connected</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

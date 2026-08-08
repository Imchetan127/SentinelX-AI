'use client';

import React from 'react';
import { Shield, Flame, Activity, Brain, Cpu, Mail, User, LogOut, Radio, Info } from 'lucide-react';
import { motion } from 'framer-motion';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  user: { username: string; role: string } | null;
  onOpenLogin: () => void;
  onLogout: () => void;
  onGoHome: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  user,
  onOpenLogin,
  onLogout,
  onGoHome,
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Overview', icon: Activity },
    { id: 'red-team', label: 'Red Team Simulator', icon: Flame },
    { id: 'blue-team', label: 'Blue Team AI Inspector', icon: Shield },
    { id: 'email-url-lab', label: 'Threat Intelligence Lab', icon: Mail },
    { id: 'ml-engine', label: 'ML Benchmarks', icon: Cpu },
    { id: 'explainability', label: 'Explainable AI', icon: Brain },
    { id: 'about', label: 'About', icon: Info },
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#090B10]/85 backdrop-blur-md border-b border-white/[0.08] px-6 py-3.5 flex items-center justify-between min-w-[1280px]">
      {/* Left: Primary SaaS Brand Navigation Element */}
      <button
        onClick={() => setActiveTab('dashboard')}
        className="flex items-center space-x-3 group cursor-pointer transition-all duration-200 hover:brightness-125 hover:scale-[1.01] text-left focus:outline-none"
        title="SentinelX AI — Dashboard Home"
      >
        <div>
          <div className="flex items-center space-x-2.5">
            <h1 className="text-base font-extrabold tracking-tight text-white">
              Sentinel<span className="text-[#00D4FF]">X</span> AI
            </h1>
            <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-[#00D4FF]/10 text-[#00D4FF] border border-[#00D4FF]/20 font-semibold">
              v1.0
            </span>
            <span className="hidden xl:inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[#2EE59D] text-[10px] font-mono">
              <Radio className="w-2.5 h-2.5 animate-pulse text-[#2EE59D]" />
              <span>SOC ACTIVE</span>
            </span>
          </div>
          <p className="text-[10px] text-slate-400 font-mono tracking-widest uppercase">ENTERPRISE SOC PLATFORM</p>
        </div>
      </button>

      {/* Navigation Tabs with Framer Motion Sliding Pill */}
      <nav className="flex items-center space-x-1 bg-[#111827] p-1 rounded-xl border border-white/[0.08] text-xs font-medium relative">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          const isXAI = item.id === 'explainability';

          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`relative flex items-center space-x-2 px-3.5 py-2 rounded-lg transition-colors duration-150 ${
                isActive
                  ? isXAI
                    ? 'text-purple-300 font-semibold'
                    : 'text-[#00D4FF] font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {isActive && (
                <motion.div
                  layoutId="activeTabIndicator"
                  className={`absolute inset-0 rounded-lg ${
                    isXAI
                      ? 'bg-purple-500/15 border border-purple-500/30'
                      : 'bg-[#161B22] border border-[#00D4FF]/30'
                  }`}
                  transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                />
              )}
              <span className="relative z-10 flex items-center space-x-2">
                <Icon className={`w-3.5 h-3.5 ${isActive ? (isXAI ? 'text-purple-400' : 'text-[#00D4FF]') : 'text-slate-500'}`} />
                <span>{item.label}</span>
              </span>
            </button>
          );
        })}
      </nav>

      {/* Right: Authenticated User & Actions */}
      <div className="flex items-center space-x-3 text-xs font-mono">
        {user ? (
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 px-3.5 py-1.5 rounded-xl bg-[#111827] border border-white/[0.08] text-slate-200">
              <User className="w-3.5 h-3.5 text-[#00D4FF]" />
              <span className="font-semibold text-xs tracking-wide text-white">{user.username}</span>
              <span
                className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold uppercase tracking-wider ${
                  (user.role || 'USER').toUpperCase() === 'ADMIN'
                    ? 'bg-[#FF5D73]/15 text-[#FF5D73] border border-[#FF5D73]/30'
                    : (user.role || 'USER').toUpperCase().includes('ANALYST')
                    ? 'bg-[#00D4FF]/15 text-[#00D4FF] border border-[#00D4FF]/30'
                    : 'bg-[#2EE59D]/15 text-[#2EE59D] border border-[#2EE59D]/30'
                }`}
              >
                {(user.role || 'USER').toUpperCase()}
              </span>
            </div>
            <button
              onClick={onLogout}
              className="p-2 rounded-xl bg-[#111827] border border-white/[0.08] hover:border-[#FF5D73]/40 text-slate-400 hover:text-[#FF5D73] transition-all btn-premium"
              title="Sign Out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <button
            onClick={onOpenLogin}
            className="px-4 py-2 rounded-xl bg-[#00D4FF] hover:bg-[#00D4FF]/90 text-slate-950 font-bold text-xs transition-all shadow-md btn-premium"
          >
            Sign In / Register
          </button>
        )}
      </div>
    </header>
  );
};

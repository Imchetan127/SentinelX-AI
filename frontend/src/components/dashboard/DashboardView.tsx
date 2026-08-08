'use client';

import React, { useEffect, useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, Activity, Cpu, Flame, TrendingUp, ShieldAlert, ArrowUpRight, Clock, Search, Filter } from 'lucide-react';
import { motion } from 'framer-motion';

const API_BASE = 'http://localhost:8000/api/v1';

async function authFetch(path: string, init: RequestInit = {}) {
  const token = sessionStorage.getItem('rb_auth_token');
  const headers = {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(init.headers || {}),
  };

  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  });

  if (response.status === 401 || response.status === 403) {
    sessionStorage.removeItem('rb_auth_token');
    window.location.href = '/';
  }

  return response;
}

interface DashboardViewProps {
  username?: string;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ username = 'Security Analyst' }) => {
  const [metrics, setMetrics] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [greeting, setGreeting] = useState('Good Day');

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good Morning');
    else if (hour < 18) setGreeting('Good Afternoon');
    else setGreeting('Good Evening');

    const fetchMetrics = () => {
      authFetch('/dashboard/metrics')
        .then((res) => res.json())
        .then((data) => setMetrics(data))
        .catch(() => {});
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 3000);
    return () => clearInterval(interval);
  }, []);

  if (!metrics) {
    return (
      <div className="min-h-[400px] flex flex-col items-center justify-center space-y-3 font-mono text-xs text-[#00D4FF]">
        <Activity className="w-8 h-8 animate-spin text-[#00D4FF]" />
        <span>Initializing Security Operations Center Matrix...</span>
      </div>
    );
  }

  const filteredEvents = metrics.recent_activity_timeline?.filter((act: any) =>
    act.event.toLowerCase().includes(searchQuery.toLowerCase()) ||
    act.severity.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  return (
    <div className="space-y-6">
      {/* Executive Hero Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-white/[0.08] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <div className="flex items-center space-x-3">
            <h2 className="text-2xl font-extrabold text-white tracking-tight">
              {greeting}, <span className="text-[#00D4FF]">{username}</span>
            </h2>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-[#2EE59D] border border-emerald-500/20 font-semibold">
              SOC ONLINE
            </span>
          </div>
          <p className="text-xs text-slate-400 font-mono">
            Autonomous threat simulation engine active • Real-time ML detection model confidence: {metrics.detection_accuracy_percent}%
          </p>

          {/* Status Metrics Pills */}
          <div className="flex flex-wrap gap-2 pt-1 font-mono text-[11px]">
            <div className="px-2.5 py-1 rounded-lg bg-[#111827] border border-white/[0.08] flex items-center space-x-1.5">
              <span className="text-slate-400">Security Status:</span>
              <span className="text-[#2EE59D] font-bold">OPTIMAL</span>
            </div>
            <div className="px-2.5 py-1 rounded-lg bg-[#111827] border border-white/[0.08] flex items-center space-x-1.5">
              <span className="text-slate-400">Threat Level:</span>
              <span className="text-[#00D4FF] font-bold">MODERATE</span>
            </div>
            <div className="px-2.5 py-1 rounded-lg bg-[#111827] border border-white/[0.08] flex items-center space-x-1.5">
              <span className="text-slate-400">Model Pipeline:</span>
              <span className="text-purple-300 font-bold">ACTIVE</span>
            </div>
            <div className="px-2.5 py-1 rounded-lg bg-[#111827] border border-white/[0.08] flex items-center space-x-1.5 text-slate-400">
              <Clock className="w-3 h-3 text-[#00D4FF]" />
              <span>Last Analysis: Just now</span>
            </div>
          </div>
        </div>
      </div>

      {/* Top Banner KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Telemetry Processed */}
        <motion.div
          whileHover={{ y: -3 }}
          transition={{ duration: 0.2 }}
          className="glass-panel p-5 rounded-2xl border border-white/[0.08] relative overflow-hidden space-y-3"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase text-slate-400 tracking-wider">Total Telemetry</span>
            <div className="p-2 rounded-xl bg-[#00D4FF]/10 text-[#00D4FF] border border-[#00D4FF]/20">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div>
            <p className="text-3xl font-extrabold text-white font-mono tracking-tight">
              {metrics.total_threats_analyzed.toLocaleString()}
            </p>
            <div className="flex items-center space-x-1 mt-1 text-xs text-[#00D4FF] font-mono">
              <TrendingUp className="w-3.5 h-3.5" />
              <span>+14.2% from baseline</span>
            </div>
          </div>
        </motion.div>

        {/* Threats Detected */}
        <motion.div
          whileHover={{ y: -3 }}
          transition={{ duration: 0.2 }}
          className="glass-panel p-5 rounded-2xl border border-white/[0.08] relative overflow-hidden space-y-3"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase text-slate-400 tracking-wider">Threats Detected</span>
            <div className="p-2 rounded-xl bg-[#FF5D73]/10 text-[#FF5D73] border border-[#FF5D73]/20">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div>
            <p className="text-3xl font-extrabold text-[#FF5D73] font-mono tracking-tight">
              {metrics.threats_detected.toLocaleString()}
            </p>
            <span className="text-xs text-slate-400 font-mono mt-1 block">
              34.2% of total traffic
            </span>
          </div>
        </motion.div>

        {/* Mitigated / Blocked Rate */}
        <motion.div
          whileHover={{ y: -3 }}
          transition={{ duration: 0.2 }}
          className="glass-panel p-5 rounded-2xl border border-white/[0.08] relative overflow-hidden space-y-3"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase text-slate-400 tracking-wider">Mitigated Rate</span>
            <div className="p-2 rounded-xl bg-[#2EE59D]/10 text-[#2EE59D] border border-[#2EE59D]/20">
              <CheckCircle className="w-4 h-4" />
            </div>
          </div>
          <div>
            <p className="text-3xl font-extrabold text-[#2EE59D] font-mono tracking-tight">
              {metrics.threats_blocked.toLocaleString()}
            </p>
            <div className="flex items-center space-x-1 mt-1 text-xs text-[#2EE59D] font-mono">
              <ArrowUpRight className="w-3.5 h-3.5" />
              <span>99.34% Mitigation Efficiency</span>
            </div>
          </div>
        </motion.div>

        {/* AI Detection Accuracy */}
        <motion.div
          whileHover={{ y: -3 }}
          transition={{ duration: 0.2 }}
          className="glass-panel p-5 rounded-2xl border border-white/[0.08] relative overflow-hidden space-y-3"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase text-slate-400 tracking-wider">AI Accuracy</span>
            <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <Cpu className="w-4 h-4" />
            </div>
          </div>
          <div>
            <p className="text-3xl font-extrabold text-white font-mono tracking-tight">
              {metrics.detection_accuracy_percent}%
            </p>
            <span className="text-xs text-purple-300 font-mono mt-1 block">
              False Positives: {metrics.false_positives_percent}%
            </span>
          </div>
        </motion.div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2-Cols: Red Team vs Blue Team System Defense Status */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-white/[0.08] space-y-6">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-xl bg-[#FF5D73]/10 text-[#FF5D73]">
                <Flame className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">System Defense Matrix</h3>
                <p className="text-xs text-slate-400 font-mono">Red Team Adversary Simulation vs Blue Team ML Defense</p>
              </div>
            </div>
            <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-500/10 text-[#2EE59D] border border-emerald-500/20">
              {metrics.system_health || 'OPTIMAL'}
            </span>
          </div>

          {/* Key Security Indicators Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-[#111827] border border-white/[0.08] space-y-1">
              <span className="text-xs text-slate-400 font-mono uppercase">System Health Status</span>
              <p className="text-lg font-bold text-[#2EE59D] font-mono">{metrics.system_health}</p>
            </div>
            <div className="p-4 rounded-xl bg-[#111827] border border-white/[0.08] space-y-1">
              <span className="text-xs text-slate-400 font-mono uppercase">Adversary Success</span>
              <p className="text-lg font-bold text-[#FFB547] font-mono">{metrics.attack_success_rate_percent}%</p>
            </div>
            <div className="p-4 rounded-xl bg-[#111827] border border-white/[0.08] space-y-1">
              <span className="text-xs text-slate-400 font-mono uppercase">False Negatives Rate</span>
              <p className="text-lg font-bold text-[#00D4FF] font-mono">{metrics.false_negatives_percent}%</p>
            </div>
          </div>

          {/* Model Accuracy Visual Bar Indicator */}
          <div className="p-5 rounded-xl bg-[#111827] border border-white/[0.08] space-y-3">
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-slate-300 font-semibold">Active Model Confidence Index</span>
              <span className="text-[#00D4FF] font-bold">{metrics.detection_accuracy_percent}% Optimal</span>
            </div>
            <div className="w-full bg-[#090B10] rounded-full h-2.5 overflow-hidden border border-white/[0.08]">
              <div
                className="h-full bg-gradient-to-r from-[#00D4FF] to-purple-500 rounded-full transition-all duration-500"
                style={{ width: `${metrics.detection_accuracy_percent}%` }}
              />
            </div>
          </div>
        </div>

        {/* Right 1-Col: Live Security Audit Stream Feed with Search Filter */}
        <div className="glass-panel p-6 rounded-2xl border border-white/[0.08] space-y-4 flex flex-col">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
            <div className="flex items-center space-x-2">
              <ShieldAlert className="w-4 h-4 text-[#00D4FF]" />
              <h3 className="text-sm font-bold text-white uppercase font-mono">Live Audit Stream</h3>
            </div>
            <span className="text-[10px] font-mono text-slate-400">REALTIME</span>
          </div>

          {/* Search Filter Input */}
          <div className="relative font-mono text-xs">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search events or severity..."
              className="w-full bg-[#090B10] border border-white/[0.08] rounded-xl pl-9 pr-3 py-2 text-slate-200 focus:outline-none focus:border-[#00D4FF]/50 text-xs"
            />
          </div>

          {/* Stream Log Items */}
          <div className="space-y-3 font-mono text-xs max-h-[350px] overflow-y-auto pr-1 flex-1">
            {filteredEvents.map((act: any, idx: number) => (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-[#111827] border border-white/[0.08] space-y-1.5 hover:border-white/[0.15] transition-all"
              >
                <div className="flex items-center justify-between text-slate-400 text-[11px]">
                  <span>{act.time}</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                      act.severity === 'Critical'
                        ? 'bg-[#FF5D73]/15 text-[#FF5D73] border border-[#FF5D73]/30'
                        : act.severity === 'High'
                        ? 'bg-[#FFB547]/15 text-[#FFB547] border border-[#FFB547]/30'
                        : 'bg-[#00D4FF]/15 text-[#00D4FF] border border-[#00D4FF]/30'
                    }`}
                  >
                    {act.severity}
                  </span>
                </div>
                <p className="text-slate-200 font-sans text-xs leading-relaxed">{act.event}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

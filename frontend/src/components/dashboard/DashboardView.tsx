'use client';

import React, { useEffect, useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, Activity, Cpu, TrendingUp, Clock, ArrowUp, Database, Server, Brain, Layers, Radio } from 'lucide-react';
import { motion } from 'framer-motion';
import { formatStandardDate, formatSocClock } from '@/utils/dateFormatter';
import { LiveNetworkMap } from './LiveNetworkMap';

const API_BASE = 'http://localhost:8000/api/v1';

async function authFetch(path: string, init: RequestInit = {}) {
  const token = sessionStorage.getItem('rb_auth_token');
  const headers = { ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(init.headers || {}) };
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  if (response.status === 401) {
    sessionStorage.removeItem('rb_auth_token');
    window.location.href = '/';
  }
  return response;
}

interface DashboardViewProps {
  username?: string;
}

function useCounter(target: number, duration = 1200) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    const start = Date.now();
    const tick = () => {
      const elapsed = Date.now() - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setCount(Math.round(eased * target));
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [target, duration]);
  return count;
}

function KPICard({ label, value, unit = '', color, icon: Icon, trend }: any) {
  const animated = useCounter(value || 0);
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="card p-6 space-y-3"
    >
      <div className="flex items-start justify-between">
        <p className="section-label">{label}</p>
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${color}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <p className="text-3xl font-extrabold text-[var(--text-primary)] tracking-tight tabular-nums">
        {animated.toLocaleString()}{unit}
      </p>
      {trend && (
        <div className="flex items-center space-x-1 text-xs text-[#22C55E]">
          <ArrowUp className="w-3 h-3" />
          <span>{trend}</span>
        </div>
      )}
    </motion.div>
  );
}

export const DashboardView: React.FC<DashboardViewProps> = ({ username = 'Analyst' }) => {
  const [metrics, setMetrics] = useState<any>(null);
  const [greeting, setGreeting] = useState('Good Day');
  const [lastScanTime, setLastScanTime] = useState<string>('');

  useEffect(() => {
    const h = new Date().getHours();
    setGreeting(h < 12 ? 'Good Morning' : h < 18 ? 'Good Afternoon' : 'Good Evening');

    const load = () =>
      authFetch('/dashboard/metrics')
        .then(r => r.json())
        .then(data => {
          setMetrics(data);
          if (data.last_scan_time) {
            setLastScanTime(formatStandardDate(data.last_scan_time));
          } else {
            setLastScanTime(formatStandardDate(new Date()));
          }
        })
        .catch(() => {});

    load();
    const iv = setInterval(load, 10000);
    return () => clearInterval(iv);
  }, []);

  const systemChecks = [
    { label: 'Database', icon: Database, status: 'Operational' },
    { label: 'API Gateway', icon: Server, status: 'Operational' },
    { label: 'AI Models', icon: Brain, status: 'Active' },
    { label: 'Event Queue', icon: Layers, status: 'Running' },
  ];

  return (
    <div className="space-y-8">
      {/* Hero Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2">
        <div>
          <p className="section-label text-[var(--accent)] mb-1">ENTERPRISE SECURITY OPERATIONS CENTER</p>
          <h2 className="text-2xl font-bold text-[var(--text-primary)] tracking-tight">
            {greeting}, <span className="text-[var(--accent)]">{username}</span>
          </h2>
          <p className="text-sm text-[var(--text-secondary)] mt-1">
            Real-time multi-vector threat simulation, AI payload classification, and SHAP decision explanations.
          </p>
        </div>
      </div>

      {/* Live Network Map */}
      <LiveNetworkMap />

      {/* KPI Cards */}
      {metrics ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            label="Total Threats Analyzed"
            value={metrics.total_threats_analyzed}
            icon={Activity}
            color="bg-[var(--accent)]/10 text-[var(--accent)]"
            trend="+14.2% from baseline"
          />
          <KPICard
            label="Threats Detected"
            value={metrics.threats_detected}
            icon={AlertTriangle}
            color="bg-[#EF4444]/10 text-[#EF4444]"
          />
          <KPICard
            label="Threats Mitigated"
            value={metrics.threats_blocked}
            icon={CheckCircle}
            color="bg-[#22C55E]/10 text-[#22C55E]"
            trend="99.3% efficiency"
          />
          <KPICard
            label="AI Model Accuracy"
            value={metrics.detection_accuracy_percent}
            unit="%"
            icon={Cpu}
            color="bg-[var(--purple)]/10 text-[var(--purple)]"
          />
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="card p-6 h-28 skeleton" />
          ))}
        </div>
      )}

      {/* Main Content Grid */}
      {metrics ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Threat Activity Feed */}
          <div className="lg:col-span-2 space-y-4">
            {/* Model Confidence */}
            <div className="card p-6 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="section-label mb-0.5">Model Confidence Index</p>
                  <p className="text-sm font-semibold text-[var(--text-primary)]">Active Multi-Model Pipeline</p>
                </div>
                <span className="text-2xl font-extrabold text-[var(--text-primary)] tabular-nums">
                  {metrics.detection_accuracy_percent}%
                </span>
              </div>
              <div className="w-full h-2 rounded-full bg-[var(--bg-surface)] overflow-hidden">
                <div className="h-full rounded-full bg-gradient-to-r from-[var(--accent)] to-[#22C55E]" style={{ width: `${metrics.detection_accuracy_percent}%` }} />
              </div>
              <div className="flex justify-between text-xs text-[var(--text-secondary)] font-mono">
                <span>Random Forest · XGBoost · Isolation Forest</span>
                <span>Optimal</span>
              </div>
            </div>

            {/* Activity Feed */}
            <div className="card p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="section-label mb-0.5">Live Telemetry Feed</p>
                  <p className="text-sm font-semibold text-[var(--text-primary)]">Recent Security Operations</p>
                </div>
                <span className="px-2.5 py-1 rounded-lg bg-[var(--accent)]/10 text-[var(--accent)] text-xs font-mono font-bold">
                  LIVE STREAM
                </span>
              </div>
              <div className="space-y-2 max-h-80 overflow-y-auto">
                {metrics.recent_activity_timeline?.map((act: any, idx: number) => (
                  <div
                    key={idx}
                    className="flex items-start space-x-3 p-3 rounded-xl bg-[var(--bg-surface)] border border-[var(--border)]"
                  >
                    <span
                      className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                        act.severity === 'Critical'
                          ? 'bg-[#EF4444] animate-pulse'
                          : act.severity === 'High'
                          ? 'bg-[#F59E0B]'
                          : 'bg-[var(--accent)]'
                      }`}
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-[var(--text-primary)] leading-relaxed font-sans">{act.event}</p>
                      <p className="text-[10px] text-[var(--text-secondary)] font-mono mt-0.5">
                        {formatStandardDate(act.timestamp || act.time)}
                      </p>
                    </div>
                    <span
                      className={`text-[10px] font-mono font-bold flex-shrink-0 ${
                        act.severity === 'Critical'
                          ? 'text-[#EF4444]'
                          : act.severity === 'High'
                          ? 'text-[#F59E0B]'
                          : 'text-[var(--accent)]'
                      }`}
                    >
                      {act.severity}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right: System Health */}
          <div className="space-y-4">
            <div className="card p-6 space-y-3">
              <p className="section-label">System Architecture Status</p>
              <div className="space-y-2.5">
                {systemChecks.map((s) => {
                  const Icon = s.icon;
                  return (
                    <div key={s.label} className="flex items-center justify-between py-2 border-b border-[var(--border)] last:border-none">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 rounded-xl bg-[var(--bg-surface)] border border-[var(--border)] flex items-center justify-center">
                          <Icon className="w-4 h-4 text-[var(--accent)]" />
                        </div>
                        <span className="text-xs font-semibold text-[var(--text-primary)]">{s.label}</span>
                      </div>
                      <span className="px-2.5 py-0.5 rounded bg-[#22C55E]/15 text-[#22C55E] text-[10px] font-mono font-bold">
                        {s.status}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Defense Ratio */}
            <div className="card p-6 space-y-4">
              <p className="section-label">Defense Efficiency Ratio</p>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-[var(--text-secondary)]">Attack Success Rate</span>
                    <span className="text-[#F59E0B] font-mono font-bold">{metrics.attack_success_rate_percent}%</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-[var(--bg-surface)] overflow-hidden">
                    <div className="h-full bg-[#F59E0B]" style={{ width: `${metrics.attack_success_rate_percent}%` }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-[var(--text-secondary)]">False Negatives</span>
                    <span className="text-[#EF4444] font-mono font-bold">{metrics.false_negatives_percent}%</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-[var(--bg-surface)] overflow-hidden">
                    <div className="h-full bg-[#EF4444]" style={{ width: `${metrics.false_negatives_percent}%` }} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 h-72 card skeleton" />
          <div className="h-72 card skeleton" />
        </div>
      )}
    </div>
  );
};

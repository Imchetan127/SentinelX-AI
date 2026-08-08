import React, { useEffect, useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, Activity, Cpu, Lock, Flame } from 'lucide-react';

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

export const DashboardView: React.FC = () => {
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
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

  if (!metrics) return <div className="p-8 text-cyan-400 font-mono">Loading Security Matrix...</div>;

  return (
    <div className="space-y-6">
      {/* Top Banner Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-cyan-500/20 glow-blue">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase font-mono text-slate-400">Total Telemetry Processed</span>
            <Activity className="w-5 h-5 text-cyan-400" />
          </div>
          <p className="text-3xl font-extrabold text-white mt-2 font-mono">{metrics.total_threats_analyzed.toLocaleString()}</p>
          <span className="text-xs text-cyan-400 mt-1 inline-block">+14.2% from baseline</span>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-rose-500/20 glow-red">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase font-mono text-slate-400">Threats Detected</span>
            <AlertTriangle className="w-5 h-5 text-rose-400" />
          </div>
          <p className="text-3xl font-extrabold text-rose-400 mt-2 font-mono">{metrics.threats_detected.toLocaleString()}</p>
          <span className="text-xs text-rose-400 mt-1 inline-block">34.2% total traffic</span>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-emerald-500/20">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase font-mono text-slate-400">Mitigated / Blocked</span>
            <CheckCircle className="w-5 h-5 text-emerald-400" />
          </div>
          <p className="text-3xl font-extrabold text-emerald-400 mt-2 font-mono">{metrics.threats_blocked.toLocaleString()}</p>
          <span className="text-xs text-emerald-400 mt-1 inline-block">99.34% Mitigation Rate</span>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-purple-500/20 glow-purple">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase font-mono text-slate-400">AI Detection Accuracy</span>
            <Cpu className="w-5 h-5 text-purple-400" />
          </div>
          <p className="text-3xl font-extrabold text-purple-300 mt-2 font-mono">{metrics.detection_accuracy_percent}%</p>
          <span className="text-xs text-purple-400 mt-1 inline-block">False Positives: {metrics.false_positives_percent}%</span>
        </div>
      </div>

      {/* Main Grid: Attack Matrix & Live Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h2 className="text-lg font-bold text-slate-100 flex items-center space-x-2">
            <Flame className="w-5 h-5 text-rose-500" />
            <span>Red Team Simulation vs Blue Team AI Defense Status</span>
          </h2>
          <p className="text-sm text-slate-400">
            Real-time adversary simulation engine continuously injects mock vector threats (SQLi, Phishing, XSS, DDoS, Prompt Injection) to validate Blue Team ML models.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-2">
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-xs text-slate-400 uppercase font-mono">System Health</span>
              <p className="text-lg font-bold text-emerald-400 mt-1 font-mono">{metrics.system_health}</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-xs text-slate-400 uppercase font-mono">Attack Success Rate</span>
              <p className="text-lg font-bold text-amber-400 mt-1 font-mono">{metrics.attack_success_rate_percent}%</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-xs text-slate-400 uppercase font-mono">False Negatives</span>
              <p className="text-lg font-bold text-cyan-400 mt-1 font-mono">{metrics.false_negatives_percent}%</p>
            </div>
          </div>
        </div>

        {/* Timeline Log */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-md font-bold text-slate-200 flex items-center space-x-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            <span>Live Security Audit Log</span>
          </h3>
          <div className="space-y-3 font-mono text-xs">
            {metrics.recent_activity_timeline?.map((act: any, idx: number) => (
              <div key={idx} className="p-3 rounded-lg bg-slate-900/70 border border-slate-800/80 flex flex-col space-y-1">
                <div className="flex items-center justify-between text-slate-400">
                  <span>{act.time}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                    act.severity === 'Critical' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40' :
                    act.severity === 'High' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40' :
                    'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'
                  }`}>
                    {act.severity}
                  </span>
                </div>
                <p className="text-slate-200">{act.event}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

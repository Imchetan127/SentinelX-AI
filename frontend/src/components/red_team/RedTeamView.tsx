import React, { useEffect, useState } from 'react';
import { Flame, Play, Terminal, Code } from 'lucide-react';

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

export const RedTeamView: React.FC = () => {
  const [vectors, setVectors] = useState<any[]>([]);
  const [selectedVector, setSelectedVector] = useState<any>(null);
  const [simulationResult, setSimulationResult] = useState<any>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  useEffect(() => {
    authFetch('/red-team/vectors')
      .then((res) => res.json())
      .then((data) => {
        if (data.vectors && data.vectors.length > 0) {
          setVectors(data.vectors);
          setSelectedVector(data.vectors[0]);
        }
      })
      .catch(() => {});
  }, []);

  const handleSimulate = (vectorId: string) => {
    setIsSimulating(true);
    setSimulationResult(null);
    authFetch(`/red-team/simulate/${vectorId}`, { method: 'POST' })
      .then((res) => res.json())
      .then((data) => {
        setSimulationResult(data);
        setIsSimulating(false);
      })
      .catch(() => {
        setIsSimulating(false);
      });
  };

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl border border-rose-500/30 flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <Flame className="w-6 h-6 text-rose-500 animate-pulse" />
            <span className="gradient-text-red">Red Team Attack Scenario Simulator</span>
          </h2>
          <p className="text-sm text-slate-400">
            Safely execute mock adversarial vectors across Phishing, SQLi, XSS, DDoS, Command Injection, Ransomware, and Prompt Injection.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Vector Selection List */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
          <h3 className="text-xs uppercase font-mono text-slate-400 tracking-wider">Select Attack Scenario</h3>
          <div className="space-y-2">
            {vectors.map((vec) => (
              <div
                key={vec.id}
                onClick={() => setSelectedVector(vec)}
                className={`p-3 rounded-xl cursor-pointer border transition-all duration-150 ${
                  selectedVector?.id === vec.id
                    ? 'bg-rose-500/10 border-rose-500/50 glow-red'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-slate-400">{vec.id}</span>
                  <span className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold ${
                    vec.risk_level === 'Critical' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40' :
                    vec.risk_level === 'High' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40' :
                    'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'
                  }`}>
                    {vec.risk_level}
                  </span>
                </div>
                <h4 className="text-sm font-semibold text-slate-200 mt-1">{vec.name}</h4>
                <p className="text-xs text-slate-400 line-clamp-1 mt-0.5">{vec.category}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Center & Right Column: Vector Details & Terminal Logs */}
        <div className="lg:col-span-2 space-y-6">
          {selectedVector && (
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs font-mono text-rose-400 uppercase tracking-widest">{selectedVector.category}</span>
                  <h3 className="text-lg font-bold text-white mt-1">{selectedVector.name}</h3>
                </div>
                <button
                  onClick={() => handleSimulate(selectedVector.id)}
                  disabled={isSimulating}
                  className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-medium text-sm transition-all glow-red disabled:opacity-50"
                >
                  <Play className="w-4 h-4 fill-current" />
                  <span>{isSimulating ? 'Simulating...' : 'Execute Simulation'}</span>
                </button>
              </div>

              <div className="grid grid-cols-2 gap-4 text-xs font-mono">
                <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                  <span className="text-slate-500">Expected Behavior:</span>
                  <p className="text-slate-300 mt-1">{selectedVector.expected_behaviour}</p>
                </div>
                <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                  <span className="text-slate-500">Estimated Success Probability:</span>
                  <p className="text-rose-400 font-bold mt-1 text-base">{(selectedVector.success_probability * 100).toFixed(0)}%</p>
                </div>
              </div>

              {/* Payload Box */}
              <div className="space-y-1">
                <span className="text-xs font-mono text-slate-400 flex items-center space-x-1">
                  <Code className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Generated Synthetic Payload Preview</span>
                </span>
                <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-cyan-300 overflow-x-auto">
                  {JSON.stringify(selectedVector.payload, null, 2)}
                </pre>
              </div>

              {/* Simulation Result Terminal */}
              {simulationResult && (
                <div className="space-y-2 pt-2">
                  <span className="text-xs font-mono text-emerald-400 flex items-center space-x-1">
                    <Terminal className="w-4 h-4" />
                    <span>Red Team Execution Terminal Output</span>
                  </span>
                  <div className="p-4 rounded-xl bg-slate-950 border border-emerald-500/30 font-mono text-xs text-emerald-400 space-y-1">
                    {simulationResult.logs?.map((log: string, idx: number) => (
                      <div key={idx}>{log}</div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

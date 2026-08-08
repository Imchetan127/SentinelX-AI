import React, { useEffect, useState } from 'react';
import { Flame, Play, Terminal, Code, AlertTriangle, Shield, CheckCircle2 } from 'lucide-react';

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
      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-white/[0.08] flex items-center justify-between">
        <div className="space-y-1">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-[#FF5D73]/10 text-[#FF5D73]">
              <Flame className="w-5 h-5" />
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">Red Team Adversary Simulation Console</h2>
          </div>
          <p className="text-xs text-slate-400">
            Safely execute mock adversarial vectors across Phishing, SQL Injection, Cross-Site Scripting (XSS), Distributed Denial of Service (DDoS), Command Injection, and Prompt Injection playbooks.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Attack Scenario Playbook Selector */}
        <div className="glass-panel p-5 rounded-2xl border border-white/[0.08] space-y-4">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
            <h3 className="text-xs uppercase font-mono text-slate-400 tracking-wider">Attack Playbooks</h3>
            <span className="text-[11px] font-mono text-slate-500">{vectors.length} Scenarios</span>
          </div>

          <div className="space-y-2.5 max-h-[560px] overflow-y-auto pr-1">
            {vectors.map((vec) => {
              const isSelected = selectedVector?.id === vec.id;
              return (
                <div
                  key={vec.id}
                  onClick={() => setSelectedVector(vec)}
                  className={`p-3.5 rounded-xl cursor-pointer border transition-all duration-150 ${
                    isSelected
                      ? 'bg-[#111827] border-[#FF5D73]/50 shadow-md'
                      : 'bg-[#111827]/60 border-white/[0.06] hover:border-white/[0.14]'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-400 font-semibold">{vec.id}</span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold uppercase ${
                        vec.risk_level === 'Critical'
                          ? 'bg-[#FF5D73]/15 text-[#FF5D73] border border-[#FF5D73]/30'
                          : vec.risk_level === 'High'
                          ? 'bg-[#FFB547]/15 text-[#FFB547] border border-[#FFB547]/30'
                          : 'bg-[#00D4FF]/15 text-[#00D4FF] border border-[#00D4FF]/30'
                      }`}
                    >
                      {vec.risk_level}
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-white mt-1.5 font-sans">{vec.name}</h4>
                  <p className="text-xs text-slate-400 line-clamp-1 mt-0.5 font-mono text-[11px]">{vec.category}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Center & Right Column: Playbook Execution Workspace */}
        <div className="lg:col-span-2 space-y-6">
          {selectedVector && (
            <div className="glass-panel p-6 rounded-2xl border border-white/[0.08] space-y-5">
              {/* Playbook Header & Execute Action */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/[0.08] pb-4">
                <div>
                  <span className="text-xs font-mono text-[#FF5D73] uppercase tracking-wider font-semibold">
                    {selectedVector.category}
                  </span>
                  <h3 className="text-lg font-bold text-white mt-0.5">{selectedVector.name}</h3>
                </div>

                <button
                  onClick={() => handleSimulate(selectedVector.id)}
                  disabled={isSimulating}
                  className="flex items-center justify-center space-x-2 px-6 py-3 rounded-xl bg-[#FF5D73] hover:bg-[#FF5D73]/90 text-white font-bold text-xs font-mono transition-all shadow-lg disabled:opacity-50"
                >
                  <Play className="w-4 h-4 fill-current" />
                  <span>{isSimulating ? 'SIMULATING ATTACK...' : 'EXECUTE PLAYBOOK'}</span>
                </button>
              </div>

              {/* Behavior & Probability Summary Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
                <div className="p-4 rounded-xl bg-[#111827] border border-white/[0.08] space-y-1">
                  <span className="text-slate-400 uppercase text-[10px]">Expected Behavior:</span>
                  <p className="text-slate-200 font-sans text-xs mt-1 leading-relaxed">{selectedVector.expected_behaviour}</p>
                </div>
                <div className="p-4 rounded-xl bg-[#111827] border border-white/[0.08] space-y-1">
                  <span className="text-slate-400 uppercase text-[10px]">Adversary Success Probability:</span>
                  <p className="text-2xl font-bold text-[#FF5D73] font-mono mt-1">
                    {(selectedVector.success_probability * 100).toFixed(0)}%
                  </p>
                </div>
              </div>

              {/* Synthetic Payload Code Block */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-400 flex items-center space-x-1">
                    <Code className="w-3.5 h-3.5 text-[#00D4FF]" />
                    <span>Generated Payload Artifact</span>
                  </span>
                  <span className="text-[10px] text-slate-500">SYNTHETIC ADVERSARY ARTIFACT</span>
                </div>
                <pre className="p-4 rounded-xl bg-[#090B10] border border-white/[0.08] text-xs font-mono text-[#00D4FF] overflow-x-auto leading-relaxed">
                  {JSON.stringify(selectedVector.payload, null, 2)}
                </pre>
              </div>

              {/* Execution Log Terminal Output */}
              {simulationResult && (
                <div className="space-y-2 pt-2 border-t border-white/[0.08]">
                  <div className="flex items-center justify-between text-xs font-mono text-[#2EE59D]">
                    <span className="flex items-center space-x-1.5">
                      <Terminal className="w-4 h-4" />
                      <span className="font-bold">Red Team Terminal Execution Stream</span>
                    </span>
                    <span className="text-[10px] text-[#2EE59D] font-bold">STATUS: COMPLETED</span>
                  </div>

                  <div className="p-4 rounded-xl bg-[#090B10] border border-[#2EE59D]/30 font-mono text-xs text-[#2EE59D] space-y-1.5 max-h-[220px] overflow-y-auto">
                    {simulationResult.logs?.map((log: string, idx: number) => (
                      <div key={idx} className="leading-relaxed">{log}</div>
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

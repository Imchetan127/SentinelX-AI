'use client';

import React, { useEffect, useState } from 'react';
import { Flame, Play, Code, Terminal, Zap, CheckCircle2, ShieldAlert, ArrowRight, ShieldCheck } from 'lucide-react';
import { motion } from 'framer-motion';
import { formatStandardDate } from '@/utils/dateFormatter';

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

interface RedTeamViewProps {
  onNavigateToAttack?: (attackId: string, targetTab?: string) => void;
}

export const RedTeamView: React.FC<RedTeamViewProps> = ({ onNavigateToAttack }) => {
  const [vectors, setVectors] = useState<any[]>([]);
  const [selectedVector, setSelectedVector] = useState<any>(null);
  const [simulationResult, setSimulationResult] = useState<any>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [visibleLogs, setVisibleLogs] = useState<string[]>([]);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    authFetch('/red-team/vectors')
      .then(r => r.json())
      .then(data => {
        if (data.vectors?.length > 0) {
          setVectors(data.vectors);
          setSelectedVector(data.vectors[0]);
        }
      })
      .catch(() => {});
  }, []);

  const handleSimulate = (vectorId: string) => {
    setIsSimulating(true);
    setSimulationResult(null);
    setVisibleLogs([]);
    setProgress(15);

    const progressInterval = setInterval(() => {
      setProgress(prev => (prev < 90 ? prev + 25 : prev));
    }, 200);

    authFetch(`/red-team/simulate/${vectorId}`, { method: 'POST' })
      .then(r => r.json())
      .then(data => {
        clearInterval(progressInterval);
        setProgress(100);
        setSimulationResult(data);
        setIsSimulating(false);

        // Stream terminal logs line by line for live feel
        if (data.logs && Array.isArray(data.logs)) {
          data.logs.forEach((logLine: string, idx: number) => {
            setTimeout(() => {
              setVisibleLogs(prev => [...prev, logLine]);
            }, idx * 180);
          });
        }
      })
      .catch(() => {
        clearInterval(progressInterval);
        setIsSimulating(false);
      });
  };

  const riskColor = (level: string) => {
    if (level === 'Critical') return 'text-[#EF4444] bg-[#EF4444]/10 border-[#EF4444]/30';
    if (level === 'High') return 'text-[#F59E0B] bg-[#F59E0B]/10 border-[#F59E0B]/30';
    return 'text-[#00D4FF] bg-[#00D4FF]/10 border-[#00D4FF]/30';
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-[#EF4444] animate-pulse" />
            <p className="section-label text-[#EF4444]">RED TEAM SIMULATION WORKSPACE</p>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight mt-1">Attack Simulation Center</h2>
          <p className="text-sm text-slate-400 mt-1">
            Safe in-memory execution of adversarial playbooks across 15+ attack vectors.
          </p>
        </div>
        <span className="px-3 py-1 rounded-lg text-xs font-mono font-bold bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/25">
          OFFENSIVE SIMULATION ACTIVE
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Playbook Selector */}
        <div className="card p-0 overflow-hidden border-[#EF4444]/20">
          <div className="px-5 py-4 border-b border-white/[0.06] bg-[#121826]/80 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Flame className="w-4 h-4 text-[#EF4444]" />
              <p className="text-sm font-semibold text-white">Attack Playbooks</p>
            </div>
            <span className="text-xs text-slate-500 font-mono">{vectors.length} scenarios</span>
          </div>
          <div className="overflow-y-auto max-h-[560px]">
            {vectors.map((vec) => {
              const isSelected = selectedVector?.id === vec.id;
              return (
                <button
                  key={vec.id}
                  onClick={() => { setSelectedVector(vec); setSimulationResult(null); setVisibleLogs([]); }}
                  className={`w-full text-left px-5 py-4 border-b border-white/[0.04] transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-[#EF4444]/08 border-l-4 border-l-[#EF4444] text-white'
                      : 'hover:bg-white/[0.02] text-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[11px] font-mono text-slate-400">{vec.category}</span>
                    <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${riskColor(vec.risk_level)}`}>
                      {vec.risk_level}
                    </span>
                  </div>
                  <p className={`text-sm font-medium ${isSelected ? 'text-white' : 'text-slate-300'}`}>
                    {vec.name}
                  </p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Execution Workspace */}
        <div className="lg:col-span-2 space-y-5">
          {selectedVector && (
            <motion.div
              key={selectedVector.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25 }}
              className="card p-6 space-y-5 border-[#EF4444]/20"
            >
              {/* Header & Execute Button */}
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs font-mono font-bold text-[#EF4444] uppercase tracking-wider">{selectedVector.category}</span>
                  <h3 className="text-xl font-bold text-white mt-1">{selectedVector.name}</h3>
                </div>
                <motion.button
                  onClick={() => handleSimulate(selectedVector.id)}
                  disabled={isSimulating}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex items-center space-x-2 px-6 py-2.5 rounded-xl font-semibold text-xs text-white bg-[#EF4444] hover:bg-[#DC2626] shadow-lg shadow-[#EF4444]/20 disabled:opacity-50 transition-all cursor-pointer"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>{isSimulating ? 'Simulating Attack...' : 'Execute Playbook'}</span>
                </motion.button>
              </div>

              {/* Progress bar when simulating */}
              {isSimulating && (
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs font-mono text-slate-400">
                    <span>Deploying simulation payload & running event pipeline...</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-[#1A2236] overflow-hidden">
                    <motion.div
                      className="h-full bg-[#EF4444]"
                      initial={{ width: '0%' }}
                      animate={{ width: `${progress}%` }}
                      transition={{ duration: 0.2 }}
                    />
                  </div>
                </div>
              )}

              {/* Real Pipeline Correlation Banner */}
              {simulationResult && (
                <motion.div
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-4 rounded-xl bg-[#00D4FF]/08 border border-[#00D4FF]/30 space-y-3 font-mono text-xs"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <ShieldCheck className="w-4 h-4 text-[#00D4FF]" />
                      <span className="text-white font-bold uppercase">EVENT PIPELINE COMPLETE — SHARED CORRELATION ID</span>
                    </div>
                    <span className="px-2 py-0.5 rounded bg-[#22C55E]/15 border border-[#22C55E]/30 text-[#22C55E] font-bold text-[10px]">
                      AUTO DETECTED & MITIGATED
                    </span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-[11px] text-slate-300">
                    <div>
                      <span className="text-slate-500 block">ATTACK ID:</span>
                      <span className="text-[#00D4FF] font-bold truncate block">{simulationResult.attack_id}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">DETECTION ID:</span>
                      <span className="text-white font-bold truncate block">{simulationResult.pipeline?.detection_id || 'Completed'}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">INCIDENT ID:</span>
                      <span className="text-[#EF4444] font-bold truncate block">{simulationResult.pipeline?.incident_id || 'None'}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">CONSENSUS SCORE:</span>
                      <span className="text-[#F59E0B] font-bold block">{simulationResult.pipeline?.consensus_threat_score}/100</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">ACTION TAKEN:</span>
                      <span className="text-[#22C55E] font-bold block">{simulationResult.pipeline?.action_taken}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">RISK LEVEL:</span>
                      <span className="text-white font-bold block">{simulationResult.pipeline?.risk_level}</span>
                    </div>
                  </div>
                  {onNavigateToAttack && simulationResult.attack_id && (
                    <button
                      onClick={() => onNavigateToAttack(simulationResult.attack_id, 'blue-team')}
                      className="w-full py-2 rounded-lg bg-[#00D4FF]/15 hover:bg-[#00D4FF]/25 border border-[#00D4FF]/40 text-[#00D4FF] font-bold flex items-center justify-center space-x-2 transition-all cursor-pointer mt-2"
                    >
                      <span>Investigate in Blue Team Defense Center</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  )}
                </motion.div>
              )}

              {/* Stats Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-[#1A2236] rounded-xl p-4 border border-white/[0.04] space-y-1">
                  <p className="text-[11px] font-mono text-slate-400">EXPECTED ADVERSARY BEHAVIOR</p>
                  <p className="text-xs text-slate-300 leading-relaxed">{selectedVector.expected_behaviour}</p>
                </div>
                <div className="bg-[#1A2236] rounded-xl p-4 border border-white/[0.04] flex items-center justify-between">
                  <div>
                    <p className="text-[11px] font-mono text-slate-400 uppercase">SCENARIO HISTORICAL DIFFICULTY</p>
                    <p className="text-3xl font-extrabold text-[#EF4444] tabular-nums mt-1">
                      {(selectedVector.success_probability * 100).toFixed(0)}%
                    </p>
                    <p className="text-[10px] font-mono text-slate-500 mt-0.5">Static Red Team scenario metadata</p>
                  </div>
                  <div className="w-10 h-10 rounded-xl bg-[#EF4444]/10 border border-[#EF4444]/20 flex items-center justify-center">
                    <Zap className="w-5 h-5 text-[#EF4444]" />
                  </div>
                </div>
              </div>

              {/* Payload Code Box */}
              <div>
                <div className="flex items-center space-x-2 mb-2">
                  <Code className="w-3.5 h-3.5 text-[#EF4444]" />
                  <span className="text-xs font-mono text-slate-400">SYNTHETIC PAYLOAD CONTENT</span>
                </div>
                <pre className="bg-[#080C14] border border-[#EF4444]/20 rounded-xl p-4 text-xs font-mono text-[#EF4444] overflow-x-auto leading-relaxed shadow-inner">
                  {JSON.stringify(selectedVector.payload, null, 2)}
                </pre>
              </div>

              {/* Execution Log Terminal */}
              {simulationResult && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="border-t border-white/[0.06] pt-5 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Terminal className="w-4 h-4 text-[#22C55E]" />
                      <span className="text-xs font-mono font-bold text-white">SIMULATION TERMINAL OUTPUT</span>
                      <span className="text-[11px] font-mono text-slate-500 ml-2">
                        • {formatStandardDate(simulationResult.timestamp || new Date())}
                      </span>
                    </div>
                    <span className="px-2.5 py-0.5 rounded bg-[#22C55E]/15 border border-[#22C55E]/30 text-[#22C55E] text-[10px] font-mono font-bold">
                      EXECUTION COMPLETED
                    </span>
                  </div>
                  <div className="bg-[#080C14] border border-white/[0.06] rounded-xl p-4 font-mono text-xs text-[#22C55E] space-y-1.5 max-h-56 overflow-y-auto leading-relaxed">
                    {visibleLogs.map((log: string, idx: number) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: -6 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.15 }}
                        className={log.includes('CRITICAL') || log.includes('HIGH') ? 'text-[#EF4444] font-bold' : ''}
                      >
                        {log}
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

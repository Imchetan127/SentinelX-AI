'use client';

import React, { useEffect, useState } from 'react';
import { Shield, Search, CheckCircle2, Cpu, AlertTriangle, Lock, ShieldCheck, Activity, Terminal, ArrowRight, Layers, FileText, Info } from 'lucide-react';
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

interface BlueTeamViewProps {
  attackId?: string | null;
  onNavigateToExplainability?: (attackId: string) => void;
}

export const BlueTeamView: React.FC<BlueTeamViewProps> = ({ attackId, onNavigateToExplainability }) => {
  const [activeSubTab, setActiveSubTab] = useState<'live' | 'manual'>('live');

  // Live SOC Feed State
  const [attacksList, setAttacksList] = useState<any[]>([]);
  const [selectedAttackId, setSelectedAttackId] = useState<string | null>(attackId || null);
  const [liveDetection, setLiveDetection] = useState<any>(null);
  const [liveStatus, setLiveStatus] = useState<any>(null);
  const [liveTimeline, setLiveTimeline] = useState<any[]>([]);
  const [isLoadingFeed, setIsLoadingFeed] = useState(true);
  const [feedError, setFeedError] = useState<string | null>(null);

  // Manual Inspector State (Secondary Tab)
  const [inputText, setInputText] = useState("admin' OR '1'='1 --");
  const [artifactType, setArtifactType] = useState('SQL Injection Payload');
  const [manualResult, setManualResult] = useState<any>(null);
  const [isAnalyzingManual, setIsAnalyzingManual] = useState(false);

  // 1. Fetch attacks list on mount
  useEffect(() => {
    setIsLoadingFeed(true);
    authFetch('/attacks')
      .then(r => r.json())
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          setAttacksList(data);
          // Default to passed attackId or first attack in list
          const targetId = attackId && data.some(a => a.id === attackId) ? attackId : data[0].id;
          setSelectedAttackId(targetId);
        } else {
          setAttacksList([]);
        }
        setIsLoadingFeed(false);
      })
      .catch(() => {
        setFeedError('Detection Engine Offline or Backend Unreachable');
        setIsLoadingFeed(false);
      });
  }, [attackId]);

  // 2. Fetch specific attack details whenever selectedAttackId changes
  useEffect(() => {
    if (!selectedAttackId) return;

    // Fetch detection
    authFetch(`/attacks/${selectedAttackId}/detection`)
      .then(r => r.json())
      .then(data => {
        if (data.success && data.data) {
          setLiveDetection(data.data);
        } else {
          setLiveDetection(null);
        }
      })
      .catch(() => setLiveDetection(null));

    // Fetch status
    authFetch(`/attacks/${selectedAttackId}/status`)
      .then(r => r.json())
      .then(setLiveStatus)
      .catch(() => setLiveStatus(null));

    // Fetch timeline
    authFetch(`/attacks/${selectedAttackId}/timeline`)
      .then(r => r.json())
      .then(data => {
        if (data.success && Array.isArray(data.events)) {
          setLiveTimeline(data.events);
        } else {
          setLiveTimeline([]);
        }
      })
      .catch(() => setLiveTimeline([]));
  }, [selectedAttackId]);

  const handleInspectManual = () => {
    setIsAnalyzingManual(true);
    authFetch('/blue-team/inspect-text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: inputText, artifact_type: artifactType }),
    })
      .then(r => r.json())
      .then(data => { setManualResult(data); setIsAnalyzingManual(false); })
      .catch(() => setIsAnalyzingManual(false));
  };

  const selectedAttackObj = attacksList.find(a => a.id === selectedAttackId);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-[#00D4FF] animate-pulse" />
            <p className="section-label text-[#00D4FF]">BLUE TEAM DEFENSE ENGINE</p>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight mt-1">Defense & Threat Investigation Center</h2>
          <p className="text-sm text-slate-400 mt-1">
            Real-time payload inspection, multi-model consensus scoring, and automated WAF mitigation.
          </p>
        </div>
        {/* Tab Switcher */}
        <div className="flex items-center p-1 bg-[#121826] border border-white/[0.08] rounded-xl font-mono text-xs">
          <button
            onClick={() => setActiveSubTab('live')}
            className={`px-4 py-1.5 rounded-lg font-bold transition-all cursor-pointer ${
              activeSubTab === 'live'
                ? 'bg-[#00D4FF] text-black shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Live Threat Feed ({attacksList.length})
          </button>
          <button
            onClick={() => setActiveSubTab('manual')}
            className={`px-4 py-1.5 rounded-lg font-bold transition-all cursor-pointer ${
              activeSubTab === 'manual'
                ? 'bg-[#00D4FF] text-black shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Ad-Hoc Manual Inspector
          </button>
        </div>
      </div>

      {/* ERROR / OFFLINE STATE */}
      {feedError && (
        <div className="p-4 rounded-xl bg-[#EF4444]/10 border border-[#EF4444]/30 text-xs font-mono text-[#EF4444] flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4" />
            <span>Detection Engine Offline: Backend API unreachable at http://localhost:8000</span>
          </div>
          <span className="font-bold">STATUS: OFFLINE</span>
        </div>
      )}

      {/* ----------------------------------------------------------------- */}
      {/* SUB-TAB 1: LIVE SOC THREAT STREAM (PRIMARY VIEW)                  */}
      {/* ----------------------------------------------------------------- */}
      {activeSubTab === 'live' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Attack Stream Selector Column */}
          <div className="card p-0 overflow-hidden border-[#00D4FF]/20">
            <div className="px-5 py-4 border-b border-white/[0.06] bg-[#121826]/80 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4 text-[#00D4FF]" />
                <p className="text-sm font-semibold text-white">Live Adversary Attacks</p>
              </div>
              <span className="text-xs text-slate-500 font-mono">{attacksList.length} events</span>
            </div>

            {isLoadingFeed ? (
              <div className="p-8 text-center text-xs font-mono text-slate-500 space-y-2">
                <div className="w-6 h-6 border-2 border-[#00D4FF]/30 border-t-[#00D4FF] rounded-full animate-spin mx-auto" />
                <p>Loading real telemetry from PostgreSQL...</p>
              </div>
            ) : attacksList.length === 0 ? (
              <div className="p-8 text-center text-xs font-mono text-slate-500 space-y-2">
                <Shield className="w-8 h-8 mx-auto text-slate-600" />
                <p>No attacks simulated yet.</p>
                <p className="text-[11px] text-slate-600">Run an offensive playbook in Red Team Center to generate live events.</p>
              </div>
            ) : (
              <div className="overflow-y-auto max-h-[580px]">
                {attacksList.map((atk) => {
                  const isSelected = selectedAttackId === atk.id;
                  return (
                    <button
                      key={atk.id}
                      onClick={() => setSelectedAttackId(atk.id)}
                      className={`w-full text-left px-5 py-4 border-b border-white/[0.04] transition-all cursor-pointer ${
                        isSelected
                          ? 'bg-[#00D4FF]/08 border-l-4 border-l-[#00D4FF] text-white'
                          : 'hover:bg-white/[0.02] text-slate-300'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] font-mono text-slate-400 truncate max-w-[160px]">{atk.id}</span>
                        <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${
                          atk.severity === 'CRITICAL' || atk.severity === 'HIGH'
                            ? 'text-[#EF4444] bg-[#EF4444]/10 border-[#EF4444]/30'
                            : 'text-[#F59E0B] bg-[#F59E0B]/10 border-[#F59E0B]/30'
                        }`}>
                          {atk.severity}
                        </span>
                      </div>
                      <p className={`text-xs font-bold ${isSelected ? 'text-white' : 'text-slate-300'}`}>
                        {atk.attack_type}
                      </p>
                      <p className="text-[10px] font-mono text-slate-500 mt-1">
                        {formatStandardDate(atk.created_at || new Date())}
                      </p>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Selected Attack Investigation Panel */}
          <div className="lg:col-span-2 space-y-5">
            {selectedAttackObj ? (
              <div className="space-y-5">
                {/* 1. Root Attack Telemetry Card */}
                <div className="card p-5 border-[#00D4FF]/20 space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-[10px] font-mono font-bold text-[#00D4FF] uppercase">ROOT CORRELATION TELEMETRY</span>
                      <h3 className="text-lg font-bold text-white mt-0.5">{selectedAttackObj.attack_type}</h3>
                      <span className="text-xs font-mono text-slate-400 block mt-0.5">ID: {selectedAttackObj.id}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] font-mono text-slate-400 block">PIPELINE STATUS</span>
                      <span className="px-2.5 py-1 rounded bg-[#22C55E]/15 border border-[#22C55E]/30 text-[#22C55E] text-xs font-mono font-bold">
                        {liveStatus?.detection_status?.toUpperCase() || 'COMPLETED'}
                      </span>
                    </div>
                  </div>

                  {/* Raw Payload Display */}
                  <div className="bg-[#080C14] rounded-xl p-3.5 border border-white/[0.06] font-mono text-xs text-[#00D4FF]">
                    <span className="text-[10px] text-slate-500 block mb-1">INSPECTED PAYLOAD STRING:</span>
                    <p className="break-all">{selectedAttackObj.payload}</p>
                  </div>
                </div>

                {/* 2. Multi-Model Predictions & Consensus Card */}
                {liveDetection ? (
                  <div className="card p-6 space-y-5 border-[#00D4FF]/20">
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-[10px] font-mono font-bold text-[#00D4FF] uppercase">MULTI-MODEL ENSEMBLE CONSENSUS</span>
                        <h3 className="text-base font-bold text-white mt-0.5">Live Model Classification Matrix</h3>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={async () => {
                            if (!selectedAttackId) return;
                            try {
                              const res = await authFetch(`/reports/incidents/${selectedAttackId}`, { method: 'POST' });
                              const data = await res.json();
                              if (res.ok && data.success) {
                                alert(`Report Generated Successfully!\nReport Title: ${data.data.title}\nSHA-256 Digest: ${data.data.sha256_hash}`);
                              } else {
                                alert(`Report Generation Notice: ${data.message || 'Unable to compile report for this event.'}`);
                              }
                            } catch (e: any) {
                              alert(`Report Generation Notice: ${e.message || 'Server error generating PDF report.'}`);
                            }
                          }}
                          className="px-3 py-1.5 rounded-lg bg-[#00D4FF]/15 hover:bg-[#00D4FF]/25 border border-[#00D4FF]/40 text-[#00D4FF] text-xs font-mono font-bold flex items-center space-x-1.5 transition-all cursor-pointer"
                        >
                          <FileText className="w-3.5 h-3.5" />
                          <span>Generate Report</span>
                        </button>
                        {onNavigateToExplainability && (
                          <button
                            onClick={() => onNavigateToExplainability(selectedAttackId!)}
                            className="px-3 py-1.5 rounded-lg bg-[#A78BFA]/15 hover:bg-[#A78BFA]/25 border border-[#A78BFA]/40 text-[#A78BFA] text-xs font-mono font-bold flex items-center space-x-1.5 transition-all cursor-pointer"
                          >
                            <span>SHAP Matrix</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Model Predictions Grid */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      {liveDetection.predictions?.map((pred: any, idx: number) => {
                        const modelTitle = pred.model_name || (pred.algorithm ? pred.algorithm.replace('_', ' ').toUpperCase() : `MODEL ENGINE #${idx + 1}`);
                        const isUnavailable = pred.prediction === 'unavailable' || pred.status === 'unavailable';
                        const confidencePct = pred.confidence != null ? (pred.confidence * 100).toFixed(1) : 'N/A';

                        return (
                          <div key={idx} className="p-4 rounded-xl bg-[#1A2236] border border-white/[0.06] space-y-2 font-mono">
                            <div className="flex items-center justify-between">
                              <span className="text-[11px] font-bold text-white uppercase truncate max-w-[140px]">{modelTitle}</span>
                              <span className={`text-[9px] font-bold px-2 py-0.5 rounded ${
                                isUnavailable
                                  ? 'text-slate-400 bg-slate-800 border border-slate-700'
                                  : pred.prediction === 'malicious'
                                  ? 'text-[#EF4444] bg-[#EF4444]/15 border border-[#EF4444]/30'
                                  : 'text-[#22C55E] bg-[#22C55E]/15 border border-[#22C55E]/30'
                              }`}>
                                {isUnavailable ? 'UNAVAILABLE' : pred.prediction.toUpperCase()}
                              </span>
                            </div>
                            <div className="flex items-center justify-between text-xs">
                              <span className="text-slate-400">{isUnavailable ? 'Status:' : 'Confidence:'}</span>
                              <span className="text-white font-bold text-[11px]">{isUnavailable ? 'Offline' : `${confidencePct}%`}</span>
                            </div>
                            <div className="w-full h-1.5 rounded-full bg-[#080C14] overflow-hidden">
                              <div
                                className={`h-full ${isUnavailable ? 'bg-slate-600' : pred.prediction === 'malicious' ? 'bg-[#EF4444]' : 'bg-[#22C55E]'}`}
                                style={{ width: isUnavailable ? '100%' : `${(pred.confidence || 0) * 100}%` }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    {/* Confidence Metric Clarification Subtext */}
                    <div className="p-3 rounded-lg bg-[#080C14] border border-white/[0.06] text-[11px] text-slate-400 font-mono flex items-start space-x-2">
                      <Info className="w-4 h-4 text-[#00D4FF] flex-shrink-0 mt-0.5" />
                      <span>
                        <strong className="text-white">Confidence Label Note:</strong> Confidence reflects model recognition of this specific simulated attack pattern. See <span className="text-[#00D4FF]">ML Benchmarks</span> for generalization accuracy on novel, unseen attacks (~65-75%).
                      </span>
                    </div>

                    {/* WAF Response Rule Applied */}
                    {liveDetection.mitigation && (
                      <div className="p-4 rounded-xl bg-[#22C55E]/08 border border-[#22C55E]/25 space-y-2 font-mono text-xs">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2 text-[#22C55E] font-bold">
                            <ShieldCheck className="w-4 h-4" />
                            <span>AUTOMATED WAF DEFENSE RULE</span>
                          </div>
                          <span className="px-2 py-0.5 rounded bg-[#22C55E]/20 text-[#22C55E] font-bold text-[10px]">
                            {liveDetection.mitigation.status}
                          </span>
                        </div>
                        <p className="text-slate-300">{liveDetection.mitigation.rule_applied}</p>
                      </div>
                    )}

                    {/* Timeline Event Stream */}
                    {liveTimeline.length > 0 && (
                      <div className="space-y-2 pt-3 border-t border-white/[0.06]">
                        <div className="flex items-center space-x-2 text-xs font-mono font-bold text-slate-400">
                          <Terminal className="w-4 h-4 text-[#00D4FF]" />
                          <span>EVENT PIPELINE CHRONOLOGICAL TIMELINE</span>
                        </div>
                        <div className="space-y-1.5 font-mono text-xs">
                          {liveTimeline.map((evt) => (
                            <div key={evt.id} className="p-3 rounded-lg bg-[#080C14] border border-white/[0.04] flex items-start justify-between">
                              <div className="space-y-0.5">
                                <div className="flex items-center space-x-2">
                                  <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-white/[0.08] text-[#00D4FF]">
                                    {evt.stage}
                                  </span>
                                  <span className="font-bold text-white">{evt.title}</span>
                                </div>
                                {evt.details && <p className="text-slate-400 text-[11px] mt-1">{evt.details}</p>}
                              </div>
                              <span className="text-[10px] text-slate-500 whitespace-nowrap ml-4">
                                {formatStandardDate(evt.timestamp)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="card p-8 text-center text-xs font-mono text-slate-500">
                    <p>No live detection pipeline executed for this attack record yet.</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="card p-12 text-center text-xs font-mono text-slate-500 space-y-3">
                <Cpu className="w-10 h-10 text-[#00D4FF] mx-auto animate-pulse" />
                <p>Select an attack event from the left stream to inspect live predictions & multi-model consensus.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ----------------------------------------------------------------- */}
      {/* SUB-TAB 2: AD-HOC MANUAL PAYLOAD SANDBOX (SECONDARY TOOL)          */}
      {/* ----------------------------------------------------------------- */}
      {activeSubTab === 'manual' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card p-6 space-y-5 border-[#00D4FF]/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Shield className="w-4 h-4 text-[#00D4FF]" />
                <p className="text-sm font-semibold text-white">Ad-Hoc Manual Payload Sandbox</p>
              </div>
              <select
                value={artifactType}
                onChange={e => setArtifactType(e.target.value)}
                className="input-field w-auto text-xs py-1.5 px-3 bg-[#1A2236] border border-white/[0.08]"
              >
                <option value="SQL Injection Payload">SQL Injection</option>
                <option value="Phishing Email Body">Phishing Email</option>
                <option value="XSS Script Vector">XSS Script</option>
                <option value="LLM Prompt Vector">LLM Prompt</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="section-label">Raw Payload / Test Telemetry:</label>
              <textarea
                value={inputText}
                onChange={e => setInputText(e.target.value)}
                rows={9}
                className="input-field resize-none font-mono text-xs leading-relaxed bg-[#080C14] border border-[#00D4FF]/20 text-[#00D4FF]"
                placeholder="Paste raw telemetry or payload here for analyst testing..."
              />
            </div>

            <button
              onClick={handleInspectManual}
              disabled={isAnalyzingManual}
              className="btn-primary w-full justify-center disabled:opacity-50 text-xs py-3 cursor-pointer"
            >
              <Search className="w-4 h-4" />
              <span>{isAnalyzingManual ? 'Analyzing Test Payload...' : 'Execute Ad-Hoc Payload Inspection'}</span>
            </button>
          </div>

          <div className="card p-6 space-y-5 border-[#00D4FF]/20">
            <p className="text-sm font-semibold text-white">Manual Threat Inspection Scorecard</p>
            {manualResult ? (
              <div className="space-y-5 font-mono text-xs">
                <div className={`p-4 rounded-xl border flex items-center justify-between ${
                  manualResult.threat_detected ? 'bg-[#EF4444]/08 border-[#EF4444]/30 text-[#EF4444]' : 'bg-[#22C55E]/08 border-[#22C55E]/30 text-[#22C55E]'
                }`}>
                  <div>
                    <span className="font-bold block uppercase">{manualResult.threat_detected ? 'THREAT DETECTED' : 'SAFE PAYLOAD'}</span>
                    <span className="text-white text-sm font-bold block mt-0.5">{manualResult.threat_category}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-slate-400 block text-[10px]">RISK SCORE</span>
                    <span className="text-xl font-bold text-white">{(manualResult.threat_score * 100).toFixed(0)}/100</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <span className="text-slate-400 font-bold block">MODEL PREDICTIONS (ACTUAL INFERENCE):</span>
                  {manualResult.models?.map((m: any, idx: number) => (
                    <div key={idx} className="p-3 rounded-lg bg-[#1A2236] border border-white/[0.04] flex items-center justify-between">
                      <span className="text-slate-300 uppercase">{m.algorithm || `MODEL #${idx + 1}`}</span>
                      <span className="text-white font-bold">{m.status === 'unavailable' ? 'Unavailable' : `${(m.confidence * 100).toFixed(1)}% ${m.prediction}`}</span>
                    </div>
                  )) || (
                    <div className="p-3 rounded-lg bg-[#1A2236] border border-white/[0.04] text-slate-400">
                      Rule Engine Score: {(manualResult.threat_score * 100).toFixed(0)}% Malicious
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-64 text-slate-500 space-y-3 font-mono text-xs">
                <Cpu className="w-8 h-8 text-[#00D4FF] animate-pulse" />
                <p>Submit a payload to run ad-hoc analysis.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

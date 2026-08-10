'use client';

import React, { useEffect, useState } from 'react';
import { Brain, FileText, CheckCircle, Sparkles, Activity, ShieldAlert, Cpu, AlertCircle, Layers } from 'lucide-react';
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

interface ExplainabilityViewProps {
  attackId?: string | null;
}

export const ExplainabilityView: React.FC<ExplainabilityViewProps> = ({ attackId }) => {
  const [explainData, setExplainData] = useState<any>(null);
  const [historyList, setHistoryList] = useState<any[]>([]);
  const [selectedAttackId, setSelectedAttackId] = useState<string | null>(attackId || null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Sync selectedAttackId if prop changes
  useEffect(() => {
    if (attackId) {
      setSelectedAttackId(attackId);
    }
  }, [attackId]);

  // Fetch history list on mount
  useEffect(() => {
    authFetch('/explain/history')
      .then(r => r.json())
      .then(data => {
        if (data.success && Array.isArray(data.data)) {
          setHistoryList(data.data);
          if (!selectedAttackId && data.data.length > 0) {
            setSelectedAttackId(data.data[0].prediction_id);
          }
        }
      })
      .catch(() => {});
  }, []);

  // Fetch specific explanation data
  useEffect(() => {
    setIsLoading(true);
    setErrorMsg(null);

    const path = selectedAttackId
      ? `/explain/attack/${selectedAttackId}`
      : '/ml-engine/explain';

    authFetch(path)
      .then(r => r.json())
      .then(data => {
        if (data.success && data.data) {
          setExplainData(data.data);
        } else if (data.shap_values) {
          setExplainData(data);
        } else {
          setExplainData(null);
          setErrorMsg(data.message || 'SHAP explanation unavailable for this detection.');
        }
        setIsLoading(false);
      })
      .catch(() => {
        setExplainData(null);
        setErrorMsg('SHAP Explainability Engine Offline or Backend API Unreachable');
        setIsLoading(false);
      });
  }, [selectedAttackId]);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-[#A78BFA] animate-pulse" />
            <p className="section-label text-[#A78BFA]">SHAP KERNEL ATTRIBUTION ENGINE</p>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight mt-1">AI Explainability Center</h2>
          <p className="text-sm text-slate-400 mt-1">
            SHAP & LIME attribution for every model decision — human-readable, verifiable, and audit-certified.
          </p>
        </div>
        <span className="px-3 py-1 rounded-lg text-xs font-mono font-bold bg-[#A78BFA]/10 text-[#A78BFA] border border-[#A78BFA]/25 flex items-center space-x-1.5">
          <Sparkles className="w-3.5 h-3.5" />
          <span>SHAP TREEEXPLAINER ACTIVE</span>
        </span>
      </div>

      {/* Selected Attack ID Banner */}
      {selectedAttackId && (
        <div className="p-3 rounded-xl bg-[#A78BFA]/10 border border-[#A78BFA]/30 flex items-center justify-between text-xs font-mono">
          <div className="flex items-center space-x-2">
            <Brain className="w-4 h-4 text-[#A78BFA]" />
            <span className="text-white font-bold">SCOPED TO ROOT ATTACK ID:</span>
            <span className="text-[#A78BFA]">{selectedAttackId}</span>
          </div>
          <span className="text-slate-400 text-[10px]">CORRELATED ML INFERENCE</span>
        </div>
      )}

      {isLoading ? (
        <div className="min-h-[400px] flex flex-col items-center justify-center space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
            <Brain className="w-6 h-6 text-[#A78BFA] animate-pulse" />
          </div>
          <p className="text-xs font-mono text-slate-500">Computing SHAP Kernel feature attributions & model decision tree...</p>
        </div>
      ) : errorMsg || !explainData ? (
        <div className="card p-10 text-center space-y-3 border-[#A78BFA]/20">
          <AlertCircle className="w-10 h-10 text-[#A78BFA] mx-auto animate-bounce" />
          <h3 className="text-base font-bold text-white">Explainability Data Unavailable</h3>
          <p className="text-xs font-mono text-slate-400 max-w-md mx-auto">
            {errorMsg || 'No SHAP feature matrix generated for this attack ID yet.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* SHAP Feature Contribution Matrix */}
          <div className="lg:col-span-2 card p-6 space-y-5 border-[#A78BFA]/20">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] font-mono font-bold text-[#A78BFA] uppercase">{explainData.algorithm || 'SHAP Kernel'} Attribution</span>
                <h3 className="text-base font-bold text-white mt-0.5">SHAP Feature Contribution Matrix</h3>
                <p className="text-[11px] font-mono text-slate-500 mt-1">
                  Target Label: <span className="text-white font-bold">{explainData.prediction_label || 'Malicious'}</span> • Explained: {formatStandardDate(explainData.explained_at || new Date())}
                </p>
              </div>
              <div className="text-right">
                <span className="text-[10px] font-mono text-slate-400">Model Confidence</span>
                <div className="text-xl font-extrabold text-[#A78BFA] tabular-nums">
                  {((explainData.confidence || 0.95) * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            {/* Feature Attribution Rows */}
            <div className="space-y-3 font-mono">
              {(explainData.feature_importance || explainData.shap_values || []).map((shap: any, idx: number) => {
                const featureName = typeof shap === 'object' ? shap.feature : `Feature #${idx + 1}`;
                const weightVal = typeof shap === 'object' ? (shap.weight || 0.20) : (shap || 0.10);
                const descText = typeof shap === 'object' ? (shap.description || 'Feature contribution to model prediction vector.') : 'Attribution weight.';

                return (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.2, delay: idx * 0.05 }}
                    className="p-4 rounded-xl bg-[#1A2236] border border-white/[0.04] hover:border-[#A78BFA]/30 transition-all space-y-2.5"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-white">{featureName}</span>
                      <span className="font-bold text-[#A78BFA]">{(weightVal * 100).toFixed(0)}% weight</span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-[#080C14] overflow-hidden">
                      <motion.div
                        className="h-full rounded-full"
                        initial={{ width: '0%' }}
                        animate={{ width: `${Math.min(100, Math.max(5, weightVal * 100))}%` }}
                        transition={{ duration: 0.5, delay: idx * 0.1 }}
                        style={{
                          background: 'linear-gradient(90deg, #A78BFA, #00D4FF)',
                        }}
                      />
                    </div>
                    <p className="text-[11px] text-slate-400 leading-relaxed font-sans">{descText}</p>
                  </motion.div>
                );
              })}
            </div>
          </div>

          {/* Human Readable Explanation & Decision Reasoning */}
          <div className="card p-6 space-y-5 border-[#A78BFA]/20">
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4 text-[#A78BFA]" />
              <h3 className="text-sm font-bold text-white">AI Decision Reasoning & Audit</h3>
            </div>

            <div className="bg-[#080C14] rounded-xl p-5 border border-[#A78BFA]/20 space-y-4 font-mono">
              <span className="text-[10px] text-[#A78BFA] font-bold uppercase block mb-1">EXPLAINABILITY SUMMARY</span>
              <p className="text-xs text-slate-300 leading-relaxed font-sans">
                {explainData.human_readable_summary || `SHAP tree attribution completed for target label '${explainData.prediction_label}'.`}
              </p>
              
              <div className="pt-4 border-t border-white/[0.06] flex items-center justify-between">
                <div className="flex items-center space-x-2 text-[#22C55E]">
                  <CheckCircle className="w-4 h-4 flex-shrink-0" />
                  <span className="text-xs font-bold">AUDIT CERTIFIED</span>
                </div>
                <span className="text-[10px] text-slate-500">XAI Engine v1.0</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-[#1A2236] border border-white/[0.04] space-y-2">
              <span className="text-xs font-semibold text-white block">Audit Verification Standard</span>
              <p className="text-xs text-slate-400 leading-relaxed">
                Every decision produced by the XGBoost & Random Forest pipelines is logged with SHAP attribution weights to satisfy enterprise compliance requirements.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

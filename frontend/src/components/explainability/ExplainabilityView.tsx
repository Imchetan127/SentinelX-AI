import React, { useEffect, useState } from 'react';
import { Brain, FileText, CheckCircle, Sparkles, Activity } from 'lucide-react';

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

export const ExplainabilityView: React.FC = () => {
  const [explainData, setExplainData] = useState<any>(null);

  useEffect(() => {
    authFetch('/ml-engine/explain')
      .then((res) => res.json())
      .then((data) => setExplainData(data))
      .catch(() => {});
  }, []);

  if (!explainData) {
    return (
      <div className="min-h-[400px] flex flex-col items-center justify-center space-y-3 font-mono text-xs text-purple-400">
        <Activity className="w-8 h-8 animate-spin text-purple-400" />
        <span>Generating SHAP Feature Attribution Explanations...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-purple-500/30 flex items-center justify-between">
        <div className="space-y-1">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <Brain className="w-5 h-5" />
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">Explainable AI (XAI) Model Decision Engine</h2>
          </div>
          <p className="text-xs text-slate-400">
            Model interpretability console utilizing SHAP (SHapley Additive exPlanations) & LIME algorithms to demystify neural network and tree decision boundaries.
          </p>
        </div>

        <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs font-mono">
          <Sparkles className="w-3.5 h-3.5 text-purple-400" />
          <span>SHAP KERNEL ACTIVE</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: SHAP Feature Importance Breakdown */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-white/[0.08] space-y-5">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
            <div>
              <span className="text-xs font-mono uppercase text-purple-400 font-semibold tracking-wider">
                {explainData.method} Attribution
              </span>
              <h3 className="text-base font-bold text-white mt-0.5">SHAP Feature Contribution Matrix</h3>
            </div>

            <span className="px-3.5 py-1 rounded-xl bg-[#FF5D73]/15 text-[#FF5D73] text-xs font-mono font-bold border border-[#FF5D73]/30">
              Threat Score: {(explainData.threat_score * 100).toFixed(0)} / 100
            </span>
          </div>

          <div className="space-y-3.5 pt-1">
            {explainData.shap_values?.map((shap: any, idx: number) => (
              <div key={idx} className="p-4 rounded-xl bg-[#111827] border border-white/[0.08] space-y-2 hover:border-purple-500/30 transition-all">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="font-bold text-slate-100">{shap.feature}</span>
                  <span className="text-purple-300 font-bold">{(shap.weight * 100).toFixed(0)}% Weight Impact</span>
                </div>

                <div className="w-full bg-[#090B10] rounded-full h-2 overflow-hidden border border-white/[0.08]">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-[#00D4FF] h-full rounded-full transition-all duration-500"
                    style={{ width: `${shap.weight * 100}%` }}
                  />
                </div>

                <p className="text-xs text-slate-400 leading-relaxed font-sans">{shap.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Human Readable Explanation Summary */}
        <div className="glass-panel p-6 rounded-2xl border border-white/[0.08] space-y-5">
          <div className="border-b border-white/[0.08] pb-3">
            <h3 className="text-sm font-bold text-white uppercase font-mono flex items-center space-x-2">
              <FileText className="w-4 h-4 text-purple-400" />
              <span>Human-Readable Explanation</span>
            </h3>
          </div>

          <div className="p-5 rounded-xl bg-[#090B10] border border-purple-500/20 text-xs font-mono text-slate-200 leading-relaxed space-y-4">
            <p className="font-sans text-xs leading-relaxed text-slate-300">{explainData.human_readable_summary}</p>
            <div className="pt-3 border-t border-white/[0.08] flex items-center space-x-2 text-[#2EE59D]">
              <CheckCircle className="w-4 h-4 flex-shrink-0" />
              <span className="font-bold text-[11px]">Audit Certified by Explainable AI Engine</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

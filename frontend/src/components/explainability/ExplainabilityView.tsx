import React, { useEffect, useState } from 'react';
import { Brain, FileText, CheckCircle } from 'lucide-react';

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

  if (!explainData) return <div className="p-8 text-cyan-400 font-mono">Generating Explainable AI Explanations...</div>;

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl border border-cyan-500/30 flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <Brain className="w-6 h-6 text-cyan-400" />
            <span className="gradient-text-blue">Explainable AI (XAI) Model Decision Engine</span>
          </h2>
          <p className="text-sm text-slate-400">
            Interpretability dashboard utilizing SHAP (SHapley Additive exPlanations) & LIME to demystify complex neural network and tree decision boundaries.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <span className="text-xs uppercase font-mono text-cyan-400">{explainData.method}</span>
              <h3 className="text-md font-bold text-white mt-0.5">SHAP Feature Importance Breakdown</h3>
            </div>
            <span className="px-3 py-1 rounded bg-rose-500/20 text-rose-400 text-xs font-mono font-bold border border-rose-500/40">
              Score: {(explainData.threat_score * 100).toFixed(0)} / 100
            </span>
          </div>

          <div className="space-y-3 pt-2">
            {explainData.shap_values?.map((shap: any, idx: number) => (
              <div key={idx} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="font-bold text-slate-200">{shap.feature}</span>
                  <span className="text-cyan-400 font-bold">{(shap.weight * 100).toFixed(0)}% Impact</span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                  <div
                    className="bg-gradient-to-r from-cyan-500 to-purple-500 h-2 rounded-full"
                    style={{ width: `${shap.weight * 100}%` }}
                  ></div>
                </div>
                <p className="text-xs text-slate-400">{shap.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Human Readable Summary */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-slate-200 uppercase font-mono flex items-center space-x-2">
            <FileText className="w-4 h-4 text-cyan-400" />
            <span>Human-Readable Explanation Summary</span>
          </h3>

          <div className="p-4 rounded-xl bg-slate-950 border border-cyan-500/20 text-xs font-mono text-slate-300 leading-relaxed space-y-3">
            <p>{explainData.human_readable_summary}</p>
            <div className="pt-2 border-t border-slate-800 flex items-center space-x-2 text-cyan-400">
              <CheckCircle className="w-4 h-4" />
              <span>Verified by Explainable AI Auditor</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

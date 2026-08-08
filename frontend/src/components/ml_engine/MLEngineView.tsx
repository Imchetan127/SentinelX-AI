import React, { useEffect, useState } from 'react';
import { Cpu, Zap, Award, Activity, RefreshCw } from 'lucide-react';

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

export const MLEngineView: React.FC = () => {
  const [benchmarks, setBenchmarks] = useState<any>(null);
  const [trainingResult, setTrainingResult] = useState<any>(null);

  useEffect(() => {
    authFetch('/ml-engine/benchmarks')
      .then((res) => res.json())
      .then((data) => setBenchmarks(data))
      .catch(() => {});
  }, []);

  const handleTrain = (modelName: string) => {
    authFetch(`/ml-engine/train/${modelName}`, { method: 'POST' })
      .then((res) => res.json())
      .then((data) => {
        setTrainingResult(data);
      })
      .catch(() => {});
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-white/[0.08] flex items-center justify-between">
        <div className="space-y-1">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400">
              <Cpu className="w-5 h-5" />
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">Machine Learning Benchmarks & Model Trainer</h2>
          </div>
          <p className="text-xs text-slate-400">
            Compare cross-validation performance metrics across supervised decision trees, gradient boosting, and neural classifiers (Random Forest, LightGBM, XGBoost, Isolation Forest, CNN-GRU).
          </p>
        </div>
      </div>

      {benchmarks && (
        <div className="glass-panel p-6 rounded-2xl border border-white/[0.08] space-y-4">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
            <h3 className="text-sm font-bold text-white uppercase font-mono">Model Comparison Matrix</h3>
            <span className="text-[11px] font-mono text-slate-400">5-Fold Cross Validation</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs font-mono">
              <thead>
                <tr className="border-b border-white/[0.08] text-slate-400 uppercase text-[11px] tracking-wider">
                  <th className="py-3 px-4 font-semibold">Architecture</th>
                  <th className="py-3 px-4 font-semibold">Accuracy</th>
                  <th className="py-3 px-4 font-semibold">Precision</th>
                  <th className="py-3 px-4 font-semibold">Recall</th>
                  <th className="py-3 px-4 font-semibold">F1 Score</th>
                  <th className="py-3 px-4 font-semibold">ROC AUC</th>
                  <th className="py-3 px-4 font-semibold">Train Time</th>
                  <th className="py-3 px-4 font-semibold">Latency</th>
                  <th className="py-3 px-4 text-right font-semibold">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.06]">
                {Object.entries(benchmarks).map(([mName, mData]: [string, any]) => (
                  <tr key={mName} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3.5 px-4 font-bold text-white flex items-center space-x-2">
                      <Award className="w-4 h-4 text-purple-400" />
                      <span>{mName}</span>
                    </td>
                    <td className="py-3.5 px-4 text-[#00D4FF] font-bold">{(mData.accuracy * 100).toFixed(1)}%</td>
                    <td className="py-3.5 px-4 text-[#2EE59D]">{(mData.precision * 100).toFixed(1)}%</td>
                    <td className="py-3.5 px-4 text-[#2EE59D]">{(mData.recall * 100).toFixed(1)}%</td>
                    <td className="py-3.5 px-4 text-purple-300 font-bold">{(mData.f1_score * 100).toFixed(1)}%</td>
                    <td className="py-3.5 px-4 text-[#FFB547]">{mData.roc_auc}</td>
                    <td className="py-3.5 px-4 text-slate-400">{mData.training_time_sec}s</td>
                    <td className="py-3.5 px-4 text-slate-400">{mData.inference_time_ms} ms</td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => handleTrain(mName)}
                        className="px-3.5 py-1.5 rounded-lg bg-purple-500/15 hover:bg-purple-500/30 text-purple-300 border border-purple-500/30 text-[11px] font-mono font-bold transition-all"
                      >
                        Retrain Model
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {trainingResult && (
        <div className="glass-panel p-6 rounded-2xl border border-purple-500/30 space-y-5">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
            <h3 className="text-sm font-bold text-white uppercase font-mono flex items-center space-x-2">
              <Zap className="w-4 h-4 text-purple-400" />
              <span>Retraining & Matrix Evaluation: {trainingResult.model_name}</span>
            </h3>
            <span className="px-2.5 py-0.5 rounded text-[11px] font-mono bg-purple-500/20 text-purple-300 border border-purple-500/40 font-bold">
              STATUS: TRAINED & VERIFIED
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Confusion Matrix */}
            <div className="space-y-3 font-mono text-xs">
              <span className="text-slate-400 font-semibold block uppercase">Confusion Matrix Breakdown:</span>
              <div className="grid grid-cols-2 gap-3 text-center">
                <div className="p-4 bg-[#111827] rounded-xl border border-white/[0.08]">
                  <span className="text-slate-400 text-[10px] uppercase block">True Negative</span>
                  <span className="text-[#2EE59D] text-lg font-bold mt-1 block">
                    {trainingResult.confusion_matrix[0][0]}
                  </span>
                </div>
                <div className="p-4 bg-[#111827] rounded-xl border border-white/[0.08]">
                  <span className="text-slate-400 text-[10px] uppercase block">False Positive</span>
                  <span className="text-[#FFB547] text-lg font-bold mt-1 block">
                    {trainingResult.confusion_matrix[0][1]}
                  </span>
                </div>
                <div className="p-4 bg-[#111827] rounded-xl border border-white/[0.08]">
                  <span className="text-slate-400 text-[10px] uppercase block">False Negative</span>
                  <span className="text-[#FF5D73] text-lg font-bold mt-1 block">
                    {trainingResult.confusion_matrix[1][0]}
                  </span>
                </div>
                <div className="p-4 bg-[#111827] rounded-xl border border-white/[0.08]">
                  <span className="text-slate-400 text-[10px] uppercase block">True Positive</span>
                  <span className="text-[#00D4FF] text-lg font-bold mt-1 block">
                    {trainingResult.confusion_matrix[1][1]}
                  </span>
                </div>
              </div>
            </div>

            {/* Feature Importance Weights */}
            <div className="space-y-3 font-mono text-xs">
              <span className="text-slate-400 font-semibold block uppercase">Top Feature Importance Weights:</span>
              <div className="space-y-2">
                {trainingResult.feature_importance?.map((feat: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-[#111827] border border-white/[0.08]">
                    <span className="text-slate-200">{feat.feature}</span>
                    <span className="text-purple-300 font-bold">{(feat.importance * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

import React, { useEffect, useState } from 'react';
import { Cpu, Zap, Award } from 'lucide-react';

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
      <div className="glass-panel p-6 rounded-2xl border border-purple-500/30 flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <Cpu className="w-6 h-6 text-purple-400" />
            <span className="gradient-text-purple">Machine Learning Engine Benchmarks & Model Trainer</span>
          </h2>
          <p className="text-sm text-slate-400">
            Compare performance metrics across supervised classifiers and anomaly detection models (Random Forest, LightGBM, XGBoost, Isolation Forest, CNN-GRU).
          </p>
        </div>
      </div>

      {benchmarks && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-slate-200 uppercase font-mono">Model Comparison Matrix</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-3 px-4">Model Architecture</th>
                  <th className="py-3 px-4">Accuracy</th>
                  <th className="py-3 px-4">Precision</th>
                  <th className="py-3 px-4">Recall</th>
                  <th className="py-3 px-4">F1 Score</th>
                  <th className="py-3 px-4">ROC AUC</th>
                  <th className="py-3 px-4">Training Time</th>
                  <th className="py-3 px-4">Inference Latency</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {Object.entries(benchmarks).map(([mName, mData]: [string, any]) => (
                  <tr key={mName} className="hover:bg-slate-900/50">
                    <td className="py-3 px-4 font-bold text-white flex items-center space-x-2">
                      <Award className="w-3.5 h-3.5 text-purple-400" />
                      <span>{mName}</span>
                    </td>
                    <td className="py-3 px-4 text-cyan-300">{(mData.accuracy * 100).toFixed(1)}%</td>
                    <td className="py-3 px-4 text-emerald-300">{(mData.precision * 100).toFixed(1)}%</td>
                    <td className="py-3 px-4 text-emerald-300">{(mData.recall * 100).toFixed(1)}%</td>
                    <td className="py-3 px-4 text-purple-300">{(mData.f1_score * 100).toFixed(1)}%</td>
                    <td className="py-3 px-4 text-amber-300">{mData.roc_auc}</td>
                    <td className="py-3 px-4 text-slate-400">{mData.training_time_sec}s</td>
                    <td className="py-3 px-4 text-slate-400">{mData.inference_time_ms} ms</td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleTrain(mName)}
                        className="px-3 py-1 rounded bg-purple-600/30 hover:bg-purple-600/50 text-purple-300 border border-purple-500/40 text-[11px] font-mono transition-all"
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
        <div className="glass-panel p-6 rounded-2xl border border-purple-500/30 space-y-4">
          <h3 className="text-sm font-bold text-slate-200 uppercase font-mono flex items-center space-x-2">
            <Zap className="w-4 h-4 text-purple-400" />
            <span>Retraining & Feature Importance: {trainingResult.model_name}</span>
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <span className="text-xs font-mono text-slate-400">Confusion Matrix Output:</span>
              <div className="grid grid-cols-2 gap-2 text-center font-mono text-xs">
                <div className="p-3 bg-slate-900 rounded border border-slate-800">
                  <span className="text-slate-500 block">True Negative</span>
                  <span className="text-emerald-400 text-base font-bold">{trainingResult.confusion_matrix[0][0]}</span>
                </div>
                <div className="p-3 bg-slate-900 rounded border border-slate-800">
                  <span className="text-slate-500 block">False Positive</span>
                  <span className="text-amber-400 text-base font-bold">{trainingResult.confusion_matrix[0][1]}</span>
                </div>
                <div className="p-3 bg-slate-900 rounded border border-slate-800">
                  <span className="text-slate-500 block">False Negative</span>
                  <span className="text-rose-400 text-base font-bold">{trainingResult.confusion_matrix[1][0]}</span>
                </div>
                <div className="p-3 bg-slate-900 rounded border border-slate-800">
                  <span className="text-slate-500 block">True Positive</span>
                  <span className="text-cyan-400 text-base font-bold">{trainingResult.confusion_matrix[1][1]}</span>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <span className="text-xs font-mono text-slate-400">Top Feature Importance Weights:</span>
              <div className="space-y-1.5 font-mono text-xs">
                {trainingResult.feature_importance?.map((feat: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-2 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-300">{feat.feature}</span>
                    <span className="text-purple-400 font-bold">{(feat.importance * 100).toFixed(0)}%</span>
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

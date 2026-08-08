import React, { useState } from 'react';
import { Shield, Search, CheckCircle2, Cpu } from 'lucide-react';

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

export const BlueTeamView: React.FC = () => {
  const [inputText, setInputText] = useState("admin' OR '1'='1 --");
  const [artifactType, setArtifactType] = useState("SQL Injection Payload");
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleInspect = () => {
    setIsAnalyzing(true);
    authFetch('/blue-team/inspect-text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: inputText, artifact_type: artifactType })
    })
      .then((res) => res.json())
      .then((data) => {
        setAnalysisResult(data);
        setIsAnalyzing(false);
      })
      .catch(() => {
        setIsAnalyzing(false);
      });
  };

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl border border-cyan-500/30 flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <Shield className="w-6 h-6 text-cyan-400" />
            <span className="gradient-text-blue">Blue Team Real-Time AI Threat Inspector</span>
          </h2>
          <p className="text-sm text-slate-400">
            Submit raw HTTP request bodies, email headers, SQL strings, or PCAP telemetry to analyze via automated AI detection models.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Panel */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-200 uppercase font-mono">Payload & Artifact Inspector</h3>
            <select
              value={artifactType}
              onChange={(e) => setArtifactType(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-300 font-mono focus:outline-none focus:border-cyan-500"
            >
              <option value="SQL Injection Payload">SQL Injection Payload</option>
              <option value="Phishing Email Body">Phishing Email Body</option>
              <option value="XSS Script Vector">XSS Script Vector</option>
              <option value="LLM Prompt Vector">LLM Prompt Vector</option>
            </select>
          </div>

          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            rows={8}
            className="w-full p-4 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-xs font-mono focus:outline-none focus:border-cyan-500/50"
            placeholder="Paste text or payload here..."
          />

          <button
            onClick={handleInspect}
            disabled={isAnalyzing}
            className="w-full py-3 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-sm flex items-center justify-center space-x-2 transition-all glow-blue disabled:opacity-50"
          >
            <Search className="w-4 h-4" />
            <span>{isAnalyzing ? 'Analyzing Payload...' : 'Inspect & Classify Threat'}</span>
          </button>
        </div>

        {/* Results Panel */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-slate-200 uppercase font-mono">AI Threat Scorecard</h3>

          {analysisResult ? (
            <div className="space-y-4">
              <div className={`p-4 rounded-xl border flex items-center justify-between ${
                analysisResult.threat_detected
                  ? 'bg-rose-500/10 border-rose-500/40 glow-red'
                  : 'bg-emerald-500/10 border-emerald-500/40'
              }`}>
                <div>
                  <span className="text-xs uppercase font-mono text-slate-400">Classification</span>
                  <h4 className={`text-lg font-bold ${analysisResult.threat_detected ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {analysisResult.threat_category}
                  </h4>
                </div>
                <div className="text-right">
                  <span className="text-xs uppercase font-mono text-slate-400">Risk Score</span>
                  <p className="text-2xl font-bold font-mono text-white">{(analysisResult.threat_score * 100).toFixed(0)} / 100</p>
                </div>
              </div>

              <div className="space-y-2">
                <span className="text-xs font-mono text-slate-400">Indicators & Patterns Found:</span>
                <div className="space-y-1">
                  {analysisResult.indicators?.map((ind: string, idx: number) => (
                    <div key={idx} className="p-2 rounded bg-slate-900 border border-slate-800 text-xs font-mono text-amber-300">
                      • {ind}
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <span className="text-xs font-mono text-slate-400">Recommended Blue Team Mitigations:</span>
                <div className="space-y-1">
                  {analysisResult.recommended_mitigations?.map((mit: string, idx: number) => (
                    <div key={idx} className="p-2 rounded bg-slate-900 border border-slate-800 text-xs font-mono text-cyan-300 flex items-center space-x-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
                      <span>{mit}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-center text-slate-500 space-y-2">
              <Cpu className="w-10 h-10 text-slate-700 animate-pulse" />
              <p className="text-xs font-mono">Submit payload content above to initiate real-time AI classification.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

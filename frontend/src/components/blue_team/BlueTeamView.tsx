import React, { useState } from 'react';
import { Shield, Search, CheckCircle2, Cpu, AlertTriangle, Code, FileCode } from 'lucide-react';

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
      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-white/[0.08] flex items-center justify-between">
        <div className="space-y-1">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-[#00D4FF]/10 text-[#00D4FF]">
              <Shield className="w-5 h-5" />
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">Blue Team Real-Time AI Threat Inspector</h2>
          </div>
          <p className="text-xs text-slate-400">
            Submit raw HTTP request bodies, email headers, SQL query strings, or PCAP network telemetry for automated real-time classification by supervised ML models.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Input Payload Panel */}
        <div className="glass-panel p-6 rounded-2xl border border-white/[0.08] space-y-4">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
            <div className="flex items-center space-x-2">
              <FileCode className="w-4 h-4 text-[#00D4FF]" />
              <h3 className="text-sm font-bold text-white uppercase font-mono">Payload & Artifact Inspector</h3>
            </div>
            <select
              value={artifactType}
              onChange={(e) => setArtifactType(e.target.value)}
              className="bg-[#111827] border border-white/[0.08] rounded-xl px-3 py-1.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-[#00D4FF]/50"
            >
              <option value="SQL Injection Payload">SQL Injection Payload</option>
              <option value="Phishing Email Body">Phishing Email Body</option>
              <option value="XSS Script Vector">XSS Script Vector</option>
              <option value="LLM Prompt Vector">LLM Prompt Vector</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-mono text-slate-400">Raw Telemetry / Payload Input:</label>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              rows={9}
              className="w-full p-4 rounded-xl bg-[#090B10] border border-white/[0.08] text-slate-200 text-xs font-mono focus:outline-none focus:border-[#00D4FF]/50 leading-relaxed"
              placeholder="Paste raw telemetry or code string here..."
            />
          </div>

          <button
            onClick={handleInspect}
            disabled={isAnalyzing}
            className="w-full py-3.5 rounded-xl bg-[#00D4FF] hover:bg-[#00D4FF]/90 text-slate-950 font-bold text-xs font-mono flex items-center justify-center space-x-2 transition-all shadow-md disabled:opacity-50"
          >
            <Search className="w-4 h-4" />
            <span>{isAnalyzing ? 'CLASSIFYING TELEMETRY...' : 'INSPECT & CLASSIFY THREAT'}</span>
          </button>
        </div>

        {/* Right Column: AI Threat Scorecard */}
        <div className="glass-panel p-6 rounded-2xl border border-white/[0.08] space-y-5">
          <div className="border-b border-white/[0.08] pb-3">
            <h3 className="text-sm font-bold text-white uppercase font-mono">AI Threat Scorecard</h3>
          </div>

          {analysisResult ? (
            <div className="space-y-5">
              {/* Classification Status & Risk Score */}
              <div
                className={`p-5 rounded-xl border flex items-center justify-between ${
                  analysisResult.threat_detected
                    ? 'bg-[#FF5D73]/10 border-[#FF5D73]/30'
                    : 'bg-[#2EE59D]/10 border-[#2EE59D]/30'
                }`}
              >
                <div>
                  <span className="text-[10px] uppercase font-mono text-slate-400">Classification Outcome</span>
                  <h4
                    className={`text-lg font-bold font-mono mt-0.5 ${
                      analysisResult.threat_detected ? 'text-[#FF5D73]' : 'text-[#2EE59D]'
                    }`}
                  >
                    {analysisResult.threat_category}
                  </h4>
                </div>
                <div className="text-right">
                  <span className="text-[10px] uppercase font-mono text-slate-400">AI Risk Index</span>
                  <p className="text-2xl font-bold font-mono text-white mt-0.5">
                    {(analysisResult.threat_score * 100).toFixed(0)} <span className="text-xs text-slate-400">/ 100</span>
                  </p>
                </div>
              </div>

              {/* Indicators Detected */}
              <div className="space-y-2">
                <span className="text-xs font-mono text-slate-400 font-semibold">Matched Threat Indicators:</span>
                <div className="space-y-1.5 font-mono text-xs">
                  {analysisResult.indicators?.map((ind: string, idx: number) => (
                    <div key={idx} className="p-2.5 rounded-lg bg-[#111827] border border-white/[0.08] text-[#FFB547]">
                      • {ind}
                    </div>
                  ))}
                </div>
              </div>

              {/* Blue Team Mitigations */}
              <div className="space-y-2">
                <span className="text-xs font-mono text-slate-400 font-semibold">Automated Blue Team Mitigations:</span>
                <div className="space-y-1.5 font-mono text-xs">
                  {analysisResult.recommended_mitigations?.map((mit: string, idx: number) => (
                    <div key={idx} className="p-2.5 rounded-lg bg-[#111827] border border-white/[0.08] text-[#00D4FF] flex items-center space-x-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-[#00D4FF] flex-shrink-0" />
                      <span>{mit}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="min-h-[280px] flex flex-col items-center justify-center text-center text-slate-500 space-y-3 font-mono">
              <Cpu className="w-10 h-10 text-slate-600 animate-pulse" />
              <p className="text-xs">Submit payload content above to initiate real-time AI classification.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

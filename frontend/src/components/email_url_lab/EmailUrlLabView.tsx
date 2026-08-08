import React, { useState } from 'react';
import { Mail, Globe, Search, ArrowRight, ShieldCheck, ShieldAlert, Lock, Server } from 'lucide-react';

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

export const EmailUrlLabView: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'url' | 'email'>('url');

  // URL State
  const [inputUrl, setInputUrl] = useState('http://185.220.101.5/verify-account-bank-update/login.php');
  const [urlResult, setUrlResult] = useState<any>(null);
  const [isUrlAnalyzing, setIsUrlAnalyzing] = useState(false);

  // Email State
  const [emailSubject, setEmailSubject] = useState('URGENT: Executive Payroll & Security Verification Required');
  const [emailSender, setEmailSender] = useState('ceo-security@company-corp-auth-verify.xyz');
  const [emailBody, setEmailBody] = useState('Dear Employee,\n\nYour corporate email access will be suspended within 24 hours unless you log in immediately to verify your credentials.\n\nClick link: http://secure-verify-auth.xyz/login\n\nSecurity Team');
  const [emailResult, setEmailResult] = useState<any>(null);
  const [isEmailAnalyzing, setIsEmailAnalyzing] = useState(false);

  const sampleUrls = [
    { label: "Phishing URL (Spoofed IP & Keyword)", url: "http://185.220.101.5/verify-account-bank-update/login.php" },
    { label: "Suspicious TLD & Brand Spoof", url: "https://paypal-security-update-account-verification.xyz/checkout" },
    { label: "Legitimate Corporate URL", url: "https://www.github.com/security/overview" },
    { label: "Legitimate Bank Domain", url: "https://www.chase.com/personal/banking" }
  ];

  const sampleEmails = [
    {
      label: "Spear Phishing Executive Impersonation",
      subject: "URGENT: Executive Payroll & Security Verification Required",
      sender: "ceo-security@company-corp-auth-verify.xyz",
      body: "Dear Employee,\n\nYour corporate email access will be suspended within 24 hours unless you log in immediately to verify your credentials.\n\nClick link: http://secure-verify-auth.xyz/login\n\nSecurity Team"
    },
    {
      label: "Crypto Scam Lottery Spam",
      subject: "CONGRATULATIONS! You won 2.5 BTC Claim Prize Immediately",
      sender: "claims@bitcoin-crypto-rewards.online",
      body: "You have been selected as the weekly crypto bonus winner! Claim 2.5 Bitcoin rewards now before timer expires: http://crypto-claim-bonus.site"
    },
    {
      label: "Legitimate System Notification",
      subject: "[GitHub] Security advisory alert for repository",
      sender: "notifications@github.com",
      body: "We detected a new security vulnerability alert in one of your repository dependencies. Visit your repository security tab for details."
    }
  ];

  const handleInspectUrl = (urlToTest?: string) => {
    const targetUrl = urlToTest || inputUrl;
    setIsUrlAnalyzing(true);
    authFetch('/blue-team/inspect-url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: targetUrl })
    })
      .then((res) => res.json())
      .then((data) => {
        setUrlResult(data);
        setIsUrlAnalyzing(false);
      })
      .catch(() => {
        setIsUrlAnalyzing(false);
      });
  };

  const handleInspectEmail = () => {
    setIsEmailAnalyzing(true);
    authFetch('/blue-team/inspect-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ subject: emailSubject, sender: emailSender, body: emailBody })
    })
      .then((res) => res.json())
      .then((data) => {
        setEmailResult(data);
        setIsEmailAnalyzing(false);
      })
      .catch(() => {
        setIsEmailAnalyzing(false);
      });
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-white/[0.08] flex items-center justify-between">
        <div className="space-y-1">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-[#00D4FF]/10 text-[#00D4FF]">
              <Globe className="w-5 h-5" />
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">Threat Intelligence & Phishing Lab</h2>
          </div>
          <p className="text-xs text-slate-400">
            Dedicated laboratory for extracting URL domain feature entropy, analyzing suspicious TLDs, inspecting spam email headers, and validating SPF/DKIM/DMARC signatures.
          </p>
        </div>

        <div className="flex items-center space-x-1.5 bg-[#111827] p-1.5 rounded-xl border border-white/[0.08] font-mono text-xs">
          <button
            onClick={() => setActiveSubTab('url')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              activeSubTab === 'url'
                ? 'bg-[#161B22] text-[#00D4FF] border border-[#00D4FF]/30 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            URL Intelligence
          </button>
          <button
            onClick={() => setActiveSubTab('email')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              activeSubTab === 'email'
                ? 'bg-[#161B22] text-purple-300 border border-purple-500/30 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Email Intelligence
          </button>
        </div>
      </div>

      {activeSubTab === 'url' ? (
        /* URL INTELLIGENCE WORKSPACE */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-white/[0.08] space-y-5">
            <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
              <h3 className="text-sm font-bold text-white uppercase font-mono flex items-center space-x-2">
                <Globe className="w-4 h-4 text-[#00D4FF]" />
                <span>URL Phishing Inspection & Entropy Extraction</span>
              </h3>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-mono text-slate-400">Target Web URL String:</label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={inputUrl}
                  onChange={(e) => setInputUrl(e.target.value)}
                  className="flex-1 bg-[#090B10] border border-white/[0.08] rounded-xl px-4 py-3 text-xs font-mono text-[#00D4FF] focus:outline-none focus:border-[#00D4FF]/50"
                  placeholder="https://example.com/login"
                />
                <button
                  onClick={() => handleInspectUrl()}
                  disabled={isUrlAnalyzing}
                  className="px-6 py-3 rounded-xl bg-[#00D4FF] hover:bg-[#00D4FF]/90 text-slate-950 font-bold text-xs font-mono flex items-center space-x-2 transition-all shadow-md disabled:opacity-50"
                >
                  <Search className="w-4 h-4" />
                  <span>{isUrlAnalyzing ? 'ANALYZING...' : 'ANALYZE URL'}</span>
                </button>
              </div>
            </div>

            {/* Presets */}
            <div className="space-y-2">
              <span className="text-xs font-mono text-slate-400">Preset Simulation Targets:</span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {sampleUrls.map((s, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setInputUrl(s.url);
                      handleInspectUrl(s.url);
                    }}
                    className="p-3.5 rounded-xl bg-[#111827] hover:bg-[#111827]/80 border border-white/[0.08] hover:border-white/[0.16] text-left text-xs font-mono space-y-1 transition-all"
                  >
                    <span className="text-[#00D4FF] font-bold block">{s.label}</span>
                    <span className="text-slate-400 truncate block text-[11px] font-mono">{s.url}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Results Output */}
            {urlResult && (
              <div className="space-y-4 pt-4 border-t border-white/[0.08]">
                <div
                  className={`p-4 rounded-xl border flex items-center justify-between ${
                    urlResult.is_phishing
                      ? 'bg-[#FF5D73]/10 border-[#FF5D73]/30'
                      : 'bg-[#2EE59D]/10 border-[#2EE59D]/30'
                  }`}
                >
                  <div>
                    <span className="text-[10px] uppercase font-mono text-slate-400">Classification Outcome</span>
                    <h4
                      className={`text-lg font-bold font-mono ${
                        urlResult.is_phishing ? 'text-[#FF5D73]' : 'text-[#2EE59D]'
                      }`}
                    >
                      {urlResult.category}
                    </h4>
                  </div>
                  <div className="text-right font-mono">
                    <span className="text-[10px] uppercase text-slate-400">Threat Score</span>
                    <p className="text-2xl font-bold text-white">{(urlResult.threat_score * 100).toFixed(0)} <span className="text-xs text-slate-400">/ 100</span></p>
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
                  <div className="p-3 rounded-xl bg-[#111827] border border-white/[0.08]">
                    <span className="text-slate-400 text-[10px] block">IP Host Check</span>
                    <p className={`font-bold mt-1 ${urlResult.extracted_features?.has_ip_address ? 'text-[#FF5D73]' : 'text-[#2EE59D]'}`}>
                      {urlResult.extracted_features?.has_ip_address ? 'YES (IP Host)' : 'NO (Domain Host)'}
                    </p>
                  </div>
                  <div className="p-3 rounded-xl bg-[#111827] border border-white/[0.08]">
                    <span className="text-slate-400 text-[10px] block">URL Length</span>
                    <p className="text-slate-200 font-bold mt-1">{urlResult.extracted_features?.url_length} chars</p>
                  </div>
                  <div className="p-3 rounded-xl bg-[#111827] border border-white/[0.08]">
                    <span className="text-slate-400 text-[10px] block">SSL Status</span>
                    <p className={`font-bold mt-1 ${urlResult.extracted_features?.is_https ? 'text-[#2EE59D]' : 'text-[#FFB547]'}`}>
                      {urlResult.extracted_features?.is_https ? 'HTTPS Encrypted' : 'HTTP Unencrypted'}
                    </p>
                  </div>
                  <div className="p-3 rounded-xl bg-[#111827] border border-white/[0.08]">
                    <span className="text-slate-400 text-[10px] block">Brand Keywords</span>
                    <p className="text-[#00D4FF] font-bold mt-1">{urlResult.extracted_features?.suspicious_keyword_count} matched</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Info Box */}
          <div className="glass-panel p-6 rounded-2xl border border-white/[0.08] space-y-4">
            <h4 className="text-sm font-bold text-white uppercase font-mono">Extracted Feature Indicators</h4>
            {urlResult ? (
              <div className="space-y-2 font-mono text-xs">
                {urlResult.indicators?.map((ind: string, idx: number) => (
                  <div key={idx} className="p-3 rounded-xl bg-[#111827] border border-white/[0.08] text-[#FFB547]">
                    • {ind}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500 font-mono">Run a URL scan above to extract security indicators.</p>
            )}
          </div>
        </div>
      ) : (
        /* EMAIL INTELLIGENCE WORKSPACE */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-white/[0.08] space-y-4">
            <h3 className="text-sm font-bold text-white uppercase font-mono flex items-center space-x-2 border-b border-white/[0.08] pb-3">
              <Mail className="w-4 h-4 text-purple-400" />
              <span>Spam Email Header & Payload Inspection</span>
            </h3>

            <div className="space-y-3 font-mono text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Subject Header:</label>
                <input
                  type="text"
                  value={emailSubject}
                  onChange={(e) => setEmailSubject(e.target.value)}
                  className="w-full bg-[#090B10] border border-white/[0.08] rounded-xl px-4 py-2.5 text-slate-200 focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Sender Email Address:</label>
                <input
                  type="text"
                  value={emailSender}
                  onChange={(e) => setEmailSender(e.target.value)}
                  className="w-full bg-[#090B10] border border-white/[0.08] rounded-xl px-4 py-2.5 text-slate-200 focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Email Body Content:</label>
                <textarea
                  value={emailBody}
                  onChange={(e) => setEmailBody(e.target.value)}
                  rows={5}
                  className="w-full bg-[#090B10] border border-white/[0.08] rounded-xl p-4 text-slate-200 focus:outline-none focus:border-purple-500 leading-relaxed"
                />
              </div>

              <button
                onClick={handleInspectEmail}
                disabled={isEmailAnalyzing}
                className="w-full py-3.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs font-mono flex items-center justify-center space-x-2 transition-all shadow-md disabled:opacity-50"
              >
                <Search className="w-4 h-4" />
                <span>{isEmailAnalyzing ? 'INSPECTING EMAIL...' : 'INSPECT EMAIL WITH AI MODEL'}</span>
              </button>
            </div>

            {/* Email Presets */}
            <div className="space-y-2 pt-2 border-t border-white/[0.08]">
              <span className="text-xs font-mono text-slate-400">Preset Attack Scenarios:</span>
              <div className="space-y-2 font-mono text-xs">
                {sampleEmails.map((se, idx) => (
                  <div
                    key={idx}
                    onClick={() => {
                      setEmailSubject(se.subject);
                      setEmailSender(se.sender);
                      setEmailBody(se.body);
                    }}
                    className="p-3.5 rounded-xl bg-[#111827] hover:bg-[#111827]/80 border border-white/[0.08] cursor-pointer transition-all flex items-center justify-between"
                  >
                    <div>
                      <span className="text-purple-300 font-bold block">{se.label}</span>
                      <span className="text-slate-400 text-[11px] block">{se.subject}</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-slate-500" />
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Email Result Output */}
          <div className="glass-panel p-6 rounded-2xl border border-white/[0.08] space-y-4">
            <h4 className="text-sm font-bold text-white uppercase font-mono">Email AI Scorecard</h4>
            {emailResult ? (
              <div className="space-y-4 font-mono text-xs">
                <div
                  className={`p-4 rounded-xl border flex items-center justify-between ${
                    emailResult.is_spam
                      ? 'bg-[#FF5D73]/10 border-[#FF5D73]/30'
                      : 'bg-[#2EE59D]/10 border-[#2EE59D]/30'
                  }`}
                >
                  <div>
                    <span className="text-slate-400 uppercase text-[10px]">Classification</span>
                    <h4
                      className={`text-base font-bold ${
                        emailResult.is_spam ? 'text-[#FF5D73]' : 'text-[#2EE59D]'
                      }`}
                    >
                      {emailResult.category}
                    </h4>
                  </div>
                  <div className="text-right">
                    <span className="text-slate-400 uppercase text-[10px]">Threat Score</span>
                    <p className="text-xl font-bold text-white">{(emailResult.threat_score * 100).toFixed(0)} <span className="text-xs text-slate-400">/ 100</span></p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="p-2.5 rounded-xl bg-[#111827] border border-white/[0.08]">
                    <span className="text-slate-400 block text-[10px]">SPF Header</span>
                    <span
                      className={`font-bold mt-1 block ${
                        emailResult.spf_status === 'FAIL' ? 'text-[#FF5D73]' : 'text-[#2EE59D]'
                      }`}
                    >
                      {emailResult.spf_status}
                    </span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-[#111827] border border-white/[0.08]">
                    <span className="text-slate-400 block text-[10px]">DKIM Status</span>
                    <span
                      className={`font-bold mt-1 block ${
                        emailResult.dkim_status === 'FAIL' ? 'text-[#FF5D73]' : 'text-[#2EE59D]'
                      }`}
                    >
                      {emailResult.dkim_status}
                    </span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-[#111827] border border-white/[0.08]">
                    <span className="text-slate-400 block text-[10px]">DMARC Rule</span>
                    <span
                      className={`font-bold mt-1 block ${
                        emailResult.dmarc_status === 'REJECT' ? 'text-[#FF5D73]' : 'text-[#2EE59D]'
                      }`}
                    >
                      {emailResult.dmarc_status}
                    </span>
                  </div>
                </div>

                <div className="space-y-2">
                  <span className="text-slate-400 font-semibold">Matched Threat Signals:</span>
                  {emailResult.indicators?.map((ind: string, idx: number) => (
                    <div key={idx} className="p-2.5 rounded-xl bg-[#111827] border border-white/[0.08] text-[#FFB547]">
                      • {ind}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-500 font-mono">Submit email details above to generate email AI classification scorecard.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

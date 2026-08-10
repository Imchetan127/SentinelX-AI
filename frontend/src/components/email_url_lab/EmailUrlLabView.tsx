'use client';

import React, { useState } from 'react';
import { Globe, Mail, Search, ArrowRight, ShieldAlert, Cpu, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
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
    { label: 'Phishing URL (Spoofed IP & Keyword)', url: 'http://185.220.101.5/verify-account-bank-update/login.php' },
    { label: 'Suspicious TLD & Brand Spoof', url: 'https://paypal-security-update-account-verification.xyz/checkout' },
    { label: 'Legitimate Corporate URL', url: 'https://www.github.com/security/overview' },
    { label: 'Legitimate Bank Domain', url: 'https://www.chase.com/personal/banking' },
  ];

  const sampleEmails = [
    {
      label: 'Spear Phishing Executive Impersonation',
      subject: 'URGENT: Executive Payroll & Security Verification Required',
      sender: 'ceo-security@company-corp-auth-verify.xyz',
      body: 'Dear Employee,\n\nYour corporate email access will be suspended within 24 hours unless you log in immediately to verify your credentials.\n\nClick link: http://secure-verify-auth.xyz/login\n\nSecurity Team',
    },
    {
      label: 'Crypto Scam Lottery Spam',
      subject: 'CONGRATULATIONS! You won 2.5 BTC Claim Prize Immediately',
      sender: 'claims@bitcoin-crypto-rewards.online',
      body: 'You have been selected as the weekly crypto bonus winner! Claim 2.5 Bitcoin rewards now before timer expires: http://crypto-claim-bonus.site',
    },
    {
      label: 'Legitimate System Notification',
      subject: '[GitHub] Security advisory alert for repository',
      sender: 'notifications@github.com',
      body: 'We detected a new security vulnerability alert in one of your repository dependencies. Visit your repository security tab for details.',
    },
  ];

  const handleInspectUrl = (urlToTest?: string) => {
    const targetUrl = urlToTest || inputUrl;
    setIsUrlAnalyzing(true);
    authFetch('/blue-team/inspect-url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: targetUrl }),
    })
      .then(r => r.json())
      .then(data => { setUrlResult(data); setIsUrlAnalyzing(false); })
      .catch(() => setIsUrlAnalyzing(false));
  };

  const handleInspectEmail = () => {
    setIsEmailAnalyzing(true);
    authFetch('/blue-team/inspect-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ subject: emailSubject, sender: emailSender, body: emailBody }),
    })
      .then(r => r.json())
      .then(data => { setEmailResult(data); setIsEmailAnalyzing(false); })
      .catch(() => setIsEmailAnalyzing(false));
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-[#F59E0B] animate-pulse" />
            <p className="section-label text-[#F59E0B]">THREAT INTEL & INDICATOR LAB</p>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight mt-1">Threat Intelligence Lab</h2>
          <p className="text-sm text-slate-400 mt-1">
            URL entropy extraction, MITRE ATT&CK mapping, and email SPF/DKIM/DMARC validation.
          </p>
        </div>

        {/* Sub-tab toggle */}
        <div className="flex items-center space-x-1 bg-[#121826] p-1 rounded-xl border border-[#F59E0B]/20">
          {[
            { id: 'url', label: 'URL Intelligence', icon: Globe },
            { id: 'email', label: 'Email Intelligence', icon: Mail },
          ].map(tab => {
            const Icon = tab.icon;
            const active = activeSubTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveSubTab(tab.id as 'url' | 'email')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                  active
                    ? 'bg-[#F59E0B] text-[#080C15] shadow-lg shadow-[#F59E0B]/20'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      <AnimatePresence mode="wait">
        {activeSubTab === 'url' ? (
          <motion.div
            key="url"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-6"
          >
            {/* URL Inspector */}
            <div className="lg:col-span-2 card p-6 space-y-5 border-[#F59E0B]/20">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Globe className="w-4 h-4 text-[#F59E0B]" />
                  <p className="text-sm font-semibold text-white">URL Phishing & Entropy Inspector</p>
                </div>
                <span className="text-xs font-mono text-slate-500">Live Indicator Extractor</span>
              </div>

              {/* Input */}
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={inputUrl}
                  onChange={e => setInputUrl(e.target.value)}
                  className="input-field font-mono text-xs flex-1 bg-[#080C14] border border-[#F59E0B]/20 text-[#00D4FF]"
                  placeholder="https://suspicious-target-url.com"
                />
                <button
                  onClick={() => handleInspectUrl()}
                  disabled={isUrlAnalyzing}
                  className="px-5 py-2.5 rounded-xl bg-[#F59E0B] hover:bg-[#D97706] text-[#080C15] font-bold text-xs flex items-center space-x-2 transition-all disabled:opacity-50 flex-shrink-0 cursor-pointer"
                >
                  <Search className="w-3.5 h-3.5" />
                  <span>{isUrlAnalyzing ? 'Extracting...' : 'Inspect URL'}</span>
                </button>
              </div>

              {/* Presets */}
              <div className="pt-3 border-t border-white/[0.06]">
                <p className="section-label mb-3">Sample URL Vectors</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {sampleUrls.map((s, idx) => (
                    <button
                      key={idx}
                      onClick={() => { setInputUrl(s.url); handleInspectUrl(s.url); }}
                      className="p-3.5 rounded-xl bg-[#1A2236] hover:bg-[#1E2A40] border border-white/[0.04] hover:border-[#F59E0B]/30 text-left transition-all space-y-1 cursor-pointer"
                    >
                      <span className="text-xs font-medium text-[#F59E0B] block">{s.label}</span>
                      <span className="text-[11px] text-slate-400 font-mono truncate block">{s.url}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Result */}
              {urlResult && (
                <div className="space-y-4 pt-4 border-t border-white/[0.06]">
                  <div className={`p-4 rounded-xl border flex items-center justify-between ${
                    urlResult.is_phishing ? 'bg-[#EF4444]/08 border-[#EF4444]/25' : 'bg-[#22C55E]/08 border-[#22C55E]/25'
                  }`}>
                    <div>
                      <span className="text-[10px] font-mono font-bold uppercase" style={{ color: urlResult.is_phishing ? '#EF4444' : '#22C55E' }}>
                        CLASSIFICATION RESULT
                      </span>
                      <h4 className={`text-base font-bold ${urlResult.is_phishing ? 'text-[#EF4444]' : 'text-[#22C55E]'}`}>
                        {urlResult.category}
                      </h4>
                      <p className="text-[11px] font-mono text-slate-500 mt-1">
                        Analyzed: {formatStandardDate(urlResult.timestamp || new Date())}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="section-label mb-1">Threat Score</p>
                      <p className="text-3xl font-extrabold text-white tabular-nums">
                        {(urlResult.threat_score * 100).toFixed(0)}
                        <span className="text-sm font-normal text-slate-500"> / 100</span>
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {[
                      { label: 'IP Host', value: urlResult.extracted_features?.has_ip_address ? 'YES' : 'NO', color: urlResult.extracted_features?.has_ip_address ? 'text-[#EF4444]' : 'text-[#22C55E]' },
                      { label: 'URL Length', value: `${urlResult.extracted_features?.url_length} chars`, color: 'text-slate-300' },
                      { label: 'SSL Status', value: urlResult.extracted_features?.is_https ? 'HTTPS' : 'HTTP', color: urlResult.extracted_features?.is_https ? 'text-[#22C55E]' : 'text-[#F59E0B]' },
                      { label: 'Brand Keywords', value: `${urlResult.extracted_features?.suspicious_keyword_count} matched`, color: 'text-[#00D4FF]' },
                    ].map(cell => (
                      <div key={cell.label} className="p-3 rounded-xl bg-[#1A2236] border border-white/[0.04] text-center">
                        <p className="section-label mb-1">{cell.label}</p>
                        <p className={`text-xs font-bold font-mono ${cell.color}`}>{cell.value}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* MITRE ATT&CK & Extracted Indicators Panel */}
            <div className="card p-6 space-y-4 border-[#F59E0B]/20">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-white">MITRE ATT&CK & CVE Mapping</p>
                <span className="text-[10px] font-mono text-[#00D4FF]">v14.1</span>
              </div>

              <div className="space-y-2.5">
                <div className="p-3 rounded-xl bg-[#1A2236] border border-white/[0.04] space-y-1">
                  <div className="flex justify-between text-xs font-mono font-bold text-[#00D4FF]">
                    <span>T1566.002</span>
                    <span>Spearphishing Link</span>
                  </div>
                  <p className="text-[11px] text-slate-400">Initial Access technique using spoofed domain links.</p>
                </div>

                <div className="p-3 rounded-xl bg-[#1A2236] border border-white/[0.04] space-y-1">
                  <div className="flex justify-between text-xs font-mono font-bold text-[#F59E0B]">
                    <span>CVE-2026-1184</span>
                    <span>SQLi RCE Vulnerability</span>
                  </div>
                  <p className="text-[11px] text-slate-400">Critical remote code execution risk rating 9.8.</p>
                </div>
              </div>

              <p className="text-sm font-semibold text-white pt-2">Extracted Threat Indicators</p>
              {urlResult ? (
                <div className="space-y-2">
                  {urlResult.indicators?.map((ind: string, idx: number) => (
                    <div key={idx} className="p-2.5 rounded-lg bg-[#1A2236] border border-white/[0.04] text-xs font-mono text-[#F59E0B]">
                      • {ind}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-500 font-mono">Inspect a URL or Email to view security indicators.</p>
              )}
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="email"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-6"
          >
            {/* Email Inspector */}
            <div className="lg:col-span-2 card p-6 space-y-4 border-[#F59E0B]/20">
              <div className="flex items-center space-x-2">
                <Mail className="w-4 h-4 text-[#F59E0B]" />
                <p className="text-sm font-semibold text-white">Email Header & Body Inspector</p>
              </div>

              <div className="space-y-3">
                {[
                  { label: 'Subject Header', value: emailSubject, onChange: setEmailSubject, type: 'input' },
                  { label: 'Sender Address', value: emailSender, onChange: setEmailSender, type: 'input' },
                ].map(field => (
                  <div key={field.label}>
                    <label className="section-label mb-1.5 block">{field.label}</label>
                    <input
                      type="text"
                      value={field.value}
                      onChange={e => field.onChange(e.target.value)}
                      className="input-field font-mono text-xs bg-[#080C14] border border-white/[0.08]"
                    />
                  </div>
                ))}
                <div>
                  <label className="section-label mb-1.5 block">Email Body Content</label>
                  <textarea
                    value={emailBody}
                    onChange={e => setEmailBody(e.target.value)}
                    rows={6}
                    className="input-field font-mono text-xs leading-relaxed resize-none bg-[#080C14] border border-white/[0.08]"
                  />
                </div>
                <button
                  onClick={handleInspectEmail}
                  disabled={isEmailAnalyzing}
                  className="w-full py-3 rounded-xl bg-[#F59E0B] hover:bg-[#D97706] text-[#080C15] font-bold text-xs flex items-center justify-center space-x-2 transition-all disabled:opacity-50 cursor-pointer"
                >
                  <Mail className="w-4 h-4" />
                  <span>{isEmailAnalyzing ? 'Analyzing Email Headers...' : 'Inspect Email with AI Model'}</span>
                </button>
              </div>

              {/* Presets */}
              <div className="pt-4 border-t border-white/[0.06]">
                <p className="section-label mb-3">Preset Attack Scenarios</p>
                <div className="space-y-2">
                  {sampleEmails.map((se, idx) => (
                    <button
                      key={idx}
                      onClick={() => { setEmailSubject(se.subject); setEmailSender(se.sender); setEmailBody(se.body); }}
                      className="w-full p-3.5 rounded-xl bg-[#1A2236] hover:bg-[#1E2A40] border border-white/[0.04] hover:border-[#F59E0B]/30 text-left transition-all flex items-center justify-between cursor-pointer"
                    >
                      <div>
                        <span className="text-xs font-medium text-[#F59E0B] block">{se.label}</span>
                        <span className="text-[11px] text-slate-400 font-mono truncate">{se.subject}</span>
                      </div>
                      <ArrowRight className="w-4 h-4 text-slate-500 flex-shrink-0" />
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Email AI Scorecard with SPF / DKIM / DMARC */}
            <div className="card p-6 space-y-5 border-[#F59E0B]/20">
              <p className="text-sm font-semibold text-white">Email AI Scorecard & Authentication</p>
              {emailResult ? (
                <div className="space-y-4">
                  <div className={`p-4 rounded-xl border flex items-center justify-between ${
                    emailResult.is_spam ? 'bg-[#EF4444]/08 border-[#EF4444]/25' : 'bg-[#22C55E]/08 border-[#22C55E]/25'
                  }`}>
                    <div>
                      <span className="text-[10px] font-mono font-bold uppercase" style={{ color: emailResult.is_spam ? '#EF4444' : '#22C55E' }}>
                        CLASSIFICATION
                      </span>
                      <h4 className={`text-base font-bold ${emailResult.is_spam ? 'text-[#EF4444]' : 'text-[#22C55E]'}`}>
                        {emailResult.category}
                      </h4>
                      <p className="text-[11px] font-mono text-slate-500 mt-1">
                        Inspected: {formatStandardDate(emailResult.timestamp || new Date())}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="section-label mb-1">Risk Score</p>
                      <p className="text-2xl font-extrabold text-white tabular-nums">
                        {(emailResult.threat_score * 100).toFixed(0)}
                        <span className="text-sm font-normal text-slate-500"> / 100</span>
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-center">
                    {[
                      { label: 'SPF', value: emailResult.spf_status, color: emailResult.spf_status === 'FAIL' ? 'text-[#EF4444]' : 'text-[#22C55E]' },
                      { label: 'DKIM', value: emailResult.dkim_status, color: emailResult.dkim_status === 'FAIL' ? 'text-[#EF4444]' : 'text-[#22C55E]' },
                      { label: 'DMARC', value: emailResult.dmarc_status, color: emailResult.dmarc_status === 'REJECT' ? 'text-[#EF4444]' : 'text-[#22C55E]' },
                    ].map(cell => (
                      <div key={cell.label} className="p-3 rounded-xl bg-[#1A2236] border border-white/[0.04]">
                        <p className="section-label mb-1">{cell.label}</p>
                        <p className={`text-xs font-bold font-mono ${cell.color}`}>{cell.value}</p>
                      </div>
                    ))}
                  </div>

                  <div className="space-y-2">
                    <p className="section-label">Threat Signals</p>
                    {emailResult.indicators?.map((ind: string, idx: number) => (
                      <div key={idx} className="p-2.5 rounded-lg bg-[#1A2236] border border-white/[0.04] text-xs font-mono text-[#F59E0B]">
                        • {ind}
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-64 text-slate-500 space-y-3">
                  <Mail className="w-10 h-10 text-[#F59E0B] animate-pulse" />
                  <p className="text-xs font-mono text-center max-w-xs">
                    Submit email subject, sender, or preset vector to trigger header authentication & AI score.
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

'use client';

import React, { useState } from 'react';
import { Sparkles, Send, X, Bot } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = 'http://localhost:8000/api/v1';

async function authFetch(path: string, init: RequestInit = {}) {
  const token = sessionStorage.getItem('rb_auth_token');
  const headers = { ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(init.headers || {}) };
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  return response;
}

interface Message {
  sender: 'user' | 'bot';
  text: string;
}

interface AiCopilotProps {
  setActiveTab: (tab: string) => void;
}

export const AiCopilot: React.FC<AiCopilotProps> = ({ setActiveTab }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [inputMsg, setInputMsg] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: 'bot',
      text: 'Sentinel Assistant Active. I am grounded in live SentinelX telemetry — ask me to summarize the latest incident, check system status, or explain model attributions.',
    },
  ]);

  const quickPrompts = [
    { label: 'Summarize Latest Incident', action: 'incident' },
    { label: 'Check System & ML Status', action: 'status' },
    { label: 'Open Defense Center', action: 'nav-blue' },
  ];

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || inputMsg;
    if (!text.trim()) return;

    setMessages(prev => [...prev, { sender: 'user', text }]);
    setInputMsg('');

    const lower = text.toLowerCase();
    let botResponse = '';

    try {
      if (lower.includes('incident') || lower.includes('latest') || lower.includes('summarize')) {
        const res = await authFetch('/attacks/');
        if (res.ok) {
          const attacks = await res.json();
          if (attacks.length > 0) {
            const latest = attacks[0];
            botResponse = `LATEST INCIDENT SUMMARY:\n• Attack ID: ${latest.id}\n• Vector Type: ${latest.attack_type}\n• Severity Level: ${latest.severity}\n• Target: ${latest.target || 'Internal SOC Endpoint'}\n• Status: ${latest.status.toUpperCase()}`;
          } else {
            botResponse = 'No attack incidents found in database. Run a simulation in Attack Center to generate telemetry.';
          }
        } else {
          botResponse = 'Unable to connect to PostgreSQL database to retrieve latest incident summary.';
        }
      } else if (lower.includes('status') || lower.includes('system') || lower.includes('health') || lower.includes('benchmark')) {
        const res = await authFetch('/ml-engine/benchmarks');
        if (res.ok) {
          const bench = await res.json();
          const modelsCount = Object.keys(bench).length;
          botResponse = `SYSTEM & ENGINE STATUS:\n• Backend FastAPI: ONLINE (127.0.0.1:8000)\n• Active ML Models: ${modelsCount} (XGBoost, Random Forest, LightGBM, Isolation Forest)\n• Leakage-Free CV Accuracy: 75.4% Mean ± 11.7%`;
        } else {
          botResponse = 'FastAPI backend service is offline or unreachable.';
        }
      } else if (lower.includes('explain') || lower.includes('shap') || lower.includes('attribution')) {
        botResponse = 'SHAP Attribution Matrix computes top feature drivers (e.g. sqli_keyword_entropy, special_char_ratio, payload_length) for every live classification decision. Opening AI Explainability Matrix...';
        setActiveTab('explainability');
      } else if (lower.includes('attack') || lower.includes('red team')) {
        botResponse = 'Navigating to Attack Center. You can execute adversarial simulation playbooks across 15+ threat vectors.';
        setActiveTab('red-team');
      } else if (lower.includes('defense') || lower.includes('blue team')) {
        botResponse = 'Navigating to Defense Center. Live model classification matrix and automated WAF mitigation rules active.';
        setActiveTab('blue-team');
      } else {
        const res = await authFetch('/dashboard/metrics');
        if (res.ok) {
          const metrics = await res.json();
          botResponse = `SENTINEL ASSISTANT TELEMETRY REPORT:\n• Query: "${text}"\n• Analyzed Attacks: ${metrics.total_threats_analyzed}\n• Detected Threats: ${metrics.threats_detected}\n• Mitigated Threats: ${metrics.threats_blocked}\n• System Health: ${metrics.system_health}`;
        } else {
          botResponse = `Query "${text}" received. Backend API connection error.`;
        }
      }
    } catch (err) {
      botResponse = 'Error querying backend telemetry. Ensure FastAPI server is running on http://127.0.0.1:8000.';
    }

    setMessages(prev => [...prev, { sender: 'bot', text: botResponse }]);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 12, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 12, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="mb-4 w-80 sm:w-96 bg-[var(--bg-card)] border border-[var(--border-hover)] rounded-2xl shadow-2xl overflow-hidden flex flex-col h-[420px]"
          >
            {/* Header */}
            <div className="p-4 border-b border-[var(--border)] bg-[var(--bg-surface)] flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <div className="w-7 h-7 rounded-lg bg-[var(--purple)]/15 border border-[var(--purple)]/30 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-[var(--purple)]" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[var(--text-primary)]">Sentinel Assistant</h4>
                  <span className="text-[10px] font-mono text-[#22C55E]">● Grounded in Real Telemetry</span>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Chat Body */}
            <div className="flex-1 p-4 overflow-y-auto space-y-3 font-sans text-xs">
              {messages.map((m, idx) => (
                <div
                  key={idx}
                  className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] p-3 rounded-xl leading-relaxed whitespace-pre-wrap ${
                      m.sender === 'user'
                        ? 'bg-[var(--accent)] text-[#080C15] font-semibold'
                        : 'bg-[var(--bg-surface)] text-[var(--text-primary)] border border-[var(--border)] font-mono text-[11px]'
                    }`}
                  >
                    {m.text}
                  </div>
                </div>
              ))}
            </div>

            {/* Quick Prompts */}
            <div className="px-3 py-2 border-t border-[var(--border)] bg-[var(--bg-surface)]/50 flex space-x-1.5 overflow-x-auto">
              {quickPrompts.map(p => (
                <button
                  key={p.label}
                  onClick={() => handleSend(p.label)}
                  className="px-2.5 py-1 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] text-[10px] font-mono text-slate-300 hover:text-white transition-colors whitespace-nowrap cursor-pointer border border-white/[0.06]"
                >
                  {p.label}
                </button>
              ))}
            </div>

            {/* Input Box */}
            <div className="p-3 border-t border-[var(--border)] bg-[var(--bg-surface)] flex items-center space-x-2">
              <input
                type="text"
                value={inputMsg}
                onChange={e => setInputMsg(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                placeholder="Ask Sentinel Assistant..."
                className="flex-1 bg-[var(--bg-card)] border border-[var(--border)] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-[var(--accent)] font-mono"
              />
              <button
                onClick={() => handleSend()}
                className="p-2 rounded-xl bg-[var(--accent)] text-[#080C15] hover:brightness-110 transition-all cursor-pointer"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Trigger Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-4 py-3 rounded-2xl bg-[var(--purple)] text-[#080C15] font-bold text-xs shadow-xl shadow-[var(--purple)]/20 cursor-pointer"
      >
        <Sparkles className="w-4 h-4 fill-current" />
        <span>Sentinel Assistant</span>
      </motion.button>
    </div>
  );
};

import React from 'react';
import { Shield, Flame, Activity, Brain, Cpu, Mail, Lock, ArrowRight, CheckCircle2, Zap, Radio } from 'lucide-react';
import { Footer } from '@/components/layout/Footer';

interface LandingPageProps {
  onGetStarted: () => void;
  onOpenLogin: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onGetStarted, onOpenLogin }) => {
  return (
    <div className="min-h-screen bg-[#090B10] text-slate-100 flex flex-col justify-between selection:bg-[#00D4FF]/20 selection:text-cyan-200 min-w-[1280px]">
      {/* Header Bar */}
      <header className="px-10 py-4 flex items-center justify-between border-b border-white/[0.08] bg-[#090B10]/90 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-[#00D4FF]/10 border border-[#00D4FF]/30 text-[#00D4FF]">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight text-white">
                Sentinel<span className="text-[#00D4FF]">X</span> AI
              </h1>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-[#00D4FF]/10 text-[#00D4FF] border border-[#00D4FF]/20 font-semibold">
                v1.0
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono tracking-wide">ENTERPRISE SOC THREAT SIMULATION & AI PLATFORM</p>
          </div>
        </div>

        <div className="flex items-center space-x-4 font-mono text-xs">
          <button
            onClick={onOpenLogin}
            className="px-5 py-2.5 rounded-xl border border-white/[0.08] hover:border-white/[0.2] text-slate-300 hover:text-white transition-all font-medium"
          >
            Sign In / Register
          </button>
          <button
            onClick={onGetStarted}
            className="px-6 py-2.5 rounded-xl bg-[#00D4FF] hover:bg-[#00D4FF]/90 text-slate-950 font-bold shadow-md flex items-center space-x-2 transition-all"
          >
            <span>Launch Console</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="px-10 py-20 max-w-[1400px] mx-auto text-center space-y-8 my-auto">
        <div className="inline-flex items-center space-x-2.5 px-4 py-1.5 rounded-full bg-[#00D4FF]/10 border border-[#00D4FF]/20 text-[#00D4FF] text-xs font-mono">
          <Radio className="w-3.5 h-3.5 text-[#00D4FF] animate-pulse" />
          <span>ENTERPRISE SOC AI THREAT PLATFORM</span>
        </div>

        <h1 className="text-5xl lg:text-7xl font-extrabold tracking-tight leading-tight max-w-5xl mx-auto text-white">
          Autonomous Adversary Simulation & Real-Time AI Threat Detection with{' '}
          <span className="text-[#FF5D73]">Red Team</span> vs{' '}
          <span className="text-[#00D4FF]">Blue Team</span> Architecture
        </h1>

        <p className="text-sm text-slate-400 max-w-3xl mx-auto leading-relaxed font-mono">
          An enterprise-grade cybersecurity console combining automated adversarial vector playbooks with real-time ML detection models, 5-fold cross-validation benchmarks, and SHAP Explainable AI feature attribution.
        </p>

        <div className="flex items-center justify-center space-x-5 pt-4 font-mono">
          <button
            onClick={onGetStarted}
            className="px-8 py-4 rounded-xl bg-[#00D4FF] hover:bg-[#00D4FF]/90 text-slate-950 font-extrabold text-sm shadow-xl flex items-center space-x-2 transition-all"
          >
            <span>ENTER SOC DASHBOARD</span>
            <ArrowRight className="w-5 h-5" />
          </button>
          <button
            onClick={onOpenLogin}
            className="px-8 py-4 rounded-xl bg-[#161B22] border border-white/[0.08] hover:border-white/[0.2] text-slate-200 font-bold text-sm transition-all"
          >
            AUTHENTICATE PORTAL
          </button>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-16 text-left">
          {/* Card 1: Red Team */}
          <div className="glass-panel p-8 rounded-2xl border border-white/[0.08] space-y-4 hover:border-[#FF5D73]/40 transition-all">
            <div className="p-3 rounded-xl bg-[#FF5D73]/10 text-[#FF5D73] border border-[#FF5D73]/20 w-fit">
              <Flame className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">Red Team Adversary Simulator</h3>
            <p className="text-xs text-slate-400 leading-relaxed font-mono">
              Safely inject adversarial vectors across SQL Injection, Phishing Emails, XSS, DDoS, Command Injection, and Prompt Injection playbooks with real-time execution logs.
            </p>
          </div>

          {/* Card 2: Blue Team */}
          <div className="glass-panel p-8 rounded-2xl border border-white/[0.08] space-y-4 hover:border-[#00D4FF]/40 transition-all">
            <div className="p-3 rounded-xl bg-[#00D4FF]/10 text-[#00D4FF] border border-[#00D4FF]/20 w-fit">
              <Shield className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">Blue Team AI Inspector</h3>
            <p className="text-xs text-slate-400 leading-relaxed font-mono">
              Real-time payload classification, risk score calculation, matched indicator extraction, and automated Blue Team mitigation rule generation.
            </p>
          </div>

          {/* Card 3: XAI & Benchmarks */}
          <div className="glass-panel p-8 rounded-2xl border border-white/[0.08] space-y-4 hover:border-purple-500/40 transition-all">
            <div className="p-3 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20 w-fit">
              <Brain className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">ML Benchmarks & SHAP XAI</h3>
            <p className="text-xs text-slate-400 leading-relaxed font-mono">
              Benchmark Random Forest, LightGBM, and XGBoost models with SHAP feature weight visualizations and certified human-readable decision summaries.
            </p>
          </div>
        </div>
      </section>

      {/* Development Team & Enterprise Footer */}
      <Footer onNavigate={() => onOpenLogin()} />
    </div>
  );
};

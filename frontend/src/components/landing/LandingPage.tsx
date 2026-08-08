import React from 'react';
import { Shield, Flame, Activity, Brain, Cpu, Mail, Lock, ArrowRight, CheckCircle2, Zap } from 'lucide-react';

interface LandingPageProps {
  onGetStarted: () => void;
  onOpenLogin: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onGetStarted, onOpenLogin }) => {
  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col justify-between selection:bg-cyan-500 selection:text-black min-w-[1280px]">
      {/* Desktop Header Bar */}
      <header className="px-10 py-6 flex items-center justify-between border-b border-slate-800/80 glass-panel sticky top-0 z-40">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 glow-blue">
            <Shield className="w-7 h-7 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold tracking-wider gradient-text-blue">
              CYBER-AI DISRUPT
            </h1>
            <p className="text-xs text-slate-400 uppercase tracking-widest font-mono">Red Team vs Blue Team Framework</p>
          </div>
        </div>

        <div className="flex items-center space-x-4 font-mono text-xs">
          <button
            onClick={onOpenLogin}
            className="px-6 py-3 rounded-xl border border-slate-700 hover:border-cyan-500 text-slate-300 hover:text-white transition-all font-medium"
          >
            Sign In / Register
          </button>
          <button
            onClick={onGetStarted}
            className="px-7 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-400 hover:to-purple-500 text-white font-semibold shadow-lg glow-blue flex items-center space-x-2 transition-all"
          >
            <span>Launch Desktop Console</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Desktop Hero Section */}
      <section className="px-10 py-24 max-w-[1400px] mx-auto text-center space-y-10 my-auto">
        <div className="inline-flex items-center space-x-2 px-5 py-2 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono">
          <Zap className="w-4 h-4 text-cyan-400 animate-pulse" />
          <span>FINAL YEAR ENGINEERING PROJECT • AI CYBER SECURITY PLATFORM</span>
        </div>

        <h1 className="text-5xl lg:text-7xl font-extrabold tracking-tight leading-tight max-w-5xl mx-auto">
          AI-Driven Threat Simulation & Real-Time Defense using{' '}
          <span className="gradient-text-blue">Red Team</span> vs{' '}
          <span className="gradient-text-red">Blue Team</span> Framework
        </h1>

        <p className="text-lg text-slate-400 max-w-3xl mx-auto leading-relaxed font-mono">
          An enterprise-grade desktop cybersecurity console combining 15+ safe adversarial attack vector simulations with real-time AI detection models, dataset training, and Explainable AI (SHAP & LIME) feature attribution.
        </p>

        <div className="flex items-center justify-center space-x-6 pt-4">
          <button
            onClick={onGetStarted}
            className="px-10 py-5 rounded-2xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-extrabold text-base font-mono shadow-2xl glow-blue flex items-center space-x-3 transition-all"
          >
            <span>GET STARTED NOW</span>
            <ArrowRight className="w-6 h-6" />
          </button>
          <button
            onClick={onOpenLogin}
            className="px-10 py-5 rounded-2xl glass-panel border border-slate-700 hover:border-slate-500 text-slate-200 font-bold text-base font-mono transition-all"
          >
            LOGIN TO DASHBOARD
          </button>
        </div>

        {/* Highlight Cards Grid for Desktop */}
        <div className="grid grid-cols-3 gap-8 pt-20 text-left">
          <div className="glass-panel p-8 rounded-3xl border border-rose-500/20 glow-red space-y-4">
            <div className="p-3.5 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-400 w-fit">
              <Flame className="w-7 h-7" />
            </div>
            <h3 className="text-xl font-bold text-white font-mono">Red Team Simulator</h3>
            <p className="text-xs text-slate-400 leading-relaxed font-mono">
              Safely inject 15+ adversarial vectors (Phishing Emails, SQLi, XSS, DDoS, Command Injection, Ransomware, Prompt Injection) in memory.
            </p>
          </div>

          <div className="glass-panel p-8 rounded-3xl border border-cyan-500/20 glow-blue space-y-4">
            <div className="p-3.5 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 w-fit">
              <Shield className="w-7 h-7" />
            </div>
            <h3 className="text-xl font-bold text-white font-mono">Blue Team AI Detector</h3>
            <p className="text-xs text-slate-400 leading-relaxed font-mono">
              Real-time ML payload classifier, risk score calculator, indicator extraction, and automated mitigation rule generator.
            </p>
          </div>

          <div className="glass-panel p-8 rounded-3xl border border-purple-500/20 glow-purple space-y-4">
            <div className="p-3.5 rounded-2xl bg-purple-500/10 border border-purple-500/30 text-purple-400 w-fit">
              <Brain className="w-7 h-7" />
            </div>
            <h3 className="text-xl font-bold text-white font-mono">Dataset ML & XAI</h3>
            <p className="text-xs text-slate-400 leading-relaxed font-mono">
              Train Scikit-Learn, LightGBM, and XGBoost models on CICIDS2017 & Phishing datasets with SHAP feature weight visualizations.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-10 py-6 border-t border-slate-800/80 text-center text-xs font-mono text-slate-500">
        © 2026 AI-Driven Cyber Threat Simulation & Detection Platform • Red Team vs Blue Team
      </footer>
    </div>
  );
};

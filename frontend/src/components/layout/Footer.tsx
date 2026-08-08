import React from 'react';
import { Shield, Github, ExternalLink, BookOpen } from 'lucide-react';

interface FooterProps {
  onNavigate?: (tab: string) => void;
}

export const Footer: React.FC<FooterProps> = ({ onNavigate }) => {
  return (
    <footer className="mt-16 border-t border-white/[0.08] bg-[#090B10]/95 pt-10 pb-8 text-slate-300 font-sans">
      <div className="max-w-[1600px] mx-auto px-6 space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Col 1: Branding & License */}
          <div className="space-y-3 md:col-span-1">
            <div className="flex items-center space-x-2.5">
              <div className="p-2 rounded-xl bg-[#00D4FF]/10 text-[#00D4FF] border border-[#00D4FF]/30">
                <Shield className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white tracking-tight">
                  Sentinel<span className="text-[#00D4FF]">X</span> AI
                </h3>
                <p className="text-[10px] font-mono text-slate-400 uppercase tracking-widest">Enterprise Platform</p>
              </div>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed font-mono">
              Autonomous Red Team Simulation, Blue Team AI Detection, SHAP Explainability & SOC Incident Reporting Platform.
            </p>
            <div className="flex items-center space-x-3 font-mono text-xs pt-1">
              <span className="px-2 py-0.5 rounded bg-white/[0.06] text-slate-300 border border-white/[0.08]">
                v1.0.0
              </span>
              <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                MIT License
              </span>
            </div>
          </div>

          {/* Col 2: Quick Navigation */}
          <div className="space-y-3 font-mono text-xs">
            <h4 className="text-white font-bold uppercase tracking-wider text-[11px]">Platform Navigation</h4>
            <ul className="space-y-2 text-slate-400">
              <li>
                <button onClick={() => onNavigate?.('dashboard')} className="hover:text-[#00D4FF] transition-colors">
                  Security Overview
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate?.('red-team')} className="hover:text-[#FF5D73] transition-colors">
                  Red Team Simulator
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate?.('blue-team')} className="hover:text-[#00D4FF] transition-colors">
                  Blue Team AI Inspector
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate?.('email-url-lab')} className="hover:text-[#00D4FF] transition-colors">
                  Threat Intelligence Lab
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate?.('ml-engine')} className="hover:text-[#A855F7] transition-colors">
                  ML Benchmarks
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate?.('explainability')} className="hover:text-[#A855F7] transition-colors">
                  Explainable AI (XAI)
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate?.('about')} className="hover:text-[#00D4FF] font-bold text-white transition-colors">
                  About & Team
                </button>
              </li>
            </ul>
          </div>

          {/* Col 3: Developer & API Docs */}
          <div className="space-y-3 font-mono text-xs">
            <h4 className="text-white font-bold uppercase tracking-wider text-[11px]">Documentation & Code</h4>
            <ul className="space-y-2 text-slate-400">
              <li>
                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-[#00D4FF] transition-colors flex items-center space-x-1.5"
                >
                  <BookOpen className="w-3.5 h-3.5 text-[#00D4FF]" />
                  <span>API Documentation</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/Imchetan127/SentinelX-AI"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white transition-colors flex items-center space-x-1.5"
                >
                  <Github className="w-3.5 h-3.5 text-slate-300" />
                  <span>GitHub Repository</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <span className="text-slate-500 block">Architecture: Microservices</span>
              </li>
              <li>
                <span className="text-slate-500 block">DB: PostgreSQL / SQLite</span>
              </li>
            </ul>
          </div>

          {/* Col 4: Technology Stack & Guidance */}
          <div className="space-y-3 font-mono text-xs">
            <h4 className="text-white font-bold uppercase tracking-wider text-[11px]">Technology Stack</h4>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Built with Python, FastAPI, Next.js, Docker, PostgreSQL, SQLite, Tailwind CSS.
            </p>
            <div className="pt-1">
              <p className="text-slate-400 text-[11px] leading-relaxed font-sans border-l-2 border-[#00D4FF]/40 pl-2">
                Developed collaboratively by the SentinelX AI Team under the guidance of <span className="text-amber-300 font-semibold">Sneha Karamadi</span>.
              </p>
            </div>
          </div>
        </div>

        {/* Bottom Copyright & Attribution Bar */}
        <div className="pt-6 border-t border-white/[0.06] flex flex-col md:flex-row items-center justify-between font-mono text-xs text-slate-500 gap-4">
          <p>Copyright © 2026 SentinelX AI. All rights reserved.</p>
          <p className="text-[11px]">
            Department of Artificial Intelligence & Data Science • K.S. School of Engineering & Management
          </p>
        </div>
      </div>
    </footer>
  );
};

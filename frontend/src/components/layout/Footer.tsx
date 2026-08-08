import React from 'react';
import { Shield, Github, Linkedin, ExternalLink, Code2, Award, BookOpen, Layers } from 'lucide-react';

interface FooterProps {
  onNavigate?: (tab: string) => void;
}

export const Footer: React.FC<FooterProps> = ({ onNavigate }) => {
  const teamMembers = [
    {
      name: 'Chetan B K',
      role: 'Project Lead & Full Stack AI Developer',
      description:
        'Led the design and development of SentinelX AI, integrating AI-powered cybersecurity workflows, backend services, machine learning, explainable AI, reporting, and deployment.',
      initials: 'CB',
      github: 'https://github.com/Imchetan127',
      linkedin: 'https://linkedin.com',
      isFaculty: false,
    },
    {
      name: 'H Deepak',
      role: 'AI & Software Developer',
      description:
        'Contributed to system development, feature implementation, testing, and collaborative engineering throughout the project.',
      initials: 'HD',
      image: '/images/team/h_deepak.png',
      github: 'https://github.com',
      linkedin: 'https://linkedin.com',
      isFaculty: false,
    },
    {
      name: 'Nivas M R',
      role: 'Software Developer',
      description:
        'Contributed to frontend development, integration, application improvements, and testing.',
      initials: 'NM',
      github: 'https://github.com',
      linkedin: 'https://linkedin.com',
      isFaculty: false,
    },
    {
      name: 'Kiran D',
      role: 'Software Developer',
      description:
        'Supported feature development, debugging, quality assurance, and implementation.',
      initials: 'KD',
      image: '/images/team/kiran_d.png',
      github: 'https://github.com',
      linkedin: 'https://linkedin.com',
      isFaculty: false,
    },
    {
      name: 'Sneha Karamadi',
      role: 'Assistant Professor',
      department: 'Dept. of Artificial Intelligence & Data Science',
      institution: 'K.S. School of Engineering and Management',
      description:
        'Provided academic guidance, technical mentorship, project reviews, and continuous support throughout the development of SentinelX AI.',
      initials: 'SK',
      isFaculty: true,
    },
  ];

  return (
    <footer className="mt-20 border-t border-white/[0.08] bg-[#090B10] text-slate-300 font-sans">
      {/* 1. MEET THE DEVELOPMENT TEAM SECTION */}
      <div className="max-w-[1600px] mx-auto px-6 py-16 space-y-12">
        <div className="text-center space-y-3 max-w-3xl mx-auto">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1 rounded-full bg-[#00D4FF]/10 border border-[#00D4FF]/20 text-[#00D4FF] text-xs font-mono">
            <Award className="w-3.5 h-3.5 text-[#00D4FF]" />
            <span>PROJECT CREATORS & ACADEMIC MENTORSHIP</span>
          </div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">Meet the Development Team</h2>
          <p className="text-xs text-slate-400 font-mono leading-relaxed">
            Engineered collaboratively for final year engineering synthesis at K.S. School of Engineering and Management (Dept. of AI & Data Science).
          </p>
        </div>

        {/* 5 Profile Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {teamMembers.map((member, idx) => (
            <div
              key={idx}
              className={`p-6 rounded-2xl border flex flex-col justify-between space-y-4 transition-all duration-200 relative overflow-hidden ${
                member.isFaculty
                  ? 'bg-[#161B22]/90 border-amber-500/40 shadow-lg ring-1 ring-amber-500/20'
                  : 'bg-[#161B22]/70 border-white/[0.08] hover:border-white/[0.18]'
              }`}
            >
              {/* Faculty Ribbon Banner */}
              {member.isFaculty && (
                <div className="absolute top-0 right-0">
                  <span className="px-3 py-1 bg-amber-500/20 text-amber-300 border-b border-l border-amber-500/30 text-[10px] font-mono font-bold tracking-wider uppercase rounded-bl-xl block">
                    FACULTY GUIDE
                  </span>
                </div>
              )}

              <div className="space-y-4">
                {/* Avatar / Profile Photo */}
                <div className="flex items-center space-x-3">
                  {member.image ? (
                    <img
                      src={member.image}
                      alt={member.name}
                      className="w-12 h-12 rounded-full object-cover border border-[#00D4FF]/40 shadow-sm flex-shrink-0"
                    />
                  ) : (
                    <div
                      className={`w-12 h-12 rounded-full flex items-center justify-center font-mono font-bold text-sm border flex-shrink-0 ${
                        member.isFaculty
                          ? 'bg-amber-500/10 text-amber-300 border-amber-500/40'
                          : 'bg-[#00D4FF]/10 text-[#00D4FF] border-[#00D4FF]/30'
                      }`}
                    >
                      {member.initials}
                    </div>
                  )}
                  <div>
                    <h3 className="text-base font-bold text-white tracking-tight">{member.name}</h3>
                    <p
                      className={`text-[11px] font-mono font-semibold ${
                        member.isFaculty ? 'text-amber-300' : 'text-[#00D4FF]'
                      }`}
                    >
                      {member.role}
                    </p>
                  </div>
                </div>

                {/* Additional Institution Details for Faculty */}
                {member.isFaculty && (
                  <div className="text-[11px] font-mono text-slate-400 space-y-0.5 border-l-2 border-amber-500/40 pl-2 py-0.5">
                    <p className="text-slate-300 font-semibold">{member.department}</p>
                    <p className="text-slate-400">{member.institution}</p>
                  </div>
                )}

                {/* Professional Description */}
                <p className="text-xs text-slate-400 leading-relaxed font-sans">{member.description}</p>
              </div>

              {/* Student Links */}
              {!member.isFaculty && (member.github || member.linkedin) && (
                <div className="pt-3 border-t border-white/[0.06] flex items-center space-x-3 text-slate-400">
                  {member.github && (
                    <a
                      href={member.github}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:text-white transition-colors"
                      title="GitHub Profile"
                    >
                      <Github className="w-4 h-4" />
                    </a>
                  )}
                  {member.linkedin && (
                    <a
                      href={member.linkedin}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:text-[#00D4FF] transition-colors"
                      title="LinkedIn Profile"
                    >
                      <Linkedin className="w-4 h-4" />
                    </a>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 2. ENTERPRISE FOOTER BOTTOM */}
      <div className="border-t border-white/[0.08] bg-[#090B10]/95 pt-12 pb-8">
        <div className="max-w-[1600px] mx-auto px-6 space-y-10">
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
              Dept. of Artificial Intelligence & Data Science • K.S. School of Engineering and Management
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

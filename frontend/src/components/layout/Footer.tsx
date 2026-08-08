import React from 'react';
import { Shield, Github, Linkedin, ExternalLink, Award, BookOpen, GraduationCap } from 'lucide-react';

interface FooterProps {
  onNavigate?: (tab: string) => void;
}

export const Footer: React.FC<FooterProps> = ({ onNavigate }) => {
  const studentDevelopers = [
    {
      name: 'Chetan B K',
      role: 'Project Lead & Full Stack AI Developer',
      description:
        'Led the design and development of SentinelX AI, integrating AI-powered cybersecurity workflows, backend services, machine learning, explainable AI, reporting, and deployment.',
      initials: 'CB',
      image: '/images/team/chetan_bk.jpg',
      github: 'https://github.com/Imchetan127',
      linkedin: 'https://linkedin.com',
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
    },
    {
      name: 'Nivas M R',
      role: 'Software Developer',
      description:
        'Contributed to frontend development, integration, application improvements, and testing.',
      initials: 'NM',
      image: '/images/team/nivas_mr.jpg',
      github: 'https://github.com',
      linkedin: 'https://linkedin.com',
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
    },
  ];

  const academicMentor = {
    name: 'Sneha Karamadi',
    role: 'Assistant Professor',
    department: 'Department of Artificial Intelligence & Data Science',
    institution: 'K.S. School of Engineering & Management',
    description:
      'Provided academic mentorship, technical guidance, project reviews, and continuous support throughout the design and development of SentinelX AI.',
    initials: 'SK',
  };

  return (
    <footer className="mt-20 border-t border-white/[0.08] bg-[#090B10] text-slate-300 font-sans">
      {/* 1. MEET THE DEVELOPMENT TEAM SECTION */}
      <div className="max-w-[1600px] mx-auto px-6 py-16 space-y-12">
        <div className="text-center space-y-3 max-w-3xl mx-auto">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1 rounded-full bg-[#00D4FF]/10 border border-[#00D4FF]/20 text-[#00D4FF] text-xs font-mono">
            <Award className="w-3.5 h-3.5 text-[#00D4FF]" />
            <span>ENGINEERING DEVELOPMENT TEAM & ACADEMIC ADVISORY</span>
          </div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">Meet the Development Team</h2>
          <p className="text-xs text-slate-400 font-mono leading-relaxed">
            Engineered collaboratively for final year engineering synthesis at K.S. School of Engineering & Management.
          </p>
        </div>

        {/* Row 1: Student Developers Grid (4 Centered Cards) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {studentDevelopers.map((member, idx) => (
            <div
              key={idx}
              className="p-6 rounded-2xl bg-[#161B22]/70 border border-white/[0.08] hover:border-white/[0.18] flex flex-col justify-between space-y-4 transition-all duration-200"
            >
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
                    <div className="w-12 h-12 rounded-full bg-[#00D4FF]/10 text-[#00D4FF] border border-[#00D4FF]/30 flex items-center justify-center font-mono font-bold text-sm flex-shrink-0">
                      {member.initials}
                    </div>
                  )}
                  <div>
                    <h3 className="text-base font-bold text-white tracking-tight">{member.name}</h3>
                    <p className="text-[11px] font-mono font-semibold text-[#00D4FF]">
                      {member.role}
                    </p>
                  </div>
                </div>

                {/* Professional Description */}
                <p className="text-xs text-slate-400 leading-relaxed font-sans">{member.description}</p>
              </div>

              {/* Student Links */}
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
            </div>
          ))}
        </div>

        {/* Subtle Divider between Development Team & Academic Mentor */}
        <div className="flex items-center justify-center py-2">
          <div className="h-[1px] bg-gradient-to-r from-transparent via-white/[0.12] to-transparent w-full max-w-xl" />
        </div>

        {/* Row 2: Centered Prestigious Academic Mentor Section */}
        <div className="flex justify-center">
          <div className="w-full max-w-2xl p-7 rounded-2xl bg-[#161B22]/90 border border-amber-500/40 shadow-xl ring-1 ring-amber-500/20 relative overflow-hidden space-y-4">
            {/* Academic Mentor Badge Banner */}
            <div className="absolute top-0 right-0">
              <span className="px-3.5 py-1 bg-amber-500/20 text-amber-300 border-b border-l border-amber-500/30 text-[10px] font-mono font-bold tracking-wider uppercase rounded-bl-xl flex items-center space-x-1">
                <GraduationCap className="w-3 h-3 text-amber-400" />
                <span>ACADEMIC MENTOR</span>
              </span>
            </div>

            <div className="flex flex-col sm:flex-row sm:items-center space-y-3 sm:space-y-0 sm:space-x-4 border-b border-white/[0.08] pb-4">
              <div className="w-14 h-14 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/40 flex items-center justify-center font-mono font-bold text-lg flex-shrink-0 shadow-sm">
                {academicMentor.initials}
              </div>
              <div className="space-y-0.5">
                <h3 className="text-xl font-bold text-white tracking-tight">{academicMentor.name}</h3>
                <p className="text-xs font-mono font-bold text-amber-300">{academicMentor.role}</p>
                <p className="text-xs font-mono text-slate-300">{academicMentor.department}</p>
                <p className="text-xs font-mono text-slate-400">{academicMentor.institution}</p>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed font-sans pt-1">
              {academicMentor.description}
            </p>
          </div>
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
              Department of Artificial Intelligence & Data Science • K.S. School of Engineering & Management
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

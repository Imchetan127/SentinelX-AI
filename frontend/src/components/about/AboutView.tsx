'use client';

import React from 'react';
import { Shield, Github, Linkedin, ExternalLink, Award, BookOpen, GraduationCap, Cpu, Layers, Server, Code2, CheckCircle2 } from 'lucide-react';

export const AboutView: React.FC = () => {
  const studentDevelopers = [
    {
      name: 'Chetan B K',
      role: 'AI Systems Engineer',
      description:
        'Designed and integrated the core AI-driven cybersecurity platform by developing backend services, connecting machine learning models, implementing Explainable AI (XAI), designing secure workflows, and ensuring seamless communication across all system modules.',
      initials: 'CB',
      image: '/images/team/chetan_bk.jpg',
      github: 'https://github.com/Imchetan127',
      linkedin: 'https://linkedin.com',
    },
    {
      name: 'H Deepak',
      role: 'Backend & AI Engineer',
      description:
        'Developed backend APIs, integrated AI components, optimized server-side functionality, implemented business logic, and collaborated on testing, debugging, and improving overall platform performance and reliability.',
      initials: 'HD',
      image: '/images/team/h_deepak.png',
      github: 'https://github.com',
      linkedin: 'https://linkedin.com',
    },
    {
      name: 'Nivas M R',
      role: 'Frontend & Integration Engineer',
      description:
        'Built responsive user interfaces, integrated frontend components with backend services, enhanced user experience, implemented interactive dashboards, and ensured smooth communication between system modules.',
      initials: 'NM',
      image: '/images/team/nivas_mr.jpg',
      github: 'https://github.com',
      linkedin: 'https://linkedin.com',
    },
    {
      name: 'Kiran D',
      role: 'Software Quality & Systems Engineer',
      description:
        'Focused on system validation, feature implementation, software testing, debugging, quality assurance, and performance optimization to ensure the stability and reliability of the SentinelX AI platform.',
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
      'Provided academic mentorship, technical guidance, architectural reviews, and continuous support throughout the planning, development, testing, and successful completion of the SentinelX AI platform.',
    initials: 'SK',
  };

  const techStack = [
    { category: 'AI & ML Engine', tech: 'Python, Scikit-Learn, XGBoost, SHAP, LIME' },
    { category: 'Backend API', tech: 'FastAPI, Uvicorn, Pydantic, SQLAlchemy' },
    { category: 'Frontend Application', tech: 'Next.js 15, React 19, Tailwind CSS, Framer Motion' },
    { category: 'Database & Security', tech: 'PostgreSQL, SQLite, JWT, Bcrypt' },
    { category: 'Deployment & DevOps', tech: 'Docker, Multi-Stage Builds, Alembic' },
  ];

  return (
    <div className="space-y-10">
      {/* 1. HEADER BANNER */}
      <div className="glass-panel p-6 rounded-2xl border border-white/[0.08] flex items-center justify-between">
        <div className="space-y-1">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-[#00D4FF]/10 text-[#00D4FF]">
              <Shield className="w-5 h-5" />
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">About SentinelX AI Platform</h2>
          </div>
          <p className="text-xs text-slate-400">
            System Specifications, Architectural Blueprint, Development Engineering Team & Academic Mentorship.
          </p>
        </div>
        <div className="hidden md:flex items-center space-x-3 font-mono text-xs">
          <span className="px-2.5 py-1 rounded-lg bg-white/[0.06] text-slate-300 border border-white/[0.08]">
            v1.0.0
          </span>
          <span className="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-[#2EE59D] border border-emerald-500/20">
            MIT License
          </span>
        </div>
      </div>

      {/* 2. PROJECT & ARCHITECTURE OVERVIEW */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-white/[0.08] space-y-4">
          <div className="flex items-center space-x-2 border-b border-white/[0.08] pb-3">
            <Layers className="w-4 h-4 text-[#00D4FF]" />
            <h3 className="text-sm font-bold text-white uppercase font-mono">Project & Architecture Overview</h3>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed font-sans">
            SentinelX AI is an enterprise-grade cybersecurity platform combining autonomous Red Team adversary simulation playbooks with real-time Blue Team machine learning threat detection models, SHAP interpretability feature attribution, and automated incident reporting.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 font-mono text-xs">
            <div className="p-3.5 rounded-xl bg-[#111827] border border-white/[0.08] space-y-1">
              <span className="text-[#00D4FF] font-bold block">Red Team Simulator</span>
              <p className="text-slate-400 text-[11px]">Safe in-memory execution of 15+ attack vectors including SQLi, Phishing, XSS, DDoS, Ransomware, and Prompt Injection.</p>
            </div>
            <div className="p-3.5 rounded-xl bg-[#111827] border border-white/[0.08] space-y-1">
              <span className="text-[#2EE59D] font-bold block">Blue Team AI Inspector</span>
              <p className="text-slate-400 text-[11px]">Real-time payload classification, risk scoring, feature extraction, and automated mitigation rule generation.</p>
            </div>
            <div className="p-3.5 rounded-xl bg-[#111827] border border-white/[0.08] space-y-1">
              <span className="text-purple-300 font-bold block">ML Benchmarks & XAI</span>
              <p className="text-slate-400 text-[11px]">5-fold cross-validation performance matrix across Random Forest, XGBoost, and SHAP decision explanations.</p>
            </div>
            <div className="p-3.5 rounded-xl bg-[#111827] border border-white/[0.08] space-y-1">
              <span className="text-[#FFB547] font-bold block">Enterprise Reporting</span>
              <p className="text-slate-400 text-[11px]">Automated PDF report generation with SHA-256 integrity verification and MITRE ATT&CK mapping.</p>
            </div>
          </div>
        </div>

        {/* Tech Stack Summary Card */}
        <div className="glass-panel p-6 rounded-2xl border border-white/[0.08] space-y-4">
          <div className="flex items-center space-x-2 border-b border-white/[0.08] pb-3">
            <Cpu className="w-4 h-4 text-[#00D4FF]" />
            <h3 className="text-sm font-bold text-white uppercase font-mono">Technology Stack</h3>
          </div>

          <div className="space-y-3 font-mono text-xs">
            {techStack.map((item, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-[#111827] border border-white/[0.08] space-y-1">
                <span className="text-slate-400 text-[10px] uppercase font-bold">{item.category}</span>
                <p className="text-slate-200 font-bold text-[11px]">{item.tech}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 3. MEET THE ENGINEERING TEAM SECTION */}
      <div className="space-y-6 pt-4">
        <div className="text-center space-y-2 max-w-3xl mx-auto">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1 rounded-full bg-[#00D4FF]/10 border border-[#00D4FF]/20 text-[#00D4FF] text-xs font-mono">
            <Award className="w-3.5 h-3.5 text-[#00D4FF]" />
            <span>ENGINEERING DEVELOPMENT TEAM</span>
          </div>
          <h3 className="text-2xl font-extrabold text-white tracking-tight">Meet the Engineering Team</h3>
          <p className="text-xs text-slate-400 font-mono leading-relaxed">
            Engineered collaboratively for final year engineering synthesis at K.S. School of Engineering & Management.
          </p>
        </div>

        {/* 4 Student Developers Grid (Single Centered Row) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {studentDevelopers.map((member, idx) => (
            <div
              key={idx}
              className="p-6 rounded-2xl bg-[#161B22]/80 border border-white/[0.08] hover:border-white/[0.18] flex flex-col justify-between space-y-4 transition-all duration-200"
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
                    <h4 className="text-base font-bold text-white tracking-tight">{member.name}</h4>
                    <p className="text-[11px] font-mono font-semibold text-[#00D4FF]">
                      {member.role}
                    </p>
                  </div>
                </div>

                {/* Professional Description */}
                <p className="text-xs text-slate-400 leading-relaxed font-sans">{member.description}</p>
              </div>

              {/* Student Links */}
              <div className="pt-3 border-t border-white/[0.06] flex items-center space-x-3 text-slate-400 font-mono text-xs">
                {member.github && (
                  <a
                    href={member.github}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-white transition-colors flex items-center space-x-1"
                    title="GitHub Profile"
                  >
                    <Github className="w-3.5 h-3.5" />
                  </a>
                )}
                {member.linkedin && (
                  <a
                    href={member.linkedin}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-[#00D4FF] transition-colors flex items-center space-x-1"
                    title="LinkedIn Profile"
                  >
                    <Linkedin className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Subtle Divider */}
      <div className="flex items-center justify-center py-2">
        <div className="h-[1px] bg-gradient-to-r from-transparent via-white/[0.12] to-transparent w-full max-w-xl" />
      </div>

      {/* 4. ACADEMIC MENTOR SECTION */}
      <div className="flex justify-center pb-6">
        <div className="w-full max-w-2xl p-7 rounded-2xl bg-[#161B22]/90 border border-amber-500/40 shadow-xl ring-1 ring-amber-500/20 relative overflow-hidden space-y-4">
          {/* Academic Mentor Ribbon */}
          <div className="absolute top-0 right-0">
            <span className="px-3.5 py-1 bg-amber-500/20 text-amber-300 border-b border-l border-amber-500/30 text-[10px] font-mono font-bold tracking-wider uppercase rounded-bl-xl flex items-center space-x-1">
              <GraduationCap className="w-3.5 h-3.5 text-amber-400" />
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
  );
};

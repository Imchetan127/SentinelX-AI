'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
  ArrowRight, Shield, Zap, Eye, FileText, Brain, Globe,
  ChevronRight, CheckCircle2, X, Activity, BarChart3,
  Lock, Radio, Cpu, Layers, Play, Terminal, Database,
  Server, GitBranch, AlertTriangle, TrendingUp, Sparkles,
  ChevronDown, ExternalLink, Github, Clock, Users,
  Award, Flame, GraduationCap, Linkedin, Instagram, Star
} from 'lucide-react';
import {
  motion, useScroll, useTransform, AnimatePresence,
  useInView, useMotionValue, useSpring, useReducedMotion
} from 'framer-motion';

interface LandingPageProps {
  onGetStarted: () => void;
  onOpenLogin: () => void;
  onNavigateAbout?: () => void;
}

// ─────────────────────────────────────────────────────────────
// DATA
// ─────────────────────────────────────────────────────────────

const TICKER_ITEMS = [
  { event: 'SQL Injection Detected', status: 'BLOCKED', severity: 'critical' },
  { event: 'Phishing Email Analyzed', status: 'HIGH RISK', severity: 'high' },
  { event: 'Prompt Injection Attempt', status: 'BLOCKED', severity: 'critical' },
  { event: 'AI Confidence Score', status: '81.6%', severity: 'safe' },
  { event: 'XSS Payload Neutralized', status: 'BLOCKED', severity: 'critical' },
  { event: 'Threat Report Generated', status: 'COMPLETE', severity: 'safe' },
  { event: 'SHAP Attribution Computed', status: 'CERTIFIED', severity: 'safe' },
  { event: 'DDoS Simulation Complete', status: 'ANALYZED', severity: 'high' },
  { event: 'Command Injection Blocked', status: 'BLOCKED', severity: 'critical' },
  { event: 'URL Entropy Score', status: '0.91', severity: 'high' },
  { event: 'SPF Validation Failed', status: 'FLAGGED', severity: 'high' },
  { event: 'Model Retrained', status: 'VERIFIED', severity: 'safe' },
];

const STATS = [
  { value: 81.6, suffix: '%', label: 'Detection Accuracy', sub: 'Leakage-free 5-fold cross-validation' },
  { value: 99.3, suffix: '%', label: 'Mitigation Rate', sub: 'Automated response success' },
  { value: 12000, suffix: '+', label: 'Threat Simulations', sub: 'Adversarial playbooks run' },
  { value: 24, suffix: '/7', label: 'SOC Monitoring', sub: 'Continuous defense uptime' },
];

const BENTO_FEATURES = [
  {
    id: 'attack',
    size: 'large',
    title: 'Attack Simulation Center',
    desc: 'Execute 15+ adversarial playbooks — SQL Injection, Phishing, XSS, DDoS, Command Injection, and Prompt Injection — safely in-memory with real-time execution logs.',
    icon: Zap,
    color: '#EF4444',
    bg: 'rgba(239,68,68,0.06)',
    border: 'rgba(239,68,68,0.14)',
    accent: 'rgba(239,68,68,0.08)',
    badge: 'RED TEAM',
  },
  {
    id: 'threat-intel',
    size: 'medium',
    title: 'Threat Intelligence Lab',
    desc: 'URL entropy extraction, SPF/DKIM/DMARC validation, and email phishing analysis with per-feature risk scoring.',
    icon: Globe,
    color: '#00D4FF',
    bg: 'rgba(0,212,255,0.04)',
    border: 'rgba(0,212,255,0.12)',
    accent: 'rgba(0,212,255,0.06)',
    badge: 'INTEL',
  },
  {
    id: 'investigation',
    size: 'medium',
    title: 'Threat Investigation Center',
    desc: 'Real-time payload classification using Random Forest, XGBoost, and Isolation Forest models with risk index output.',
    icon: Shield,
    color: '#00D4FF',
    bg: 'rgba(0,212,255,0.04)',
    border: 'rgba(0,212,255,0.12)',
    accent: 'rgba(0,212,255,0.06)',
    badge: 'BLUE TEAM',
  },
  {
    id: 'reports',
    size: 'small',
    title: 'Executive Reports',
    desc: 'Automated PDF reports with SHA-256 integrity and MITRE ATT&CK mapping.',
    icon: FileText,
    color: '#22C55E',
    bg: 'rgba(34,197,94,0.04)',
    border: 'rgba(34,197,94,0.12)',
    accent: 'rgba(34,197,94,0.06)',
    badge: 'REPORTS',
  },
  {
    id: 'ml',
    size: 'small',
    title: 'Model Performance',
    desc: '5-fold cross-validation benchmarks with confusion matrices and feature importance rankings.',
    icon: BarChart3,
    color: '#A78BFA',
    bg: 'rgba(167,139,250,0.04)',
    border: 'rgba(167,139,250,0.12)',
    accent: 'rgba(167,139,250,0.06)',
    badge: 'ML ENGINE',
  },
  {
    id: 'xai',
    size: 'large',
    title: 'AI Explainability Center',
    desc: 'SHAP and LIME attribution demystifies every neural network and tree model decision. Human-readable summaries, audit-certified, with visual feature weight bars.',
    icon: Brain,
    color: '#A78BFA',
    bg: 'rgba(167,139,250,0.05)',
    border: 'rgba(167,139,250,0.15)',
    accent: 'rgba(167,139,250,0.08)',
    badge: 'SHAP / LIME',
  },
];

const WORKFLOW_STEPS = [
  { label: 'Attack Vector', icon: Zap, color: '#EF4444', desc: 'Adversarial payload injected' },
  { label: 'AI Detection', icon: Cpu, color: '#F59E0B', desc: 'ML pipeline classifies threat' },
  { label: 'Threat Intel', icon: Globe, color: '#00D4FF', desc: 'Indicators extracted & scored' },
  { label: 'Explainable AI', icon: Brain, color: '#A78BFA', desc: 'SHAP attribution generated' },
  { label: 'Incident Report', icon: FileText, color: '#22C55E', desc: 'PDF generated & signed' },
  { label: 'SOC Dashboard', icon: Activity, color: '#00D4FF', desc: 'Executive metrics updated' },
];

const ARCH_LAYERS = [
  { label: 'Security Analyst', icon: Users, color: '#00D4FF' },
  { label: 'Next.js Frontend', icon: Layers, color: '#F8FAFC' },
  { label: 'FastAPI Backend', icon: Server, color: '#22C55E' },
  { label: 'JWT Authentication', icon: Lock, color: '#F59E0B' },
  { label: 'ML Engine (XGBoost · RF · SHAP)', icon: Brain, color: '#A78BFA' },
  { label: 'SQLite / PostgreSQL', icon: Database, color: '#3B82F6' },
  { label: 'SOC Dashboard', icon: Activity, color: '#00D4FF' },
];

const TECH = [
  { name: 'Python', color: '#3B82F6' },
  { name: 'FastAPI', color: '#22C55E' },
  { name: 'Next.js', color: '#F8FAFC' },
  { name: 'React', color: '#00D4FF' },
  { name: 'Docker', color: '#3B82F6' },
  { name: 'PostgreSQL', color: '#336791' },
  { name: 'SQLite', color: '#00D4FF' },
  { name: 'XGBoost', color: '#F59E0B' },
  { name: 'Random Forest', color: '#22C55E' },
  { name: 'SHAP', color: '#A78BFA' },
  { name: 'Tailwind CSS', color: '#00D4FF' },
  { name: 'JWT', color: '#EF4444' },
];

const ORBIT_NODES = [
  { label: 'Attack Sim', angle: -90, color: '#EF4444', icon: Zap },
  { label: 'Threat Intel', angle: -30, color: '#00D4FF', icon: Globe },
  { label: 'Investigation', angle: 30, color: '#00D4FF', icon: Shield },
  { label: 'ML Engine', angle: 90, color: '#A78BFA', icon: BarChart3 },
  { label: 'XAI', angle: 150, color: '#A78BFA', icon: Brain },
  { label: 'Reports', angle: 210, color: '#22C55E', icon: FileText },
];

const MOCK_SCREENSHOTS = [
  { label: 'SOC Dashboard', tag: 'Overview', color: '#00D4FF' },
  { label: 'Attack Simulation', tag: 'Red Team', color: '#EF4444' },
  { label: 'Threat Investigation', tag: 'Blue Team', color: '#00D4FF' },
  { label: 'Threat Intelligence', tag: 'Intel Lab', color: '#F59E0B' },
  { label: 'AI Explainability', tag: 'SHAP', color: '#A78BFA' },
  { label: 'Executive Reports', tag: 'Reports', color: '#22C55E' },
];

// ─────────────────────────────────────────────────────────────
// ANIMATED COUNTER
// ─────────────────────────────────────────────────────────────
function Counter({ target, suffix }: { target: number; suffix: string }) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: '-60px' });

  useEffect(() => {
    if (!inView) return;
    const dur = 2200;
    const start = Date.now();
    const step = () => {
      const t = Math.min((Date.now() - start) / dur, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      const val = eased * target;
      setCount(target % 1 !== 0 ? parseFloat(val.toFixed(1)) : Math.round(val));
      if (t < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [inView, target]);

  return (
    <span ref={ref} className="tabular-nums">
      {target % 1 !== 0 ? count.toFixed(1) : count.toLocaleString()}
      {suffix}
    </span>
  );
}

// ─────────────────────────────────────────────────────────────
// PARTICLE CANVAS
// ─────────────────────────────────────────────────────────────
function ParticleCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    let raf: number;

    const pts: Array<{ x: number; y: number; vx: number; vy: number; a: number; r: number }> = [];
    const resize = () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight; };
    resize();
    window.addEventListener('resize', resize);

    for (let i = 0; i < 70; i++) {
      pts.push({ x: Math.random() * canvas.width, y: Math.random() * canvas.height, vx: (Math.random() - 0.5) * 0.3, vy: (Math.random() - 0.5) * 0.3, a: Math.random() * 0.35 + 0.05, r: Math.random() * 1.4 + 0.3 });
    }

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (let i = 0; i < pts.length; i++) {
        for (let j = i + 1; j < pts.length; j++) {
          const dx = pts[i].x - pts[j].x, dy = pts[i].y - pts[j].y;
          const d = Math.sqrt(dx * dx + dy * dy);
          if (d < 130) {
            ctx.strokeStyle = `rgba(0,212,255,${0.05 * (1 - d / 130)})`;
            ctx.lineWidth = 0.5;
            ctx.beginPath(); ctx.moveTo(pts[i].x, pts[i].y); ctx.lineTo(pts[j].x, pts[j].y); ctx.stroke();
          }
        }
      }
      pts.forEach(p => {
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0,212,255,${p.a})`; ctx.fill();
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
      });
      raf = requestAnimationFrame(draw);
    };
    draw();
    return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', resize); };
  }, []);

  return <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none opacity-50" />;
}

// ─────────────────────────────────────────────────────────────
// CYBER COMMAND CENTER
// ─────────────────────────────────────────────────────────────
function CyberCommandCenter() {
  const [tick, setTick] = useState(0);
  const [activeIdx, setActiveIdx] = useState(0);
  const [packetIdx, setPacketIdx] = useState(0);

  useEffect(() => {
    const t1 = setInterval(() => setTick(v => v + 1), 40);
    const t2 = setInterval(() => setActiveIdx(v => (v + 1) % ORBIT_NODES.length), 1600);
    const t3 = setInterval(() => setPacketIdx(v => (v + 1) % ORBIT_NODES.length), 800);
    return () => { clearInterval(t1); clearInterval(t2); clearInterval(t3); };
  }, []);

  const R = 155;
  const CX = 220, CY = 220;
  const packetT = ((tick % 60) / 60);

  const getPos = (deg: number) => ({
    x: CX + R * Math.cos((deg - 90) * Math.PI / 180),
    y: CY + R * Math.sin((deg - 90) * Math.PI / 180),
  });

  return (
    <div className="relative" style={{ width: 440, height: 440 }}>
      {/* Ambient glows */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute inset-0 rounded-full" style={{ background: 'radial-gradient(circle at 50% 50%, rgba(0,212,255,0.06) 0%, transparent 65%)' }} />
      </div>

      <svg className="absolute inset-0" width={440} height={440} style={{ overflow: 'visible' }}>
        {/* Outer ring slow rotation */}
        <g transform={`rotate(${tick * 0.15}, ${CX}, ${CY})`}>
          <circle cx={CX} cy={CY} r={R + 28} stroke="rgba(0,212,255,0.04)" strokeWidth={0.5} fill="none" strokeDasharray="3 12" />
        </g>
        <g transform={`rotate(${-tick * 0.08}, ${CX}, ${CY})`}>
          <circle cx={CX} cy={CY} r={R + 14} stroke="rgba(167,139,250,0.04)" strokeWidth={0.5} fill="none" strokeDasharray="2 8" />
        </g>
        <circle cx={CX} cy={CY} r={R} stroke="rgba(0,212,255,0.05)" strokeWidth={0.5} fill="none" />

        {/* Connection lines + packets */}
        {ORBIT_NODES.map((node, i) => {
          const pos = getPos(node.angle);
          const isActive = i === activeIdx;
          const hasPacket = i === packetIdx;
          const px = CX + (pos.x - CX) * packetT;
          const py = CY + (pos.y - CY) * packetT;

          return (
            <g key={i}>
              <line
                x1={CX} y1={CY} x2={pos.x} y2={pos.y}
                stroke={isActive ? node.color : 'rgba(255,255,255,0.04)'}
                strokeWidth={isActive ? 1 : 0.5}
                strokeDasharray={isActive ? '5 4' : '2 8'}
                style={{ transition: 'stroke 0.5s, stroke-width 0.5s' }}
              />
              {hasPacket && (
                <circle cx={px} cy={py} r={2.5} fill={node.color} opacity={0.85} />
              )}
            </g>
          );
        })}
      </svg>

      {/* Module nodes */}
      {ORBIT_NODES.map((node, i) => {
        const pos = getPos(node.angle);
        const Icon = node.icon;
        const isActive = i === activeIdx;
        return (
          <div key={i} className="absolute flex flex-col items-center" style={{ left: pos.x - 22, top: pos.y - 22, width: 44 }}>
            <div
              className="w-11 h-11 rounded-2xl flex items-center justify-center border transition-all duration-500"
              style={{
                background: isActive ? `${node.color}12` : 'rgba(12,18,30,0.95)',
                borderColor: isActive ? `${node.color}45` : 'rgba(255,255,255,0.07)',
                boxShadow: isActive ? `0 0 20px ${node.color}20` : 'none',
              }}
            >
              <Icon className="w-4 h-4 transition-colors duration-500" style={{ color: isActive ? node.color : 'rgba(148,163,184,0.5)' }} />
            </div>
            <span className="text-[8px] font-mono mt-1 text-center whitespace-nowrap transition-colors duration-500" style={{ color: isActive ? node.color : 'rgba(100,116,139,0.7)' }}>
              {node.label}
            </span>
          </div>
        );
      })}

      {/* Core */}
      <div className="absolute" style={{ left: CX - 40, top: CY - 40, width: 80, height: 80 }}>
        <div className="relative w-20 h-20 flex items-center justify-center">
          <div className="absolute inset-0 rounded-full border border-[#00D4FF]/20 animate-[ping_3s_ease-in-out_infinite]" style={{ animationDelay: '0s' }} />
          <div className="absolute inset-[3px] rounded-full border border-[#00D4FF]/15" />
          <div className="absolute inset-[8px] rounded-full flex items-center justify-center" style={{ background: 'rgba(0,212,255,0.06)', border: '1px solid rgba(0,212,255,0.2)' }}>
            <Shield className="w-6 h-6 text-[#00D4FF]" />
          </div>
        </div>
      </div>

      {/* Core label */}
      <div className="absolute text-center" style={{ left: CX - 40, top: CY + 46, width: 80 }}>
        <span className="text-[9px] font-mono tracking-[0.15em] text-[#00D4FF]/50">SENTINELX</span>
      </div>

      {/* Status badge */}
      <div
        className="absolute top-4 right-4 flex items-center space-x-1.5 px-2.5 py-1 rounded-lg text-[10px] font-mono font-semibold"
        style={{ background: 'rgba(34,197,94,0.08)', border: '1px solid rgba(34,197,94,0.2)', color: '#22C55E' }}
      >
        <span className="w-1.5 h-1.5 rounded-full bg-[#22C55E] animate-pulse" />
        <span>LIVE</span>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// SECURITY TICKER
// ─────────────────────────────────────────────────────────────
function SecurityTicker() {
  const items = [...TICKER_ITEMS, ...TICKER_ITEMS];
  const severityColor = (s: string) => s === 'critical' ? '#EF4444' : s === 'high' ? '#F59E0B' : '#22C55E';

  return (
    <div className="relative overflow-hidden py-3 border-y" style={{ borderColor: 'rgba(255,255,255,0.05)', background: 'rgba(0,212,255,0.02)' }}>
      {/* Fade masks */}
      <div className="absolute left-0 top-0 bottom-0 w-24 z-10 pointer-events-none" style={{ background: 'linear-gradient(to right, #080C15, transparent)' }} />
      <div className="absolute right-0 top-0 bottom-0 w-24 z-10 pointer-events-none" style={{ background: 'linear-gradient(to left, #080C15, transparent)' }} />

      <motion.div
        className="flex items-center space-x-10 whitespace-nowrap"
        animate={{ x: ['0%', '-50%'] }}
        transition={{ duration: 40, repeat: Infinity, ease: 'linear' }}
      >
        {items.map((item, i) => (
          <div key={i} className="flex items-center space-x-3 flex-shrink-0">
            <span className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: severityColor(item.severity) }} />
            <span className="text-xs text-slate-400 font-mono">{item.event}</span>
            <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded" style={{ color: severityColor(item.severity), background: `${severityColor(item.severity)}12`, border: `1px solid ${severityColor(item.severity)}25` }}>
              {item.status}
            </span>
            <span className="text-slate-700 font-mono">·</span>
          </div>
        ))}
      </motion.div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// PLATFORM MOCKUP CAROUSEL
// ─────────────────────────────────────────────────────────────
function PlatformCarousel() {
  const [active, setActive] = useState(0);
  const [direction, setDirection] = useState(1);
  const interval = useRef<ReturnType<typeof setInterval> | null>(null);

  const go = useCallback((next: number) => {
    setDirection(next > active ? 1 : -1);
    setActive(next);
  }, [active]);

  useEffect(() => {
    interval.current = setInterval(() => {
      setDirection(1);
      setActive(v => (v + 1) % MOCK_SCREENSHOTS.length);
    }, 4200);
    return () => { if (interval.current) clearInterval(interval.current); };
  }, []);

  const screen = MOCK_SCREENSHOTS[active];

  return (
    <div className="relative max-w-4xl mx-auto">
      {/* Tab strip */}
      <div className="flex items-center space-x-1 mb-6 p-1 rounded-xl overflow-x-auto" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}>
        {MOCK_SCREENSHOTS.map((s, i) => (
          <button
            key={i}
            onClick={() => { if (interval.current) clearInterval(interval.current); go(i); }}
            className="flex-shrink-0 flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-medium transition-all"
            style={{
              background: i === active ? `${s.color}14` : 'transparent',
              color: i === active ? s.color : 'rgba(148,163,184,0.6)',
              border: i === active ? `1px solid ${s.color}30` : '1px solid transparent',
            }}
          >
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: s.color, display: 'inline-block', flexShrink: 0, opacity: i === active ? 1 : 0.4 }} />
            <span>{s.tag}</span>
          </button>
        ))}
      </div>

      {/* Laptop frame */}
      <div className="relative">
        {/* Laptop body */}
        <div className="relative rounded-2xl overflow-hidden border" style={{ background: 'rgba(15,23,42,0.95)', borderColor: 'rgba(255,255,255,0.08)', boxShadow: '0 40px 120px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.04)' }}>
          {/* Browser chrome */}
          <div className="flex items-center space-x-2 px-5 py-3 border-b" style={{ background: 'rgba(8,12,21,0.95)', borderColor: 'rgba(255,255,255,0.05)' }}>
            <div className="flex space-x-1.5">
              {['#EF4444', '#F59E0B', '#22C55E'].map(c => <div key={c} className="w-3 h-3 rounded-full" style={{ background: c, opacity: 0.7 }} />)}
            </div>
            <div className="flex-1 mx-4 h-6 rounded-md flex items-center px-3 text-[11px] font-mono text-slate-500" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)' }}>
              localhost:3000/{screen.label.toLowerCase().replace(/ /g, '-')}
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded font-bold" style={{ color: screen.color, background: `${screen.color}15`, border: `1px solid ${screen.color}25` }}>
              {screen.tag}
            </span>
          </div>

          {/* Screen content */}
          <div className="relative overflow-hidden" style={{ minHeight: 360 }}>
            <AnimatePresence mode="wait" custom={direction}>
              <motion.div
                key={active}
                custom={direction}
                initial={{ opacity: 0, x: direction * 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -direction * 50 }}
                transition={{ duration: 0.38, ease: 'easeInOut' }}
                className="p-6"
                style={{ background: '#080C15' }}
              >
                {/* 1. OVERVIEW SCREEN */}
                {active === 0 && (
                  <div className="space-y-4 text-left">
                    <div className="grid grid-cols-4 gap-3">
                      <div className="rounded-xl p-3 border bg-[#121826] border-white/[0.06]">
                        <div className="text-[9px] font-mono text-slate-500 mb-1">PLAYBOOK VECTORS</div>
                        <div className="text-base font-extrabold text-[#00D4FF]">15+</div>
                        <div className="text-[10px] text-[#22C55E] font-mono mt-0.5">Adversary Scenarios</div>
                      </div>
                      <div className="rounded-xl p-3 border bg-[#121826] border-white/[0.06]">
                        <div className="text-[9px] font-mono text-slate-500 mb-1">ACTIVE INCIDENTS</div>
                        <div className="text-base font-extrabold text-white">0</div>
                        <div className="text-[10px] text-[#22C55E] font-mono mt-0.5">Systems Clean</div>
                      </div>
                      <div className="rounded-xl p-3 border bg-[#121826] border-white/[0.06]">
                        <div className="text-[9px] font-mono text-slate-500 mb-1">TARGET WAF BLOCK</div>
                        <div className="text-base font-extrabold text-[#22C55E]">99.3%</div>
                        <div className="text-[10px] text-[#22C55E] font-mono mt-0.5">Automated WAF</div>
                      </div>
                      <div className="rounded-xl p-3 border bg-[#121826] border-white/[0.06]">
                        <div className="text-[9px] font-mono text-slate-500 mb-1">BENCHMARK ACCURACY</div>
                        <div className="text-base font-extrabold text-[#A78BFA]">81.6%</div>
                        <div className="text-[10px] text-purple-400 font-mono mt-0.5">XGB / RF Benchmark</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                      <div className="col-span-2 rounded-xl p-4 border bg-[#121826] border-white/[0.06] space-y-2.5">
                        <div className="flex items-center justify-between text-xs font-semibold text-white">
                          <span>Live Threat Activity Timeline</span>
                          <span className="text-[10px] font-mono text-[#00D4FF]">REAL TIME</span>
                        </div>
                        <div className="space-y-2 text-xs font-mono">
                          <div className="flex items-center justify-between p-2 rounded bg-[#1A2236]">
                            <div className="flex items-center space-x-2">
                              <span className="w-1.5 h-1.5 rounded-full bg-[#EF4444]" />
                              <span className="text-slate-300">SQL Injection Attack Attempt</span>
                            </div>
                            <span className="text-[10px] text-[#EF4444] font-bold">BLOCKED</span>
                          </div>
                          <div className="flex items-center justify-between p-2 rounded bg-[#1A2236]">
                            <div className="flex items-center space-x-2">
                              <span className="w-1.5 h-1.5 rounded-full bg-[#F59E0B]" />
                              <span className="text-slate-300">Spear Phishing Email Flagged</span>
                            </div>
                            <span className="text-[10px] text-[#F59E0B] font-bold">ISOLATED</span>
                          </div>
                          <div className="flex items-center justify-between p-2 rounded bg-[#1A2236]">
                            <div className="flex items-center space-x-2">
                              <span className="w-1.5 h-1.5 rounded-full bg-[#22C55E]" />
                              <span className="text-slate-300">SHAP Explanation Audit Log</span>
                            </div>
                            <span className="text-[10px] text-[#22C55E] font-bold">PASSED</span>
                          </div>
                        </div>
                      </div>

                      <div className="rounded-xl p-4 border bg-[#121826] border-white/[0.06] space-y-3">
                        <div className="text-xs font-semibold text-white">Defense Health</div>
                        <div className="space-y-2 text-[11px]">
                          <div className="flex justify-between text-slate-400"><span>AI WAF Engine</span><span className="text-[#22C55E] font-mono">ONLINE</span></div>
                          <div className="flex justify-between text-slate-400"><span>ML Filter</span><span className="text-[#22C55E] font-mono">81.6%</span></div>
                          <div className="flex justify-between text-slate-400"><span>SYN Guard</span><span className="text-[#00D4FF] font-mono">SHIELDED</span></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* 2. RED TEAM SCREEN */}
                {active === 1 && (
                  <div className="grid grid-cols-3 gap-4 text-left">
                    <div className="rounded-xl p-3 border bg-[#121826] border-white/[0.06] space-y-2">
                      <div className="text-xs font-semibold text-white mb-1">Simulated Playbooks</div>
                      {[
                        { name: 'SQL Injection Payload', sev: 'CRITICAL', c: '#EF4444', active: true },
                        { name: 'Spear Phishing Wire', sev: 'HIGH', c: '#F59E0B', active: false },
                        { name: 'Prompt Injection Override', sev: 'CRITICAL', c: '#EF4444', active: false },
                      ].map(p => (
                        <div key={p.name} className={`p-2 rounded text-[11px] font-mono border ${p.active ? 'bg-[#EF4444]/10 border-[#EF4444]/30 text-white' : 'bg-[#1A2236] border-white/[0.04] text-slate-400'}`}>
                          <div className="flex justify-between">
                            <span className="truncate">{p.name}</span>
                            <span style={{ color: p.c, fontSize: 9, fontWeight: 'bold' }}>{p.sev}</span>
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="col-span-2 rounded-xl p-4 border bg-[#121826] border-white/[0.06] space-y-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="text-[9px] font-mono text-[#EF4444] uppercase font-bold">SQL INJECTION SCENARIO</span>
                          <div className="text-xs font-bold text-white">Target Endpoint: https://api.bank.com/v1/login</div>
                        </div>
                        <span className="px-2.5 py-1 rounded bg-[#EF4444]/15 border border-[#EF4444]/30 text-[#EF4444] text-[10px] font-mono font-bold">
                          SIMULATING (88% Prob)
                        </span>
                      </div>

                      <div className="p-2.5 rounded bg-[#080C14] border border-[#EF4444]/20 text-[11px] font-mono text-[#EF4444] overflow-x-auto">
                        <code>SELECT * FROM users WHERE username = &apos;admin&apos; AND &apos;1&apos;=&apos;1&apos;--</code>
                      </div>

                      <div className="p-3 rounded bg-[#080C14] border border-white/[0.05] text-[10px] font-mono text-[#22C55E] space-y-1 h-24 overflow-y-auto">
                        <div>[RED_TEAM_SIM] Initializing scenario SIM-SQLi-01...</div>
                        <div>[RED_TEAM_SIM] Vector category: SQL Injection.</div>
                        <div>[RED_TEAM_SIM] Generating synthetic payload...</div>
                        <div className="text-[#EF4444]">[RED_TEAM_SIM] Payload deployed to sandbox endpoint.</div>
                        <div>[RED_TEAM_SIM] Attack simulation completed. Impact: CRITICAL.</div>
                      </div>
                    </div>
                  </div>
                )}

                {/* 3. BLUE TEAM SCREEN */}
                {active === 2 && (
                  <div className="space-y-4 text-left">
                    <div className="p-3 rounded-xl border bg-[#EF4444]/08 border-[#EF4444]/25 flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-2 h-2 rounded-full bg-[#EF4444] animate-ping" />
                        <div>
                          <span className="text-[10px] font-mono text-[#EF4444] font-bold uppercase">MALICIOUS PAYLOAD DETECTED</span>
                          <div className="text-xs font-bold text-white">SQL Injection Attempt in Authorization Header</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="text-[10px] font-mono text-slate-400">AI Risk Score</span>
                        <div className="text-base font-extrabold text-[#EF4444]">98 / 100</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-3">
                      <div className="rounded-xl p-3.5 border bg-[#121826] border-white/[0.06] space-y-1.5">
                        <span className="text-[9px] font-mono text-slate-500 uppercase">RANDOM FOREST</span>
                        <div className="text-sm font-bold text-[#EF4444]">99.4% Malicious</div>
                        <div className="w-full h-1.5 rounded-full bg-[#1A2236] overflow-hidden">
                          <div className="h-full bg-[#EF4444] w-[99%]" />
                        </div>
                      </div>

                      <div className="rounded-xl p-3.5 border bg-[#121826] border-white/[0.06] space-y-1.5">
                        <span className="text-[9px] font-mono text-slate-500 uppercase">XGBOOST ENGINE</span>
                        <div className="text-sm font-bold text-[#EF4444]">98.7% Malicious</div>
                        <div className="w-full h-1.5 rounded-full bg-[#1A2236] overflow-hidden">
                          <div className="h-full bg-[#EF4444] w-[98%]" />
                        </div>
                      </div>

                      <div className="rounded-xl p-3.5 border bg-[#121826] border-white/[0.06] space-y-1.5">
                        <span className="text-[9px] font-mono text-slate-500 uppercase">ISOLATION FOREST</span>
                        <div className="text-sm font-bold text-[#F59E0B]">Anomaly 0.94</div>
                        <div className="w-full h-1.5 rounded-full bg-[#1A2236] overflow-hidden">
                          <div className="h-full bg-[#F59E0B] w-[94%]" />
                        </div>
                      </div>
                    </div>

                    <div className="p-3 rounded-xl border bg-[#22C55E]/08 border-[#22C55E]/20 flex items-center justify-between text-xs font-mono">
                      <div className="flex items-center space-x-2 text-slate-300">
                        <span className="text-[#22C55E]">✓</span>
                        <span>Automated WAF Mitigation: Block IP 185.220.101.5 & Reset Session</span>
                      </div>
                      <span className="px-2 py-0.5 rounded bg-[#22C55E]/15 text-[#22C55E] font-bold text-[10px]">RULE ACTIVE</span>
                    </div>
                  </div>
                )}

                {/* 4. THREAT INTEL LAB */}
                {active === 3 && (
                  <div className="grid grid-cols-2 gap-4 text-left">
                    <div className="rounded-xl p-4 border bg-[#121826] border-white/[0.06] space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-white">URL Phishing Intelligence</span>
                        <span className="text-[10px] font-mono text-[#EF4444] font-bold bg-[#EF4444]/10 px-2 py-0.5 rounded border border-[#EF4444]/20">HIGH RISK</span>
                      </div>
                      <div className="p-2 rounded bg-[#080C14] text-[11px] font-mono text-[#00D4FF] truncate">
                        https://paypal-security-update-account.xyz/checkout
                      </div>
                      <div className="grid grid-cols-3 gap-2 text-center text-[10px] font-mono">
                        <div className="p-2 rounded bg-[#1A2236]">
                          <div className="text-slate-500">SPF</div>
                          <div className="text-[#EF4444] font-bold">FAIL</div>
                        </div>
                        <div className="p-2 rounded bg-[#1A2236]">
                          <div className="text-slate-500">DKIM</div>
                          <div className="text-[#EF4444] font-bold">FAIL</div>
                        </div>
                        <div className="p-2 rounded bg-[#1A2236]">
                          <div className="text-slate-500">DMARC</div>
                          <div className="text-[#EF4444] font-bold">REJECT</div>
                        </div>
                      </div>
                      <div className="text-[11px] text-slate-400 space-y-1">
                        <div>• Suspicious TLD: <span className="text-[#F59E0B] font-mono">.xyz</span></div>
                        <div>• Brand Keyword Spoofing matched</div>
                      </div>
                    </div>

                    <div className="rounded-xl p-4 border bg-[#121826] border-white/[0.06] space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-white">MITRE ATT&CK & CVE Mapping</span>
                        <span className="text-[10px] font-mono text-[#00D4FF]">v14.1</span>
                      </div>
                      <div className="space-y-2">
                        <div className="p-2.5 rounded bg-[#1A2236] border border-white/[0.04]">
                          <div className="flex justify-between text-[11px] font-mono font-bold text-[#00D4FF]">
                            <span>T1566.002</span>
                            <span>Spearphishing Link</span>
                          </div>
                          <div className="text-[10px] text-slate-500 mt-0.5">Initial Access via credential harvest URL</div>
                        </div>
                        <div className="p-2.5 rounded bg-[#1A2236] border border-white/[0.04]">
                          <div className="flex justify-between text-[11px] font-mono font-bold text-[#F59E0B]">
                            <span>CVE-2026-1184</span>
                            <span>SQLi RCE Vulnerability</span>
                          </div>
                          <div className="text-[10px] text-slate-500 mt-0.5">CVSS 9.8 Critical Risk Score</div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* 5. EXPLAINABLE AI (XAI) */}
                {active === 4 && (
                  <div className="space-y-4 text-left">
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-[10px] font-mono text-[#A78BFA] font-bold uppercase">SHAP KERNEL ATTRIBUTION</span>
                        <h4 className="text-xs font-bold text-white">Model Decision Feature Weight Breakdown</h4>
                      </div>
                      <span className="px-2.5 py-1 rounded bg-[#A78BFA]/15 border border-[#A78BFA]/30 text-[#A78BFA] text-[10px] font-mono font-bold">
                        CONFIDENCE: 98.4%
                      </span>
                    </div>

                    <div className="space-y-2.5">
                      {[
                        { feature: 'Flow Duration', weight: 42, color: '#A78BFA', desc: 'Anomalous burst connection length' },
                        { feature: 'Fwd Packet Length Max', weight: 28, color: '#00D4FF', desc: 'Exceeds normal request payload boundary' },
                        { feature: 'SYN Flag Count', weight: 18, color: '#F59E0B', desc: 'High SYN handshake frequency' },
                      ].map(f => (
                        <div key={f.feature} className="p-2.5 rounded-lg bg-[#121826] border border-white/[0.06] space-y-1">
                          <div className="flex justify-between text-xs font-mono">
                            <span className="text-white font-semibold">{f.feature}</span>
                            <span style={{ color: f.color }} className="font-bold">{f.weight}% weight</span>
                          </div>
                          <div className="w-full h-1.5 rounded-full bg-[#1A2236] overflow-hidden">
                            <div className="h-full rounded-full" style={{ width: `${f.weight}%`, background: f.color }} />
                          </div>
                          <div className="text-[10px] text-slate-500">{f.desc}</div>
                        </div>
                      ))}
                    </div>

                    <div className="p-3 rounded-xl bg-[#080C14] border border-[#A78BFA]/20 text-[11px] text-slate-300 leading-relaxed flex items-center justify-between">
                      <span>Model flagged connection due to anomalous packet frequency combined with SQLi payload signature.</span>
                      <span className="text-[10px] font-mono text-[#22C55E] font-bold flex-shrink-0 ml-3">✓ AUDIT CERTIFIED</span>
                    </div>
                  </div>
                )}

                {/* 6. EXECUTIVE REPORTING */}
                {active === 5 && (
                  <div className="space-y-4 text-left">
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-[10px] font-mono text-[#22C55E] font-bold uppercase">INCIDENT REPORTS & AUDIT TRAIL</span>
                        <h4 className="text-xs font-bold text-white">Automated PDF Security Documentation</h4>
                      </div>
                      <button className="px-3 py-1.5 rounded-lg bg-[#22C55E] text-[#080C15] text-[11px] font-bold font-mono">
                        + Generate PDF Report
                      </button>
                    </div>

                    <div className="space-y-2.5">
                      {[
                        { id: 'REP-SQLI-8849', title: 'Incident_Report_SQLi_2026.pdf', date: '08 Aug 2026 • 21:02:24 IST', hash: 'e3b0c442...855', status: 'VERIFIED' },
                        { id: 'REP-AUDIT-9921', title: 'Executive_Q3_Security_Audit.pdf', date: '08 Aug 2026 • 18:30:00 IST', hash: 'a591a6d4...109', status: 'VERIFIED' },
                      ].map(rep => (
                        <div key={rep.id} className="p-3.5 rounded-xl bg-[#121826] border border-white/[0.06] flex items-center justify-between">
                          <div className="space-y-0.5">
                            <div className="flex items-center space-x-2">
                              <span className="text-xs font-bold text-white">{rep.title}</span>
                              <span className="text-[9px] font-mono text-[#22C55E] bg-[#22C55E]/10 border border-[#22C55E]/20 px-1.5 py-0.5 rounded">{rep.status}</span>
                            </div>
                            <div className="text-[10px] font-mono text-slate-500">
                              Generated: {rep.date} · SHA-256: {rep.hash}
                            </div>
                          </div>
                          <button className="px-3 py-1.5 rounded-lg bg-[#1A2236] hover:bg-[#1E2A40] text-xs font-mono text-[#00D4FF] border border-white/[0.06] transition-colors">
                            Download PDF
                          </button>
                        </div>
                      ))}
                    </div>

                    <div className="p-3 rounded-xl bg-[#080C14] border border-white/[0.05] text-[10px] font-mono text-slate-400 flex items-center justify-between">
                      <span>Integrity Check: SHA-256 digest calculated and signed for compliance verification.</span>
                      <span className="text-[#22C55E] font-bold">100% MATCH</span>
                    </div>
                  </div>
                )}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>

        {/* Bottom stand */}
        <div className="mx-auto mt-0 h-2 rounded-b-xl" style={{ width: '60%', background: 'rgba(255,255,255,0.04)', boxShadow: '0 8px 24px rgba(0,0,0,0.3)' }} />
        <div className="mx-auto mt-0 h-1 rounded-b-xl" style={{ width: '50%', background: 'rgba(255,255,255,0.02)' }} />
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// BENTO GRID
// ─────────────────────────────────────────────────────────────
function BentoGrid({ onGetStarted }: { onGetStarted: () => void }) {
  return (
    <div className="grid grid-cols-12 grid-rows-2 gap-4" style={{ height: 520 }}>
      {/* Attack Simulation — large left */}
      {BENTO_FEATURES.filter(f => f.id === 'attack').map(feat => {
        const Icon = feat.icon;
        return (
          <motion.div
            key={feat.id}
            whileHover={{ y: -4, boxShadow: `0 16px 48px rgba(0,0,0,0.35), 0 0 0 1px ${feat.color}20` }}
            transition={{ duration: 0.2 }}
            className="col-span-5 row-span-2 rounded-2xl p-7 flex flex-col justify-between relative overflow-hidden cursor-default border"
            style={{ background: `linear-gradient(135deg, ${feat.bg} 0%, rgba(8,12,21,0.95) 100%)`, borderColor: feat.border }}
            onClick={onGetStarted}
          >
            <div className="absolute top-0 left-0 right-0 h-px" style={{ background: `linear-gradient(90deg, transparent, ${feat.color}35, transparent)` }} />
            <div className="absolute -right-20 -bottom-20 w-48 h-48 rounded-full blur-[60px]" style={{ background: `${feat.color}08` }} />
            <div>
              <span className="inline-block text-[10px] font-mono font-bold tracking-[0.1em] px-2.5 py-1 rounded-lg mb-4" style={{ background: feat.accent, color: feat.color, border: `1px solid ${feat.color}20` }}>{feat.badge}</span>
              <div className="w-11 h-11 rounded-xl flex items-center justify-center mb-4 border" style={{ background: feat.accent, borderColor: `${feat.color}20` }}>
                <Icon className="w-5 h-5" style={{ color: feat.color }} />
              </div>
              <h3 className="text-xl font-bold text-white mb-3 tracking-tight">{feat.title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed">{feat.desc}</p>
            </div>
            <div className="flex items-center space-x-1.5 text-xs font-medium mt-4" style={{ color: feat.color }}>
              <span>Explore module</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </div>
          </motion.div>
        );
      })}

      {/* Threat Intelligence — medium top center */}
      {BENTO_FEATURES.filter(f => f.id === 'threat-intel').map(feat => {
        const Icon = feat.icon;
        return (
          <motion.div key={feat.id} whileHover={{ y: -3 }} transition={{ duration: 0.2 }}
            className="col-span-4 row-span-1 rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden cursor-default border"
            style={{ background: `linear-gradient(135deg, ${feat.bg} 0%, rgba(8,12,21,0.95) 100%)`, borderColor: feat.border }}
            onClick={onGetStarted}
          >
            <div className="absolute top-0 left-0 right-0 h-px" style={{ background: `linear-gradient(90deg, transparent, ${feat.color}25, transparent)` }} />
            <div>
              <span className="inline-block text-[10px] font-mono font-bold tracking-widest px-2 py-0.5 rounded mb-3" style={{ background: feat.accent, color: feat.color }}>{feat.badge}</span>
              <div className="flex items-center space-x-3 mb-3">
                <div className="w-9 h-9 rounded-xl flex items-center justify-center border" style={{ background: feat.accent, borderColor: `${feat.color}20` }}>
                  <Icon className="w-4 h-4" style={{ color: feat.color }} />
                </div>
                <h3 className="text-base font-bold text-white tracking-tight">{feat.title}</h3>
              </div>
              <p className="text-xs text-slate-500 leading-relaxed">{feat.desc}</p>
            </div>
          </motion.div>
        );
      })}

      {/* Investigation — medium top right */}
      {BENTO_FEATURES.filter(f => f.id === 'investigation').map(feat => {
        const Icon = feat.icon;
        return (
          <motion.div key={feat.id} whileHover={{ y: -3 }} transition={{ duration: 0.2 }}
            className="col-span-3 row-span-1 rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden cursor-default border"
            style={{ background: `linear-gradient(135deg, ${feat.bg} 0%, rgba(8,12,21,0.95) 100%)`, borderColor: feat.border }}
            onClick={onGetStarted}
          >
            <div className="absolute top-0 left-0 right-0 h-px" style={{ background: `linear-gradient(90deg, transparent, ${feat.color}25, transparent)` }} />
            <div>
              <span className="inline-block text-[10px] font-mono font-bold tracking-widest px-2 py-0.5 rounded mb-3" style={{ background: feat.accent, color: feat.color }}>{feat.badge}</span>
              <div className="w-9 h-9 rounded-xl flex items-center justify-center border mb-3" style={{ background: feat.accent, borderColor: `${feat.color}20` }}>
                <Icon className="w-4 h-4" style={{ color: feat.color }} />
              </div>
              <h3 className="text-sm font-bold text-white mb-2">{feat.title}</h3>
              <p className="text-xs text-slate-500 leading-relaxed line-clamp-3">{feat.desc}</p>
            </div>
          </motion.div>
        );
      })}

      {/* Reports — small bottom center-left */}
      {BENTO_FEATURES.filter(f => f.id === 'reports').map(feat => {
        const Icon = feat.icon;
        return (
          <motion.div key={feat.id} whileHover={{ y: -3 }} transition={{ duration: 0.2 }}
            className="col-span-2 row-span-1 rounded-2xl p-5 flex flex-col justify-between relative overflow-hidden cursor-default border"
            style={{ background: `linear-gradient(135deg, ${feat.bg} 0%, rgba(8,12,21,0.95) 100%)`, borderColor: feat.border }}
            onClick={onGetStarted}
          >
            <div className="w-8 h-8 rounded-xl flex items-center justify-center border mb-3" style={{ background: feat.accent, borderColor: `${feat.color}20` }}>
              <Icon className="w-3.5 h-3.5" style={{ color: feat.color }} />
            </div>
            <div>
              <h3 className="text-xs font-bold text-white mb-1">{feat.title}</h3>
              <p className="text-[11px] text-slate-600 leading-relaxed line-clamp-2">{feat.desc}</p>
            </div>
          </motion.div>
        );
      })}

      {/* ML Engine — small bottom center */}
      {BENTO_FEATURES.filter(f => f.id === 'ml').map(feat => {
        const Icon = feat.icon;
        return (
          <motion.div key={feat.id} whileHover={{ y: -3 }} transition={{ duration: 0.2 }}
            className="col-span-2 row-span-1 rounded-2xl p-5 flex flex-col justify-between relative overflow-hidden cursor-default border"
            style={{ background: `linear-gradient(135deg, ${feat.bg} 0%, rgba(8,12,21,0.95) 100%)`, borderColor: feat.border }}
            onClick={onGetStarted}
          >
            <div className="w-8 h-8 rounded-xl flex items-center justify-center border mb-3" style={{ background: feat.accent, borderColor: `${feat.color}20` }}>
              <Icon className="w-3.5 h-3.5" style={{ color: feat.color }} />
            </div>
            <div>
              <h3 className="text-xs font-bold text-white mb-1">{feat.title}</h3>
              <p className="text-[11px] text-slate-600 leading-relaxed line-clamp-2">{feat.desc}</p>
            </div>
          </motion.div>
        );
      })}

      {/* XAI — large right */}
      {BENTO_FEATURES.filter(f => f.id === 'xai').map(feat => {
        const Icon = feat.icon;
        return (
          <motion.div
            key={feat.id}
            whileHover={{ y: -4, boxShadow: `0 16px 48px rgba(0,0,0,0.35), 0 0 0 1px ${feat.color}20` }}
            transition={{ duration: 0.2 }}
            className="col-span-5 row-span-1 rounded-2xl p-7 flex flex-col justify-between relative overflow-hidden cursor-default border"
            style={{ background: `linear-gradient(135deg, ${feat.bg} 0%, rgba(8,12,21,0.95) 100%)`, borderColor: feat.border }}
            onClick={onGetStarted}
          >
            <div className="absolute top-0 left-0 right-0 h-px" style={{ background: `linear-gradient(90deg, transparent, ${feat.color}35, transparent)` }} />
            <div className="absolute -right-16 -bottom-16 w-40 h-40 rounded-full blur-[50px]" style={{ background: `${feat.color}06` }} />
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="inline-block text-[10px] font-mono font-bold tracking-widest px-2.5 py-1 rounded-lg" style={{ background: feat.accent, color: feat.color, border: `1px solid ${feat.color}20` }}>{feat.badge}</span>
                <Sparkles className="w-4 h-4" style={{ color: feat.color, opacity: 0.5 }} />
              </div>
              <div className="flex items-start space-x-4">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center border flex-shrink-0" style={{ background: feat.accent, borderColor: `${feat.color}20` }}>
                  <Icon className="w-5 h-5" style={{ color: feat.color }} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white mb-2 tracking-tight">{feat.title}</h3>
                  <p className="text-sm text-slate-500 leading-relaxed">{feat.desc}</p>
                </div>
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// MAIN COMPONENT
// ─────────────────────────────────────────────────────────────
export const LandingPage: React.FC<LandingPageProps> = ({ onGetStarted, onOpenLogin, onNavigateAbout }) => {
  const { scrollY } = useScroll();
  const navBg = useTransform(scrollY, [0, 60], ['rgba(8,12,21,0)', 'rgba(8,12,21,0.96)']);
  const navBorder = useTransform(scrollY, [0, 60], ['rgba(255,255,255,0)', 'rgba(255,255,255,0.05)']);

  const featuresRef = useRef<HTMLDivElement>(null);
  const scrollToFeatures = () => featuresRef.current?.scrollIntoView({ behavior: 'smooth' });

  // Mouse parallax
  const mx = useMotionValue(0);
  const my = useMotionValue(0);
  const springX = useSpring(mx, { stiffness: 40, damping: 25 });
  const springY = useSpring(my, { stiffness: 40, damping: 25 });
  const handleMouse = useCallback((e: React.MouseEvent) => {
    mx.set((e.clientX / window.innerWidth - 0.5) * 18);
    my.set((e.clientY / window.innerHeight - 0.5) * 18);
  }, [mx, my]);

  const [videoModal, setVideoModal] = useState(false);

  return (
    <div className="min-h-screen text-white overflow-x-hidden" style={{ background: '#080C15' }} onMouseMove={handleMouse}>

      {/* ── BACKGROUND ── */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <ParticleCanvas />
        <div className="absolute inset-0" style={{
          background: `
            radial-gradient(ellipse 110% 55% at 50% -5%, rgba(0,212,255,0.055) 0%, transparent 60%),
            radial-gradient(ellipse 70% 50% at 85% 75%, rgba(167,139,250,0.04) 0%, transparent 55%),
            radial-gradient(ellipse 55% 40% at 8% 65%, rgba(0,212,255,0.03) 0%, transparent 52%)
          `
        }} />
        <div className="absolute inset-0 opacity-[0.022]" style={{
          backgroundImage: 'linear-gradient(rgba(0,212,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,255,1) 1px, transparent 1px)',
          backgroundSize: '72px 72px'
        }} />
      </div>

      {/* ── NAVBAR ── */}
      <motion.header
        style={{ backgroundColor: navBg, borderBottomColor: navBorder }}
        className="fixed top-0 inset-x-0 z-50 border-b backdrop-blur-xl"
      >
        <div className="max-w-[1280px] mx-auto px-8 h-[62px] flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-xl flex items-center justify-center border" style={{ background: 'rgba(0,212,255,0.08)', borderColor: 'rgba(0,212,255,0.25)' }}>
              <Shield className="w-4 h-4 text-[#00D4FF]" />
            </div>
            <span className="text-[15px] font-bold tracking-tight">
              Sentinel<span className="text-[#00D4FF]">X</span>
              <span className="text-slate-500 font-normal"> AI</span>
            </span>
          </div>

          <nav className="hidden lg:flex items-center space-x-7">
            {[
              { label: 'Features', ref: '#features' },
              { label: 'Platform', ref: '#platform' },
              { label: 'Architecture', ref: '#architecture' },
              { label: 'Technology', ref: '#technology' },
              { label: 'About', action: onNavigateAbout },
            ].map(l => (
              <button
                key={l.label}
                onClick={l.action || (() => { const el = document.querySelector(l.ref || ''); el?.scrollIntoView({ behavior: 'smooth' }); })}
                className="text-sm font-medium text-slate-400 hover:text-white transition-colors"
              >
                {l.label}
              </button>
            ))}
          </nav>

          <div className="flex items-center space-x-3">
            <div className="hidden md:flex items-center space-x-1.5 mr-1">
              <Radio className="w-2.5 h-2.5 text-[#22C55E] animate-pulse" />
              <span className="text-[11px] font-mono text-slate-600">SOC ACTIVE</span>
            </div>
            <button onClick={onOpenLogin} className="text-sm font-medium text-slate-400 hover:text-white transition-colors px-3 py-2">
              Sign In
            </button>
            <motion.button
              onClick={onGetStarted}
              whileHover={{ y: -1, boxShadow: '0 8px 28px rgba(0,212,255,0.3)' }}
              whileTap={{ scale: 0.98 }}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-[#080C15]"
              style={{ background: '#00D4FF' }}
            >
              <span>Launch Platform</span>
              <ArrowRight className="w-4 h-4" />
            </motion.button>
          </div>
        </div>
      </motion.header>

      {/* ── HERO ── */}
      <section className="relative z-10 min-h-screen flex items-center pt-[62px]" id="hero">
        <div className="max-w-[1280px] mx-auto px-8 w-full py-20">
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_auto] gap-16 items-center">

            {/* LEFT */}
            <div className="space-y-8 max-w-[560px]">
              <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45 }}>
                <span className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full text-[11px] font-mono font-semibold" style={{ background: 'rgba(0,212,255,0.06)', border: '1px solid rgba(0,212,255,0.18)', color: '#00D4FF', letterSpacing: '0.07em' }}>
                  <span className="w-1.5 h-1.5 rounded-full bg-[#00D4FF] animate-pulse" />
                  <span>ENTERPRISE AI SECURITY PLATFORM</span>
                </span>
              </motion.div>

              <motion.h1
                initial={{ opacity: 0, y: 22 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.55, delay: 0.1 }}
                className="font-extrabold tracking-tight leading-[1.04]"
                style={{ fontSize: 'clamp(2.75rem, 4.5vw, 3.85rem)' }}
              >
                AI-Powered Cyber Defense
                <br />
                <span style={{ color: '#00D4FF' }}>for Modern Enterprises</span>
              </motion.h1>

              <motion.p
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="text-[1.05rem] text-slate-400 leading-relaxed"
              >
                SentinelX AI unifies{' '}
                <span className="text-slate-200 font-medium">Red Team simulation</span>,{' '}
                <span className="text-slate-200 font-medium">Blue Team AI detection</span>,{' '}
                <span className="text-[#A78BFA] font-medium">Explainable AI</span>,{' '}
                <span className="text-slate-200 font-medium">Threat Intelligence</span>,{' '}
                <span className="text-slate-200 font-medium">Machine Learning</span>, and{' '}
                <span className="text-slate-200 font-medium">Executive Security Reporting</span>{' '}
                into one intelligent enterprise platform.
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
                className="flex flex-wrap gap-3"
              >
                <motion.button
                  onClick={onGetStarted}
                  whileHover={{ y: -2, boxShadow: '0 12px 40px rgba(0,212,255,0.35)' }}
                  whileTap={{ scale: 0.97 }}
                  className="flex items-center space-x-2.5 px-7 py-3.5 rounded-xl font-semibold text-sm text-[#080C15]"
                  style={{ background: '#00D4FF' }}
                >
                  <span>Launch Security Center</span>
                  <ArrowRight className="w-4 h-4" />
                </motion.button>
                <motion.button
                  onClick={scrollToFeatures}
                  whileHover={{ y: -2 }}
                  whileTap={{ scale: 0.97 }}
                  className="flex items-center space-x-2.5 px-7 py-3.5 rounded-xl font-semibold text-sm text-slate-300 border border-white/10 hover:border-white/18 hover:bg-white/[0.03] transition-all"
                >
                  <span>Explore Platform</span>
                  <ChevronDown className="w-4 h-4" />
                </motion.button>
              </motion.div>

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5, delay: 0.48 }}
                className="flex flex-wrap gap-5 pt-1"
              >
                {[
                  { icon: CheckCircle2, label: 'MITRE ATT&CK Mapped', color: '#22C55E' },
                  { icon: Lock, label: 'JWT Authentication', color: '#00D4FF' },
                  { icon: Cpu, label: '81.6% AI Accuracy', color: '#A78BFA' },
                ].map(i => (
                  <div key={i.label} className="flex items-center space-x-1.5 text-xs text-slate-600">
                    <i.icon className="w-3.5 h-3.5" style={{ color: i.color }} />
                    <span>{i.label}</span>
                  </div>
                ))}
              </motion.div>
            </div>

            {/* RIGHT — Cyber Command Center */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.7, delay: 0.22, ease: 'easeOut' }}
              style={{ x: springX, y: springY }}
            >
              <div
                className="relative rounded-3xl p-6 border"
                style={{
                  background: 'linear-gradient(135deg, rgba(15,23,42,0.92) 0%, rgba(8,12,21,0.97) 100%)',
                  borderColor: 'rgba(0,212,255,0.1)',
                  boxShadow: '0 32px 100px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.04)',
                }}
              >
                <CyberCommandCenter />
              </div>
            </motion.div>
          </div>
        </div>

        {/* Scroll indicator */}
        <motion.div
          className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center space-y-2 cursor-pointer"
          animate={{ y: [0, 6, 0] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
          onClick={scrollToFeatures}
        >
          <span className="text-[10px] font-mono text-slate-600 tracking-[0.12em]">SCROLL</span>
          <ChevronDown className="w-4 h-4 text-slate-700" />
        </motion.div>
      </section>

      {/* ── SECURITY TICKER ── */}
      <SecurityTicker />

      {/* ── KPI STATS ── */}
      <section className="relative z-10 py-20">
        <div className="max-w-[1280px] mx-auto px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {STATS.map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-60px' }}
                transition={{ duration: 0.45, delay: i * 0.08 }}
                whileHover={{ y: -3 }}
                className="relative p-7 rounded-2xl border overflow-hidden group cursor-default"
                style={{ background: 'rgba(15,23,42,0.6)', borderColor: 'rgba(255,255,255,0.06)' }}
              >
                <div className="absolute top-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity" style={{ background: 'linear-gradient(90deg, transparent, rgba(0,212,255,0.3), transparent)' }} />
                <div className="text-[2.6rem] font-extrabold tracking-tight leading-none mb-2" style={{ color: '#00D4FF' }}>
                  <Counter target={stat.value} suffix={stat.suffix} />
                </div>
                <p className="text-sm font-semibold text-white mb-1">{stat.label}</p>
                <p className="text-xs text-slate-600 font-mono">{stat.sub}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── PLATFORM CAPABILITIES (BENTO GRID) ── */}
      <section ref={featuresRef} id="features" className="relative z-10 py-24 border-t" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
        <div className="max-w-[1280px] mx-auto px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="mb-12 space-y-3"
          >
            <span className="text-xs font-mono font-semibold tracking-[0.13em] text-[#00D4FF]">PLATFORM CAPABILITIES</span>
            <h2 className="text-4xl font-extrabold tracking-tight">
              Six integrated security modules
            </h2>
            <p className="text-slate-400 text-base max-w-xl">
              Built to simulate, detect, explain, and report — everything your SOC needs in one intelligent platform.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 28 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-40px' }}
            transition={{ duration: 0.55 }}
          >
            <BentoGrid onGetStarted={onGetStarted} />
          </motion.div>
        </div>
      </section>

      {/* ── INSIDE THE PLATFORM ── */}
      <section id="platform" className="relative z-10 py-24 border-t" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
        <div className="max-w-[1280px] mx-auto px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="text-center mb-12 space-y-3"
          >
            <span className="text-xs font-mono font-semibold tracking-[0.13em] text-[#A78BFA]">INSIDE THE PLATFORM</span>
            <h2 className="text-4xl font-extrabold tracking-tight">See SentinelX AI in action</h2>
            <p className="text-slate-400 text-base max-w-lg mx-auto">
              Every module is purpose-built for enterprise security operations with a clean, professional interface.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 28 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-40px' }}
            transition={{ duration: 0.55 }}
          >
            <PlatformCarousel />
          </motion.div>
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section className="relative z-10 py-24 border-t" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
        <div className="max-w-[1280px] mx-auto px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="text-center mb-14 space-y-3"
          >
            <span className="text-xs font-mono font-semibold tracking-[0.13em] text-[#22C55E]">HOW IT WORKS</span>
            <h2 className="text-4xl font-extrabold tracking-tight">AI-powered security pipeline</h2>
            <p className="text-slate-400 text-base max-w-md mx-auto">
              From attack vector to executive dashboard — a fully automated, explainable AI pipeline.
            </p>
          </motion.div>

          <div className="flex flex-col lg:flex-row items-center justify-center gap-0 max-w-5xl mx-auto">
            {WORKFLOW_STEPS.map((step, i) => {
              const Icon = step.icon;
              const isLast = i === WORKFLOW_STEPS.length - 1;
              return (
                <React.Fragment key={step.label}>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.4, delay: i * 0.08 }}
                    className="flex flex-col items-center text-center w-36"
                  >
                    <motion.div
                      whileHover={{ scale: 1.08 }}
                      className="w-14 h-14 rounded-2xl flex items-center justify-center border mb-3 cursor-default"
                      style={{ background: `${step.color}08`, borderColor: `${step.color}22` }}
                    >
                      <Icon className="w-5 h-5" style={{ color: step.color }} />
                    </motion.div>
                    <p className="text-xs font-semibold text-white mb-1">{step.label}</p>
                    <p className="text-[11px] text-slate-600 leading-snug">{step.desc}</p>
                  </motion.div>

                  {!isLast && (
                    <motion.div
                      initial={{ opacity: 0, scaleX: 0 }}
                      whileInView={{ opacity: 1, scaleX: 1 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.5, delay: i * 0.08 + 0.2 }}
                      className="hidden lg:flex items-center px-2 flex-shrink-0"
                    >
                      <div className="relative h-px w-12" style={{ background: 'linear-gradient(90deg, rgba(0,212,255,0.2), rgba(0,212,255,0.5))' }}>
                        <motion.div
                          className="absolute top-1/2 -translate-y-1/2 w-2 h-2 rounded-full"
                          style={{ background: '#00D4FF' }}
                          animate={{ x: [0, 44, 0] }}
                          transition={{ duration: 3, repeat: Infinity, delay: i * 0.5, ease: 'linear' }}
                        />
                      </div>
                      <ArrowRight className="w-3 h-3 text-slate-700 flex-shrink-0" />
                    </motion.div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── ENTERPRISE ARCHITECTURE ── */}
      <section id="architecture" className="relative z-10 py-24 border-t" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
        <div className="max-w-[1280px] mx-auto px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, x: -24 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.55 }}
              className="space-y-4"
            >
              <span className="text-xs font-mono font-semibold tracking-[0.13em] text-[#F59E0B]">ENTERPRISE ARCHITECTURE</span>
              <h2 className="text-4xl font-extrabold tracking-tight">
                Production-grade
                <br />
                <span style={{ color: '#00D4FF' }}>microservices design</span>
              </h2>
              <p className="text-slate-400 text-base leading-relaxed">
                SentinelX AI is built on a clean separation of concerns — a Next.js 15 frontend, FastAPI backend, JWT authentication, and a dedicated ML engine — all connected through a RESTful API layer.
              </p>
              <div className="flex flex-wrap gap-2 pt-2">
                {['Microservices', 'REST API', 'JWT Auth', 'ORM', 'Hot Reload', 'Docker Ready'].map(tag => (
                  <span key={tag} className="px-3 py-1 rounded-lg text-xs font-mono text-slate-400 border" style={{ background: 'rgba(255,255,255,0.03)', borderColor: 'rgba(255,255,255,0.07)' }}>{tag}</span>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 24 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.55 }}
              className="space-y-2"
            >
              {ARCH_LAYERS.map((layer, i) => {
                const Icon = layer.icon;
                return (
                  <React.Fragment key={layer.label}>
                    <motion.div
                      initial={{ opacity: 0, x: 20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.35, delay: i * 0.06 }}
                      whileHover={{ x: 4 }}
                      className="flex items-center space-x-4 p-4 rounded-xl border cursor-default transition-colors hover:border-white/10"
                      style={{ background: 'rgba(15,23,42,0.5)', borderColor: 'rgba(255,255,255,0.05)' }}
                    >
                      <div className="w-9 h-9 rounded-xl flex items-center justify-center border flex-shrink-0" style={{ background: `${layer.color}08`, borderColor: `${layer.color}20` }}>
                        <Icon className="w-4 h-4" style={{ color: layer.color }} />
                      </div>
                      <span className="text-sm font-medium text-slate-300">{layer.label}</span>
                      <div className="flex-1" />
                      <div className="w-2 h-2 rounded-full" style={{ background: layer.color, opacity: 0.5 }} />
                    </motion.div>
                    {i < ARCH_LAYERS.length - 1 && (
                      <div className="flex justify-center">
                        <div className="w-px h-4" style={{ background: 'rgba(255,255,255,0.06)' }} />
                      </div>
                    )}
                  </React.Fragment>
                );
              })}
            </motion.div>
          </div>
        </div>
      </section>

      {/* ── TECHNOLOGY STACK ── */}
      <section id="technology" className="relative z-10 py-24 border-t" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
        <div className="max-w-[1280px] mx-auto px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="text-center mb-12 space-y-3"
          >
            <span className="text-xs font-mono font-semibold tracking-[0.13em] text-[#F59E0B]">TECHNOLOGY STACK</span>
            <h2 className="text-4xl font-extrabold tracking-tight">Built on proven enterprise technology</h2>
          </motion.div>

          <div className="flex flex-wrap justify-center gap-3">
            {TECH.map((tech, i) => (
              <motion.div
                key={tech.name}
                initial={{ opacity: 0, y: 14 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.3, delay: i * 0.04 }}
                whileHover={{ y: -4, scale: 1.05 }}
                className="px-5 py-2.5 rounded-xl border text-sm font-medium cursor-default"
                style={{
                  background: `${tech.color}06`,
                  borderColor: `${tech.color}18`,
                  color: tech.color === '#F8FAFC' ? '#F8FAFC' : tech.color,
                  boxShadow: 'none',
                  transition: 'box-shadow 0.2s',
                }}
                onMouseEnter={e => { (e.currentTarget as HTMLDivElement).style.boxShadow = `0 6px 24px ${tech.color}18`; }}
                onMouseLeave={e => { (e.currentTarget as HTMLDivElement).style.boxShadow = 'none'; }}
              >
                {tech.name}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── WHY SENTINELX AI ── */}
      <section className="relative z-10 py-24 border-t" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
        <div className="max-w-[1280px] mx-auto px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="text-center mb-12 space-y-3"
          >
            <span className="text-xs font-mono font-semibold tracking-[0.13em] text-[#22C55E]">THE INTELLIGENT ADVANTAGE</span>
            <h2 className="text-4xl font-extrabold tracking-tight">Why SentinelX AI?</h2>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 max-w-4xl mx-auto">
            {/* Traditional */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
              className="p-8 rounded-2xl border space-y-5"
              style={{ background: 'rgba(239,68,68,0.02)', borderColor: 'rgba(239,68,68,0.1)' }}
            >
              <div className="flex items-center space-x-3">
                <div className="w-9 h-9 rounded-xl flex items-center justify-center border" style={{ background: 'rgba(239,68,68,0.08)', borderColor: 'rgba(239,68,68,0.2)' }}>
                  <X className="w-4 h-4 text-[#EF4444]" />
                </div>
                <h3 className="text-base font-semibold text-white">Traditional SOC</h3>
              </div>
              <div className="space-y-3">
                {['Reactive — responds only after breach', 'Manual analysis — bottlenecked by analysts', 'Fragmented tools — no integration', 'Slow incident response workflows', 'High false positive rates', 'No explainability or auditability'].map(item => (
                  <div key={item} className="flex items-start space-x-3">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#EF4444]/50 mt-2 flex-shrink-0" />
                    <span className="text-sm text-slate-500">{item}</span>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* SentinelX */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
              className="relative p-8 rounded-2xl border space-y-5 overflow-hidden"
              style={{ background: 'rgba(0,212,255,0.025)', borderColor: 'rgba(0,212,255,0.14)' }}
            >
              <div className="absolute top-0 inset-x-0 h-px" style={{ background: 'linear-gradient(90deg, transparent, rgba(0,212,255,0.4), transparent)' }} />
              <div className="flex items-center space-x-3">
                <div className="w-9 h-9 rounded-xl flex items-center justify-center border" style={{ background: 'rgba(0,212,255,0.08)', borderColor: 'rgba(0,212,255,0.2)' }}>
                  <Shield className="w-4 h-4 text-[#00D4FF]" />
                </div>
                <h3 className="text-base font-semibold text-white">SentinelX AI</h3>
              </div>
              <div className="space-y-3">
                {[
                  { text: 'AI-Powered — proactive threat simulation', color: '#00D4FF' },
                  { text: 'Predictive — 81.6% ML detection accuracy', color: '#22C55E' },
                  { text: 'Integrated — six modules, one platform', color: '#00D4FF' },
                  { text: 'Real-time — instant classification engine', color: '#22C55E' },
                  { text: 'Explainable — SHAP attribution on every decision', color: '#A78BFA' },
                  { text: 'Enterprise-ready — MITRE ATT&CK mapped reports', color: '#F59E0B' },
                ].map(item => (
                  <div key={item.text} className="flex items-start space-x-3">
                    <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: item.color }} />
                    <span className="text-sm text-slate-300">{item.text}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ── ENGINEERING TEAM & ACADEMIC MENTOR ── */}
      <section className="relative z-10 py-24 border-t" style={{ borderColor: 'rgba(255,255,255,0.04)' }} id="team">
        <div className="max-w-[1280px] mx-auto px-8 space-y-16">
          {/* Section Header */}
          <div className="text-center space-y-4 max-w-3xl mx-auto">
            <span className="inline-flex items-center space-x-2 px-3.5 py-1 rounded-full text-xs font-mono font-bold tracking-widest text-[#00D4FF]" style={{ background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.2)' }}>
              <Award className="w-3.5 h-3.5 text-[#00D4FF]" />
              <span>ENGINEERING DEVELOPMENT TEAM</span>
            </span>
            <h2 className="text-4xl font-extrabold tracking-tight text-white">
              Built by Engineers. <span style={{ color: '#00D4FF' }}>Powered by AI.</span>
            </h2>
            <p className="text-sm text-slate-400 leading-relaxed font-sans">
              SentinelX AI was architected, engineered, and integrated as a final-year Enterprise Security Operations Center platform by students of the Department of Artificial Intelligence &amp; Data Science at K.S. School of Engineering &amp; Management.
            </p>
          </div>

          {/* Animated Team Statistics Row */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            {[
              { label: 'ENGINEERS', value: '4', icon: Users, color: '#00D4FF' },
              { label: 'ENTERPRISE MODULES', value: '6', icon: Layers, color: '#A78BFA' },
              { label: 'ATTACK SIMULATIONS', value: '15+', icon: Flame, color: '#EF4444' },
              { label: 'DETECTION ACCURACY', value: '81.6%', icon: Cpu, color: '#22C55E' },
              { label: 'ACADEMIC MENTOR', value: '1', icon: GraduationCap, color: '#F59E0B' },
            ].map(stat => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={stat.label}
                  whileHover={{ y: -3 }}
                  className="p-5 rounded-2xl border text-center space-y-1"
                  style={{ background: 'rgba(15,23,42,0.6)', borderColor: 'rgba(255,255,255,0.06)' }}
                >
                  <div className="w-8 h-8 rounded-lg mx-auto flex items-center justify-center border mb-2" style={{ background: `${stat.color}10`, borderColor: `${stat.color}25` }}>
                    <Icon className="w-4 h-4" style={{ color: stat.color }} />
                  </div>
                  <div className="text-2xl font-extrabold text-white tracking-tight tabular-nums">{stat.value}</div>
                  <div className="text-[10px] font-mono text-slate-500 tracking-wider font-bold">{stat.label}</div>
                </motion.div>
              );
            })}
          </div>

          {/* Team Philosophy Statement */}
          <div className="text-center max-w-2xl mx-auto">
            <p className="text-xs font-mono text-slate-400 leading-relaxed italic">
              "Enterprise platforms are never built by one person. SentinelX AI is the result of collaborative engineering, machine learning research, software development, system integration, and academic mentorship."
            </p>
          </div>

          {/* 4 Engineer Cards (Single Row) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 pt-2">
            {[
              {
                name: 'Nivas M R',
                role: 'Frontend & Platform Engineer',
                desc: 'Designed responsive enterprise dashboards, implemented interactive frontend components, integrated APIs, enhanced user experience, and ensured seamless communication between modules.',
                initials: 'NM',
                image: '/images/team/nivas_mr.jpg',
                github: 'https://github.com',
                linkedin: 'https://www.linkedin.com/in/nivas-manisha-120ab0326/',
                instagram: 'https://www.instagram.com/iamnivas.mr/',
                isLead: true,
              },
              {
                name: 'Chetan B K',
                role: 'Lead AI Systems Engineer',
                desc: 'Designed the enterprise architecture of SentinelX AI, integrated AI-powered cybersecurity modules, connected machine learning pipelines, implemented Explainable AI (SHAP), developed backend services, and coordinated complete platform integration.',
                initials: 'CB',
                image: '/images/team/chetan_bk.jpg',
                github: 'https://github.com/Imchetan127',
                linkedin: 'https://www.linkedin.com/in/chetan-bhaskar-/',
                instagram: 'https://www.instagram.com/chetan_b.k_/',
              },
              {
                name: 'H Deepak',
                role: 'Backend & AI Engineer',
                desc: 'Developed FastAPI backend services, REST APIs, authentication workflows, database integration, machine learning connectivity, and optimized backend performance.',
                initials: 'HD',
                image: '/images/team/h_deepak.png',
                github: 'https://github.com',
                linkedin: 'https://www.linkedin.com/in/deepak-hemberal/',
                instagram: 'https://www.instagram.com/deepak._.hemberal/',
              },
              {
                name: 'Kiran D',
                role: 'Software Quality & Integration Engineer',
                desc: 'Focused on testing, debugging, validation, software quality assurance, performance optimization, system stability, and overall platform reliability.',
                initials: 'KD',
                image: '/images/team/kiran_d.png',
                github: 'https://github.com',
                linkedin: 'https://www.linkedin.com/in/kiran-d-b40a29335/',
                instagram: 'https://www.instagram.com/kiran.shetty02/',
              },
            ].map((member, idx) => (
              <motion.div
                key={idx}
                whileHover={{ y: -5, boxShadow: member.isLead ? '0 20px 40px rgba(34,197,94,0.3), 0 0 0 1px rgba(34,197,94,0.4)' : '0 20px 40px rgba(0,0,0,0.4), 0 0 0 1px rgba(0,212,255,0.2)' }}
                transition={{ duration: 0.2 }}
                className="relative p-6 rounded-2xl border overflow-hidden flex flex-col justify-between space-y-4 cursor-default"
                style={{
                  background: 'rgba(15,23,42,0.7)',
                  borderColor: member.isLead ? 'rgba(34,197,94,0.4)' : 'rgba(255,255,255,0.08)',
                  boxShadow: member.isLead ? '0 0 25px rgba(34,197,94,0.15)' : undefined
                }}
              >
                {member.isLead && (
                  <div className="absolute top-0 right-0 z-10">
                    <span
                      className="px-3.5 py-1 text-[10px] font-mono font-bold tracking-wider uppercase rounded-bl-xl flex items-center space-x-1"
                      style={{
                        background: 'rgba(34,197,94,0.15)',
                        color: '#22C55E',
                        borderBottom: '1px solid rgba(34,197,94,0.3)',
                        borderLeft: '1px solid rgba(34,197,94,0.3)'
                      }}
                    >
                      <Star className="w-3 h-3 text-[#22C55E] fill-[#22C55E]" />
                      <span>TEAM LEAD</span>
                    </span>
                  </div>
                )}
                <div className="space-y-4">
                  {/* Photo & Role */}
                  <div className="flex items-center space-x-3">
                    {member.image ? (
                      <img
                        src={member.image}
                        alt={member.name}
                        className="w-12 h-12 rounded-full object-cover border flex-shrink-0 shadow-sm transition-transform duration-200 hover:scale-105"
                        style={{ borderColor: member.isLead ? 'rgba(34,197,94,0.6)' : 'rgba(0,212,255,0.4)' }}
                      />
                    ) : (
                      <div className="w-12 h-12 rounded-full flex items-center justify-center font-mono font-bold text-sm flex-shrink-0 border" style={{ background: member.isLead ? 'rgba(34,197,94,0.1)' : 'rgba(0,212,255,0.1)', borderColor: member.isLead ? 'rgba(34,197,94,0.4)' : 'rgba(0,212,255,0.3)', color: member.isLead ? '#22C55E' : '#00D4FF' }}>
                        {member.initials}
                      </div>
                    )}
                    <div>
                      <h4 className="text-base font-bold text-white tracking-tight">{member.name}</h4>
                      <p className="text-[11px] font-mono font-semibold mt-0.5" style={{ color: member.isLead ? '#22C55E' : '#00D4FF' }}>
                        {member.role}
                      </p>
                    </div>
                  </div>

                  {/* Contribution text */}
                  <p className="text-xs text-slate-400 leading-relaxed">{member.desc}</p>
                </div>

                {/* Social Links */}
                <div className="pt-3 border-t flex items-center space-x-3 text-slate-400 font-mono text-xs" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
                  {member.github && (
                    <a
                      href={member.github}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label={`${member.name} GitHub`}
                      className="text-slate-400 hover:text-white hover:scale-110 transition-all duration-200 flex items-center space-x-1 cursor-pointer"
                      title={`${member.name} GitHub`}
                    >
                      <Github className="w-4 h-4" />
                    </a>
                  )}
                  {member.linkedin && (
                    <a
                      href={member.linkedin}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label={`${member.name} LinkedIn`}
                      className="text-slate-400 hover:text-[#00D4FF] hover:scale-110 transition-all duration-200 flex items-center space-x-1 cursor-pointer"
                      title={`${member.name} LinkedIn`}
                    >
                      <Linkedin className="w-4 h-4" />
                    </a>
                  )}
                  {member.instagram && (
                    <a
                      href={member.instagram}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label={`${member.name} Instagram`}
                      className="text-slate-400 hover:text-[#00D4FF] hover:scale-110 transition-all duration-200 flex items-center space-x-1 cursor-pointer"
                      title={`${member.name} Instagram`}
                    >
                      <Instagram className="w-4 h-4" />
                    </a>
                  )}
                </div>
              </motion.div>
            ))}
          </div>

          {/* Academic Mentor Panel */}
          <div className="flex justify-center">
            <div className="w-full max-w-3xl p-7 rounded-2xl border relative overflow-hidden space-y-4" style={{ background: 'rgba(15,23,42,0.85)', borderColor: 'rgba(245,158,11,0.35)', boxShadow: '0 20px 50px rgba(0,0,0,0.5)' }}>
              <div className="absolute top-0 right-0">
                <span className="px-3.5 py-1 text-[10px] font-mono font-bold tracking-wider uppercase rounded-bl-xl flex items-center space-x-1" style={{ background: 'rgba(245,158,11,0.15)', color: '#F59E0B', borderBottom: '1px solid rgba(245,158,11,0.25)', borderLeft: '1px solid rgba(245,158,11,0.25)' }}>
                  <GraduationCap className="w-3.5 h-3.5 text-[#F59E0B]" />
                  <span>ACADEMIC MENTOR</span>
                </span>
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center space-y-3 sm:space-y-0 sm:space-x-4 border-b pb-4" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
                <div className="w-14 h-14 rounded-full flex items-center justify-center font-mono font-bold text-lg flex-shrink-0 border" style={{ background: 'rgba(245,158,11,0.12)', color: '#F59E0B', borderColor: 'rgba(245,158,11,0.35)' }}>
                  SK
                </div>
                <div className="space-y-0.5">
                  <h3 className="text-xl font-bold text-white tracking-tight">Sneha Karamadi</h3>
                  <p className="text-xs font-mono font-bold text-[#F59E0B]">Assistant Professor</p>
                  <p className="text-xs font-mono text-slate-300">Department of Artificial Intelligence &amp; Data Science</p>
                  <p className="text-xs font-mono text-slate-400">K.S. School of Engineering &amp; Management</p>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed font-sans">
                Provided technical guidance, architectural reviews, project evaluation, engineering mentorship, and continuous support throughout the successful development of SentinelX AI.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── FINAL CTA ── */}
      <section className="relative z-10 py-32 border-t overflow-hidden" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute inset-0" style={{ background: 'radial-gradient(ellipse 80% 60% at 50% 50%, rgba(0,212,255,0.05) 0%, transparent 65%)' }} />
        </div>
        <div className="relative max-w-[900px] mx-auto px-8 text-center space-y-7">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.55 }}
          >
            <span className="text-xs font-mono font-semibold tracking-[0.13em] text-[#00D4FF] block mb-5">GET STARTED TODAY</span>
            <h2 className="font-extrabold tracking-tight leading-tight" style={{ fontSize: 'clamp(2.2rem, 5vw, 3.5rem)' }}>
              Ready to experience enterprise
              <br />
              <span style={{ color: '#00D4FF' }}>AI cybersecurity?</span>
            </h2>
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-lg text-slate-400 max-w-xl mx-auto"
          >
            Launch the Security Operations Center and experience six integrated AI modules working together in real time.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.18 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2"
          >
            <motion.button
              onClick={onGetStarted}
              whileHover={{ y: -3, boxShadow: '0 16px 50px rgba(0,212,255,0.4)' }}
              whileTap={{ scale: 0.97 }}
              className="flex items-center space-x-3 px-10 py-4 rounded-2xl font-bold text-base text-[#080C15]"
              style={{ background: 'linear-gradient(135deg, #00D4FF 0%, #0EA5E9 100%)' }}
            >
              <span>Launch Security Operations Center</span>
              <ArrowRight className="w-5 h-5" />
            </motion.button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex items-center justify-center space-x-6 pt-2"
          >
            {['No installation required', 'All modules included', 'MIT Licensed'].map(t => (
              <div key={t} className="flex items-center space-x-1.5 text-xs text-slate-600">
                <CheckCircle2 className="w-3 h-3 text-[#22C55E]" />
                <span>{t}</span>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className="relative z-10 border-t pt-14 pb-8" style={{ borderColor: 'rgba(255,255,255,0.05)' }}>
        <div className="max-w-[1280px] mx-auto px-8">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-12">
            {/* Brand */}
            <div className="col-span-2 space-y-4">
              <div className="flex items-center space-x-3">
                <div className="w-9 h-9 rounded-xl flex items-center justify-center border" style={{ background: 'rgba(0,212,255,0.08)', borderColor: 'rgba(0,212,255,0.22)' }}>
                  <Shield className="w-4.5 h-4.5 text-[#00D4FF]" />
                </div>
                <div>
                  <span className="text-base font-bold">Sentinel<span className="text-[#00D4FF]">X</span> AI</span>
                  <div className="text-[10px] font-mono text-slate-600">Enterprise Security Platform</div>
                </div>
              </div>
              <p className="text-sm text-slate-500 leading-relaxed max-w-xs">
                AI-powered cybersecurity operations platform. Simulate, detect, explain, and report — end to end.
              </p>
              <div className="flex items-center space-x-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-mono border" style={{ background: 'rgba(255,255,255,0.03)', borderColor: 'rgba(255,255,255,0.07)', color: '#64748b' }}>v1.0.0</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono border" style={{ background: 'rgba(34,197,94,0.07)', borderColor: 'rgba(34,197,94,0.15)', color: '#22C55E' }}>MIT License</span>
              </div>
            </div>

            {/* Platform */}
            <div className="space-y-3">
              <p className="text-[11px] font-mono font-semibold tracking-[0.1em] text-slate-600 uppercase mb-4">Platform</p>
              {['Attack Simulation', 'Threat Investigation', 'Threat Intelligence', 'Model Performance', 'AI Explainability'].map(l => (
                <button key={l} onClick={onGetStarted} className="block text-sm text-slate-500 hover:text-slate-300 transition-colors text-left">{l}</button>
              ))}
            </div>

            {/* Resources */}
            <div className="space-y-3">
              <p className="text-[11px] font-mono font-semibold tracking-[0.1em] text-slate-600 uppercase mb-4">Resources</p>
              {[
                { label: 'API Docs', href: 'http://localhost:8000/docs' },
                { label: 'GitHub', href: 'https://github.com/Imchetan127/SentinelX-AI' },
                { label: 'About', action: onNavigateAbout },
              ].map(l => l.action ? (
                <button key={l.label} onClick={l.action} className="block text-sm text-slate-500 hover:text-slate-300 transition-colors text-left">{l.label}</button>
              ) : (
                <a key={l.label} href={l.href} target="_blank" rel="noopener noreferrer" className="block text-sm text-slate-500 hover:text-slate-300 transition-colors">{l.label}</a>
              ))}
            </div>

            {/* Engineering */}
            <div className="space-y-3">
              <p className="text-[11px] font-mono font-semibold tracking-[0.1em] text-slate-600 uppercase mb-4">Engineering</p>
              <p className="text-sm text-slate-500">Chetan B K</p>
              <p className="text-sm text-slate-500">H Deepak</p>
              <p className="text-sm text-slate-500">Nivas M R</p>
              <p className="text-sm text-slate-500">Kiran D</p>
              <p className="text-xs text-slate-600 mt-3 font-mono">Mentor: Sneha Karamadi</p>
            </div>
          </div>

          <div className="border-t pt-6 flex flex-col md:flex-row items-center justify-between gap-3" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
            <p className="text-xs text-slate-700 font-mono">© 2026 SentinelX AI. All rights reserved.</p>
            <p className="text-xs text-slate-700 font-mono text-center">
              Dept. of AI & Data Science · K.S. School of Engineering & Management, Bengaluru
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

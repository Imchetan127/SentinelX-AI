'use client';

import React, { useState } from 'react';
import { Shield, Server, Globe, Database, Terminal, CheckCircle2, Lock } from 'lucide-react';
import { motion } from 'framer-motion';

export const LiveNetworkMap: React.FC = () => {
  const [activeHoverNode, setActiveHoverNode] = useState<string | null>(null);

  const nodes = [
    { id: 'attacker', label: 'Adversary (Red Team)', ip: '185.220.101.5', protocol: 'HTTPS/TCP', latency: '42ms', threat: 'SQLi Payload', icon: Terminal, color: '#EF4444' },
    { id: 'internet', label: 'Public Internet / WAN', ip: '0.0.0.0/0', protocol: 'BGP/IP', latency: '12ms', threat: 'Encrypted Traffic', icon: Globe, color: '#F59E0B' },
    { id: 'firewall', label: 'WAF & Firewall Guard', ip: '10.0.1.1', protocol: 'TLS 1.3', latency: '2ms', threat: 'Rule Applied', icon: Lock, color: '#00D4FF' },
    { id: 'sentinelx', label: 'SentinelX AI Core', ip: '10.0.2.50', protocol: 'gRPC / Internal', latency: '1ms', threat: 'SHAP Inspection', icon: Shield, color: '#A78BFA' },
    { id: 'database', label: 'Protected Database', ip: '10.0.3.100', protocol: 'PostgreSQL SQL', latency: '0.5ms', threat: 'Access Shielded', icon: Database, color: '#22C55E' },
  ];

  return (
    <div className="card p-6 space-y-4 border-[var(--accent)]/20">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Shield className="w-4 h-4 text-[var(--accent)]" />
          <h3 className="text-sm font-bold text-[var(--text-primary)]">Enterprise Live Telemetry Network Map</h3>
        </div>
        <span className="text-[10px] font-mono text-[#22C55E] flex items-center space-x-1">
          <span className="w-1.5 h-1.5 rounded-full bg-[#22C55E] animate-ping" />
          <span>PACKET STREAM ACTIVE</span>
        </span>
      </div>

      {/* SVG Network Canvas */}
      <div className="relative bg-[#080C14] border border-[var(--border)] rounded-2xl p-6 overflow-hidden min-h-[220px] flex items-center justify-around">
        {/* Animated packet flow line */}
        <div className="absolute inset-x-12 top-1/2 -translate-y-1/2 h-[2px] bg-gradient-to-r from-[#EF4444] via-[#00D4FF] to-[#22C55E] opacity-30" />

        {/* Traveling packets */}
        <motion.div
          className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-[#EF4444] shadow-lg shadow-[#EF4444]/50 z-10"
          initial={{ left: '10%' }}
          animate={{ left: '50%' }}
          transition={{ duration: 2.5, repeat: Infinity, ease: 'linear' }}
        />
        <motion.div
          className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-[#22C55E] shadow-lg shadow-[#22C55E]/50 z-10"
          initial={{ left: '50%' }}
          animate={{ left: '90%' }}
          transition={{ duration: 2.5, repeat: Infinity, ease: 'linear', delay: 1.2 }}
        />

        {/* Nodes */}
        {nodes.map(n => {
          const Icon = n.icon;
          const isHovered = activeHoverNode === n.id;
          return (
            <div
              key={n.id}
              onMouseEnter={() => setActiveHoverNode(n.id)}
              onMouseLeave={() => setActiveHoverNode(null)}
              className="relative z-20 flex flex-col items-center cursor-pointer group"
            >
              <div
                className="w-12 h-12 rounded-2xl flex items-center justify-center border transition-all duration-200"
                style={{
                  backgroundColor: `${n.color}15`,
                  borderColor: isHovered ? n.color : `${n.color}40`,
                  boxShadow: isHovered ? `0 0 20px ${n.color}40` : 'none',
                }}
              >
                <Icon className="w-5 h-5" style={{ color: n.color }} />
              </div>
              <span className="text-[11px] font-mono font-bold text-[var(--text-primary)] mt-2">{n.label}</span>
              <span className="text-[9px] font-mono text-[var(--text-muted)]">{n.ip}</span>

              {/* Hover Tooltip Card */}
              {isHovered && (
                <motion.div
                  initial={{ opacity: 0, y: 8, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  className="absolute bottom-full mb-3 w-48 p-3 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hover)] shadow-2xl z-30 text-[10px] font-mono space-y-1"
                >
                  <div className="font-bold text-[var(--text-primary)]" style={{ color: n.color }}>{n.label}</div>
                  <div className="text-[var(--text-secondary)]">IP: {n.ip}</div>
                  <div className="text-[var(--text-secondary)]">Protocol: {n.protocol}</div>
                  <div className="text-[var(--text-secondary)]">Latency: {n.latency}</div>
                  <div className="text-[#22C55E] font-bold">Status: {n.threat}</div>
                </motion.div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

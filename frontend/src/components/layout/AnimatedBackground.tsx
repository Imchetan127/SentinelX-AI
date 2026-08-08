'use client';

import React from 'react';

export const AnimatedBackground: React.FC = () => {
  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden select-none">
      {/* 1. Slow Drifting Grid Pattern */}
      <div className="absolute inset-0 bg-grid-pattern opacity-[0.05]" />

      {/* 2. Top Centered Radial Ambient Cyan Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-[#00D4FF]/[0.03] blur-[120px] rounded-full" />

      {/* 3. Bottom Right Ambient Purple Glow */}
      <div className="absolute bottom-0 right-0 w-[800px] h-[450px] bg-purple-600/[0.02] blur-[140px] rounded-full" />

      {/* 4. Soft Floating Particle Dots */}
      <div className="absolute top-1/4 left-1/5 w-1.5 h-1.5 rounded-full bg-[#00D4FF]/20 animate-ping duration-[4000ms]" />
      <div className="absolute top-3/4 left-2/3 w-1 h-1 rounded-full bg-purple-400/20 animate-ping duration-[6000ms]" />
      <div className="absolute top-1/3 right-1/4 w-1.5 h-1.5 rounded-full bg-emerald-400/20 animate-ping duration-[5000ms]" />
    </div>
  );
};

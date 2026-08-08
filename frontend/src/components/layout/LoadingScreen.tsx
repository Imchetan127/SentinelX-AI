'use client';

import React, { useEffect, useState } from 'react';
import { Shield, Activity, CheckCircle2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface LoadingScreenProps {
  onComplete?: () => void;
}

export const LoadingScreen: React.FC<LoadingScreenProps> = ({ onComplete }) => {
  const steps = [
    'Initializing Security Operations Center Engine...',
    'Loading Supervised Machine Learning Models (Random Forest, XGBoost)...',
    'Establishing Secure Database & Audit Telemetry Session...',
    'Analyzing Real-Time Threat Intelligence Feeds...',
    'Preparing Executive SOC Dashboard...',
    'Ready.',
  ];

  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(15);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < steps.length - 1) {
          const next = prev + 1;
          setProgress(Math.min(100, Math.round(((next + 1) / steps.length) * 100)));
          return next;
        }
        clearInterval(timer);
        setTimeout(() => {
          onComplete?.();
        }, 400);
        return prev;
      });
    }, 450);

    return () => clearInterval(timer);
  }, [steps.length, onComplete]);

  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#090B10] text-slate-100 font-sans selection:bg-[#00D4FF]/20 select-none">
      {/* Ambient Top Glow */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-[#00D4FF]/[0.05] blur-[100px] rounded-full pointer-events-none" />

      <div className="w-full max-w-md p-8 flex flex-col items-center text-center space-y-8 relative z-10">
        {/* Shield Logo with Pulsing Ring */}
        <div className="relative flex items-center justify-center">
          <div className="absolute inset-0 rounded-2xl bg-[#00D4FF]/20 animate-ping duration-[3000ms]" />
          <div className="p-4 rounded-2xl bg-[#161B22] border border-[#00D4FF]/40 shadow-2xl relative">
            <Shield className="w-10 h-10 text-[#00D4FF]" />
          </div>
        </div>

        {/* Title & Tagline */}
        <div className="space-y-1">
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Sentinel<span className="text-[#00D4FF]">X</span> AI
          </h1>
          <p className="text-xs text-slate-400 font-mono tracking-widest uppercase">
            ENTERPRISE SOC PLATFORM
          </p>
        </div>

        {/* Dynamic Loading Step Text */}
        <div className="min-h-[48px] flex items-center justify-center w-full px-4">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.2 }}
              className="flex items-center space-x-2 text-xs font-mono text-[#00D4FF]"
            >
              {currentStep === steps.length - 1 ? (
                <CheckCircle2 className="w-4 h-4 text-[#2EE59D] flex-shrink-0" />
              ) : (
                <Activity className="w-4 h-4 text-[#00D4FF] animate-spin flex-shrink-0" />
              )}
              <span className={currentStep === steps.length - 1 ? 'text-[#2EE59D] font-bold' : ''}>
                {steps[currentStep]}
              </span>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Progress Bar */}
        <div className="w-full space-y-2">
          <div className="w-full bg-[#161B22] rounded-full h-1.5 overflow-hidden border border-white/[0.08]">
            <motion.div
              className="h-full bg-gradient-to-r from-[#00D4FF] via-purple-500 to-[#2EE59D] rounded-full"
              initial={{ width: '15%' }}
              animate={{ width: `${progress}%` }}
              transition={{ ease: 'easeOut', duration: 0.3 }}
            />
          </div>
          <div className="flex justify-between items-center text-[10px] font-mono text-slate-500">
            <span>SOC INTEGRITY CHECK</span>
            <span>{progress}%</span>
          </div>
        </div>
      </div>
    </div>
  );
};

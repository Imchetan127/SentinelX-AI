'use client';

import React, { useState, useEffect } from 'react';
import { Shield, Lock, User, Eye, EyeOff, CheckCircle2, ArrowRight, X, Radio } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = 'http://localhost:8000/api/v1';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: (username: string, role: string, token: string) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onLoginSuccess }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('analyst');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberDevice, setRememberDevice] = useState(true);

  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [authSuccess, setAuthSuccess] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const endpoint = mode === 'login' ? `${API_BASE}/auth/login` : `${API_BASE}/auth/register`;
    const payload = mode === 'login' ? { username, password } : { username, email, password, role };

    fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.message || data.detail || 'Authentication failed');
        }
        return data;
      })
      .then((data) => {
        setIsLoading(false);
        setAuthSuccess(true);
        setTimeout(() => {
          onLoginSuccess(data.username || username, data.role || role, data.access_token);
          onClose();
        }, 800);
      })
      .catch((err) => {
        setIsLoading(false);
        setError(err.message);
      });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#050B16]/90 backdrop-blur-xl p-4 overflow-y-auto select-none">
      {/* Background Telemetry Canvas */}
      <div className="absolute inset-0 pointer-events-none opacity-20 overflow-hidden">
        <svg className="w-full h-full stroke-white/[0.06]" fill="none">
          <defs>
            <pattern id="socGrid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" strokeWidth="0.5" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#socGrid)" />
        </svg>
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-[#00D4FF]/[0.05] blur-[140px] rounded-full" />
      </div>

      {/* Login Security Panel (Glassmorphism ~560px width) */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 15 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 15 }}
        transition={{ duration: 0.25, ease: 'easeOut' }}
        className="relative w-full max-w-[560px] p-8 sm:p-10 rounded-3xl bg-[#0F172A]/85 border border-white/[0.08] shadow-[0_25px_70px_rgba(0,0,0,0.7)] backdrop-blur-2xl space-y-6 z-10 my-8"
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-6 right-6 p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/[0.06] transition-colors cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Header & Logo */}
        <div className="text-center space-y-3">
          <motion.div
            animate={{ y: [0, -4, 0] }}
            transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
            className="inline-flex p-3.5 rounded-2xl bg-[#00D4FF]/10 border border-[#00D4FF]/30 text-[#00D4FF] shadow-[0_0_30px_rgba(0,212,255,0.25)]"
          >
            <Shield className="w-8 h-8" />
          </motion.div>

          <div>
            <h2 className="text-2xl font-extrabold text-white tracking-tight flex items-center justify-center space-x-2">
              <span>Sentinel<span className="text-[#00D4FF]">X</span> AI</span>
            </h2>
            <p className="text-xs font-mono font-semibold text-[#00D4FF] tracking-wider uppercase mt-1">
              Enterprise Security Operations Center
            </p>
          </div>

          {/* Glowing Shield Divider */}
          <div className="flex items-center justify-center space-x-3 py-1">
            <div className="h-[1px] bg-gradient-to-r from-transparent via-white/[0.12] to-transparent w-full max-w-xs" />
            <Shield className="w-3 h-3 text-[#00D4FF] flex-shrink-0" />
            <div className="h-[1px] bg-gradient-to-r from-transparent via-white/[0.12] to-transparent w-full max-w-xs" />
          </div>

          {/* Welcome Subtitle */}
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight">
              {mode === 'login' ? 'Welcome Back' : 'Request Security Access'}
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              {mode === 'login'
                ? 'Sign in to continue monitoring your enterprise security environment.'
                : 'Create an analyst account to access the SentinelX AI threat platform.'}
            </p>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-3.5 rounded-xl bg-[#EF4444]/10 border border-[#EF4444]/30 text-[#EF4444] text-xs font-mono text-center"
          >
            {error}
          </motion.div>
        )}

        {/* Authentication Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Username */}
          <div className="space-y-1.5">
            <label className="text-xs font-mono text-slate-300 font-semibold block">Username / Analyst ID</label>
            <div className="relative">
              <User className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
              <input
                type="text"
                autoFocus
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
                className="w-full bg-[#080C14] border border-white/[0.08] focus:border-[#00D4FF] focus:ring-2 focus:ring-[#00D4FF]/20 rounded-xl pl-10 pr-4 py-3 text-xs text-white placeholder-slate-500 transition-all font-mono outline-none"
              />
            </div>
          </div>

          {/* Email (Register mode) */}
          {mode === 'register' && (
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-300 font-semibold block">Corporate Email Address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="analyst@company.com"
                className="w-full bg-[#080C14] border border-white/[0.08] focus:border-[#00D4FF] focus:ring-2 focus:ring-[#00D4FF]/20 rounded-xl px-4 py-3 text-xs text-white placeholder-slate-500 transition-all font-mono outline-none"
              />
            </div>
          )}

          {/* Password */}
          <div className="space-y-1.5">
            <label className="text-xs font-mono text-slate-300 font-semibold block">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
              <input
                type={showPassword ? 'text' : 'password'}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full bg-[#080C14] border border-white/[0.08] focus:border-[#00D4FF] focus:ring-2 focus:ring-[#00D4FF]/20 rounded-xl pl-10 pr-10 py-3 text-xs text-white placeholder-slate-500 transition-all font-mono outline-none"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-3.5 text-slate-500 hover:text-white transition-colors cursor-pointer"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Assigned Role (Register mode) */}
          {mode === 'register' && (
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-300 font-semibold block">Assigned Security Role</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full bg-[#080C14] border border-white/[0.08] focus:border-[#00D4FF] rounded-xl px-4 py-3 text-xs text-white font-mono outline-none"
              >
                <option value="user">User</option>
                <option value="analyst">SOC Analyst</option>
                <option value="admin">Administrator</option>
              </select>
            </div>
          )}

          {/* Remember Me & Forgot Password */}
          {mode === 'login' && (
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 pt-1">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberDevice}
                  onChange={(e) => setRememberDevice(e.target.checked)}
                  className="rounded border-white/[0.1] bg-[#080C14] text-[#00D4FF] focus:ring-[#00D4FF]/30 cursor-pointer"
                />
                <span>Remember this device</span>
              </label>
              <button type="button" className="hover:text-[#00D4FF] hover:underline transition-all cursor-pointer">
                Forgot Password?
              </button>
            </div>
          )}

          {/* Primary Action Button */}
          <motion.button
            type="submit"
            disabled={isLoading || authSuccess}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            className={`w-full py-3.5 rounded-xl font-bold text-xs font-mono flex items-center justify-center space-x-2 transition-all shadow-lg cursor-pointer ${
              authSuccess
                ? 'bg-[#22C55E] text-[#080C15]'
                : 'bg-gradient-to-r from-[#00D4FF] to-[#2563EB] text-[#080C15] hover:brightness-110 shadow-[#00D4FF]/20'
            } disabled:opacity-50`}
          >
            {authSuccess ? (
              <>
                <CheckCircle2 className="w-4 h-4" />
                <span>✓ Authentication Successful</span>
              </>
            ) : isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-[#080C15]/30 border-t-[#080C15] rounded-full animate-spin" />
                <span>Authenticating Credentials...</span>
              </>
            ) : (
              <>
                <span>{mode === 'login' ? 'Access Security Workspace' : 'Submit Access Request'}</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </motion.button>
        </form>

        {/* SSO Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-center space-x-3">
            <div className="h-[1px] bg-white/[0.08] flex-1" />
            <span className="text-[10px] font-mono text-slate-500 uppercase">OR</span>
            <div className="h-[1px] bg-white/[0.08] flex-1" />
          </div>

          <button
            type="button"
            className="w-full py-3 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.08] text-xs font-mono font-semibold text-slate-300 flex items-center justify-center space-x-2 transition-all cursor-pointer"
          >
            <Shield className="w-4 h-4 text-[#00D4FF]" />
            <span>Continue with Enterprise SSO</span>
          </button>
        </div>

        {/* Security & System Status */}
        <div className="pt-3 border-t border-white/[0.08] space-y-3">
          <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400">
            <div className="flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#22C55E] animate-pulse" />
              <span>TLS 1.3 Encrypted</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#22C55E] animate-pulse" />
              <span>JWT Authentication</span>
            </div>
          </div>

          {/* Compliance Pills */}
          <div className="flex items-center justify-center space-x-2 pt-1 font-mono text-[9px]">
            {['ISO 27001', 'SOC 2', 'GDPR', 'JWT', 'Secure by Design'].map((badge) => (
              <span
                key={badge}
                className="px-2 py-0.5 rounded bg-white/[0.04] text-slate-400 border border-white/[0.06]"
              >
                {badge}
              </span>
            ))}
          </div>
        </div>

        {/* Toggle Mode */}
        <div className="text-center text-xs font-mono text-slate-400">
          {mode === 'login' ? (
            <p>
              Don't have an account?{' '}
              <button
                onClick={() => setMode('register')}
                className="text-[#00D4FF] hover:underline font-bold transition-all cursor-pointer"
              >
                Request Access →
              </button>
            </p>
          ) : (
            <p>
              Already registered?{' '}
              <button
                onClick={() => setMode('login')}
                className="text-[#00D4FF] hover:underline font-bold transition-all cursor-pointer"
              >
                Back to Sign In →
              </button>
            </p>
          )}
        </div>
      </motion.div>
    </div>
  );
};

import React, { useState } from 'react';
import { Shield, Lock, User, Mail, Key, X } from 'lucide-react';

const API_BASE = 'http://localhost:8000/api/v1';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: (username: string, role: string, token: string) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onLoginSuccess }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [username, setUsername] = useState('analyst');
  const [email, setEmail] = useState('analyst@cyber-defense.org');
  const [password, setPassword] = useState('analyst123');
  const [role, setRole] = useState('analyst');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

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
        onLoginSuccess(data.username || username, data.role || role, data.access_token);
        onClose();
      })
      .catch((err) => {
        setIsLoading(false);
        setError(err.message);
      });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
      <div className="bg-[#161B22] w-full max-w-md p-8 rounded-2xl border border-white/[0.08] shadow-2xl relative space-y-6">
        <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-[#00D4FF]/10 text-[#00D4FF] border border-[#00D4FF]/20">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">
                {mode === 'login' ? 'Security Portal Access' : 'Create Researcher Account'}
              </h3>
              <p className="text-[11px] text-slate-400 font-mono">SentinelX AI Platform</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.05]">
            <X className="w-4 h-4" />
          </button>
        </div>

        {error && (
          <div className="p-3.5 rounded-xl bg-[#FF5D73]/10 border border-[#FF5D73]/30 text-[#FF5D73] text-xs font-mono">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs font-mono">
          <div>
            <label className="text-slate-400 block mb-1">Username:</label>
            <div className="relative">
              <User className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-[#090B10] border border-white/[0.08] rounded-xl pl-9 pr-4 py-2.5 text-slate-200 focus:outline-none focus:border-[#00D4FF]/50"
                placeholder="Enter username"
              />
            </div>
          </div>

          {mode === 'register' && (
            <div>
              <label className="text-slate-400 block mb-1">Email Address:</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-[#090B10] border border-white/[0.08] rounded-xl pl-9 pr-4 py-2.5 text-slate-200 focus:outline-none focus:border-[#00D4FF]/50"
                  placeholder="analyst@domain.com"
                />
              </div>
            </div>
          )}

          <div>
            <label className="text-slate-400 block mb-1">Password:</label>
            <div className="relative">
              <Key className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-[#090B10] border border-white/[0.08] rounded-xl pl-9 pr-4 py-2.5 text-slate-200 focus:outline-none focus:border-[#00D4FF]/50"
                placeholder="••••••••"
              />
            </div>
          </div>

          {mode === 'register' && (
            <div>
              <label className="text-slate-400 block mb-1">Assigned Security Role:</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full bg-[#090B10] border border-white/[0.08] rounded-xl px-4 py-2.5 text-slate-200 focus:outline-none focus:border-[#00D4FF]/50"
              >
                <option value="user">User</option>
                <option value="analyst">Analyst</option>
                <option value="admin">Admin</option>
              </select>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 rounded-xl bg-[#00D4FF] hover:bg-[#00D4FF]/90 text-slate-950 font-bold text-xs font-mono flex items-center justify-center space-x-2 transition-all shadow-md disabled:opacity-50"
          >
            <Lock className="w-4 h-4" />
            <span>{isLoading ? 'Authenticating...' : (mode === 'login' ? 'Authenticate & Enter Portal' : 'Register Account')}</span>
          </button>
        </form>

        <div className="pt-2 text-center text-xs font-mono text-slate-400 border-t border-white/[0.08]">
          {mode === 'login' ? (
            <p>
              Need an account?{' '}
              <button onClick={() => setMode('register')} className="text-[#00D4FF] underline font-bold">
                Register Here
              </button>
            </p>
          ) : (
            <p>
              Already registered?{' '}
              <button onClick={() => setMode('login')} className="text-[#00D4FF] underline font-bold">
                Log In Here
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

import React, { useState } from 'react';
import { Shield, Lock, User, Mail, Key } from 'lucide-react';

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
      <div className="glass-panel w-full max-w-md p-8 rounded-3xl border border-cyan-500/30 glow-blue relative space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <Shield className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white tracking-wider">
                {mode === 'login' ? 'Security Portal Access' : 'Create Researcher Account'}
              </h3>
              <p className="text-xs text-slate-400 font-mono">Red Team vs Blue Team Platform</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-xl">✕</button>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-rose-500/20 border border-rose-500/40 text-rose-300 text-xs font-mono">
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
                className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2.5 text-slate-200 focus:outline-none focus:border-cyan-500"
                placeholder="enter username"
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
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2.5 text-slate-200 focus:outline-none focus:border-cyan-500"
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
                className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2.5 text-slate-200 focus:outline-none focus:border-cyan-500"
                placeholder="••••••••"
              />
            </div>
          </div>

          {mode === 'register' && (
            <div>
              <label className="text-slate-400 block mb-1">User Role:</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-slate-200 focus:outline-none focus:border-cyan-500"
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
            className="w-full py-3 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs font-mono flex items-center justify-center space-x-2 transition-all glow-blue disabled:opacity-50"
          >
            <Lock className="w-4 h-4" />
            <span>{isLoading ? 'Authenticating...' : (mode === 'login' ? 'Authenticate & Enter Portal' : 'Register Account')}</span>
          </button>
        </form>

        <div className="pt-2 text-center text-xs font-mono text-slate-400">
          {mode === 'login' ? (
            <p>
              Need an account?{' '}
              <button onClick={() => setMode('register')} className="text-cyan-400 underline font-bold">
                Register Here
              </button>
            </p>
          ) : (
            <p>
              Already registered?{' '}
              <button onClick={() => setMode('login')} className="text-cyan-400 underline font-bold">
                Log In Here
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

import React from 'react';
import { Shield, Flame, Activity, Brain, Cpu, Mail, User, LogOut, Home } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  user: { username: string; role: string } | null;
  onOpenLogin: () => void;
  onLogout: () => void;
  onGoHome: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  user,
  onOpenLogin,
  onLogout,
  onGoHome,
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Security Dashboard', icon: Activity },
    { id: 'red-team', label: 'Red Team Simulator', icon: Flame },
    { id: 'blue-team', label: 'Blue Team AI Inspector', icon: Shield },
    { id: 'email-url-lab', label: 'Spam Email & URL Lab', icon: Mail },
    { id: 'ml-engine', label: 'ML Benchmarks & Trainer', icon: Cpu },
    { id: 'explainability', label: 'Explainable AI (XAI)', icon: Brain },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-cyan-500/20 px-8 py-4 flex items-center justify-between min-w-[1024px]">
      <div className="flex items-center space-x-4">
        <button
          onClick={onGoHome}
          className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-cyan-500/40 text-slate-300 hover:text-cyan-400 transition-all flex items-center space-x-1"
          title="Return to Home Landing Page"
        >
          <Home className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
          <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/40 glow-blue">
            <Shield className="w-6 h-6 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-wider gradient-text-blue">
              CYBER-AI DISRUPT
            </h1>
            <p className="text-xs text-slate-400 uppercase tracking-widest font-mono">Red Team vs Blue Team Framework</p>
          </div>
        </div>
      </div>

      <nav className="flex items-center space-x-1 bg-slate-900/80 p-1.5 rounded-xl border border-slate-800 font-mono text-xs">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center space-x-2 px-4 py-2.5 rounded-lg font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm glow-blue'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : ''}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="flex items-center space-x-3 font-mono text-xs">
        {user ? (
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-200">
              <User className="w-4 h-4 text-cyan-400" />
              <span className="font-bold text-sm tracking-wide text-white">{user.username}</span>
              <span
                className={`text-[10px] px-2.5 py-0.5 rounded-md uppercase tracking-wider ${
                  (user.role || 'USER').toUpperCase() === 'ADMIN'
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                    : (user.role || 'USER').toUpperCase().includes('ANALYST')
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                    : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                }`}
              >
                {(user.role || 'USER').toUpperCase()}
              </span>
            </div>
            <button
              onClick={onLogout}
              className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-rose-500/40 text-slate-400 hover:text-rose-400 transition-all"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (

          <button
            onClick={onOpenLogin}
            className="px-5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs font-mono transition-all glow-blue"
          >
            Sign In / Register
          </button>
        )}
      </div>
    </header>
  );
};

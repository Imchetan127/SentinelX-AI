'use client';

import React, { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Navbar } from '@/components/layout/Navbar';
import { Sidebar } from '@/components/layout/Sidebar';
import { CommandPalette } from '@/components/layout/CommandPalette';
import { AiCopilot } from '@/components/layout/AiCopilot';
import { Footer } from '@/components/layout/Footer';
import { LandingPage } from '@/components/landing/LandingPage';
import { AuthModal } from '@/components/auth/AuthModal';
import { DashboardView } from '@/components/dashboard/DashboardView';
import { RedTeamView } from '@/components/red_team/RedTeamView';
import { BlueTeamView } from '@/components/blue_team/BlueTeamView';
import { EmailUrlLabView } from '@/components/email_url_lab/EmailUrlLabView';
import { MLEngineView } from '@/components/ml_engine/MLEngineView';
import { ExplainabilityView } from '@/components/explainability/ExplainabilityView';
import { AboutView } from '@/components/about/AboutView';
import { SettingsView } from '@/components/settings/SettingsView';

const API_BASE = 'http://localhost:8000/api/v1';

export default function Home() {
  const [viewMode, setViewMode] = useState<'landing' | 'workspace'>('landing');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [user, setUser] = useState<{ username: string; role: string } | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedAttackId, setSelectedAttackId] = useState<string | null>(null);

  // Session restoration
  useEffect(() => {
    const token = sessionStorage.getItem('rb_auth_token');
    if (!token) { setIsLoading(false); return; }

    fetch(`${API_BASE}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then(async r => {
        const data = await r.json();
        if (r.ok && data.success && data.user) {
          setUser(data.user);
          setViewMode('workspace');
        } else {
          sessionStorage.removeItem('rb_auth_token');
        }
      })
      .catch(() => sessionStorage.removeItem('rb_auth_token'))
      .finally(() => setIsLoading(false));
  }, []);

  const handleLoginSuccess = (username: string, role: string, token: string) => {
    sessionStorage.setItem('rb_auth_token', token);
    setUser({ username, role });
    setViewMode('workspace');
    setIsAuthModalOpen(false);
  };

  const handleLogout = () => {
    const token = sessionStorage.getItem('rb_auth_token');
    if (token) {
      fetch(`${API_BASE}/auth/logout`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } }).catch(() => {});
    }
    sessionStorage.removeItem('rb_auth_token');
    setUser(null);
    setViewMode('landing');
  };

  const handleNavigateToAttack = (attackId: string, targetTab: string = 'blue-team') => {
    setSelectedAttackId(attackId);
    setActiveTab(targetTab);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen ambient-bg flex items-center justify-center">
        <div className="flex items-center space-x-3 text-[#94A3B8] font-mono text-sm">
          <div className="w-4 h-4 border-2 border-[#00D4FF]/30 border-t-[#00D4FF] rounded-full animate-spin" />
          <span>Initializing SentinelX AI v5.0 SOC...</span>
        </div>
      </div>
    );
  }

  // Landing page view
  if (viewMode === 'landing') {
    return (
      <>
        <LandingPage
          onGetStarted={() => setIsAuthModalOpen(true)}
          onOpenLogin={() => setIsAuthModalOpen(true)}
          onNavigateAbout={() => {
            setViewMode('workspace');
            setActiveTab('about');
          }}
        />
        <AuthModal
          isOpen={isAuthModalOpen}
          onClose={() => setIsAuthModalOpen(false)}
          onLoginSuccess={handleLoginSuccess}
        />
      </>
    );
  }

  // Enterprise SOC Workspace View
  return (
    <div className="min-h-screen flex bg-[var(--bg-base)] overflow-x-hidden">
      {/* Enterprise Collapsible Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Workspace Column */}
      <div className="flex-1 flex flex-col min-w-0 min-h-screen">
        <Navbar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          user={user}
          onOpenLogin={() => setIsAuthModalOpen(true)}
          onLogout={handleLogout}
          onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
        />

        <main className="flex-1 p-6 md:p-8 max-w-[1500px] w-full mx-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.2, ease: 'easeOut' }}
            >
              {activeTab === 'dashboard'    && <DashboardView username={user?.username} />}
              {activeTab === 'red-team'     && <RedTeamView onNavigateToAttack={handleNavigateToAttack} />}
              {activeTab === 'blue-team'    && <BlueTeamView attackId={selectedAttackId} onNavigateToExplainability={(id) => handleNavigateToAttack(id, 'explainability')} />}
              {activeTab === 'email-url-lab'&& <EmailUrlLabView />}
              {activeTab === 'ml-engine'    && <MLEngineView />}
              {activeTab === 'explainability'&&<ExplainabilityView attackId={selectedAttackId} />}
              {activeTab === 'about'        && <AboutView attackId={selectedAttackId} />}
              {activeTab === 'settings'     && <SettingsView user={user} />}
            </motion.div>
          </AnimatePresence>
        </main>

        <Footer onNavigate={setActiveTab} />
      </div>

      {/* Global Command Palette (Ctrl+K) */}
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        setActiveTab={setActiveTab}
        onLogout={handleLogout}
      />

      {/* Floating AI Copilot Assistant */}
      <AiCopilot setActiveTab={setActiveTab} />

      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onLoginSuccess={handleLoginSuccess}
      />
    </div>
  );
}

'use client';

import React, { useEffect, useState } from 'react';
import { Navbar } from '@/components/layout/Navbar';
import { LandingPage } from '@/components/landing/LandingPage';
import { AuthModal } from '@/components/auth/AuthModal';
import { DashboardView } from '@/components/dashboard/DashboardView';
import { RedTeamView } from '@/components/red_team/RedTeamView';
import { BlueTeamView } from '@/components/blue_team/BlueTeamView';
import { EmailUrlLabView } from '@/components/email_url_lab/EmailUrlLabView';
import { MLEngineView } from '@/components/ml_engine/MLEngineView';
import { ExplainabilityView } from '@/components/explainability/ExplainabilityView';

const API_BASE = 'http://localhost:8000/api/v1';

export default function Home() {
  const [viewMode, setViewMode] = useState<'landing' | 'workspace'>('landing');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [user, setUser] = useState<{ username: string; role: string; id?: string } | null>(null);
  const [isAuthLoading, setIsAuthLoading] = useState(true);

  useEffect(() => {
    const verifySession = async () => {
      const token = sessionStorage.getItem('rb_auth_token');
      if (!token) {
        setIsAuthLoading(false);
        return;
      }

      try {
        const response = await fetch(`${API_BASE}/auth/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Unauthorized');
        }

        const data = await response.json();
        if (data.success && data.user) {
          setUser(data.user);
          setViewMode('workspace');
        } else {
          sessionStorage.removeItem('rb_auth_token');
        }
      } catch {
        sessionStorage.removeItem('rb_auth_token');
        setUser(null);
        setViewMode('landing');
      } finally {
        setIsAuthLoading(false);
      }
    };

    verifySession();
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
      fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }).catch(() => undefined);
    }

    sessionStorage.removeItem('rb_auth_token');
    setUser(null);
    setViewMode('landing');
  };

  if (isAuthLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#090d16] text-cyan-300 font-mono">
        Verifying authentication...
      </div>
    );
  }

  if (viewMode === 'landing') {
    return (
      <>
        <LandingPage
          onGetStarted={() => setIsAuthModalOpen(true)}
          onOpenLogin={() => setIsAuthModalOpen(true)}
        />
        <AuthModal
          isOpen={isAuthModalOpen}
          onClose={() => setIsAuthModalOpen(false)}
          onLoginSuccess={handleLoginSuccess}
        />
      </>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#090d16] min-w-[1280px]">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        user={user}
        onOpenLogin={() => setIsAuthModalOpen(true)}
        onLogout={handleLogout}
        onGoHome={() => setViewMode('landing')}
      />
      <main className="flex-1 p-8 max-w-[1600px] mx-auto w-full">
        {activeTab === 'dashboard' && <DashboardView />}
        {activeTab === 'red-team' && <RedTeamView />}
        {activeTab === 'blue-team' && <BlueTeamView />}
        {activeTab === 'email-url-lab' && <EmailUrlLabView />}
        {activeTab === 'ml-engine' && <MLEngineView />}
        {activeTab === 'explainability' && <ExplainabilityView />}
      </main>

      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onLoginSuccess={handleLoginSuccess}
      />
    </div>
  );
}

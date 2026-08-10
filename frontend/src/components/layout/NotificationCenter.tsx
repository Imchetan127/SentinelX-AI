'use client';

import React, { useState, useEffect } from 'react';
import { Bell, Flame, ShieldAlert, FileText, CheckCircle2, X, AlertTriangle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { formatStandardDate } from '@/utils/dateFormatter';

const API_BASE = 'http://localhost:8000/api/v1';

async function authFetch(path: string, init: RequestInit = {}) {
  const token = sessionStorage.getItem('rb_auth_token');
  const headers = { ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(init.headers || {}) };
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  return response;
}

interface NotificationCenterProps {
  setActiveTab: (tab: string) => void;
}

interface NotificationItem {
  id: string;
  title: string;
  desc: string;
  time: string;
  rawDate: Date;
  type: string;
  tab: string;
  severity: string;
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({ setActiveTab }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchRealEvents = async () => {
    try {
      const res = await authFetch('/attacks/');
      if (res.ok) {
        const attacks = await res.json();
        const items: NotificationItem[] = attacks.slice(0, 8).map((atk: any) => ({
          id: atk.id,
          title: `${atk.attack_type} Event`,
          desc: `Vector ID: ${atk.id.substring(0, 8)}... | Severity: ${atk.severity}`,
          time: formatStandardDate(atk.created_at || new Date()),
          rawDate: new Date(atk.created_at || Date.now()),
          type: atk.severity === 'CRITICAL' ? 'threat' : 'attack',
          tab: 'blue-team',
          severity: atk.severity,
        }));

        setNotifications(items);

        // Check unread count based on lastSeenTimestamp
        const lastSeen = sessionStorage.getItem('sentinelx_last_notification_seen');
        const lastSeenTime = lastSeen ? new Date(lastSeen).getTime() : 0;
        const newUnread = items.filter(n => n.rawDate.getTime() > lastSeenTime).length;
        setUnreadCount(newUnread);
      }
    } catch (err) {
      // Graceful fallback if backend offline
    }
  };

  useEffect(() => {
    fetchRealEvents();
    const interval = setInterval(fetchRealEvents, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleOpenDropdown = () => {
    setIsOpen(!isOpen);
    setUnreadCount(0);
    sessionStorage.setItem('sentinelx_last_notification_seen', new Date().toISOString());
  };

  const handleNotificationClick = (tab: string) => {
    setActiveTab(tab);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={handleOpenDropdown}
        className="relative p-2 rounded-xl bg-[var(--bg-surface)] hover:bg-white/[0.08] border border-[var(--border)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-all cursor-pointer"
        title="SOC Notification Center"
      >
        <Bell className="w-4 h-4" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-[#EF4444] text-white text-[10px] font-mono font-bold flex items-center justify-center animate-bounce">
            {unreadCount}
          </span>
        )}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ duration: 0.18 }}
            className="absolute right-0 mt-2 w-80 sm:w-96 bg-[var(--bg-card)] border border-[var(--border-hover)] rounded-2xl shadow-2xl overflow-hidden z-50 font-mono text-xs"
          >
            {/* Header */}
            <div className="p-4 border-b border-[var(--border)] bg-[var(--bg-surface)] flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Bell className="w-4 h-4 text-[var(--accent)]" />
                <span className="text-xs font-bold text-white uppercase">Real SOC Telemetry Stream</span>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Event List */}
            <div className="max-h-80 overflow-y-auto divide-y divide-white/[0.04]">
              {notifications.length === 0 ? (
                <div className="p-6 text-center text-slate-500 text-[11px]">
                  No real attack events logged in database yet.
                </div>
              ) : (
                notifications.map((n) => (
                  <button
                    key={n.id}
                    onClick={() => handleNotificationClick(n.tab)}
                    className="w-full p-3.5 hover:bg-white/[0.04] transition-colors text-left flex items-start space-x-3 cursor-pointer group"
                  >
                    <div className={`p-2 rounded-xl flex-shrink-0 mt-0.5 ${
                      n.severity === 'CRITICAL' ? 'bg-[#EF4444]/15 text-[#EF4444]' : 'bg-[#F59E0B]/15 text-[#F59E0B]'
                    }`}>
                      {n.severity === 'CRITICAL' ? <ShieldAlert className="w-4 h-4" /> : <Flame className="w-4 h-4" />}
                    </div>
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-white group-hover:text-[var(--accent)] transition-colors">
                          {n.title}
                        </span>
                        <span className="text-[10px] text-slate-500">{n.time}</span>
                      </div>
                      <p className="text-[11px] text-slate-400 leading-relaxed">{n.desc}</p>
                    </div>
                  </button>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

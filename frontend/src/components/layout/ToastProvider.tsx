'use client';

import React, { createContext, useContext, useState } from 'react';
import { CheckCircle2, AlertTriangle, Info, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export interface Toast {
  id: string;
  type: 'success' | 'warning' | 'error' | 'info';
  title: string;
  message: string;
}

interface ToastContextType {
  showToast: (title: string, message: string, type?: Toast['type']) => void;
}

const ToastContext = createContext<ToastContextType>({
  showToast: () => {},
});

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = (title: string, message: string, type: Toast['type'] = 'success') => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts(prev => [...prev, { id, type, title, message }]);

    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4000);
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div className="fixed top-20 right-6 z-50 space-y-2 max-w-sm pointer-events-none">
        <AnimatePresence>
          {toasts.map(toast => (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, x: 20, scale: 0.95 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 20, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className="pointer-events-auto p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hover)] shadow-2xl flex items-start space-x-3"
            >
              <div className="mt-0.5">
                {toast.type === 'success' && <CheckCircle2 className="w-4 h-4 text-[#22C55E]" />}
                {toast.type === 'warning' && <AlertTriangle className="w-4 h-4 text-[#F59E0B]" />}
                {toast.type === 'error' && <AlertTriangle className="w-4 h-4 text-[#EF4444]" />}
                {toast.type === 'info' && <Info className="w-4 h-4 text-[var(--accent)]" />}
              </div>
              <div className="flex-1 space-y-0.5">
                <h5 className="text-xs font-bold text-[var(--text-primary)]">{toast.title}</h5>
                <p className="text-[11px] text-[var(--text-secondary)] leading-relaxed">{toast.message}</p>
              </div>
              <button
                onClick={() => removeToast(toast.id)}
                className="text-[var(--text-muted)] hover:text-white transition-colors"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => useContext(ToastContext);

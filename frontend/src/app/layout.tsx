import type { Metadata } from 'next';
import './globals.css';
import { ThemeProvider } from '@/context/ThemeContext';
import { ToastProvider } from '@/components/layout/ToastProvider';

export const metadata: Metadata = {
  title: 'SentinelX AI — Enterprise Security Operations Center v5.0',
  description: 'Autonomous Red Team Simulation, Blue Team AI Detection, SHAP Explainability & SOC Incident Reporting Platform.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-theme="midnight-blue">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="ambient-bg text-slate-100 antialiased min-h-screen selection:bg-[#00D4FF]/15 selection:text-[#00D4FF]">
        <ThemeProvider>
          <ToastProvider>
            {children}
          </ToastProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}

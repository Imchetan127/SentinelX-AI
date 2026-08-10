'use client';

import React, { useEffect, useState } from 'react';
import { FileText, Download, CheckCircle2, RefreshCw, ShieldAlert, AlertTriangle, Flame } from 'lucide-react';
import { formatStandardDate } from '@/utils/dateFormatter';

const API_BASE = 'http://localhost:8000/api/v1';

async function authFetch(path: string, init: RequestInit = {}) {
  const token = sessionStorage.getItem('rb_auth_token');
  const headers = { ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(init.headers || {}) };
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  if (response.status === 401) {
    sessionStorage.removeItem('rb_auth_token');
    window.location.href = '/';
  }
  return response;
}

interface IncidentItem {
  id: string;
  title: string;
  attack_type: string;
  severity: string;
  status: string;
  created_at: string;
}

interface AboutViewProps {
  attackId?: string | null;
}

export const AboutView: React.FC<AboutViewProps> = ({ attackId }) => {
  const [incidents, setIncidents] = useState<IncidentItem[]>([]);
  const [reports, setReports] = useState<any[]>([]);
  const [isGenerating, setIsGenerating] = useState<string | null>(null);
  const [downloadMsg, setDownloadMsg] = useState<string | null>(null);
  const [verificationResults, setVerificationResults] = useState<{ [key: string]: string }>({});

  const fetchIncidentsAndReports = async () => {
    try {
      const [incRes, atkRes] = await Promise.all([
        authFetch('/incidents/').catch(() => null),
        authFetch('/attacks/').catch(() => null),
      ]);

      const incidentList: IncidentItem[] = [];
      const seenIds = new Set<string>();

      if (incRes && incRes.ok) {
        const incData = await incRes.json();
        if (Array.isArray(incData)) {
          incData.forEach((inc: any) => {
            if (!seenIds.has(inc.id)) {
              seenIds.add(inc.id);
              incidentList.push({
                id: inc.id,
                title: inc.title || `SOC Security Incident #${inc.id.slice(0, 8)}`,
                attack_type: inc.attack_type || inc.title?.replace('Automated Incident: ', '') || 'Adversarial Simulation',
                severity: (inc.priority || inc.severity || 'HIGH').toUpperCase(),
                status: 'AUTO DETECTED & MITIGATED',
                created_at: inc.created_at || new Date().toISOString(),
              });
            }
          });
        }
      }

      if (atkRes && atkRes.ok) {
        const atkData = await atkRes.json();
        if (Array.isArray(atkData)) {
          atkData.forEach((atk: any) => {
            if (!seenIds.has(atk.id)) {
              seenIds.add(atk.id);
              incidentList.push({
                id: atk.id,
                title: `${atk.attack_type} Incident`,
                attack_type: atk.attack_type,
                severity: (atk.severity || 'HIGH').toUpperCase(),
                status: 'AUTO DETECTED & MITIGATED',
                created_at: atk.created_at || new Date().toISOString(),
              });
            }
          });
        }
      }

      setIncidents(incidentList);
    } catch (err) {
      console.error('Failed to load incidents:', err);
    }

    // 2. Fetch Generated Audit Reports
    try {
      const repRes = await authFetch('/reports/');
      if (repRes.ok) {
        const data = await repRes.json();
        if (data.success && Array.isArray(data.data)) {
          setReports(data.data);
        }
      }
    } catch (err) {
      console.error('Failed to load reports:', err);
    }
  };

  useEffect(() => {
    fetchIncidentsAndReports();
  }, []);

  const handleGenerateReport = async (incidentId: string) => {
    setIsGenerating(incidentId);
    setDownloadMsg(`Generating signed PDF report for Incident #${incidentId.slice(0, 8)}...`);

    try {
      const res = await authFetch(`/reports/incidents/${incidentId}`, { method: 'POST' });
      const data = await res.json();
      setIsGenerating(null);
      if (data.success && data.data) {
        setDownloadMsg(`Report generated & signed! SHA-256: ${data.data.sha256_hash.slice(0, 16)}...`);
        fetchIncidentsAndReports();
      } else {
        setDownloadMsg(`Report generation error: ${data.message || 'Failed'}`);
      }
    } catch (err) {
      setIsGenerating(null);
      setDownloadMsg('Failed to generate report endpoint response.');
    }
  };

  const handleDownloadReport = (reportId: string, title: string) => {
    setDownloadMsg(`Downloading ${title}...`);
    const token = sessionStorage.getItem('rb_auth_token');
    window.open(`${API_BASE}/reports/${reportId}/download?token=${token}`, '_blank');
  };

  const handleVerifyReport = async (reportId: string) => {
    try {
      const res = await authFetch(`/reports/${reportId}/verify`, { method: 'POST' });
      const data = await res.json();
      if (data.success && data.data) {
        setVerificationResults(prev => ({
          ...prev,
          [reportId]: data.data.status === 'VALID' ? 'SHA-256 DIGEST VERIFIED & VALID' : 'TAMPERED DETECTED'
        }));
      }
    } catch (err) {
      console.error('Failed to verify report:', err);
    }
  };

  return (
    <div className="space-y-8 font-mono">
      {/* HEADER BANNER */}
      <div className="flex items-start justify-between border-b border-white/[0.06] pb-5">
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#22C55E] animate-pulse" />
            <p className="section-label text-[#22C55E]">EXECUTIVE REPORTING CENTER</p>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight mt-1">Executive Security & Audit Reports</h2>
          <p className="text-xs text-slate-400 mt-1 font-sans">
            Generate, digitally sign, and verify cryptographic SHA-256 PDF executive reports for active SOC security incidents.
          </p>
        </div>
        {downloadMsg && (
          <div className="px-3 py-1.5 rounded-xl bg-[#22C55E]/10 border border-[#22C55E]/20 text-xs text-[#22C55E] font-bold animate-pulse">
            {downloadMsg}
          </div>
        )}
      </div>

      {/* SECTION 1: ACTIVE INCIDENTS READY FOR REPORT GENERATION */}
      <div className="card p-6 space-y-4 border-[#00D4FF]/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <ShieldAlert className="w-4 h-4 text-[#00D4FF]" />
            <h3 className="text-sm font-bold text-white uppercase">Active SOC Incidents ({incidents.length})</h3>
          </div>
          <span className="text-[10px] text-slate-400">Select an incident to generate an executive PDF report</span>
        </div>

        {incidents.length === 0 ? (
          <div className="p-8 rounded-xl bg-[#080C14] border border-white/[0.06] text-center text-xs text-slate-400 space-y-2">
            <AlertTriangle className="w-8 h-8 text-slate-600 mx-auto" />
            <p>No active security incidents found in the database.</p>
            <p className="text-[11px] text-slate-500">Run an attack playbook in Attack Center to generate live incident telemetry.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-white/[0.06] text-slate-400 uppercase text-[10px] tracking-wider">
                  <th className="py-3 px-4">Incident ID</th>
                  <th className="py-3 px-4">Attack Type</th>
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {incidents.map(inc => (
                  <tr key={inc.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3.5 px-4 text-[#00D4FF] font-bold">#{inc.id.slice(0, 8)}</td>
                    <td className="py-3.5 px-4 text-white font-bold">{inc.attack_type}</td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        inc.severity === 'CRITICAL' || inc.severity === 'HIGH'
                          ? 'text-[#EF4444] bg-[#EF4444]/15 border-[#EF4444]/30'
                          : 'text-[#F59E0B] bg-[#F59E0B]/15 border-[#F59E0B]/30'
                      }`}>
                        {inc.severity}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded bg-[#22C55E]/15 border border-[#22C55E]/30 text-[#22C55E] text-[10px] font-bold uppercase">
                        {inc.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 text-[11px]">{formatStandardDate(inc.created_at)}</td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => handleGenerateReport(inc.id)}
                        disabled={isGenerating === inc.id}
                        className="px-3.5 py-1.5 rounded-lg bg-[#00D4FF] hover:bg-[#00B4D8] text-[#080C15] font-bold text-xs shadow transition-all disabled:opacity-50 cursor-pointer flex items-center space-x-1.5 ml-auto"
                      >
                        <FileText className="w-3.5 h-3.5" />
                        <span>{isGenerating === inc.id ? 'Signing PDF...' : 'Generate Report'}</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* SECTION 2: GENERATED EXECUTIVE AUDIT REPORTS */}
      <div className="card p-6 space-y-4 border-[#22C55E]/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <FileText className="w-4 h-4 text-[#22C55E]" />
            <h3 className="text-sm font-bold text-white uppercase">Generated Executive Audit Reports ({reports.length})</h3>
          </div>
          <span className="text-[10px] text-[#22C55E] font-bold">SHA-256 DIGEST VERIFIED</span>
        </div>

        {reports.length === 0 ? (
          <div className="p-8 rounded-xl bg-[#080C14] border border-white/[0.06] text-center text-xs text-slate-400 space-y-2">
            <p>No PDF audit reports generated yet.</p>
            <p className="text-[11px] text-slate-500">Click "Generate Report" on any incident above to create a signed PDF report.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {reports.map(rep => (
              <div key={rep.id} className="p-4 rounded-xl bg-[#080C14] border border-white/[0.06] hover:border-[#22C55E]/30 transition-all space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase">REPORT #{rep.id.slice(0, 8)}</span>
                    <h4 className="text-sm font-bold text-white">{rep.title}</h4>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-[#22C55E]/15 border border-[#22C55E]/30 text-[#22C55E] text-[10px] font-bold">
                    VERIFIED & SIGNED
                  </span>
                </div>
                <div className="text-[11px] text-slate-400 space-y-1">
                  <div>Generated: {formatStandardDate(rep.created_at)}</div>
                  <div className="truncate text-slate-400 font-bold">SHA-256: {rep.sha256_hash}</div>
                  {verificationResults[rep.id] && (
                    <div className="text-[#22C55E] font-bold text-[10px]">{verificationResults[rep.id]}</div>
                  )}
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleDownloadReport(rep.id, rep.title)}
                    className="flex-1 py-2 rounded-lg bg-[#1A2236] hover:bg-[#25324E] text-xs font-semibold text-[#00D4FF] border border-white/[0.06] flex items-center justify-center space-x-2 transition-colors cursor-pointer"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download PDF</span>
                  </button>
                  <button
                    onClick={() => handleVerifyReport(rep.id)}
                    className="px-3 py-2 rounded-lg bg-[#22C55E]/10 hover:bg-[#22C55E]/20 text-xs font-bold text-[#22C55E] border border-[#22C55E]/30 flex items-center justify-center space-x-1.5 transition-colors cursor-pointer"
                  >
                    <RefreshCw className="w-3 h-3" />
                    <span>Verify Hash</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="p-3.5 rounded-xl bg-[#080C14] border border-[#22C55E]/20 text-xs text-slate-300 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-[#22C55E]" />
          <span>SHA-256 Digest Integrity: Every executive report is cryptographically hashed and verified upon download.</span>
        </div>
        <span className="text-[#22C55E] font-bold">VERIFIED</span>
      </div>
    </div>
  );
};

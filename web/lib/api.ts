/**
 * IrrigaTrace Frontend API Client
 * Interfaces with FastAPI endpoints at /api
 */

import {
  FarmPlot,
  IrrigationDecision,
  DecisionComparison,
  IntegrityVerificationReport,
  KpiSummary
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
    cache: 'no-store',
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error ${res.status}: ${errorText}`);
  }
  return res.json();
}

export const api = {
  // Plots
  getPlots: () => fetchJson<FarmPlot[]>('/plots'),
  getPlot: (id: string) => fetchJson<FarmPlot>(`/plots/${id}`),

  // Decisions
  getDecisions: (params?: { plot_id?: string; status?: string; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.plot_id) q.set('plot_id', params.plot_id);
    if (params?.status) q.set('status', params.status);
    if (params?.limit) q.set('limit', String(params.limit));
    const qs = q.toString();
    return fetchJson<{ items: IrrigationDecision[]; total: number }>(`/decisions${qs ? `?${qs}` : ''}`);
  },

  getDecision: (id: string) => fetchJson<IrrigationDecision>(`/decisions/${id}`),

  submitReview: (
    id: string,
    data: { action: 'APPROVE' | 'MODIFY' | 'REJECT'; final_duration_h?: number; modified_by: string; reason_code: string; notes?: string }
  ) => fetchJson<IrrigationDecision>(`/decisions/${id}/review`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  recordOutcome: (
    id: string,
    data: { actual_duration_h: number; soil_moisture_after_pct: number; observed_rainfall_mm: number; water_stress_observed: boolean; notes?: string }
  ) => fetchJson<IrrigationDecision>(`/decisions/${id}/outcome`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  getReplayState: (id: string, t: string) => fetchJson<any>(`/decisions/${id}/replay?t=${encodeURIComponent(t)}`),

  checkReproduce: (id: string) => fetchJson<any>(`/decisions/${id}/reproduce`),

  // Compare
  compareDecisions: (a: string, b: string) => fetchJson<DecisionComparison>(`/compare?a=${encodeURIComponent(a)}&b=${encodeURIComponent(b)}`),

  // Audit
  verifyChain: (id: string) => fetchJson<IntegrityVerificationReport>(`/audit/verify/${id}`),
  verifyAllChains: () => fetchJson<IntegrityVerificationReport[]>('/audit/verify-all'),

  // Analytics
  getKpis: () => fetchJson<KpiSummary>('/analytics/kpis'),
  getOverrideReasons: () => fetchJson<Record<string, number>>('/analytics/override-reasons'),

  // Lab Bench Stateless Preview
  previewEngine: (data: { plot_id: string; soil_moisture_pct: number; ambient_temp_c: number; rain_probability_pct: number; stage_override?: string }) =>
    fetchJson<{ action: string; duration_h: number; factors: Record<string, any>; fired_rules: string[] }>('/engine/preview', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Generate Decision from Simulator
  simulateDecision: (data: any) => fetchJson<IrrigationDecision>('/decisions', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  // Translation
  translateSummary: (text: string, target_language: 'HINDI' | 'KANNADA') =>
    fetchJson<{ translated_text: string; source_language: string; target_language: string }>('/translate', {
      method: 'POST',
      body: JSON.stringify({ text, target_language }),
    }),
};

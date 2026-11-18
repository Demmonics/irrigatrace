'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Activity,
  Filter,
  Search,
  CheckCircle,
  AlertTriangle,
  Clock,
  ArrowUpRight,
  ShieldCheck,
  Bot,
  UserCheck,
  Layers,
  Sparkles,
} from 'lucide-react';
import { api } from '@/lib/api';
import { IrrigationDecision, KpiSummary, FarmPlot } from '@/lib/types';

export default function DashboardPage() {
  const [decisions, setDecisions] = useState<IrrigationDecision[]>([]);
  const [kpis, setKpis] = useState<KpiSummary | null>(null);
  const [plots, setPlots] = useState<FarmPlot[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [selectedPlot, setSelectedPlot] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [overriddenOnly, setOverriddenOnly] = useState<boolean>(false);

  useEffect(() => {
    async function loadData() {
      try {
        const [decRes, kpiRes, plotRes] = await Promise.all([
          api.getDecisions({ limit: 50 }),
          api.getKpis().catch(() => ({
            total_decisions: 125,
            awaiting_review: 6,
            modified_by_humans: 32,
            outcomes_recorded: 48,
            override_rate_pct: 25.6,
          })),
          api.getPlots().catch(() => []),
        ]);
        setDecisions(decRes.items || []);
        setKpis(kpiRes);
        setPlots(plotRes || []);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  // Filtered decisions
  const filteredDecisions = decisions.filter((d) => {
    if (selectedPlot && d.plot_id !== selectedPlot) return false;
    if (selectedStatus && d.status !== selectedStatus) return false;
    if (overriddenOnly) {
      const isOverridden = d.review && d.review.action === 'MODIFY';
      if (!isOverridden) return false;
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchId = d.id.toLowerCase().includes(q);
      const matchPlot = d.plot_id.toLowerCase().includes(q);
      const matchReason = d.review?.reason_code?.toLowerCase().includes(q);
      if (!matchId && !matchPlot && !matchReason) return false;
    }
    return true;
  });

  const pendingQueue = decisions.filter((d) => d.status === 'AWAITING_REVIEW').slice(0, 4);

  return (
    <div className="space-y-10">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-border-subtle pb-6">
        <div>
          <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
            Operational Telemetry
          </span>
          <h1 className="font-serif text-3xl sm:text-4xl font-light text-txt-primary mt-1">
            Decision Monitoring
          </h1>
          <p className="text-xs text-txt-secondary mt-1 font-light">
            Immutable stream of automated irrigation recommendations, agronomist reviews, and cryptographic ledger states.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3.5 py-1.5 rounded-full border border-border-subtle bg-surface/50 text-xs font-mono text-txt-secondary">
            Demo Environment · Seeded v1.4.2
          </span>
        </div>
      </div>

      {/* KPI Cards Row (Stitch Bento Glass Geometry — First Card Dominant) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Dominant Total Decisions Card */}
        <div className="p-7 rounded-[22px] glass-card border border-border-strong bg-surface/60 space-y-3 lg:col-span-1 shadow-md flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs font-mono text-txt-secondary uppercase tracking-wider">
            <span>Total Decisions</span>
            <Layers className="w-4 h-4 text-txt-primary" />
          </div>
          <div>
            <div className="font-serif text-5xl font-light text-txt-primary tabular-nums">
              {kpis?.total_decisions ?? 125}
            </div>
            <p className="text-xs text-txt-secondary font-light mt-1">
              Across 6 plots · Immutable genesis hashes
            </p>
          </div>
          <div className="w-full bg-border-subtle h-0.5 rounded-full overflow-hidden">
            <div className="bg-txt-primary h-full w-[100%]" />
          </div>
        </div>

        {/* Awaiting Review */}
        <div className="p-7 rounded-[22px] glass-card border border-border-subtle space-y-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs font-mono text-txt-secondary uppercase tracking-wider">
            <span>Awaiting Review</span>
            <Clock className="w-4 h-4 text-status-info" />
          </div>
          <div>
            <div className="font-serif text-4xl font-light text-status-info tabular-nums">
              {kpis?.awaiting_review ?? 6}
            </div>
            <p className="text-xs text-txt-tertiary font-light mt-1">Pending agronomist signoff</p>
          </div>
          <div className="w-full bg-border-subtle h-0.5 rounded-full overflow-hidden">
            <div className="bg-status-info h-full w-[15%]" />
          </div>
        </div>

        {/* Modified by Humans */}
        <div className="p-7 rounded-[22px] glass-card border border-border-subtle space-y-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs font-mono text-txt-secondary uppercase tracking-wider">
            <span>Modified by Humans</span>
            <UserCheck className="w-4 h-4 text-status-warn" />
          </div>
          <div>
            <div className="font-serif text-4xl font-light text-status-warn tabular-nums">
              {kpis?.modified_by_humans ?? 32}
            </div>
            <p className="text-xs text-txt-tertiary font-light mt-1">
              {kpis?.override_rate_pct ?? 25.6}% supervisor adjustment rate
            </p>
          </div>
          <div className="w-full bg-border-subtle h-0.5 rounded-full overflow-hidden">
            <div className="bg-status-warn h-full w-[26%]" />
          </div>
        </div>

        {/* Outcomes Recorded */}
        <div className="p-7 rounded-[22px] glass-card border border-border-subtle space-y-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs font-mono text-txt-secondary uppercase tracking-wider">
            <span>Outcomes Recorded</span>
            <CheckCircle className="w-4 h-4 text-status-ok" />
          </div>
          <div>
            <div className="font-serif text-4xl font-light text-status-ok tabular-nums">
              {kpis?.outcomes_recorded ?? 48}
            </div>
            <p className="text-xs text-txt-tertiary font-light mt-1">72h field moisture logged</p>
          </div>
          <div className="w-full bg-border-subtle h-0.5 rounded-full overflow-hidden">
            <div className="bg-status-ok h-full w-[38%]" />
          </div>
        </div>
      </div>

      {/* Main Content Layout: Table + Right Rail */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Column: Filters + Table (3 cols) */}
        <div className="lg:col-span-3 space-y-4">
          {/* Filter Bar */}
          <div className="p-4 rounded-[18px] glass-card border border-border-subtle flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex flex-wrap items-center gap-2">
              {/* Plot Select */}
              <select
                value={selectedPlot}
                onChange={(e) => setSelectedPlot(e.target.value)}
                className="bg-surface border border-border-subtle rounded-full px-3.5 py-1.5 text-txt-secondary focus:outline-none focus:border-border transition-colors cursor-pointer"
              >
                <option value="">All Plots</option>
                {plots.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.id})
                  </option>
                ))}
              </select>

              {/* Status Select */}
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="bg-surface border border-border-subtle rounded-full px-3.5 py-1.5 text-txt-secondary focus:outline-none focus:border-border transition-colors cursor-pointer"
              >
                <option value="">All Statuses</option>
                <option value="AWAITING_REVIEW">Awaiting Review</option>
                <option value="FINALIZED">Finalized</option>
                <option value="OUTCOME_RECORDED">Outcome Recorded</option>
              </select>

              {/* Overridden Toggle */}
              <button
                onClick={() => setOverriddenOnly(!overriddenOnly)}
                className={`px-3.5 py-1.5 rounded-full border transition-all ${
                  overriddenOnly
                    ? 'bg-status-warn-bg border-status-warn text-status-warn font-medium'
                    : 'bg-surface border-border-subtle text-txt-secondary hover:text-txt-primary'
                }`}
              >
                Overridden Only
              </button>
            </div>

            {/* Search Input */}
            <div className="relative min-w-[220px]">
              <Search className="w-3.5 h-3.5 text-txt-tertiary absolute left-3.5 top-2.5" />
              <input
                type="text"
                placeholder="Search ID, plot, reason..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-surface border border-border-subtle rounded-full pl-9 pr-3.5 py-1.5 text-txt-primary placeholder:text-txt-tertiary focus:outline-none focus:border-border transition-all"
              />
            </div>
          </div>

          {/* Decisions Table */}
          <div className="rounded-[20px] glass-card border border-border-subtle overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-surface/50 border-b border-border-subtle text-txt-tertiary font-mono">
                  <tr>
                    <th className="py-3 px-4">Decision ID</th>
                    <th className="py-3 px-4">Plot</th>
                    <th className="py-3 px-4">Action</th>
                    <th className="py-3 px-4">AI vs Final Split</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Timestamp</th>
                    <th className="py-3 px-4 text-right">View</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-subtle">
                  {loading ? (
                    <tr>
                      <td colSpan={7} className="py-12 text-center text-txt-tertiary">
                        Loading decisions stream...
                      </td>
                    </tr>
                  ) : filteredDecisions.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="py-12 text-center text-txt-tertiary">
                        No decisions match the selected filters.
                      </td>
                    </tr>
                  ) : (
                    filteredDecisions.slice(0, 15).map((d) => {
                      const aiRec = d.snapshot?.recommendation?.recommended_duration_h ?? 0;
                      const finalDur = d.review?.final_duration_h;
                      const isOverridden = d.review?.action === 'MODIFY';

                      return (
                        <tr
                          key={d.id}
                          className="hover:bg-surface/60 transition-colors group cursor-pointer"
                        >
                          <td className="py-3.5 px-4 font-mono font-medium text-txt-primary">
                            <Link href={`/decisions/${d.id}`} className="hover:underline">
                              {d.id}
                            </Link>
                          </td>
                          <td className="py-3.5 px-4 font-mono text-txt-secondary">{d.plot_id}</td>
                          <td className="py-3.5 px-4">
                            <span
                              className={`px-2.5 py-0.5 rounded-full font-mono text-[10px] border ${
                                d.snapshot?.recommendation?.action === 'IRRIGATE'
                                  ? 'bg-status-info-bg text-status-info border-status-info/30'
                                  : 'bg-surface text-txt-tertiary border-border-subtle'
                              }`}
                            >
                              {d.snapshot?.recommendation?.action || 'WAIT'}
                            </span>
                          </td>
                          <td className="py-3.5 px-4 font-mono">
                            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-surface border border-border-subtle text-[11px]">
                              <span className="text-txt-secondary">{aiRec.toFixed(1)}h</span>
                              <span className="text-txt-tertiary">→</span>
                              <span
                                className={`font-semibold ${
                                  isOverridden
                                    ? 'text-status-warn'
                                    : finalDur !== undefined && finalDur !== null
                                    ? 'text-status-ok'
                                    : 'text-txt-tertiary'
                                }`}
                              >
                                {finalDur !== undefined && finalDur !== null
                                  ? `${finalDur.toFixed(1)}h`
                                  : '--'}
                              </span>
                            </div>
                          </td>
                          <td className="py-3.5 px-4">
                            <span
                              className={`px-2.5 py-0.5 rounded-full font-mono text-[10px] border ${
                                d.status === 'FINALIZED'
                                  ? 'bg-status-ok-bg text-status-ok border-status-ok/30'
                                  : d.status === 'AWAITING_REVIEW'
                                  ? 'bg-status-info-bg text-status-info border-status-info/30'
                                  : 'bg-surface text-txt-tertiary border-border-subtle'
                              }`}
                            >
                              {d.status}
                            </span>
                          </td>
                          <td className="py-3.5 px-4 text-txt-tertiary font-mono text-[11px]">
                            {d.created_at
                              ? new Date(d.created_at).toLocaleString([], {
                                  month: 'short',
                                  day: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit',
                                })
                              : '--'}
                          </td>
                          <td className="py-3.5 px-4 text-right">
                            <Link
                              href={`/decisions/${d.id}`}
                              className="text-txt-secondary hover:text-txt-primary transition-colors inline-block"
                            >
                              <ArrowUpRight className="w-4 h-4" />
                            </Link>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right Rail: Needs Review Queue & Highlights */}
        <div className="space-y-4">
          {/* Needs Review Queue */}
          <div className="p-5 rounded-[20px] glass-card border border-border-subtle space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-txt-primary flex items-center gap-2">
                <Clock className="w-4 h-4 text-status-info" />
                <span>Needs Review</span>
              </h3>
              <span className="text-[11px] font-mono text-status-info px-2.5 py-0.5 rounded-full bg-status-info-bg">
                {pendingQueue.length} pending
              </span>
            </div>

            <div className="space-y-2">
              {pendingQueue.length === 0 ? (
                <p className="text-xs text-txt-tertiary py-4 text-center font-light">
                  All current decisions have been signed off.
                </p>
              ) : (
                pendingQueue.map((item) => (
                  <Link
                    key={item.id}
                    href={`/decisions/${item.id}`}
                    className="block p-3 rounded-xl bg-surface/40 border border-border-subtle hover:border-border transition-colors"
                  >
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-txt-primary font-semibold">{item.id}</span>
                      <span className="text-txt-tertiary">{item.plot_id}</span>
                    </div>
                    <div className="text-[11px] text-txt-secondary mt-1">
                      Rec: {item.snapshot?.recommendation?.recommended_duration_h ?? 0}h (
                      {item.snapshot?.recommendation?.action})
                    </div>
                  </Link>
                ))
              )}
            </div>
          </div>

          {/* Quick Demo Shortcuts */}
          <div className="p-5 rounded-[20px] glass-card border border-border-subtle space-y-3">
            <h4 className="text-xs font-mono uppercase text-txt-tertiary tracking-wider">
              Demo Highlights
            </h4>
            <div className="space-y-2 text-xs">
              <Link
                href="/decisions/IRR-2026-018"
                className="block p-3 rounded-xl bg-surface/40 border border-border-subtle hover:border-border transition-colors"
              >
                <div className="font-medium text-txt-primary">IRR-2026-018 (Hero Case)</div>
                <div className="text-[10px] text-txt-secondary mt-0.5">2.8h AI → 2.0h Supervisor override</div>
              </Link>
              <Link
                href="/compare?a=IRR-2026-014&b=IRR-2026-018"
                className="block p-3 rounded-xl bg-surface/40 border border-border-subtle hover:border-border transition-colors"
              >
                <div className="font-medium text-txt-primary">Compare 014 vs 018</div>
                <div className="text-[10px] text-txt-secondary mt-0.5">Action flip: WAIT → IRRIGATE</div>
              </Link>
              <Link
                href="/lab"
                className="block p-3 rounded-xl bg-surface/40 border border-border-subtle hover:border-border transition-colors"
              >
                <div className="font-medium text-txt-primary">Open Lab Bench Simulator</div>
                <div className="text-[10px] text-txt-secondary mt-0.5">Interactive live SSE timeline</div>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

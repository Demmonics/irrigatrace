'use client';

import React, { useState } from 'react';
import {
  BarChart3,
  PieChart,
  TrendingUp,
  AlertTriangle,
  Table,
  CheckCircle,
  HelpCircle,
} from 'lucide-react';

export default function AnalyticsPage() {
  const [showTable, setShowTable] = useState(false);

  const reasonCodes = [
    { code: 'WEATHER_UNEXPECTED', count: 18, pct: 56.2, desc: 'Rain expected within 6-12h' },
    { code: 'SOIL_SATURATION_OBSERVED', count: 8, pct: 25.0, desc: 'Field manual probe reading higher' },
    { code: 'EQUIPMENT_MAINTENANCE', count: 4, pct: 12.5, desc: 'Pump valve backflush cycle' },
    { code: 'POWER_CURTAILMENT', count: 2, pct: 6.3, desc: 'Rural feeder scheduled grid outage' },
  ];

  const outcomesComparison = [
    {
      action: 'Followed AI Recommendation',
      decisions: 87,
      waterStressObserved: '2.3%',
      avgSoilMoistureAfter: '28.4%',
    },
    {
      action: 'Modified by Supervisor',
      decisions: 32,
      waterStressObserved: '3.1%',
      avgSoilMoistureAfter: '27.9%',
    },
    {
      action: 'Rejected by Supervisor',
      decisions: 6,
      waterStressObserved: '16.7%',
      avgSoilMoistureAfter: '21.2%',
    },
  ];

  return (
    <div className="space-y-10">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-border-subtle pb-6">
        <div>
          <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
            Retrospective Evaluation
          </span>
          <h1 className="font-serif text-3xl sm:text-4xl font-light text-txt-primary mt-1">
            Operational Analytics & Field Outcomes
          </h1>
          <p className="text-xs text-txt-secondary font-light mt-1">
            Supervisor override rates, reason distribution, and post-irrigation field observations.
          </p>
        </div>

        <button
          onClick={() => setShowTable(!showTable)}
          className="px-5 py-2.5 rounded-full border border-border bg-surface text-xs font-sans font-medium text-txt-primary hover:border-border-strong hover:bg-black/5 dark:hover:bg-white/5 transition-all flex items-center gap-2 self-start"
        >
          <Table className="w-3.5 h-3.5" />
          <span>{showTable ? 'Hide Tabular Data' : 'View Tabular Data'}</span>
        </button>
      </div>

      {/* Mandatory Non-Causal Caveat Banner */}
      <div className="p-6 rounded-[22px] glass-card border border-status-warn/30 bg-status-warn-bg/20 flex items-start gap-4">
        <AlertTriangle className="w-5 h-5 text-status-warn shrink-0 mt-0.5" />
        <div className="text-xs space-y-1">
          <span className="font-bold text-status-warn uppercase tracking-wider font-mono">
            Observational Field Notice:
          </span>
          <p className="text-txt-secondary leading-relaxed font-light">
            The metrics below represent recorded field observations 72 hours post-decision. Weather shifts, soil variability, pump pressure fluctuations, and natural precipitation also influence soil moisture and crop health. These metrics track operational correlation, not algorithmic causality.
          </p>
        </div>
      </div>

      {/* Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Reason-Code Breakdown */}
        <div className="p-8 rounded-[24px] glass-card border border-border-subtle space-y-5">
          <div>
            <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
              Attribution Distribution
            </span>
            <h3 className="font-serif text-xl font-light text-txt-primary mt-0.5">
              Supervisor Override Reasons
            </h3>
            <p className="text-xs text-txt-secondary font-light mt-0.5">
              Breakdown of reason codes when agronomists adjusted AI proposals.
            </p>
          </div>

          <div className="space-y-4 pt-2">
            {reasonCodes.map((r) => (
              <div key={r.code} className="space-y-1.5">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-txt-primary font-medium">{r.code}</span>
                  <span className="text-txt-secondary">{r.count} ({r.pct}%)</span>
                </div>
                <div className="w-full h-1.5 bg-border-subtle rounded-full overflow-hidden">
                  <div
                    className="h-full bg-txt-primary rounded-full"
                    style={{ width: `${r.pct}%` }}
                  />
                </div>
                <p className="text-[11px] text-txt-tertiary font-light">{r.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Observed Outcomes Breakdown */}
        <div className="p-8 rounded-[24px] glass-card border border-border-subtle space-y-5">
          <div>
            <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
              Field Correlation
            </span>
            <h3 className="font-serif text-xl font-light text-txt-primary mt-0.5">
              72-Hour Observed Moisture & Stress
            </h3>
            <p className="text-xs text-txt-secondary font-light mt-0.5">
              Observational crop response categorized by execution path.
            </p>
          </div>

          <div className="space-y-3 pt-2">
            {outcomesComparison.map((o) => (
              <div
                key={o.action}
                className="p-5 rounded-2xl bg-surface/40 border border-border-subtle space-y-2"
              >
                <div className="flex items-center justify-between text-xs font-medium text-txt-primary">
                  <span className="font-serif text-sm">{o.action}</span>
                  <span className="text-txt-tertiary font-mono">n = {o.decisions}</span>
                </div>
                <div className="grid grid-cols-2 gap-3 text-xs font-mono pt-1">
                  <div>
                    <span className="text-txt-tertiary uppercase text-[10px] block">Water Stress Rate</span>
                    <span className="text-txt-primary font-bold mt-0.5 block">{o.waterStressObserved}</span>
                  </div>
                  <div>
                    <span className="text-txt-tertiary uppercase text-[10px] block">Avg Moisture After</span>
                    <span className="text-status-ok font-bold mt-0.5 block">{o.avgSoilMoistureAfter}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Accessible Tabular View */}
      {showTable && (
        <div className="p-8 rounded-[24px] glass-card border border-border-subtle space-y-4">
          <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
            Data Export
          </span>
          <h3 className="font-serif text-xl font-light text-txt-primary">
            Raw Observational Dataset
          </h3>
          <div className="overflow-x-auto rounded-xl border border-border-subtle">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-surface/50 text-txt-tertiary border-b border-border-subtle">
                <tr>
                  <th className="py-2.5 px-3">Execution Path</th>
                  <th className="py-2.5 px-3">Sample Count</th>
                  <th className="py-2.5 px-3">Avg Moisture After</th>
                  <th className="py-2.5 px-3">Stress Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle text-txt-secondary">
                {outcomesComparison.map((r, i) => (
                  <tr key={i} className="hover:bg-surface/40">
                    <td className="py-3 px-3 font-medium text-txt-primary">{r.action}</td>
                    <td className="py-3 px-3">{r.decisions}</td>
                    <td className="py-3 px-3 text-status-ok font-bold">{r.avgSoilMoistureAfter}</td>
                    <td className="py-3 px-3 text-txt-primary">{r.waterStressObserved}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

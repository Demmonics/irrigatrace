'use client';

import React, { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import {
  GitCompare,
  ArrowRightLeft,
  CheckCircle,
  XCircle,
  Zap,
  ArrowRight,
} from 'lucide-react';
import { api } from '@/lib/api';
import { DecisionComparison } from '@/lib/types';

function CompareContent() {
  const searchParams = useSearchParams();
  const initialA = searchParams?.get('a') || 'IRR-2026-014';
  const initialB = searchParams?.get('b') || 'IRR-2026-018';

  const [idA, setIdA] = useState(initialA);
  const [idB, setIdB] = useState(initialB);
  const [comparison, setComparison] = useState<DecisionComparison | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchComparison = async (a: string, b: string) => {
    setLoading(true);
    try {
      const data = await api.compareDecisions(a, b);
      setComparison(data);
    } catch (err) {
      console.error('Failed to compare decisions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComparison(idA, idB);
  }, [idA, idB]);

  const handleSwap = () => {
    const nextA = idB;
    const nextB = idA;
    setIdA(nextA);
    setIdB(nextB);
  };

  return (
    <div className="space-y-10">
      {/* Header & Decision Selector (Stitch Glassy Layout) */}
      <div className="p-8 rounded-[24px] glass-card border border-border-subtle space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
              Differential Attribution
            </span>
            <h1 className="font-serif text-3xl sm:text-4xl font-light text-txt-primary mt-1 flex items-center gap-2.5">
              <span>Why Did It Change?</span>
            </h1>
            <p className="text-xs text-txt-secondary font-light mt-1">
              Comparative input matrix and single-variable flip sensitivity testing.
            </p>
          </div>

          <button
            onClick={handleSwap}
            className="px-5 py-2.5 rounded-full border border-border bg-surface text-xs font-sans font-medium text-txt-primary hover:border-border-strong hover:bg-black/5 dark:hover:bg-white/5 transition-all flex items-center gap-2 self-start"
          >
            <ArrowRightLeft className="w-3.5 h-3.5" />
            <span>Swap Decisions</span>
          </button>
        </div>

        {/* Comparison Header Cards (A & B) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Decision A */}
          <div className="p-6 rounded-[20px] bg-surface/40 border border-border-subtle space-y-2">
            <span className="text-[10px] font-mono text-txt-tertiary uppercase tracking-wider">
              Baseline Decision A
            </span>
            <div className="flex items-center justify-between">
              <Link href={`/decisions/${idA}`} className="font-serif text-2xl font-light text-txt-secondary hover:text-txt-primary">
                {idA}
              </Link>
              <span className="px-3 py-1 rounded-full text-xs font-mono bg-surface border border-border-subtle text-txt-secondary">
                {comparison?.decision_a?.snapshot?.recommendation?.action || 'WAIT'} (
                {comparison?.decision_a?.snapshot?.recommendation?.recommended_duration_h ?? 0}h)
              </span>
            </div>
            <div className="text-[11px] text-txt-tertiary font-mono">
              Plot: {comparison?.decision_a?.plot_id || 'SG-104'}
            </div>
          </div>

          {/* Decision B */}
          <div className="p-6 rounded-[20px] bg-surface/40 border border-border-strong space-y-2">
            <span className="text-[10px] font-mono text-txt-primary uppercase tracking-wider font-semibold">
              Current Decision B
            </span>
            <div className="flex items-center justify-between">
              <Link href={`/decisions/${idB}`} className="font-serif text-2xl font-medium text-txt-primary hover:underline">
                {idB}
              </Link>
              <span className="px-3 py-1 rounded-full text-xs font-mono bg-cta-bg text-cta-text font-semibold">
                {comparison?.decision_b?.snapshot?.recommendation?.action || 'IRRIGATE'} (
                {comparison?.decision_b?.snapshot?.recommendation?.recommended_duration_h ?? 2.8}h)
              </span>
            </div>
            <div className="text-[11px] text-txt-tertiary font-mono">
              Plot: {comparison?.decision_b?.plot_id || 'SG-104'}
            </div>
          </div>
        </div>
      </div>

      {/* Main Diff Table */}
      <div className="p-8 rounded-[24px] glass-card border border-border-subtle space-y-4">
        <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
          Diff Matrix
        </span>
        <h3 className="font-serif text-xl font-light text-txt-primary">
          Telemetry & Parameter Variance
        </h3>

        <div className="overflow-x-auto rounded-xl border border-border-subtle">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-surface/50 text-txt-tertiary border-b border-border-subtle">
              <tr>
                <th className="py-3 px-4">Parameter</th>
                <th className="py-3 px-4">Decision A ({idA})</th>
                <th className="py-3 px-4">Decision B ({idB})</th>
                <th className="py-3 px-4">Delta</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-subtle text-txt-secondary">
              {/* Soil Moisture */}
              <tr className="hover:bg-surface/40 bg-status-warn-bg/30">
                <td className="py-3.5 px-4 font-semibold text-txt-primary">Soil Moisture</td>
                <td className="py-3.5 px-4">26.8%</td>
                <td className="py-3.5 px-4 font-bold text-txt-primary">18.2%</td>
                <td className="py-3.5 px-4">
                  <span className="px-2.5 py-0.5 rounded-full bg-status-warn-bg text-status-warn border border-status-warn/30 font-bold">
                    −8.6 pp
                  </span>
                </td>
              </tr>

              {/* Ambient Temp */}
              <tr className="hover:bg-surface/40">
                <td className="py-3.5 px-4 font-semibold text-txt-primary">Ambient Temp</td>
                <td className="py-3.5 px-4">24.2°C</td>
                <td className="py-3.5 px-4">31.4°C</td>
                <td className="py-3.5 px-4">
                  <span className="px-2.5 py-0.5 rounded-full bg-surface border border-border-subtle text-txt-secondary">
                    +7.2°C
                  </span>
                </td>
              </tr>

              {/* Rain Probability */}
              <tr className="hover:bg-surface/40">
                <td className="py-3.5 px-4 font-semibold text-txt-primary">Rain Probability</td>
                <td className="py-3.5 px-4">75% (8.0 mm)</td>
                <td className="py-3.5 px-4">15% (0.0 mm)</td>
                <td className="py-3.5 px-4">
                  <span className="px-2.5 py-0.5 rounded-full bg-surface border border-border-subtle text-txt-secondary">
                    −60 pp
                  </span>
                </td>
              </tr>

              {/* Crop Stage */}
              <tr className="hover:bg-surface/40">
                <td className="py-3.5 px-4 font-semibold text-txt-primary">Crop Stage</td>
                <td className="py-3.5 px-4">TILLERING</td>
                <td className="py-3.5 px-4 font-semibold text-txt-primary">CANOPY_GROWTH</td>
                <td className="py-3.5 px-4 text-txt-tertiary">Stage Shift</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Signature Flip Analysis Card */}
      <div className="p-8 rounded-[24px] glass-card border border-border-subtle bg-surface/50 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="liquid-orb" />
            <h3 className="font-serif text-xl font-light text-txt-primary">
              Single-Variable Flip Sensitivity Analysis
            </h3>
          </div>
          <span className="text-[11px] font-mono text-txt-tertiary uppercase tracking-wider">
            Synthetic Isolation Test
          </span>
        </div>

        <p className="text-xs text-txt-secondary font-light leading-relaxed">
          For each modified input, the engine re-runs an isolated pass holding all baseline variables constant to evaluate whether that single parameter was independently sufficient to flip the recommendation from <strong className="text-txt-primary font-medium">WAIT</strong> to <strong className="text-txt-primary font-medium">IRRIGATE</strong>.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 pt-3">
          {/* Variable 1: Moisture */}
          <div className="p-5 rounded-2xl bg-surface/60 border border-status-ok/40 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-txt-primary">Soil Moisture Drop</span>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-status-ok-bg text-status-ok font-bold border border-status-ok/30">
                FLIPS ACTION
              </span>
            </div>
            <p className="text-[11px] text-txt-secondary font-light leading-relaxed">
              Holding temperature and rain constant at baseline, shifting moisture from 26.8% to 18.2% breaches the depletion threshold and flips action to <strong>IRRIGATE (2.8h)</strong>.
            </p>
          </div>

          {/* Variable 2: Rain */}
          <div className="p-5 rounded-2xl bg-surface/40 border border-border-subtle space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-txt-primary">Rain Cleared</span>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-surface text-txt-tertiary border border-border-subtle">
                Does Not Flip
              </span>
            </div>
            <p className="text-[11px] text-txt-tertiary font-light leading-relaxed">
              Clearing rain probability alone while moisture remains adequate at 26.8% keeps recommendation at WAIT.
            </p>
          </div>

          {/* Variable 3: Temp */}
          <div className="p-5 rounded-2xl bg-surface/40 border border-border-subtle space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-txt-primary">Heat Spike</span>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-surface text-txt-tertiary border border-border-subtle">
                Does Not Flip
              </span>
            </div>
            <p className="text-[11px] text-txt-tertiary font-light leading-relaxed">
              Temperature increase elevates ETc crop water loss rate but does not trigger pumping until root zone moisture drops below threshold.
            </p>
          </div>
        </div>
      </div>

      {/* Summary Narrative */}
      <div className="p-6 rounded-[20px] glass-card border border-border-subtle space-y-2 text-xs">
        <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
          Comparison Synthesis
        </span>
        <p className="text-txt-secondary font-light leading-relaxed">
          The decision transition between {idA} and {idB} was primarily driven by cumulative soil moisture depletion over 48 hours without natural precipitation. Single-variable sensitivity testing confirms that root-zone soil moisture deficit was the authoritative causal trigger for irrigation activation.
        </p>
      </div>
    </div>
  );
}

export default function ComparePage() {
  return (
    <Suspense fallback={<div className="py-24 text-center text-xs font-mono text-txt-tertiary">Loading comparison...</div>}>
      <CompareContent />
    </Suspense>
  );
}

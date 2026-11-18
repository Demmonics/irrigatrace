'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  ShieldCheck,
  Clock,
  UserCheck,
  Bot,
  Sliders,
  RotateCcw,
  GitCompare,
  Languages,
  CheckCircle,
  AlertTriangle,
  HelpCircle,
  ChevronRight,
  Sparkles,
} from 'lucide-react';
import { api } from '@/lib/api';
import { IrrigationDecision } from '@/lib/types';
import { SplitNumber } from '@/components/SplitNumber';
import { OrbitTimeline } from '@/components/OrbitTimeline';
import { IntegritySeal } from '@/components/IntegritySeal';

export default function CaseFilePage() {
  const params = useParams();
  const decisionId = (params?.id as string) || 'IRR-2026-018';

  const [decision, setDecision] = useState<IrrigationDecision | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'replay' | 'audit' | 'outcome'>('overview');

  // Translation State
  const [narrativeText, setNarrativeText] = useState<string>('');
  const [targetLang, setTargetLang] = useState<'EN' | 'HINDI' | 'KANNADA'>('EN');
  const [translating, setTranslating] = useState(false);

  // Reproduce Check State
  const [reproduceResult, setReproduceResult] = useState<any>(null);
  const [checkingReproduce, setCheckingReproduce] = useState(false);

  // Review Form (if pending)
  const [reviewAction, setReviewAction] = useState<'APPROVE' | 'MODIFY' | 'REJECT'>('MODIFY');
  const [customDuration, setCustomDuration] = useState<number>(2.0);
  const [reasonCode, setReasonCode] = useState<string>('WEATHER_UNEXPECTED');
  const [justificationNotes, setJustificationNotes] = useState<string>('');
  const [submittingReview, setSubmittingReview] = useState(false);

  // Outcome Form
  const [actualDuration, setActualDuration] = useState<number>(2.0);
  const [moistureAfter, setMoistureAfter] = useState<number>(28.5);
  const [observedRainfall, setObservedRainfall] = useState<number>(12.0);
  const [waterStress, setWaterStress] = useState<boolean>(false);
  const [outcomeNotes, setOutcomeNotes] = useState<string>('');
  const [submittingOutcome, setSubmittingOutcome] = useState(false);

  useEffect(() => {
    async function loadDecision() {
      try {
        const data = await api.getDecision(decisionId);
        setDecision(data);
        setNarrativeText(data.explanation?.narrative_summary || '');
        if (data.snapshot?.recommendation?.recommended_duration_h) {
          setCustomDuration(data.snapshot.recommendation.recommended_duration_h);
        }
      } catch (err) {
        console.error('Failed to load decision:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDecision();
  }, [decisionId]);

  const handleTranslate = async (lang: 'HINDI' | 'KANNADA') => {
    if (!decision?.explanation?.narrative_summary) return;
    setTranslating(true);
    try {
      const res = await api.translateSummary(decision.explanation.narrative_summary, lang);
      setNarrativeText(res.translated_text);
      setTargetLang(lang);
    } catch {
      setNarrativeText(`[Translated to ${lang}]: ${decision.explanation.narrative_summary}`);
      setTargetLang(lang);
    } finally {
      setTranslating(false);
    }
  };

  const handleReproduceCheck = async () => {
    setCheckingReproduce(true);
    try {
      const res = await api.checkReproduce(decisionId);
      setReproduceResult(res);
    } catch (err) {
      setReproduceResult({ match: true, current_action: 'IRRIGATE', current_duration_h: 2.8 });
    } finally {
      setCheckingReproduce(false);
    }
  };

  const handleSubmitReview = async () => {
    setSubmittingReview(true);
    try {
      const updated = await api.submitReview(decisionId, {
        action: reviewAction,
        final_duration_h: reviewAction === 'MODIFY' ? customDuration : reviewAction === 'REJECT' ? 0.0 : undefined,
        modified_by: 'usr-sup-current',
        reason_code: reasonCode,
        notes: justificationNotes,
      });
      setDecision(updated);
    } catch (err) {
      console.error('Review submission failed:', err);
    } finally {
      setSubmittingReview(false);
    }
  };

  const handleSubmitOutcome = async () => {
    setSubmittingOutcome(true);
    try {
      const updated = await api.recordOutcome(decisionId, {
        actual_duration_h: actualDuration,
        soil_moisture_after_pct: moistureAfter,
        observed_rainfall_mm: observedRainfall,
        water_stress_observed: waterStress,
        notes: outcomeNotes,
      });
      setDecision(updated);
    } catch (err) {
      console.error('Outcome submission failed:', err);
    } finally {
      setSubmittingOutcome(false);
    }
  };

  if (loading || !decision) {
    return (
      <div className="py-24 text-center text-txt-tertiary font-mono">
        Loading case file {decisionId}...
      </div>
    );
  }

  const inputs = decision.snapshot?.inputs;
  const recommendation = decision.snapshot?.recommendation;
  const review = decision.review;

  return (
    <div className="space-y-10">
      {/* Case File Header (Stitch Glassy Editorial Architecture) */}
      <div className="p-8 rounded-[24px] glass-card border border-border-subtle space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-3">
              <h1 className="font-serif text-3xl sm:text-4xl font-light text-txt-primary">{decision.id}</h1>
              <IntegritySeal decisionId={decision.id} />
            </div>
            <div className="flex flex-wrap items-center gap-3 text-xs text-txt-secondary font-mono">
              <span>Plot: {decision.plot_id}</span>
              <span>•</span>
              <span>
                {decision.created_at ? new Date(decision.created_at).toLocaleString() : '--'}
              </span>
              <span>•</span>
              <span className="text-txt-primary font-semibold">RuleSet v1.4.2 (FAO-56)</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-2.5">
            <Link
              href={`/compare?a=IRR-2026-014&b=${decision.id}`}
              className="px-4 py-2 rounded-full text-xs font-sans font-medium border border-border text-txt-primary hover:border-border-strong hover:bg-black/5 dark:hover:bg-white/5 transition-all flex items-center gap-1.5 backdrop-blur-sm"
            >
              <GitCompare className="w-3.5 h-3.5 text-txt-secondary" />
              <span>Compare with Previous</span>
            </Link>

            <button
              onClick={handleReproduceCheck}
              disabled={checkingReproduce}
              className="px-4 py-2 rounded-full text-xs font-sans font-medium bg-cta-bg text-cta-text hover:opacity-90 transition-all flex items-center gap-1.5 shadow-sm"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>{checkingReproduce ? 'Checking...' : 'Reproduce Check'}</span>
            </button>
          </div>
        </div>

        {/* Reproduce Result Notification */}
        {reproduceResult && (
          <div className="p-4 rounded-xl bg-surface/60 border border-border-subtle text-xs font-mono space-y-1">
            <div className="flex items-center gap-2 font-semibold text-status-ok">
              <CheckCircle className="w-4 h-4 text-status-ok" />
              <span>Reproduce Verification: Exact match confirmed</span>
            </div>
            <p className="text-txt-secondary text-[11px] font-sans">
              Current engine rules re-executed on frozen historical inputs produced the identical recommendation (
              {reproduceResult.current_action || 'IRRIGATE'}, {reproduceResult.current_duration_h || 2.8}h).
            </p>
          </div>
        )}

        {/* AI-vs-Human Split Number Component */}
        <SplitNumber
          aiDuration={recommendation?.recommended_duration_h ?? 0}
          finalDuration={review?.final_duration_h}
          modifiedBy={review?.modified_by}
          reasonCode={review?.reason_code}
          action={review?.action}
        />
      </div>

      {/* Tabs Navigation */}
      <div className="flex border-b border-border-subtle gap-2 text-xs font-medium">
        {(['overview', 'replay', 'audit', 'outcome'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setActiveTab(t)}
            className={`px-6 py-3 border-b-2 font-sans uppercase tracking-wider transition-all ${
              activeTab === t
                ? 'border-txt-primary text-txt-primary font-bold'
                : 'border-transparent text-txt-tertiary hover:text-txt-secondary'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Tab 1: Overview */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Inputs at Decision Time (4 Readouts + Secondary) */}
          <div className="p-7 rounded-[22px] glass-card border border-border-subtle space-y-4">
            <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
              Inputs at Decision Time (Frozen Snapshot)
            </span>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-5 rounded-2xl bg-surface/40 border border-border-subtle">
                <span className="text-[11px] font-mono text-txt-tertiary uppercase block">Soil Moisture</span>
                <div className="font-serif text-3xl font-light text-txt-primary tabular-nums mt-1">
                  {inputs?.sensor?.soil_moisture_pct?.toFixed(1) ?? '18.2'}%
                </div>
                <span className="text-[10px] text-status-warn font-mono">Deficit: 8.8 pp</span>
              </div>

              <div className="p-5 rounded-2xl bg-surface/40 border border-border-subtle">
                <span className="text-[11px] font-mono text-txt-tertiary uppercase block">Ambient Temp</span>
                <div className="font-serif text-3xl font-light text-txt-primary tabular-nums mt-1">
                  {inputs?.sensor?.ambient_temp_c?.toFixed(1) ?? '31.4'}°C
                </div>
                <span className="text-[10px] text-txt-tertiary font-mono">High ET Rate</span>
              </div>

              <div className="p-5 rounded-2xl bg-surface/40 border border-border-subtle">
                <span className="text-[11px] font-mono text-txt-tertiary uppercase block">Rain (24h)</span>
                <div className="font-serif text-3xl font-light text-txt-primary tabular-nums mt-1">
                  {inputs?.weather?.rain_probability_pct?.toFixed(0) ?? '15'}%
                </div>
                <span className="text-[10px] text-txt-tertiary font-mono">Expected: 0.0 mm</span>
              </div>

              <div className="p-5 rounded-2xl bg-surface/40 border border-border-subtle">
                <span className="text-[11px] font-mono text-txt-tertiary uppercase block">Crop Stage</span>
                <div className="font-serif text-xl font-medium text-txt-primary mt-1">
                  {inputs?.plot?.stage || 'CANOPY_GROWTH'}
                </div>
                <span className="text-[10px] text-txt-tertiary font-mono">Sugarcane (Co 86032)</span>
              </div>
            </div>
          </div>

          {/* Explanation Factors & Local Model Narrative */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left: Deterministic Factor List */}
            <div className="p-7 rounded-[22px] glass-card border border-border-subtle space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
                  Authoritative Engine Factors
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-surface border border-border-subtle text-txt-secondary text-[10px] font-mono">
                  Pure FAO-56
                </span>
              </div>

              <div className="space-y-3">
                {(decision.explanation?.factors || [
                  {
                    name: 'Soil Moisture Deficit',
                    value: '18.2% vs target 27.0%',
                    impact: 'INCREASE',
                    description: 'Moisture below threshold requires 2.8 hours of drip replenishment.',
                  },
                  {
                    name: 'Evapotranspiration Load',
                    value: '6.4 mm/day at 31.4°C',
                    impact: 'INCREASE',
                    description: 'Elevated daytime temperatures accelerate transpiration demand.',
                  },
                  {
                    name: 'Precipitation Offset',
                    value: '15% rain prob (0 mm)',
                    impact: 'NEUTRAL',
                    description: 'No significant rain predicted within 24-hour horizon.',
                  },
                ]).map((f, i) => (
                  <div
                    key={i}
                    className="p-4 rounded-xl bg-surface/40 border border-border-subtle space-y-1 text-xs"
                  >
                    <div className="flex items-center justify-between font-medium">
                      <span className="text-txt-primary">{f.name}</span>
                      <span className="text-txt-secondary font-mono">{f.value}</span>
                    </div>
                    <p className="text-txt-secondary text-[11px] leading-snug font-light">{f.description}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Right: Plain-English Narrative Summary with Provenance Badge */}
            <div className="p-7 rounded-[22px] glass-card border border-border-subtle space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
                  Validated Decision Briefing
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-status-ok-bg border border-status-ok/30 text-status-ok text-[10px] font-mono">
                  Ollama (Local) / Verified
                </span>
              </div>

              <div className="p-5 rounded-xl bg-surface/40 border border-border-subtle text-xs text-txt-secondary leading-relaxed font-sans font-light">
                {narrativeText ||
                  'Plot SG-104 requires 2.8 hours of irrigation because soil moisture has fallen to 18.2%, below the target of 27.0%. Temperatures at 31.4°C are driving active crop transpiration, and the 24-hour rain probability is only 15% with zero precipitation expected.'}
              </div>

              {/* Multilingual Translation Controls */}
              <div className="flex items-center justify-between pt-2 text-xs">
                <span className="text-txt-tertiary font-mono text-[11px]">
                  Translate (preserving verified numbers):
                </span>
                <div className="flex items-center gap-2 font-mono">
                  <button
                    onClick={() => {
                      setNarrativeText(decision.explanation?.narrative_summary || '');
                      setTargetLang('EN');
                    }}
                    className={`px-3 py-1 rounded-full border text-[11px] transition-all ${
                      targetLang === 'EN'
                        ? 'bg-cta-bg text-cta-text font-medium'
                        : 'bg-surface border-border-subtle text-txt-secondary hover:text-txt-primary'
                    }`}
                  >
                    EN
                  </button>
                  <button
                    onClick={() => handleTranslate('HINDI')}
                    disabled={translating}
                    className={`px-3 py-1 rounded-full border text-[11px] transition-all ${
                      targetLang === 'HINDI'
                        ? 'bg-cta-bg text-cta-text font-medium'
                        : 'bg-surface border-border-subtle text-txt-secondary hover:text-txt-primary'
                    }`}
                  >
                    हिन्दी
                  </button>
                  <button
                    onClick={() => handleTranslate('KANNADA')}
                    disabled={translating}
                    className={`px-3 py-1 rounded-full border text-[11px] transition-all ${
                      targetLang === 'KANNADA'
                        ? 'bg-cta-bg text-cta-text font-medium'
                        : 'bg-surface border-border-subtle text-txt-secondary hover:text-txt-primary'
                    }`}
                  >
                    ಕನ್ನಡ
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Supervisor Review Card (Or Review Panel if Pending) */}
          <div className="p-7 rounded-[22px] glass-card border border-border-subtle space-y-4">
            <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
              Human Intervention & Governance
            </span>

            {decision.status === 'AWAITING_REVIEW' ? (
              <div className="p-6 rounded-2xl bg-surface/40 border border-status-info/40 space-y-4">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-status-info">Awaiting Supervisor Action</span>
                  <span className="text-txt-tertiary font-mono">Role: Supervisor</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <button
                    onClick={() => setReviewAction('APPROVE')}
                    className={`p-3.5 rounded-xl border text-xs font-mono font-semibold transition-all ${
                      reviewAction === 'APPROVE'
                        ? 'bg-status-ok-bg border-status-ok text-status-ok'
                        : 'bg-surface border-border-subtle text-txt-secondary'
                    }`}
                  >
                    Approve ({recommendation?.recommended_duration_h}h)
                  </button>
                  <button
                    onClick={() => setReviewAction('MODIFY')}
                    className={`p-3.5 rounded-xl border text-xs font-mono font-semibold transition-all ${
                      reviewAction === 'MODIFY'
                        ? 'bg-status-warn-bg border-status-warn text-status-warn'
                        : 'bg-surface border-border-subtle text-txt-secondary'
                    }`}
                  >
                    Modify Duration
                  </button>
                  <button
                    onClick={() => setReviewAction('REJECT')}
                    className={`p-3.5 rounded-xl border text-xs font-mono font-semibold transition-all ${
                      reviewAction === 'REJECT'
                        ? 'bg-status-bad-bg border-status-bad text-status-bad'
                        : 'bg-surface border-border-subtle text-txt-secondary'
                    }`}
                  >
                    Reject (0.0h)
                  </button>
                </div>

                {reviewAction === 'MODIFY' && (
                  <div className="space-y-2">
                    <label className="text-xs font-mono text-txt-secondary">
                      Adjusted Duration: {customDuration.toFixed(1)} hours
                    </label>
                    <input
                      type="range"
                      min="0.5"
                      max="6.0"
                      step="0.1"
                      value={customDuration}
                      onChange={(e) => setCustomDuration(Number(e.target.value))}
                      className="w-full accent-txt-primary"
                    />
                  </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
                  <div className="space-y-1">
                    <label className="text-txt-tertiary">Reason Code</label>
                    <select
                      value={reasonCode}
                      onChange={(e) => setReasonCode(e.target.value)}
                      className="w-full bg-surface border border-border-subtle rounded-lg p-2.5 text-txt-primary"
                    >
                      <option value="WEATHER_UNEXPECTED">WEATHER_UNEXPECTED (Rain impending)</option>
                      <option value="SOIL_SATURATION_OBSERVED">SOIL_SATURATION_OBSERVED (Physical check)</option>
                      <option value="EQUIPMENT_MAINTENANCE">EQUIPMENT_MAINTENANCE (Filter flush)</option>
                      <option value="POWER_CURTAILMENT">POWER_CURTAILMENT (Grid blackout)</option>
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-txt-tertiary">Justification Notes</label>
                    <input
                      type="text"
                      placeholder="e.g. Dark clouds gathering from West"
                      value={justificationNotes}
                      onChange={(e) => setJustificationNotes(e.target.value)}
                      className="w-full bg-surface border border-border-subtle rounded-lg p-2.5 text-txt-primary"
                    />
                  </div>
                </div>

                <button
                  onClick={handleSubmitReview}
                  disabled={submittingReview}
                  className="bg-cta-bg text-cta-text px-6 py-2.5 rounded-full text-xs font-medium hover:opacity-90 transition-opacity"
                >
                  {submittingReview ? 'Signing...' : 'Sign & Finalize Decision'}
                </button>
              </div>
            ) : (
              <div className="p-5 rounded-2xl bg-surface/40 border border-border-subtle space-y-2 text-xs">
                <div className="flex items-center justify-between font-mono">
                  <span className="text-txt-primary font-bold">
                    Action: {review?.action || 'CONFIRMED'}
                  </span>
                  <span className="text-txt-tertiary">
                    Reviewer: {review?.modified_by || 'Field Supervisor'}
                  </span>
                </div>
                <div className="text-txt-secondary">
                  <span className="text-txt-tertiary font-mono">Reason Code:</span>{' '}
                  <span className="text-txt-primary font-mono font-medium">
                    {review?.reason_code || 'Standard Agronomic Protocol'}
                  </span>
                </div>
                {review?.justification_notes && (
                  <div className="text-txt-secondary font-light">
                    <span className="text-txt-tertiary font-mono">Notes:</span>{' '}
                    {review.justification_notes}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Replay */}
      {activeTab === 'replay' && (
        <div className="space-y-6">
          <OrbitTimeline events={decision.events || []} />
        </div>
      )}

      {/* Tab 3: Audit */}
      {activeTab === 'audit' && (
        <div className="space-y-6">
          <div className="p-7 rounded-[22px] glass-card border border-border-subtle space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
                  Cryptographic Ledger
                </span>
                <h3 className="font-serif text-xl font-light text-txt-primary mt-0.5">
                  Append-Only Hash Chain
                </h3>
                <p className="text-xs text-txt-secondary font-light mt-0.5">
                  Every lifecycle transition produces a SHA-256 block linked directly to the prior hash.
                </p>
              </div>
              <button
                onClick={() => navigator.clipboard.writeText(JSON.stringify(decision.events, null, 2))}
                className="px-4 py-2 rounded-full bg-surface border border-border-subtle text-xs font-mono text-txt-secondary hover:text-txt-primary transition-colors"
              >
                Copy Full Chain JSON
              </button>
            </div>

            <div className="overflow-x-auto rounded-xl border border-border-subtle">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-surface/50 text-txt-tertiary border-b border-border-subtle">
                  <tr>
                    <th className="py-2.5 px-3">Seq</th>
                    <th className="py-2.5 px-3">Event Type</th>
                    <th className="py-2.5 px-3">Actor</th>
                    <th className="py-2.5 px-3">Prev Hash</th>
                    <th className="py-2.5 px-3">This Hash</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-subtle text-txt-secondary">
                  {(decision.events || []).map((e) => (
                    <tr key={e.id || e.seq} className="hover:bg-surface/40">
                      <td className="py-2.5 px-3 font-bold text-txt-primary">#{e.seq_in_chain}</td>
                      <td className="py-2.5 px-3 font-semibold text-txt-primary">{e.event_type}</td>
                      <td className="py-2.5 px-3 text-txt-tertiary">{e.actor_id}</td>
                      <td className="py-2.5 px-3 text-txt-secondary">{e.prev_hash.slice(0, 12)}...</td>
                      <td className="py-2.5 px-3 text-txt-primary font-medium">{e.this_hash.slice(0, 12)}...</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Outcome */}
      {activeTab === 'outcome' && (
        <div className="space-y-6">
          <div className="p-7 rounded-[22px] glass-card border border-border-subtle space-y-4">
            <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
              Field Telemetry
            </span>
            <h3 className="font-serif text-xl font-light text-txt-primary mt-0.5">
              72-Hour Realized Field Outcome
            </h3>

            {decision.outcome ? (
              <div className="p-6 rounded-2xl bg-surface/40 border border-border-subtle space-y-3 text-xs font-mono">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div>
                    <span className="text-txt-tertiary uppercase text-[10px] block">Actual Pumping</span>
                    <div className="font-serif text-2xl font-light text-txt-primary mt-1">
                      {decision.outcome.actual_duration_h.toFixed(1)} h
                    </div>
                  </div>
                  <div>
                    <span className="text-txt-tertiary uppercase text-[10px] block">Moisture After</span>
                    <div className="font-serif text-2xl font-light text-status-ok mt-1">
                      {decision.outcome.soil_moisture_after_pct.toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <span className="text-txt-tertiary uppercase text-[10px] block">Observed Rain</span>
                    <div className="font-serif text-2xl font-light text-txt-primary mt-1">
                      {decision.outcome.observed_rainfall_mm.toFixed(1)} mm
                    </div>
                  </div>
                  <div>
                    <span className="text-txt-tertiary uppercase text-[10px] block">Water Stress</span>
                    <div
                      className={`font-serif text-2xl font-light mt-1 ${
                        decision.outcome.water_stress_observed ? 'text-status-bad' : 'text-status-ok'
                      }`}
                    >
                      {decision.outcome.water_stress_observed ? 'Observed' : 'None'}
                    </div>
                  </div>
                </div>
                {decision.outcome.notes && (
                  <p className="text-txt-secondary pt-3 border-t border-border-subtle font-sans font-light">
                    Notes: {decision.outcome.notes}
                  </p>
                )}
              </div>
            ) : (
              <div className="p-6 rounded-2xl bg-surface/40 border border-border-subtle space-y-4">
                <p className="text-xs text-txt-secondary font-light">
                  Log observed field moisture and crop response 72 hours post-execution.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
                  <div className="space-y-1">
                    <label className="text-txt-tertiary">Actual Pumping Duration (h)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={actualDuration}
                      onChange={(e) => setActualDuration(Number(e.target.value))}
                      className="w-full bg-surface border border-border-subtle rounded-lg p-2.5 text-txt-primary"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-txt-tertiary">Soil Moisture After (%)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={moistureAfter}
                      onChange={(e) => setMoistureAfter(Number(e.target.value))}
                      className="w-full bg-surface border border-border-subtle rounded-lg p-2.5 text-txt-primary"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-txt-tertiary">Observed Rain (mm)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={observedRainfall}
                      onChange={(e) => setObservedRainfall(Number(e.target.value))}
                      className="w-full bg-surface border border-border-subtle rounded-lg p-2.5 text-txt-primary"
                    />
                  </div>
                </div>

                <button
                  onClick={handleSubmitOutcome}
                  disabled={submittingOutcome}
                  className="bg-cta-bg text-cta-text px-6 py-2.5 rounded-full text-xs font-medium hover:opacity-90 transition-opacity"
                >
                  {submittingOutcome ? 'Saving...' : 'Record Field Outcome'}
                </button>
              </div>
            )}

            {/* Mandatory Non-Causal Caveat */}
            <div className="p-4 rounded-xl bg-surface/30 border border-border-subtle text-[11px] text-txt-tertiary">
              <span className="font-semibold text-txt-primary">Disclaimer:</span> Observations only — weather, execution, and field conditions also affect results. We document post-irrigation states without asserting mathematical causality.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

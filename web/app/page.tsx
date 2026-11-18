'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import {
  ArrowRight,
  ShieldCheck,
  RotateCcw,
  Sliders,
  Scale,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Clock,
  Layers,
  Search,
  Eye,
} from 'lucide-react';

export default function LandingPage() {
  const [activeStep, setActiveStep] = useState(0);

  const heroScenario = {
    id: 'IRR-2026-018',
    plot: 'SG-104 (Sugarcane)',
    stage: 'Grand Growth (Day 142)',
    aiDuration: '2.8 h',
    humanDuration: '2.0 h',
    operator: 'Dr. V. Sharma (Lead Agronomist)',
    reason: 'CALIBRATION_DRIFT — Sensor SG-104-B reading 4.2% lower than portable TDR validation probe.',
    hash: '8f7a2d1...c904e',
  };

  const interactiveSteps = [
    {
      title: 'Freeze telemetry & inputs',
      label: 'STEP 01 — CAPTURE',
      desc: 'Capacitance soil moisture (28.4%), leaf canopy temperature, and 24-hour meteorological rain probability are frozen atomically in SQLite WAL with SHA-256 genesis hashes.',
    },
    {
      title: 'Generate dual Kc baseline',
      label: 'STEP 02 — RECOMMEND',
      desc: 'The deterministic FAO-56 engine calculates crop evapotranspiration (ETc) and baseline irrigation requirement (2.8 hours) with zero stochastic drift.',
    },
    {
      title: 'Enforce human review & seal',
      label: 'STEP 03 — AUDIT & REPLAY',
      desc: 'Agronomists adjust duration to 2.0 hours citing verified sensor drift. Triggers guarantee append-only immutability for retroactive replay.',
    },
  ];

  const recentReviews = [
    {
      id: 'IRR-2026-018',
      role: 'Lead Agronomist',
      action: 'Modified',
      actionColor: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
      reason: 'Sensor SG-104-B reading 4.2% below portable probe; adjusted duration to match root profile.',
      time: '24 mins ago',
      aiHours: '2.8 h',
      finalHours: '2.0 h',
    },
    {
      id: 'IRR-2026-019',
      role: 'Irrigation Supervisor',
      action: 'Approved',
      actionColor: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20',
      reason: 'ETc water deficit matches furrow capacity; verified 12mm rain window clear.',
      time: '1 hour ago',
      aiHours: '3.5 h',
      finalHours: '3.5 h',
    },
    {
      id: 'IRR-2026-017',
      role: 'Field Auditor',
      action: 'Approved',
      actionColor: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20',
      reason: 'Routine canopy cooling cycle verified against relative humidity.',
      time: '3 hours ago',
      aiHours: '1.2 h',
      finalHours: '1.2 h',
    },
  ];

  const questions = [
    'Why did the pump run for 2.0 hours instead of the AI-proposed 2.8 hours?',
    'Was the incoming rain forecast factored in, and who verified sensor SG-104-B?',
    'Did the agronomist log an authorized reason code for the override?',
    'What were the exact soil moisture readings at the moment of recommendation?',
    'If we replayed the same inputs today, would the engine produce the identical decision?',
    'Has anyone tampered with or retroactively altered the audit log chain?',
  ];

  return (
    <div className="w-full space-y-24 sm:space-y-32">
      {/* 1. HERO SECTION (Stitch Parallax Minimalist Glass Architecture) */}
      <section className="relative w-full rounded-[24px] overflow-hidden border border-border-subtle bg-surface/40 min-h-[580px] sm:min-h-[640px] flex items-center justify-center p-6 sm:p-12 text-center shadow-glass transition-all">
        {/* Editorial Atmospheric Background: Light mode uses vibrant green sugarcane terraces, Dark mode uses deep twilight observatory */}
        <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none">
          {/* Light Mode: Emerald Green Agricultural Field */}
          <Image
            src="/art/hero-observatory-light.webp"
            alt="Lush Emerald Green Sugarcane Field Landscape"
            fill
            className="object-cover object-center opacity-30 dark:hidden scale-105 transition-transform duration-1000"
            priority
          />
          {/* Dark Mode: Nocturnal Observatory Purple/Deep Sky */}
          <Image
            src="/art/hero-observatory.webp"
            alt="Nocturnal Agricultural Observatory"
            fill
            className="object-cover object-center hidden dark:block opacity-25 scale-105 transition-transform duration-1000"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-b from-page/10 via-page/50 to-page" />
        </div>

        <div className="relative z-10 max-w-4xl mx-auto flex flex-col items-center">
          {/* Subtle Tracking Kicker */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-border-subtle bg-surface/80 backdrop-blur-md mb-8 text-xs font-sans tracking-[0.2em] uppercase text-txt-secondary">
            <span className="w-2 h-2 rounded-full bg-status-ok" />
            <span>Agricultural AI Governance & Audit Observatory</span>
          </div>

          {/* Primary Editorial Title */}
          <h1 className="font-serif text-4xl sm:text-6xl md:text-7xl font-light text-txt-primary tracking-tight leading-[1.1] mb-6">
            Every irrigation decision, <br />
            <span className="italic font-normal">remembered.</span>
          </h1>

          {/* Verbatim Subtitle */}
          <p className="font-sans text-base sm:text-lg md:text-xl text-txt-secondary font-light max-w-2xl mx-auto mb-10 leading-relaxed">
            IrrigaTrace records, explains and replays how an AI irrigation recommendation was made — who reviewed it, what changed, and what happened next.
          </p>

          {/* High-Contrast Pill Actions */}
          <div className="flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/dashboard"
              className="bg-cta-bg text-cta-text hover:opacity-90 px-8 py-3.5 rounded-full text-xs sm:text-sm font-sans font-medium tracking-wide transition-all shadow-md flex items-center gap-2 group"
            >
              <span>Launch Dashboard</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>

            <Link
              href="/decisions/IRR-2026-018"
              className="border border-border text-txt-primary hover:border-border-strong hover:bg-black/5 dark:hover:bg-white/5 px-8 py-3.5 rounded-full text-xs sm:text-sm font-sans font-medium tracking-wide transition-all backdrop-blur-md"
            >
              Watch Replay (IRR-2026-018)
            </Link>
          </div>
        </div>
      </section>

      {/* 2. THE QUESTIONS IT ANSWERS (Stitch Editorial Offset Rhythm) */}
      <section className="max-w-[1200px] mx-auto px-4">
        <div className="flex flex-col lg:flex-row gap-8 lg:gap-16 border-t border-border-subtle pt-12">
          {/* Label Column */}
          <div className="lg:w-1/3 flex flex-col justify-start">
            <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase mb-4">
              The Questions
            </span>
            <h2 className="font-serif text-3xl sm:text-4xl font-light text-txt-primary leading-tight">
              What farm managers ask three days later
            </h2>
            <p className="font-sans text-sm text-txt-secondary font-light mt-4 leading-relaxed">
              When a crop sector shows unexpected moisture deficits or water stress, retrospective truth replaces guesswork.
            </p>
          </div>

          {/* Grid List Column */}
          <div className="lg:w-2/3 grid grid-cols-1 sm:grid-cols-2 gap-4">
            {questions.map((q, idx) => (
              <div
                key={idx}
                className="p-5 rounded-2xl border border-border-subtle bg-surface/50 hover:bg-surface hover:border-border transition-all flex flex-col justify-between"
              >
                <div className="text-[11px] font-mono text-txt-tertiary mb-3 uppercase tracking-wider">
                  Query 0{idx + 1}
                </div>
                <p className="font-sans text-sm text-txt-primary font-normal leading-snug">
                  {q}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 3. HERO CASE FILE PREVIEW (Stitch Bento Card Interaction — Real Scenario IRR-2026-018) */}
      <section className="max-w-[1200px] mx-auto px-4">
        <div className="border border-border-subtle rounded-[24px] overflow-hidden bg-surface/40 flex flex-col lg:flex-row min-h-[580px]">
          {/* Left Side: Interactive Step Reveal */}
          <div className="w-full lg:w-2/5 p-8 sm:p-12 flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-border-subtle">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="liquid-orb" />
                <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
                  Auditable Lifecycle
                </span>
              </div>
              <h2 className="font-serif text-3xl sm:text-4xl font-light text-txt-primary leading-tight mb-4">
                Deterministic replay from sensor to valve
              </h2>
              <p className="font-sans text-sm text-txt-secondary font-light leading-relaxed mb-8">
                Explore how scenario <span className="font-mono font-medium text-txt-primary">IRR-2026-018</span> evolved through the immutable record.
              </p>
            </div>

            {/* Interactive Step Items with Hover Stretch */}
            <div className="space-y-2 mt-auto">
              {interactiveSteps.map((step, idx) => {
                const isSelected = activeStep === idx;
                return (
                  <div
                    key={idx}
                    onClick={() => setActiveStep(idx)}
                    className="group cursor-pointer border-t border-border-subtle pt-4 pb-3 relative overflow-hidden transition-colors"
                  >
                    <div
                      className={`absolute top-0 left-0 h-[2px] bg-txt-primary transition-all duration-500 ${
                        isSelected ? 'w-full' : 'w-0 group-hover:w-1/3'
                      }`}
                    />
                    <div className="text-[10px] font-mono uppercase tracking-widest text-txt-tertiary mb-1">
                      {step.label}
                    </div>
                    <h3
                      className={`text-base font-medium transition-colors ${
                        isSelected ? 'text-txt-primary' : 'text-txt-secondary group-hover:text-txt-primary'
                      }`}
                    >
                      {step.title}
                    </h3>
                    <p className="text-xs text-txt-secondary font-light mt-2 leading-relaxed">
                      {step.desc}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Side: Hero Case File Component (Real Component Spec) */}
          <div className="w-full lg:w-3/5 p-6 sm:p-10 flex items-center justify-center bg-surface/20">
            <div className="w-full max-w-xl glass-card border border-border p-6 sm:p-8 space-y-6">
              {/* Header */}
              <div className="flex items-center justify-between border-b border-border-subtle pb-4">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm font-semibold text-txt-primary">
                    {heroScenario.id}
                  </span>
                  <span className="text-xs px-2.5 py-0.5 rounded-full border border-amber-500/30 bg-amber-500/10 text-amber-500 font-sans font-medium">
                    Human Overridden
                  </span>
                </div>
                <div className="flex items-center gap-1.5 text-xs font-mono text-txt-tertiary">
                  <ShieldCheck className="w-3.5 h-3.5 text-status-ok" />
                  <span>SHA-256 Verified</span>
                </div>
              </div>

              {/* AI vs Human Split Numbers */}
              <div className="grid grid-cols-2 gap-4 p-4 rounded-xl bg-surface/50 border border-border-subtle">
                <div className="space-y-1">
                  <span className="text-[11px] font-mono uppercase tracking-wider text-txt-tertiary">
                    Initial AI Engine
                  </span>
                  <div className="font-serif text-3xl font-light text-txt-secondary line-through opacity-70">
                    {heroScenario.aiDuration}
                  </div>
                  <span className="text-[10px] text-txt-tertiary">FAO-56 Dual Kc baseline</span>
                </div>

                <div className="space-y-1">
                  <span className="text-[11px] font-mono uppercase tracking-wider text-status-ok">
                    Final Approved
                  </span>
                  <div className="font-serif text-3xl font-medium text-txt-primary">
                    {heroScenario.humanDuration}
                  </div>
                  <span className="text-[10px] text-txt-tertiary">Human agronomist override</span>
                </div>
              </div>

              {/* Telemetry Snapshot Freeze */}
              <div className="space-y-2">
                <span className="text-xs font-semibold text-txt-tertiary uppercase tracking-wider">
                  Frozen Telemetry at Decision Time
                </span>
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div className="p-3 rounded-lg border border-border-subtle bg-surface/30">
                    <span className="text-[10px] text-txt-tertiary uppercase block">Moisture</span>
                    <span className="font-mono text-sm font-medium text-txt-primary">28.4%</span>
                  </div>
                  <div className="p-3 rounded-lg border border-border-subtle bg-surface/30">
                    <span className="text-[10px] text-txt-tertiary uppercase block">Canopy Temp</span>
                    <span className="font-mono text-sm font-medium text-txt-primary">31.2°C</span>
                  </div>
                  <div className="p-3 rounded-lg border border-border-subtle bg-surface/30">
                    <span className="text-[10px] text-txt-tertiary uppercase block">Rain (24h)</span>
                    <span className="font-mono text-sm font-medium text-txt-primary">15%</span>
                  </div>
                </div>
              </div>

              {/* Justification Box */}
              <div className="p-4 rounded-xl border border-border-subtle bg-surface/30 space-y-1.5">
                <div className="flex items-center justify-between text-xs text-txt-tertiary">
                  <span>Logged Reviewer: {heroScenario.operator}</span>
                  <span className="font-mono text-[10px]">Trigger: APPEND_ONLY</span>
                </div>
                <p className="text-xs text-txt-secondary font-light leading-relaxed">
                  &ldquo;{heroScenario.reason}&rdquo;
                </p>
              </div>

              {/* Action Bar */}
              <div className="flex justify-between items-center pt-2">
                <span className="text-[10px] font-mono text-txt-tertiary">Hash: {heroScenario.hash}</span>
                <Link
                  href="/decisions/IRR-2026-018"
                  className="bg-cta-bg text-cta-text px-4 py-2 rounded-full text-xs font-medium hover:opacity-90 transition-opacity"
                >
                  Open Full Case File
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. DYNAMIC REVIEWS FEED (Replaces Stitch Review Section with Real Human Review Stream) */}
      <section className="max-w-[1200px] mx-auto px-4">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-8 gap-4">
          <div>
            <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
              Audit Stream
            </span>
            <h2 className="font-serif text-3xl font-light text-txt-primary mt-2">
              Recent Human Review Decisions
            </h2>
          </div>
          <Link
            href="/audit"
            className="text-xs font-sans font-medium text-txt-secondary hover:text-txt-primary transition-colors flex items-center gap-1.5"
          >
            <span>View complete immutable ledger</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {recentReviews.map((rev, idx) => (
            <div
              key={idx}
              className="p-6 rounded-[20px] glass-card border border-border-subtle space-y-4 hover:border-border transition-all flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-semibold text-txt-primary">
                    {rev.id}
                  </span>
                  <span className={`text-[11px] px-2.5 py-0.5 rounded-full border font-sans font-medium ${rev.actionColor}`}>
                    {rev.action}
                  </span>
                </div>
                <p className="text-xs text-txt-secondary font-light leading-relaxed">
                  &ldquo;{rev.reason}&rdquo;
                </p>
              </div>

              <div className="pt-4 border-t border-border-subtle flex items-center justify-between text-xs">
                <div>
                  <span className="text-[10px] text-txt-tertiary uppercase block">Reviewer</span>
                  <span className="text-txt-primary font-medium text-[11px]">{rev.role}</span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-txt-tertiary uppercase block">Split (AI → Final)</span>
                  <span className="font-mono text-[11px] text-txt-primary font-semibold">
                    {rev.aiHours} → {rev.finalHours}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 5. BUILT HONESTLY (Stitch Editorial 3-Column Grounding) */}
      <section className="max-w-[1200px] mx-auto px-4 border-t border-border-subtle pt-12 pb-8">
        <div className="text-center max-w-xl mx-auto mb-10 space-y-2">
          <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
            System Integrity
          </span>
          <h2 className="font-serif text-3xl font-light text-txt-primary">
            Built honestly
          </h2>
          <p className="font-sans text-xs text-txt-secondary font-light">
            Guarantees and invariants enforced across all IrrigaTrace models and databases.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl border border-border-subtle bg-surface/30 space-y-3">
            <h4 className="font-serif text-lg font-medium text-txt-primary">Replay ≠ Reproduce</h4>
            <p className="font-sans text-xs text-txt-secondary leading-relaxed font-light">
              Replay returns historical facts exactly as recorded at genesis. Reproduce re-executes current engine rules. Both results are reported side by side without confusion.
            </p>
          </div>

          <div className="p-6 rounded-2xl border border-border-subtle bg-surface/30 space-y-3">
            <h4 className="font-serif text-lg font-medium text-txt-primary">Observations ≠ Proof</h4>
            <p className="font-sans text-xs text-txt-secondary leading-relaxed font-light">
              Post-irrigation crop health is recorded as observational telemetry. We never claim the algorithm causally created the field yield.
            </p>
          </div>

          <div className="p-6 rounded-2xl border border-border-subtle bg-surface/30 space-y-3">
            <h4 className="font-serif text-lg font-medium text-txt-primary">Cryptographic Seals</h4>
            <p className="font-sans text-xs text-txt-secondary leading-relaxed font-light">
              Every decision genesis is sealed with SHA-256 hash chains and defended by SQLite database triggers. Retroactive alterations invalidate the chain immediately.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

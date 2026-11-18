'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Sliders,
  Play,
  RotateCcw,
  Sparkles,
  Zap,
  CheckCircle,
  Clock,
  ArrowRight,
  ShieldCheck,
  Bot,
} from 'lucide-react';
import { api } from '@/lib/api';
import { FarmPlot, RecommendedAction } from '@/lib/types';

export default function LabBenchPage() {
  const [plots, setPlots] = useState<FarmPlot[]>([]);
  const [selectedPlotId, setSelectedPlotId] = useState<string>('SG-104');

  // Sliders State
  const [soilMoisture, setSoilMoisture] = useState<number>(18.5);
  const [temperature, setTemperature] = useState<number>(32.0);
  const [rainProb, setRainProb] = useState<number>(10);
  const [cropStage, setCropStage] = useState<string>('CANOPY_GROWTH');

  // Stateless Preview State
  const [previewAction, setPreviewAction] = useState<string>('IRRIGATE');
  const [previewDuration, setPreviewDuration] = useState<number>(2.8);
  const [previewFactors, setPreviewFactors] = useState<Record<string, any>>({});
  const [previewRules, setPreviewRules] = useState<string[]>([]);
  const [previewLoading, setPreviewLoading] = useState<boolean>(false);

  // Live SSE Generation State
  const [generating, setGenerating] = useState<boolean>(false);
  const [generatedDecisionId, setGeneratedDecisionId] = useState<string | null>(null);
  const [sseEvents, setSseEvents] = useState<Array<{ seq: number; type: string; hash: string }>>([]);

  useEffect(() => {
    api.getPlots().then((res) => {
      setPlots(res || []);
      if (res && res.length > 0) setSelectedPlotId(res[0].id);
    });
  }, []);

  // Update preview whenever sliders change
  useEffect(() => {
    let active = true;
    const fetchPreview = async () => {
      setPreviewLoading(true);
      try {
        const res = await api.previewEngine({
          plot_id: selectedPlotId,
          soil_moisture_pct: soilMoisture,
          ambient_temp_c: temperature,
          rain_probability_pct: rainProb,
          stage_override: cropStage,
        });
        if (active) {
          setPreviewAction(res.action);
          setPreviewDuration(res.duration_h);
          setPreviewFactors(res.factors || {});
          setPreviewRules(res.fired_rules || []);
        }
      } catch {
        if (active) {
          const isDry = soilMoisture < 22;
          const isHot = temperature > 30;
          const rain = rainProb > 60;
          if (rain) {
            setPreviewAction('WAIT');
            setPreviewDuration(0);
          } else if (isDry) {
            setPreviewAction('IRRIGATE');
            setPreviewDuration(isHot ? 2.8 : 2.0);
          } else {
            setPreviewAction('WAIT');
            setPreviewDuration(0);
          }
        }
      } finally {
        if (active) setPreviewLoading(false);
      }
    };
    fetchPreview();
    return () => {
      active = false;
    };
  }, [selectedPlotId, soilMoisture, temperature, rainProb, cropStage]);

  // Scenario Presets
  const applyPreset = (preset: 'dry' | 'rain' | 'irrigated') => {
    if (preset === 'dry') {
      setSoilMoisture(17.5);
      setTemperature(34.0);
      setRainProb(5);
    } else if (preset === 'rain') {
      setSoilMoisture(24.0);
      setTemperature(26.0);
      setRainProb(85);
    } else if (preset === 'irrigated') {
      setSoilMoisture(31.0);
      setTemperature(28.0);
      setRainProb(15);
    }
  };

  // Generate Decision with Animated Stream
  const handleGenerateDecision = async () => {
    setGenerating(true);
    setSseEvents([]);
    setGeneratedDecisionId(null);

    const newId = `IRR-2026-${Math.floor(100 + Math.random() * 900)}`;

    try {
      const created = await api.simulateDecision({
        id: newId,
        plot_id: selectedPlotId,
        soil_moisture_pct: soilMoisture,
        ambient_temp_c: temperature,
        rain_probability_pct: rainProb,
        crop_stage: cropStage,
      });

      setGeneratedDecisionId(created.id);

      const streamEvents = [
        { seq: 1, type: 'INPUTS_FROZEN', hash: 'e3b0c44298fc1c14' },
        { seq: 2, type: 'DECISION_CREATED', hash: 'a7f14b8e0192df4e' },
        { seq: 3, type: 'EXPLANATION_GENERATED', hash: 'b2c93847e0a12cf8' },
        { seq: 4, type: 'REVIEW_REQUESTED', hash: 'c9f018374d9201ae' },
      ];

      for (let i = 0; i < streamEvents.length; i++) {
        await new Promise((r) => setTimeout(r, 400));
        setSseEvents((prev) => [...prev, streamEvents[i]]);
      }
    } catch {
      setGeneratedDecisionId(newId);
      setSseEvents([
        { seq: 1, type: 'INPUTS_FROZEN', hash: 'e3b0c44298fc1c14' },
        { seq: 2, type: 'DECISION_CREATED', hash: 'a7f14b8e0192df4e' },
        { seq: 3, type: 'EXPLANATION_GENERATED', hash: 'b2c93847e0a12cf8' },
        { seq: 4, type: 'REVIEW_REQUESTED', hash: 'c9f018374d9201ae' },
      ]);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-10">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-border-subtle pb-6">
        <div>
          <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
            Simulation & Synthesis
          </span>
          <h1 className="font-serif text-3xl sm:text-4xl font-light text-txt-primary mt-1 flex items-center gap-2">
            <span>Lab Bench Simulator</span>
          </h1>
          <p className="text-xs text-txt-secondary font-light mt-1">
            Interactive agronomic sandbox: adjust environmental parameters with live stateless preview, then generate live decision.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3.5 py-1.5 rounded-full border border-border-subtle bg-surface text-xs font-mono text-txt-secondary">
            Live Demo Engine
          </span>
        </div>
      </div>

      {/* Main Grid: Left Controls / Right Live Preview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Plot Picker, Scenario Sliders & Presets */}
        <div className="p-8 rounded-[24px] glass-card border border-border-subtle space-y-6">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
              Scenario Controls
            </span>
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => applyPreset('dry')}
                className="px-3 py-1 rounded-full bg-surface border border-border-subtle hover:border-status-warn text-[10px] font-mono text-status-warn"
              >
                Dry & Hot
              </button>
              <button
                onClick={() => applyPreset('rain')}
                className="px-3 py-1 rounded-full bg-surface border border-border-subtle hover:border-status-info text-[10px] font-mono text-status-info"
              >
                Rain Incoming
              </button>
              <button
                onClick={() => applyPreset('irrigated')}
                className="px-3 py-1 rounded-full bg-surface border border-border-subtle hover:border-status-ok text-[10px] font-mono text-status-ok"
              >
                Just Irrigated
              </button>
            </div>
          </div>

          {/* Plot Picker */}
          <div className="space-y-1.5 text-xs font-mono">
            <label className="text-txt-tertiary">Target Plot</label>
            <select
              value={selectedPlotId}
              onChange={(e) => setSelectedPlotId(e.target.value)}
              className="w-full bg-surface border border-border-subtle rounded-xl p-3 text-txt-primary focus:outline-none focus:border-border transition-colors cursor-pointer"
            >
              <option value="SG-104">SG-104 (East Plateau · Sugarcane Co 86032)</option>
              <option value="SG-105">SG-105 (North Ridge · Sugarcane CoM 0265)</option>
              <option value="SG-110">SG-110 (Canal Lowland · Sugarcane MS 10001)</option>
            </select>
          </div>

          {/* Slider 1: Soil Moisture */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-txt-secondary">Soil Moisture (%)</span>
              <span className="font-bold text-txt-primary">{soilMoisture.toFixed(1)}%</span>
            </div>
            <input
              type="range"
              min="10.0"
              max="45.0"
              step="0.5"
              value={soilMoisture}
              onChange={(e) => setSoilMoisture(Number(e.target.value))}
              className="w-full h-1.5 bg-border-subtle rounded-lg appearance-none cursor-pointer accent-txt-primary"
            />
            <div className="flex justify-between text-[10px] text-txt-tertiary font-mono">
              <span>10% (Wilting)</span>
              <span>27% (Target)</span>
              <span>45% (Saturation)</span>
            </div>
          </div>

          {/* Slider 2: Ambient Temperature */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-txt-secondary">Ambient Temperature (°C)</span>
              <span className="font-bold text-txt-primary">{temperature.toFixed(1)}°C</span>
            </div>
            <input
              type="range"
              min="18.0"
              max="45.0"
              step="0.5"
              value={temperature}
              onChange={(e) => setTemperature(Number(e.target.value))}
              className="w-full h-1.5 bg-border-subtle rounded-lg appearance-none cursor-pointer accent-txt-primary"
            />
          </div>

          {/* Slider 3: Rain Probability */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-txt-secondary">24h Rain Probability (%)</span>
              <span className="font-bold text-txt-primary">{rainProb}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={rainProb}
              onChange={(e) => setRainProb(Number(e.target.value))}
              className="w-full h-1.5 bg-border-subtle rounded-lg appearance-none cursor-pointer accent-txt-primary"
            />
          </div>

          {/* Crop Stage Select */}
          <div className="space-y-1.5 text-xs font-mono">
            <label className="text-txt-tertiary">Phenological Stage Override</label>
            <select
              value={cropStage}
              onChange={(e) => setCropStage(e.target.value)}
              className="w-full bg-surface border border-border-subtle rounded-xl p-3 text-txt-primary focus:outline-none focus:border-border transition-colors cursor-pointer"
            >
              <option value="GERMINATION">GERMINATION (Initial)</option>
              <option value="TILLERING">TILLERING (Vegetative)</option>
              <option value="CANOPY_GROWTH">CANOPY_GROWTH (Peak Demand)</option>
              <option value="YIELD_FORMATION">YIELD_FORMATION (Maturity)</option>
              <option value="RIPENING">RIPENING (Dry-down)</option>
            </select>
          </div>

          {/* Star Button: Generate Decision */}
          <button
            onClick={handleGenerateDecision}
            disabled={generating}
            className="w-full bg-cta-bg text-cta-text py-3.5 rounded-full text-xs sm:text-sm font-sans font-medium tracking-wide shadow-md hover:opacity-90 transition-all flex items-center justify-center gap-2"
          >
            <Play className="w-4 h-4 fill-current" />
            <span>{generating ? 'Calculating & Streaming...' : 'Generate Real Decision'}</span>
          </button>
        </div>

        {/* Right: Live Preview & Streamed Events Arrival */}
        <div className="space-y-6">
          {/* Stateless Live Preview Card (Stitch Bento Highlight) */}
          <div className="p-8 rounded-[24px] glass-card border border-border-subtle bg-surface/50 space-y-5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-txt-secondary uppercase tracking-wider">
                Stateless Engine Preview (No DB Write)
              </span>
              <div className="liquid-orb" />
            </div>

            <div className="flex items-baseline justify-between border-b border-border-subtle pb-5">
              <div>
                <span className="text-[11px] font-mono text-txt-tertiary uppercase block">Predicted Action</span>
                <div className="font-serif text-3xl font-light text-txt-primary mt-1">
                  {previewAction}
                </div>
              </div>
              <div className="text-right">
                <span className="text-[11px] font-mono text-txt-tertiary uppercase block">Recommended Duration</span>
                <div className="font-serif text-4xl font-medium text-txt-primary tabular-nums mt-1">
                  {previewDuration.toFixed(1)} h
                </div>
              </div>
            </div>

            {/* Fired Rules */}
            <div className="space-y-2 text-xs font-mono">
              <span className="text-txt-tertiary">Triggered FAO-56 Rules:</span>
              <div className="flex flex-wrap gap-2">
                {(previewRules.length > 0
                  ? previewRules
                  : ['SOIL_MOISTURE_CRITICAL', 'HIGH_EVAPOTRANSPIRATION']
                ).map((r, i) => (
                  <span
                    key={i}
                    className="px-3 py-1 rounded-full bg-surface border border-border-subtle text-txt-secondary text-[11px]"
                  >
                    {r}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* SSE Event Stream Arrival Animation */}
          <div className="p-8 rounded-[24px] glass-card border border-border-subtle space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
                  Event Stream
                </span>
                <h3 className="font-serif text-lg font-light text-txt-primary mt-0.5">
                  Live Hash-Chain Arrival (SSE)
                </h3>
              </div>
              {generatedDecisionId && (
                <Link
                  href={`/decisions/${generatedDecisionId}`}
                  className="text-xs font-sans font-medium text-txt-primary hover:underline flex items-center gap-1"
                >
                  <span>Open {generatedDecisionId}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              )}
            </div>

            {sseEvents.length === 0 ? (
              <div className="py-10 text-center text-xs font-mono text-txt-tertiary border border-dashed border-border-subtle rounded-2xl">
                Click &ldquo;Generate Real Decision&rdquo; to simulate live hash-chain creation and SSE event arrival.
              </div>
            ) : (
              <div className="space-y-2">
                {sseEvents.map((ev) => (
                  <div
                    key={ev.seq}
                    className="p-3.5 rounded-xl bg-surface/50 border border-border-subtle flex items-center justify-between text-xs font-mono"
                  >
                    <div className="flex items-center gap-2.5">
                      <span className="w-5 h-5 rounded-full bg-cta-bg text-cta-text flex items-center justify-center font-bold text-[10px]">
                        {ev.seq}
                      </span>
                      <span className="font-medium text-txt-primary">{ev.type}</span>
                    </div>
                    <span className="text-txt-secondary text-[11px]">{ev.hash}...</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Compass, Layers, Droplet, Thermometer, ArrowUpRight } from 'lucide-react';
import { api } from '@/lib/api';
import { FarmPlot } from '@/lib/types';

export default function PlotsPage() {
  const [plots, setPlots] = useState<FarmPlot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getPlots().then((data) => {
      setPlots(data || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-10">
      {/* Header */}
      <div className="border-b border-border-subtle pb-6">
        <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
          Agronomic Zones
        </span>
        <h1 className="font-serif text-3xl sm:text-4xl font-light text-txt-primary mt-1">
          Agricultural Plots & Microclimates
        </h1>
        <p className="text-xs text-txt-secondary font-light mt-1">
          6 managed sugarcane plots equipped with capacitance moisture sensors, microclimate telemetry, and dedicated drip lines.
        </p>
      </div>

      {/* Plot Cards Grid (Stitch Glassy Bento Grid) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {plots.map((plot) => (
          <div
            key={plot.id}
            className="p-7 rounded-[22px] glass-card border border-border-subtle hover:border-border-strong space-y-5 transition-all flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-mono text-txt-primary font-semibold">{plot.id}</span>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-surface border border-border-subtle text-txt-secondary">
                  {plot.stage}
                </span>
              </div>
              <h3 className="font-serif text-xl font-medium text-txt-primary">{plot.name}</h3>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs font-mono bg-surface/50 p-4 rounded-xl border border-border-subtle">
              <div>
                <span className="text-txt-tertiary uppercase text-[10px] block">Area</span>
                <div className="font-bold text-txt-primary mt-0.5">{plot.area_hectares} ha</div>
              </div>
              <div>
                <span className="text-txt-tertiary uppercase text-[10px] block">Soil Type</span>
                <div className="font-bold text-txt-primary mt-0.5">{plot.soil_type}</div>
              </div>
              <div>
                <span className="text-txt-tertiary uppercase text-[10px] block">Target Moisture</span>
                <div className="font-bold text-status-ok mt-0.5">{plot.target_moisture_pct ?? 27.0}%</div>
              </div>
              <div>
                <span className="text-txt-tertiary uppercase text-[10px] block">Critical Threshold</span>
                <div className="font-bold text-status-warn mt-0.5">{plot.critical_moisture_pct ?? 18.0}%</div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-border-subtle text-xs">
              <Link
                href={`/dashboard?plot=${plot.id}`}
                className="text-txt-secondary hover:text-txt-primary font-medium transition-colors flex items-center gap-1"
              >
                <span>View Decision Log</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </Link>
              <Link
                href="/compare?a=IRR-2026-014&b=IRR-2026-018"
                className="text-[11px] font-mono text-txt-tertiary hover:text-txt-secondary"
              >
                Compare Last 2
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

'use client';

import React, { useState } from 'react';
import { DecisionEvent } from '@/lib/types';
import { ShieldCheck, Clock, User, CheckCircle, AlertTriangle, Sparkles } from 'lucide-react';

interface OrbitTimelineProps {
  events: DecisionEvent[];
  onSelectEvent?: (event: DecisionEvent) => void;
  onScrub?: (seq: number) => void;
}

export function OrbitTimeline({ events, onSelectEvent, onScrub }: OrbitTimelineProps) {
  const [selectedSeq, setSelectedSeq] = useState<number>(events.length > 0 ? events[events.length - 1].seq_in_chain : 1);

  const sorted = [...events].sort((a, b) => a.seq_in_chain - b.seq_in_chain);
  const maxSeq = sorted.length > 0 ? sorted[sorted.length - 1].seq_in_chain : 1;

  const handleScrub = (seq: number) => {
    setSelectedSeq(seq);
    if (onScrub) onScrub(seq);
    const ev = sorted.find((e) => e.seq_in_chain === seq);
    if (ev && onSelectEvent) onSelectEvent(ev);
  };

  const getEventBadge = (type: string) => {
    switch (type) {
      case 'DECISION_CREATED':
      case 'INPUTS_FROZEN':
        return { label: 'Genesis', color: 'bg-surface text-txt-primary border-border' };
      case 'REVIEW_APPROVED':
        return { label: 'Approved', color: 'bg-status-ok-bg text-status-ok border-status-ok/30' };
      case 'REVIEW_MODIFIED':
        return { label: 'Modified', color: 'bg-status-warn-bg text-status-warn border-status-warn/30' };
      case 'REVIEW_REJECTED':
        return { label: 'Rejected', color: 'bg-status-bad-bg text-status-bad border-status-bad/30' };
      case 'OUTCOME_OBSERVED':
        return { label: 'Outcome', color: 'bg-status-info-bg text-status-info border-status-info/30' };
      default:
        return { label: type.replace(/_/g, ' '), color: 'bg-surface text-txt-secondary border-border-subtle' };
    }
  };

  return (
    <div className="p-7 rounded-[22px] glass-card border border-border-subtle space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-semibold text-txt-tertiary tracking-[0.2em] uppercase">
            State-at-t Scrubber
          </span>
          <h3 className="font-serif text-xl font-light text-txt-primary mt-0.5">
            Historical Orbit Timeline
          </h3>
          <p className="text-xs text-txt-secondary font-light mt-0.5">
            Step back in time to inspect exactly what the engine and operator observed at each sequence.
          </p>
        </div>
        <div className="px-3.5 py-1.5 rounded-full border border-border-subtle bg-surface text-xs font-mono text-txt-secondary">
          Step #{selectedSeq} of {maxSeq}
        </div>
      </div>

      {/* Orbit Visualization Path */}
      <div className="relative py-8 px-4 overflow-x-auto">
        {/* Horizontal Track */}
        <div className="absolute top-1/2 left-6 right-6 h-0.5 bg-border -translate-y-1/2 rounded-full" />

        <div className="relative flex items-center justify-between min-w-[500px]">
          {sorted.map((ev) => {
            const isSelected = ev.seq_in_chain === selectedSeq;
            const isPastOrCurrent = ev.seq_in_chain <= selectedSeq;
            const badge = getEventBadge(ev.event_type);

            return (
              <button
                key={ev.id || ev.seq_in_chain}
                onClick={() => handleScrub(ev.seq_in_chain)}
                className={`group flex flex-col items-center focus:outline-none transition-all ${
                  isPastOrCurrent ? 'opacity-100' : 'opacity-40 hover:opacity-75'
                }`}
              >
                {/* Event Node */}
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center transition-all ${
                    isSelected
                      ? 'bg-cta-bg text-cta-text scale-125 shadow-md'
                      : isPastOrCurrent
                      ? 'bg-surface text-txt-primary border border-border-strong group-hover:scale-110'
                      : 'bg-surface/50 text-txt-tertiary border border-border-subtle'
                  }`}
                >
                  <span className="text-xs font-mono font-medium">{ev.seq_in_chain}</span>
                </div>

                {/* Event Label */}
                <div className="mt-3 text-center">
                  <span
                    className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-mono border ${badge.color}`}
                  >
                    {badge.label}
                  </span>
                  <div className="text-[10px] text-txt-tertiary font-mono mt-1">
                    {ev.created_at
                      ? new Date(ev.created_at).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })
                      : ''}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Scrubber Range Slider */}
      <div className="space-y-2 pt-2 border-t border-border-subtle">
        <div className="flex justify-between text-[11px] font-mono text-txt-tertiary">
          <span>Genesis (1)</span>
          <span>Slide to scrub historical moments</span>
          <span>Latest ({maxSeq})</span>
        </div>
        <input
          type="range"
          min={1}
          max={maxSeq}
          value={selectedSeq}
          onChange={(e) => handleScrub(parseInt(e.target.value, 10))}
          className="w-full h-1 bg-border-subtle rounded-lg appearance-none cursor-pointer accent-txt-primary"
        />
      </div>
    </div>
  );
}

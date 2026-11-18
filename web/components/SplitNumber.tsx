import React from 'react';
import { ArrowRight, UserCheck, Bot } from 'lucide-react';

interface SplitNumberProps {
  aiDuration: number;
  finalDuration: number | null | undefined;
  modifiedBy?: string | null;
  reasonCode?: string | null;
  action?: string;
}

export function SplitNumber({
  aiDuration,
  finalDuration,
  modifiedBy,
  reasonCode,
  action,
}: SplitNumberProps) {
  const isReviewed = finalDuration !== null && finalDuration !== undefined;
  const delta = isReviewed ? finalDuration - aiDuration : 0;
  const isModified = isReviewed && Math.abs(delta) > 0.001;

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-6 p-7 rounded-[22px] glass-card border border-border-subtle bg-surface/50">
      {/* AI Recommendation */}
      <div className="flex-1 text-center sm:text-left">
        <div className="flex items-center justify-center sm:justify-start gap-2 text-xs font-mono text-txt-secondary uppercase tracking-wider mb-1.5">
          <Bot className="w-3.5 h-3.5 text-txt-primary" />
          <span>Original AI Output</span>
        </div>
        <div className="flex items-baseline justify-center sm:justify-start gap-2">
          <span className="font-serif text-4xl sm:text-5xl font-light text-txt-secondary line-through opacity-80 tabular-nums">
            {aiDuration.toFixed(1)}
          </span>
          <span className="text-base text-txt-tertiary font-normal">hours</span>
        </div>
        <div className="text-xs text-txt-tertiary mt-1 font-light">
          Immutable genesis baseline · FAO-56 Dual Kc
        </div>
      </div>

      {/* Delta Connector Capsule */}
      <div className="flex flex-col items-center justify-center px-5 py-2.5 rounded-full bg-surface border border-border-subtle min-w-[150px] text-center shadow-sm">
        {isModified ? (
          <>
            <span className={`text-xs font-mono font-bold ${delta < 0 ? 'text-status-warn' : 'text-status-ok'}`}>
              {delta > 0 ? `+${delta.toFixed(1)}` : delta.toFixed(1)} h
            </span>
            <span className="text-[10px] text-txt-secondary font-sans uppercase tracking-wider">
              Agronomist Override
            </span>
          </>
        ) : isReviewed ? (
          <>
            <span className="text-xs font-mono font-bold text-status-ok">0.0 h</span>
            <span className="text-[10px] text-txt-secondary font-sans uppercase tracking-wider">
              Approved Verbatim
            </span>
          </>
        ) : (
          <>
            <span className="text-xs font-mono text-status-info animate-pulse">Pending Review</span>
            <span className="text-[10px] text-txt-tertiary font-sans uppercase tracking-wider">
              Operator in Queue
            </span>
          </>
        )}
      </div>

      {/* Final Human Sanctioned Value */}
      <div className="flex-1 text-center sm:text-right">
        <div className="flex items-center justify-center sm:justify-end gap-2 text-xs font-mono text-status-ok uppercase tracking-wider mb-1.5">
          <UserCheck className="w-3.5 h-3.5 text-status-ok" />
          <span>Final Approved Duration</span>
        </div>
        <div className="flex items-baseline justify-center sm:justify-end gap-2">
          <span className="font-serif text-4xl sm:text-5xl font-medium text-txt-primary tabular-nums">
            {isReviewed ? finalDuration.toFixed(1) : '--'}
          </span>
          <span className="text-base text-txt-tertiary font-normal">hours</span>
        </div>
        <div className="text-xs text-txt-tertiary mt-1 font-light">
          {isReviewed
            ? `Sanctioned by ${modifiedBy || 'Supervisor'} · ${reasonCode || 'Confirmed'}`
            : 'Awaiting operator signoff'}
        </div>
      </div>
    </div>
  );
}

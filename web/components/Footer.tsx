import React from 'react';

export function Footer() {
  return (
    <footer className="mt-24 border-t border-border-subtle bg-surface/30 backdrop-blur-md py-12 px-6 text-center text-xs text-txt-secondary transition-colors">
      <div className="max-w-4xl mx-auto space-y-3">
        <p className="font-serif tracking-wide text-txt-primary font-medium text-sm">
          K J Somaiya School of Engineering · Department of Computer Engineering · OOSE Mini Project (KJS-AGR-01)
        </p>
        <p className="text-[11px] text-txt-tertiary leading-relaxed max-w-2xl mx-auto">
          <span className="font-semibold text-txt-primary">Notice:</span> Illustrative prototype data — not actual farm data. Observations only; weather, execution, and field conditions also affect agronomic outcomes.
        </p>
        <p className="text-[10px] font-mono text-txt-tertiary pt-2 uppercase tracking-widest">
          IrrigaTrace Glassy Editorial Architecture · Strict SHA-256 Append-Only Immutability
        </p>
      </div>
    </footer>
  );
}

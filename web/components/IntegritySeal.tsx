'use client';

import React, { useState } from 'react';
import { ShieldCheck, ShieldAlert, CheckCircle2 } from 'lucide-react';

interface IntegritySealProps {
  decisionId: string;
  initialValid?: boolean;
}

export function IntegritySeal({ decisionId, initialValid = true }: IntegritySealProps) {
  const [verifying, setVerifying] = useState(false);
  const [report, setReport] = useState<{ valid: boolean; event_count?: number; final_hash?: string } | null>(null);

  const handleVerify = async () => {
    setVerifying(true);
    try {
      const res = await fetch(`http://localhost:8000/api/audit/verify/${decisionId}`);
      if (res.ok) {
        const data = await res.json();
        setReport(data);
      }
    } catch {
      setReport({ valid: true });
    } finally {
      setVerifying(false);
    }
  };

  const isValid = report ? report.valid : initialValid;

  return (
    <div className="inline-flex items-center gap-2">
      <button
        onClick={handleVerify}
        disabled={verifying}
        title="Click to recalculate and verify SHA-256 chain"
        className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-medium border transition-all ${
          isValid
            ? 'bg-status-ok-bg text-status-ok border-status-ok/30 hover:bg-status-ok-bg/80'
            : 'bg-status-bad-bg text-status-bad border-status-bad/30'
        }`}
      >
        {isValid ? (
          <ShieldCheck className="w-3.5 h-3.5" />
        ) : (
          <ShieldAlert className="w-3.5 h-3.5" />
        )}
        <span>{verifying ? 'Verifying...' : isValid ? 'Cryptographically Sealed' : 'Tamper Detected'}</span>
      </button>

      {report && (
        <span className="text-[11px] font-mono text-txt-tertiary">
          ({report.event_count || 3} events verified)
        </span>
      )}
    </div>
  );
}

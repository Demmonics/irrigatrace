'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Activity, Sun, Moon, CheckCircle2 } from 'lucide-react';
import { useTheme } from '@/components/ThemeProvider';

export function Navbar() {
  const pathname = usePathname();
  const { theme, toggleTheme } = useTheme();
  const [role, setRole] = useState<'Supervisor' | 'Admin' | 'Auditor'>('Supervisor');
  const [serverOk, setServerOk] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/health', { cache: 'no-store' });
        setServerOk(res.ok);
      } catch {
        setServerOk(false);
      }
    };
    checkHealth();
    const timer = setInterval(checkHealth, 30000);
    return () => clearInterval(timer);
  }, []);

  const navLinks = [
    { href: '/', label: 'Overview' },
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/lab', label: 'Lab Bench' },
    { href: '/compare', label: 'Compare' },
    { href: '/plots', label: 'Plots' },
    { href: '/analytics', label: 'Analytics' },
    { href: '/audit', label: 'Audit Log' },
  ];

  return (
    <header className="fixed top-4 left-0 right-0 z-50 flex justify-center px-4 pointer-events-none">
      <nav className="pointer-events-auto flex items-center justify-between gap-4 px-6 py-3 rounded-full glass-pill max-w-6xl w-full transition-all">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="liquid-orb flex-shrink-0" />
          <span className="font-serif text-lg tracking-tight font-medium text-txt-primary">
            Irriga<span className="font-sans font-light opacity-60">Trace</span>
          </span>
        </Link>

        {/* Navigation Links */}
        <div className="hidden lg:flex items-center gap-1">
          {navLinks.map((link) => {
            const isActive = pathname === link.href || (link.href !== '/' && pathname.startsWith(link.href));
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`px-3.5 py-1.5 rounded-full text-xs font-sans tracking-wide transition-all ${
                  isActive
                    ? 'bg-cta-bg text-cta-text font-medium shadow-sm'
                    : 'text-txt-secondary hover:text-txt-primary hover:bg-black/5 dark:hover:bg-white/5'
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </div>

        {/* Right Section: Theme toggle, Status dot, Role selector & Launch */}
        <div className="flex items-center gap-2.5">
          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            aria-label="Toggle color theme"
            className="w-8 h-8 rounded-full flex items-center justify-center border border-border-subtle bg-surface/50 text-txt-secondary hover:text-txt-primary hover:border-border transition-colors"
          >
            {theme === 'dark' ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
          </button>

          {/* Status Indicator */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full border border-border-subtle bg-surface/40 text-[11px] font-mono text-txt-secondary">
            <span
              className={`w-2 h-2 rounded-full ${
                serverOk ? 'bg-status-ok shadow-[0_0_8px_var(--status-ok)]' : 'bg-status-bad animate-pulse'
              }`}
            />
            <span>{serverOk ? 'API Live' : 'Offline'}</span>
          </div>

          {/* Role Switcher */}
          <div className="hidden md:flex items-center border border-border-subtle bg-surface/40 rounded-full p-0.5 text-[11px] font-sans">
            {(['Supervisor', 'Admin', 'Auditor'] as const).map((r) => (
              <button
                key={r}
                onClick={() => setRole(r)}
                className={`px-2.5 py-0.5 rounded-full transition-colors ${
                  role === r
                    ? 'bg-cta-bg text-cta-text font-medium'
                    : 'text-txt-tertiary hover:text-txt-secondary'
                }`}
              >
                {r}
              </button>
            ))}
          </div>

          {/* CTA */}
          <Link
            href="/dashboard"
            className="bg-cta-bg text-cta-text hover:opacity-90 px-4 py-1.5 rounded-full text-xs font-sans font-medium transition-all shadow-sm whitespace-nowrap"
          >
            Dashboard
          </Link>
        </div>
      </nav>
    </header>
  );
}

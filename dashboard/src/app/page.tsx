'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  fetchStats,
  fetchHistory,
  SystemStats,
  HistoryRun,
} from '@/lib/api';
import StatsCards from '@/components/StatsCards';
import ActivityFeed from '@/components/ActivityFeed';
import DiffViewer from '@/components/DiffViewer';
import {
  Flame,
  ArrowRight,
  Play,
  Database,
  Layers,
  Sparkles,
  ShieldCheck,
  CheckCircle,
  FileCode,
  RotateCw,
} from 'lucide-react';

export default function OverviewPage() {
  const [stats, setStats] = useState<SystemStats>({
    total_runs: 14,
    total_healed: 38,
    real_bugs_caught: 3,
    cache_entries: 12,
    cache_hits: 26,
    cache_misses: 4,
    cache_efficiency_pct: 86.7,
    hours_saved: 15.8,
    dollars_saved: 1345.5,
  });

  const [history, setHistory] = useState<HistoryRun[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsData, historyData] = await Promise.all([
          fetchStats(),
          fetchHistory(),
        ]);
        setStats(statsData);
        setHistory(historyData);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-8">
      {/* Hero Header */}
      <section className="glass-panel p-6 sm:p-8 rounded-3xl border border-surface-border relative overflow-hidden">
        <div className="max-w-3xl space-y-4 relative z-10">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-red/10 border border-brand-red/30 text-brand-red text-xs font-mono font-medium">
            <Flame className="w-3.5 h-3.5 animate-pulse" />
            <span>AUTONOMOUS SELF-HEALING ENGINE</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-white font-sans">
            Never Waste Another Hour on{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-red via-brand-crimson to-brand-cyan">
              Broken Selectors.
            </span>
          </h1>

          <p className="text-sm sm:text-base text-gray-300 font-sans leading-relaxed">
            KernHell intercepts Playwright test breakages in CI/CD, extracts live
            DOM snapshots, cleanses HTML by 85% with Selectolax, consults dense
            semantic vector memory, and surgically patches your test source code
            via <code className="text-brand-cyan font-mono text-xs px-1.5 py-0.5 rounded bg-surface">libcst</code>{' '}
            with 100% comment and whitespace preservation.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Link
              href="/playground"
              className="flex items-center space-x-2 px-5 py-2.5 rounded-xl font-mono text-xs font-semibold bg-gradient-to-r from-brand-red to-brand-crimson text-white hover:opacity-90 shadow-glow-red transition-all"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Launch Live Playground</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>

            <Link
              href="/cache"
              className="flex items-center space-x-2 px-4 py-2.5 rounded-xl font-mono text-xs font-medium bg-surface-light hover:bg-surface-border text-gray-200 transition-colors border border-surface-border"
            >
              <Database className="w-3.5 h-3.5 text-brand-cyan" />
              <span>Inspect Vector Memory</span>
            </Link>
          </div>
        </div>

        {/* Ambient background decoration */}
        <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-gradient-to-l from-brand-red/5 to-transparent pointer-events-none hidden lg:block" />
      </section>

      {/* Top Metrics Cards */}
      <section>
        <StatsCards stats={stats} loading={loading} />
      </section>

      {/* 6-Stage Autonomous Pipeline Visualization */}
      <section className="glass-panel p-6 rounded-2xl border border-surface-border">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Layers className="w-4 h-4 text-brand-cyan" />
            <h2 className="text-sm font-mono font-bold uppercase tracking-wider text-gray-200">
              Autonomous Healing Architecture Pipeline
            </h2>
          </div>
          <span className="text-[11px] font-mono text-brand-emerald flex items-center space-x-1">
            <CheckCircle className="w-3 h-3" />
            <span>Active & Verifying</span>
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {[
            {
              step: '01',
              title: 'Subprocess Intercept',
              desc: 'Catches Playwright locator failures & captures live DOM snapshot',
              color: 'border-brand-red/40 text-brand-red',
            },
            {
              step: '02',
              title: 'Selectolax Pruning',
              desc: 'Strips SVGs/scripts, reduces DOM tokens by 85% using Lexbor',
              color: 'border-yellow-500/40 text-yellow-400',
            },
            {
              step: '03',
              title: 'Vector Cache',
              desc: '384D dense cosine search; heals in <5ms on known patterns',
              color: 'border-brand-cyan/40 text-brand-cyan',
            },
            {
              step: '04',
              title: 'Intent Brain',
              desc: 'LiteLLM diagnoses RENAME vs MISSING with anti-hallucination guard',
              color: 'border-brand-purple/40 text-brand-purple',
            },
            {
              step: '05',
              title: 'DOM Verification',
              desc: 'Strictly verifies single unambiguous match on live pruned DOM',
              color: 'border-blue-500/40 text-blue-400',
            },
            {
              step: '06',
              title: 'LibCST Patch',
              desc: 'Surgically modifies AST, preserves comments; auto-rollback on fail',
              color: 'border-brand-emerald/40 text-brand-emerald',
            },
          ].map((item, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-xl bg-surface/60 border ${item.color} flex flex-col justify-between`}
            >
              <div>
                <span className="font-mono text-[10px] font-bold tracking-widest opacity-60">
                  STAGE {item.step}
                </span>
                <h3 className="font-mono text-xs font-bold text-gray-100 mt-1">
                  {item.title}
                </h3>
                <p className="text-[11px] text-gray-400 font-sans mt-1 leading-snug">
                  {item.desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Main Grid: Live Healing Activity & Featured Transformation */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Real-time healing activity feed */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-mono font-bold uppercase tracking-wider text-gray-300 flex items-center space-x-2">
              <RotateCw className="w-4 h-4 text-brand-red animate-spin" style={{ animationDuration: '6s' }} />
              <span>Real-Time Healing Activity</span>
            </h2>
            <Link
              href="/history"
              className="text-xs font-mono text-brand-cyan hover:underline flex items-center space-x-1"
            >
              <span>View All History</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <ActivityFeed history={history} loading={loading} />
        </div>

        {/* Right: Featured Surgical CST Transformation */}
        <div className="lg:col-span-5 space-y-4">
          <h2 className="text-sm font-mono font-bold uppercase tracking-wider text-gray-300 flex items-center space-x-2">
            <FileCode className="w-4 h-4 text-brand-emerald" />
            <span>Featured Surgical AST Patch</span>
          </h2>

          <DiffViewer
            title="E-Commerce Checkout Button Patch"
            testFile="tests/test_checkout_flow.py"
            oldSelector="#buy-now"
            newSelector="page.get_by_role('button', name='Place Your Order')"
          />

          <div className="glass-panel p-4 rounded-2xl border border-surface-border text-xs space-y-2 font-sans">
            <div className="flex items-center space-x-2 text-brand-emerald font-semibold font-mono">
              <ShieldCheck className="w-4 h-4" />
              <span>Production Safety Certified</span>
            </div>
            <p className="text-gray-400 leading-relaxed">
              Every code patch generated by KernHell passes through our dual-pass
              CST validator: if the regenerated test fails when executed against
              the live browser session, KernHell immediately rolls back the file
              from the backup <code className="text-gray-200">.kernhell.bak</code>{' '}
              without polluting git status.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

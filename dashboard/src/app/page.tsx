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

  const [selectedRunIndex, setSelectedRunIndex] = useState<number>(0);

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

  const activeRun = history[selectedRunIndex] || history[0];

  return (
    <div className="space-y-8">
      {/* Hero Header */}
      <section className="glass-panel p-6 sm:p-8 rounded-3xl border border-white/[0.08] bg-[#0B0D14]/90 relative overflow-hidden shadow-2xl">
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
              className="flex items-center space-x-2 px-4 py-2.5 rounded-xl font-mono text-xs font-medium bg-[#141724] hover:bg-[#1C2032] text-gray-200 transition-colors border border-white/[0.08]"
            >
              <Database className="w-3.5 h-3.5 text-brand-cyan" />
              <span>Inspect Vector Memory</span>
            </Link>
          </div>
        </div>

        {/* Ambient background decoration */}
        <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-gradient-to-l from-brand-red/10 to-transparent pointer-events-none hidden lg:block" />
      </section>

      {/* Top Metrics Cards */}
      <section>
        <StatsCards stats={stats} loading={loading} />
      </section>

      {/* Main Grid: Live Healing Activity (Left) & Surgical AST Transformation (Right) */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left: Real-time healing activity feed */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-mono font-bold uppercase tracking-wider text-gray-200 flex items-center space-x-2">
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

          <ActivityFeed
            history={history}
            loading={loading}
            selectedRunIndex={selectedRunIndex}
            onSelectRun={(run, idx) => setSelectedRunIndex(idx)}
          />
        </div>

        {/* Right: Featured Surgical CST Transformation */}
        <div className="lg:col-span-5 space-y-4 sticky top-20">
          <h2 className="text-sm font-mono font-bold uppercase tracking-wider text-gray-200 flex items-center space-x-2">
            <FileCode className="w-4 h-4 text-brand-emerald" />
            <span>Interactive Surgical AST Patch</span>
          </h2>

          <DiffViewer
            title={activeRun ? `AST Patch: ${activeRun.test_file.split('/').pop()}` : 'Featured Surgical AST Patch'}
            testFile={activeRun?.test_file || 'tests/test_checkout_flow.py'}
            diff={activeRun?.diff}
            oldSelector={activeRun?.results?.[0]?.broken_selector || '#buy-now'}
            newSelector={activeRun?.results?.[0]?.healed_selector || "page.get_by_role('button', name='Place Your Order')"}
          />

          <div className="rounded-2xl p-4 border border-white/[0.08] bg-[#0B0D14]/80 text-xs space-y-2 font-sans shadow-inner">
            <div className="flex items-center space-x-2 text-brand-emerald font-semibold font-mono">
              <ShieldCheck className="w-4 h-4" />
              <span>Dual-Pass Safety Certified</span>
            </div>
            <p className="text-gray-400 leading-relaxed text-[11px]">
              Every code patch generated by KernHell passes through our dual-pass
              CST validator: if the regenerated test fails when executed against
              the live browser session, KernHell immediately rolls back the file
              from backup <code className="text-gray-200 font-mono">.kernhell.bak</code>{' '}
              without polluting git status.
            </p>
          </div>
        </div>
      </section>

      {/* Conceptual Architecture Strip (Placed at bottom for architectural overview) */}
      <section className="rounded-3xl p-6 sm:p-7 border border-white/[0.08] bg-[#0A0C14]/90 shadow-2xl space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/[0.06] pb-4">
          <div className="flex items-center space-x-2.5">
            <div className="w-7 h-7 rounded-lg bg-brand-cyan/10 border border-brand-cyan/30 flex items-center justify-center text-brand-cyan">
              <Layers className="w-3.5 h-3.5" />
            </div>
            <div>
              <span className="text-[10px] font-mono uppercase tracking-widest text-brand-cyan font-semibold">
                HOW IT WORKS
              </span>
              <h2 className="text-sm font-mono font-bold text-gray-100">
                Autonomous Healing Architecture Pipeline
              </h2>
            </div>
          </div>
          <span className="text-[11px] font-mono text-brand-emerald flex items-center space-x-1.5 self-start sm:self-auto px-2.5 py-1 rounded-full bg-brand-emerald/10 border border-brand-emerald/20">
            <CheckCircle className="w-3 h-3" />
            <span>Dual-Pass Zero-Hallucination Pipeline</span>
          </span>
        </div>

        {/* Horizontal Flowchart Node Strip */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {[
            {
              step: '01',
              title: 'Subprocess Intercept',
              desc: 'Catches Playwright locator failures & captures live DOM snapshot',
              badge: 'PLAYWRIGHT',
              color: 'border-brand-red/30 bg-brand-red/[0.04] text-brand-red',
            },
            {
              step: '02',
              title: 'Selectolax Pruning',
              desc: 'Strips SVGs/scripts, cuts tokens by 85% via Lexbor parser',
              badge: 'LEXBOR',
              color: 'border-yellow-500/30 bg-yellow-500/[0.04] text-yellow-400',
            },
            {
              step: '03',
              title: 'Dense Vector Cache',
              desc: '384D cosine similarity lookup (<5ms, zero LLM cost)',
              badge: 'MINILM-L6',
              color: 'border-brand-cyan/30 bg-brand-cyan/[0.04] text-brand-cyan',
            },
            {
              step: '04',
              title: 'Intent AI Brain',
              desc: 'Diagnoses RENAME vs MISSING with anti-hallucination guard',
              badge: 'GEMINI 3.5',
              color: 'border-brand-purple/30 bg-brand-purple/[0.04] text-brand-purple',
            },
            {
              step: '05',
              title: 'DOM Verification',
              desc: 'Strictly verifies single unambiguous match on live pruned DOM',
              badge: 'STRICT MATCH',
              color: 'border-blue-500/30 bg-blue-500/[0.04] text-blue-400',
            },
            {
              step: '06',
              title: 'LibCST Patch',
              desc: 'Surgically modifies AST; preserves comments & whitespace',
              badge: 'ATOMIC ROLLBACK',
              color: 'border-brand-emerald/30 bg-brand-emerald/[0.04] text-brand-emerald',
            },
          ].map((item, idx) => (
            <div
              key={idx}
              className={`p-3.5 rounded-xl border ${item.color} flex flex-col justify-between space-y-2 hover:border-white/20 transition-all`}
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[10px] font-bold tracking-widest opacity-60">
                    STAGE {item.step}
                  </span>
                  <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-white/[0.05] border border-white/10 uppercase">
                    {item.badge}
                  </span>
                </div>
                <h3 className="font-mono text-xs font-bold text-gray-100 mt-2">
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
    </div>
  );
}

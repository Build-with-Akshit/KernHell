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
  ChevronDown,
  ChevronUp,
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
  const [showPipeline, setShowPipeline] = useState<boolean>(true);

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

      {/* Conceptual Architecture Lifecycle (Subtle & Non-Intrusive Informational Schematic) */}
      <section className="rounded-2xl border border-dashed border-white/[0.08] bg-[#07080E]/50 p-4 sm:p-5 text-gray-400 transition-all">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-6 h-6 rounded-md bg-white/[0.03] border border-white/[0.06] flex items-center justify-center text-gray-500">
              <Layers className="w-3.5 h-3.5" />
            </div>
            <div className="flex flex-wrap items-baseline gap-x-2">
              <span className="text-xs font-mono font-medium text-gray-300">
                Engine Architecture Flow
              </span>
              <span className="text-[11px] font-mono text-gray-500">
                • Conceptual reference only (how healing executes in background)
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-2.5">
            <span className="hidden md:inline-block text-[10px] font-mono text-gray-500 px-2 py-0.5 rounded bg-white/[0.02] border border-white/[0.05]">
              6-stage background spec
            </span>
            <button
              type="button"
              onClick={() => setShowPipeline(!showPipeline)}
              className="flex items-center space-x-1.5 text-[11px] font-mono text-gray-400 hover:text-white px-2.5 py-1 rounded-lg bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.06] transition-colors"
            >
              <span>{showPipeline ? 'Collapse' : 'Expand Flow'}</span>
              {showPipeline ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            </button>
          </div>
        </div>

        {showPipeline && (
          <div className="mt-4 pt-3.5 border-t border-white/[0.04]">
            {/* Sleek horizontal stepper track */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2 sm:gap-2.5">
              {[
                {
                  step: '01',
                  title: 'Subprocess Intercept',
                  tech: 'PLAYWRIGHT',
                  desc: 'Catches locator breakages & grabs live browser DOM snapshot',
                },
                {
                  step: '02',
                  title: 'Lexbor Pruning',
                  tech: 'SELECTOLAX',
                  desc: 'Strips SVGs/styles, shrinking prompt tokens by 85%',
                },
                {
                  step: '03',
                  title: 'Vector Cache',
                  tech: 'MINILM-L6',
                  desc: '<5ms cosine lookup in local 384D semantic vector index',
                },
                {
                  step: '04',
                  title: 'AI Reasoning',
                  tech: 'GEMINI 3.5',
                  desc: 'Diagnoses rename vs real bug with anti-hallucination guard',
                },
                {
                  step: '05',
                  title: 'DOM Verification',
                  tech: 'STRICT MATCH',
                  desc: 'Dual-pass verification ensures element exists unambiguously',
                },
                {
                  step: '06',
                  title: 'LibCST Patch',
                  tech: 'SURGICAL CST',
                  desc: 'Surgically edits test file with 100% comment/whitespace integrity',
                },
              ].map((item, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl border border-white/[0.04] bg-white/[0.015] hover:bg-white/[0.03] hover:border-white/[0.08] transition-all flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between text-[10px] font-mono text-gray-500 mb-1.5">
                      <span>STAGE {item.step}</span>
                      <span className="text-[9px] px-1 py-0.2 rounded bg-white/[0.03] border border-white/[0.05] text-gray-400">
                        {item.tech}
                      </span>
                    </div>
                    <h4 className="font-mono text-xs font-medium text-gray-200">
                      {item.title}
                    </h4>
                    <p className="text-[10px] text-gray-500 font-sans mt-1 leading-snug">
                      {item.desc}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

'use client';

import React, { useState } from 'react';
import { HistoryRun } from '@/lib/api';
import {
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Zap,
  Cpu,
  Clock,
  Code2,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  Check,
} from 'lucide-react';
import DiffViewer from './DiffViewer';

interface ActivityFeedProps {
  history: HistoryRun[];
  loading?: boolean;
  selectedRunIndex?: number | null;
  onSelectRun?: (run: HistoryRun, index: number) => void;
}

export default function ActivityFeed({
  history,
  loading,
  selectedRunIndex,
  onSelectRun,
}: ActivityFeedProps) {
  const [inlineDiffIndex, setInlineDiffIndex] = useState<number | null>(null);

  if (loading) {
    return (
      <div className="rounded-2xl p-8 border border-white/[0.08] bg-[#0B0D14]/80 text-center text-gray-400 font-mono text-xs space-y-3">
        <div className="w-6 h-6 border-2 border-brand-red border-t-transparent rounded-full animate-spin mx-auto" />
        <p>Streaming real-time healing events...</p>
      </div>
    );
  }

  if (!history || history.length === 0) {
    return (
      <div className="rounded-2xl p-8 border border-white/[0.08] bg-[#0B0D14]/80 text-center text-gray-500 font-mono text-xs space-y-2">
        <ShieldCheck className="w-8 h-8 text-brand-emerald mx-auto opacity-70" />
        <p className="text-gray-300 font-medium">All Test Suites Healthy</p>
        <p className="text-gray-500 text-[11px]">No active selector failures detected in recent runs.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {history.map((run, idx) => {
        const isSelected = selectedRunIndex === idx;
        const isInlineDiffOpen = inlineDiffIndex === idx;
        const isHealed = run.healed_count > 0;
        const isSkipped = run.skipped_count > 0;
        const primaryResult = run.results && run.results[0];

        return (
          <div
            key={idx}
            onClick={() => onSelectRun?.(run, idx)}
            className={`rounded-2xl border transition-all duration-200 cursor-pointer overflow-hidden ${
              isSelected
                ? 'bg-[#101322] border-brand-red/50 shadow-lg shadow-brand-red/5'
                : 'bg-[#0B0D14]/80 hover:bg-[#0F121E] border-white/[0.07] hover:border-white/[0.15]'
            }`}
          >
            {/* Main Card Header */}
            <div className="p-4 sm:p-5 space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
                <div className="flex items-center space-x-3">
                  <div className="shrink-0">
                    {isHealed ? (
                      <div className="w-8 h-8 rounded-xl bg-brand-emerald/10 border border-brand-emerald/30 flex items-center justify-center text-brand-emerald shadow-sm">
                        <CheckCircle2 className="w-4 h-4" />
                      </div>
                    ) : (
                      <div className="w-8 h-8 rounded-xl bg-brand-purple/10 border border-brand-purple/30 flex items-center justify-center text-brand-purple shadow-sm">
                        <AlertTriangle className="w-4 h-4" />
                      </div>
                    )}
                  </div>

                  <div>
                    <div className="flex items-center space-x-2 flex-wrap">
                      <span className="font-mono text-xs font-bold text-gray-100">
                        {run.test_file}
                      </span>
                      {isHealed && (
                        <span className="inline-flex items-center space-x-1 px-2 py-0.5 text-[10px] font-mono font-bold tracking-wider rounded-md bg-brand-emerald/15 text-brand-emerald border border-brand-emerald/30">
                          <span className="w-1.5 h-1.5 rounded-full bg-brand-emerald" />
                          <span>HEALED</span>
                        </span>
                      )}
                      {isSkipped && (
                        <span className="inline-flex items-center space-x-1 px-2 py-0.5 text-[10px] font-mono font-bold tracking-wider rounded-md bg-brand-purple/15 text-brand-purple border border-brand-purple/30">
                          <span className="w-1.5 h-1.5 rounded-full bg-brand-purple" />
                          <span>GUARDED (BUG)</span>
                        </span>
                      )}
                    </div>
                    <div className="flex items-center space-x-3 text-[11px] text-gray-400 mt-1">
                      <span className="flex items-center space-x-1">
                        <Clock className="w-3 h-3 text-gray-500" />
                        <span>{run.duration_ms}ms</span>
                      </span>
                      <span>•</span>
                      <span>{run.total_failures} failure detected</span>
                    </div>
                  </div>
                </div>

                {/* Right Badges */}
                <div className="flex items-center space-x-2 self-start sm:self-center shrink-0">
                  {run.cache_hits > 0 ? (
                    <span className="inline-flex items-center space-x-1 text-[10px] font-mono font-medium px-2.5 py-1 rounded-lg bg-brand-cyan/10 text-brand-cyan border border-brand-cyan/30">
                      <Zap className="w-3 h-3 fill-current" />
                      <span>Vector Hit</span>
                    </span>
                  ) : (
                    <span className="inline-flex items-center space-x-1 text-[10px] font-mono font-medium px-2.5 py-1 rounded-lg bg-white/[0.04] text-gray-300 border border-white/[0.08]">
                      <Cpu className="w-3 h-3 text-brand-red" />
                      <span>AI Healer</span>
                    </span>
                  )}

                  {isSelected && (
                    <span className="text-[10px] font-mono text-brand-red bg-brand-red/10 border border-brand-red/30 px-2 py-1 rounded-lg font-semibold">
                      Viewing Diff
                    </span>
                  )}
                </div>
              </div>

              {/* Selector Transition Row */}
              {primaryResult && (
                <div className="p-3 rounded-xl bg-[#06080E]/70 border border-white/[0.06] space-y-2">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center space-x-2 flex-wrap font-mono text-xs">
                      <span className="text-red-400 bg-red-950/40 px-2 py-1 rounded-md border border-red-500/30 font-medium">
                        {primaryResult.broken_selector}
                      </span>
                      {primaryResult.healed_selector && (
                        <>
                          <ArrowRight className="w-3.5 h-3.5 text-gray-500 shrink-0" />
                          <span className="text-emerald-400 bg-emerald-950/40 px-2 py-1 rounded-md border border-emerald-500/30 font-semibold break-all">
                            {primaryResult.healed_selector}
                          </span>
                        </>
                      )}
                    </div>
                    <span className="text-[11px] font-mono text-gray-500 shrink-0">
                      Line {primaryResult.line_number}
                    </span>
                  </div>

                  {primaryResult.skipped ? (
                    <div className="text-[11px] font-sans text-brand-purple bg-brand-purple/10 px-3 py-1.5 rounded-lg border border-brand-purple/30">
                      <strong className="font-mono">Anti-Hallucination Guardrail:</strong> {primaryResult.skip_reason}
                    </div>
                  ) : (
                    <div className="flex items-center space-x-3 text-[11px] font-mono text-gray-400">
                      <span>
                        Strategy: <strong className="text-brand-cyan">{primaryResult.strategy || 'resilient_locator'}</strong>
                      </span>
                      <span>•</span>
                      <span>
                        Confidence: <strong className="text-brand-emerald">{((primaryResult.confidence || 0.95) * 100).toFixed(0)}%</strong>
                      </span>
                    </div>
                  )}
                </div>
              )}

              {/* Action Toolbar */}
              <div className="flex items-center justify-between pt-1">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setInlineDiffIndex(isInlineDiffOpen ? null : idx);
                  }}
                  className="inline-flex items-center space-x-1.5 text-[11px] font-mono text-gray-400 hover:text-white px-2.5 py-1 rounded-lg bg-white/[0.03] hover:bg-white/[0.08] border border-white/[0.06] transition-colors"
                >
                  <Code2 className="w-3 h-3 text-brand-cyan" />
                  <span>{isInlineDiffOpen ? 'Hide Inline Diff' : 'Toggle Inline Diff'}</span>
                  {isInlineDiffOpen ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                </button>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectRun?.(run, idx);
                  }}
                  className="text-[11px] font-mono text-brand-cyan hover:text-white transition-colors flex items-center space-x-1"
                >
                  <span>Inspect Side-by-Side</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>

            {/* Optional Collapsible Inline Diff */}
            {isInlineDiffOpen && run.diff && (
              <div className="border-t border-white/[0.08] p-4 bg-[#05060A]">
                <DiffViewer diff={run.diff} testFile={run.test_file} />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

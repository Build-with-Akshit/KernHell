'use client';

import React, { useState } from 'react';
import { HistoryRun } from '@/lib/api';
import { CheckCircle2, AlertTriangle, ArrowRight, Zap, Cpu, Clock, ChevronDown, ChevronUp } from 'lucide-react';
import DiffViewer from './DiffViewer';

interface ActivityFeedProps {
  history: HistoryRun[];
  loading?: boolean;
}

export default function ActivityFeed({ history, loading }: ActivityFeedProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0);

  const toggleExpand = (idx: number) => {
    setExpandedIndex(expandedIndex === idx ? null : idx);
  };

  if (loading) {
    return (
      <div className="glass-panel rounded-2xl p-6 border border-surface-border text-center text-gray-500 font-mono text-sm">
        Loading real-time healing stream...
      </div>
    );
  }

  if (!history || history.length === 0) {
    return (
      <div className="glass-panel rounded-2xl p-6 border border-surface-border text-center text-gray-500 font-mono text-sm">
        No recent test suite failures recorded. System healthy.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {history.map((run, idx) => {
        const isExpanded = expandedIndex === idx;
        const isHealed = run.healed_count > 0;
        const isSkipped = run.skipped_count > 0;

        return (
          <div
            key={idx}
            className="glass-panel rounded-2xl border border-surface-border overflow-hidden transition-all duration-200"
          >
            {/* Row header */}
            <div
              onClick={() => toggleExpand(idx)}
              className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 cursor-pointer hover:bg-surface-light/40 transition-colors"
            >
              <div className="flex items-start sm:items-center space-x-3">
                <div className="mt-0.5 sm:mt-0">
                  {isHealed ? (
                    <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
                      <CheckCircle2 className="w-4 h-4 text-brand-emerald" />
                    </div>
                  ) : (
                    <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center">
                      <AlertTriangle className="w-4 h-4 text-brand-purple" />
                    </div>
                  )}
                </div>

                <div>
                  <div className="flex items-center space-x-2 flex-wrap">
                    <span className="font-mono text-xs font-semibold text-gray-200">
                      {run.test_file}
                    </span>
                    {isHealed && (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-brand-emerald/10 text-brand-emerald border border-brand-emerald/30 font-semibold">
                        HEALED ({run.healed_count})
                      </span>
                    )}
                    {isSkipped && (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-brand-purple/10 text-brand-purple border border-brand-purple/30 font-semibold">
                        GUARDED (REAL BUG)
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-gray-400 font-sans mt-0.5">
                    {run.total_failures} failure detected • Duration: {run.duration_ms}ms
                  </p>
                </div>
              </div>

              {/* Right indicators */}
              <div className="flex items-center space-x-3 self-end sm:self-center">
                {run.cache_hits > 0 ? (
                  <span className="flex items-center space-x-1 text-[11px] font-mono px-2 py-1 rounded bg-brand-cyan/10 text-brand-cyan border border-brand-cyan/20">
                    <Zap className="w-3 h-3" />
                    <span>Vector Hit</span>
                  </span>
                ) : (
                  <span className="flex items-center space-x-1 text-[11px] font-mono px-2 py-1 rounded bg-surface text-gray-400 border border-surface-border">
                    <Cpu className="w-3 h-3 text-brand-red" />
                    <span>LLM Diagnosed</span>
                  </span>
                )}

                <button className="text-gray-400 hover:text-white p-1">
                  {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Expanded failure details */}
            {isExpanded && (
              <div className="px-4 pb-4 pt-1 border-t border-surface-border/60 bg-[#08090e]/50 space-y-3">
                {run.results.map((res, rIdx) => (
                  <div
                    key={rIdx}
                    className="p-3 rounded-xl bg-surface/80 border border-surface-border font-mono text-xs space-y-2"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-red-400 bg-red-950/40 px-2 py-0.5 rounded border border-red-800/40">
                          {res.broken_selector}
                        </span>
                        {res.healed_selector && (
                          <>
                            <ArrowRight className="w-3 h-3 text-gray-500" />
                            <span className="text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-800/40">
                              {res.healed_selector}
                            </span>
                          </>
                        )}
                      </div>
                      <span className="text-[10px] text-gray-500">Line {res.line_number}</span>
                    </div>

                    {res.skipped ? (
                      <div className="text-[11px] font-sans text-brand-purple bg-brand-purple/5 p-2 rounded border border-brand-purple/20">
                        <strong>Anti-Hallucination Guardrail:</strong> {res.skip_reason}
                      </div>
                    ) : (
                      <div className="flex items-center space-x-3 text-[10px] text-gray-400">
                        <span>
                          Strategy: <strong className="text-brand-cyan">{res.strategy}</strong>
                        </span>
                        <span>•</span>
                        <span>
                          Confidence: <strong className="text-brand-emerald">{((res.confidence || 0.95) * 100).toFixed(0)}%</strong>
                        </span>
                      </div>
                    )}
                  </div>
                ))}

                {/* Diff Viewer for this run */}
                {run.diff && (
                  <div className="pt-2">
                    <DiffViewer diff={run.diff} testFile={run.test_file} />
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

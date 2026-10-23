'use client';

import React, { useEffect, useState } from 'react';
import { fetchHistory, HistoryRun } from '@/lib/api';
import ActivityFeed from '@/components/ActivityFeed';
import { History, Filter, FileText, CheckCircle, ShieldAlert, Layers } from 'lucide-react';

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterMode, setFilterMode] = useState<'all' | 'healed' | 'guarded'>('all');

  useEffect(() => {
    loadHistory();
  }, []);

  async function loadHistory() {
    setLoading(true);
    try {
      const data = await fetchHistory();
      setHistory(data);
    } catch (e) {
      console.error('Failed to load history:', e);
    } finally {
      setLoading(false);
    }
  }

  const filtered = history.filter((run) => {
    if (filterMode === 'healed') return run.healed_count > 0;
    if (filterMode === 'guarded') return run.skipped_count > 0;
    return true;
  });

  const totalRuns = history.length;
  const totalHealed = history.reduce((acc, curr) => acc + curr.healed_count, 0);
  const totalGuarded = history.reduce((acc, curr) => acc + curr.skipped_count, 0);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-surface-border">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-red/10 border border-brand-red/30 text-brand-red text-xs font-mono font-medium">
              <History className="w-3.5 h-3.5" />
              <span>CI/CD RUN AUDIT LOG & DIFF INSPECTOR</span>
            </div>
            <h1 className="text-2xl sm:text-4xl font-black text-white font-sans">
              Test Run History
            </h1>
            <p className="text-xs sm:text-sm text-gray-400 font-sans max-w-2xl">
              Chronological log of all Playwright test suite failures, self-healing
              transformations, and anti-hallucination guardrail actions.
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center space-x-2 self-start md:self-auto bg-surface-light p-1 rounded-xl border border-surface-border text-xs font-mono">
            <button
              onClick={() => setFilterMode('all')}
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                filterMode === 'all'
                  ? 'bg-surface-border text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              All Runs ({totalRuns})
            </button>
            <button
              onClick={() => setFilterMode('healed')}
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                filterMode === 'healed'
                  ? 'bg-brand-emerald/20 text-brand-emerald border border-brand-emerald/30'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Healed ({totalHealed})
            </button>
            <button
              onClick={() => setFilterMode('guarded')}
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                filterMode === 'guarded'
                  ? 'bg-brand-purple/20 text-brand-purple border border-brand-purple/30'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Guarded ({totalGuarded})
            </button>
          </div>
        </div>
      </div>

      {/* Main Stream */}
      <div>
        <ActivityFeed history={filtered} loading={loading} />
      </div>
    </div>
  );
}

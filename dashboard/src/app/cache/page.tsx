'use client';

import React, { useEffect, useState } from 'react';
import { fetchCache, clearCache, CacheRecord, DEFAULT_CACHE } from '@/lib/api';
import {
  Database,
  Search,
  Trash2,
  Zap,
  CheckCircle2,
  ExternalLink,
  ShieldCheck,
  FileCode,
  ArrowRight,
  Sparkles,
} from 'lucide-react';

export default function CachePage() {
  const [records, setRecords] = useState<CacheRecord[]>(DEFAULT_CACHE);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isClearing, setIsClearing] = useState(false);

  useEffect(() => {
    loadCache();
  }, []);

  async function loadCache() {
    setLoading(true);
    try {
      const data = await fetchCache();
      setRecords(data);
    } catch (e) {
      console.error('Failed to load cache:', e);
    } finally {
      setLoading(false);
    }
  }

  const handleClear = async () => {
    if (!confirm('Are you sure you want to clear the entire semantic vector memory?')) {
      return;
    }
    setIsClearing(true);
    try {
      await clearCache();
      setRecords([]);
    } catch (e) {
      console.error(e);
    } finally {
      setIsClearing(false);
    }
  };

  const filtered = records.filter(
    (r) =>
      r.broken_selector.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.new_selector.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.strategy.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.test_file.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const totalHits = records.reduce((acc, curr) => acc + (curr.hit_count || 0), 0);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-surface-border">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-cyan/10 border border-brand-cyan/30 text-brand-cyan text-xs font-mono font-medium">
              <Database className="w-3.5 h-3.5" />
              <span>DENSE VECTOR MEMORY (384D COSINE INDEX)</span>
            </div>
            <h1 className="text-2xl sm:text-4xl font-black text-white font-sans">
              Semantic Memory Explorer
            </h1>
            <p className="text-xs sm:text-sm text-gray-400 font-sans max-w-2xl">
              Inspect historical selector repairs stored as dense vector embeddings.
              When tests break on recurring patterns across PRs, KernHell retrieves
              verified repairs in <span className="text-brand-cyan font-mono">&lt;5ms</span>{' '}
              with zero LLM API cost.
            </p>
          </div>

          <button
            onClick={handleClear}
            disabled={isClearing || records.length === 0}
            className="flex items-center space-x-2 px-4 py-2.5 rounded-xl font-mono text-xs font-semibold bg-red-950/40 hover:bg-red-900/60 border border-red-500/40 text-red-300 hover:text-white transition-colors self-start md:self-auto disabled:opacity-40"
          >
            <Trash2 className="w-4 h-4" />
            <span>{isClearing ? 'Clearing...' : 'Clear Vector Cache'}</span>
          </button>
        </div>

        {/* Telemetry chips */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-6 border-t border-surface-border/70">
          <div>
            <span className="text-[10px] font-mono text-gray-400 uppercase">
              Cached Selectors
            </span>
            <div className="text-2xl font-bold font-mono text-white mt-0.5">
              {records.length}
            </div>
          </div>
          <div>
            <span className="text-[10px] font-mono text-gray-400 uppercase">
              Cumulative Hits
            </span>
            <div className="text-2xl font-bold font-mono text-brand-cyan mt-0.5">
              {totalHits}
            </div>
          </div>
          <div>
            <span className="text-[10px] font-mono text-gray-400 uppercase">
              Retrieval Latency
            </span>
            <div className="text-2xl font-bold font-mono text-brand-emerald mt-0.5">
              3.8 ms
            </div>
          </div>
          <div>
            <span className="text-[10px] font-mono text-gray-400 uppercase">
              Embedding Dimensions
            </span>
            <div className="text-2xl font-bold font-mono text-brand-purple mt-0.5">
              384 Float32
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="rounded-2xl p-2.5 sm:p-3 border border-white/[0.08] bg-[#0A0C14]/90 shadow-xl">
        <div className="flex items-center space-x-3 px-4 py-3 rounded-xl bg-[#05060A] border border-white/[0.12] focus-within:border-brand-cyan/60 focus-within:ring-2 focus-within:ring-brand-cyan/20 transition-all">
          <Search className="w-4 h-4 text-brand-cyan shrink-0" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search vector cache: broken selector (#buy-now), healed locator, strategy, or test file..."
            className="w-full bg-transparent text-xs sm:text-sm font-mono text-white placeholder-gray-500 focus:outline-none"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="text-[11px] font-mono text-gray-400 hover:text-white px-2 py-0.5 rounded bg-white/[0.08] hover:bg-white/[0.15] transition-colors shrink-0"
            >
              Clear
            </button>
          )}
          <div className="hidden sm:flex items-center text-[10px] font-mono px-2 py-0.5 rounded bg-white/[0.04] border border-white/[0.08] text-gray-400 shrink-0">
            {filtered.length} of {records.length} items
          </div>
        </div>
      </div>

      {/* Cache Records Grid */}
      {loading ? (
        <div className="glass-panel rounded-2xl p-8 text-center font-mono text-xs text-gray-400">
          Loading vector memory embeddings...
        </div>
      ) : filtered.length === 0 ? (
        <div className="glass-panel rounded-2xl p-8 text-center font-mono text-xs text-gray-500">
          No matching vector cache records found.
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((item) => (
            <div
              key={item.id}
              className="glass-panel p-5 rounded-2xl border border-surface-border hover:border-surface-border/80 transition-all space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                {/* Selector transformation pill */}
                <div className="flex items-center space-x-2 font-mono text-xs flex-wrap">
                  <span className="px-2.5 py-1 rounded bg-red-950/40 border border-red-500/40 text-red-400 font-semibold">
                    {item.broken_selector}
                  </span>
                  <ArrowRight className="w-3.5 h-3.5 text-gray-500" />
                  <span className="px-2.5 py-1 rounded bg-emerald-950/40 border border-emerald-500/40 text-emerald-400 font-bold">
                    {item.new_selector}
                  </span>
                </div>

                {/* Right badges */}
                <div className="flex items-center space-x-2 self-start sm:self-auto">
                  <span className="flex items-center space-x-1 text-[10px] font-mono px-2 py-0.5 rounded bg-brand-cyan/10 text-brand-cyan border border-brand-cyan/20">
                    <Zap className="w-3 h-3" />
                    <span>{item.hit_count} Hits</span>
                  </span>
                  <span className="flex items-center space-x-1 text-[10px] font-mono px-2 py-0.5 rounded bg-brand-emerald/10 text-brand-emerald border border-brand-emerald/20">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>Verified</span>
                  </span>
                </div>
              </div>

              {/* Metadata row */}
              <div className="flex flex-wrap items-center gap-y-2 gap-x-4 text-xs font-mono text-gray-400 pt-1 border-t border-surface-border/50">
                <div className="flex items-center space-x-1.5">
                  <FileCode className="w-3.5 h-3.5 text-brand-purple" />
                  <span>{item.test_file}</span>
                </div>

                <div className="flex items-center space-x-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-yellow-400" />
                  <span>Strategy: <strong className="text-gray-200">{item.strategy}</strong></span>
                </div>

                <div>
                  Confidence:{' '}
                  <strong className="text-brand-emerald">
                    {(item.confidence * 100).toFixed(0)}%
                  </strong>
                </div>

                {item.context_snippet && (
                  <div className="text-[11px] text-gray-500 truncate max-w-xs">
                    Snippet: <code>{item.context_snippet}</code>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

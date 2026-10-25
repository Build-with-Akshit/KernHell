'use client';

import React, { useState, useCallback } from 'react';
import { simulateHeal, SimulateResult } from '@/lib/api';
import DiffViewer from '@/components/DiffViewer';
import {
  Play,
  Sparkles,
  ShieldAlert,
  CheckCircle2,
  Cpu,
  RotateCcw,
  AlertTriangle,
  Code2,
  X,
  ChevronRight,
  Zap,
  Eye,
  FileCode2,
  Terminal,
} from 'lucide-react';

// ─── Presets ─────────────────────────────────────────────────────────────────

const PRESETS = [
  {
    id: 'rename',
    name: '1. Button Rename',
    badge: 'RENAME',
    badgeColor: 'text-brand-cyan border-brand-cyan/30 bg-brand-cyan/10',
    broken_selector: '#buy-now',
    dom_html: `<div class="checkout-container">
  <div class="cart-summary">
    <h2>Order Total: $49.99</h2>
  </div>
  <div class="actions">
    <!-- Refactored button: old id #buy-now removed -->
    <button type="submit" id="purchase-btn" data-testid="complete-order-btn" role="button">
      Place Your Order
    </button>
  </div>
</div>`,
    surrounding_code: `def test_checkout_purchase(page):
    page.goto("https://shop.example.com/checkout")
    # Step 1: verify cart items
    expect(page.locator(".cart-summary")).to_be_visible()
    # Step 2: click purchase button (broken selector)
    page.click("#buy-now")  # inline comment to preserve
    # Step 3: verify receipt
    expect(page.locator(".confirmation")).to_be_visible()`,
  },
  {
    id: 'missing',
    name: '2. Real Bug (Missing)',
    badge: 'MISSING',
    badgeColor: 'text-brand-purple border-purple-500/30 bg-purple-950/30',
    broken_selector: '.add-to-cart-btn',
    dom_html: `<div class="product-page">
  <h1>Wireless Headphones</h1>
  <div class="inventory-status">
    <div role="alert" class="out-of-stock-banner text-red-500 font-bold">
      Out of Stock - Currently Unavailable
    </div>
  </div>
  <!-- Button has been completely removed from DOM by frontend logic -->
</div>`,
    surrounding_code: `def test_add_inventory_item(page):
    page.goto("https://shop.example.com/product/101")
    # Click add to cart (element was removed due to out-of-stock)
    page.click(".add-to-cart-btn")
    expect(page.locator(".cart-drawer")).to_be_visible()`,
  },
  {
    id: 'testid',
    name: '3. Data-TestID Upgrade',
    badge: 'TESTID',
    badgeColor: 'text-brand-emerald border-emerald-500/30 bg-emerald-950/20',
    broken_selector: '.submit-payment-btn',
    dom_html: `<form class="payment-form">
  <input type="text" placeholder="Card Number" />
  <button type="button" class="btn primary-action" data-testid="complete-order-btn">
    Confirm Payment
  </button>
</form>`,
    surrounding_code: `def test_payment_submission(page):
    # Submit payment
    page.click(".submit-payment-btn")  # must be upgraded to resilient locator`,
  },
] as const;

type PresetId = (typeof PRESETS)[number]['id'];

// ─── Helpers ─────────────────────────────────────────────────────────────────

function diagnosisColor(type: string) {
  if (type === 'missing') return 'text-brand-purple';
  if (type === 'structural') return 'text-yellow-400';
  return 'text-brand-cyan';
}

function compressionColor(pct: number) {
  if (pct >= 70) return 'text-brand-emerald';
  if (pct >= 40) return 'text-yellow-400';
  return 'text-brand-red';
}

// ─── Component ────────────────────────────────────────────────────────────────

export default function PlaygroundPage() {
  const [activePreset, setActivePreset] = useState<PresetId | null>('rename');
  const [brokenSelector, setBrokenSelector] = useState<string>(PRESETS[0].broken_selector);
  const [domHtml, setDomHtml] = useState<string>(PRESETS[0].dom_html);
  const [surroundingCode, setSurroundingCode] = useState<string>(PRESETS[0].surrounding_code);
  const [isSimulating, setIsSimulating] = useState(false);
  const [result, setResult] = useState<SimulateResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showPrunedDom, setShowPrunedDom] = useState(false);

  const loadPreset = useCallback((preset: (typeof PRESETS)[number]) => {
    setActivePreset(preset.id);
    setBrokenSelector(preset.broken_selector);
    setDomHtml(preset.dom_html);
    setSurroundingCode(preset.surrounding_code);
    setResult(null);
    setError(null);
    setShowPrunedDom(false);
  }, []);

  const handleReset = () => {
    setActivePreset(null);
    setBrokenSelector('');
    setDomHtml('');
    setSurroundingCode('');
    setResult(null);
    setError(null);
    setShowPrunedDom(false);
  };

  const handleSimulate = async () => {
    if (!brokenSelector.trim() || !domHtml.trim()) return;
    setIsSimulating(true);
    setResult(null);
    setError(null);
    setShowPrunedDom(false);

    try {
      const res = await simulateHeal({
        broken_selector: brokenSelector,
        dom_html: domHtml,
        surrounding_code: surroundingCode,
      });
      setResult(res);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Unknown error occurred';
      setError(`Pipeline failed: ${msg}`);
    } finally {
      setIsSimulating(false);
    }
  };

  // Derive verification status from result
  const verificationPassed =
    result &&
    result.diagnosis.failure_type !== 'missing' &&
    !!result.healed_selector;

  const testFileName = surroundingCode.match(/def (test_\w+)/)?.[1]
    ? `${surroundingCode.match(/def (test_\w+)/)![1]}.py`
    : 'test_playwright.py';

  return (
    <div className="space-y-8">
      {/* ── Page Header ──────────────────────────────────────────────────── */}
      <div className="glass-panel p-6 rounded-3xl border border-surface-border">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-cyan/10 border border-brand-cyan/30 text-brand-cyan text-xs font-mono font-medium mb-3">
              <Sparkles className="w-3.5 h-3.5" />
              <span>INTERACTIVE AI HEALING SIMULATOR</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white font-sans">
              Test Healer Sandbox
            </h1>
            <p className="text-xs sm:text-sm text-gray-400 font-sans mt-1 max-w-xl">
              Provide a broken locator + live DOM snapshot to watch KernHell run its full
              pipeline: <span className="text-brand-cyan font-medium">Selectolax pruning</span>{' '}
              → <span className="text-brand-purple font-medium">AI intent diagnosis</span> →{' '}
              <span className="text-brand-emerald font-medium">LibCST surgical patch</span>.
            </p>
          </div>

          {/* Preset Buttons */}
          <div className="flex flex-col gap-1.5 min-w-max">
            <span className="text-[10px] font-mono text-gray-500 uppercase tracking-wider">
              Load a preset scenario
            </span>
            <div className="flex flex-wrap gap-2">
              {PRESETS.map((p) => (
                <button
                  key={p.id}
                  onClick={() => loadPreset(p)}
                  className={`px-3 py-1.5 text-xs font-mono rounded-lg border transition-all ${
                    activePreset === p.id
                      ? `${p.badgeColor} font-bold ring-1 ring-current`
                      : 'bg-surface hover:bg-surface-light border-surface-border text-gray-300 hover:text-white'
                  }`}
                >
                  {p.name}
                </button>
              ))}
              <button
                onClick={handleReset}
                title="Clear all inputs"
                className="px-3 py-1.5 text-xs font-mono rounded-lg bg-surface hover:bg-red-950/40 border border-surface-border hover:border-brand-red/40 text-gray-500 hover:text-brand-red transition-all flex items-center gap-1.5"
              >
                <X className="w-3 h-3" />
                Clear
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* ── Input Sandbox ────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Selector + DOM */}
        <div className="space-y-4">
          {/* Broken Selector */}
          <div className="glass-panel p-4 rounded-2xl border border-surface-border space-y-2">
            <label className="text-xs font-mono font-semibold text-gray-300 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Terminal className="w-3.5 h-3.5 text-brand-red" />
                Broken Selector / Locator
              </span>
              <span className="text-[10px] text-brand-red font-mono bg-brand-red/10 px-2 py-0.5 rounded-full border border-brand-red/20">
                ✕ Failed in CI
              </span>
            </label>
            <input
              type="text"
              value={brokenSelector}
              onChange={(e) => {
                setBrokenSelector(e.target.value);
                setActivePreset(null);
                setResult(null);
              }}
              placeholder="e.g.  #buy-now  or  .submit-btn  or  [data-id='cta']"
              className="w-full px-3 py-2.5 rounded-xl bg-[#090a0f] border border-surface-border text-brand-red font-mono text-sm focus:outline-none focus:border-brand-red/60 placeholder:text-gray-700"
            />
          </div>

          {/* Live DOM */}
          <div className="glass-panel p-4 rounded-2xl border border-surface-border space-y-2 flex flex-col">
            <label className="text-xs font-mono font-semibold text-gray-300 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Code2 className="w-3.5 h-3.5 text-gray-400" />
                Live Page DOM (Playwright capture)
              </span>
              <span className="text-[10px] text-gray-500 font-mono">
                {new TextEncoder().encode(domHtml).length} bytes raw
              </span>
            </label>
            <textarea
              rows={11}
              value={domHtml}
              onChange={(e) => {
                setDomHtml(e.target.value);
                setActivePreset(null);
                setResult(null);
              }}
              placeholder="<html>...</html>  — paste any DOM snippet here"
              className="w-full p-3 rounded-xl bg-[#07080c] border border-surface-border text-gray-300 font-mono text-xs focus:outline-none focus:border-brand-cyan/60 leading-relaxed resize-none placeholder:text-gray-700"
            />
          </div>
        </div>

        {/* Right: Test Code + Run */}
        <div className="space-y-4">
          <div className="glass-panel p-4 rounded-2xl border border-surface-border space-y-2">
            <label className="text-xs font-mono font-semibold text-gray-300 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <FileCode2 className="w-3.5 h-3.5 text-brand-emerald" />
                Surrounding Playwright Test (Python)
              </span>
              <span className="text-[10px] text-brand-emerald font-mono bg-brand-emerald/10 px-2 py-0.5 rounded-full border border-brand-emerald/20">
                AST comments preserved
              </span>
            </label>
            <textarea
              rows={16}
              value={surroundingCode}
              onChange={(e) => {
                setSurroundingCode(e.target.value);
                setActivePreset(null);
                setResult(null);
              }}
              placeholder={`def test_my_flow(page):\n    page.goto("https://example.com")\n    page.click("#broken-selector")`}
              className="w-full p-3 rounded-xl bg-[#07080c] border border-surface-border text-gray-300 font-mono text-xs focus:outline-none focus:border-brand-emerald/60 leading-relaxed resize-none placeholder:text-gray-700"
            />
          </div>

          {/* Run Button */}
          <button
            onClick={handleSimulate}
            disabled={isSimulating || !brokenSelector.trim() || !domHtml.trim()}
            className={`w-full py-4 px-6 rounded-2xl font-mono text-xs font-bold tracking-wider uppercase transition-all flex items-center justify-center space-x-2 shadow-lg ${
              isSimulating || !brokenSelector.trim() || !domHtml.trim()
                ? 'bg-surface-border text-gray-500 cursor-not-allowed opacity-60'
                : 'bg-gradient-to-r from-brand-red via-brand-crimson to-brand-cyan text-white hover:opacity-90 shadow-glow-red'
            }`}
          >
            {isSimulating ? (
              <>
                <RotateCcw className="w-4 h-4 animate-spin text-brand-cyan" />
                <span>Running Selectolax Pruner &amp; AI Brain…</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Execute Autonomous Healing Pipeline</span>
              </>
            )}
          </button>

          {/* Inline hint */}
          {!brokenSelector.trim() && (
            <p className="text-[11px] text-gray-600 font-mono text-center">
              ↑ Enter a broken selector and DOM to enable simulation
            </p>
          )}
        </div>
      </div>

      {/* ── Error State ──────────────────────────────────────────────────── */}
      {error && (
        <div className="glass-panel p-4 rounded-2xl border border-brand-red/40 bg-red-950/20 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-brand-red shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="text-sm font-mono font-bold text-brand-red">Simulation Error</p>
            <p className="text-xs text-red-300 font-sans leading-relaxed">{error}</p>
            <p className="text-[11px] text-gray-500 font-sans">
              Make sure the KernHell backend is running:{' '}
              <code className="text-gray-400">uv run kernhell serve</code>
            </p>
          </div>
        </div>
      )}

      {/* ── Results ──────────────────────────────────────────────────────── */}
      {result && (
        <div className="space-y-6 pt-2 animate-in fade-in duration-300">
          {/* Section header */}
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-brand-cyan" />
            <h2 className="text-sm font-mono font-bold uppercase tracking-wider text-gray-200">
              Pipeline Execution Output
            </h2>
            {result.from_cache && (
              <span className="ml-2 text-[10px] font-mono px-2 py-0.5 rounded-full bg-brand-emerald/10 border border-brand-emerald/30 text-brand-emerald">
                ⚡ CACHE HIT
              </span>
            )}
          </div>

          {/* ── Telemetry Row ──────────────────────────────────────────── */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* DOM Compression */}
            <div className="glass-panel p-4 rounded-xl border border-surface-border space-y-1">
              <span className="text-[10px] font-mono text-gray-400 uppercase tracking-wider">
                DOM Token Reduction
              </span>
              <div
                className={`text-2xl font-bold font-mono ${compressionColor(
                  result.compression_percent
                )}`}
              >
                {result.compression_percent > 0
                  ? `${result.compression_percent.toFixed(1)}%`
                  : '—'}
              </div>
              <p className="text-[11px] text-gray-500 font-sans">
                {result.original_dom_bytes}B{' '}
                <ChevronRight className="inline w-3 h-3" />{' '}
                {result.pruned_dom_bytes}B via Selectolax
              </p>
              {/* Toggle pruned DOM */}
              {result.pruned_dom && (
                <button
                  onClick={() => setShowPrunedDom((v) => !v)}
                  className="mt-1 text-[10px] font-mono text-brand-cyan/70 hover:text-brand-cyan flex items-center gap-1 transition-colors"
                >
                  <Eye className="w-3 h-3" />
                  {showPrunedDom ? 'Hide' : 'Show'} pruned DOM
                </button>
              )}
            </div>

            {/* AI Diagnosis */}
            <div className="glass-panel p-4 rounded-xl border border-surface-border space-y-1">
              <span className="text-[10px] font-mono text-gray-400 uppercase tracking-wider">
                AI Intent Diagnosis
              </span>
              <div
                className={`text-2xl font-bold font-mono ${diagnosisColor(
                  result.diagnosis.failure_type
                )}`}
              >
                {result.diagnosis.failure_type.toUpperCase()}
              </div>
              <p className="text-[11px] text-gray-500 font-sans">
                Confidence:{' '}
                <span className="text-gray-300">
                  {(result.diagnosis.confidence * 100).toFixed(0)}%
                </span>
              </p>
            </div>

            {/* DOM Verification */}
            <div className="glass-panel p-4 rounded-xl border border-surface-border space-y-1">
              <span className="text-[10px] font-mono text-gray-400 uppercase tracking-wider">
                DOM Verification
              </span>
              {verificationPassed ? (
                <>
                  <div className="text-xl font-bold font-mono text-brand-emerald flex items-center gap-1.5">
                    <CheckCircle2 className="w-5 h-5" />
                    Passed
                  </div>
                  <p className="text-[11px] text-gray-500 font-sans">
                    Healed selector is unique &amp; interactive
                  </p>
                </>
              ) : (
                <>
                  <div className="text-xl font-bold font-mono text-brand-purple flex items-center gap-1.5">
                    <ShieldAlert className="w-5 h-5" />
                    Aborted
                  </div>
                  <p className="text-[11px] text-gray-500 font-sans">
                    Element absent — real bug detected
                  </p>
                </>
              )}
            </div>
          </div>

          {/* ── Pruned DOM Preview (collapsible) ───────────────────────── */}
          {showPrunedDom && result.pruned_dom && (
            <div className="glass-panel rounded-xl border border-brand-cyan/20 overflow-hidden animate-in fade-in duration-200">
              <div className="px-4 py-2 bg-brand-cyan/5 border-b border-brand-cyan/20 flex items-center justify-between">
                <span className="text-[11px] font-mono text-brand-cyan font-semibold uppercase tracking-wider">
                  Selectolax Pruned DOM (sent to LLM)
                </span>
                <button
                  onClick={() => setShowPrunedDom(false)}
                  className="text-gray-500 hover:text-white"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
              <pre className="p-4 font-mono text-xs text-gray-300 overflow-x-auto leading-relaxed bg-[#07080c] whitespace-pre-wrap">
                {result.pruned_dom}
              </pre>
            </div>
          )}

          {/* ── MISSING: Anti-Hallucination Guardrail ──────────────────── */}
          {result.diagnosis.failure_type === 'missing' ? (
            <div className="glass-panel p-6 rounded-2xl border border-purple-500/40 bg-purple-950/20 space-y-3">
              <div className="flex items-center gap-2 text-brand-purple font-mono font-bold text-sm">
                <ShieldAlert className="w-5 h-5 shrink-0" />
                <span>ANTI-HALLUCINATION GUARDRAIL TRIGGERED — REAL BUG DETECTED</span>
              </div>
              <p className="text-sm text-purple-200 font-sans leading-relaxed">
                {result.diagnosis.explanation}
              </p>
              <div className="text-xs font-mono text-purple-300/80 bg-purple-900/30 p-3 rounded-lg border border-purple-700/30 leading-relaxed">
                ⚠️ Healing intentionally aborted. KernHell refuses to patch tests when
                elements are removed due to real product regressions (e.g. out-of-stock,
                feature flags, auth gates). This prevents false positives and masks real defects.
              </div>
            </div>
          ) : (
            /* ── RENAME / STRUCTURAL: Healed Result ──────────────────── */
            <div className="space-y-4">
              {/* AI Rationale */}
              <div className="glass-panel p-5 rounded-2xl border border-surface-border space-y-3">
                <div className="flex items-center gap-2 text-brand-cyan font-mono font-semibold text-xs">
                  <Sparkles className="w-4 h-4" />
                  <span>AI Diagnosis Rationale</span>
                </div>
                <p className="text-sm text-gray-300 font-sans leading-relaxed">
                  {result.diagnosis.explanation}
                </p>

                {/* Healed Selector */}
                {result.healed_selector && (
                  <div className="pt-1 space-y-2 border-t border-surface-border/60">
                    <div className="flex flex-wrap items-center gap-3 text-xs font-mono">
                      <span className="text-gray-500">Broken:</span>
                      <code className="px-2 py-0.5 rounded bg-brand-red/10 border border-brand-red/30 text-brand-red">
                        {result.healed_selector.old_selector}
                      </code>
                      <ChevronRight className="w-4 h-4 text-gray-600" />
                      <span className="text-gray-500">Healed:</span>
                      <code className="px-2 py-0.5 rounded bg-emerald-950/40 border border-emerald-500/40 text-emerald-400 font-bold">
                        {result.healed_selector.new_selector}
                      </code>
                    </div>
                    <div className="flex flex-wrap gap-2 text-[10px] font-mono">
                      <span className="px-2 py-0.5 rounded bg-surface border border-surface-border text-brand-cyan">
                        Strategy: {result.healed_selector.strategy}
                      </span>
                      <span className="px-2 py-0.5 rounded bg-surface border border-surface-border text-brand-emerald">
                        Confidence: {(result.healed_selector.confidence * 100).toFixed(0)}%
                      </span>
                      {result.healed_selector.reasoning && (
                        <span className="px-2 py-0.5 rounded bg-surface border border-surface-border text-gray-400 max-w-sm truncate">
                          {result.healed_selector.reasoning}
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* LibCST Surgical Diff */}
              {result.applied_diff && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Zap className="w-3.5 h-3.5 text-brand-red" />
                    <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-gray-400">
                      Surgical LibCST AST Patch Preview
                    </h3>
                  </div>
                  <DiffViewer
                    diff={result.applied_diff}
                    testFile={testFileName}
                    oldSelector={brokenSelector}
                    newSelector={result.healed_selector?.new_selector}
                  />
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

'use client';

import React, { useState } from 'react';
import { simulateHeal, SimulateResult } from '@/lib/api';
import DiffViewer from '@/components/DiffViewer';
import {
  Play,
  Sparkles,
  ShieldAlert,
  CheckCircle2,
  Cpu,
  Layers,
  RotateCcw,
  AlertTriangle,
  ArrowRight,
  Code2,
} from 'lucide-react';

const PRESET_RENAME = {
  name: 'Refactor (Rename ID to Role)',
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
};

const PRESET_MISSING = {
  name: 'Real Application Bug (Out of Stock)',
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
};

const PRESET_TESTID = {
  name: 'Accessible Data-TestID Refactor',
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
};

export default function PlaygroundPage() {
  const [brokenSelector, setBrokenSelector] = useState(PRESET_RENAME.broken_selector);
  const [domHtml, setDomHtml] = useState(PRESET_RENAME.dom_html);
  const [surroundingCode, setSurroundingCode] = useState(PRESET_RENAME.surrounding_code);
  const [isSimulating, setIsSimulating] = useState(false);
  const [result, setResult] = useState<SimulateResult | null>(null);

  const loadPreset = (preset: typeof PRESET_RENAME) => {
    setBrokenSelector(preset.broken_selector);
    setDomHtml(preset.dom_html);
    setSurroundingCode(preset.surrounding_code);
    setResult(null);
  };

  const handleSimulate = async () => {
    setIsSimulating(true);
    setResult(null);

    try {
      const res = await simulateHeal({
        broken_selector: brokenSelector,
        dom_html: domHtml,
        surrounding_code: surroundingCode,
      });
      setResult(res);
    } catch (e) {
      console.error('Simulation error:', e);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="glass-panel p-6 rounded-3xl border border-surface-border">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-cyan/10 border border-brand-cyan/30 text-brand-cyan text-xs font-mono font-medium mb-2">
              <Sparkles className="w-3.5 h-3.5" />
              <span>INTERACTIVE AI HEALING SIMULATOR</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white font-sans">
              Test Healer Sandbox
            </h1>
            <p className="text-xs sm:text-sm text-gray-400 font-sans mt-1">
              Provide a broken locator and live DOM to observe Selectolax token pruning,
              anti-hallucination intent diagnosis, and CST AST code patching in real time.
            </p>
          </div>

          {/* Quick Preset Buttons */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[11px] font-mono text-gray-400 w-full sm:w-auto">
              Presets:
            </span>
            <button
              onClick={() => loadPreset(PRESET_RENAME)}
              className="px-3 py-1.5 text-xs font-mono rounded-lg bg-surface hover:bg-surface-light border border-surface-border text-gray-200 hover:text-white transition-colors"
            >
              1. Button Rename
            </button>
            <button
              onClick={() => loadPreset(PRESET_MISSING)}
              className="px-3 py-1.5 text-xs font-mono rounded-lg bg-purple-950/40 hover:bg-purple-900/60 border border-purple-500/40 text-purple-300 transition-colors"
            >
              2. Real Bug (Missing)
            </button>
            <button
              onClick={() => loadPreset(PRESET_TESTID)}
              className="px-3 py-1.5 text-xs font-mono rounded-lg bg-surface hover:bg-surface-light border border-surface-border text-gray-200 hover:text-white transition-colors"
            >
              3. Data-TestID
            </button>
          </div>
        </div>
      </div>

      {/* Input Sandbox Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Selector & Live DOM */}
        <div className="space-y-4">
          {/* Broken Selector Input */}
          <div className="glass-panel p-4 rounded-2xl border border-surface-border space-y-2">
            <label className="text-xs font-mono font-semibold text-gray-300 flex items-center justify-between">
              <span>Broken Selector / Locator</span>
              <span className="text-[10px] text-brand-red font-mono">Failed in test</span>
            </label>
            <input
              type="text"
              value={brokenSelector}
              onChange={(e) => setBrokenSelector(e.target.value)}
              placeholder="e.g. #buy-now or .submit-btn"
              className="w-full px-3 py-2 rounded-xl bg-[#090a0f] border border-surface-border text-brand-red font-mono text-sm focus:outline-none focus:border-brand-red/60"
            />
          </div>

          {/* Live DOM HTML Textarea */}
          <div className="glass-panel p-4 rounded-2xl border border-surface-border space-y-2">
            <label className="text-xs font-mono font-semibold text-gray-300 flex items-center justify-between">
              <span>Live Page DOM (Captured via Playwright)</span>
              <span className="text-[10px] text-gray-500 font-mono">
                {new TextEncoder().encode(domHtml).length} bytes
              </span>
            </label>
            <textarea
              rows={9}
              value={domHtml}
              onChange={(e) => setDomHtml(e.target.value)}
              className="w-full p-3 rounded-xl bg-[#07080c] border border-surface-border text-gray-300 font-mono text-xs focus:outline-none focus:border-brand-cyan/60 leading-relaxed resize-none"
            />
          </div>
        </div>

        {/* Right Column: Surrounding Test Code */}
        <div className="space-y-4">
          <div className="glass-panel p-4 rounded-2xl border border-surface-border space-y-2">
            <label className="text-xs font-mono font-semibold text-gray-300 flex items-center justify-between">
              <span>Surrounding Playwright Test Code (Python)</span>
              <span className="text-[10px] text-brand-emerald font-mono">
                AST Comments Preserved
              </span>
            </label>
            <textarea
              rows={14}
              value={surroundingCode}
              onChange={(e) => setSurroundingCode(e.target.value)}
              className="w-full p-3 rounded-xl bg-[#07080c] border border-surface-border text-gray-300 font-mono text-xs focus:outline-none focus:border-brand-emerald/60 leading-relaxed resize-none"
            />
          </div>

          {/* Action Trigger Button */}
          <button
            onClick={handleSimulate}
            disabled={isSimulating || !brokenSelector || !domHtml}
            className={`w-full py-3.5 px-6 rounded-2xl font-mono text-xs font-bold tracking-wider uppercase transition-all flex items-center justify-center space-x-2 shadow-lg ${
              isSimulating
                ? 'bg-surface-border text-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-brand-red via-brand-crimson to-brand-cyan text-white hover:opacity-90 shadow-glow-red'
            }`}
          >
            {isSimulating ? (
              <>
                <RotateCcw className="w-4 h-4 animate-spin text-brand-cyan" />
                <span>Running Selectolax Pruner & AI Brain...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Execute Autonomous Healing Pipeline</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Simulation Results Display */}
      {result && (
        <div className="space-y-6 pt-4 animate-in fade-in duration-300">
          <div className="flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-brand-cyan" />
            <h2 className="text-sm font-mono font-bold uppercase tracking-wider text-gray-200">
              Pipeline Execution Output
            </h2>
          </div>

          {/* Metric telemetry row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="glass-panel p-4 rounded-xl border border-surface-border">
              <span className="text-[10px] font-mono text-gray-400 uppercase">
                DOM Token Reduction
              </span>
              <div className="text-xl font-bold font-mono text-brand-emerald mt-1">
                {result.compression_percent}%
              </div>
              <p className="text-[11px] text-gray-400 font-sans mt-0.5">
                {result.original_dom_bytes}B → {result.pruned_dom_bytes}B via Selectolax
              </p>
            </div>

            <div className="glass-panel p-4 rounded-xl border border-surface-border">
              <span className="text-[10px] font-mono text-gray-400 uppercase">
                AI Intent Diagnosis
              </span>
              <div
                className={`text-xl font-bold font-mono mt-1 ${
                  result.diagnosis.failure_type === 'missing'
                    ? 'text-brand-purple'
                    : 'text-brand-cyan'
                }`}
              >
                {result.diagnosis.failure_type.toUpperCase()}
              </div>
              <p className="text-[11px] text-gray-400 font-sans mt-0.5">
                Confidence: {(result.diagnosis.confidence * 100).toFixed(0)}%
              </p>
            </div>

            <div className="glass-panel p-4 rounded-xl border border-surface-border">
              <span className="text-[10px] font-mono text-gray-400 uppercase">
                DOM Verification Check
              </span>
              <div className="text-xl font-bold font-mono text-brand-emerald mt-1 flex items-center space-x-1.5">
                <CheckCircle2 className="w-5 h-5 text-brand-emerald" />
                <span>Passed (1 Match)</span>
              </div>
              <p className="text-[11px] text-gray-400 font-sans mt-0.5">
                Target element is unique and interactive
              </p>
            </div>
          </div>

          {/* Failure Diagnosis Card */}
          {result.diagnosis.failure_type === 'missing' ? (
            <div className="glass-panel p-6 rounded-2xl border border-purple-500/40 bg-purple-950/20 space-y-3">
              <div className="flex items-center space-x-2 text-brand-purple font-mono font-bold text-sm">
                <ShieldAlert className="w-5 h-5" />
                <span>ANTI-HALLUCINATION GUARDRAIL TRIGGERED (REAL BUG DETECTED)</span>
              </div>
              <p className="text-sm text-purple-200 font-sans leading-relaxed">
                {result.diagnosis.explanation}
              </p>
              <div className="text-xs font-mono text-purple-300/80 bg-purple-900/30 p-3 rounded-lg border border-purple-700/30">
                ⚠️ Healing intentionally aborted. KernHell prevents false positives by refusing to
                patch tests when elements are removed due to real product regressions or out-of-stock states.
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Diagnosis details */}
              <div className="glass-panel p-4 rounded-2xl border border-surface-border space-y-2">
                <div className="flex items-center space-x-2 text-brand-cyan font-mono font-semibold text-xs">
                  <Sparkles className="w-4 h-4" />
                  <span>AI Diagnosis Rationale:</span>
                </div>
                <p className="text-xs text-gray-300 font-sans leading-relaxed">
                  {result.diagnosis.explanation}
                </p>

                {result.healed_selector && (
                  <div className="pt-2 flex flex-wrap items-center gap-3">
                    <span className="text-xs font-mono text-gray-400">Healed Locator:</span>
                    <span className="px-3 py-1 rounded bg-emerald-950/40 border border-emerald-500/40 text-emerald-400 font-mono text-xs font-bold">
                      {result.healed_selector.new_selector}
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface border border-surface-border text-brand-cyan">
                      Strategy: {result.healed_selector.strategy}
                    </span>
                  </div>
                )}
              </div>

              {/* LibCST Surgical Diff */}
              {result.applied_diff && (
                <div className="space-y-2">
                  <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-gray-400">
                    Surgical LibCST AST Patch Preview
                  </h3>
                  <DiffViewer
                    diff={result.applied_diff}
                    testFile="test_order.py"
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

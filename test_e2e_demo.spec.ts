import { test, expect, Page, Locator } from '@playwright/test';

/**
 * Enterprise Billing Types & Interfaces
 */
export interface OrganizationSubscription {
  orgId: string;
  currentPlan: 'starter' | 'pro' | 'enterprise';
  billingCycle: 'monthly' | 'annual';
}

/**
 * Page Object Model (POM) for Enterprise Billing Dashboard
 */
export class BillingDashboardPage {
  readonly page: Page;
  readonly plansSection: Locator;
  readonly upgradeButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.plansSection = page.locator('section#subscription-tiers');

    // Intentionally broken selector (legacy CTA before redesign)
    this.upgradeButton = page.locator('[data-testid="complete-enterprise-upgrade-btn"]');
  }

  async selectEnterpriseTier(): Promise<void> {
    // Triggers enterprise plan upgrade
    await this.upgradeButton.click();
  }
}

test.describe('Enterprise SaaS Billing & Checkout E2E Suite', () => {
  test.beforeEach(async ({ page }) => {
    // Rich, realistic enterprise web page with Tailwind, SVGs, and refactored DOM
    await page.setContent(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Enterprise SaaS Billing & Subscriptions</title>
</head>
<body class="bg-slate-900 text-white font-sans">
  <div id="__app_root" class="min-h-screen flex flex-col justify-between">
    <header class="navbar flex items-center justify-between px-8 py-4 border-b border-slate-800 bg-slate-950/80 backdrop-blur">
      <div class="logo font-black text-xl text-indigo-400">CloudScale AI</div>
      <div class="user-badge flex items-center gap-2">
        <span class="user-name text-slate-300 font-medium">Enterprise Admin</span>
        <span class="status-indicator w-2 h-2 rounded-full bg-emerald-400"></span>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-12 flex-1 w-full">
      <div class="mb-10">
        <h1 class="text-4xl font-extrabold tracking-tight">Subscription & License Tiers</h1>
        <p class="text-slate-400 mt-2 text-lg">Scale autonomous compute clusters and AI test runners seamlessly.</p>
      </div>

      <!-- Subscription Tiers Grid -->
      <section id="subscription-tiers" class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Starter Tier -->
        <div class="tier-card p-8 rounded-2xl bg-slate-800/50 border border-slate-700/80 flex flex-col justify-between shadow-xl">
          <div>
            <h3 class="text-xl font-bold text-slate-200">Starter Dev</h3>
            <p class="text-slate-400 text-sm mt-1">For single developers exploring test automation</p>
            <p class="text-4xl font-black mt-6">$29 <span class="text-sm font-normal text-slate-400">/mo</span></p>
          </div>
          <button class="mt-8 w-full py-3 rounded-xl bg-slate-700 text-slate-300 font-medium hover:bg-slate-600">Downgrade</button>
        </div>

        <!-- Pro Tier -->
        <div class="tier-card p-8 rounded-2xl bg-slate-800/50 border border-slate-700/80 flex flex-col justify-between shadow-xl">
          <div>
            <h3 class="text-xl font-bold text-slate-200">Professional Team</h3>
            <p class="text-slate-400 text-sm mt-1">For growing agile teams with daily CI/CD</p>
            <p class="text-4xl font-black mt-6">$99 <span class="text-sm font-normal text-slate-400">/mo</span></p>
          </div>
          <button class="mt-8 w-full py-3 rounded-xl bg-slate-700 text-slate-300 font-medium cursor-not-allowed opacity-60">Current Plan</button>
        </div>

        <!-- Enterprise Tier (Refactored Target Button) -->
        <div class="tier-card p-8 rounded-2xl bg-gradient-to-b from-indigo-950/40 to-slate-900 border-2 border-indigo-500 flex flex-col justify-between shadow-2xl relative">
          <span class="absolute -top-3.5 right-6 px-3 py-1 rounded-full text-xs font-bold bg-indigo-500 text-white uppercase tracking-wider shadow-md">Recommended</span>
          <div>
            <h3 class="text-xl font-bold text-indigo-300">Enterprise Scale</h3>
            <p class="text-slate-400 text-sm mt-1">Unlimited self-healing test runs & dedicated VPC</p>
            <p class="text-4xl font-black mt-6 text-white">$499 <span class="text-sm font-normal text-slate-400">/mo</span></p>
          </div>

          <!-- The refactored button: old class replaced with modern data-testid & ID -->
          <button
            id="enterprise-upgrade-confirm-action"
            data-testid="complete-enterprise-upgrade-btn"
            class="mt-8 w-full py-3.5 px-6 rounded-xl font-bold text-white bg-indigo-600 hover:bg-indigo-500 shadow-lg shadow-indigo-500/30 flex items-center justify-center gap-2 transition"
          >
            <svg class="w-5 h-5 text-indigo-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            <span>Upgrade to Enterprise Scale</span>
          </button>
        </div>
      </section>

      <!-- Confirmation Banner -->
      <div id="upgrade-success-notification" class="hidden mt-10 p-6 rounded-2xl bg-emerald-950/40 border border-emerald-500 text-emerald-300 flex items-center gap-3">
        <svg class="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
        <span class="font-semibold text-lg">Organization upgraded to Enterprise Scale successfully!</span>
      </div>
    </main>
  </div>

  <script>
    document.getElementById('enterprise-upgrade-confirm-action').addEventListener('click', function() {
      document.getElementById('upgrade-success-notification').classList.remove('hidden');
    });
  </script>
</body>
</html>`);
  });

  test('should allow user to upgrade to enterprise tier via Page Object Model', async ({ page }) => {
    const dashboard = new BillingDashboardPage(page);

    // Call POM method to click the enterprise upgrade CTA
    await dashboard.selectEnterpriseTier();

    // Verify confirmation notification appears
    await expect(page.locator('#upgrade-success-notification')).toBeVisible({ timeout: 5000 });
  });
});

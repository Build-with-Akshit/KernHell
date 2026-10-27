"""Enterprise E2E Playwright Test Suite for AI Cluster Provisioning.

Demonstrates real-world Page Object Model (POM) architecture with:
- Multiple classes and inheritance (BasePage -> EnterpriseClusterPage)
- Strict type annotations (Page, Locator, str, dict)
- Inline comments, docstrings, and class constants
- Deeply structured enterprise HTML with Tailwind CSS & dynamic components
"""

from __future__ import annotations

from typing import Optional
from playwright.sync_api import Page, Locator, expect, sync_playwright


class BasePage:
    """Base class for all enterprise test automation page objects."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.nav_header = page.locator("header.enterprise-navbar")


class EnterpriseClusterPage(BasePage):
    """Page Object Model encapsulating the AI cluster checkout and provisioning flow."""

    DEFAULT_TIMEOUT_MS: int = 15000

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Form field locators
        self.org_name_input = page.locator("input#org-name")
        self.admin_email_input = page.locator("input#admin-email")
        self.cluster_tiers_section = page.locator("section#compute-tiers")

        # Intentionally broken selector (legacy CTA before redesign)
        self.confirm_deployment_button = page.locator('role=button[name="Confirm & Deploy Cluster"]')

    def fill_organization_credentials(self, org_name: str, email: str) -> None:
        """Populates organization details and admin email."""
        self.org_name_input.fill(org_name)
        self.admin_email_input.fill(email)

    def trigger_cluster_provisioning(self) -> None:
        """Executes the final confirmation action for cluster deployment."""
        # Action step targeting the broken selector
        self.confirm_deployment_button.click()


def test_enterprise_ai_cluster_checkout() -> None:
    """End-to-End test verifying autonomous provisioning of an 8x H100 cluster."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_default_timeout(5000)

        # Rich, modern, real-world enterprise DOM snapshot
        page.set_content('''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CloudScale AI - Enterprise Cluster Provisioning</title>
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen">
  <div id="root" class="max-w-6xl mx-auto px-6 py-12">
    <header class="enterprise-navbar flex items-center justify-between pb-6 border-b border-slate-800">
      <div class="flex items-center gap-3">
        <span class="text-2xl font-black text-indigo-400 tracking-tight">CloudScale AI</span>
        <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">Console v4.2</span>
      </div>
      <div class="flex items-center gap-4 text-sm text-slate-400">
        <span>Org: <strong class="text-white">DeepMind Labs</strong></span>
      </div>
    </header>

    <main class="mt-10">
      <div class="mb-8">
        <h1 class="text-3xl font-extrabold text-white">Deploy Dedicated GPU Compute Cluster</h1>
        <p class="text-slate-400 mt-2">Provision isolated bare-metal GPU nodes with low-latency InfiniBand interconnect.</p>
      </div>

      <!-- Credentials Form -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 bg-slate-900/60 p-8 rounded-2xl border border-slate-800 mb-8">
        <div>
          <label for="org-name" class="block text-sm font-semibold text-slate-300 mb-2">Organization Name</label>
          <input id="org-name" type="text" class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-700 text-white" value="DeepMind Labs" />
        </div>
        <div>
          <label for="admin-email" class="block text-sm font-semibold text-slate-300 mb-2">Technical Contact</label>
          <input id="admin-email" type="email" class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-700 text-white" value="admin@deepmind.com" />
        </div>
      </div>

      <!-- Compute Tiers -->
      <section id="compute-tiers" class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="p-6 rounded-2xl bg-slate-900/50 border border-slate-800">
          <h3 class="font-bold text-lg text-slate-200">1x A100 (80GB)</h3>
          <p class="text-slate-400 text-sm mt-1">Light fine-tuning & inference</p>
          <p class="text-2xl font-black text-white mt-4">$2,499 <span class="text-xs text-slate-400">/mo</span></p>
        </div>

        <div class="p-6 rounded-2xl bg-slate-900/50 border border-slate-800">
          <h3 class="font-bold text-lg text-slate-200">4x H100 SXM5</h3>
          <p class="text-slate-400 text-sm mt-1">Distributed pre-training</p>
          <p class="text-2xl font-black text-white mt-4">$8,999 <span class="text-xs text-slate-400">/mo</span></p>
        </div>

        <!-- Selected Tier with Refactored CTA Button -->
        <div class="p-6 rounded-2xl bg-gradient-to-b from-indigo-950/40 to-slate-900 border-2 border-indigo-500 relative">
          <span class="absolute -top-3 right-4 px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-500 text-white uppercase">Selected</span>
          <h3 class="font-bold text-lg text-indigo-300">8x H100 NVLink Cluster</h3>
          <p class="text-slate-400 text-sm mt-1">Full foundation model scale</p>
          <p class="text-2xl font-black text-white mt-4">$14,999 <span class="text-xs text-slate-400">/mo</span></p>

          <!-- Refactored Button: Old selector button.legacy-place-order-cta replaced with modern data-testid & ID -->
          <button
            id="confirm-cluster-provisioning-btn"
            data-testid="complete-enterprise-order-action"
            class="mt-6 w-full py-3.5 px-6 rounded-xl font-bold text-white bg-indigo-600 hover:bg-indigo-500 shadow-lg shadow-indigo-500/25 flex items-center justify-center gap-2 transition"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            <span>Confirm & Deploy Cluster</span>
          </button>
        </div>
      </section>

      <!-- Success Notification Card -->
      <div id="provisioning-success-card" class="hidden p-6 rounded-2xl bg-emerald-950/40 border border-emerald-500 text-emerald-300 flex items-center gap-3">
        <svg class="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
        <span class="font-bold text-lg">Cluster #H100-PROV-9421 successfully provisioned and ready for workload execution!</span>
      </div>
    </main>
  </div>

  <script>
    document.getElementById('confirm-cluster-provisioning-btn').addEventListener('click', function() {
      document.getElementById('provisioning-success-card').classList.remove('hidden');
    });
  </script>
</body>
</html>''')

        # Instantiate Page Object Model
        cluster_page = EnterpriseClusterPage(page)

        # Execute business logic steps
        cluster_page.fill_organization_credentials("DeepMind Labs", "admin@deepmind.com")
        cluster_page.trigger_cluster_provisioning()

        # Assertion
        expect(page.locator("#provisioning-success-card")).to_be_visible(timeout=5000)

        browser.close()

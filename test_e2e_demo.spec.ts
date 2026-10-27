import { test, expect, Page, Locator } from '@playwright/test';

/**
 * Enterprise Payment Types & Interfaces
 */
export interface PaymentDetails {
  cardHolder: string;
  cardNumber: string;
  expiry: string;
  cvv: string;
  amount: number;
}

/**
 * Page Object Model (POM) for Checkout & Payment Processing
 */
export class PaymentCheckoutPage {
  readonly page: Page;
  readonly cardHolderInput: Locator;
  readonly cardNumberInput: Locator;
  readonly expiryInput: Locator;
  readonly cvvInput: Locator;
  readonly payNowButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.cardHolderInput = page.locator('input#card-holder');
    this.cardNumberInput = page.locator('input#card-number');
    this.expiryInput = page.locator('input#card-expiry');
    this.cvvInput = page.locator('input#card-cvv');

    // Target button for checkout payment action
    // TIP: To test KernHell self-healing, intentionally change this to a broken selector like:
    // this.payNowButton = page.locator('button.old-pay-button');
    this.payNowButton = page.locator('[data-testid="complete-payment-button"]');
  }

  async fillPaymentForm(holder: string, cardNum: string): Promise<void> {
    await this.cardHolderInput.fill(holder);
    await this.cardNumberInput.fill(cardNum);
  }

  async submitPayment(): Promise<void> {
    // Triggers payment transaction
    await this.payNowButton.click();
  }
}

test.describe('Enterprise Payment & Checkout E2E Suite', () => {
  test.beforeEach(async ({ page }) => {
    // Realistic enterprise dark-mode payment gateway web page
    await page.setContent(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CloudScale AI - Secure Checkout & Payment</title>
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen">
  <div id="checkout-root" class="max-w-4xl mx-auto px-6 py-12">
    <!-- Navbar Header -->
    <header class="flex items-center justify-between pb-6 border-b border-slate-800">
      <div class="flex items-center gap-3">
        <span class="text-2xl font-black text-indigo-400 tracking-tight">CloudScale AI</span>
        <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">SSL 256-Bit Encrypted</span>
      </div>
      <div class="text-sm text-slate-400">
        Order ID: <strong class="text-white font-mono">#ORD-99214</strong>
      </div>
    </header>

    <main class="mt-10 grid grid-cols-1 md:grid-cols-3 gap-8">
      <!-- Order Summary Card -->
      <div class="md:col-span-1 bg-slate-900/60 p-6 rounded-2xl border border-slate-800 h-fit">
        <h3 class="text-lg font-bold text-white mb-4">Order Summary</h3>
        <div class="space-y-3 text-sm">
          <div class="flex justify-between text-slate-400">
            <span>AI Test Engine (Monthly)</span>
            <span class="text-slate-200 font-semibold">$49.00</span>
          </div>
          <div class="flex justify-between text-slate-400">
            <span>Cloud Cluster Runners</span>
            <span class="text-slate-200 font-semibold">$0.00</span>
          </div>
          <div class="flex justify-between text-slate-400">
            <span>Taxes & GST (18%)</span>
            <span class="text-slate-200 font-semibold">$8.82</span>
          </div>
          <div class="pt-3 border-t border-slate-800 flex justify-between text-base font-bold text-white">
            <span>Total Payable</span>
            <span class="text-indigo-400">$57.82</span>
          </div>
        </div>
      </div>

      <!-- Payment Form Container -->
      <div class="md:col-span-2 bg-slate-900/80 p-8 rounded-2xl border border-slate-800 shadow-xl">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-extrabold text-white">Payment Details</h2>
          <div class="flex gap-2 text-xs font-semibold text-slate-400">
            <span class="px-2 py-1 rounded bg-slate-800 border border-slate-700">Visa</span>
            <span class="px-2 py-1 rounded bg-slate-800 border border-slate-700">Mastercard</span>
            <span class="px-2 py-1 rounded bg-slate-800 border border-slate-700">UPI</span>
          </div>
        </div>

        <form id="payment-checkout-form" onsubmit="event.preventDefault();">
          <div class="space-y-5">
            <div>
              <label for="card-holder" class="block text-sm font-semibold text-slate-300 mb-1.5">Cardholder Name</label>
              <input
                id="card-holder"
                type="text"
                class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-700 text-white focus:outline-none focus:border-indigo-500 font-medium"
                value="Ritesh Kumar"
              />
            </div>

            <div>
              <label for="card-number" class="block text-sm font-semibold text-slate-300 mb-1.5">Card Number</label>
              <input
                id="card-number"
                type="text"
                class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-700 text-white focus:outline-none focus:border-indigo-500 font-mono tracking-wider"
                value="4242 4242 4242 4242"
              />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label for="card-expiry" class="block text-sm font-semibold text-slate-300 mb-1.5">Valid Thru (MM/YY)</label>
                <input
                  id="card-expiry"
                  type="text"
                  class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-700 text-white focus:outline-none focus:border-indigo-500 font-mono"
                  value="12/28"
                />
              </div>
              <div>
                <label for="card-cvv" class="block text-sm font-semibold text-slate-300 mb-1.5">CVV / CVC</label>
                <input
                  id="card-cvv"
                  type="password"
                  maxlength="4"
                  class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-700 text-white focus:outline-none focus:border-indigo-500 font-mono"
                  value="888"
                />
              </div>
            </div>

            <!-- Target Pay Now Action Button -->
            <button
              id="pay-now-action-btn"
              data-testid="complete-payment-button"
              class="w-full mt-4 py-4 px-6 rounded-xl font-bold text-white bg-emerald-600 hover:bg-emerald-500 shadow-lg shadow-emerald-500/25 flex items-center justify-center gap-2 transition cursor-pointer"
            >
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
              <span>Pay $57.82 Now</span>
            </button>
          </div>
        </form>

        <!-- Payment Success Card -->
        <div id="payment-success-card" class="hidden mt-6 p-5 rounded-2xl bg-emerald-950/60 border border-emerald-500 text-emerald-300 flex items-center gap-4 shadow-xl">
          <svg class="w-6 h-6 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
          <div>
            <h4 class="font-bold text-base text-white">Payment Received Successfully!</h4>
            <p class="text-xs text-emerald-400 mt-0.5">Transaction ID: #TXN-9842109 • Order activated.</p>
          </div>
        </div>
      </div>
    </main>
  </div>

  <script>
    document.getElementById('pay-now-action-btn').addEventListener('click', function() {
      document.getElementById('payment-success-card').classList.remove('hidden');
    });
  </script>
</body>
</html>`);
  });

  test('should fill payment details and complete checkout successfully', async ({ page }) => {
    const checkoutPage = new PaymentCheckoutPage(page);

    // 1. Fill card details
    await checkoutPage.fillPaymentForm('Ritesh Kumar', '4242 4242 4242 4242');

    // 2. Submit payment transaction
    await checkoutPage.submitPayment();

    // 3. Verify confirmation notification appears
    await expect(page.locator('#payment-success-card')).toBeVisible({ timeout: 5000 });
  });
});

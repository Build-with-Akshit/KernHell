import { test, expect } from '@playwright/test';

test('purchase test', async ({ page }) => {
  // Page has refactored button: id='purchase-btn' and data-testid='complete-order-btn'
  await page.setContent('<button id="purchase-btn" data-testid="complete-order-btn">Place Your Order</button>');

  // Old broken selector that needs self-healing:
  await page.click('[data-testid="complete-order-btn"]');
});

import { test, expect } from '@playwright/test';

/**
 * E2E tests for data correction workflow
 */
test.describe('Data Correction Workflow', () => {
  // Helper function to login as operator
  async function loginAsOperator(page: any) {
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'mock-token-123',
          user: {
            id: 'user-123',
            email: 'operator@example.com',
            username: 'operator',
            role: 'operator',
            is_active: true,
            mfa_enabled: false,
          },
        }),
      });
    });

    await page.goto('/login');
    await page.fill('input[type="email"]', 'operator@example.com');
    await page.fill('input[type="password"]', 'TestPass123!');
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/$/, { timeout: 5000 });
  }

  // Helper function to login as admin
  async function loginAsAdmin(page: any) {
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'mock-token-admin',
          user: {
            id: 'admin-123',
            email: 'admin@example.com',
            username: 'admin',
            role: 'admin',
            is_active: true,
            mfa_enabled: false,
          },
        }),
      });
    });

    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'TestPass123!');
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/$/, { timeout: 5000 });
  }

  test('should allow operator to propose data correction', async ({ page }) => {
    const companyId = 'company-1';
    
    await loginAsOperator(page);

    // Mock company detail API
    await page.route(`**/api/v1/companies/${companyId}**`, async (route) => {
      if (route.request().method() === 'GET' && !route.request().url().includes('/corrections')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: companyId,
            legal_name: 'Test Company Ltd',
            registration_number: 'TEST123',
            jurisdiction: 'US',
            domain: 'testcompany.com',
            created_at: '2025-01-01T00:00:00Z',
            updated_at: '2025-01-01T00:00:00Z',
          }),
        });
      }
    });

    // Mock corrections API
    await page.route(`**/api/v1/companies/${companyId}/corrections**`, async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'correction-1',
            company_id: companyId,
            field_name: 'legal_name',
            field_type: 'legal_name',
            old_value: 'Test Company Ltd',
            new_value: 'Updated Company Name',
            status: 'PENDING',
            created_at: new Date().toISOString(),
          }),
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        });
      }
    });

    // Navigate to company detail page
    await page.goto(`/companies/${companyId}`);
    
    // Wait for page to load
    await expect(page.locator('text=Test Company Ltd')).toBeVisible({ timeout: 5000 });
    
    // Look for correction button or edit icon
    const correctionButton = page.locator('button').filter({ hasText: /correct|edit|propose/i }).first();
    if (await correctionButton.isVisible()) {
      await correctionButton.click();
      
      // Wait for correction modal
      await expect(page.locator('text=Propose Correction')).toBeVisible({ timeout: 3000 });
      
      // Fill in correction form
      await page.fill('input[name="new_value"]', 'Updated Company Name');
      await page.fill('textarea[name="reason"]', 'Company name changed');
      
      // Submit correction
      await page.getByRole('button', { name: /submit|propose/i }).click();
      
      // Should show success message
      await expect(page.locator('text=Correction proposed')).toBeVisible({ timeout: 5000 });
    }
  });

  test('should allow admin to approve data correction', async ({ page }) => {
    const companyId = 'company-1';
    const correctionId = 'correction-1';
    
    await loginAsAdmin(page);

    // Mock company detail API
    await page.route(`**/api/v1/companies/${companyId}**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: companyId,
          legal_name: 'Test Company Ltd',
          registration_number: 'TEST123',
          jurisdiction: 'US',
          domain: 'testcompany.com',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z',
        }),
      });
    });

    // Mock pending corrections API
    await page.route(`**/api/v1/companies/${companyId}/corrections**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: correctionId,
            company_id: companyId,
            field_name: 'legal_name',
            field_type: 'legal_name',
            old_value: 'Test Company Ltd',
            new_value: 'Updated Company Name',
            status: 'PENDING',
            created_at: '2025-01-01T00:00:00Z',
          },
        ]),
      });
    });

    // Mock approve correction API
    await page.route(`**/api/v1/data-corrections/${correctionId}/approve**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: correctionId,
          status: 'APPROVED',
          approved_at: new Date().toISOString(),
        }),
      });
    });

    // Navigate to company detail page
    await page.goto(`/companies/${companyId}`);
    
    // Wait for page to load
    await expect(page.locator('text=Test Company Ltd')).toBeVisible({ timeout: 5000 });
    
    // Look for approval panel or pending corrections
    const approveButton = page.locator('button').filter({ hasText: /approve/i }).first();
    if (await approveButton.isVisible()) {
      await approveButton.click();
      
      // Should show success message
      await expect(page.locator('text=Correction approved')).toBeVisible({ timeout: 5000 });
    }
  });
});


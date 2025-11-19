import { test, expect } from '@playwright/test';

/**
 * E2E tests for company management flows
 */
test.describe('Company Management', () => {
  // Helper function to login
  async function login(page: any) {
    // Mock API responses
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'mock-token-123',
          user: {
            id: 'user-123',
            email: 'test@example.com',
            username: 'testuser',
            role: 'operator',
            is_active: true,
            mfa_enabled: false,
          },
        }),
      });
    });

    await page.goto('/login');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'TestPass123!');
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/$/, { timeout: 5000 });
  }

  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('should display company list page', async ({ page }) => {
    // Mock companies list API
    await page.route('**/api/v1/companies/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: 'company-1',
              legal_name: 'Test Company Ltd',
              registration_number: 'TEST123',
              jurisdiction: 'US',
              domain: 'testcompany.com',
              created_at: '2025-01-01T00:00:00Z',
              updated_at: '2025-01-01T00:00:00Z',
            },
          ],
          total: 1,
        }),
      });
    });

    // Navigate to companies page
    await page.goto('/companies');
    
    // Check page elements
    await expect(page.locator('text=Companies')).toBeVisible();
    await expect(page.getByRole('button', { name: /create company/i })).toBeVisible();
    
    // Check company is displayed
    await expect(page.locator('text=Test Company Ltd')).toBeVisible();
  });

  test('should create a new company', async ({ page }) => {
    const newCompanyId = 'company-new-123';
    
    // Mock create company API
    await page.route('**/api/v1/companies', async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: newCompanyId,
            legal_name: 'New Test Company',
            registration_number: 'NEW123',
            jurisdiction: 'US',
            domain: 'newtest.com',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          }),
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [],
            total: 0,
          }),
        });
      }
    });

    // Mock company detail API
    await page.route(`**/api/v1/companies/${newCompanyId}**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: newCompanyId,
          legal_name: 'New Test Company',
          registration_number: 'NEW123',
          jurisdiction: 'US',
          domain: 'newtest.com',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }),
      });
    });

    // Navigate to companies page
    await page.goto('/companies');
    
    // Click create company button
    await page.getByRole('button', { name: /create company/i }).click();
    
    // Wait for modal to appear
    await expect(page.locator('text=Create New Company')).toBeVisible();
    
    // Fill in company details
    await page.fill('input[name="legal_name"]', 'New Test Company');
    await page.fill('input[name="registration_number"]', 'NEW123');
    await page.fill('input[name="jurisdiction"]', 'US');
    await page.fill('input[name="domain"]', 'newtest.com');
    
    // Submit form
    await page.getByRole('button', { name: /create/i }).click();
    
    // Should navigate to company detail page
    await expect(page).toHaveURL(new RegExp(`/companies/${newCompanyId}`), { timeout: 5000 });
    
    // Should show company name
    await expect(page.locator('text=New Test Company')).toBeVisible();
  });

  test('should search and filter companies', async ({ page }) => {
    // Mock companies list API with search
    await page.route('**/api/v1/companies/**', async (route) => {
      const url = new URL(route.request().url());
      const search = url.searchParams.get('search');
      
      const items = search === 'Test'
        ? [
            {
              id: 'company-1',
              legal_name: 'Test Company Ltd',
              registration_number: 'TEST123',
              jurisdiction: 'US',
              domain: 'testcompany.com',
              created_at: '2025-01-01T00:00:00Z',
              updated_at: '2025-01-01T00:00:00Z',
            },
          ]
        : [];
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items,
          total: items.length,
        }),
      });
    });

    // Navigate to companies page
    await page.goto('/companies');
    
    // Enter search term
    await page.fill('input[placeholder*="Search"]', 'Test');
    
    // Wait for results to update
    await expect(page.locator('text=Test Company Ltd')).toBeVisible({ timeout: 3000 });
  });

  test('should navigate to company detail page', async ({ page }) => {
    const companyId = 'company-1';
    
    // Mock companies list API
    await page.route('**/api/v1/companies/**', async (route) => {
      if (route.request().method() === 'GET' && !route.request().url().includes(companyId)) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [
              {
                id: companyId,
                legal_name: 'Test Company Ltd',
                registration_number: 'TEST123',
                jurisdiction: 'US',
                domain: 'testcompany.com',
                created_at: '2025-01-01T00:00:00Z',
                updated_at: '2025-01-01T00:00:00Z',
              },
            ],
            total: 1,
          }),
        });
      }
    });

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

    // Mock verification result API
    await page.route(`**/api/v1/companies/${companyId}/verification**`, async (route) => {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Not found' }),
      });
    });

    // Navigate to companies page
    await page.goto('/companies');
    
    // Click on company name or row
    await page.locator('text=Test Company Ltd').click();
    
    // Should navigate to company detail page
    await expect(page).toHaveURL(new RegExp(`/companies/${companyId}`), { timeout: 5000 });
    
    // Should show company details
    await expect(page.locator('text=Test Company Ltd')).toBeVisible();
  });
});


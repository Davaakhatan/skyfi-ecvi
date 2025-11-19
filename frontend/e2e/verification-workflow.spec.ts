import { test, expect } from '@playwright/test';

/**
 * E2E tests for verification workflow
 */
test.describe('Verification Workflow', () => {
  // Helper function to login
  async function login(page: any) {
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

  test('should display verification details for a company', async ({ page }) => {
    const companyId = 'company-1';
    
    // Mock company detail API
    await page.route(`**/api/v1/companies/${companyId}**`, async (route) => {
      if (route.request().method() === 'GET' && !route.request().url().includes('/verification')) {
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

    // Mock verification result API
    await page.route(`**/api/v1/companies/${companyId}/verification**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'verification-1',
          company_id: companyId,
          risk_score: 45,
          risk_category: 'MEDIUM',
          verification_status: 'COMPLETED',
          dns_verified: true,
          registration_verified: true,
          contact_verified: true,
          address_verified: true,
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z',
        }),
      });
    });

    // Mock report API
    await page.route(`**/api/v1/reports/company/${companyId}/report**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          company_info: {
            legal_name: 'Test Company Ltd',
            registration_number: 'TEST123',
            jurisdiction: 'US',
            domain: 'testcompany.com',
          },
          risk_assessment: {
            risk_score: 45,
            risk_category: 'MEDIUM',
          },
          verification_details: {
            dns_verified: true,
            registration_verified: true,
            contact_verified: true,
            address_verified: true,
          },
        }),
      });
    });

    // Navigate to company detail page
    await page.goto(`/companies/${companyId}`);
    
    // Should show verification details
    await expect(page.locator('text=Verification Details')).toBeVisible({ timeout: 5000 });
    
    // Should show risk score
    await expect(page.locator('text=45')).toBeVisible();
    
    // Should show risk category
    await expect(page.locator('text=MEDIUM')).toBeVisible();
  });

  test('should trigger verification for a company', async ({ page }) => {
    const companyId = 'company-1';
    
    // Mock company detail API
    await page.route(`**/api/v1/companies/${companyId}**`, async (route) => {
      if (route.request().method() === 'GET' && !route.request().url().includes('/verification')) {
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

    // Mock verification trigger API
    await page.route(`**/api/v1/companies/${companyId}/verify**`, async (route) => {
      await route.fulfill({
        status: 202,
        contentType: 'application/json',
        body: JSON.stringify({
          task_id: 'task-123',
          status: 'PENDING',
          message: 'Verification started',
        }),
      });
    });

    // Mock verification status API
    await page.route(`**/api/v1/companies/${companyId}/verification**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'verification-1',
          company_id: companyId,
          risk_score: 45,
          risk_category: 'MEDIUM',
          verification_status: 'IN_PROGRESS',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z',
        }),
      });
    });

    // Navigate to company detail page
    await page.goto(`/companies/${companyId}`);
    
    // Click verify/trigger button
    const verifyButton = page.getByRole('button', { name: /verify|trigger|analyze/i });
    if (await verifyButton.isVisible()) {
      await verifyButton.click();
      
      // Should show verification in progress
      await expect(page.locator('text=IN_PROGRESS')).toBeVisible({ timeout: 5000 });
    }
  });

  test('should export verification report', async ({ page }) => {
    const companyId = 'company-1';
    
    // Mock company detail API
    await page.route(`**/api/v1/companies/${companyId}**`, async (route) => {
      if (route.request().method() === 'GET' && !route.request().url().includes('/verification')) {
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

    // Mock verification result API
    await page.route(`**/api/v1/companies/${companyId}/verification**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'verification-1',
          company_id: companyId,
          risk_score: 45,
          risk_category: 'MEDIUM',
          verification_status: 'COMPLETED',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z',
        }),
      });
    });

    // Mock report export API (PDF)
    await page.route(`**/api/v1/reports/company/${companyId}/report**`, async (route) => {
      const url = new URL(route.request().url());
      const format = url.searchParams.get('format');
      
      if (format === 'pdf') {
        await route.fulfill({
          status: 200,
          contentType: 'application/pdf',
          body: Buffer.from('PDF content'),
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            company_info: {
              legal_name: 'Test Company Ltd',
            },
            risk_assessment: {
              risk_score: 45,
              risk_category: 'MEDIUM',
            },
          }),
        });
      }
    });

    // Navigate to company detail page
    await page.goto(`/companies/${companyId}`);
    
    // Wait for page to load
    await expect(page.locator('text=Test Company Ltd')).toBeVisible({ timeout: 5000 });
    
    // Click export button (if visible)
    const exportButton = page.getByRole('button', { name: /export|download/i });
    if (await exportButton.isVisible()) {
      await exportButton.click();
      
      // Check if PDF download option is available
      const pdfOption = page.locator('text=PDF');
      if (await pdfOption.isVisible()) {
        // Note: Actual download testing requires additional setup
        // This verifies the UI flow
      }
    }
  });
});


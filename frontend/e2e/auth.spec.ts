import { test, expect } from '@playwright/test';

/**
 * E2E tests for authentication flows
 */
test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
  });

  test('should display login page correctly', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/ECVI/);
    
    // Check login form elements
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    // Fill in invalid credentials
    await page.fill('input[type="email"]', 'invalid@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    
    // Submit form
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Wait for error message
    await expect(page.locator('text=Invalid email or password')).toBeVisible({ timeout: 5000 });
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    // Mock API response for successful login
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

    // Mock companies list API
    await page.route('**/api/v1/companies/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0,
        }),
      });
    });

    // Fill in valid credentials
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'TestPass123!');
    
    // Submit form
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/\/$/, { timeout: 5000 });
    
    // Should show dashboard content
    await expect(page.locator('text=Dashboard')).toBeVisible();
  });

  test('should redirect to login when not authenticated', async ({ page }) => {
    // Try to access protected route
    await page.goto('/companies');
    
    // Should redirect to login
    await expect(page).toHaveURL(/\/login/);
  });
});


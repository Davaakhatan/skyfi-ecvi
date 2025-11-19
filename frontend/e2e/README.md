# E2E Testing with Playwright

This directory contains end-to-end (E2E) tests for the ECVI frontend application using Playwright.

## Overview

E2E tests verify critical user flows from a user's perspective, ensuring that the entire application works correctly from login to data verification and report generation.

## Test Structure

```
e2e/
├── auth.spec.ts              # Authentication flows (login, logout, session)
├── company-management.spec.ts # Company CRUD operations
├── verification-workflow.spec.ts # Verification process and reports
└── data-correction.spec.ts   # Data correction workflow
```

## Running Tests

### Run all E2E tests
```bash
npm run test:e2e
```

### Run tests in UI mode (interactive)
```bash
npm run test:e2e:ui
```

### Run tests in headed mode (see browser)
```bash
npm run test:e2e:headed
```

### Run tests in debug mode
```bash
npm run test:e2e:debug
```

### Run specific test file
```bash
npx playwright test e2e/auth.spec.ts
```

### Run tests in specific browser
```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

## Prerequisites

1. **Backend server must be running** on `http://localhost:8000`
2. **Frontend dev server** will be started automatically by Playwright (configured in `playwright.config.ts`)
3. **Test database** should be set up with test fixtures

## Test Environment Setup

### Backend Setup
```bash
cd backend
# Set up test database
export DATABASE_URL=postgresql://test_user:test_password@localhost:5432/test_db
alembic upgrade head

# Create test users (if needed)
python scripts/create_test_users.py
```

### Frontend Setup
```bash
cd frontend
npm install
```

## Writing New Tests

### Basic Test Structure
```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup before each test
    await page.goto('/login');
  });

  test('should do something', async ({ page }) => {
    // Test implementation
    await expect(page.locator('text=Expected Text')).toBeVisible();
  });
});
```

### Mocking API Responses
```typescript
// Mock API response
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
```

### Helper Functions
Create reusable helper functions for common operations:

```typescript
async function login(page: any, email: string, password: string) {
  await page.goto('/login');
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);
  await page.getByRole('button', { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/$/, { timeout: 5000 });
}
```

## Test Coverage

### Critical User Flows Covered

1. **Authentication**
   - Login with valid credentials
   - Login with invalid credentials
   - Session management
   - Protected route access

2. **Company Management**
   - View company list
   - Create new company
   - Search and filter companies
   - Navigate to company details

3. **Verification Workflow**
   - View verification details
   - Trigger verification
   - Monitor verification status
   - Export verification reports

4. **Data Correction**
   - Propose data correction (operator)
   - Approve data correction (admin)
   - View correction history

## Best Practices

1. **Use descriptive test names** that explain what is being tested
2. **Mock API responses** to avoid dependencies on external services
3. **Use page object pattern** for complex pages (optional)
4. **Keep tests independent** - each test should be able to run alone
5. **Clean up after tests** - reset state if needed
6. **Use appropriate wait strategies** - prefer `toBeVisible()` over `waitFor()`
7. **Test user-visible behavior** - focus on what users see and do

## Debugging Failed Tests

1. **Run tests in headed mode** to see what's happening:
   ```bash
   npm run test:e2e:headed
   ```

2. **Use debug mode** to step through tests:
   ```bash
   npm run test:e2e:debug
   ```

3. **Check test artifacts**:
   - Screenshots: `test-results/`
   - Videos: `test-results/`
   - Traces: `test-results/`

4. **View HTML report**:
   ```bash
   npx playwright show-report
   ```

## CI/CD Integration

E2E tests are configured to run in CI/CD pipelines. The tests will:
- Start the frontend dev server automatically
- Run tests against the running application
- Generate test reports and artifacts
- Continue on error (to not block deployments)

## Troubleshooting

### Tests fail with "Navigation timeout"
- Ensure backend server is running on port 8000
- Check that frontend dev server can start
- Verify network connectivity

### Tests fail with "Element not found"
- Check if selectors are correct
- Verify that elements are visible (not hidden)
- Add appropriate waits for dynamic content

### Tests are flaky
- Add explicit waits instead of fixed timeouts
- Ensure test data is properly set up
- Check for race conditions in async operations

## Resources

- [Playwright Documentation](https://playwright.dev/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright API Reference](https://playwright.dev/docs/api/class-test)


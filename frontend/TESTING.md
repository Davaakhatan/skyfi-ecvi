# Frontend Testing Guide

## Overview

The ECVI frontend uses a comprehensive testing strategy with both unit tests (Vitest) and end-to-end tests (Playwright). Tests can run with or without a live backend server.

## Test Types

### 1. Unit Tests (Vitest)

Unit tests run in isolation with mocked API calls. They test individual components, utilities, and stores.

**Location:** `src/**/__tests__/*.test.tsx` and `src/**/__tests__/*.test.ts`

**Run:**
```bash
npm run test          # Watch mode
npm run test:unit     # Run once
npm run test:ui       # UI mode
npm run test:coverage # With coverage
```

### 2. E2E Tests (Playwright)

End-to-end tests run against a real backend and frontend. They test complete user workflows.

**Location:** `e2e/*.spec.ts`

**Run:**
```bash
npm run test:e2e          # Run all E2E tests
npm run test:e2e:ui       # UI mode
npm run test:e2e:headed   # Headed browser
npm run test:e2e:debug    # Debug mode
```

### 3. All Tests

Run both unit and E2E tests:

```bash
npm run test:all
# Or use the comprehensive script:
bash scripts/run-tests.sh
```

## Test Setup with Backend

### Automatic Setup (Recommended)

Playwright automatically starts the backend and frontend servers when running E2E tests:

```bash
npm run test:e2e
```

The `playwright.config.ts` uses `webServer` to:
1. Start backend server via `scripts/test-setup.sh`
2. Start frontend dev server
3. Wait for both to be ready
4. Run tests
5. Clean up automatically

### Manual Setup

If you need to run tests manually:

```bash
# Terminal 1: Start backend
cd frontend
npm run test:setup

# Terminal 2: Start frontend
npm run dev

# Terminal 3: Run tests
npm run test:e2e

# Cleanup
npm run test:teardown
```

## Test Scripts

### Available Scripts

- `npm run test` - Run unit tests in watch mode
- `npm run test:unit` - Run unit tests once
- `npm run test:ui` - Run unit tests with UI
- `npm run test:coverage` - Run unit tests with coverage
- `npm run test:e2e` - Run E2E tests (auto-starts backend/frontend)
- `npm run test:e2e:ui` - Run E2E tests with UI
- `npm run test:e2e:headed` - Run E2E tests in headed browser
- `npm run test:e2e:debug` - Run E2E tests in debug mode
- `npm run test:all` - Run all tests (unit + E2E)
- `npm run test:setup` - Manually start backend for testing
- `npm run test:teardown` - Manually stop backend

### Comprehensive Test Runner

Use the comprehensive test runner for more control:

```bash
bash scripts/run-tests.sh [options]
```

**Options:**
- `--unit-only` - Run only unit tests
- `--e2e-only` - Run only E2E tests
- `--coverage` - Include coverage report
- `--watch` - Watch mode for unit tests

**Examples:**
```bash
# Run all tests
bash scripts/run-tests.sh

# Run only unit tests with coverage
bash scripts/run-tests.sh --unit-only --coverage

# Run only E2E tests
bash scripts/run-tests.sh --e2e-only
```

## API Mocking

### For Unit Tests

Use the API mocking utilities in `src/test/api-mocks.ts`:

```typescript
import { mockApiEndpoints, setupApiMocks } from '@/test/api-mocks';
import api from '@/services/api';

// Setup mocks
const axiosMock = createMockAxios();
setupApiMocks(axiosMock);

// Use in tests
vi.mock('@/services/api', () => ({
  default: axiosMock,
}));
```

### For E2E Tests

E2E tests use Playwright's route interception:

```typescript
await page.route('**/api/v1/auth/login', async (route) => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ access_token: 'token' }),
  });
});
```

Or use the real backend (recommended for E2E).

## Test Configuration

### Vitest Configuration

Located in `vite.config.ts`:

- Environment: `jsdom` (browser-like environment)
- Setup file: `src/test/setup.ts`
- Coverage provider: `v8`

### Playwright Configuration

Located in `playwright.config.ts`:

- Base URL: `http://localhost:5173`
- API URL: `http://localhost:8000`
- Browsers: Chromium, Firefox, WebKit
- Auto-starts backend and frontend servers

## Writing Tests

### Unit Test Example

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import MyComponent from './MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

### E2E Test Example

```typescript
import { test, expect } from '@playwright/test';

test('user can login', async ({ page }) => {
  await page.goto('/login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'password');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/dashboard');
});
```

## CI/CD Integration

Tests run automatically in GitHub Actions:

1. **Unit Tests** - Run in parallel, no backend needed
2. **E2E Tests** - Run with backend and frontend servers
3. **Coverage** - Uploaded to Codecov

See `.github/workflows/ci.yml` for details.

## Troubleshooting

### Backend Not Starting

- Check Python version (3.11+)
- Verify dependencies installed: `pip install -e ".[dev]"`
- Check backend logs: `/tmp/backend.log`
- Ensure port 8000 is available

### Frontend Not Starting

- Check Node.js version (20+)
- Install dependencies: `npm ci`
- Ensure port 5173 is available

### Tests Failing

- Check test output for specific errors
- Run tests individually to isolate issues
- Use `--debug` flag for E2E tests
- Check browser console for errors

### Port Conflicts

If ports are in use:

```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:5173 | xargs kill -9  # Frontend
```

## Best Practices

1. **Unit Tests**: Mock external dependencies (API, localStorage, etc.)
2. **E2E Tests**: Use real backend when possible
3. **Test Isolation**: Each test should be independent
4. **Cleanup**: Always cleanup after tests
5. **Descriptive Names**: Use clear test descriptions
6. **Arrange-Act-Assert**: Follow AAA pattern

## Coverage Goals

- **Unit Tests**: > 80% coverage
- **E2E Tests**: Cover critical user flows
- **Components**: Test all user interactions
- **Utilities**: 100% coverage

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Library](https://testing-library.com/)
- [API Mocking Guide](src/test/api-mocks.ts)


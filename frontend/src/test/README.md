# Frontend Tests

This directory contains all frontend test files for the ECVI project.

## Test Structure

- `setup.ts` - Vitest configuration and setup
- `utils/test-utils.tsx` - Custom render function with providers
- `__tests__/` - Test files organized by component/module

## Running Tests

### Run all tests
```bash
cd frontend
npm test
```

### Run in watch mode
```bash
npm test -- --watch
```

### Run with UI
```bash
npm run test:ui
```

### Run with coverage
```bash
npm run test:coverage
```

## Test Files

### Component Tests
- `components/__tests__/RiskScoreBadge.test.tsx` - Risk score badge component tests
- `components/__tests__/VerificationIndicator.test.tsx` - Verification indicator component tests

### Store Tests
- `store/__tests__/authStore.test.ts` - Authentication store tests
- `store/__tests__/notificationStore.test.ts` - Notification store tests

### Utility Tests
- `utils/__tests__/validators.test.ts` - Validation utility tests

## Writing New Tests

1. Create test files next to the component/module being tested
2. Use the custom `render` function from `test/utils/test-utils.tsx` for components
3. Use descriptive test descriptions
4. Follow the existing test patterns
5. Mock external dependencies (API calls, etc.)

## Test Utilities

- `render` - Custom render function that includes React Router and other providers
- `screen` - Testing Library screen queries
- `userEvent` - User interaction simulation


/**
 * API mocking utilities for frontend tests
 * Use these helpers to mock API responses in unit tests
 */

import { vi } from 'vitest';

export interface MockApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
}

/**
 * Create a mock API response
 */
export function createMockResponse<T>(
  data: T,
  status: number = 200,
  statusText: string = 'OK'
): MockApiResponse<T> {
  return {
    data,
    status,
    statusText,
  };
}

/**
 * Mock axios instance for testing
 */
export function createMockAxios() {
  const mockGet = vi.fn();
  const mockPost = vi.fn();
  const mockPut = vi.fn();
  const mockDelete = vi.fn();
  const mockPatch = vi.fn();

  return {
    get: mockGet,
    post: mockPost,
    put: mockPut,
    delete: mockDelete,
    patch: mockPatch,
    defaults: {
      headers: {
        common: {},
      },
    },
    interceptors: {
      request: {
        use: vi.fn(),
        eject: vi.fn(),
      },
      response: {
        use: vi.fn(),
        eject: vi.fn(),
      },
    },
  };
}

/**
 * Mock API endpoints for common operations
 */
export const mockApiEndpoints = {
  // Auth endpoints
  login: (success: boolean = true) => {
    if (success) {
      return createMockResponse({
        access_token: 'mock-jwt-token',
        token_type: 'bearer',
      });
    }
    return createMockResponse(
      { detail: 'Invalid credentials' },
      401,
      'Unauthorized'
    );
  },

  getCurrentUser: () => {
    return createMockResponse({
      id: 'user-123',
      email: 'test@example.com',
      username: 'testuser',
      role: 'operator',
      is_active: true,
      mfa_enabled: false,
    });
  },

  // Company endpoints
  getCompanies: (page: number = 1, limit: number = 10) => {
    return createMockResponse({
      items: [
        {
          id: 'company-1',
          legal_name: 'Test Company Inc',
          registration_number: 'TEST123',
          jurisdiction: 'US',
          domain: 'testcompany.com',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ],
      total: 1,
      page,
      limit,
      pages: 1,
    });
  },

  getCompany: (id: string = 'company-1') => {
    return createMockResponse({
      id,
      legal_name: 'Test Company Inc',
      registration_number: 'TEST123',
      jurisdiction: 'US',
      domain: 'testcompany.com',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    });
  },

  createCompany: () => {
    return createMockResponse(
      {
        id: 'company-new',
        legal_name: 'New Company Inc',
        registration_number: 'NEW123',
        jurisdiction: 'US',
        domain: 'newcompany.com',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      201,
      'Created'
    );
  },

  // Verification endpoints
  getVerificationResult: (companyId: string = 'company-1') => {
    return createMockResponse({
      id: 'verification-1',
      company_id: companyId,
      risk_score: 45,
      risk_category: 'MEDIUM',
      verification_status: 'COMPLETED',
      dns_verified: true,
      registration_verified: true,
      contact_verified: true,
      address_verified: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    });
  },

  triggerVerification: (companyId: string = 'company-1') => {
    return createMockResponse(
      {
        task_id: 'task-123',
        status: 'PENDING',
        message: 'Verification started',
      },
      202,
      'Accepted'
    );
  },

  // Report endpoints
  generateReport: (companyId: string = 'company-1') => {
    return createMockResponse({
      report_metadata: {
        company_name: 'Test Company Inc',
        report_id: 'report-123',
        generated_at: new Date().toISOString(),
      },
      company_info: {
        legal_name: 'Test Company Inc',
        registration_number: 'TEST123',
      },
      risk_assessment: {
        risk_score: 45,
        risk_category: 'MEDIUM',
      },
      summary: {
        total_data_points: 10,
        verified_data_points: 8,
        verification_rate: 80,
      },
    });
  },
};

/**
 * Setup API mocks for a test suite
 */
export function setupApiMocks(axiosMock: any) {
  // Default successful responses
  axiosMock.get.mockImplementation((url: string) => {
    if (url.includes('/auth/me')) {
      return Promise.resolve(mockApiEndpoints.getCurrentUser());
    }
    if (url.includes('/companies') && !url.includes('/verify')) {
      if (url.match(/\/companies\/[^/]+$/)) {
        return Promise.resolve(mockApiEndpoints.getCompany());
      }
      return Promise.resolve(mockApiEndpoints.getCompanies());
    }
    if (url.includes('/verification')) {
      return Promise.resolve(mockApiEndpoints.getVerificationResult());
    }
    if (url.includes('/reports')) {
      return Promise.resolve(mockApiEndpoints.generateReport());
    }
    return Promise.reject(new Error(`Unmocked GET request: ${url}`));
  });

  axiosMock.post.mockImplementation((url: string) => {
    if (url.includes('/auth/login')) {
      return Promise.resolve(mockApiEndpoints.login());
    }
    if (url.includes('/companies')) {
      return Promise.resolve(mockApiEndpoints.createCompany());
    }
    if (url.includes('/verify')) {
      return Promise.resolve(mockApiEndpoints.triggerVerification());
    }
    return Promise.reject(new Error(`Unmocked POST request: ${url}`));
  });

  return axiosMock;
}


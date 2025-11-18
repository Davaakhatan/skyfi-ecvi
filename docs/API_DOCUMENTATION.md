# API Documentation
## Enterprise Company Verification Intelligence (ECVI)

**Version:** 1.0  
**Base URL:** `https://api.ecvi.example.com/api/v1`  
**Authentication:** Bearer Token (JWT)

---

## Table of Contents

1. [Authentication](#authentication)
2. [Companies](#companies)
3. [Verification](#verification)
4. [Reports](#reports)
5. [Reviews](#reviews)
6. [Data Corrections](#data-corrections)
7. [Contact Verification](#contact-verification)
8. [Risk Scoring](#risk-scoring)
9. [Audit Logs](#audit-logs)
10. [Security](#security)
11. [Error Handling](#error-handling)
12. [Rate Limiting](#rate-limiting)

---

## Authentication

### Login

Authenticate and receive an access token.

**Endpoint:** `POST /auth/login`

**Request:**
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=yourpassword
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Usage:**
Include the token in subsequent requests:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Companies

### List Companies

Get a paginated list of companies with optional filtering.

**Endpoint:** `GET /companies/`

**Query Parameters:**
- `skip` (integer, default: 0): Number of records to skip
- `limit` (integer, default: 50): Number of records to return
- `search` (string, optional): Search by company name
- `risk_category` (string, optional): Filter by risk category (LOW, MEDIUM, HIGH)
- `verification_status` (string, optional): Filter by status (PENDING, IN_PROGRESS, COMPLETED, FAILED)
- `review_status` (string, optional): Filter by review status (APPROVED, FLAGGED, REJECTED, PENDING)

**Request:**
```http
GET /api/v1/companies/?skip=0&limit=50&risk_category=HIGH
Authorization: Bearer {token}
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "legal_name": "Example Company Inc",
      "registration_number": "12345678",
      "jurisdiction": "US",
      "domain": "example.com",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z",
      "verification_result": {
        "risk_score": 75,
        "risk_category": "HIGH",
        "verification_status": "COMPLETED"
      }
    }
  ],
  "total": 100,
  "skip": 0,
  "limit": 50
}
```

### Get Company

Get detailed information about a specific company.

**Endpoint:** `GET /companies/{company_id}`

**Request:**
```http
GET /api/v1/companies/{company_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "uuid",
  "legal_name": "Example Company Inc",
  "registration_number": "12345678",
  "jurisdiction": "US",
  "domain": "example.com",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "verification_results": [...],
  "reviews": [...],
  "data_corrections": [...]
}
```

### Create Company

Create a new company and trigger automatic verification.

**Endpoint:** `POST /companies/`

**Request:**
```http
POST /api/v1/companies/
Authorization: Bearer {token}
Content-Type: application/json

{
  "legal_name": "New Company Ltd",
  "registration_number": "REG123456",
  "jurisdiction": "US",
  "domain": "newcompany.com"
}
```

**Response:**
```json
{
  "id": "uuid",
  "legal_name": "New Company Ltd",
  "registration_number": "REG123456",
  "jurisdiction": "US",
  "domain": "newcompany.com",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

**Status Code:** 201 Created

---

## Verification

### Get Verification Result

Get the latest verification result for a company.

**Endpoint:** `GET /companies/{company_id}/verification`

**Request:**
```http
GET /api/v1/companies/{company_id}/verification
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "uuid",
  "company_id": "uuid",
  "risk_score": 65,
  "risk_category": "MEDIUM",
  "verification_status": "COMPLETED",
  "analysis_started_at": "2025-01-01T10:00:00Z",
  "analysis_completed_at": "2025-01-01T11:30:00Z",
  "created_at": "2025-01-01T10:00:00Z",
  "dns_verification": {...},
  "contact_verification": {...},
  "registration_verification": {...},
  "hq_address_verification": {...},
  "discrepancies": [...],
  "confidence_scores": {...}
}
```

### Trigger Verification

Manually trigger verification for a company.

**Endpoint:** `POST /companies/{company_id}/verify`

**Request:**
```http
POST /api/v1/companies/{company_id}/verify
Authorization: Bearer {token}
```

**Response:**
```json
{
  "message": "Verification started",
  "verification_id": "uuid",
  "status": "IN_PROGRESS"
}
```

### Get Verification History

Get all verification results for a company.

**Endpoint:** `GET /companies/{company_id}/verification/history`

**Request:**
```http
GET /api/v1/companies/{company_id}/verification/history
Authorization: Bearer {token}
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "risk_score": 65,
      "risk_category": "MEDIUM",
      "verification_status": "COMPLETED",
      "created_at": "2025-01-01T10:00:00Z"
    }
  ],
  "total": 5
}
```

---

## Reports

### Get Verification Report

Get a comprehensive verification report for a company.

**Endpoint:** `GET /reports/companies/{company_id}`

**Query Parameters:**
- `format` (string, optional): Report format (json, csv, pdf, html). Default: json

**Request:**
```http
GET /api/v1/reports/companies/{company_id}?format=json
Authorization: Bearer {token}
```

**Response (JSON):**
```json
{
  "company": {...},
  "verification_result": {...},
  "registration_data": {...},
  "contact_information": {...},
  "hq_address": {...},
  "dns_verification": {...},
  "risk_breakdown": {...},
  "data_sources": [...],
  "confidence_scores": {...},
  "discrepancies": [...],
  "generated_at": "2025-01-01T12:00:00Z"
}
```

**Response (PDF/CSV/HTML):**
Returns file download with appropriate Content-Type header.

### Create Shareable Report Link

Create a shareable link to a report (accessible without authentication).

**Endpoint:** `POST /reports/companies/{company_id}/share`

**Request:**
```http
POST /api/v1/reports/companies/{company_id}/share
Authorization: Bearer {token}
Content-Type: application/json

{
  "expires_in_days": 30,
  "format": "json"
}
```

**Response:**
```json
{
  "share_token": "abc123def456...",
  "share_url": "https://ecvi.example.com/shared/abc123def456...",
  "expires_at": "2025-02-01T12:00:00Z"
}
```

### Get Shared Report

Get a report using a shareable token (no authentication required).

**Endpoint:** `GET /shared/{share_token}`

**Request:**
```http
GET /api/v1/shared/{share_token}
```

**Response:**
Same as Get Verification Report

---

## Reviews

### Get Review

Get the review status for a company.

**Endpoint:** `GET /reviews/companies/{company_id}/review`

**Request:**
```http
GET /api/v1/reviews/companies/{company_id}/review
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "uuid",
  "company_id": "uuid",
  "status": "APPROVED",
  "notes": "Company verified and approved",
  "reviewed_at": "2025-01-01T12:00:00Z",
  "reviewer_id": "uuid",
  "reviewer_name": "John Doe"
}
```

**Status Code:** 404 if no review exists

### Create/Update Review

Create or update a review for a company.

**Endpoint:** `POST /reviews/companies/{company_id}/review`

**Request:**
```http
POST /api/v1/reviews/companies/{company_id}/review
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "APPROVED",
  "notes": "Company verified and approved"
}
```

**Response:**
```json
{
  "id": "uuid",
  "company_id": "uuid",
  "status": "APPROVED",
  "notes": "Company verified and approved",
  "reviewed_at": "2025-01-01T12:00:00Z",
  "reviewer_id": "uuid",
  "reviewer_name": "John Doe"
}
```

**Valid Status Values:**
- `APPROVED`: Company approved
- `FLAGGED`: Requires additional review
- `REJECTED`: Company rejected
- `PENDING`: Review pending

---

## Data Corrections

### List Corrections

Get all data corrections for a company.

**Endpoint:** `GET /companies/{company_id}/corrections`

**Request:**
```http
GET /api/v1/companies/{company_id}/corrections
Authorization: Bearer {token}
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "company_id": "uuid",
      "field_name": "legal_name",
      "field_type": "legal_name",
      "old_value": "Old Company Name",
      "new_value": "New Company Name",
      "status": "APPROVED",
      "reason": "Corrected typo",
      "proposed_by": "uuid",
      "approved_by": "uuid",
      "created_at": "2025-01-01T12:00:00Z"
    }
  ],
  "total": 3
}
```

### Propose Correction

Propose a data correction.

**Endpoint:** `POST /corrections/`

**Request:**
```http
POST /api/v1/corrections/
Authorization: Bearer {token}
Content-Type: application/json

{
  "company_id": "uuid",
  "field_name": "legal_name",
  "field_type": "legal_name",
  "new_value": "Corrected Company Name",
  "reason": "Found typo in original data"
}
```

**Response:**
```json
{
  "id": "uuid",
  "company_id": "uuid",
  "field_name": "legal_name",
  "field_type": "legal_name",
  "old_value": "Old Company Name",
  "new_value": "Corrected Company Name",
  "status": "PENDING",
  "reason": "Found typo in original data",
  "proposed_by": "uuid",
  "created_at": "2025-01-01T12:00:00Z"
}
```

### Approve Correction

Approve a pending correction (Admin only).

**Endpoint:** `POST /corrections/{correction_id}/approve`

**Request:**
```http
POST /api/v1/corrections/{correction_id}/approve
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "uuid",
  "status": "APPROVED",
  "approved_by": "uuid",
  "approved_at": "2025-01-01T12:00:00Z",
  "message": "Correction approved and applied"
}
```

### Reject Correction

Reject a pending correction (Admin only).

**Endpoint:** `POST /corrections/{correction_id}/reject`

**Request:**
```http
POST /api/v1/corrections/{correction_id}/reject?rejection_reason=Incorrect data
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "uuid",
  "status": "REJECTED",
  "rejected_by": "uuid",
  "rejected_at": "2025-01-01T12:00:00Z",
  "rejection_reason": "Incorrect data"
}
```

---

## Contact Verification

### Verify Contact Information

Verify email, phone, or name for a company.

**Endpoint:** `POST /companies/{company_id}/contact/verify`

**Request:**
```http
POST /api/v1/companies/{company_id}/contact/verify
Authorization: Bearer {token}
Content-Type: application/json

{
  "email": "contact@example.com",
  "phone": "+1234567890",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "email_verification": {
    "email": "contact@example.com",
    "format_valid": true,
    "domain_valid": true,
    "mx_records_found": true,
    "status": "VERIFIED",
    "confidence": 0.95
  },
  "phone_verification": {
    "phone": "+1234567890",
    "format_valid": true,
    "country_code_valid": true,
    "status": "VERIFIED",
    "confidence": 0.90
  },
  "name_verification": {
    "name": "John Doe",
    "status": "PARTIAL",
    "confidence": 0.75
  }
}
```

### Get Contact Verification Results

Get contact verification results for a company.

**Endpoint:** `GET /companies/{company_id}/contact/verification`

**Request:**
```http
GET /api/v1/companies/{company_id}/contact/verification
Authorization: Bearer {token}
```

**Response:**
Same as Verify Contact Information

---

## Risk Scoring

### Get Risk Score

Get the current risk score for a company.

**Endpoint:** `GET /risk/companies/{company_id}`

**Request:**
```http
GET /api/v1/risk/companies/{company_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "company_id": "uuid",
  "risk_score": 65,
  "risk_category": "MEDIUM",
  "breakdown": {
    "dns_risk": 20,
    "registration_consistency": 15,
    "contact_validation": 10,
    "domain_authenticity": 10,
    "cross_source_validation": 10
  },
  "calculated_at": "2025-01-01T11:30:00Z"
}
```

### Get Risk History

Get historical risk scores for a company.

**Endpoint:** `GET /risk/companies/{company_id}/history`

**Query Parameters:**
- `limit` (integer, optional): Number of records to return. Default: 50

**Request:**
```http
GET /api/v1/risk/companies/{company_id}/history?limit=10
Authorization: Bearer {token}
```

**Response:**
```json
{
  "items": [
    {
      "risk_score": 65,
      "risk_category": "MEDIUM",
      "calculated_at": "2025-01-01T11:30:00Z"
    }
  ],
  "total": 5,
  "trend": "increasing"
}
```

---

## Audit Logs

### List Audit Logs

Get audit logs (Admin only).

**Endpoint:** `GET /audit/`

**Query Parameters:**
- `skip` (integer, default: 0)
- `limit` (integer, default: 50)
- `user_id` (string, optional): Filter by user
- `action` (string, optional): Filter by action
- `resource_type` (string, optional): Filter by resource type
- `start_date` (datetime, optional): Filter by start date
- `end_date` (datetime, optional): Filter by end date

**Request:**
```http
GET /api/v1/audit/?limit=100&action=LOGIN
Authorization: Bearer {token}
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "action": "LOGIN",
      "resource_type": "user",
      "resource_id": "uuid",
      "details": {...},
      "ip_address": "192.168.1.1",
      "created_at": "2025-01-01T12:00:00Z"
    }
  ],
  "total": 1000,
  "skip": 0,
  "limit": 100
}
```

---

## Security

### Get Security Audit - Failed Logins

Get failed login attempts (Admin only).

**Endpoint:** `GET /security/audit/failed-logins`

**Query Parameters:**
- `hours` (integer, optional): Hours to look back. Default: 24

**Request:**
```http
GET /api/v1/security/audit/failed-logins?hours=48
Authorization: Bearer {token}
```

**Response:**
```json
{
  "failed_attempts": [
    {
      "username": "user@example.com",
      "ip_address": "192.168.1.1",
      "attempted_at": "2025-01-01T12:00:00Z",
      "count": 5
    }
  ],
  "total": 10,
  "suspicious_patterns": [...]
}
```

### Get Security Audit - Unauthorized Access

Get unauthorized access attempts (Admin only).

**Endpoint:** `GET /security/audit/unauthorized-access`

**Request:**
```http
GET /api/v1/security/audit/unauthorized-access
Authorization: Bearer {token}
```

**Response:**
```json
{
  "unauthorized_attempts": [
    {
      "user_id": "uuid",
      "resource": "/api/v1/admin/users",
      "ip_address": "192.168.1.1",
      "attempted_at": "2025-01-01T12:00:00Z"
    }
  ],
  "total": 3
}
```

### Get Security Audit - Inactive Admins

Get inactive admin accounts (Admin only).

**Endpoint:** `GET /security/audit/inactive-admins`

**Query Parameters:**
- `days` (integer, optional): Days of inactivity. Default: 30

**Request:**
```http
GET /api/v1/security/audit/inactive-admins?days=60
Authorization: Bearer {token}
```

**Response:**
```json
{
  "inactive_admins": [
    {
      "user_id": "uuid",
      "username": "admin@example.com",
      "last_login": "2024-11-01T12:00:00Z",
      "days_inactive": 61
    }
  ],
  "total": 2
}
```

---

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Example Error Responses

**401 Unauthorized:**
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden:**
```json
{
  "detail": "Insufficient permissions to perform this action"
}
```

**404 Not Found:**
```json
{
  "detail": "Company not found"
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "legal_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Rate Limiting

### Rate Limits

- **Default:** 60 requests per minute per IP address
- **Authenticated Users:** 100 requests per minute per user
- **Admin Users:** 200 requests per minute per user

### Rate Limit Headers

Response headers include rate limit information:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640995200
```

### Rate Limit Exceeded

When rate limit is exceeded:

**Status Code:** 429 Too Many Requests

**Response:**
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

---

## Pagination

### Pagination Parameters

- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 50, max: 100)

### Pagination Response

All paginated responses include:

```json
{
  "items": [...],
  "total": 1000,
  "skip": 0,
  "limit": 50
}
```

### Pagination Headers

Response headers include pagination information:

```http
X-Total-Count: 1000
X-Page-Count: 20
```

---

## Data Models

### Company

```typescript
interface Company {
  id: string;
  legal_name: string;
  registration_number: string | null;
  jurisdiction: string | null;
  domain: string | null;
  created_at: string;
  updated_at: string;
}
```

### Verification Result

```typescript
interface VerificationResult {
  id: string;
  company_id: string;
  risk_score: number;
  risk_category: "LOW" | "MEDIUM" | "HIGH";
  verification_status: "PENDING" | "IN_PROGRESS" | "COMPLETED" | "FAILED";
  analysis_started_at: string | null;
  analysis_completed_at: string | null;
  created_at: string;
}
```

### Review

```typescript
interface Review {
  id: string;
  company_id: string;
  status: "APPROVED" | "FLAGGED" | "REJECTED" | "PENDING";
  notes: string | null;
  reviewed_at: string | null;
  reviewer_id: string;
  reviewer_name: string;
}
```

---

## SDKs and Libraries

### Python

```python
import requests

base_url = "https://api.ecvi.example.com/api/v1"
token = "your_access_token"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Get companies
response = requests.get(f"{base_url}/companies/", headers=headers)
companies = response.json()
```

### JavaScript/TypeScript

```typescript
const baseUrl = 'https://api.ecvi.example.com/api/v1';
const token = 'your_access_token';

const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};

// Get companies
const response = await fetch(`${baseUrl}/companies/`, { headers });
const companies = await response.json();
```

---

## Webhooks (Future)

Webhook support for real-time notifications is planned for future releases.

---

## Support

For API support:
- **Email:** api-support@ecvi.example.com
- **Documentation:** https://docs.ecvi.example.com
- **Status Page:** https://status.ecvi.example.com

---

**API Version:** 1.0  
**Last Updated:** 2025  
**Base URL:** `https://api.ecvi.example.com/api/v1`


# Performance Optimization Guide

## Overview

This document outlines the performance optimizations implemented in the ECVI system to ensure fast response times and efficient resource usage.

## Database Optimizations

### Indexes

Comprehensive database indexes have been added to optimize common query patterns:

**Companies Table:**
- `ix_companies_legal_name_created_at` - Composite index for search + date range queries
- `ix_companies_registration_number` - Partial index for registration number lookups

**Verification Results:**
- `ix_verification_results_company_status_risk` - Composite index for filtering by company, status, and risk
- `ix_verification_results_company_created` - Index for latest verification per company

**Reviews:**
- `ix_reviews_company_reviewer_status` - Composite index for review filtering
- `ix_reviews_company_reviewed_at` - Index for latest review per company

**Company Data:**
- `ix_company_data_company_type_field` - Composite index for data queries

**Data Corrections:**
- `ix_data_corrections_company_status` - Index for correction filtering

**Audit Logs:**
- `ix_audit_logs_user_action_created` - Composite index for audit queries

**Shared Reports:**
- `ix_shared_reports_token_active` - Index for token lookups

**Contact Verifications:**
- `ix_contact_verifications_company_type_status` - Composite index for contact verification queries

### Query Optimization

**Eager Loading:**
- Companies list endpoint uses `selectinload` to eagerly load verification results and reviews
- Prevents N+1 query problems
- Batch loads user data to avoid repeated queries

**Example:**
```python
companies = query.options(
    selectinload(Company.verification_results).order_by(desc(VerificationResult.created_at)).limit(1),
    selectinload(Company.reviews).filter(Review.reviewer_id == current_user.id).order_by(desc(Review.reviewed_at)).limit(1)
).offset(skip).limit(limit).all()
```

**Batch User Loading:**
- Collects all user IDs first
- Loads all users in a single query
- Maps users by ID for O(1) lookup

## Caching Strategy

### Redis Caching

A centralized `CacheService` provides caching functionality:

**Features:**
- Automatic Redis connection management
- Graceful fallback if Redis unavailable
- TTL-based expiration
- Pattern-based cache invalidation
- JSON serialization/deserialization

**Cache Keys:**
- `company:{company_id}` - Company data (30 min TTL)
- `verification:{company_id}:latest` - Latest verification result (15 min TTL)
- `report:{company_id}:{verification_result_id}:{format}` - Generated reports (1 hour TTL)
- `report:shared:{share_token}:{format}` - Shared reports (1 hour TTL)

**Cache Invalidation:**
- Automatic invalidation on company create/update/delete
- Pattern-based invalidation for related data
- `invalidate_company_cache()` method for comprehensive cleanup

### Cached Endpoints

**Companies:**
- `GET /companies/{id}` - Cached for 30 minutes
- `GET /companies/{id}/verification` - Cached for 15 minutes

**Reports:**
- `GET /reports/company/{id}/report?format=json` - Cached for 1 hour
- `GET /reports/shared/{token}?format=json` - Cached for 1 hour

## API Response Time Optimizations

### Target Response Times
- List views: < 2 seconds
- Detail views: < 500ms
- Report generation: < 30 seconds

### Optimizations Applied

1. **Eager Loading** - Reduces database round trips
2. **Batch Queries** - Loads related data in single queries
3. **Caching** - Serves cached responses when available
4. **Index Usage** - Ensures fast query execution
5. **Query Optimization** - Minimizes data transfer

## Frontend Optimizations

### Code Splitting

Manual chunk configuration for optimal caching:

```typescript
manualChunks: {
  'vendor-react': ['react', 'react-dom', 'react-router-dom'],
  'vendor-ui': ['lucide-react', 'recharts'],
  'vendor-utils': ['axios', 'zustand', 'date-fns', 'clsx'],
}
```

**Benefits:**
- Vendor libraries cached separately
- Application code changes don't invalidate vendor cache
- Smaller initial bundle size

### Lazy Loading

Route-based code splitting with React.lazy:

```typescript
const Dashboard = lazy(() => import('./pages/Dashboard'))
const CompanyList = lazy(() => import('./pages/CompanyList'))
const CompanyDetail = lazy(() => import('./pages/CompanyDetail'))
```

**Benefits:**
- Only loads code for current route
- Faster initial page load
- Reduced bundle size

### Production Build Optimizations

- **Terser Minification** - Reduces bundle size
- **Console Removal** - Drops console.log in production
- **Chunk Size Warnings** - Alerts on large bundles

## Report Generation Optimizations

### Eager Loading

ReportGenerator uses eager loading to minimize queries:

```python
self._company_query = db.query(Company).options(
    joinedload(Company.verification_results),
    joinedload(Company.company_data)
)
```

### Data Pre-processing

- Filters company data once by type
- Reuses filtered data across sections
- Avoids repeated filtering operations

### Caching

- JSON reports cached for 1 hour
- Reduces database load for repeated requests
- Fast response for cached reports

## Performance Monitoring

### Cache Hit Indicators

API responses include `X-Cache: HIT` header when serving cached data.

### Metrics to Monitor

1. **Database Query Count** - Should decrease with eager loading
2. **API Response Times** - Should meet target times
3. **Cache Hit Rate** - Should be high for frequently accessed data
4. **Frontend Bundle Size** - Should be optimized with code splitting

## Best Practices

1. **Always use eager loading** for related data in list views
2. **Batch load users** instead of querying individually
3. **Cache frequently accessed data** with appropriate TTL
4. **Invalidate cache** when data changes
5. **Use indexes** for all filtered/sorted columns
6. **Lazy load** large components and routes
7. **Monitor performance** and adjust caching strategies

## Migration

To apply database indexes:

```bash
cd backend
alembic upgrade head
```

This will apply the `d4e5f6a7b8c9_add_performance_indexes` migration.

## Future Optimizations

- [ ] Query result pagination optimization
- [ ] Database connection pooling tuning
- [ ] CDN for static assets
- [ ] API response compression
- [ ] GraphQL for flexible queries
- [ ] Read replicas for reporting queries


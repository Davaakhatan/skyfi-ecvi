# Performance Testing Guide

## Overview

Performance testing ensures the ECVI system meets performance requirements under various load conditions. This document outlines the performance testing strategy, tools, and procedures.

## Performance Requirements

### Response Time Targets

- **API Endpoints**: < 500ms (95th percentile)
- **List Views**: < 2 seconds
- **Report Generation**: < 30 seconds
- **AI Analysis**: < 2 hours

### Throughput Targets

- **Concurrent Users**: 100+ concurrent users
- **Requests per Second**: 50+ RPS under normal load
- **Error Rate**: < 1% under normal load

## Testing Tools

### 1. pytest-benchmark

**Purpose**: Unit-level performance benchmarks

**Usage**:
```bash
cd backend
pytest tests/test_performance.py --benchmark-only
```

**Benefits**:
- Integrated with pytest
- Easy to run in CI/CD
- Provides statistical analysis
- Tracks performance over time

### 2. Locust

**Purpose**: Load testing and stress testing

**Usage**:
```bash
cd backend
locust -f load_tests/locustfile.py --host=http://localhost:8000
```

**Benefits**:
- Python-based (easy to customize)
- Web UI for real-time monitoring
- Distributed testing support
- Detailed statistics and charts

## Test Scenarios

### 1. API Endpoint Performance

Tests individual API endpoints to ensure they meet response time targets:

- `GET /api/v1/companies/` - < 2 seconds
- `GET /api/v1/companies/{id}` - < 500ms
- `POST /api/v1/companies/` - < 500ms
- `GET /api/v1/reports/companies/{id}` - < 30 seconds

**Location**: `backend/tests/test_performance.py`

### 2. Database Query Performance

Tests database query optimization:

- Indexed queries
- Eager loading effectiveness
- Query count reduction

**Location**: `backend/tests/test_performance.py::TestDatabaseQueryPerformance`

### 3. Caching Performance

Tests caching effectiveness:

- Cache hit rates
- Response time improvement with caching
- Cache invalidation

**Location**: `backend/tests/test_performance.py::TestCachingPerformance`

### 4. Load Testing

Simulates real user behavior under load:

- Normal load (10-50 users)
- High load (100-500 users)
- Spike testing (sudden traffic increase)

**Location**: `backend/load_tests/locustfile.py`

## Running Performance Tests

### Unit Performance Tests

```bash
cd backend
pytest tests/test_performance.py -v
```

### Benchmark Tests

```bash
cd backend
pytest tests/test_performance.py --benchmark-only --benchmark-json=benchmark.json
```

### Load Tests

1. Start the application:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. Run Locust:
```bash
cd backend
locust -f load_tests/locustfile.py --host=http://localhost:8000
```

3. Open Locust web UI: http://localhost:8089

4. Configure test:
   - Number of users: 50
   - Spawn rate: 5 users/second
   - Host: http://localhost:8000

5. Start test and monitor results

## Performance Metrics

### Key Metrics to Monitor

1. **Response Time Percentiles**
   - p50 (median)
   - p95 (95th percentile)
   - p99 (99th percentile)

2. **Throughput**
   - Requests per second (RPS)
   - Successful requests per second

3. **Error Rate**
   - Percentage of failed requests
   - Types of errors (4xx, 5xx)

4. **Resource Usage**
   - CPU usage
   - Memory usage
   - Database connections
   - Redis connections

### Acceptable Performance

- **p95 Response Time**: < 500ms for API endpoints
- **p95 Response Time**: < 2 seconds for list views
- **Error Rate**: < 1% under normal load
- **Throughput**: 50+ RPS

## Performance Optimization Checklist

After performance testing, optimize based on findings:

- [ ] Identify slow queries and optimize
- [ ] Add missing database indexes
- [ ] Optimize eager loading strategies
- [ ] Improve cache hit rates
- [ ] Reduce N+1 query problems
- [ ] Optimize API response payloads
- [ ] Enable response compression
- [ ] Scale horizontally if needed

## Continuous Performance Monitoring

### In CI/CD

Performance tests run in CI/CD to catch regressions:

```yaml
# .github/workflows/ci.yml
- name: Run performance tests
  run: pytest tests/test_performance.py --benchmark-only
```

### Production Monitoring

- APM tools (e.g., New Relic, Datadog)
- Application logs
- Database query logs
- Redis monitoring
- Server metrics (CPU, memory, disk)

## Troubleshooting Performance Issues

### Slow API Responses

1. Check database query performance
2. Verify indexes are being used
3. Check cache hit rates
4. Review eager loading strategies
5. Analyze slow query logs

### High Error Rates

1. Check database connection pool
2. Verify Redis connectivity
3. Review rate limiting settings
4. Check for memory leaks
5. Monitor resource usage

### High Resource Usage

1. Optimize database queries
2. Increase cache hit rates
3. Scale horizontally
4. Optimize application code
5. Review third-party API calls

## Best Practices

1. **Run performance tests regularly** - Catch regressions early
2. **Test under realistic conditions** - Use production-like data volumes
3. **Monitor key metrics** - Track performance over time
4. **Set performance budgets** - Define acceptable limits
5. **Optimize incrementally** - Focus on biggest bottlenecks first
6. **Document findings** - Keep performance test results
7. **Automate testing** - Include in CI/CD pipeline

## Future Enhancements

- [ ] Add performance tests to CI/CD pipeline
- [ ] Set up automated performance regression detection
- [ ] Integrate with APM tools
- [ ] Add distributed load testing
- [ ] Create performance dashboards
- [ ] Set up alerting for performance degradation


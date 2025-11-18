# Load Testing

This directory contains load testing scripts for the ECVI API.

## Tools

- **Locust**: Python-based load testing tool
- **pytest-benchmark**: Performance benchmarking for unit tests

## Running Load Tests

### Prerequisites

```bash
cd backend
pip install -e ".[perf]"
```

### Locust Load Testing

1. Start the backend server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. Run Locust:
```bash
locust -f load_tests/locustfile.py --host=http://localhost:8000
```

3. Access Locust web UI:
   - Open browser: http://localhost:8089
   - Set number of users and spawn rate
   - Start the test

### Command Line Load Testing

```bash
# Run with specific number of users
locust -f load_tests/locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --run-time 5m

# Run headless (no web UI)
locust -f load_tests/locustfile.py --host=http://localhost:8000 --users 50 --spawn-rate 5 --headless --run-time 2m
```

### Performance Benchmarks

Run performance benchmarks with pytest:

```bash
pytest tests/test_performance.py --benchmark-only
```

## Test Scenarios

### Normal Load
- 10-50 concurrent users
- Typical user behavior (browsing, searching, viewing reports)
- Expected: All requests < 500ms

### High Load
- 100-500 concurrent users
- Stress testing
- Expected: System remains stable, graceful degradation

### Spike Testing
- Sudden increase from 10 to 200 users
- Test system's ability to handle traffic spikes
- Expected: System recovers quickly

## Performance Targets

- **API Endpoints**: < 500ms response time (95th percentile)
- **List Views**: < 2 seconds response time
- **Report Generation**: < 30 seconds
- **Concurrent Users**: Support 100+ concurrent users
- **Error Rate**: < 1% under normal load

## Monitoring

During load tests, monitor:
- Response times (p50, p95, p99)
- Error rates
- Database connection pool usage
- Redis cache hit rates
- Memory and CPU usage
- Request throughput (requests/second)

## Results Analysis

After load testing:
1. Review response time percentiles
2. Identify bottlenecks
3. Check for memory leaks
4. Verify caching effectiveness
5. Optimize slow queries
6. Update performance documentation


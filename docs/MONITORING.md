# Monitoring and Observability Guide
## Enterprise Company Verification Intelligence (ECVI)

**Version:** 1.0  
**Date:** 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Metrics](#metrics)
3. [Prometheus Setup](#prometheus-setup)
4. [Grafana Dashboards](#grafana-dashboards)
5. [Error Tracking (Sentry)](#error-tracking-sentry)
6. [Log Aggregation](#log-aggregation)
7. [Alerting](#alerting)
8. [Runbooks](#runbooks)

---

## Overview

ECVI includes comprehensive monitoring and observability features:

- **Prometheus Metrics** - Application and system metrics
- **Grafana Dashboards** - Visualization and analysis
- **Sentry Integration** - Error tracking and alerting
- **Health Checks** - Service health monitoring
- **Log Aggregation** - Centralized logging

---

## Metrics

### Available Metrics

#### HTTP Metrics
- `http_requests_total` - Total HTTP requests by method, endpoint, and status code
- `http_request_duration_seconds` - HTTP request duration histogram
- `http_requests_in_progress` - Currently active HTTP requests

#### Database Metrics
- `db_connections_active` - Active database connections
- `db_connections_idle` - Idle database connections

#### Celery Task Metrics
- `celery_tasks_total` - Total Celery tasks by name and status
- `celery_task_duration_seconds` - Celery task duration histogram

### Metrics Endpoint

Access metrics at: `http://your-backend/api/v1/metrics`

Example:
```bash
curl http://localhost:8000/api/v1/metrics
```

---

## Prometheus Setup

### Docker Compose

Add Prometheus to `docker-compose.prod.yml`:

```yaml
prometheus:
  image: prom/prometheus:latest
  container_name: ecvi-prometheus
  volumes:
    - ./monitoring/prometheus-config.yaml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
  ports:
    - "9090:9090"
  networks:
    - ecvi-network
```

### Kubernetes

1. **Install Prometheus Operator** (if not already installed):
```bash
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml
```

2. **Apply ServiceMonitor**:
```bash
kubectl apply -f k8s/prometheus-servicemonitor.yaml
```

3. **Verify metrics are being scraped**:
```bash
kubectl port-forward svc/prometheus 9090:9090 -n monitoring
# Open http://localhost:9090
```

### Prometheus Queries

**Request Rate:**
```promql
rate(http_requests_total[5m])
```

**95th Percentile Latency:**
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**Error Rate:**
```promql
rate(http_requests_total{status_code=~"5.."}[5m])
```

**Active Requests:**
```promql
http_requests_in_progress
```

---

## Grafana Dashboards

### Setup

1. **Install Grafana:**
```bash
# Docker
docker run -d -p 3000:3000 --name=grafana grafana/grafana

# Kubernetes
kubectl apply -f https://raw.githubusercontent.com/grafana/grafana/main/deployment/kubernetes/grafana.yaml
```

2. **Import Dashboard:**
   - Open Grafana UI (http://localhost:3000)
   - Go to Dashboards → Import
   - Upload `monitoring/grafana-dashboard.json`
   - Configure Prometheus data source

### Dashboard Panels

1. **HTTP Request Rate** - Requests per second by endpoint
2. **HTTP Request Duration (p95)** - 95th percentile latency
3. **HTTP Status Codes** - Distribution of status codes
4. **Active Requests** - Currently processing requests
5. **Database Connections** - Active and idle connections
6. **Celery Tasks** - Task execution rate and status
7. **Celery Task Duration** - Task execution time
8. **Error Rate** - 4xx and 5xx error rates

---

## Error Tracking (Sentry)

### Setup

1. **Create Sentry Project:**
   - Go to https://sentry.io
   - Create a new project (FastAPI)
   - Copy the DSN

2. **Configure Environment Variable:**
```bash
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

3. **Verify Integration:**
   - Trigger an error in the application
   - Check Sentry dashboard for error reports

### Features

- **Automatic Error Capture** - All unhandled exceptions
- **Performance Monitoring** - Transaction tracing (10% sample rate)
- **Release Tracking** - Track errors by application version
- **Environment Tagging** - Separate staging/production errors

### Custom Error Reporting

```python
import sentry_sdk

# Capture exception
try:
    risky_operation()
except Exception as e:
    sentry_sdk.capture_exception(e)

# Add context
with sentry_sdk.push_scope() as scope:
    scope.set_tag("company_id", company_id)
    scope.set_context("verification", {"status": "failed"})
    sentry_sdk.capture_message("Verification failed")
```

---

## Log Aggregation

### Structured Logging

ECVI uses structured JSON logging in production:

```json
{
  "timestamp": "2025-01-01T00:00:00Z",
  "level": "INFO",
  "logger": "app.api.v1.companies",
  "message": "Company created",
  "company_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "user-123"
}
```

### Log Collection

#### Docker
```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Export logs
docker-compose -f docker-compose.prod.yml logs backend > backend.log
```

#### Kubernetes
```bash
# View logs
kubectl logs -f deployment/backend -n ecvi

# Export logs
kubectl logs deployment/backend -n ecvi > backend.log
```

### Log Aggregation Tools

**ELK Stack (Elasticsearch, Logstash, Kibana):**
- Collect logs from all services
- Search and analyze logs
- Create visualizations

**Loki + Grafana:**
- Lightweight log aggregation
- Integrated with Grafana dashboards
- PromQL-like query language

**Cloud Logging:**
- AWS CloudWatch Logs
- Google Cloud Logging
- Azure Monitor Logs

---

## Alerting

### Prometheus Alerting Rules

Create `monitoring/alerts.yaml`:

```yaml
groups:
  - name: ecvi_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "95th percentile latency is {{ $value }}s"

      - alert: DatabaseConnectionPoolExhausted
        expr: db_connections_active / (db_connections_active + db_connections_idle) > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database connection pool nearly exhausted"

      - alert: CeleryTaskFailureRate
        expr: rate(celery_tasks_total{status="FAILURE"}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High Celery task failure rate"
```

### Alertmanager Configuration

```yaml
route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'
      continue: true

receivers:
  - name: 'default'
    email_configs:
      - to: 'team@example.com'
        from: 'alerts@example.com'
        smarthost: 'smtp.example.com:587'
        auth_username: 'alerts@example.com'
        auth_password: 'password'

  - name: 'critical-alerts'
    email_configs:
      - to: 'oncall@example.com'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
```

---

## Runbooks

### High Error Rate

**Symptoms:**
- Error rate > 10 errors/sec
- 5xx status codes increasing

**Actions:**
1. Check application logs: `kubectl logs -f deployment/backend -n ecvi`
2. Check Sentry for error details
3. Review recent deployments
4. Check database connectivity: `curl http://backend:8000/health`
5. Scale backend if needed: `kubectl scale deployment backend --replicas=5 -n ecvi`

### High Latency

**Symptoms:**
- p95 latency > 1 second
- Slow API responses

**Actions:**
1. Check database query performance
2. Review slow query logs
3. Check Redis cache hit rate
4. Review Celery task queue length
5. Scale backend services
6. Optimize database queries

### Database Connection Pool Exhausted

**Symptoms:**
- High active connection count
- Connection timeout errors

**Actions:**
1. Check for connection leaks
2. Review long-running queries
3. Increase connection pool size
4. Kill idle connections if needed
5. Restart backend services

### Celery Task Failures

**Symptoms:**
- High task failure rate
- Tasks stuck in queue

**Actions:**
1. Check Celery worker logs
2. Review task error details in Sentry
3. Check Redis connectivity
4. Verify task dependencies
5. Restart Celery workers if needed

### Service Unhealthy

**Symptoms:**
- Health check endpoint returns unhealthy
- Service not responding

**Actions:**
1. Check service logs
2. Verify database connectivity
3. Check Redis connectivity
4. Review resource usage (CPU, memory)
5. Restart service if needed
6. Check for recent configuration changes

---

## Best Practices

1. **Monitor Key Metrics:**
   - Request rate and latency
   - Error rates
   - Database connection pool
   - Celery task queue length

2. **Set Appropriate Alerts:**
   - Critical alerts for service outages
   - Warning alerts for degradation
   - Avoid alert fatigue

3. **Regular Review:**
   - Review dashboards daily
   - Analyze error trends weekly
   - Review performance metrics monthly

4. **Log Retention:**
   - Keep logs for at least 30 days
   - Archive older logs
   - Comply with audit requirements

5. **Documentation:**
   - Keep runbooks updated
   - Document alert thresholds
   - Record incident responses

---

## Support

For monitoring issues:
1. Check Prometheus targets: http://prometheus:9090/targets
2. Verify ServiceMonitor: `kubectl get servicemonitor -n ecvi`
3. Check metrics endpoint: `curl http://backend:8000/api/v1/metrics`
4. Review Grafana data source configuration
5. Check Sentry project settings

---

**Last Updated:** 2025


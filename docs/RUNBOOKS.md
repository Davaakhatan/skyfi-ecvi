# Runbooks
## Enterprise Company Verification Intelligence (ECVI)

**Version:** 1.0  
**Date:** 2025

---

## Table of Contents

1. [Service Health Checks](#service-health-checks)
2. [Common Issues](#common-issues)
3. [Emergency Procedures](#emergency-procedures)
4. [Maintenance Procedures](#maintenance-procedures)

---

## Service Health Checks

### Backend Health Check

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "database": "healthy",
  "redis": "healthy",
  "version": "0.1.0"
}
```

### Frontend Health Check

```bash
curl http://localhost/health

# Expected response: "healthy"
```

### Database Connectivity

```bash
# Docker
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U ecvi_user

# Kubernetes
kubectl exec -it deployment/postgres -n ecvi -- pg_isready -U ecvi_user
```

### Redis Connectivity

```bash
# Docker
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# Kubernetes
kubectl exec -it deployment/redis -n ecvi -- redis-cli ping
```

---

## Common Issues

### Issue: Backend Returns 500 Errors

**Symptoms:**
- API endpoints return 500 status codes
- Error logs show exceptions

**Diagnosis:**
```bash
# Check backend logs
docker-compose -f docker-compose.prod.yml logs backend | tail -50
# or
kubectl logs -f deployment/backend -n ecvi --tail=50

# Check health endpoint
curl http://localhost:8000/health

# Check Sentry for error details
```

**Resolution:**
1. Identify the error from logs or Sentry
2. Check database connectivity
3. Verify environment variables
4. Check for recent deployments
5. Rollback if needed: `kubectl rollout undo deployment/backend -n ecvi`

---

### Issue: High Database Connection Usage

**Symptoms:**
- Database connection pool exhausted
- Connection timeout errors
- Slow queries

**Diagnosis:**
```bash
# Check active connections
docker-compose -f docker-compose.prod.yml exec postgres psql -U ecvi_user -d ecvi -c "SELECT count(*) FROM pg_stat_activity;"

# Check long-running queries
docker-compose -f docker-compose.prod.yml exec postgres psql -U ecvi_user -d ecvi -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';"
```

**Resolution:**
1. Kill long-running queries if safe
2. Increase connection pool size in configuration
3. Check for connection leaks in code
4. Restart backend services to reset connections

---

### Issue: Celery Tasks Not Processing

**Symptoms:**
- Tasks stuck in queue
- No task execution
- High queue length

**Diagnosis:**
```bash
# Check Celery worker status
docker-compose -f docker-compose.prod.yml exec celery-worker celery -A app.tasks.celery_app inspect active

# Check Redis connectivity
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# Check queue length
docker-compose -f docker-compose.prod.yml exec celery-worker celery -A app.tasks.celery_app inspect reserved
```

**Resolution:**
1. Check Celery worker logs
2. Verify Redis connectivity
3. Restart Celery workers
4. Check for task errors in Sentry
5. Scale Celery workers if needed

---

### Issue: Slow API Responses

**Symptoms:**
- API response time > 1 second
- Timeout errors
- High latency metrics

**Diagnosis:**
```bash
# Check Prometheus metrics
# Query: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Check database query performance
docker-compose -f docker-compose.prod.yml exec postgres psql -U ecvi_user -d ecvi -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Check Redis cache hit rate
docker-compose -f docker-compose.prod.yml exec redis redis-cli INFO stats | grep keyspace
```

**Resolution:**
1. Optimize slow database queries
2. Check Redis cache effectiveness
3. Review N+1 query patterns
4. Add database indexes if needed
5. Scale backend services

---

### Issue: Frontend Not Loading

**Symptoms:**
- Frontend returns blank page
- 404 errors
- API connection errors

**Diagnosis:**
```bash
# Check frontend logs
docker-compose -f docker-compose.prod.yml logs frontend
# or
kubectl logs -f deployment/frontend -n ecvi

# Check nginx configuration
docker-compose -f docker-compose.prod.yml exec frontend nginx -t

# Check backend connectivity
curl http://backend:8000/health
```

**Resolution:**
1. Verify backend is accessible
2. Check CORS configuration
3. Verify nginx configuration
4. Check frontend build artifacts
5. Restart frontend service

---

## Emergency Procedures

### Service Outage

**If entire service is down:**

1. **Check service status:**
```bash
# Docker
docker-compose -f docker-compose.prod.yml ps

# Kubernetes
kubectl get pods -n ecvi
```

2. **Check logs:**
```bash
docker-compose -f docker-compose.prod.yml logs --tail=100
```

3. **Restart services:**
```bash
# Docker
docker-compose -f docker-compose.prod.yml restart

# Kubernetes
kubectl rollout restart deployment/backend -n ecvi
kubectl rollout restart deployment/frontend -n ecvi
```

4. **If restart doesn't work:**
   - Check database connectivity
   - Verify environment variables
   - Review recent changes
   - Rollback to previous version

---

### Database Corruption

**If database is corrupted:**

1. **Stop services:**
```bash
docker-compose -f docker-compose.prod.yml stop backend celery-worker
```

2. **Check database:**
```bash
docker-compose -f docker-compose.prod.yml exec postgres pg_isready
```

3. **Restore from backup:**
```bash
# Restore latest backup
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U ecvi_user ecvi < backup.sql
```

4. **Verify data:**
```bash
docker-compose -f docker-compose.prod.yml exec postgres psql -U ecvi_user -d ecvi -c "SELECT count(*) FROM companies;"
```

5. **Restart services:**
```bash
docker-compose -f docker-compose.prod.yml start backend celery-worker
```

---

### Security Incident

**If security breach is suspected:**

1. **Immediately:**
   - Disable affected user accounts
   - Review audit logs
   - Check for unauthorized access

2. **Investigation:**
```bash
# Check audit logs
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/audit/logs?action=login

# Check failed login attempts
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/security/audit/report
```

3. **Remediation:**
   - Rotate secrets (SECRET_KEY, database passwords)
   - Force password reset for affected users
   - Review and update security policies
   - Document incident

---

## Maintenance Procedures

### Database Backup

**Scheduled backups:**

```bash
# Create backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U ecvi_user ecvi > backup_$(date +%Y%m%d_%H%M%S).sql

# Compress backup
gzip backup_*.sql

# Upload to backup storage (S3, etc.)
aws s3 cp backup_*.sql.gz s3://your-backup-bucket/
```

**Automated backup script:**

```bash
#!/bin/bash
# backup.sh
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U ecvi_user ecvi > $BACKUP_FILE
gzip $BACKUP_FILE
aws s3 cp ${BACKUP_FILE}.gz s3://your-backup-bucket/
rm ${BACKUP_FILE}.gz
```

---

### Database Migration

**Run migrations:**

```bash
# Docker
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Kubernetes
kubectl exec -it deployment/backend -n ecvi -- alembic upgrade head
```

**Rollback migration:**

```bash
# Rollback one version
docker-compose -f docker-compose.prod.yml exec backend alembic downgrade -1

# Rollback to specific version
docker-compose -f docker-compose.prod.yml exec backend alembic downgrade <revision>
```

---

### Service Update

**Deploy new version:**

```bash
# Docker
docker-compose -f docker-compose.prod.yml build backend
docker-compose -f docker-compose.prod.yml up -d backend

# Kubernetes
kubectl set image deployment/backend backend=your-registry/ecvi-backend:v1.1.0 -n ecvi
kubectl rollout status deployment/backend -n ecvi
```

**Rollback:**

```bash
# Kubernetes
kubectl rollout undo deployment/backend -n ecvi
```

---

### Log Rotation

**Configure log rotation:**

```yaml
# docker-compose.prod.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## Escalation Procedures

### Severity Levels

**Critical (P1):**
- Service completely down
- Data loss or corruption
- Security breach

**High (P2):**
- Major feature broken
- Performance degradation
- Partial service outage

**Medium (P3):**
- Minor feature issues
- Non-critical errors
- Performance warnings

**Low (P4):**
- Cosmetic issues
- Enhancement requests
- Documentation updates

### Escalation Path

1. **On-Call Engineer** - Initial response (15 minutes)
2. **Team Lead** - If unresolved (1 hour)
3. **Engineering Manager** - For critical issues (2 hours)
4. **CTO** - For business-critical issues (4 hours)

---

## Contact Information

- **On-Call:** oncall@example.com
- **Team Lead:** team-lead@example.com
- **Engineering Manager:** eng-manager@example.com
- **Emergency:** +1-XXX-XXX-XXXX

---

**Last Updated:** 2025


# Deployment Guide
## Enterprise Company Verification Intelligence (ECVI)

**Version:** 1.0  
**Date:** 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Database Setup](#database-setup)
7. [Health Checks](#health-checks)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)

---

## Overview

ECVI can be deployed using:
- **Docker Compose** - For single-server deployments
- **Kubernetes** - For production, scalable deployments

Both methods support cloud-agnostic deployment (AWS, Azure, GCP, on-premises).

---

## Prerequisites

### Required
- Docker 20.10+ and Docker Compose 2.0+ (for Docker deployment)
- Kubernetes 1.24+ cluster (for Kubernetes deployment)
- PostgreSQL 15+ (or managed database service)
- Redis 7+ (or managed cache service)
- Domain name with DNS configured
- SSL/TLS certificates (for production)

### Optional
- Container registry (Docker Hub, ECR, GCR, ACR)
- CI/CD pipeline (GitHub Actions, GitLab CI, Jenkins)
- Monitoring tools (Prometheus, Grafana)
- Log aggregation (ELK, Loki)

---

## Docker Deployment

### Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/your-org/skyfi-ecvi.git
cd skyfi-ecvi
```

2. **Create environment file:**
```bash
cp .env.example .env.production
# Edit .env.production with your configuration
```

3. **Build and start services:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

4. **Check service status:**
```bash
docker-compose -f docker-compose.prod.yml ps
```

5. **View logs:**
```bash
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Environment Variables

Create a `.env.production` file with the following variables:

```bash
# Database
POSTGRES_DB=ecvi
POSTGRES_USER=ecvi_user
POSTGRES_PASSWORD=your_secure_password_here

# Redis
REDIS_PASSWORD=your_redis_password_here

# Security
SECRET_KEY=your_secret_key_minimum_32_characters_long
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# AI/ML
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
LLM_PROVIDER=openai

# Logging
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### Service URLs

After deployment:
- **Frontend:** http://localhost
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/docs

### Database Migrations

Migrations run automatically on backend startup. To run manually:

```bash
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### Scaling Services

Scale backend workers:
```bash
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

Scale Celery workers:
```bash
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=2
```

---

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.24+)
- `kubectl` configured
- Container registry access
- Ingress controller (nginx, traefik, etc.)

### Step 1: Build and Push Images

```bash
# Build backend image
cd backend
docker build -t your-registry/ecvi-backend:latest .
docker push your-registry/ecvi-backend:latest

# Build frontend image
cd ../frontend
docker build -t your-registry/ecvi-frontend:latest .
docker push your-registry/ecvi-frontend:latest
```

### Step 2: Update Image References

Edit Kubernetes manifests to use your registry:
```bash
# In k8s/backend.yaml and k8s/celery-worker.yaml
image: your-registry/ecvi-backend:latest

# In k8s/frontend.yaml
image: your-registry/ecvi-frontend:latest
```

### Step 3: Create Secrets

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets (update secret.yaml.example first)
kubectl create secret generic ecvi-secrets \
  --from-file=k8s/secret.yaml \
  -n ecvi
```

### Step 4: Deploy Services

```bash
# Deploy in order
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/celery-worker.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/ingress.yaml
```

### Step 5: Verify Deployment

```bash
# Check pods
kubectl get pods -n ecvi

# Check services
kubectl get svc -n ecvi

# Check ingress
kubectl get ingress -n ecvi

# View logs
kubectl logs -f deployment/backend -n ecvi
```

### Rolling Updates

```bash
# Update backend
kubectl set image deployment/backend backend=your-registry/ecvi-backend:v1.1.0 -n ecvi

# Monitor rollout
kubectl rollout status deployment/backend -n ecvi

# Rollback if needed
kubectl rollout undo deployment/backend -n ecvi
```

---

## Environment Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | JWT secret key (min 32 chars) | `your-secret-key-here` |
| `REDIS_URL` | Redis connection string | `redis://:pass@host:6379/0` |
| `CORS_ORIGINS` | Allowed CORS origins | `https://app.yourdomain.com` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `LLM_PROVIDER` | LLM provider (openai/anthropic) | `openai` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `RATE_LIMIT_ENABLED` | Enable rate limiting | `true` |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | Rate limit threshold | `60` |

---

## Database Setup

### Initial Setup

1. **Create database:**
```sql
CREATE DATABASE ecvi;
CREATE USER ecvi_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ecvi TO ecvi_user;
```

2. **Run migrations:**
```bash
# Docker
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Kubernetes
kubectl exec -it deployment/backend -n ecvi -- alembic upgrade head
```

### Backup and Restore

**Backup:**
```bash
# Docker
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U ecvi_user ecvi > backup.sql

# Kubernetes
kubectl exec -it deployment/postgres -n ecvi -- pg_dump -U ecvi_user ecvi > backup.sql
```

**Restore:**
```bash
# Docker
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U ecvi_user ecvi < backup.sql

# Kubernetes
kubectl exec -i deployment/postgres -n ecvi -- psql -U ecvi_user ecvi < backup.sql
```

---

## Health Checks

### Backend Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
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
```

Response: `healthy`

### Kubernetes Health Checks

Health checks are configured in deployment manifests:
- **Liveness Probe:** Restarts container if unhealthy
- **Readiness Probe:** Removes from load balancer if not ready

---

## Monitoring

### Application Metrics

- **Health endpoint:** `/health`
- **Metrics endpoint:** `/api/v1/metrics` (Prometheus format)

See [MONITORING.md](MONITORING.md) for detailed monitoring setup and configuration.

### Log Aggregation

**Docker:**
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

**Kubernetes:**
```bash
kubectl logs -f deployment/backend -n ecvi
```

### Resource Monitoring

**Kubernetes:**
```bash
# CPU and memory usage
kubectl top pods -n ecvi

# HPA status
kubectl get hpa -n ecvi
```

---

## Troubleshooting

### Backend Won't Start

1. **Check logs:**
```bash
docker-compose -f docker-compose.prod.yml logs backend
```

2. **Verify database connection:**
```bash
docker-compose -f docker-compose.prod.yml exec backend python -c "from app.db.database import engine; engine.connect()"
```

3. **Check environment variables:**
```bash
docker-compose -f docker-compose.prod.yml exec backend env | grep DATABASE
```

### Database Migration Issues

1. **Check migration status:**
```bash
docker-compose -f docker-compose.prod.yml exec backend alembic current
```

2. **Rollback migration:**
```bash
docker-compose -f docker-compose.prod.yml exec backend alembic downgrade -1
```

### Redis Connection Issues

1. **Test Redis connection:**
```bash
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
```

2. **Check Redis password:**
```bash
docker-compose -f docker-compose.prod.yml exec redis redis-cli -a your_password ping
```

### High Memory Usage

1. **Check resource limits:**
```bash
# Docker
docker stats

# Kubernetes
kubectl top pods -n ecvi
```

2. **Scale services:**
```bash
# Docker
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Kubernetes
kubectl scale deployment backend --replicas=3 -n ecvi
```

---

## Production Checklist

- [ ] Environment variables configured
- [ ] Secrets properly secured (not in code)
- [ ] Database backups configured
- [ ] SSL/TLS certificates installed
- [ ] CORS origins restricted
- [ ] Rate limiting enabled
- [ ] Health checks configured
- [ ] Monitoring and alerting set up
- [ ] Log aggregation configured
- [ ] Backup and restore procedures tested
- [ ] Disaster recovery plan documented
- [ ] Security audit completed

---

## Support

For deployment issues:
1. Check logs: `docker-compose logs` or `kubectl logs`
2. Review health checks: `/health` endpoint
3. Verify environment variables
4. Check database and Redis connectivity
5. Review monitoring dashboards

---

**Last Updated:** 2025


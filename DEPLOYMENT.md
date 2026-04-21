# AI Finance Assistant - Deployment Guide

> **For EU Companies**: Complete guide to deploy AI Finance Assistant to production, including Docker, cloud hosting, CI/CD, and GDPR compliance.

---

## Table of Contents
1. [Deployment Overview](#deployment-overview)
2. [Docker Containerization](#docker-containerization)
3. [Local Docker Deployment](#local-docker-deployment)
4. [Cloud Deployment Options](#cloud-deployment-options)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Production Configuration](#production-configuration)
7. [Monitoring & Logging](#monitoring--logging)
8. [EU Compliance & Security](#eu-compliance--security)
9. [Scaling & Performance](#scaling--performance)
10. [Rollback Procedures](#rollback-procedures)

---

## Deployment Overview

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                        CDN / Load Balancer                  │
│                      (Cloudflare/AWS CloudFront)            │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │ Frontend │    │ Frontend │    │ Frontend │
    │Docker 1  │    │Docker 2  │    │Docker 3  │
    │(Nginx)   │    │(Nginx)   │    │(Nginx)   │
    └────┬────┘    └────┬────┘    └────┬────┘
         │              │              │
         └──────────────┼──────────────┘
                        │
         ┌──────────────┼──────────────┐
         │                             │
    ┌────▼──────────────┐      ┌──────▼────────────┐
    │  API Load Balancer │      │  WebSocket LB     │
    │   (AWS ALB)        │      │  (Sticky Sessions)│
    └────┬──────────────┘      └──────┬────────────┘
         │                             │
    ┌────┴──────────────┬──────────────┴────┐
    │                   │                   │
┌───▼──────┐    ┌──────▼───┐    ┌──────────▼──┐
│ Backend  │    │ Backend  │    │ Background  │
│ Pod 1    │    │ Pod 2    │    │ Worker      │
│(FastAPI) │    │(FastAPI) │    │ (Celery)    │
└───┬──────┘    └──────┬───┘    └──────────┬──┘
    │                  │                   │
    └──────────────────┼───────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼──┐   ┌────▼──┐   ┌─────▼────┐
    │Chroma │   │ Redis │   │PostgreSQL│
    │  DB   │   │ Cache │   │  (Logs)  │
    └───────┘   └───────┘   └──────────┘
```

### Deployment Strategies

| Strategy | Best For | Downtime | Complexity |
|----------|----------|----------|-----------|
| **Blue-Green** | Zero-downtime updates | None | Medium |
| **Canary** | Safe rollouts (5% → 100%) | None | High |
| **Rolling** | Gradual replacement | Minimal | Low |
| **Recreate** | Development/testing | Yes | Low |

**Recommendation for EU**: Use **Blue-Green** for critical production, **Rolling** for staging.

---

## Docker Containerization

### Backend Dockerfile

Create `Dockerfile` in project root:

```dockerfile
# Multi-stage build to minimize image size
FROM python:3.11-slim as builder

WORKDIR /tmp

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final runtime image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY src/ ./src/
COPY config.yaml .
COPY run_api.py .

# Set PATH to use local pip packages
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Install serve to run production build
RUN npm install -g serve

# Copy built application from builder
COPY --from=builder /app/dist ./dist

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Change ownership
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/health || exit 1

# Serve the application
CMD ["serve", "-s", "dist", "-l", "3000"]
```

### Docker Compose Configuration

Create `docker-compose.yml` for complete stack:

```yaml
version: '3.8'

services:
  # PostgreSQL for persistent data
  postgres:
    image: postgres:15-alpine
    container_name: finance_postgres
    environment:
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-secure_password}
      POSTGRES_DB: ${DB_NAME:-finance_ai}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - finance_network

  # Redis for caching and sessions
  redis:
    image: redis:7-alpine
    container_name: finance_redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - finance_network

  # Chroma Vector Database
  chroma:
    image: ghcr.io/chroma-core/chroma:latest
    container_name: finance_chroma
    environment:
      IS_PERSISTENT: "TRUE"
      PERSIST_DIRECTORY: /chroma/data
      ALLOW_RESET: "FALSE"
    volumes:
      - chroma_data:/chroma/data
    ports:
      - "8001:8000"
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/api/v1/heartbeat || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - finance_network

  # Backend API
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: finance_backend
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      chroma:
        condition: service_healthy
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      GOOGLE_API_KEY: ${GOOGLE_API_KEY}
      DB_HOST: postgres
      DB_PORT: 5432
      DB_USER: ${DB_USER:-postgres}
      DB_PASSWORD: ${DB_PASSWORD:-secure_password}
      DB_NAME: ${DB_NAME:-finance_ai}
      REDIS_URL: redis://redis:6379
      CHROMA_HOST: chroma
      CHROMA_PORT: 8000
      ENVIRONMENT: ${ENVIRONMENT:-production}
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
    volumes:
      - ./src:/app/src
      - ./config.yaml:/app/config.yaml
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    networks:
      - finance_network

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: finance_frontend
    depends_on:
      - backend
    environment:
      VITE_API_URL: ${VITE_API_URL:-http://localhost:8000}
    ports:
      - "3000:3000"
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    networks:
      - finance_network

volumes:
  postgres_data:
  redis_data:
  chroma_data:

networks:
  finance_network:
    driver: bridge
```

---

## Local Docker Deployment

### Prerequisites
- Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop))
- Docker Compose included with Docker Desktop

### Build & Run Locally

```bash
# Navigate to project root
cd ai_finance_assistant

# Create .env.docker file with production settings
cat > .env.docker << EOF
OPENAI_API_KEY=sk-your-key-here
GOOGLE_API_KEY=your-key-here
DB_USER=postgres
DB_PASSWORD=your-secure-password
ENVIRONMENT=production
LOG_LEVEL=INFO
VITE_API_URL=http://localhost:8000
EOF

# Build images
docker-compose build

# Start all services
docker-compose up -d

# Watch logs
docker-compose logs -f

# Verify all services are healthy
docker-compose ps

# Stop services
docker-compose down
```

### Health Checks

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check database
docker exec finance_postgres psql -U postgres -d finance_ai -c "SELECT 1;"

# View logs
docker-compose logs backend
docker-compose logs frontend
```

---

## Cloud Deployment Options

### Option 1: AWS ECS (Recommended for EU)

**Setup:**
```bash
# Install AWS CLI and configure credentials
aws configure  # Use eu-west-1 for Ireland region

# Create ECR repositories
aws ecr create-repository --repository-name finance-ai-backend --region eu-west-1
aws ecr create-repository --repository-name finance-ai-frontend --region eu-west-1

# Build and push images
docker build -t 123456789.dkr.ecr.eu-west-1.amazonaws.com/finance-ai-backend:latest .
docker push 123456789.dkr.ecr.eu-west-1.amazonaws.com/finance-ai-backend:latest

# Create ECS cluster, task definitions, and services via AWS Console or Terraform
```

**Terraform Example (aws.tf):**
```hcl
provider "aws" {
  region = "eu-west-1"
}

# ECS Cluster
resource "aws_ecs_cluster" "finance" {
  name = "finance-ai-cluster"
}

# Task Definition
resource "aws_ecs_task_definition" "backend" {
  family                   = "finance-ai-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  
  container_definitions = jsonencode([{
    name      = "backend"
    image     = "123456789.dkr.ecr.eu-west-1.amazonaws.com/finance-ai-backend:latest"
    essential = true
    portMappings = [{
      containerPort = 8000
      hostPort      = 8000
      protocol      = "tcp"
    }]
  }])
}

# ECS Service
resource "aws_ecs_service" "backend" {
  name            = "finance-ai-backend-service"
  cluster         = aws_ecs_cluster.finance.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 2
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets         = var.subnet_ids
    security_groups = [aws_security_group.backend.id]
  }
}
```

### Option 2: Railway (Simplest for Startups)

**Setup:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Create project
railway init

# Deploy
railway up

# View logs
railway logs
```

### Option 3: Heroku (Legacy, EU Data)

```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login

# Create app
heroku create finance-ai --region eu

# Set environment variables
heroku config:set OPENAI_API_KEY=sk-...

# Deploy via git
git push heroku main

# View logs
heroku logs --tail
```

### Option 4: DigitalOcean App Platform

1. Push code to GitHub
2. Connect GitHub repository to DigitalOcean
3. Create new App from repository
4. Configure environment variables
5. Deploy (automatic on every git push)

---

## CI/CD Pipeline

### GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run tests
        run: |
          pytest tests/ -v --cov=src --cov-report=xml
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
  
  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push backend
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:latest
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:buildcache,mode=max
      
      - name: Build and push frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:latest
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to AWS ECS
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          # Update ECS task definition
          aws ecs update-service \
            --cluster finance-ai-cluster \
            --service finance-ai-backend-service \
            --force-new-deployment \
            --region eu-west-1
```

---

## Production Configuration

### Environment Variables

Create `.env.production`:

```env
# API Configuration
OPENAI_API_KEY=${OPENAI_KEY_PROD}
GOOGLE_API_KEY=${GOOGLE_KEY_PROD}

# Server
ENVIRONMENT=production
LOG_LEVEL=WARNING
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Database (RDS/PostgreSQL)
DB_HOST=rds.eu-west-1.rds.amazonaws.com
DB_PORT=5432
DB_USER=admin
DB_PASSWORD=${DB_PASSWORD_PROD}
DB_NAME=finance_ai_prod

# Cache
REDIS_URL=redis://redis.prod.example.com:6379

# Chroma
CHROMA_HOST=chroma.prod.example.com
CHROMA_PORT=8000

# CORS (Update for production domain)
CORS_ORIGINS=["https://app.financeai.eu","https://api.financeai.eu"]

# Frontend
VITE_API_URL=https://api.financeai.eu

# Security
SECURE_COOKIES=true
ALLOWED_HOSTS=["app.financeai.eu","api.financeai.eu"]
```

### Security Hardening

```python
# In src/core/config.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.https import HTTPSMiddleware

app.add_middleware(HTTPSMiddleware)  # Enforce HTTPS
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.allowed_hosts
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Add rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Add request ID tracking for EU audit logs
@app.middleware("http")
async def add_request_id(request, call_next):
    request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

---

## Monitoring & Logging

### Structured Logging with DataDog/ELK

```python
# src/utils/logging.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
    return logger

logger = setup_logging()

# Use in code
logger.info("Chat request", extra={
    "user_id": user.id,
    "message_length": len(message),
    "response_time": elapsed_time
})
```

### Prometheus Metrics

```python
# src/api/metrics.py
from prometheus_client import Counter, Histogram, generate_latest

chat_requests = Counter('chat_requests_total', 'Total chat requests')
response_time = Histogram('response_time_seconds', 'Response time in seconds')
rag_retrievals = Counter('rag_retrievals_total', 'RAG document retrievals')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### CloudWatch Integration (AWS)

```python
import watchtower
import logging

logger = logging.getLogger(__name__)
logger.addHandler(watchtower.CloudWatchLogHandler(
    log_group='finance-ai-logs',
    stream_name='backend'
))
```

---

## EU Compliance & Security

### GDPR Data Protection

**1. User Consent Management:**
```python
# Before processing user data
if not user.gdpr_consent:
    raise HTTPException(status_code=403, detail="GDPR consent required")

# Log all data processing
audit_log.info("Process user portfolio", user_id=user.id, timestamp=now())
```

**2. Data Deletion (Right to be Forgotten):**
```python
@app.delete("/api/user/{user_id}")
async def delete_user_data(user_id: str, token: str = Depends(verify_jwt)):
    """Delete all user data as per GDPR Article 17"""
    # Delete from PostgreSQL
    await db.users.delete(user_id)
    # Delete from Chroma (if personalized documents)
    await vector_db.delete(user_id)
    # Delete from logs (within retention period)
    await log_service.anonymize(user_id)
    
    return {"status": "User data deleted"}
```

**3. Data Encryption:**
```bash
# In Docker Compose - enable encryption at rest
postgres:
  environment:
    POSTGRES_INITDB_ARGS: "-c shared_preload_libraries=pgcrypto"
```

### PCI DSS Compliance (Payment Data)

- Never store credit card data - use Stripe/PayPal
- Encrypt all data in transit (TLS 1.2+)
- Regular security audits and penetration testing
- Maintain audit logs for 7 years (EU requirement)

### Privacy Shield & Data Residency

```yaml
# Ensure data stays in EU
# Use eu-west-1 (Ireland) region for AWS
# Use GDPR-compliant LLM providers:
# - Mistral AI (France)
# - Aleph Alpha (Germany)
# - LocalAI (self-hosted, on-premises)
```

### Penetration Testing Checklist

- [ ] SQL injection protection (use parameterized queries)
- [ ] XSS prevention (sanitize user input, CSP headers)
- [ ] CSRF token validation
- [ ] Rate limiting on API endpoints
- [ ] Authentication/authorization tests
- [ ] API key rotation procedures
- [ ] Secrets management (AWS Secrets Manager/HashiCorp Vault)

---

## Scaling & Performance

### Database Optimization

```sql
-- Create indexes for frequently queried fields
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_portfolios_user_id ON portfolios(user_id);

-- Use connection pooling
-- In production: use PgBouncer or AWS RDS Proxy
```

### Caching Strategy

```python
# Redis cache for RAG retrieval
from redis import Redis

cache = Redis(host='redis', port=6379, decode_responses=True)

@app.get("/api/market/{symbol}")
async def get_market_data(symbol: str):
    # Check cache first (5 minute TTL)
    cached = cache.get(f"market:{symbol}")
    if cached:
        return json.loads(cached)
    
    # Fetch from API
    data = await fetch_market_data(symbol)
    cache.setex(f"market:{symbol}", 300, json.dumps(data))
    return data
```

### Load Balancing Configuration

**AWS ALB Health Check:**
```hcl
resource "aws_lb_target_group" "backend" {
  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    interval            = 30
    path                = "/health"
    matcher             = "200"
  }
}
```

### Auto-Scaling

```hcl
resource "aws_autoscaling_group" "backend" {
  name                = "backend-asg"
  vpc_zone_identifier = var.subnet_ids
  max_size            = 10
  min_size            = 2
  desired_capacity    = 3
  launch_configuration = aws_launch_configuration.backend.id

  tag {
    key                 = "Name"
    value               = "finance-ai-backend"
    propagate_at_launch = true
  }
}

resource "aws_autoscaling_policy" "scale_up" {
  name                   = "backend-scale-up"
  autoscaling_group_name = aws_autoscaling_group.backend.name
  adjustment_type        = "ChangeInCapacity"
  scaling_adjustment     = 1
  cooldown               = 300
}
```

---

## Rollback Procedures

### Blue-Green Deployment Strategy

```bash
# Step 1: Deploy to GREEN environment
docker-compose -f docker-compose.green.yml up -d

# Step 2: Test GREEN environment
./scripts/smoke_tests.sh http://green.prod.example.com

# Step 3: Switch traffic to GREEN
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:... \
  --attributes Key=deregistration_delay.timeout_seconds,Value=30

# Step 4: If issues, switch back to BLUE
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch file://switch-to-blue.json

# Step 5: Scale down GREEN
docker-compose -f docker-compose.green.yml down
```

### Database Migration Rollback

```bash
# Keep database backup before migration
pg_dump postgres://user:pass@prod-db/finance_ai > backup_$(date +%s).sql

# If migration fails
psql postgres://user:pass@prod-db/finance_ai < backup_TIMESTAMP.sql

# Update application to previous code version
git checkout v1.2.0
docker build -t backend:v1.2.0 .
docker-compose up -d
```

---

## Monitoring Dashboard (Grafana)

Create `docker-compose.monitoring.yml`:

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}

volumes:
  prometheus_data:
  grafana_data:
```

**Key Metrics to Monitor:**
- API response time (p50, p95, p99)
- Error rate (4xx, 5xx responses)
- Database connection pool utilization
- RAG retrieval latency
- LLM API cost per request
- Vector database query time

---

## Deployment Checklist

- [ ] All tests passing locally
- [ ] Environment variables configured
- [ ] Database migrations tested
- [ ] Docker images built and tested
- [ ] CORS origins configured for production
- [ ] SSL/TLS certificates installed
- [ ] Monitoring and logging configured
- [ ] Backup and recovery plan documented
- [ ] Security audit completed
- [ ] GDPR compliance verified
- [ ] Performance load testing passed
- [ ] Runbooks and incident response documented
- [ ] Team trained on deployment procedures

---

## Support & Resources

- **Docker**: https://docs.docker.com/
- **AWS ECS**: https://docs.aws.amazon.com/ecs/
- **Terraform**: https://www.terraform.io/docs
- **GitHub Actions**: https://docs.github.com/en/actions

---

**Last Updated**: 2025 | **For**: EU Companies & Remote Developers

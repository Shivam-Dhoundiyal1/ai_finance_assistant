# AI Finance Assistant - Deployment Guide

> Complete guide to deploy AI Finance Assistant to production, including Docker and cloud hosting options.

---

## Table of Contents
1. [Deployment Overview](#deployment-overview)
2. [Docker Containerization](#docker-containerization)
3. [Local Docker Deployment](#local-docker-deployment)
4. [Cloud Deployment Options](#cloud-deployment-options)
5. [Production Configuration](#production-configuration)
6. [Monitoring & Logging](#monitoring--logging)

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
│Docker 1  │    │Docker 2  │    │ Workers    │
│(FastAPI) │    │(FastAPI) │    │(Celery)   │
└──────────┘    └──────────┘    └────────────┘
```

---

## Docker Containerization

### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile
```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## Local Docker Deployment

### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=postgresql://user:password@postgres:5432/finance_ai
    depends_on:
      - postgres
      - redis
      - chroma

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: finance_ai
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  chroma:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma

volumes:
  postgres_data:
  chroma_data:
```

### Run Locally
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Cloud Deployment Options

### Option 1: AWS ECS (Recommended)

**Setup:**
```bash
# Install AWS CLI and configure credentials
aws configure

# Create ECR repositories
aws ecr create-repository --repository-name finance-ai-backend
aws ecr create-repository --repository-name finance-ai-frontend

# Build and push images
docker build -t your-account.dkr.ecr.amazonaws.com/finance-ai-backend:latest .
docker push your-account.dkr.ecr.amazonaws.com/finance-ai-backend:latest

# Create ECS cluster, task definitions, and services via AWS Console or Terraform
```

**Terraform Example:**
```hcl
provider "aws" {
  region = "us-west-2"
}

# ECS Cluster
resource "aws_ecs_cluster" "finance_ai" {
  name = "finance-ai-cluster"
}

# Task Definition
resource "aws_ecs_task_definition" "backend" {
  family                   = "finance-ai-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  
  container_definitions = jsonencode([{
    name      = "backend"
    image     = "your-account.dkr.ecr.amazonaws.com/finance-ai-backend:latest"
    essential = true
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
  }])
}
```

### Option 2: Render (Simple)

**Setup:**
```bash
# Install Render CLI
npm install -g @render/cli

# Deploy backend
render deploy

# Deploy frontend
render deploy --service frontend
```

### Option 3: Railway

**Setup:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway up
```

---

## Production Configuration

### Environment Variables
```bash
# Core API
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4o-mini

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Redis
REDIS_URL=redis://host:6379

# Server
SERVER_PORT=8000
ENVIRONMENT=production

# CORS (Update for production domain)
CORS_ORIGINS=["https://yourdomain.com","https://api.yourdomain.com"]

# Frontend
VITE_API_URL=https://api.yourdomain.com
```

### Security Hardening
```python
# Rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# HTTPS only in production
@app.middleware("http")
async def enforce_https(request, call_next):
    if request.headers.get("x-forwarded-proto") != "https":
        raise HTTPException(status_code=403, detail="HTTPS required")
    return await call_next(request)
```

---

## Monitoring & Logging

### Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

### Logging Configuration
```python
import logging
import sys

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log")
    ]
)
```

### Docker Health Checks
```dockerfile
# Add to Dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

---

## Deployment Checklist

Before deploying to production:

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database migrations tested
- [ ] Health checks implemented
- [ ] Monitoring and logging configured
- [ ] Backup and recovery plan documented
- [ ] Performance load testing passed
- [ ] Runbooks and incident response documented

---

**Last Updated**: 2025 | **For**: Production Deployment

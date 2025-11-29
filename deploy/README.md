# Deployment & Monitoring Guide

## 1. GitHub Actions CI/CD

The workflow defined in `.github/workflows/ci.yml` runs on each push/PR:

1. **tests** – installs dependencies, runs migrations and launches `manage.py test`.
2. **load-test** – starts a local Django server and executes the k6 scenario from `tests/perf/load_test.js`.
3. **deploy** – builds a Docker image and pushes it to GHCR (`ghcr.io/<org>/<repo>/fintrack:<sha>`) for production rollouts. The job runs only on `main`.

### Required secrets

No extra secrets are required for CI. The default `GITHUB_TOKEN` is enough for GHCR pushes. Add any deployment-related secrets (e.g. cloud credentials) later if needed.

## 2. Container image

The root `Dockerfile` packages FinTrack with Gunicorn. Build locally:

```bash
docker build -t fintrack:dev .
docker run -p 8000:8000 --env DJANGO_SECRET_KEY=dev-key fintrack:dev
```

`docker-compose.yml` offers a quick local stack:

```bash
docker compose up --build
```

Provide the required environment variables via a `.env` file or your shell (`DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DATABASE_URL`, etc.).

## 3. Render deployment example

`deploy/render.yaml` can be imported into Render:

```yaml
services:
  - type: web
    name: fintrack
    env: docker
    plan: starter
    dockerfilePath: ./Dockerfile
    envVars:
      - key: DJANGO_SECRET_KEY
        sync: false
      - key: DJANGO_ALLOWED_HOSTS
        value: your-domain.onrender.com
      - key: DJANGO_DEBUG
        value: "False"
      - key: DATABASE_URL
        sync: false
```

Render (or any Docker-compatible PaaS) will pull the GHCR image built by GitHub Actions and run migrations via a deploy hook.

## 4. Monitoring & Metrics

### Health Check Endpoint

`/health/` – lightweight JSON health check (used in load tests and uptime monitoring).

Response format:
```json
{
  "status": "ok",
  "database": "ok",
  "timestamp": "2025-11-28T12:00:00Z",
  "detail": "healthy"
}
```

### Prometheus Metrics Endpoint

`/metrics/` – Prometheus-compatible metrics endpoint exposing:

**HTTP Metrics:**
- `fintrack_request_latency_seconds` (Histogram) – Request latency by method and path
- `fintrack_request_total` (Counter) – Total requests by method, path, and status code

**Business Metrics:**
- `fintrack_active_sessions` (Gauge) – Number of authenticated Django sessions
- `fintrack_active_clients` (Gauge) – Number of active clients
- `fintrack_premium_clients` (Gauge) – Number of premium clients
- `fintrack_basic_clients` (Gauge) – Number of basic clients

### Prometheus Configuration

Add FinTrack to your `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'fintrack'
    scheme: https  # or http for local development
    metrics_path: '/metrics/'
    static_configs:
      - targets: ['fintrack.example.com']  # Replace with your domain
    scrape_interval: 30s
    scrape_timeout: 10s
```

For local development:
```yaml
  - job_name: 'fintrack-local'
    scheme: http
    metrics_path: '/metrics/'
    static_configs:
      - targets: ['localhost:8000']
```

### Grafana Dashboard Setup

1. **Add Prometheus as Data Source:**
   - Go to Configuration → Data Sources → Add data source
   - Select Prometheus
   - Enter your Prometheus URL (e.g., `http://prometheus:9090`)

2. **Create Dashboard:**

   **Request Latency Panel:**
   ```promql
   histogram_quantile(0.95, rate(fintrack_request_latency_seconds_bucket[5m]))
   ```

   **Request Rate Panel:**
   ```promql
   rate(fintrack_request_total[5m])
   ```

   **Error Rate Panel:**
   ```promql
   rate(fintrack_request_total{status_code=~"5.."}[5m])
   ```

   **Active Clients Panel:**
   ```promql
   fintrack_active_clients
   ```

   **Premium vs Basic Clients:**
   ```promql
   fintrack_premium_clients
   fintrack_basic_clients
   ```

3. **Example Dashboard JSON:**
   Save this as `grafana-dashboard.json` and import into Grafana:

   ```json
   {
     "dashboard": {
       "title": "FinTrack Metrics",
       "panels": [
         {
           "title": "Request Latency (p95)",
           "targets": [{
             "expr": "histogram_quantile(0.95, rate(fintrack_request_latency_seconds_bucket[5m]))"
           }]
         },
         {
           "title": "Request Rate",
           "targets": [{
             "expr": "rate(fintrack_request_total[5m])"
           }]
         },
         {
           "title": "Active Clients",
           "targets": [{
             "expr": "fintrack_active_clients"
           }]
         }
       ]
     }
   }
   ```

### Logging

Application logs are written to stdout/stderr and can be collected by:
- **Docker logs:** `docker logs <container-id>`
- **Kubernetes:** Use Fluentd/Fluent Bit to forward to ELK stack
- **Cloud platforms:** Most PaaS services (Render, Heroku, etc.) automatically collect stdout logs

For centralized logging with ELK:
1. Configure Logstash to collect from your deployment
2. Use Filebeat or similar to forward logs to Elasticsearch
3. Create Kibana dashboards for log analysis

## 5. Load testing workflow

`tests/perf/load_test.js` defines a short ramp-up/ramp-down scenario against `/health/`. Run locally with Docker:

```bash
docker run --rm -i -e BASE_URL=http://host.docker.internal:8000 \
  -v "$(pwd)/tests/perf:/scripts" grafana/k6 run /scripts/load_test.js
```

Tune the `options` block to match production SLAs or longer stress tests.


# Go Feature Service Layout

This guide explains the structure of the Go feature service, how to work with it locally, and how to deploy it via Docker and Helm. Keep it handy when onboarding or when you need a refresher on the moving parts.

## Table of Contents

1. [Service Overview](#service-overview)
2. [Repository Layout](#repository-layout)
3. [Getting Started](#getting-started)
4. [Docker Image](#docker-image)
5. [Helm Chart Layout](#helm-chart-layout)
6. [Deployment](#deployment)
7. [Future Enhancements](#future-enhancements)

## Service Overview

The `go-microservice` project exposes feature-related APIs. It separates HTTP handling, business logic, and persistence behind clear boundaries so that backing implementations (in-memory or Postgres) can be swapped with minimal friction.

### Mental Model

- `handlers` process HTTP/JSON and depend only on `services.FeatureService`.
- `services` contain domain logic plus persistence abstractions.
- `models` are pure domain structs; no transport/storage details leak in.
- `cmd/server` is the composition root that selects the persistence backend, wires the router, and configures probes.

## Repository Layout

```
go-microservice/
  cmd/server/main.go              → entrypoint (wiring, HTTP server, mode switch)
  internal/models/feature.go      → domain model (Feature struct, enums)
  internal/services/
    interface.go                  → FeatureService interface + shared errors
    feature_service_inmemory.go   → in-memory implementation (local/dev)
    feature_service_postgres.go   → Postgres implementation (K8s/prod-ish)
  internal/handlers/feature_handler.go
                                  → HTTP layer (routes + JSON)
  pkg/logger                      → placeholder for shared logging utils
  Dockerfile                      → container image for deployment
  go.mod / go.sum                 → module + dependencies
feature-service-chart/            → Helm chart (see section below)
```

## Getting Started

### Prerequisites

- Go 1.21+ (matching `go.mod`)
- Docker (optional, for container builds)
- kubectl, Helm, MicroK8s/kind/minikube (for Kubernetes deployment)

### Local Development Workflow

```bash
# Install/clean up dependencies
go mod tidy

# Run the HTTP server (defaults to in-memory backend)
go run ./cmd/server

# Execute the unit/integration tests
go test ./...
```

### Build and Test the Docker Image

```bash
# Build
docker build -t rammurthymalisetti/feature-service:<tag> .

# Optional: run the container locally
docker run --rm -p 8080:8080 rammurthymalisetti/feature-service:<tag>

# Push the image (requires registry auth)
docker push rammurthymalisetti/feature-service:<tag>
```

## Docker Image

- The `Dockerfile` in the repo root produces a minimal container suitable for Kubernetes.
- Tag images consistently (`<registry>/<repo>/feature-service:<tag>`), then push to your registry of choice before deploying.

## Helm Chart Layout

```
feature-service-chart/
  Chart.yaml                      → chart metadata
  values.yaml                     → default config (image, resources, probes, Postgres)
  prod-values.yaml                → environment-specific overrides (prod)
  stage-values.yaml               → environment-specific overrides (stage)
  templates/
    deployment.yaml               → app Deployment (env, probes, image, replicas)
    service.yaml                  → app Service (NodePort/ClusterIP)
    postgres-statefulset.yaml     → Postgres DB pod (StatefulSet, emptyDir)
    postgres-service.yaml         → Postgres ClusterIP service
    postgres-secret.yaml          → DB creds + `DATABASE_URL` for the app
    postgres-configmap.yaml       → `init.sql` seed for schema
    _helpers.tpl                  → naming helpers (e.g., DB URL)
```

### Helm Mental Model

- The chart deploys both the stateless Go app and the stateful Postgres DB.
- `DATABASE_URL` is injected via a Secret into the Deployment to link the app to the DB.
- K8s Service names provide DNS wiring inside the cluster.
- `init.sql` in the ConfigMap bootstraps the schema on first DB start.

## Deployment

### Install/Upgrade with Helm

```bash
microk8s helm upgrade feature-service ./feature-service-chart \
  --namespace feature-service \
  --install
```

Use `-f prod-values.yaml` or `-f stage-values.yaml` for environment-specific overrides, and ensure the referenced Docker image/tag is already available in your registry.

### What the Chart Installs

- Go application `Deployment` with readiness/liveness probes
- `StatefulSet` for Postgres with persistent storage (or `emptyDir` as configured)
- ClusterIP `Service` objects for the app and the database
- Secrets & ConfigMaps carrying credentials, connection strings, and `init.sql`
- Environment variable wiring so the app reads `DATABASE_URL` from the Secret

### Verify

```bash
kubectl get pods -n feature-service
kubectl logs -n feature-service deploy/feature-service
kubectl port-forward svc/feature-service 8080:80
```

## Future Enhancements

These experiments help evolve the service, roughly in order of impact:

1. **Tests**
   - Add unit tests for `PostgresFeatureService` (backed by a test DB or container).
   - Add handler tests via `httptest` using the in-memory service for fast feedback.
2. **Metrics & Logging**
   - Expose `/metrics` with the Prometheus Go client.
   - Record request counters, DB latency histograms, and structured logs using `slog` or `zap`.
3. **Ingress**
   - Configure an NGINX Ingress (e.g., on MicroK8s) for host/path routing.
   - Target URLs like `http://features.local/api/v1/features`.
4. **CI/CD**
   - GitHub Actions workflow to build/test, publish the image, and run `helm upgrade` (or push via ArgoCD).
5. **Additional Services**
   - Add a second microservice (e.g., `go-microservice-auth/`) and start with REST communication before moving to gRPC.

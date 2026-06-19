# Kubernetes — Evaluation Scaffold

**Status:** PARTIAL — minimal Deployment + Service manifest provided; not wired to CI or production cluster.

## Files

| File | Purpose |
|------|---------|
| `onboarding-api-deployment.yaml` | Deployment + Service for FastAPI |

## Apply (local cluster required)

```bash
# Build image first
docker build -t onboarding-api:local services/onboarding-api

# kind/minikube example
kubectl apply -f infra/kubernetes/onboarding-api-deployment.yaml
kubectl port-forward svc/onboarding-api 8000:8000
curl http://localhost:8000/health
```

## Gaps

- No Postgres StatefulSet, Ingress, Helm chart, or HPA
- No CI deploy job
- Secrets placeholder only

See `docs/devops-validation.md` § Kubernetes.

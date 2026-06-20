# Kubernetes — KYC Platform

Minimal manifests for local cluster verification (kind / minikube / k3d).

## Files

| File | Resources |
|------|-----------|
| `kyc-platform.yaml` | Namespace, ConfigMap, Secret, Postgres Service + StatefulSet, Ingress |
| `onboarding-api-deployment.yaml` | API Deployment + ClusterIP Service |

## Prerequisites

- Docker (build images)
- `kubectl` and a local cluster tool (`kind`, `minikube`, or `k3d`)

```bash
# Example: install kubectl + kind to ~/.local/bin (macOS arm64)
curl -fsSL "https://dl.k8s.io/release/$(curl -fsSL https://dl.k8s.io/release/stable.txt)/bin/darwin/arm64/kubectl" -o ~/.local/bin/kubectl
curl -fsSL "https://kind.sigs.k8s.io/dl/v0.27.0/kind-darwin-arm64" -o ~/.local/bin/kind
chmod +x ~/.local/bin/kubectl ~/.local/bin/kind
```

## Up (kind example)

```bash
export PATH="$HOME/.local/bin:$PATH"
CLUSTER=kyc-local

# 1. Cluster
kind create cluster --name "$CLUSTER" --wait 120s

# 2. Images (build + load into kind node)
docker build -t onboarding-api:local services/onboarding-api
kind load docker-image onboarding-api:local --name "$CLUSTER"
# If registry pull fails inside kind (TLS), preload postgres too:
kind load docker-image postgres:16-alpine --name "$CLUSTER"

# 3. Apply (platform first, then API)
kubectl apply -f infra/kubernetes/kyc-platform.yaml
kubectl apply -f infra/kubernetes/onboarding-api-deployment.yaml

# 4. Wait for ready
kubectl -n kyc-platform wait --for=condition=ready pod -l app=postgres --timeout=180s
kubectl -n kyc-platform wait --for=condition=ready pod -l app=onboarding-api --timeout=180s

# 5. Smoke test
kubectl -n kyc-platform port-forward svc/onboarding-api 18080:8000 &
curl http://localhost:18080/health
```

## Down

```bash
kind delete cluster --name kyc-local
# Or: kubectl delete namespace kyc-platform
```

## Validate only (no cluster apply)

```bash
make k8s-verify
# Requires kubectl; uses client dry-run when cluster context is set,
# or YAML structure fallback when kubectl/kubeconform unavailable.
```

## Gaps

- No resource requests/limits on workloads
- Ingress has no `ingressClassName` / controller (port-forward used for local smoke test)
- Secret uses `stringData` placeholder (not production-safe)
- No Helm chart, HPA, or CI kind job

See `docs/beginner/D4-kubernetes/D4_REPORT.md` and `docs/devops-validation.md`.

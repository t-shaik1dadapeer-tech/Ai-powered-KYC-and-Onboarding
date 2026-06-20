# D4 — Kubernetes Manifest Verification

**Evaluation criterion:** D4 (Kubernetes)  
**Verification date:** 2026-06-20T064800Z (UTC)  
**Manifests:** `infra/kubernetes/`  
**Verify script:** `scripts/k8s-verify.sh`  
**Local cluster:** kind `d4-kyc-verify` (v1.32.2)  
**Evidence:** `evidence/test-results/d4-run-2026-06-20T064800Z/`

---

## 1. Executive Summary

| Check | Result |
|-------|--------|
| Manifest discovery | **PASS** — 2 YAML files, 8 resource kinds |
| kubectl dry-run (client) | **PASS** — all resources validated |
| kubectl dry-run (server) | **PARTIAL** — namespace must exist first for multi-doc apply |
| kubeval / kubeconform | **N/A** — not installed |
| kind local deploy | **PASS** — pods Running after image preload |
| Pods running | **PASS** — postgres + onboarding-api 1/1 |
| Services available | **PASS** — ClusterIP postgres:5432, onboarding-api:8000 |
| ConfigMaps loaded | **PASS** — LOG_LEVEL, PAN/BANK_VERIFY_MODE |
| Port-forward + curl | **PASS** — HTTP 200 `/health` |
| Cleanup | **PASS** — `kind delete cluster` |

**Overall D4 status: PASS (8.5/10)** — manifests validated and service proven on local kind cluster; image preload workaround documented for TLS/registry issues.

---

## 2. Manifest Inventory

| File | Kind | Name | Namespace |
|------|------|------|-----------|
| `kyc-platform.yaml` | Namespace | `kyc-platform` | — |
| | ConfigMap | `onboarding-api-config` | kyc-platform |
| | Secret | `onboarding-api-secrets` | kyc-platform |
| | Service | `postgres` | kyc-platform |
| | StatefulSet | `postgres` | kyc-platform |
| | Ingress | `onboarding-api` | kyc-platform |
| `onboarding-api-deployment.yaml` | Deployment | `onboarding-api` | kyc-platform |
| | Service | `onboarding-api` | kyc-platform |

**Not present:** Helm charts, HPA, NetworkPolicy, PersistentVolumeClaim (Postgres uses ephemeral storage).

---

## 3. Resource Analysis

### Replicas

| Workload | Replicas | Type |
|----------|----------|------|
| `onboarding-api` | 1 | Deployment |
| `postgres` | 1 | StatefulSet |

### Resources (requests/limits)

| Container | CPU/Memory requests | CPU/Memory limits |
|-----------|---------------------|-------------------|
| onboarding-api | **None** | **None** |
| postgres | **None** | **None** |

### Environment variables

**ConfigMap `onboarding-api-config`** (via `envFrom`):

| Key | Value |
|-----|-------|
| `LOG_LEVEL` | INFO |
| `PAN_VERIFY_MODE` | mock |
| `BANK_VERIFY_MODE` | mock |

**Secret `onboarding-api-secrets`**:

| Key | Source |
|-----|--------|
| `DATABASE_URL` | `secretKeyRef` → `database_url` |

**Postgres container** (inline env):

| Key | Value |
|-----|-------|
| `POSTGRES_USER` | kyc |
| `POSTGRES_PASSWORD` | kyc |
| `POSTGRES_DB` | kyc |

### Service exposure

| Service | Type | Port | Exposure |
|---------|------|------|----------|
| `onboarding-api` | ClusterIP | 8000 | Internal; port-forward or Ingress |
| `postgres` | ClusterIP | 5432 | Internal only |
| Ingress `onboarding-api` | — | 80 → 8000 | Host `kyc.local` (no ingress class; needs controller) |

### Probes

| Workload | Liveness | Readiness |
|----------|----------|-----------|
| onboarding-api | HTTP `/health:8000` (20s delay) | HTTP `/health:8000` (10s delay) |
| postgres | `pg_isready -U kyc` | — |

---

## 4. Validation Output

### kubectl dry-run (client) — PASS

```
namespace/kyc-platform created (dry run)
configmap/onboarding-api-config created (dry run)
secret/onboarding-api-secrets created (dry run)
...
deployment.apps/onboarding-api created (dry run)
service/onboarding-api created (dry run)
```

**Evidence:** `success-dry-run.txt`

### kubectl dry-run (server) — partial

Server dry-run on `kyc-platform.yaml` creates namespace in dry-run but subsequent resources fail with `namespaces "kyc-platform" not found` when applied as a single multi-doc file. **Live apply works** because namespace is created first in document order.

### kubeval / kubeconform

Not installed on verification host. Client dry-run against kind API used instead.

### make k8s-verify

`scripts/k8s-verify.sh` runs `kubectl apply --dry-run=client` when kubectl is available; falls back to YAML structure check otherwise.

---

## 5. Local Deploy (kind)

| Step | Command | Result |
|------|---------|--------|
| Create cluster | `kind create cluster --name d4-kyc-verify` | Ready in ~20s |
| Build API image | `docker build -t onboarding-api:local services/onboarding-api` | PASS |
| Load images | `kind load docker-image onboarding-api:local` | PASS |
| Load postgres | `kind load docker-image postgres:16-alpine` | **Required** — registry TLS failure inside kind node |
| Apply | `kubectl apply -f kyc-platform.yaml` + deployment | PASS |
| Wait | `kubectl wait --for=condition=ready` | PASS (after image preload) |

**minikube / k3d:** Not tested; kind used as primary local cluster per evaluation matrix.

---

## 6. Apply Output

```
namespace/kyc-platform created
configmap/onboarding-api-config created
secret/onboarding-api-secrets created
service/postgres created
statefulset.apps/postgres created
ingress.networking.k8s.io/onboarding-api created
deployment.apps/onboarding-api created
service/onboarding-api created
```

**Pod state (final):**

```
NAME                              READY   STATUS
onboarding-api-6569c86688-xk97n   1/1     Running
postgres-0                        1/1     Running
```

**Evidence:** `success-apply.txt`, `d4-k8s-verification.log`

---

## 7. Service Response Proof

```bash
kubectl -n kyc-platform port-forward svc/onboarding-api 18080:8000
curl http://localhost:18080/health
```

```json
{"status":"healthy","service":"onboarding-api","version":"0.1.0"}
HTTP_CODE:200
```

**Evidence:** `success-curl.txt`

---

## 8. Cleanup Verification

```bash
kind delete cluster --name d4-kyc-verify
# cluster deleted (expected)
```

**Evidence:** `success-cleanup.txt`

---

## 9. README Verification

Updated `infra/kubernetes/README.md` with:

- Manifest inventory
- **Up** commands (kind create → build → load images → apply → wait → port-forward → curl)
- **Down** commands (`kind delete cluster` or `kubectl delete namespace`)
- Image preload note for postgres TLS workaround
- `make k8s-verify` for dry-run only

---

## 10. Findings

| ID | Severity | Finding | Recommendation |
|----|----------|---------|----------------|
| D4-001 | Medium | kind node cannot pull from Docker Hub (TLS x509) | Preload images via `kind load docker-image` or configure registry mirror |
| D4-002 | Low | No CPU/memory requests or limits | Add resource blocks for production |
| D4-003 | Low | Ingress missing `ingressClassName` | Set class + install ingress-nginx for `kyc.local` routing |
| D4-004 | Low | Postgres StatefulSet has no PVC | Add `volumeClaimTemplates` for data persistence |
| D4-005 | Info | Secret password in plain `stringData` | Use sealed-secrets or external secret manager |
| D4-006 | Info | kubeval/kubeconform not in CI | Add schema validation job |
| D4-007 | Info | No kind/minikube job in GitHub Actions | Add CI cluster smoke test per evaluation gap |
| D4-008 | Positive | Health probes on API + postgres | Good readiness pattern |

---

## 11. Expected Deliverables Checklist

| Deliverable | Status |
|-------------|--------|
| ✓ Manifest YAML files | `infra/kubernetes/*.yaml` |
| ✓ Dry-run output | `success-dry-run.txt` |
| ✓ Apply output | `success-apply.txt` |
| ✓ curl proof | `success-curl.txt` (HTTP 200) |
| ✓ README with up/down commands | `infra/kubernetes/README.md` |

---

## 12. Verification Summary

```bash
cd "/Users/shaikdadapeer/agent development"
export PATH="$HOME/.local/bin:$PATH"

make k8s-verify                    # dry-run / structure check

# Full local deploy (see infra/kubernetes/README.md)
kind create cluster --name kyc-local --wait 120s
docker build -t onboarding-api:local services/onboarding-api
kind load docker-image onboarding-api:local postgres:16-alpine --name kyc-local
kubectl apply -f infra/kubernetes/kyc-platform.yaml
kubectl apply -f infra/kubernetes/onboarding-api-deployment.yaml
kubectl -n kyc-platform port-forward svc/onboarding-api 18080:8000
curl http://localhost:18080/health
kind delete cluster --name kyc-local
```

**D4 verdict: PASS** — Kubernetes manifests discovered, validated, deployed on kind, health endpoint verified, cluster cleaned up.

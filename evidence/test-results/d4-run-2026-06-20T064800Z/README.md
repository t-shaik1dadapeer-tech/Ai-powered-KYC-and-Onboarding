# D4 Kubernetes — Evidence Bundle

**Run:** 2026-06-20T064800Z  
**Report:** `docs/beginner/D4-kubernetes/D4_REPORT.md`  
**Cluster:** kind `d4-kyc-verify` (Kubernetes v1.32.2)

| File | Description |
|------|-------------|
| `d4-k8s-verification.log` | Full transcript |
| `success-dry-run.txt` | kubectl client dry-run output |
| `success-apply.txt` | Live apply + pod status |
| `success-curl.txt` | Port-forward health check (HTTP 200) |
| `success-cleanup.txt` | kind cluster teardown |

Also: `evidence/k8s-results/k8s-verify.txt` (dry-run via `make k8s-verify` when kubectl available)

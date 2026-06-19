# Safe Change Process

Run **before every PR** to avoid regressions across the polyglot monorepo.

## Gate command

```bash
make safe-change-check
```

This runs, in order:

1. `make ci-local` — lint + all 70 tests + optional Docker build
2. `scripts/terraform-verify.sh` — `terraform init`, `validate`, `apply` (local provider)
3. `scripts/k8s-verify.sh` — `kubectl apply --dry-run=client` on all manifests
4. `docker compose config` — compose syntax (when Docker is installed)
5. `scripts/load-test.sh` — 200 in-process `/pages requests, p95 < 500ms

Evidence is written to `evidence/safe-change/safe-change-check.txt`.

## Manual checklist

- [ ] Change scoped to one layer (routers → services → repos → models)
- [ ] New endpoints have tests + OpenAPI export updated (`make export-openapi`)
- [ ] If DB fixtures changed, confirm isolation (see BUG-001 in `docs/bug-investigation.md`)
- [ ] `verification/phase-N.md` updated if phase scope changed
- [ ] `make evidence-index` if new evidence artifacts added

## Rollback

```bash
git revert <commit>
make safe-change-check
```

## Related

- `CONTRIBUTING.md` — setup and layer rules
- `docs/bug-investigation.md` — BUG-001 SQLite fixture isolation
- `.github/pull_request_template.md` — PR checklist

# Contributing

## Prerequisites

- Python 3.9+
- Node.js 18+
- Rust stable (for `engines/rust-analyzer`)
- Optional: Docker Desktop

## Setup

```bash
# Single command (fresh clone)
make bootstrap

# Or step-by-step:
cd services/onboarding-api
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt pytest pytest-cov httpx

# Intelligence engine
cd engines/intelligence
python3 -m venv .venv
.venv/bin/pip install pydantic pytest pytest-cov

# Node CLI
cd clients/node-cli && npm install

# Rust
cd engines/rust-analyzer && cargo build --release
```

## Layer rules (onboarding-api)

```
routers → services → repositories → models
```

Routers must not import repositories directly.

## Commands

| Command | Purpose |
|---------|---------|
| `make bootstrap` | One-shot dev env setup (venv + npm + cargo) |
| `make test` | All 70 tests + coverage |
| `make ci-local` | Simulate GitHub Actions |
| `make lint` | _(use ci-local lint stage)_ |
| `make verify-phases` | 15 verification files |
| `make evidence-index` | Regenerate `evidence/INDEX.md` |

## Before submitting

1. `make safe-change-check` (or at minimum `make test` + `make ci-local`)
2. Update `verification/phase-N.md` if phase scope changed
3. Run `make evidence-index` if evidence artifacts changed

## Safe change

See **`docs/safe-change.md`** — mandatory gate before PRs:

```bash
make safe-change-check   # ci-local + terraform + k8s + load test
make terraform-verify    # D1 — infra/terraform/*.tf
make k8s-verify          # D4 — kubectl dry-run
make load-test           # A6 — 200 req /health p95 check
```

## Documentation

- Architecture: `docs/architecture/`
- Evaluation: `docs/evaluation-matrix.md`
- API map: `docs/api-map.md`

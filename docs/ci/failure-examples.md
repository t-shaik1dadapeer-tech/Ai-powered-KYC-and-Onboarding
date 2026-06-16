# CI Failure Examples

Documented failure modes for the GitHub Actions pipeline (`.github/workflows/ci.yml`). Use these to verify CI catches regressions and to replay failures locally.

---

## 1. Lint failure — unused Python import

**Trigger:** Add an unused import in any Python module under `engines/intelligence/src/`.

```python
import shutil  # unused
```

**Expected CI output (job: `Lint`):**

```
ruff check engines/intelligence/src engines/intelligence/tests
F401 [*] `shutil` imported but unused
Found 1 error.
```

**Local replay:**

```bash
cd engines/intelligence
.venv/bin/ruff check src tests
```

**Fix:** Remove the unused import or run `ruff check --fix`.

---

## 2. Test failure — broken API validation

**Trigger:** Relax a Pydantic validator so invalid PAN passes (e.g. remove length check).

**Expected CI output (job: `Test — onboarding-api`):**

```
FAILED tests/test_kyc.py::test_invalid_pan_rejected - assert 201 == 422
```

**Local replay:**

```bash
cd services/onboarding-api
PYTHONPATH=. .venv/bin/pytest -q
```

**Fix:** Restore validation rules; ensure unit tests cover the constraint.

---

## 3. Node CLI failure — broken validator

**Trigger:** Change `validatePhone` to accept fewer than 10 digits.

**Expected CI output (job: `Test — node-cli`):**

```
✖ validators.test.js — validatePhone rejects short numbers
```

**Local replay:**

```bash
cd clients/node-cli
npm test
```

**Fix:** Restore phone validation; keep tests aligned with API rules.

---

## 4. Rust clippy failure — unused variable

**Trigger:** Introduce `let x = 1;` without use in `engines/rust-analyzer/src/`.

**Expected CI output (job: `Lint`):**

```
error: unused variable: `x`
  = note: `-D warnings` implied by `-D warnings`
```

**Local replay:**

```bash
cd engines/rust-analyzer
cargo clippy --all-targets -- -D warnings
```

**Fix:** Prefix with `_` or remove the variable.

---

## 5. E2E failure — intelligence CLI broken

**Trigger:** Break `intelligence.cli` entry point (e.g. rename `main` without updating `__main__`).

**Expected CI output (job: `Test — platform E2E`):**

```
FAILED test_platform_e2e.py::test_e2e_intelligence_analyzes_onboarding_api
AssertionError: ... returncode != 0
```

**Local replay:**

```bash
cd services/onboarding-api
PYTHONPATH=. .venv/bin/pytest -q ../../tests/e2e/test_platform_e2e.py
```

**Fix:** Restore CLI module path and PYTHONPATH=src convention.

---

## 6. Docker build failure — missing dependency

**Trigger:** Add a Python import in `onboarding-api` without updating `requirements.txt`.

**Expected CI output (job: `Docker build`):**

```
ModuleNotFoundError: No module named 'psycopg2'
ERROR: process "/bin/sh -c pip install -r requirements.txt" did not complete successfully
```

**Local replay:**

```bash
cd infra/docker
docker compose build onboarding-api
```

**Fix:** Add the package to `services/onboarding-api/requirements.txt`.

---

## 7. CI retry / flake mitigation

| Scenario | Mitigation |
|----------|------------|
| Transient npm registry timeout | Re-run failed job in GitHub Actions |
| Rust cache cold start | `dtolnay/rust-toolchain@stable` caches via actions |
| Parallel job cancellation | `concurrency.cancel-in-progress: true` on new pushes |

---

## 8. Verifying a green pipeline locally

```bash
make ci-local
# or
bash scripts/ci-local.sh
```

Evidence written to `evidence/ci-results/phase-9-ci-local.txt`.

After pushing to GitHub, download artifacts from the Actions run:

| Artifact | Contents |
|----------|----------|
| `onboarding-api-coverage` | `coverage.xml` |
| `intelligence-coverage` | `coverage.xml` |
| `rust-analyzer-release` | release binary |
| `docker-build-evidence` | build log + resolved compose |

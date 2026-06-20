# A4 M1 Rollback — Node CLI API Key Support

Use this runbook to undo the A4 first-step modernization (CLI `X-API-Key` wiring).

## When to roll back

- Production incident traced to auth header handling in the CLI
- Need to restore pre-A4 CLI behavior while keeping server middleware unchanged

## Option A — After A4 commit is on `main` (preferred)

```bash
cd "/Users/shaikdadapeer/agent development"
git log --oneline -5   # find commit: A4: repository modernization analysis
git revert --no-edit <A4_COMMIT_SHA>
make test-node make test-api make test-e2e
git push origin main
```

## Option B — Script (revert by commit SHA)

```bash
bash scripts/modernization-rollback-m1.sh <A4_COMMIT_SHA>
```

## Option C — Restore files only (uncommitted / local)

```bash
git checkout origin/main -- \
  clients/node-cli/lib/api-client.js \
  clients/node-cli/commands/customer-create.js \
  clients/node-cli/commands/submit-kyc.js \
  clients/node-cli/bin/kyc-cli.js \
  clients/node-cli/tests/api-client.test.js \
  clients/node-cli/tests/commands.test.js \
  clients/node-cli/README.md
cd clients/node-cli && npm test
```

## Post-rollback behavior

| Server `API_KEY` | CLI behavior |
|------------------|--------------|
| Unset | No change vs pre-A4 |
| Set | CLI calls return **401** until key support is re-applied or auth disabled |

## Verification after rollback

```bash
cd clients/node-cli && npm test
make test-api test-e2e
```

Expected: Node suite returns to **17** tests (not 19).

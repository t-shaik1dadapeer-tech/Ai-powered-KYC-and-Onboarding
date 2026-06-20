# A3 Polyglot Mini-System — Evidence Bundle

**Run:** 2026-06-20T06:02:39Z  
**Report:** `docs/beginner/A3-polyglot-mini-system/A3_REPORT.md`

| File | Description |
|------|-------------|
| `a3-live-integration.log` | Full live integration transcript |
| `test-results.txt` | Consolidated test summary |
| `health.json` | API health response |
| `node-customer-create.txt` | CLI → POST /customers |
| `node-submit-kyc.txt` | CLI → POST /kyc |
| `rust-risk.json` | Rust `risk` subcommand output |
| `node-generate-report.txt` | Node → Python → Rust path |
| `report-files.txt` | Generated analysis artifacts listing |

**Analysis output:** consolidated under [`evidence/api-maps/onboarding-api/`](../../api-maps/onboarding-api/) (see `analysis-manifest.json` for `rust_scan` timing).

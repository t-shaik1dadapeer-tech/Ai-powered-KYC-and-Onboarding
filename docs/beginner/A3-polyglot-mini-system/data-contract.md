# A3 Data Contracts — Polyglot Mini-System

## Contract A: Node CLI → FastAPI (KYC)

**Transport:** HTTP/JSON  
**Client:** `clients/node-cli/lib/api-client.js`  
**Server:** `services/onboarding-api/app/routers/*`

### POST /customers

| Field (client) | Field (API) | Validation |
|----------------|---------------|------------|
| `fullName` | `full_name` | min 2 chars |
| `email` | `email` | EmailStr, lowercased |
| `phone` | `phone` | 10 digits |

**Response:** `CustomerResponse` — `id` (UUID), `status`, timestamps

### POST /kyc

| Field (client) | Field (API) | Validation |
|----------------|---------------|------------|
| `customerId` | `customer_id` | UUID |
| `pan` | `pan` | `^[A-Z]{5}[0-9]{4}[A-Z]$` |
| `accountNumber` | `account_number` | 9–18 digits |
| `ifsc` | `ifsc` | `^[A-Z]{4}0[A-Z0-9]{6}$` |

**Response:** `KycStatusResponse` — submission id, pan/bank verification status

### POST /risk-score (API-internal Python scoring)

| Request | `{ "customer_id": "<uuid>" }` |
| Response | `{ "score": int, "band": "low\|medium\|high", "factors": {...} }` |

**Note:** This risk score is computed in **Python** (`RiskScoreService`), not Rust.

---

## Contract B: Node CLI → Python Intelligence

**Transport:** subprocess (`spawnSync`)  
**Bridge:** `clients/node-cli/lib/analyzer-client.js`

```
python3 -m intelligence.cli <repo_path> -o <output_dir> --json
```

**Env:** `PYTHONPATH=src` (cwd: `engines/intelligence`)

**Stdout:** JSON summary with `repository`, `framework`, `apis`, `models`, `flow_traces`, `output_dir`

---

## Contract C: Python Intelligence → Rust Analyzer

**Transport:** subprocess  
**Bridge:** `engines/intelligence/src/intelligence/rust_bridge/cli.py`

```
rust-analyzer scan --path <repo_path>
```

**Binary discovery:** `engines/rust-analyzer/target/{release,debug}/rust-analyzer`

### Rust `ScanResult` JSON (stdout)

```json
{
  "repository": "/path",
  "file_count": 60,
  "files": [{ "path": "...", "language": "python", "imports": [], "symbols": [], "test_file": false }],
  "graph_edges": [{ "from": "a.py", "to": "b.py", "import": "app.b" }],
  "risk": {
    "score": 55,
    "band": "medium",
    "factors": { "test_ratio": 0.15, "total_files": 60 }
  },
  "scan_duration_ms": 182
}
```

### Enrichment on `AnalysisResult`

Python attaches `rust_scan` subset to manifest:

```json
{
  "file_count": 60,
  "graph_edges": 81,
  "risk": { "score": 55, "band": "medium", "factors": {} },
  "scan_duration_ms": 182
}
```

---

## Contract D: Rust `risk` subcommand (standalone)

```
rust-analyzer risk --path <repo_path>
```

Returns only the `risk` object (repository-level static analysis score, not customer KYC score).

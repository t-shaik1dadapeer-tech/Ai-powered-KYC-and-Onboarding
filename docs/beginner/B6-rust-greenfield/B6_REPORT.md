# B6 — Rust Greenfield Tool/Binary Verification

**Evaluation criterion:** B6 (Rust Greenfield)  
**Application:** `engines/rust-analyzer/`  
**Verification date:** 2026-06-20T04:55:00Z (UTC)  
**Evidence:** `evidence/test-results/b6-run-2026-06-20-1025/`  
**Machine-readable:** `cli-commands.csv`, `structure-inventory.csv`

---

## 1. Executive Summary

| Check | Result | Confidence |
|-------|--------|------------|
| Application type | **CLI binary** (not HTTP server) | Confirmed |
| Modular Rust architecture | **PASS** | Confirmed |
| Release build | **PASS** | Confirmed |
| `cargo test` | **10/10 PASS** (8 unit + 2 integration) | Confirmed |
| `scan` command on onboarding-api | **PASS** (59 files, JSON) | Confirmed |
| `risk` command | **PASS** (score 55, medium band) | Confirmed |
| Invalid path error handling | **PASS** (exit 1, JSON error) | Confirmed |
| README with build/run/test | **PASS** | Confirmed |
| Benchmark target present | **PASS** | Confirmed (not executed in this run) |

**Overall B6 status: PASS (9/10)** — production-quality Rust CLI with tests and JSON I/O.

---

## 2. Project Structure

```
engines/rust-analyzer/
├── src/
│   ├── main.rs           # CLI entry (clap)
│   ├── lib.rs            # Public API
│   ├── scan.rs           # scan_repository orchestration
│   ├── file_walker.rs    # Walkdir with skip rules
│   ├── graph/mod.rs      # Import graph edges
│   ├── parser/
│   │   ├── mod.rs
│   │   ├── python.rs     # Python AST-lite parsing
│   │   └── universal.rs  # JS/TS/generic
│   ├── risk/mod.rs       # Risk scoring
│   └── error.rs          # thiserror types
├── tests/
│   └── integration_test.rs
├── benches/
│   └── scan_benchmark.rs
├── Cargo.toml
├── Dockerfile
└── README.md
```

---

## 3. Application Discovery

| Type | Applicable |
|------|------------|
| REST/GraphQL API | No |
| CLI binary | **Yes** (`rust-analyzer`) |
| Library crate | **Yes** (`rust_analyzer` lib) |
| Worker service | No |

**Entry point:** `src/main.rs` — binary `rust-analyzer`  
**Core API:** `scan_repository(&Path) -> Result<ScanResult>` in `src/scan.rs`

---

## 4. CLI Command Inventory

| Command | Flags | Output |
|---------|-------|--------|
| `scan` | `--path <dir>`, `--pretty` (default true) | Full `ScanResult` JSON |
| `risk` | `--path <dir>` | `RiskAssessment` JSON only |

**ScanResult fields:** `repository`, `file_count`, `files[]`, `graph_edges[]`, `risk`, `scan_duration_ms`

---

## 5. Validation Analysis

| Input | Validation | Error |
|-------|------------|-------|
| `--path` | Must exist as directory | `Invalid path: Repository not found` |
| Parse failures | Skipped per-file | Scan continues |
| JSON serialization | serde | Exit 1 on failure |

---

## 6. Startup Verification

```bash
cd engines/rust-analyzer
cargo build --release    # Finished release build
cargo test               # 10 passed
```

**Evidence:** `build.txt`, `cargo-test.txt`, `execution.log`

---

## 7. Functional Verification

### scan (onboarding-api)

```bash
./target/release/rust-analyzer scan --path ../../services/onboarding-api
```

**Result:** `file_count: 59`, `risk.score: 55`, `risk.band: medium`, `scan_duration_ms` present

### risk

```bash
./target/release/rust-analyzer risk --path ../../services/onboarding-api
```

**Result:** JSON risk object with factors (`test_ratio`, `dependency_count`, etc.)

### invalid path

```bash
./target/release/rust-analyzer scan --path /nonexistent/path
```

**Result:** `{"ok":false,"error":"Invalid path: Repository not found: /nonexistent/path"}` — exit 1

**Evidence:** `scan-output.json`, `risk-output.json`, `error-output.json`

---

## 8. Test Discovery and Execution

| Suite | Tests | Framework |
|-------|-------|-----------|
| Unit (`src/**`) | 8 | `#[cfg(test)]` |
| Integration (`tests/`) | 2 | `cargo test` |
| Doc tests | 0 | — |

```bash
cd engines/rust-analyzer && cargo test -q
# 8 unit + 2 integration = 10 passed
```

---

## 9. Documentation Verification

| Section | README | Status |
|---------|--------|--------|
| Build (`cargo build --release`) | Yes | PASS |
| CLI examples (`scan`, `risk`) | Yes | PASS |
| Test (`cargo test`) | Yes | PASS |
| Benchmark | Yes | PASS |
| Output schema | Yes | PASS |
| Python integration note | Yes | PASS |

---

## 10. Code Quality Assessment

| Area | Assessment |
|------|------------|
| Architecture | Clear modules: walk → parse → graph → risk |
| Error handling | `thiserror`, JSON error on CLI failure |
| Performance | Release LTO, walkdir, criterion bench |
| Testability | Tempdir unit tests + binary integration tests |
| Security | No shell execution; path validation |

---

## 11. Findings and Recommendations

**Strengths:** Fast scan, structured JSON, integration with Python intelligence engine.

**Gaps:** No `clap` validation for relative path resolution docs; benchmark not run in this verification.

**Bugs:** None found.

---

## 12. Areas Requiring Manual Verification

| Area | Reason |
|------|--------|
| Docker image build | Dockerfile present, not executed |
| Criterion benchmark numbers | Hardware-dependent |
| Large monorepo scan time | Not profiled here |

---

## 13. Verification Summary

| Step | Command | Result |
|------|---------|--------|
| Build | `cargo build --release` | PASS |
| Tests | `cargo test` | **10/10 PASS** |
| Scan | `rust-analyzer scan --path ...` | PASS |
| Risk | `rust-analyzer risk --path ...` | PASS |
| Error path | invalid directory | PASS |

**B6 verdict: PASS**

---

*Evidence: `evidence/test-results/b6-run-2026-06-20-1025/`*

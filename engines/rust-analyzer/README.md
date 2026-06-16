# Rust Repository Analyzer

High-performance repository parser, import graph builder, and risk calculator.

## Build

```bash
cd engines/rust-analyzer
cargo build --release
```

## CLI

```bash
# Full scan (JSON)
./target/release/rust-analyzer scan --path ../../services/onboarding-api

# Risk score only
./target/release/rust-analyzer risk --path ../../services/onboarding-api
```

## Test

```bash
cargo test
```

## Benchmark

```bash
cargo run --release --bench scan_benchmark -- ../../services/onboarding-api
```

## Output Schema

```json
{
  "repository": "/path/to/repo",
  "file_count": 42,
  "files": [{ "path": "app/main.py", "language": "python", "imports": [], "symbols": [], "test_file": false }],
  "graph_edges": [{ "from": "a.py", "to": "b.py", "import": "app.b" }],
  "risk": { "score": 45, "band": "medium", "factors": {} },
  "scan_duration_ms": 12
}
```

## Integration

Python intelligence engine auto-detects `target/release/rust-analyzer` and attaches `rust_scan` to analysis results.

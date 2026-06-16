use std::path::PathBuf;
use std::process::Command;

#[test]
fn cli_scan_onboarding_api() {
    let repo = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../services/onboarding-api");
    let binary = env!("CARGO_BIN_EXE_rust-analyzer");

    let output = Command::new(binary)
        .args(["scan", "--path", repo.to_str().unwrap()])
        .output()
        .expect("failed to run rust-analyzer");

    assert!(
        output.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&output.stderr)
    );

    let json: serde_json::Value =
        serde_json::from_slice(&output.stdout).expect("invalid JSON output");
    assert!(json.get("file_count").unwrap().as_u64().unwrap() > 0);
    assert!(json.get("risk").unwrap().get("score").is_some());
}

#[test]
fn cli_rejects_invalid_path() {
    let binary = env!("CARGO_BIN_EXE_rust-analyzer");
    let output = Command::new(binary)
        .args(["scan", "--path", "/nonexistent/xyz"])
        .output()
        .unwrap();
    assert!(!output.status.success());
}

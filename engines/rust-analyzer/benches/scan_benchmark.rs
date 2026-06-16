use std::hint::black_box;
use std::path::Path;

use rust_analyzer::scan_repository;

fn main() {
    let repo = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "../../services/onboarding-api".to_string());
    let path = Path::new(&repo);

    let start = std::time::Instant::now();
    for _ in 0..5 {
        black_box(scan_repository(path).unwrap());
    }
    let elapsed = start.elapsed();
    println!("5 scans of {} in {:?}", repo, elapsed);
    println!(
        "approx {:.0} files/sec",
        scan_repository(path).unwrap().file_count as f64 / (elapsed.as_secs_f64() / 5.0)
    );
}

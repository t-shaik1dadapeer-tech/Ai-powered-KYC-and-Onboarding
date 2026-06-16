use std::collections::BTreeMap;
use std::path::Path;

use regex::Regex;
use serde::{Deserialize, Serialize};

use crate::file_walker::RepoFile;
use crate::parser::ParsedFile;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct RiskAssessment {
    pub score: u32,
    pub band: String,
    pub factors: BTreeMap<String, serde_json::Value>,
}

pub fn calculate_risk(repo_path: &Path, files: &[RepoFile], parsed: &[ParsedFile]) -> RiskAssessment {
    let total = files.len().max(1);
    let test_count = parsed.iter().filter(|p| p.test_file).count();
    let test_ratio = test_count as f64 / total as f64;

    let total_lines: usize = files.iter().map(|f| f.line_count).sum();
    let avg_lines = total_lines as f64 / total as f64;

    let secret_hits = count_secret_patterns(files);
    let dependency_count = count_dependencies(repo_path);

    let mut score: f64 = 50.0;
    let mut factors = BTreeMap::new();

    if test_ratio >= 0.2 {
        score -= 15.0;
    } else {
        score += 10.0;
    }
    factors.insert("test_ratio".into(), serde_json::json!(test_ratio));

    if avg_lines > 200.0 {
        score += 10.0;
    } else if avg_lines < 80.0 {
        score -= 5.0;
    }
    factors.insert("avg_lines_per_file".into(), serde_json::json!(avg_lines));

    score += (secret_hits as f64) * 8.0;
    factors.insert("secret_pattern_hits".into(), serde_json::json!(secret_hits));

    if dependency_count > 30 {
        score += 5.0;
    }
    factors.insert("dependency_count".into(), serde_json::json!(dependency_count));

    factors.insert("total_files".into(), serde_json::json!(total));
    factors.insert("test_files".into(), serde_json::json!(test_count));

    let score = score.clamp(0.0, 100.0).round() as u32;
    let band = score_to_band(score);

    RiskAssessment {
        score,
        band,
        factors,
    }
}

fn score_to_band(score: u32) -> String {
    match score {
        0..=33 => "low".into(),
        34..=66 => "medium".into(),
        _ => "high".into(),
    }
}

fn count_secret_patterns(files: &[RepoFile]) -> usize {
    let secret_re = Regex::new(
        r#"(?i)(api[_-]?key|password|secret|token)\s*=\s*["'][^"']+["']"#,
    )
    .unwrap();
    let mut hits = 0;
    for file in files {
        if let Ok(content) = std::fs::read_to_string(&file.path) {
            hits += secret_re.find_iter(&content).count();
        }
    }
    hits
}

fn count_dependencies(repo_path: &Path) -> usize {
    let mut count = 0;
    for name in ["pyproject.toml", "package.json", "Cargo.toml", "pom.xml"] {
        let path = repo_path.join(name);
        if path.exists() {
            count += estimate_deps_from_file(&path);
        }
    }
    count
}

fn estimate_deps_from_file(path: &Path) -> usize {
    let content = std::fs::read_to_string(path).unwrap_or_default();
    if path.ends_with("pyproject.toml") {
        return content.matches('"').count() / 4;
    }
    if path.ends_with("package.json") {
        return content.matches(':').count().saturating_sub(2);
    }
    if path.ends_with("Cargo.toml") {
        return content.matches("\n").count().saturating_sub(5);
    }
    content.matches("<artifactId>").count()
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn low_test_ratio_increases_score() {
        let files = vec![RepoFile {
            path: PathBuf::from("a.py"),
            relative: "a.py".into(),
            extension: "py".into(),
            size_bytes: 100,
            line_count: 50,
        }];
        let parsed = vec![ParsedFile {
            path: "a.py".into(),
            language: "python".into(),
            imports: vec![],
            symbols: vec![],
            test_file: false,
        }];
        let risk = calculate_risk(Path::new("."), &files, &parsed);
        assert!(risk.score >= 50);
        assert!(risk.factors.contains_key("test_ratio"));
    }

    #[test]
    fn band_mapping() {
        assert_eq!(score_to_band(20), "low");
        assert_eq!(score_to_band(50), "medium");
        assert_eq!(score_to_band(80), "high");
    }
}

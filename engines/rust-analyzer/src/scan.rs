use std::path::Path;

use serde::{Deserialize, Serialize};

use crate::error::Result;
use crate::file_walker::walk_repository;
use crate::graph::{build_import_graph, GraphEdge};
use crate::parser::{parse_file_content, ParsedFile};
use crate::risk::{calculate_risk, RiskAssessment};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScanResult {
    pub repository: String,
    pub file_count: usize,
    pub files: Vec<ParsedFile>,
    pub graph_edges: Vec<GraphEdge>,
    pub risk: RiskAssessment,
    pub scan_duration_ms: u128,
}

pub fn scan_repository(repo_path: &Path) -> Result<ScanResult> {
    let start = std::time::Instant::now();
    let repo_files = walk_repository(repo_path)?;

    let mut parsed = Vec::with_capacity(repo_files.len());
    let mut text_contents: Vec<String> = Vec::with_capacity(repo_files.len());
    for file in &repo_files {
        let content = match std::fs::read_to_string(&file.path) {
            Ok(c) => c,
            Err(_) => continue,
        };
        text_contents.push(content.clone());
        parsed.push(parse_file_content(&file.relative, &file.path, &content));
    }

    let graph_edges = build_import_graph(&parsed);
    let risk = calculate_risk(repo_path, &repo_files, &parsed, &text_contents);

    Ok(ScanResult {
        repository: repo_path.display().to_string(),
        file_count: repo_files.len(),
        files: parsed,
        graph_edges,
        risk,
        scan_duration_ms: start.elapsed().as_millis(),
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::tempdir;

    #[test]
    fn scans_temp_repo() {
        let dir = tempdir().unwrap();
        fs::write(
            dir.path().join("main.py"),
            "from app.service import Service\nclass Main: pass\n",
        )
        .unwrap();
        fs::write(dir.path().join("app_service.py"), "class Service: pass\n").unwrap();

        let result = scan_repository(dir.path()).unwrap();
        assert!(result.file_count >= 1);
        assert!(result.risk.score <= 100);
    }
}

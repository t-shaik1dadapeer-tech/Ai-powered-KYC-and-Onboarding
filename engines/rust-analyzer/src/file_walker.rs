use std::fs;
use std::path::{Path, PathBuf};

use walkdir::WalkDir;

use crate::error::{AnalyzerError, Result};

const SKIP_DIRS: &[&str] = &[
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "target",
    "dist",
    "build",
    "htmlcov",
    "evidence",
    ".cursor",
];

const SKIP_FILES: &[&str] = &[".DS_Store"];

const MAX_FILE_BYTES: u64 = 512 * 1024;

pub struct RepoFile {
    pub path: PathBuf,
    pub relative: String,
    pub extension: String,
    pub size_bytes: u64,
    pub line_count: usize,
}

pub fn walk_repository(repo_path: &Path) -> Result<Vec<RepoFile>> {
    let canonical = fs::canonicalize(repo_path).map_err(|_| {
        AnalyzerError::InvalidPath(format!("Repository not found: {}", repo_path.display()))
    })?;

    if !canonical.is_dir() {
        return Err(AnalyzerError::InvalidPath(format!(
            "Not a directory: {}",
            canonical.display()
        )));
    }

    let ignore_patterns = load_analyzerignore(&canonical);
    let mut files = Vec::new();

    for entry in WalkDir::new(&canonical)
        .follow_links(false)
        .into_iter()
        .filter_entry(|e| !should_skip_dir(e.path(), &canonical, &ignore_patterns))
    {
        let entry = entry?;
        if !entry.file_type().is_file() {
            continue;
        }

        let path = entry.path();
        if should_skip_file(path) {
            continue;
        }

        let relative = path
            .strip_prefix(&canonical)
            .map_err(|_| AnalyzerError::Analysis("Failed to relativize path".into()))?
            .to_string_lossy()
            .replace('\\', "/");

        if matches_ignore_pattern(&relative, &ignore_patterns) {
            continue;
        }

        let metadata = fs::metadata(path)?;
        if metadata.len() > MAX_FILE_BYTES {
            continue;
        }

        let extension = path
            .extension()
            .and_then(|e| e.to_str())
            .unwrap_or("")
            .to_string();

        let line_count = count_lines(path)?;

        files.push(RepoFile {
            path: path.to_path_buf(),
            relative,
            extension,
            size_bytes: metadata.len(),
            line_count,
        });
    }

    files.sort_by(|a, b| a.relative.cmp(&b.relative));
    Ok(files)
}

fn load_analyzerignore(repo_path: &Path) -> Vec<String> {
    let ignore_file = repo_path.join(".analyzerignore");
    if !ignore_file.is_file() {
        return Vec::new();
    }
    fs::read_to_string(ignore_file)
        .unwrap_or_default()
        .lines()
        .map(|l| l.trim().to_string())
        .filter(|l| !l.is_empty() && !l.starts_with('#'))
        .collect()
}

fn should_skip_dir(path: &Path, root: &Path, ignore_patterns: &[String]) -> bool {
    if path == root {
        return false;
    }
    if let Some(name) = path.file_name().and_then(|n| n.to_str()) {
        if SKIP_DIRS.contains(&name) {
            return true;
        }
        if ignore_patterns
            .iter()
            .any(|p| name == p.trim_end_matches('/'))
        {
            return true;
        }
    }
    false
}

fn should_skip_file(path: &Path) -> bool {
    path.file_name()
        .and_then(|n| n.to_str())
        .map(|n| SKIP_FILES.contains(&n))
        .unwrap_or(false)
}

fn matches_ignore_pattern(relative: &str, patterns: &[String]) -> bool {
    patterns
        .iter()
        .any(|p| relative.starts_with(p.trim_end_matches('/')))
}

fn count_lines(path: &Path) -> Result<usize> {
    let bytes = fs::read(path)?;
    Ok(bytes.iter().filter(|&&b| b == b'\n').count())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::tempdir;

    #[test]
    fn skips_node_modules() {
        let dir = tempdir().unwrap();
        let root = dir.path();
        fs::write(root.join("app.py"), "print('ok')\n").unwrap();
        fs::create_dir_all(root.join("node_modules/pkg")).unwrap();
        fs::write(root.join("node_modules/pkg/index.js"), "x").unwrap();

        let files = walk_repository(root).unwrap();
        assert_eq!(files.len(), 1);
        assert_eq!(files[0].relative, "app.py");
    }

    #[test]
    fn rejects_missing_path() {
        let result = walk_repository(Path::new("/nonexistent/path/xyz"));
        assert!(result.is_err());
    }
}

use thiserror::Error;

pub type Result<T> = std::result::Result<T, AnalyzerError>;

#[derive(Debug, Error)]
pub enum AnalyzerError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("JSON error: {0}")]
    Json(#[from] serde_json::Error),

    #[error("Invalid path: {0}")]
    InvalidPath(String),

    #[error("Path traversal denied: {0}")]
    PathTraversal(String),

    #[error("Walk error: {0}")]
    Walk(#[from] walkdir::Error),

    #[error("Analysis failed: {0}")]
    Analysis(String),
}

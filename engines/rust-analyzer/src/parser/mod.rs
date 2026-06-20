mod python;
mod universal;

pub use python::parse_python;
pub use universal::{parse_file, parse_file_content};

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct ParsedFile {
    pub path: String,
    pub language: String,
    pub imports: Vec<String>,
    pub symbols: Vec<String>,
    pub test_file: bool,
}

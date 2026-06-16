use std::fs;
use std::path::Path;

use regex::Regex;

use super::{parse_python, ParsedFile};
use crate::error::Result;

pub fn parse_file(relative: &str, path: &Path) -> Result<ParsedFile> {
    let content = fs::read_to_string(path)?;
    let ext = path
        .extension()
        .and_then(|e| e.to_str())
        .unwrap_or("")
        .to_lowercase();

    Ok(match ext.as_str() {
        "py" => parse_python(relative, &content),
        "js" | "ts" | "jsx" | "tsx" => parse_javascript(relative, &content),
        "java" | "kt" => parse_java(relative, &content),
        "rs" => parse_rust(relative, &content),
        _ => ParsedFile {
            path: relative.to_string(),
            language: ext,
            imports: Vec::new(),
            symbols: Vec::new(),
            test_file: relative.contains("test") || relative.contains("spec"),
        },
    })
}

fn parse_javascript(relative: &str, content: &str) -> ParsedFile {
    let require_re = Regex::new(r#"require\s*\(\s*['"]([^'"]+)['"]\s*\)"#).unwrap();
    let import_re = Regex::new(r#"from\s+['"]([^'"]+)['"]"#).unwrap();
    let class_re = Regex::new(r"(?m)(?:class|function)\s+(\w+)").unwrap();

    let mut imports: Vec<String> = require_re
        .captures_iter(content)
        .chain(import_re.captures_iter(content))
        .filter_map(|c| c.get(1).map(|m| m.as_str().to_string()))
        .collect();

    imports.sort();
    imports.dedup();

    let symbols: Vec<String> = class_re
        .captures_iter(content)
        .filter_map(|c| c.get(1).map(|m| m.as_str().to_string()))
        .collect();

    ParsedFile {
        path: relative.to_string(),
        language: "javascript".into(),
        imports,
        symbols,
        test_file: relative.contains(".test.") || relative.contains(".spec."),
    }
}

fn parse_java(relative: &str, content: &str) -> ParsedFile {
    let import_re = Regex::new(r"(?m)^import\s+([\w.]+);").unwrap();
    let class_re = Regex::new(r"(?m)(?:class|interface)\s+(\w+)").unwrap();

    let imports: Vec<String> = import_re
        .captures_iter(content)
        .filter_map(|c| c.get(1).map(|m| m.as_str().to_string()))
        .collect();

    let symbols: Vec<String> = class_re
        .captures_iter(content)
        .filter_map(|c| c.get(1).map(|m| m.as_str().to_string()))
        .collect();

    ParsedFile {
        path: relative.to_string(),
        language: "java".into(),
        imports,
        symbols,
        test_file: relative.ends_with("Test.java"),
    }
}

fn parse_rust(relative: &str, content: &str) -> ParsedFile {
    let use_re = Regex::new(r"(?m)^use\s+([\w:]+);").unwrap();
    let fn_re = Regex::new(r"(?m)^(?:pub\s+)?fn\s+(\w+)").unwrap();
    let struct_re = Regex::new(r"(?m)^(?:pub\s+)?struct\s+(\w+)").unwrap();

    let imports: Vec<String> = use_re
        .captures_iter(content)
        .filter_map(|c| c.get(1).map(|m| m.as_str().to_string()))
        .collect();

    let mut symbols: Vec<String> = struct_re
        .captures_iter(content)
        .filter_map(|c| c.get(1).map(|m| m.as_str().to_string()))
        .collect();
    symbols.extend(
        fn_re
            .captures_iter(content)
            .filter_map(|c| c.get(1).map(|m| m.as_str().to_string())),
    );

    ParsedFile {
        path: relative.to_string(),
        language: "rust".into(),
        imports,
        symbols,
        test_file: relative.contains("/tests/") || relative.ends_with("_test.rs"),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_javascript_requires() {
        let content = r#"const express = require('express');
class UserService {}
"#;
        let parsed = parse_javascript("routes/users.js", content);
        assert!(parsed.imports.contains(&"express".to_string()));
        assert!(parsed.symbols.contains(&"UserService".to_string()));
    }
}

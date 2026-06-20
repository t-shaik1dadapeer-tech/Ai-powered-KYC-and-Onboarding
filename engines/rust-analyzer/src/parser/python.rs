use std::path::Path;

use regex::Regex;

use super::ParsedFile;

pub fn parse_python(relative: &str, content: &str) -> ParsedFile {
    let import_re = Regex::new(r"(?m)^(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))").unwrap();
    let class_re = Regex::new(r"(?m)^class\s+(\w+)").unwrap();
    let def_re = Regex::new(r"(?m)^def\s+(test_\w+)").unwrap();

    let mut imports = Vec::new();
    for cap in import_re.captures_iter(content) {
        if let Some(m) = cap.get(1).or_else(|| cap.get(2)) {
            imports.push(m.as_str().to_string());
        }
    }

    let mut symbols: Vec<String> = class_re
        .captures_iter(content)
        .filter_map(|c| c.get(1).map(|m| m.as_str().to_string()))
        .collect();

    symbols.extend(
        def_re
            .captures_iter(content)
            .filter_map(|c| c.get(1).map(|m| m.as_str().to_string())),
    );

    let test_file = Path::new(relative)
        .file_name()
        .and_then(|n| n.to_str())
        .map(|n| n.starts_with("test_") || relative.contains("/tests/"))
        .unwrap_or(false);

    ParsedFile {
        path: relative.to_string(),
        language: "python".into(),
        imports,
        symbols,
        test_file,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn extracts_python_imports_and_classes() {
        let content = r#"
from fastapi import APIRouter
import os

class CustomerService:
    pass

def test_create():
    pass
"#;
        let parsed = parse_python("app/services/customer.py", content);
        assert!(parsed.imports.iter().any(|i| i.contains("fastapi")));
        assert!(parsed.symbols.contains(&"CustomerService".to_string()));
        assert!(parsed.symbols.contains(&"test_create".to_string()));
    }
}

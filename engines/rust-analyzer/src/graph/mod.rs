use serde::{Deserialize, Serialize};

use crate::parser::ParsedFile;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct GraphEdge {
    pub from: String,
    pub to: String,
    pub import: String,
}

pub fn build_import_graph(files: &[ParsedFile]) -> Vec<GraphEdge> {
    let mut edges = Vec::new();

    for file in files {
        for import in &file.imports {
            if let Some(target) = resolve_import(&file.path, import, files) {
                edges.push(GraphEdge {
                    from: file.path.clone(),
                    to: target,
                    import: import.clone(),
                });
            }
        }
    }

    edges.sort_by(|a, b| (&a.from, &a.to).cmp(&(&b.from, &b.to)));
    edges.dedup_by(|a, b| a.from == b.from && a.to == b.to);
    edges
}

fn resolve_import(source: &str, import: &str, files: &[ParsedFile]) -> Option<String> {
    let module_path = import.replace('.', "/");

    for candidate in files {
        let path = &candidate.path;
        if path.contains(&module_path)
            || path.ends_with(&format!("{module_path}.py"))
            || path.ends_with(&format!("{module_path}.js"))
            || path.ends_with(&format!("{module_path}.java"))
            || path.ends_with(&format!("{module_path}.rs"))
        {
            return Some(path.clone());
        }
    }

    if source.contains("services/") && import.contains("repository") {
        return files
            .iter()
            .find(|f| f.path.contains("repositories/"))
            .map(|f| f.path.clone());
    }

    None
}

#[cfg(test)]
mod tests {
    use super::*;

    fn pf(path: &str, imports: Vec<&str>) -> ParsedFile {
        ParsedFile {
            path: path.into(),
            language: "python".into(),
            imports: imports.into_iter().map(String::from).collect(),
            symbols: vec![],
            test_file: false,
        }
    }

    #[test]
    fn builds_edges_between_files() {
        let files = vec![
            pf("app/routers/customers.py", vec!["app.services.customer_service"]),
            pf("app/services/customer_service.py", vec!["app.repositories.customer_repository"]),
            pf("app/repositories/customer_repository.py", vec![]),
        ];
        let edges = build_import_graph(&files);
        assert!(!edges.is_empty());
    }
}

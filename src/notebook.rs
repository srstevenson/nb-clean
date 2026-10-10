use std::fmt;

use serde_json::{Value, ser::PrettyFormatter, value::RawValue};

use crate::cli::Options;

pub struct Notebook(Value);

#[derive(Debug)]
pub enum Change {
    EmptyCell(usize),
    CellMetadata(usize, String),
    ExecutionCount(usize),
    Outputs(usize),
    OutputExecutionCount(usize, usize),
    NotebookMetadata(String),
    LanguageVersion,
}

impl fmt::Display for Change {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::EmptyCell(i) => write!(f, "cell {i}: empty cell"),
            Self::CellMetadata(i, field) => write!(f, "cell {i}: metadata {field}"),
            Self::ExecutionCount(i) => write!(f, "cell {i}: execution count"),
            Self::Outputs(i) => write!(f, "cell {i}: outputs"),
            Self::OutputExecutionCount(i, _) => write!(f, "cell {i}: output execution count"),
            Self::NotebookMetadata(field) => write!(f, "metadata: {field}"),
            Self::LanguageVersion => write!(f, "metadata: language_info.version"),
        }
    }
}

// nbformat strips these even when metadata is preserved:
// https://github.com/jupyter/nbformat/blob/cfb73afdd2a7f358953f2a34f747fd0d0e9d6288/nbformat/v4/rwbase.py#L95
const TRANSIENT_METADATA: [&str; 3] = ["orig_nbformat", "orig_nbformat_minor", "signature"];

impl Notebook {
    pub fn parse(bytes: &[u8]) -> Result<Self, String> {
        let json = std::str::from_utf8(bytes).map_err(|e| e.to_string())?;
        // Unicode escapes can spell a private key, so these also need explicit object parsing.
        let value = if json.contains("$serde_json::private::") || json.contains("\\u") {
            let raw: &RawValue = serde_json::from_str(json).map_err(|e| e.to_string())?;
            json_value(raw, 0)?
        } else {
            serde_json::from_str(json).map_err(|e| e.to_string())?
        };
        validate(&value)?;
        Ok(Self(value))
    }

    pub fn changes(&self, options: &Options) -> Vec<Change> {
        let mut changes = Vec::new();
        for (i, cell) in self.0["cells"].as_array().unwrap().iter().enumerate() {
            let empty = match &cell["source"] {
                Value::String(s) => s.is_empty(),
                Value::Array(lines) => lines.iter().all(|line| line.as_str() == Some("")),
                _ => unreachable!(),
            };
            if options.remove_empty_cells && empty {
                changes.push(Change::EmptyCell(i));
                continue;
            }
            for field in cell["metadata"].as_object().unwrap().keys() {
                if field == "trusted" || !options.preserves_cell_field(field) {
                    changes.push(Change::CellMetadata(i, field.clone()));
                }
            }
            if cell["cell_type"] != "code" {
                continue;
            }
            if !options.preserve_execution_counts && !cell["execution_count"].is_null() {
                changes.push(Change::ExecutionCount(i));
            }
            let outputs = cell["outputs"].as_array().unwrap();
            if !options.preserve_cell_outputs {
                if !outputs.is_empty() {
                    changes.push(Change::Outputs(i));
                }
            } else if !options.preserve_execution_counts {
                for (j, output) in outputs.iter().enumerate() {
                    if output
                        .get("execution_count")
                        .is_some_and(|count| !count.is_null())
                    {
                        changes.push(Change::OutputExecutionCount(i, j));
                    }
                }
            }
        }
        let metadata = self.0["metadata"].as_object().unwrap();
        for field in metadata.keys() {
            if options.remove_all_notebook_metadata || TRANSIENT_METADATA.contains(&field.as_str())
            {
                changes.push(Change::NotebookMetadata(field.clone()));
            }
        }
        if !options.remove_all_notebook_metadata
            && !options.preserve_notebook_metadata
            && metadata
                .get("language_info")
                .is_some_and(|info| info.get("version").is_some())
        {
            changes.push(Change::LanguageVersion);
        }
        changes
    }

    pub fn clean(&mut self, changes: &[Change]) {
        for change in changes {
            match change {
                Change::EmptyCell(_) => {}
                Change::CellMetadata(i, field) => {
                    self.0["cells"][i]["metadata"]
                        .as_object_mut()
                        .unwrap()
                        .remove(field);
                }
                Change::ExecutionCount(i) => self.0["cells"][i]["execution_count"] = Value::Null,
                Change::Outputs(i) => self.0["cells"][i]["outputs"] = Value::Array(Vec::new()),
                Change::OutputExecutionCount(i, j) => {
                    self.0["cells"][i]["outputs"][j]["execution_count"] = Value::Null;
                }
                Change::NotebookMetadata(field) => {
                    self.0["metadata"].as_object_mut().unwrap().remove(field);
                }
                Change::LanguageVersion => {
                    self.0["metadata"]["language_info"]
                        .as_object_mut()
                        .unwrap()
                        .remove("version");
                }
            }
        }
        for change in changes.iter().rev() {
            if let Change::EmptyCell(i) = change {
                self.0["cells"].as_array_mut().unwrap().remove(*i);
            }
        }
    }

    pub fn to_bytes(&self) -> Result<Vec<u8>, serde_json::Error> {
        let mut bytes = Vec::new();
        let mut serializer =
            serde_json::Serializer::with_formatter(&mut bytes, PrettyFormatter::with_indent(b" "));
        self.0.serialize(&mut serializer)?;
        bytes.push(b'\n');
        Ok(bytes)
    }
}

// Parse objects explicitly so serde_json's private number key remains ordinary data.
fn json_value(raw: &RawValue, depth: usize) -> Result<Value, String> {
    if depth >= 128 {
        return Err("JSON nesting limit exceeded".into());
    }
    let json = raw.get();
    match json.as_bytes()[0] {
        b'{' => {
            let fields: std::collections::BTreeMap<String, &RawValue> =
                serde_json::from_str(json).map_err(|e| e.to_string())?;
            fields
                .into_iter()
                .map(|(key, raw)| Ok((key, json_value(raw, depth + 1)?)))
                .collect::<Result<_, String>>()
                .map(Value::Object)
        }
        b'[' => {
            let items: Vec<&RawValue> = serde_json::from_str(json).map_err(|e| e.to_string())?;
            items
                .into_iter()
                .map(|raw| json_value(raw, depth + 1))
                .collect::<Result<_, _>>()
                .map(Value::Array)
        }
        _ => serde_json::from_str(json).map_err(|e| e.to_string()),
    }
}

fn validate(value: &Value) -> Result<(), String> {
    if !value.is_object() {
        return Err("notebook must be an object".into());
    }
    if value["nbformat"].as_u64() != Some(4) {
        return Err("only nbformat 4 is supported".into());
    }
    if value["nbformat_minor"].as_u64().is_none() {
        return Err("nbformat_minor must be a non-negative integer".into());
    }
    if !value["metadata"].is_object() {
        return Err("metadata must be an object".into());
    }
    if value["metadata"]
        .get("language_info")
        .is_some_and(|v| !v.is_object())
    {
        return Err("metadata.language_info must be an object".into());
    }
    let cells = value["cells"].as_array().ok_or("cells must be an array")?;
    for (i, cell) in cells.iter().enumerate() {
        let invalid = |message: &str| format!("cell {i}: {message}");
        if !cell.is_object() || !cell["cell_type"].is_string() {
            return Err(invalid("must be an object with a string cell_type"));
        }
        if !cell["metadata"].is_object() {
            return Err(invalid("metadata must be an object"));
        }
        let source_valid = match &cell["source"] {
            Value::String(_) => true,
            Value::Array(lines) => lines.iter().all(Value::is_string),
            _ => false,
        };
        if !source_valid {
            return Err(invalid("source must be a string or an array of strings"));
        }
        if cell["cell_type"] == "code" {
            if cell.get("execution_count").is_none() || !valid_count(&cell["execution_count"]) {
                return Err(invalid("execution_count must be an integer or null"));
            }
            let outputs = cell["outputs"]
                .as_array()
                .ok_or_else(|| invalid("outputs must be an array"))?;
            for (j, output) in outputs.iter().enumerate() {
                if !output.is_object() {
                    return Err(invalid(&format!("output {j} must be an object")));
                }
                if output
                    .get("execution_count")
                    .is_some_and(|count| !valid_count(count))
                {
                    return Err(invalid(&format!(
                        "output {j}: execution_count must be an integer or null"
                    )));
                }
            }
        }
    }
    Ok(())
}

fn valid_count(value: &Value) -> bool {
    value.is_null() || value.is_i64() || value.is_u64()
}

use serde::Serialize;

#[cfg(test)]
mod tests {
    use super::*;

    fn fixture(name: &str) -> Notebook {
        Notebook::parse(&std::fs::read(format!("tests/notebooks/{name}.ipynb")).unwrap()).unwrap()
    }

    #[test]
    fn private_serde_keys_remain_objects() {
        for key in [
            "$serde_json::private::Number",
            "$serde_json::private::RawValue",
        ] {
            for value in ["123", "text"] {
                let input = format!(
                    r#"{{"nbformat":4,"nbformat_minor":5,"metadata":{{"signature":"dirty"}},"cells":[],"extension":{{"{key}":"{value}","other":true}}}}"#
                );
                let mut notebook = Notebook::parse(input.as_bytes()).unwrap();
                notebook.clean(&notebook.changes(&Options::default()));
                assert_eq!(notebook.0["extension"][key], value);
                assert_eq!(notebook.0["extension"]["other"], true);
                let output = notebook.to_bytes().unwrap();
                let reparsed = Notebook::parse(&output).unwrap();
                assert_eq!(reparsed.0["extension"], notebook.0["extension"]);
                assert!(
                    !reparsed.0["metadata"]
                        .as_object()
                        .unwrap()
                        .contains_key("signature")
                );
            }
        }
        let escaped = br#"{"nbformat":4,"nbformat_minor":5,"metadata":{},"cells":[],"extension":[{"\u0024serde_json::private::Number":"123"}]}"#;
        let notebook = Notebook::parse(escaped).unwrap();
        assert_eq!(
            notebook.0["extension"][0]["$serde_json::private::Number"],
            "123"
        );
    }

    #[test]
    fn excessive_json_nesting_is_rejected() {
        let input = format!("{}\"\\u0024\"{}", "[".repeat(128), "]".repeat(128));
        assert_eq!(
            Notebook::parse(input.as_bytes()).err().unwrap(),
            "JSON nesting limit exceeded"
        );
    }

    #[test]
    fn existing_cleaning_fixtures() {
        for (options, expected) in [
            (Options::default(), "clean"),
            (
                Options {
                    preserve_cell_metadata: true,
                    ..Default::default()
                },
                "clean_with_cell_metadata",
            ),
            (
                Options {
                    preserve_cell_metadata_field: vec!["tags".into()],
                    ..Default::default()
                },
                "clean_with_tags_metadata",
            ),
            (
                Options {
                    preserve_cell_metadata_field: vec!["tags".into(), "special".into()],
                    ..Default::default()
                },
                "clean_with_tags_special_metadata",
            ),
            (
                Options {
                    preserve_cell_outputs: true,
                    ..Default::default()
                },
                "clean_with_outputs",
            ),
            (
                Options {
                    preserve_execution_counts: true,
                    ..Default::default()
                },
                "clean_with_counts",
            ),
            (
                Options {
                    remove_all_notebook_metadata: true,
                    ..Default::default()
                },
                "clean_without_notebook_metadata",
            ),
        ] {
            let mut notebook = fixture("dirty");
            let changes = notebook.changes(&options);
            assert!(!changes.is_empty());
            notebook.clean(&changes);
            assert_eq!(notebook.0, fixture(expected).0, "{expected}");
            assert!(notebook.changes(&options).is_empty());
        }
    }

    #[test]
    fn default_output_matches_nbformat() {
        let mut notebook = fixture("dirty");
        notebook.clean(&notebook.changes(&Options::default()));
        // Checked against nbformat 5.10.4's writer.
        assert_eq!(
            notebook.to_bytes().unwrap(),
            std::fs::read("tests/notebooks/clean.ipynb").unwrap()
        );
    }

    #[test]
    fn empty_cells() {
        let options = Options {
            remove_empty_cells: true,
            ..Default::default()
        };
        let mut notebook = fixture("clean_with_empty_cells");
        notebook.clean(&notebook.changes(&options));
        assert_eq!(notebook.0, fixture("clean_without_empty_cells").0);
    }
}

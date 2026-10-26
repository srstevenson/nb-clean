use std::{
    fs,
    io::Write,
    process::{Command, Output, Stdio},
};

use serde_json::{Value, json};
use tempfile::TempDir;

fn command() -> Command {
    Command::new(env!("CARGO_BIN_EXE_nb-clean"))
}

fn run(args: &[&str], input: &[u8]) -> Output {
    let mut child = command()
        .args(args)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    child.stdin.take().unwrap().write_all(input).unwrap();
    child.wait_with_output().unwrap()
}

fn notebook() -> Value {
    json!({
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {"language_info": {"name": "python", "version": "3.14"}},
        "cells": [{"cell_type": "code", "id": "cell-1", "source": ["print('hello')\n"],
            "metadata": {"tags": ["keep"], "timing": "remove"}, "execution_count": 0,
            "outputs": [{"output_type": "execute_result", "execution_count": 0,
                "metadata": {}, "data": {"text/plain": ["hello"]}}]}]
    })
}

fn clean_value(value: &Value, flags: &[&str]) -> Value {
    let mut args = vec!["clean"];
    args.extend_from_slice(flags);
    let output = run(&args, &serde_json::to_vec(value).unwrap());
    assert!(
        output.status.success(),
        "{args:?}: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    serde_json::from_slice(&output.stdout).unwrap_or_else(|error| {
        panic!(
            "{args:?}: invalid JSON output: {error}: {:?}",
            output.stdout
        )
    })
}

#[test]
fn clean_and_check_stdin() {
    let input = serde_json::to_vec(&notebook()).unwrap();
    let checked = run(&["check"], &input);
    assert_eq!(checked.status.code(), Some(1));
    assert!(String::from_utf8_lossy(&checked.stdout).contains("stdin cell 0: execution count"));
    let cleaned = run(&["clean"], &input);
    assert!(cleaned.status.success());
    assert!(cleaned.stderr.is_empty());
    assert!(cleaned.stdout.ends_with(b"\n"));
    assert!(run(&["check"], &cleaned.stdout).status.success());
    assert_eq!(run(&["clean"], &cleaned.stdout).stdout, cleaned.stdout);
}

#[test]
fn clean_input_passes_through_without_formatting() {
    let input = br#"{"nbformat":4,"nbformat_minor":2,"metadata":{},"cells":[]}"#;
    assert_eq!(run(&["clean"], input).stdout, input);
}

#[test]
fn option_combinations_agree_with_check() {
    let flags = ["-e", "-M", "-m", "-o", "-c", "-n"];
    for bits in 0..64 {
        if bits & 2 != 0 && bits & 32 != 0 {
            continue;
        }
        let selected: Vec<_> = flags
            .iter()
            .enumerate()
            .filter_map(|(i, flag)| (bits & (1 << i) != 0).then_some(*flag))
            .collect();
        let value = clean_value(&notebook(), &selected);
        let cell = &value["cells"][0];
        assert_eq!(
            cell["execution_count"].is_null(),
            bits & 16 == 0,
            "options: {selected:?}"
        );
        assert_eq!(
            cell["outputs"].as_array().unwrap().is_empty(),
            bits & 8 == 0,
            "options: {selected:?}"
        );
        assert_eq!(
            cell["metadata"].as_object().unwrap().is_empty(),
            bits & 4 == 0,
            "options: {selected:?}"
        );
        if bits & 8 != 0 {
            assert_eq!(
                cell["outputs"][0]["execution_count"].is_null(),
                bits & 16 == 0,
                "options: {selected:?}"
            );
        }
        assert_eq!(
            value["metadata"].as_object().unwrap().is_empty(),
            bits & 2 != 0,
            "options: {selected:?}"
        );
        let mut args = vec!["check"];
        args.extend_from_slice(&selected);
        let output = run(&args, &serde_json::to_vec(&value).unwrap());
        assert!(
            output.status.success(),
            "{args:?}: {}",
            String::from_utf8_lossy(&output.stderr)
        );
    }
}

#[test]
fn selected_metadata_fields() {
    let cleaned = clean_value(
        &notebook(),
        &[
            "--preserve-cell-metadata-field",
            "tags",
            "--preserve-cell-metadata-field",
            "missing",
        ],
    );
    assert_eq!(cleaned["cells"][0]["metadata"], json!({"tags": ["keep"]}));
}

#[test]
fn transient_fields_are_removed_despite_preservation() {
    let mut value = notebook();
    for field in ["orig_nbformat", "orig_nbformat_minor", "signature"] {
        value["metadata"][field] = json!("transient");
    }
    value["cells"][0]["metadata"]["trusted"] = json!(true);
    let cleaned = clean_value(&value, &["-m", "-n", "-c", "-o"]);
    assert!(cleaned["cells"][0]["metadata"].get("trusted").is_none());
    assert_eq!(cleaned["metadata"], notebook()["metadata"]);
    assert_eq!(
        cleaned["cells"][0]["metadata"],
        notebook()["cells"][0]["metadata"]
    );
    assert_eq!(
        run(
            &["check", "-m", "-n", "-c", "-o"],
            &serde_json::to_vec(&value).unwrap()
        )
        .status
        .code(),
        Some(1)
    );
}

#[test]
fn source_and_extensions_are_preserved() {
    let mut value = notebook();
    value["cells"][0]["source"] = json!("hello\r\nworld");
    value["cells"][0]["attachments"] = json!({"picture": {"image/svg+xml": "<svg>\n</svg>"}});
    value["extension"] = json!({"nested": ["cafe", 42]});
    value["cells"]
        .as_array_mut()
        .unwrap()
        .push(json!({"cell_type": "future", "metadata": {}, "source": [""], "extra": true}));
    let cleaned = clean_value(&value, &[]);
    assert_eq!(cleaned["cells"][0]["source"], value["cells"][0]["source"]);
    assert_eq!(
        cleaned["cells"][0]["attachments"],
        value["cells"][0]["attachments"]
    );
    assert_eq!(cleaned["cells"][0]["id"], value["cells"][0]["id"]);
    assert_eq!(cleaned["extension"], value["extension"]);
    assert_eq!(cleaned["cells"][1], value["cells"][1]);
}

#[test]
fn empty_source_forms_and_whitespace() {
    let mut value = notebook();
    value["cells"] = json!(
        [
            json!(""),
            json!([]),
            json!(["", ""]),
            json!(" "),
            json!(["\n"])
        ]
        .into_iter()
        .map(|source| json!({"cell_type": "markdown", "source": source, "metadata": {}}))
        .collect::<Vec<_>>()
    );
    let cleaned = clean_value(&value, &["-e"]);
    assert_eq!(cleaned["cells"].as_array().unwrap().len(), 2);
    assert_eq!(cleaned["cells"][0]["source"], " ");
    assert_eq!(cleaned["cells"][1]["source"], json!(["\n"]));
}

#[test]
fn large_numbers_and_unicode_survive() {
    let input = "{\"nbformat\":4,\"nbformat_minor\":5,\"cells\":[],\"metadata\":{\"large\":123456789012345678901234567890,\"float\":1.234567890123456789,\"text\":\"caf\u{e9}\",\"signature\":\"remove\"}}";
    let output = run(&["clean"], input.as_bytes());
    assert!(output.status.success());
    let text = String::from_utf8(output.stdout).unwrap();
    assert!(text.contains("123456789012345678901234567890"));
    assert!(text.contains("1.234567890123456789"));
    assert!(text.contains("caf\u{e9}"));
}

#[test]
fn malformed_inputs_and_conflicting_options() {
    for input in [b"not json".as_slice(), b"{}", b"[]"] {
        assert_eq!(run(&["clean"], input).status.code(), Some(65));
    }
    for args in [
        vec!["check", "-M", "-n"],
        vec!["clean", "-m", "--preserve-cell-metadata-field", "tags"],
        vec!["version"],
    ] {
        assert_eq!(run(&args, b"").status.code(), Some(64));
    }
    assert!(run(&["--version"], b"").status.success());
    assert!(run(&["--help"], b"").status.success());
    for field in ["source", "metadata", "outputs", "execution_count"] {
        let mut value = notebook();
        value["cells"][0][field] = json!(true);
        assert_eq!(
            run(&["clean"], &serde_json::to_vec(&value).unwrap())
                .status
                .code(),
            Some(65),
            "{field}"
        );
    }
}

#[test]
fn files_directories_and_error_continuation() {
    let dir = TempDir::new().unwrap();
    fs::create_dir(dir.path().join("nested")).unwrap();
    let dirty = dir.path().join("nested/dirty.ipynb");
    let invalid = dir.path().join("invalid.ipynb");
    fs::write(&dirty, serde_json::to_vec(&notebook()).unwrap()).unwrap();
    fs::write(&invalid, "invalid").unwrap();
    let output = command().arg("clean").arg(dir.path()).output().unwrap();
    assert_eq!(output.status.code(), Some(65));
    assert!(output.stdout.is_empty());
    assert_eq!(fs::read(&invalid).unwrap(), b"invalid");
    assert!(
        command()
            .arg("check")
            .arg(&dirty)
            .status()
            .unwrap()
            .success()
    );
    let bytes = fs::read(&dirty).unwrap();
    let modified = fs::metadata(&dirty).unwrap().modified().unwrap();
    assert!(
        command()
            .arg("clean")
            .arg(&dirty)
            .status()
            .unwrap()
            .success()
    );
    assert_eq!(fs::read(&dirty).unwrap(), bytes);
    assert_eq!(fs::metadata(&dirty).unwrap().modified().unwrap(), modified);
    assert_eq!(
        command()
            .arg("check")
            .arg(dir.path().join("missing"))
            .output()
            .unwrap()
            .status
            .code(),
        Some(66)
    );
}

#[test]
fn hidden_and_ignored_paths_are_skipped_during_recursion() {
    let dir = TempDir::new().unwrap();
    assert!(
        Command::new("git")
            .arg("init")
            .arg("-q")
            .arg(dir.path())
            .status()
            .unwrap()
            .success()
    );
    fs::write(dir.path().join(".gitignore"), "ignored/\n").unwrap();
    let dirty = serde_json::to_vec(&notebook()).unwrap();
    for name in [".ipynb_checkpoints", "ignored"] {
        fs::create_dir(dir.path().join(name)).unwrap();
        fs::write(dir.path().join(name).join("dirty.ipynb"), &dirty).unwrap();
    }
    assert!(
        command()
            .arg("check")
            .arg(dir.path())
            .status()
            .unwrap()
            .success()
    );
    for name in [".ipynb_checkpoints", "ignored"] {
        assert_eq!(
            command()
                .arg("check")
                .arg(dir.path().join(name))
                .status()
                .unwrap()
                .code(),
            Some(1),
            "{name}"
        );
    }
}

#[test]
fn overlapping_paths_are_processed_once() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("dirty.ipynb");
    fs::write(&path, serde_json::to_vec(&notebook()).unwrap()).unwrap();
    let once = command().arg("check").arg(&path).output().unwrap();
    let twice = command()
        .arg("check")
        .arg(dir.path())
        .arg(&path)
        .arg(dir.path().join("./dirty.ipynb"))
        .output()
        .unwrap();
    assert_eq!(once.stdout, twice.stdout);
}

#[cfg(unix)]
#[test]
fn symlinks_and_permissions() {
    use std::os::unix::fs::{PermissionsExt, symlink};
    let dir = TempDir::new().unwrap();
    let real = dir.path().join("real");
    let inputs = dir.path().join("inputs");
    fs::create_dir(&real).unwrap();
    fs::create_dir(&inputs).unwrap();
    let target = real.join("dirty.ipynb");
    fs::write(&target, serde_json::to_vec(&notebook()).unwrap()).unwrap();
    fs::set_permissions(&target, fs::Permissions::from_mode(0o640)).unwrap();
    symlink(&real, inputs.join("directory-link")).unwrap();
    assert!(
        command()
            .arg("check")
            .arg(&inputs)
            .output()
            .unwrap()
            .status
            .success()
    );
    assert_eq!(
        command()
            .arg("check")
            .arg(inputs.join("directory-link"))
            .output()
            .unwrap()
            .status
            .code(),
        Some(1)
    );
    let link = inputs.join("linked.ipynb");
    symlink(&target, &link).unwrap();
    assert!(
        command()
            .arg("clean")
            .arg(&link)
            .status()
            .unwrap()
            .success()
    );
    assert!(link.is_symlink());
    assert_eq!(
        fs::metadata(&target).unwrap().permissions().mode() & 0o777,
        0o640
    );
    assert!(
        command()
            .arg("check")
            .arg(&target)
            .status()
            .unwrap()
            .success()
    );
    symlink(real.join("missing"), inputs.join("broken.ipynb")).unwrap();
    assert_eq!(
        command()
            .arg("check")
            .arg(&inputs)
            .output()
            .unwrap()
            .status
            .code(),
        Some(66)
    );
}

#[test]
fn read_only_dirty_file_is_not_replaced() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("dirty.ipynb");
    let bytes = serde_json::to_vec(&notebook()).unwrap();
    fs::write(&path, &bytes).unwrap();
    let mut permissions = fs::metadata(&path).unwrap().permissions();
    permissions.set_readonly(true);
    fs::set_permissions(&path, permissions).unwrap();
    assert_eq!(
        command()
            .arg("clean")
            .arg(&path)
            .output()
            .unwrap()
            .status
            .code(),
        Some(73)
    );
    assert_eq!(fs::read(&path).unwrap(), bytes);
    // Restore write access so Windows can remove the temporary directory.
    #[cfg(windows)]
    {
        let mut permissions = fs::metadata(&path).unwrap().permissions();
        permissions.set_readonly(false);
        fs::set_permissions(&path, permissions).unwrap();
    }
}

#[test]
fn unsupported_version_is_rejected() {
    let mut value = notebook();
    value["nbformat"] = json!(3);
    assert_eq!(
        run(&["check"], &serde_json::to_vec(&value).unwrap())
            .status
            .code(),
        Some(65)
    );
    value["nbformat"] = json!(4);
    value["nbformat_minor"] = json!(99);
    assert!(
        run(&["clean"], &serde_json::to_vec(&value).unwrap())
            .status
            .success()
    );
}

#[test]
fn changed_output_matches_python_layout() {
    let output = run(
        &["clean"],
        br#"{"nbformat_minor":2,"nbformat":4,"metadata":{"signature":"remove"},"cells":[]}"#,
    );
    assert_eq!(
        output.stdout,
        b"{\n \"cells\": [],\n \"metadata\": {},\n \"nbformat\": 4,\n \"nbformat_minor\": 2\n}\n"
    );
}

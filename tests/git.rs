use std::{
    fs,
    path::{Path, PathBuf},
    process::{Command, Output},
};

use tempfile::TempDir;

fn git(root: &Path, args: &[&str]) -> Output {
    Command::new("git")
        .arg("-C")
        .arg(root)
        .args(args)
        .env(
            "GIT_CONFIG_GLOBAL",
            if cfg!(windows) { "NUL" } else { "/dev/null" },
        )
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .output()
        .unwrap()
}

fn git_ok(root: &Path, args: &[&str]) -> String {
    let output = git(root, args);
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout)
        .unwrap()
        .trim_end_matches(['\r', '\n'])
        .into()
}

fn nb(root: &Path, args: &[&str]) -> Output {
    Command::new(env!("CARGO_BIN_EXE_nb-clean"))
        .current_dir(root)
        .args(args)
        .env(
            "GIT_CONFIG_GLOBAL",
            if cfg!(windows) { "NUL" } else { "/dev/null" },
        )
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .output()
        .unwrap()
}

fn repository() -> TempDir {
    let dir = TempDir::new().unwrap();
    git_ok(dir.path(), &["init", "-q"]);
    git_ok(dir.path(), &["config", "user.name", "nb-clean tests"]);
    git_ok(dir.path(), &["config", "user.email", "tests@example.com"]);
    dir
}

fn attributes(root: &Path) -> PathBuf {
    PathBuf::from(git_ok(
        root,
        &[
            "rev-parse",
            "--path-format=absolute",
            "--git-path",
            "info/attributes",
        ],
    ))
}

#[test]
fn installation_and_removal_preserve_unrelated_settings() {
    let dir = repository();
    let root = dir.path();
    let path = attributes(root);
    fs::create_dir_all(path.parent().unwrap()).unwrap();
    fs::write(&path, "*.txt text\n").unwrap();
    git_ok(root, &["config", "filter.other.clean", "cat"]);
    git_ok(root, &["config", "filter.nb-clean.smudge", "cat"]);
    for _ in 0..2 {
        assert!(
            nb(
                root,
                &["add-filter", "-e", "--preserve-cell-metadata-field", "tags"]
            )
            .status
            .success()
        );
    }
    assert_eq!(
        fs::read_to_string(&path).unwrap(),
        "*.txt text\n*.ipynb filter=nb-clean\n"
    );
    let configured = git_ok(root, &["config", "--get", "filter.nb-clean.clean"]);
    assert!(configured.contains("--remove-empty-cells"));
    assert!(configured.contains("--preserve-cell-metadata-field=tags"));
    for _ in 0..2 {
        assert!(nb(root, &["remove-filter"]).status.success());
    }
    assert_eq!(fs::read_to_string(&path).unwrap(), "*.txt text\n");
    assert_eq!(
        git_ok(root, &["config", "--get", "filter.other.clean"]),
        "cat"
    );
    assert_eq!(
        git_ok(root, &["config", "--get", "filter.nb-clean.smudge"]),
        "cat"
    );
    assert!(
        !git(root, &["config", "--get", "filter.nb-clean.clean"])
            .status
            .success()
    );
}

#[test]
fn git_filter_cleans_the_index_and_quotes_metadata_fields() {
    for field in ["owner's $(echo injected)", "-tags", "", "a=b"] {
        check_filter_field(field);
    }
}

fn check_filter_field(field: &str) {
    let dir = repository();
    let root = dir.path();
    let input = serde_json::json!({"nbformat":4,"nbformat_minor":4,"metadata":{},"cells":[{
        "cell_type":"code","source":["x"],"metadata":{field:true,"remove":true},
        "execution_count":9,"outputs":[]} ]});
    let original = serde_json::to_vec(&input).unwrap();
    fs::write(root.join("notebook.ipynb"), &original).unwrap();
    assert!(
        nb(
            root,
            &[
                "add-filter",
                &format!("--preserve-cell-metadata-field={field}")
            ]
        )
        .status
        .success()
    );
    let binary_dir = Path::new(env!("CARGO_BIN_EXE_nb-clean")).parent().unwrap();
    let mut paths = vec![binary_dir.to_path_buf()];
    paths.extend(std::env::split_paths(
        &std::env::var_os("PATH").unwrap_or_default(),
    ));
    let output = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["add", "notebook.ipynb"])
        .env("PATH", std::env::join_paths(paths).unwrap())
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert!(
        output.stderr.is_empty(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    let staged: serde_json::Value =
        serde_json::from_str(&git_ok(root, &["show", ":notebook.ipynb"])).unwrap();
    assert_eq!(
        staged["cells"][0]["metadata"],
        serde_json::json!({field:true})
    );
    assert!(staged["cells"][0]["execution_count"].is_null());
    assert_eq!(fs::read(root.join("notebook.ipynb")).unwrap(), original);
}

#[test]
fn linked_worktree_and_subdirectory_use_the_correct_attributes() {
    let dir = repository();
    let root = dir.path();
    git_ok(root, &["commit", "--allow-empty", "-qm", "Initial commit"]);
    let worktree = root.join("linked worktree");
    git_ok(
        root,
        &[
            "worktree",
            "add",
            "-qb",
            "linked",
            worktree.to_str().unwrap(),
        ],
    );
    let subdir = worktree.join("nested");
    fs::create_dir(&subdir).unwrap();
    assert!(nb(&subdir, &["add-filter"]).status.success());
    let path = attributes(&subdir);
    assert!(
        fs::read_to_string(&path)
            .unwrap()
            .contains("*.ipynb filter=nb-clean")
    );
    assert_eq!(
        git_ok(&subdir, &["check-attr", "filter", "--", "notebook.ipynb"]),
        "notebook.ipynb: filter: nb-clean"
    );
    assert!(nb(&subdir, &["remove-filter"]).status.success());
    assert!(
        !fs::read_to_string(&path)
            .unwrap()
            .contains("filter=nb-clean")
    );
}

#[test]
fn outside_a_repository_reports_configuration_error() {
    let dir = TempDir::new().unwrap();
    assert_eq!(nb(dir.path(), &["add-filter"]).status.code(), Some(78));
    assert_eq!(nb(dir.path(), &["remove-filter"]).status.code(), Some(78));
}

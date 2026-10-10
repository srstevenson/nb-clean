use std::{fs, path::PathBuf, process::Command};

use crate::{cli::Options, error::Error, files};

const ATTRIBUTE: &str = "*.ipynb filter=nb-clean";

fn git(args: &[&str]) -> Result<String, Error> {
    let output = Command::new("git").args(args).output().map_err(|e| {
        Error::new(
            if e.kind() == std::io::ErrorKind::NotFound {
                69
            } else {
                78
            },
            format!("git: {e}"),
        )
    })?;
    if !output.status.success() {
        return Err(Error::new(
            78,
            String::from_utf8_lossy(&output.stderr).trim(),
        ));
    }
    String::from_utf8(output.stdout).map_err(|e| Error::new(78, e))
}

fn attributes_path() -> Result<PathBuf, Error> {
    let path = git(&[
        "rev-parse",
        "--path-format=absolute",
        "--git-path",
        "info/attributes",
    ])?;
    // Git terminates the path with a newline; spaces in the filename are significant.
    Ok(PathBuf::from(path.trim_end_matches(['\r', '\n'])))
}

fn attributes(path: &std::path::Path) -> Result<String, Error> {
    match fs::read_to_string(path) {
        Ok(contents) => Ok(contents),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => Ok(String::new()),
        Err(e) => Err(Error::new(78, format!("{}: {e}", path.display()))),
    }
}

pub fn add(options: &Options) -> Result<(), Error> {
    let path = attributes_path()?;
    let mut contents = attributes(&path)?;
    if !contents.lines().any(|line| line == ATTRIBUTE) {
        if !contents.is_empty() && !contents.ends_with('\n') {
            contents.push('\n');
        }
        contents.push_str(ATTRIBUTE);
        contents.push('\n');
        fs::create_dir_all(path.parent().unwrap()).map_err(|e| Error::new(78, e))?;
        files::replace(&path, contents.as_bytes())?;
    }
    let command = options
        .filter_args()
        .into_iter()
        .map(|arg| quote(&arg))
        .collect::<Vec<_>>()
        .join(" ");
    git(&["config", "--local", "filter.nb-clean.clean", &command])?;
    Ok(())
}

pub fn remove() -> Result<(), Error> {
    let path = attributes_path()?;
    let original = attributes(&path)?;
    let revised: String = original
        .split_inclusive('\n')
        .filter(|line| line.trim_end_matches(['\r', '\n']) != ATTRIBUTE)
        .collect();
    if revised != original {
        files::replace(&path, revised.as_bytes())?;
    }
    let output = Command::new("git")
        .args(["config", "--local", "--unset-all", "filter.nb-clean.clean"])
        .output()
        .map_err(|e| Error::new(69, format!("git: {e}")))?;
    // git config returns 5 when there is no matching key.
    if !output.status.success() && output.status.code() != Some(5) {
        return Err(Error::new(
            78,
            String::from_utf8_lossy(&output.stderr).trim(),
        ));
    }
    Ok(())
}

fn quote(arg: &str) -> String {
    if !arg.is_empty()
        && arg
            .bytes()
            .all(|c| c.is_ascii_alphanumeric() || b"-_./".contains(&c))
    {
        arg.into()
    } else {
        format!("'{}'", arg.replace('\'', "'\\''"))
    }
}

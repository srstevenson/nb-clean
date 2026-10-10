use std::{
    collections::BTreeSet,
    fs::{self, File},
    io::{Read, Write},
    path::{Path, PathBuf},
};

use tempfile::NamedTempFile;
use walkdir::WalkDir;

use crate::error::Error;

pub struct Input {
    pub name: PathBuf,
    pub target: PathBuf,
}

pub fn discover(paths: &[PathBuf]) -> Vec<Result<Input, Error>> {
    let mut candidates = Vec::new();
    for path in paths {
        if path.is_dir() {
            for entry in WalkDir::new(path).sort_by_file_name() {
                match entry {
                    Ok(entry)
                        if entry.path().extension().is_some_and(|ext| ext == "ipynb")
                            && !entry.file_type().is_dir() =>
                    {
                        candidates.push((entry.into_path(), None));
                    }
                    Ok(_) => {}
                    Err(error) => {
                        let name = error.path().unwrap_or(path).to_path_buf();
                        candidates.push((name, Some(Error::new(66, error))));
                    }
                }
            }
        } else {
            candidates.push((path.clone(), None));
        }
    }
    candidates.sort_by(|a, b| a.0.cmp(&b.0));
    let mut seen = BTreeSet::new();
    let mut inputs = Vec::new();
    for (name, error) in candidates {
        if let Some(error) = error {
            inputs.push(Err(error));
            continue;
        }
        match name.canonicalize() {
            Ok(target) => {
                if seen.insert(target.clone()) {
                    inputs.push(Ok(Input { name, target }));
                }
            }
            Err(error) => inputs.push(Err(Error::new(66, format!("{}: {error}", name.display())))),
        }
    }
    inputs
}

pub fn read(path: &Path) -> Result<Vec<u8>, Error> {
    let mut file =
        File::open(path).map_err(|e| Error::new(66, format!("{}: {e}", path.display())))?;
    let mut bytes = Vec::new();
    file.read_to_end(&mut bytes)
        .map_err(|e| Error::new(74, format!("{}: {e}", path.display())))?;
    Ok(bytes)
}

pub fn replace(path: &Path, bytes: &[u8]) -> Result<(), Error> {
    let failure = |e| Error::new(73, format!("{}: {e}", path.display()));
    let permissions = match fs::metadata(path) {
        Ok(metadata) => {
            if metadata.permissions().readonly() {
                return Err(Error::new(
                    73,
                    format!("{}: file is read-only", path.display()),
                ));
            }
            Some(metadata.permissions())
        }
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => None,
        Err(e) => return Err(failure(e)),
    };
    let parent = path
        .parent()
        .filter(|p| !p.as_os_str().is_empty())
        .unwrap_or(Path::new("."));
    let mut temporary = NamedTempFile::new_in(parent).map_err(failure)?;
    temporary.write_all(bytes).map_err(failure)?;
    temporary.flush().map_err(failure)?;
    if let Some(permissions) = permissions {
        temporary
            .as_file()
            .set_permissions(permissions)
            .map_err(failure)?;
    }
    temporary.persist(path).map_err(|e| failure(e.error))?;
    Ok(())
}

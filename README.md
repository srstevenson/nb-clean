<p align="center"><img src="images/nb-clean.png" width=300></p>

[![License](https://img.shields.io/github/license/srstevenson/nb-clean?label=License&color=blue)](LICENSE)
[![Crates.io](https://img.shields.io/crates/v/nb-clean)](https://crates.io/crates/nb-clean)
[![CI](https://github.com/srstevenson/nb-clean/actions/workflows/ci.yml/badge.svg)](https://github.com/srstevenson/nb-clean/actions/workflows/ci.yml)

nb-clean cleans Jupyter notebooks for version control. It removes cell metadata,
execution counts, outputs, and the notebook's language version. It can check
notebooks in CI, clean files in place, or run as a Git filter or pre-commit hook.

## Installation

Install a published release from crates.io with Cargo:

```sh
cargo install nb-clean --locked
```

Building requires Rust 1.85 or later. To install from a local checkout:

```sh
cargo install --path . --locked
```

Download binary archives from [GitHub releases](https://github.com/srstevenson/nb-clean/releases)
for macOS (Apple Silicon and Intel), Linux (ARM64 and x86-64), and Windows
(x86-64). Extract the archive and put `nb-clean` or `nb-clean.exe` on your `PATH`.
Linux archives are built on Ubuntu 22.04 and use glibc. Build from source for
systems incompatible with those binaries. Running nb-clean requires no Python
installation. Git is needed only for filter configuration.

## Checking and cleaning

```sh
nb-clean check notebook.ipynb
nb-clean check notebooks/
nb-clean clean notebook.ipynb
nb-clean clean notebooks/ another.ipynb
```

Directories are searched recursively for `.ipynb` files. Overlapping inputs and
symlink aliases are processed once. Directory symlinks encountered during
recursion are skipped; an explicitly supplied directory symlink is traversed.
Notebook file symlinks are followed, and cleaning updates their targets while
preserving the links.

`check` reports unwanted content and exits with status 1 if any notebooks are
dirty. Cells are numbered from zero. `clean` updates changed files through a
temporary file in the same directory, preserving their permissions. Already-clean
files are left untouched. If a file fails, remaining files are still processed
and the command returns an error status.

With no paths, both commands read stdin. Cleaning writes the notebook to stdout:

```sh
nb-clean check < notebook.ipynb
nb-clean clean < original.ipynb > cleaned.ipynb
```

Clean stdin is passed through unchanged. Changed notebooks are written with
sorted keys, one-space indentation, Unicode text, and a trailing newline,
following `nbformat`'s JSON layout. Source text, attachments, and retained outputs
keep their string or array representations. Numeric values are retained without
rounding; their spelling can differ from Python's writer.

nb-clean supports nbformat 4. It checks the structure needed for cleaning, keeps
unknown fields, and does not upgrade notebooks or repair cell IDs. Empty source
means an empty string or an array whose strings are all empty. Whitespace-only
cells are retained.

## Options

These options work with `check`, `clean`, and `add-filter`:

| Option | Effect |
| --- | --- |
| `-e`, `--remove-empty-cells` | Remove empty cells, or report them in checks |
| `-M`, `--remove-all-notebook-metadata` | Remove all notebook metadata |
| `-m`, `--preserve-cell-metadata` | Preserve all cell metadata except transient fields |
| `--preserve-cell-metadata-field FIELD` | Preserve a selected cell metadata field; repeat for more fields |
| `-o`, `--preserve-cell-outputs` | Preserve cell outputs |
| `-c`, `--preserve-execution-counts` | Preserve cell and output execution counts |
| `-n`, `--preserve-notebook-metadata` | Preserve notebook metadata except transient fields |

By default, notebook metadata is retained except `language_info.version` and
transient fields. Preserving outputs with `-o` still clears output execution
counts unless `-c` is also supplied.

For example, preserve cell tags and slideshow settings:

```sh
nb-clean clean --preserve-cell-metadata-field tags \
  --preserve-cell-metadata-field slideshow notebook.ipynb
```

Following `nbformat`, nb-clean always removes notebook metadata `orig_nbformat`,
`orig_nbformat_minor`, and `signature`, and cell metadata `trusted`. Preservation
options do not override this rule. Their presence makes a notebook dirty.

`-M` conflicts with `-n`. Preserving all cell metadata conflicts with selecting
individual fields. Use `nb-clean --help` or `nb-clean clean --help` for help, and
`nb-clean --version` for the version.

## Git filter

From a Git working tree:

```sh
nb-clean add-filter
# Or configure the filter with cleaning options:
nb-clean add-filter --preserve-cell-metadata-field tags
nb-clean remove-filter
```

The filter is configured in local Git configuration and `info/attributes`.
Staging cleans the notebook in the index; the working copy keeps its outputs.
Installation and removal are idempotent and preserve unrelated settings and
attributes. The executable must be on `PATH` when Git stages notebooks.

## Pre-commit

Add this to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/srstevenson/nb-clean
    rev: v5.0.0
    hooks:
      - id: nb-clean
        args: [--preserve-cell-metadata-field, tags]
```

The hook uses `language: rust`. Pre-commit builds the binary and can install Rust
if needed. Its first installation includes compilation time. The hook cleans
notebooks in the working directory, so their outputs are removed on disk.

## Jujutsu

Add this to `~/.config/jj/config.toml`, then run `jj fix`:

```toml
[fix.tools.nb-clean]
command = ["nb-clean", "clean"]
patterns = ["glob:'**/*.ipynb'"]
```

Append cleaning options to the command array as needed.

## Exit statuses

| Status | Meaning |
| --- | --- |
| `0` | Success, or all checked notebooks are clean |
| `1` | At least one checked notebook is dirty |
| `64` | Invalid command-line arguments |
| `65` | Malformed notebook or unsupported format version |
| `66` | Input cannot be opened or a directory cannot be traversed |
| `69` | Git executable is unavailable |
| `73` | Output cannot be created or replaced |
| `74` | Other read or write failure |
| `78` | Git repository or configuration error |

Errors take precedence over dirty results. If several files fail, the status
corresponds to the first error in sorted processing order. Errors go to stderr;
check findings go to stdout.

## Migrating from nb-clean 4

nb-clean 5 is a Rust CLI. The Python library API is removed.
PyPI publishing is not yet configured; use Cargo or binary archives for releases.

Use `nb-clean --version` instead of `nb-clean version`. To preserve selected
metadata, replace `--preserve-cell-metadata tags slideshow --` with
`--preserve-cell-metadata-field tags --preserve-cell-metadata-field slideshow`.
The bare `-m` option now accepts no field arguments and can appear before paths.

An execution count of zero is now reported as dirty. Transient metadata is also
reported explicitly. Processing errors use the statuses above, and clean files
are no longer rewritten just to normalise formatting. Unsupported notebook major
versions are rejected.

## Development

See [the contribution instructions](.github/CONTRIBUTING.md).
Instructions for building and testing local wheels are in
[Local Python wheels](.github/CONTRIBUTING.md#local-python-wheels).

## Copyright

Copyright Scott Stevenson. Distributed under the [ISC licence](LICENSE).

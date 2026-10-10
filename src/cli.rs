use std::path::PathBuf;

use clap::{Args, Parser, Subcommand};

#[derive(Parser)]
#[command(version, about = "Clean Jupyter notebooks for versioning")]
pub struct Cli {
    #[command(subcommand)]
    pub command: Command,
}

#[derive(Subcommand)]
pub enum Command {
    /// Check notebooks for execution counts, metadata, and outputs
    Check(Inputs),
    /// Clean notebooks in place, or from stdin to stdout
    Clean(Inputs),
    /// Add a repository-local Git clean filter
    AddFilter(Options),
    /// Remove the repository-local Git clean filter
    RemoveFilter,
}

#[derive(Args)]
pub struct Inputs {
    /// Files or directories to process (stdin when omitted)
    #[arg(value_name = "PATH")]
    pub paths: Vec<PathBuf>,
    #[command(flatten)]
    pub options: Options,
}

#[derive(Args, Default)]
pub struct Options {
    /// Remove cells with empty source
    #[arg(short = 'e', long)]
    pub remove_empty_cells: bool,
    /// Remove all notebook metadata
    #[arg(short = 'M', long, conflicts_with = "preserve_notebook_metadata")]
    pub remove_all_notebook_metadata: bool,
    /// Preserve all cell metadata except transient fields
    #[arg(short = 'm', long, conflicts_with = "preserve_cell_metadata_field")]
    pub preserve_cell_metadata: bool,
    /// Preserve a cell metadata field (repeat for multiple fields)
    #[arg(long, value_name = "FIELD")]
    pub preserve_cell_metadata_field: Vec<String>,
    /// Preserve cell outputs
    #[arg(short = 'o', long)]
    pub preserve_cell_outputs: bool,
    /// Preserve cell and output execution counts
    #[arg(short = 'c', long)]
    pub preserve_execution_counts: bool,
    /// Preserve notebook metadata except transient fields
    #[arg(short = 'n', long)]
    pub preserve_notebook_metadata: bool,
}

impl Options {
    pub fn preserves_cell_field(&self, field: &str) -> bool {
        self.preserve_cell_metadata || self.preserve_cell_metadata_field.iter().any(|f| f == field)
    }

    pub fn filter_args(&self) -> Vec<&str> {
        let mut args = vec!["nb-clean", "clean"];
        for (enabled, flag) in [
            (self.remove_empty_cells, "--remove-empty-cells"),
            (
                self.remove_all_notebook_metadata,
                "--remove-all-notebook-metadata",
            ),
            (self.preserve_cell_metadata, "--preserve-cell-metadata"),
            (self.preserve_cell_outputs, "--preserve-cell-outputs"),
            (
                self.preserve_execution_counts,
                "--preserve-execution-counts",
            ),
            (
                self.preserve_notebook_metadata,
                "--preserve-notebook-metadata",
            ),
        ] {
            if enabled {
                args.push(flag);
            }
        }
        for field in &self.preserve_cell_metadata_field {
            args.extend(["--preserve-cell-metadata-field", field]);
        }
        args
    }
}

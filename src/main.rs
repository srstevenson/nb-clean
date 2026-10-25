mod cli;
mod error;
mod files;
mod git;
mod notebook;

use std::{
    io::{self, BufWriter, Read, Write},
    process::ExitCode,
};

use clap::Parser;
use cli::{Cli, Command, Inputs};
use error::Error;
use notebook::Notebook;

#[derive(Clone, Copy, PartialEq, Eq)]
enum Mode {
    Check,
    Clean,
}

fn main() -> ExitCode {
    let cli = match Cli::try_parse() {
        Ok(cli) => cli,
        Err(error) => {
            let code = if error.use_stderr() { 64 } else { 0 };
            let _ = error.print();
            return ExitCode::from(code);
        }
    };
    let result = match cli.command {
        Command::Check(inputs) => process(inputs, Mode::Check),
        Command::Clean(inputs) => process(inputs, Mode::Clean),
        Command::AddFilter(options) => git::add(&options).map(|()| 0),
        Command::RemoveFilter => git::remove().map(|()| 0),
    };
    match result {
        Ok(code) => ExitCode::from(code),
        Err(error) => {
            eprintln!("nb-clean: error: {error}");
            ExitCode::from(error.code)
        }
    }
}

fn process(inputs: Inputs, mode: Mode) -> Result<u8, Error> {
    let mut stdout = BufWriter::new(io::stdout().lock());
    if inputs.paths.is_empty() {
        let mut bytes = Vec::new();
        io::stdin()
            .lock()
            .read_to_end(&mut bytes)
            .map_err(|e| Error::new(74, e))?;
        let (output, dirty) = transform(&bytes, "stdin", &inputs.options, mode, &mut stdout)?;
        if mode == Mode::Clean {
            stdout
                .write_all(output.as_deref().unwrap_or(&bytes))
                .map_err(|e| Error::new(74, e))?;
        }
        stdout.flush().map_err(|e| Error::new(74, e))?;
        return Ok(u8::from(mode == Mode::Check && dirty));
    }
    let mut dirty = false;
    let mut error_code = None;
    for input in files::discover(&inputs.paths) {
        let result = input.and_then(|input| {
            let bytes = files::read(&input.target)?;
            let (output, changed) = transform(
                &bytes,
                &input.name.to_string_lossy(),
                &inputs.options,
                mode,
                &mut stdout,
            )?;
            if let Some(output) = output {
                files::replace(&input.target, &output)?;
            }
            Ok(changed)
        });
        match result {
            Ok(changed) => dirty |= changed,
            Err(error) => {
                eprintln!("nb-clean: error: {error}");
                error_code.get_or_insert(error.code);
            }
        }
    }
    stdout.flush().map_err(|e| Error::new(74, e))?;
    Ok(error_code.unwrap_or(u8::from(mode == Mode::Check && dirty)))
}

fn transform(
    bytes: &[u8],
    name: &str,
    options: &cli::Options,
    mode: Mode,
    stdout: &mut impl Write,
) -> Result<(Option<Vec<u8>>, bool), Error> {
    let mut notebook =
        Notebook::parse(bytes).map_err(|e| Error::new(65, format!("{name}: {e}")))?;
    let changes = notebook.changes(options);
    if changes.is_empty() {
        return Ok((None, false));
    }
    if mode == Mode::Clean {
        notebook.clean(&changes);
        let output = notebook
            .to_bytes()
            .map_err(|e| Error::new(65, format!("{name}: {e}")))?;
        Ok((Some(output), true))
    } else {
        for change in changes {
            writeln!(stdout, "{name} {change}").map_err(|e| Error::new(74, e))?;
        }
        Ok((None, true))
    }
}

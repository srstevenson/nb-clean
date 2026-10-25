"""Install a wheel in a fresh environment and test the packaged command."""

# Copyright 2026 Scott Stevenson. Distributed under the ISC licence.

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import venv
from email.parser import BytesParser
from functools import partial
from pathlib import Path
from zipfile import ZipFile


def check_metadata(wheel: Path) -> str:
    """Check the wheel contents and return its package version."""
    with ZipFile(wheel) as archive:
        names = archive.namelist()
        metadata_path = next(name for name in names if name.endswith("/METADATA"))
        metadata = BytesParser().parsebytes(archive.read(metadata_path))
        assert metadata["Name"] == "nb-clean"
        assert not metadata.get_all("Requires-Dist", [])
        assert not any(name.endswith(".py") for name in names)
        wheel_metadata = BytesParser().parsebytes(
            archive.read(metadata_path.removesuffix("METADATA") + "WHEEL"),
        )
        tags = wheel_metadata.get_all("Tag", [])
        assert tags
        assert all(tag.startswith("py3-none-") for tag in tags)
        version = metadata["Version"]
        assert isinstance(version, str)
        return version


def run_command(
    command: list[str | Path],
    data: bytes | None = None,
    *,
    root: Path,
    env: dict[str, str],
    expected_status: int = 0,
) -> subprocess.CompletedProcess[bytes]:
    """Run a test command and report its output if the exit status differs."""
    result = subprocess.run(  # noqa: S603 -- Test commands use argument lists, without a shell.
        command,
        input=data,
        capture_output=True,
        cwd=root,
        env=env,
        check=False,
    )
    assert result.returncode == expected_status, (
        result.args,
        result.returncode,
        result.stdout,
        result.stderr,
    )
    return result


def check_cli(binary: Path, version: str, root: Path, env: dict[str, str]) -> None:
    """Check command statuses, stdin cleaning, and file cleaning."""
    run = partial(run_command, root=root, env=env)
    assert run([binary, "--version"]).stdout == f"nb-clean {version}\n".encode()
    run([binary, "--help"])
    run([binary, "check", "--unknown"], expected_status=64)
    run([binary, "check"], b"not json", expected_status=65)

    fixtures = Path(__file__).resolve().parent / "notebooks"
    dirty = (fixtures / "dirty.ipynb").read_bytes()
    expected = (fixtures / "clean.ipynb").read_bytes().replace(b"\r\n", b"\n")
    run([binary, "check"], dirty, expected_status=1)
    assert run([binary, "clean"], dirty).stdout == expected
    run([binary, "check"], expected)
    assert run([binary, "clean"], expected).stdout == expected
    notebook = root / "notebook.ipynb"
    notebook.write_bytes(dirty)
    run([binary, "clean", str(notebook)])
    assert notebook.read_bytes() == expected


def check_git_filter(binary: Path, root: Path, env: dict[str, str]) -> None:
    """Check staging, metadata option quoting, and filter removal."""
    git_path = shutil.which("git")
    assert git_path is not None
    run = partial(run_command, root=root, env=env)
    run([git_path, "init", "-q"])
    fields = ["-tags", "owner's $(echo injected)"]
    retained_metadata = dict.fromkeys(fields, True)
    value = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {},
        "cells": [
            {
                "cell_type": "code",
                "source": ["x"],
                "metadata": {**retained_metadata, "remove": True},
                "execution_count": 1,
                "outputs": [],
            },
        ],
    }
    original = json.dumps(value).encode()
    notebook = root / "notebook.ipynb"
    notebook.write_bytes(original)
    run(
        [
            binary,
            "add-filter",
            *[f"--preserve-cell-metadata-field={field}" for field in fields],
        ],
    )
    staged_result = run([git_path, "add", "notebook.ipynb"])
    assert not staged_result.stderr, staged_result.stderr
    staged = json.loads(run([git_path, "show", ":notebook.ipynb"]).stdout)
    assert staged["cells"][0]["execution_count"] is None
    assert staged["cells"][0]["metadata"] == retained_metadata
    assert notebook.read_bytes() == original
    run([binary, "remove-filter"])


def check_wheel(wheel: Path, root: Path) -> None:
    """Install the wheel and check its command in an isolated environment."""
    version = check_metadata(wheel)
    environment = root / "venv"
    venv.EnvBuilder(with_pip=True, symlinks=os.name != "nt").create(environment)
    scripts = environment / ("Scripts" if os.name == "nt" else "bin")
    python = scripts / ("python.exe" if os.name == "nt" else "python")
    subprocess.run(  # noqa: S603 -- Run pip from the temporary environment without a shell.
        [
            python,
            "-m",
            "pip",
            "install",
            "--no-cache-dir",
            "--no-index",
            "--no-deps",
            str(wheel),
        ],
        check=True,
    )
    binary = scripts / ("nb-clean.exe" if os.name == "nt" else "nb-clean")
    env = {
        **os.environ,
        "PATH": str(scripts) + os.pathsep + os.environ.get("PATH", ""),
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
    }
    check_cli(binary, version, root, env)
    check_git_filter(binary, root, env)
    print(f"Wheel checks passed: {wheel.name}")  # noqa: T201 -- CLI success message.


def main() -> None:
    """Check the single wheel in the supplied directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    wheels = list(args.directory.glob("*.whl"))
    if len(wheels) != 1:
        parser.error("expected exactly one wheel in the directory")
    with tempfile.TemporaryDirectory(prefix="nb-clean-wheel-") as directory:
        check_wheel(wheels[0].resolve(), Path(directory))


if __name__ == "__main__":
    main()

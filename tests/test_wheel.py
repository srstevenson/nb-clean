#!/usr/bin/env python3
"""Install a wheel in a fresh environment and test the packaged command."""

import argparse
import json
import os
import subprocess
import tempfile
import venv
from email.parser import BytesParser
from pathlib import Path
from zipfile import ZipFile


def check_wheel(wheel, root):
    with ZipFile(wheel) as archive:
        names = archive.namelist()
        metadata_path = next(name for name in names if name.endswith("/METADATA"))
        metadata = BytesParser().parsebytes(archive.read(metadata_path))
        assert metadata["Name"] == "nb-clean"
        assert not metadata.get_all("Requires-Dist")
        assert not any(name.endswith(".py") for name in names)
        assert not any("PLAN.md" in name for name in names)
        wheel_metadata = BytesParser().parsebytes(archive.read(metadata_path.replace("METADATA", "WHEEL")))
        assert all(tag.startswith("py3-none-") for tag in wheel_metadata.get_all("Tag"))

    environment = root / "venv"
    venv.EnvBuilder(with_pip=True, symlinks=os.name != "nt").create(environment)
    scripts = environment / ("Scripts" if os.name == "nt" else "bin")
    python = scripts / ("python.exe" if os.name == "nt" else "python")
    subprocess.run(
        [str(python), "-m", "pip", "install", "--no-cache-dir", "--no-index", "--no-deps", str(wheel)],
        check=True,
    )
    binary = scripts / ("nb-clean.exe" if os.name == "nt" else "nb-clean")
    env = {
        **os.environ,
        "PATH": str(scripts) + os.pathsep + os.environ.get("PATH", ""),
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
    }

    def run(args, data=None):
        return subprocess.run([str(binary), *args], input=data, capture_output=True, cwd=root, env=env)

    assert run(["--version"]).stdout == f"nb-clean {metadata['Version']}\n".encode()
    assert run(["--help"]).returncode == 0
    assert run(["check", "--unknown"]).returncode == 64
    assert run(["check"], b"not json").returncode == 65

    fixtures = Path(__file__).resolve().parents[1] / "tests" / "notebooks"
    dirty = (fixtures / "dirty.ipynb").read_bytes()
    expected = (fixtures / "clean.ipynb").read_bytes().replace(b"\r\n", b"\n")
    assert run(["check"], dirty).returncode == 1
    cleaned = run(["clean"], dirty)
    assert cleaned.returncode == 0, cleaned.stderr
    assert cleaned.stdout == expected
    assert run(["check"], expected).returncode == 0
    assert run(["clean"], expected).stdout == expected
    notebook = root / "notebook.ipynb"
    notebook.write_bytes(dirty)
    assert run(["clean", str(notebook)]).returncode == 0
    assert notebook.read_bytes() == expected

    def git(args):
        return subprocess.run(["git", *args], cwd=root, env=env, capture_output=True, check=True)

    git(["init", "-q"])
    fields = ["-tags", "owner's $(echo injected)"]
    value = {
        "nbformat": 4, "nbformat_minor": 5, "metadata": {},
        "cells": [{
            "cell_type": "code", "source": ["x"],
            "metadata": {**dict.fromkeys(fields, True), "remove": True},
            "execution_count": 1, "outputs": [],
        }],
    }
    original = json.dumps(value).encode()
    notebook.write_bytes(original)
    installed = run(["add-filter", *[f"--preserve-cell-metadata-field={field}" for field in fields]])
    assert installed.returncode == 0, installed.stderr
    staged_result = git(["add", "notebook.ipynb"])
    assert not staged_result.stderr, staged_result.stderr
    staged = json.loads(git(["show", ":notebook.ipynb"]).stdout)
    assert staged["cells"][0]["execution_count"] is None
    assert staged["cells"][0]["metadata"] == dict.fromkeys(fields, True)
    assert notebook.read_bytes() == original
    assert run(["remove-filter"]).returncode == 0
    print(f"Wheel checks passed: {wheel.name}")


def main():
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

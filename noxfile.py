"""Nox configuration."""

import nox

SOURCES = ["noxfile.py", "src"]


def install_dependencies(session):
    """Install Poetry and project dependencies."""
    session.install("poetry")
    session.run("poetry", "install")


@nox.session
def mypy(session):
    """Type check code with mypy."""
    install_dependencies(session)
    session.run("poetry", "run", "mypy", "--strict", "src")


@nox.session
def flake8(session):
    """Lint code with Flake8."""
    install_dependencies(session)
    session.run("poetry", "run", "flake8", *SOURCES)


@nox.session
def pylint(session):
    """Lint code with Pylint."""
    install_dependencies(session)
    session.run("poetry", "run", "pylint", *SOURCES)


@nox.session
def isort(session):
    """Check import ordering with isort."""
    install_dependencies(session)
    session.run(
        "poetry", "run", "isort", "--check-only", "--recursive", *SOURCES
    )


@nox.session
def black(session):
    """Check code formatting with black."""
    install_dependencies(session)
    session.run("poetry", "run", "black", "--check", *SOURCES)

"""Nox configuration."""

import nox

SOURCES = ["noxfile.py", "src"]


@nox.session
def mypy(session):
    """Type check code with mypy."""
    session.run("mypy", "--strict", "src", external=True)


@nox.session
def flake8(session):
    """Lint code with Flake8."""
    session.run("flake8", *SOURCES, external=True)


@nox.session
def pylint(session):
    """Lint code with Pylint."""
    session.run("pylint", *SOURCES, external=True)


@nox.session
def isort(session):
    """Check import ordering with isort."""
    session.run(
        "isort", "--check-only", "--recursive", *SOURCES, external=True
    )


@nox.session
def black(session):
    """Check code formatting with black."""
    session.run("black", "--check", *SOURCES, external=True)

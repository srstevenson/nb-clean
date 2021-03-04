"""Nox configuration."""

import nox

SOURCES = ["noxfile.py", "src", "tests"]


@nox.session
def mypy(session):
    """Type check code with mypy."""
    session.run("mypy", *SOURCES, external=True)


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
    session.run("isort", "--check", *SOURCES, external=True)


@nox.session
def black(session):
    """Check code formatting with black."""
    session.run("black", "--check", *SOURCES, external=True)


@nox.session
def pytest(session):
    """Run unit tests with pytest."""
    session.run("pytest", "--cov=nb_clean", "tests", external=True)

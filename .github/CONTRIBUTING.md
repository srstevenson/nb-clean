# Contributing

Thanks for considering contributing! The following is a set of guidelines for
doing so. They're guidelines rather than rules, so follow your best judgement,
but reading them will help make the contribution process easier and more
effective for both you and the maintainers.

## Reporting issues

GitHub issues are used for managing bug reports and feature requests, except
security vulnerabilities: these should be emailed to the maintainers instead.

Search for existing issues before creating a new one, to ensure your problem
hasn't already been reported. If it has, you're welcome to comment on the
existing issue with extra information that might help reproduce and fix the
problem, or sharing why a feature would be useful, but refrain from "+1" type
comments. Duplicate issues will be closed with a reference to the existing
issue.

In your report describe what you did, what you expected to happen, and what
happened instead. Provide a [minimal reproducible example][mre] that the
maintainers can run. Provide as much detail as you can in your description of
the problem, including the version of the project you're using, and details of
your operating system and environment, and other information which might help
diagnose the problem, such as what you've already tried to fix it.

## Contributing changes

### Planning

When you contribute a new change, the responsibility for maintenance is (by
default) transferred to the existing project maintainers. The benefit of the
contribution must be weighed against the cost of maintaining it.

If you're considering contributing a non-trivial bugfix or feature, discuss the
changes you plan to make before you start coding by opening an issue. This
ensures your proposed change will be accepted, and provides the maintainers the
opportunity to help you.

### Implementation

Changes are managed using GitHub pull requests. If you're new to pull requests,
read the [documentation][pr docs] to learn how they work.

[uv] is used for managing dependencies and packaging, and you will need it
installed. If you're not familiar with uv, we suggest reading its documentation
before you begin.

After cloning the repository, you can implement your changes as follows:

1. Install the project and its dependencies into an isolated virtual environment
   with `uv sync --dev`.
2. Before making your changes, run the tests with `uv run pytest`, and ensure
   they pass. This checks your development environment is correctly configured,
   and there aren't outstanding issues before you start coding. If they don't
   pass, you can open a GitHub issue for help debugging.
3. Checkout a new branch for your changes, branching from `main`, with a
   sensible name for your changes.
4. Implement your changes.
5. If you introduced new functionality or fixed a bug, add appropriate automated
   tests to prevent future regressions.
6. Ensure you've updated any docstrings or documentation files (including
   `README.md`) which are affected by your change.
7. Run the linter with `uv run ruff check .`, formatter with
   `uv run ruff format .`, type checker with `uv run basedpyright .`, and tests
   with `uv run pytest`, and fix any problems.
8. Commit your changes, following [these guidelines][commit guidelines] for your
   commit messages.
9. Fork the base repository on GitHub, push your branch to your fork, and open a
   pull request against the base repository. Make sure your pull request has a
   clear title and description. The easier your changes are to understand, the
   easier it is for the maintainers to approve and merge them.
10. Your pull request will be reviewed by the maintainers and either merged, or
    feedback will be provided on changes that are required.

[commit guidelines]:
  https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
[mre]: https://stackoverflow.com/help/minimal-reproducible-example
[pr docs]: https://docs.github.com/en/github/collaborating-with-pull-requests
[uv]: https://docs.astral.sh/uv/

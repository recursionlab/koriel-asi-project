# Contributing

Thank you for your interest in improving this project!

## Coding conventions
- Place library code in `src/` and keep exploratory scripts in `experiments/`.
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines.
- Use clear naming and add docstrings for public functions and classes.

## Pre-commit hooks
- Install the formatting and linting hooks:

  ```bash
  pip install pre-commit
  pre-commit install
  ```

- Run the hooks on changed files before committing:

  ```bash
  pre-commit run --files <file1> [<file2> ...]
  ```

  To check the entire codebase, use:

  ```bash
  pre-commit run --all-files
  ```

## Testing
- Add unit tests for new features in the `tests/` directory.
- Before submitting a pull request run:
  ```bash
  python -m py_compile $(git ls-files '*.py')
  pytest tests
  pytest benchmarks  # optional: runs benchmark smoke tests
  ```

## Release workflow
1. Ensure the main branch is green (all checks passing).
2. Update version information and changelog if needed.
3. Create a git tag and push it to GitHub.
4. GitHub Actions will build and test the release. After it succeeds, create a new GitHub Release.

We appreciate your contributions!


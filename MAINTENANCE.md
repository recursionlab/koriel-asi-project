Maintenance checklist — koriel-asi-project

Purpose

This document records the short-term and medium-term maintenance tasks for the repository so work can be safely resumed later.

Quick checklist (first pass)

- [x] Confirmed local changes were committed and pushed to origin/main (commit: 43a448d).
- [ ] Run repo-wide linter (ruff) and fix issues.
- [ ] Run type checks (mypy) and triage third-party stubs / type errors.
- [ ] Run unit tests and smoke tests; fix any failures.
- [ ] Address Dependabot/GitHub Security alerts.
- [ ] Add or enable pre-commit hooks (ruff, black, isort, mypy fast checks).
- [ ] Decide branching workflow: create feature branches + PRs instead of direct pushes to main.
- [ ] Configure CI to run: ruff, mypy, unit tests, coverage reporting.
- [ ] Add CODEOWNERS / reviewers and merge policy (protected branches) if desired.

Detailed steps and commands

1) Lint the whole repo with ruff

Run locally:

```bash
cd /workspaces/koriel-asi-project
ruff check .
# to auto-fix where possible
ruff check --fix .
```

2) Type-checking with mypy

Notes: SciPy/numpy may need typed stubs; use `types-` packages or `pyproject.toml`/`mypy.ini` to configure ignores.

```bash
# Use the project's python environment
pip install -r requirements.txt
# install dev stubs if needed
pip install types-numpy types-scipy mypy
mypy .
```

If mypy shows many third-party issues, two options:
- Install typed stub packages (recommended).
- Add targeted `# type: ignore` or narrow annotations where safe.

3) Run tests and a smoke test

```bash
pytest -q
# run the existing small smoke tests
python - <<'PY'
from quantum_consciousness_field import QuantumConsciousnessField
f = QuantumConsciousnessField(N=64, L=10.0, dt=0.01, enable_self_mod=False)
f.initialize_seed_state('random_coherent')
f.evolve_field(1)
print('smoke OK')
PY
```

4) CI / GitHub Actions

- Ensure workflows run on PRs and on pushes to main (lint, mypy, tests, build).
- Configure status checks required for merging on protected branch settings.
- Verify the newly added workflows under `.github/workflows/` are enabled in the repo Actions tab.

5) Dependabot / Security

- Visit the repository Security → Dependabot page and inspect the moderate vulnerability flagged after the last push.
- Apply suggested dependency updates or create a PR updating the affected package(s).

6) Branching and PR workflow (recommended)

- Create feature branches for changes and open PRs instead of committing directly to main.
- Example:

```bash
git checkout -b fix/quantum-field-lint
# make edits, commit
git push -u origin fix/quantum-field-lint
# open a PR on GitHub
```

7) Pre-commit and dev environment

- Add (or enable) pre-commit with hooks for ruff, black, isort, and simple mypy checks.

```bash
pip install pre-commit
pre-commit install
# run all hooks once
pre-commit run --all-files
```

8) Incremental cleaning strategy

- Triage one file at a time.
- For each file: apply a single small change → run compile (python -m compileall .) → run ruff → run mypy (if applicable) → run a small smoke/test that exercises the changed code.

9) Documentation and release notes

- Keep a short CHANGELOG or PR descriptions for larger behavior-affecting edits.
- Commit small non-functional changes (formatting, docstrings) on separate PRs.

10) Future improvements (nice-to-have)

- Add type annotations progressively and add `pyright` or stricter mypy config for service code.
- Add CI caching for pip/venv to speed up checks.
- Add automated vulnerability updates via Dependabot config.

Who to contact / next owner

- If you return to this repo later, start from this file. The next actionable tasks are running ruff and mypy, triaging type errors, then running tests.

Notes

- I committed and pushed current workspace changes to `origin/main` (commit 43a448d). If you'd like changes to be landed via PR instead of directly to main next time, create a branch and open a PR.
- I preserved runtime behavior in `quantum_consciousness_field.py` and ran a smoke test locally. The file is importable and a 1-step evolve runs successfully.

Timestamp: 2025-09-06

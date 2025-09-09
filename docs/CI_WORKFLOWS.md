# CI/CD Workflows

This repository uses consolidated GitHub Actions workflows for reliable continuous integration and extended automations.

## Core CI Pipeline (`core-ci.yml`)

**Purpose**: Essential checks that must pass for all pull requests and pushes to main.

**Triggers**: 
- Push to `main` or `refactor/*` branches
- Pull requests to `main`

**Jobs**:
- **lint**: Code quality checks (ruff, mypy, wildcard import detection)
- **unit-tests**: Unit and integration tests on Python 3.11 & 3.12
- **determinism-tests**: Reproducibility validation tests
- **smoke-tests**: Basic functionality and CLI tests

**Developer Notes**:
- Fast execution (< 5 minutes typical)
- Clear failure reporting
- Minimal setup requirements
- Must pass for merge approval

## Extended Automations (`automations.yml`)

**Purpose**: Non-blocking automation features that enhance the development workflow.

**Triggers**:
- PDF files added to `research/new/`
- Manual workflow dispatch
- Nightly schedule (2 AM UTC)

**Jobs**:
- **pdf-ingest**: Automatically processes new research PDFs, creates stubs, and opens PRs
- **nightly-sitrep**: Generates status reports and system health checks

**Developer Notes**:
- Runs separately from core CI
- Does not block development workflow
- Creates PRs for review when appropriate
- Provides automated maintenance tasks

## Migration Notes

The previous CI setup used multiple overlapping workflows (`ci.yaml`, `ci-enforce.yml`, `bot-verify.yml`, `ingest.yml`) which created confusion and potential conflicts. This consolidation:

1. **Eliminates duplication**: Single source of truth for core checks
2. **Improves reliability**: Clear separation of blocking vs non-blocking tests  
3. **Reduces friction**: Developers know exactly what must pass for merge
4. **Maintains automation**: All useful automation features preserved

## Backup Files

Previous workflow configurations are preserved as `.bak` files for reference:
- `.github/workflows/ci-old.yaml.bak`
- `.github/workflows/ci-enforce.yml.bak`  
- `.github/workflows/ingest.yml.bak`
- `.github/workflows/bot-verify.yml.bak`

These files are excluded from version control but available locally if needed.
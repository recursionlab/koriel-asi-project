# ADR-0001: Interface Contracts and Legacy Shim Policy

Status: Proposed

Date: 2025-09-09

Context
-------
Phase 0 of the Great Decomposition introduces strict, typed interfaces under `src/koriel/*` while
keeping legacy monolithic implementations functional during the transition. Tests and external
callers still depend on legacy symbols such as `SimpleQuantumField`, `FieldObservation`, and
`PatternMemory` exported from `koriel.field`.

Decision
--------
1. Publish minimal, language-level contracts for core abstractions:
   - `EngineProtocol` (high-level orchestration contract)
   - `FieldInterface[T]` (generic field substrate contract)
   - `OperatorSpec` (operator metadata contract)

2. Provide a compatibility shim in package initializers (e.g. `koriel.field.__init__`) that
   lazily loads legacy implementation files from their original locations and re-exports a
   limited set of legacy symbols. The shim must:
   - Avoid circular imports by loading legacy files via `importlib.util.spec_from_file_location`
     under a non-conflicting module name.
   - Only re-export a small, explicitly enumerated set of symbols.
   - Emit deprecation guidance in docs and produce a DeprecationWarning via docs/notes (not
     strictly required at Phase 0 but recommended later).

3. Require a contract test asserting legacy imports remain available. This prevents regressions
   caused by refactors that move or rename legacy files without adding a replacement shim.

Consequences
------------
- Positive: Low-risk, incremental migration path; consumer code continues to work during
  decomposition.
- Negative: Maintains dual-loading strategy; future work should aim to remove legacy files and
  consolidate names to avoid the shim.

Fallback/Rollback
-----------------
If the shim causes unexpected behavior, remove the shim and revert to the immediately previous
commit. The ADR must be revisited to choose a different migration strategy (e.g., name prefixing
legacy files with `_legacy` to avoid name collisions).

Tests and Validation
--------------------
- Add `tests/test_legacy_imports.py` asserting `from koriel.field import SimpleQuantumField, FieldObservation, PatternMemory` succeeds.
- Run full pytest and mypy (subset) during CI.

Related
-------
- Docs: docs/architecture/decomposition.md
- Future: ADR-0002 (Operator Registry)

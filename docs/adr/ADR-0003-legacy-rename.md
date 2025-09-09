# ADR-0003: Legacy Implementation Rename & Migration Policy

Status: Accepted

Date: 2025-09-09

Context
-------
As Phase 0 decomposition proceeds, legacy monolithic modules must be renamed to
clearly indicate they are implementation artifacts. This prevents name collisions
with new, interface-first packages and simplifies compatibility shims.

Decision
--------
1. Rename legacy concrete modules from `field.py` to `field_legacy_impl.py`.
2. Replace `koriel.field` package-level monolith with a small package/shim that
   re-exports a narrow set of legacy symbols for backward compatibility.
3. Add a documented deprecation path: module-level `__getattr__` issues a
   DeprecationWarning when legacy symbols are accessed. The warning points to the
   ADR and recommended replacements.

Migration Steps
---------------
- Move file `src/koriel/field.py` -> `src/koriel/field_legacy_impl.py`.
- Create `src/koriel/field.py` shim that re-exports legacy symbols and the
  new `koriel.field` package continues to expose interfaces in `koriel.field.*`.
- Update tests to import from `koriel.field` (already done in Phase 0). Add
  `tests/test_legacy_imports.py` to guard against regressions.

Consequences
------------
- Improves clarity between interface and implementation.
- Removes ad-hoc dynamic import logic. Simplifies CI and type-checking.

Rollback
--------
If regressions appear, revert the rename commit and restore the previous shim
approach; update ADR to choose alternate migration strategy.

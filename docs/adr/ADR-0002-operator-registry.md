# ADR-0002: Operator Registry Contract

Status: Proposed

Date: 2025-09-09

Context
-------
Operators provide effectful transformations applied to field substrates. A lightweight
Operator Registry is useful to centralize metadata (name, arity, category, safety tags) and
support discovery without coupling to implementation.

Decision
--------
1. Implement an in-memory `OperatorRegistry` with a minimal `OperatorEntry` dataclass.
2. Public API:
   - `register(entry: OperatorEntry) -> None` — register new operator; raise on duplicate.
   - `get(name: str) -> Optional[OperatorEntry]` — retrieve metadata.
   - `list() -> List[OperatorEntry]` — list all entries.
3. Tests will exercise registration and retrieval; consumers may adopt the registry via
   dependency injection.

Consequences
------------
- Low complexity, easy to unit test and roll back. Future versions may add persistence or
  namespacing.

# Legacy Decomposition Mapping (Phase 0)

This document tracks migration of legacy monolithic symbols into modular structured packages.

| LegacySymbol              | SourceFile                          | TargetModule                        | MigrationStatus | Notes |
|--------------------------|-------------------------------------|-------------------------------------|-----------------|-------|
| FieldState               | quantum_consciousness_field.py      | koriel.field.state                  | Done            | Extracted + shim warning in legacy file |
| GoalManifold             | quantum_goal_manifold.py            | koriel.field.goal (future)          | Planned         | Will need interface formalization |
| OperatorRegistry         | koriel_operator.py                  | koriel.operators.registry (future)  | Planned         | Must emit structured metadata |
| ConsciousnessInterface   | consciousness_interface.py          | koriel.interface.consciousness      | Planned         | Needs separation I/O vs semantics |
| QRFTChatSession          | qrft_chat.py                        | koriel.interface.session (future)   | Planned         | Convert to Session API |

## Phase 0 Migration Policy
- INV-1: All new modules under `src/koriel/*` pass strict mypy (incrementally expanded).
- INV-2: `EngineProtocol` and `FieldInterface` define the core decomposition targets; all extractions must not violate their surface expectations.

## Migration Checklist Template (apply per symbol)
- [ ] Extract
- [ ] Add shim + DeprecationWarning
- [ ] Add or extend tests
- [ ] Update this table (Planned → In-Progress → Done)
- [ ] Remove legacy after stable (≥2 releases) or explicit ADR

## Current Phase Actions
FieldState extraction completed; validating compatibility layer via re-exports and shim.

## ADR References (to create)
- ADR-0001: Engine & Field Interface Contracts
- ADR-0002: Operator Specification & Registry Protocol (future)
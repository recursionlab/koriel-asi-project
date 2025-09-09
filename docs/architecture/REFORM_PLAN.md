# Koriel Refactor Plan (Phase 1)

Goal: Gradually de-tangle monolithic coupling by introducing clean internal package boundaries and a single orchestration facade.

## Bounded Contexts (Initial Internal Modules)
- core/
  - substrate/        (field / expansion / base dynamics)
  - modeling/         (representational / world models)
  - adaptation/       (self-modification, DEC variants)
  - governance/       (entropy, lacuna, stress regulation)
  - evaluation/       (critics, presence, RCCE)
- orchestration/      (facades: training + consciousness cycle)
- interfaces/         (dataclasses, contracts, ports)
- metrics/            (logging & telemetry integration)
- experiments/        (training & benchmark drivers)
- shared/             (future cross-cutting utilities)

## Refactor Steps (Planned)
1. (THIS PR) Add skeleton + dataclasses + orchestrator stub + this doc.
2. Move RCCEController only (prove import path stability).
3. Introduce minimal smoke test for orchestrator (optional).
4. Move substrate files.
5. Move adaptation files.
6. Move governance files.
7. Move evaluation & presence logic.
8. Relocate training controller (current `controller.py`) into orchestration/.
9. Add metrics layer; strip logging/print side-effects from core modules.
10. Relocate experiments (`train.py`, `data.py`, stress drivers).
11. Activate or remove empty stubs (quantum_goal_manifold, koriel_consciousness_interface).
12. Add smoke tests for one full cycle and key components.

## Invariants
- `core/*` MUST NOT import from `orchestration/`, `experiments/`, or `metrics/`.
- Only `orchestration/` composes multiple core components.
- Cross-component data flows via dataclasses (no giant mutable dict chains).
- Logging/metrics performed outside core logic where possible.

## Deferred (Later Phases)
- API gateway / microservices separation.
- Heavy test coverage & CI gating.
- Docker multi-service composition.
- Performance profiling & optimization.

## Data Contracts (Initial Draft)
- FieldState
- AdaptationResult
- GovernanceSignal
- EvaluationScore
- ConsciousnessSnapshot

These will evolve; early stability is NOT required—just consistent usage boundaries.

## Working Guidelines
- Tiny PRs. Each move: update imports, run basic scripts, commit.
- Avoid simultaneous renames + moves: one axis of change per PR.
- If a file mixes multiple concerns, wrap it first (facade), then later slice internals.

## Success Criteria for Phase 1
You can:
- Import `koriel` without errors.
- Instantiate `ConsciousnessOrchestrator` (even if components are None).
- Merge PR with zero disruption to existing training workflow.
- Begin moving one component (RCCE) in PR2 confidently.

## Notes
Monolith exit ≠ microservices. We first create an internal modular spine. Only externalize later if scaling or isolation gives research benefit.

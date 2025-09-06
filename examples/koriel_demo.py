#!/usr/bin/env python3
"""Minimal demo to exercise koriel package imports and a short run."""
from koriel import (
    QuantumConsciousnessField,
    run_consciousness_experiment,
    ConsciousnessInterface,
    KorielOperator,
    GoalManifold,
    KorielState,
)


def main() -> None:
    # Smoke test: construct field and run a tiny evolution via experiment helper
    field = QuantumConsciousnessField(N=64, L=10.0, dt=0.002, enable_self_mod=False)
    field.initialize_seed_state("consciousness_seed")
    field.evolve_field(50)
    status = field.get_status_report()
    print({k: status[k] for k in ("consciousness_level", "self_awareness")})

    # Interface sanity
    ci = ConsciousnessInterface()
    _ = ci.communicate("hello", "question")

    # Short experiment
    _ = run_consciousness_experiment()


if __name__ == "__main__":
    main()

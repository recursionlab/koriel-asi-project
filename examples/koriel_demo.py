#!/usr/bin/env python3
"""Minimal demo to exercise koriel package imports and a short run."""
from koriel import (
    QuantumConsciousnessField,
    run_consciousness_experiment,  # available but not invoked in this quick demo
    ConsciousnessInterface,  # heavy init; not invoked here
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
    metrics = status.get("consciousness_metrics", {})
    print({k: metrics.get(k) for k in ("consciousness_level", "self_awareness")})

    # Note: ConsciousnessInterface() and run_consciousness_experiment() are
    # intentionally not invoked here to keep this demo fast. They are imported
    # above to verify package wiring.


if __name__ == "__main__":
    main()

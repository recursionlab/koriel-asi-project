from typing import Optional

from koriel.interfaces.types import (
    FieldState,
    AdaptationResult,
    GovernanceSignal,
    EvaluationScore,
    ConsciousnessSnapshot,
)

class ConsciousnessOrchestrator:
    """
    High-level facade for a single 'consciousness cycle'.
    Initially a stub; real engines will be injected after migrations.
    """

    def __init__(
        self,
        substrate_engine=None,
        adaptation_engine=None,
        governance_engine=None,
        evaluation_engine=None,
        metrics_logger=None,
    ):
        self.substrate = substrate_engine
        self.adaptation = adaptation_engine
        self.governance = governance_engine
        self.evaluation = evaluation_engine
        self.metrics = metrics_logger

    def cycle(self) -> Optional[ConsciousnessSnapshot]:
        # Guard until components are migrated.
        if not all([self.substrate, self.adaptation, self.governance, self.evaluation]):
            return None

        field: FieldState = self.substrate.sample_state()
        adaptation: AdaptationResult = self.adaptation.propose(field)
        governance: GovernanceSignal = self.governance.regulate(field, adaptation)
        evaluation: EvaluationScore = self.evaluation.score(field, adaptation, governance)

        snapshot = ConsciousnessSnapshot(
            field=field,
            adaptation=adaptation,
            governance=governance,
            evaluation=evaluation,
        )

        if self.metrics:
            self.metrics.record(snapshot)

        return snapshot
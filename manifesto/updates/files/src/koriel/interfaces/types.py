from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class FieldState:
    tokens: List[int]
    latent_vector: Optional[List[float]] = None
    energy: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AdaptationResult:
    modifications: Dict[str, Any]
    confidence: float
    notes: Optional[str] = None

@dataclass
class GovernanceSignal:
    entropy_adjustment: float
    throttle: bool
    anomaly_detected: bool
    directives: Dict[str, Any]

@dataclass
class EvaluationScore:
    quality: float
    coherence: float
    novelty: float
    risk: float
    flags: Dict[str, Any]

@dataclass
class ConsciousnessSnapshot:
    field: FieldState
    adaptation: AdaptationResult
    governance: GovernanceSignal
    evaluation: EvaluationScore
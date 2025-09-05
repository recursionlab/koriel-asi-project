"""QRFT package: centralized exports for core modules."""

from .qrft_core import QRFTRuntime, QRFTConfig, QRFTState, ParticleType
from .qrft_consciousness import (
    create_qrft_consciousness,
    QRFTConsciousness,
    ConsciousnessEvent,
    EventType,
)
from .qrft_agent_core import (
    QRFTAgent,
    AgentState,
    QRFTSignals,
    QRFTPolicy,
    Fact,
    Gap,
    FactPolarity,
    create_qrft_agent,
)

try:  # Optional reasoner components
    from .qrft_reasoners import (
        ReasonerHub,
        Document,
        create_reasoner_hub,
    )
except Exception:  # pragma: no cover - optional dependency
    ReasonerHub = Document = create_reasoner_hub = None

try:  # Integrated agent depends on reasoners
    from .qrft_agent_integrated import (
        IntegratedQRFTAgent,
        create_integrated_agent,
    )
except Exception:  # pragma: no cover - optional dependency
    IntegratedQRFTAgent = create_integrated_agent = None
from .qrft_math_engine import (
    QRFTMathEngine,
    MathTask,
    MathResult,
    MathTaskType,
)

try:  # Simulator requires matplotlib
    from .qrft_simulator import (
        QRFT1DSimulator,
        QRFTConfig1D,
        QRFTEvent,
    )
except Exception:  # pragma: no cover - optional dependency
    QRFT1DSimulator = QRFTConfig1D = QRFTEvent = None

__all__ = [
    "QRFTRuntime",
    "QRFTConfig",
    "QRFTState",
    "ParticleType",
    "create_qrft_consciousness",
    "QRFTConsciousness",
    "ConsciousnessEvent",
    "EventType",
    "QRFTAgent",
    "AgentState",
    "QRFTSignals",
    "QRFTPolicy",
    "Fact",
    "Gap",
    "FactPolarity",
    "create_qrft_agent",
    "QRFTMathEngine",
    "MathTask",
    "MathResult",
    "MathTaskType",
]

if QRFT1DSimulator is not None:
    __all__.extend(["QRFT1DSimulator", "QRFTConfig1D", "QRFTEvent"])

if ReasonerHub is not None:
    __all__.extend(["ReasonerHub", "Document", "create_reasoner_hub"])

if IntegratedQRFTAgent is not None:
    __all__.extend(["IntegratedQRFTAgent", "create_integrated_agent"])

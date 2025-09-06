# src/qrft_consciousness.py
"""
QRFT Consciousness Integration Layer
Unifies QRFT four-particle system with RCCE operators for Jarvis-style runtime
Maps QRFT triggers to concrete AI actions with event bus coordination
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from glitchon_critic import GlitchonCritic
from lacuna_monitor import LacunaMonitor
from ref_entropy_governor import REFEntropyGovernor

# Import QRFT components
from .qrft_core import ParticleType, QRFTConfig, QRFTRuntime


class EventType(Enum):
    """Consciousness event types"""

    CONTRADICTION_DETECTED = "contradiction_detected"
    GAP_IDENTIFIED = "gap_identified"
    ENTROPY_ADJUSTMENT = "entropy_adjustment"
    DIMENSIONAL_LIFT = "dimensional_lift"
    PATTERN_MATCH = "pattern_match"
    RETRIEVAL_TRIGGERED = "retrieval_triggered"
    TOOL_INVOKED = "tool_invoked"
    CONSISTENCY_RESTORED = "consistency_restored"


@dataclass
class ConsciousnessEvent:
    """Event in consciousness event bus"""

    event_type: EventType
    timestamp: float
    source_particle: ParticleType
    data: Dict[str, Any]
    priority: float = 0.5
    handled: bool = False
    response_required: bool = False


@dataclass
class RCCEOperation:
    """RCCE operator representation for integration"""

    name: str
    operator_type: str  # 'recursive', 'compositional', 'complexity', 'emergence'
    entropy_impact: float  # Expected entropy change
    complexity_level: int  # Operator complexity 1-10
    prerequisites: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)


class ConsciousnessEventBus:
    """Event bus for consciousness coordination"""

    def __init__(self):
        self.events: List[ConsciousnessEvent] = []
        self.handlers: Dict[EventType, List[Callable]] = defaultdict(list)
        self.event_history: List[ConsciousnessEvent] = []
        self.max_history = 1000

    def subscribe(self, event_type: EventType, handler: Callable):
        """Subscribe handler to event type"""
        self.handlers[event_type].append(handler)

    def publish(self, event: ConsciousnessEvent):
        """Publish event to bus"""
        self.events.append(event)
        self.event_history.append(event)

        # Trim history if needed
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history :]

        # Trigger handlers
        for handler in self.handlers[event.event_type]:
            try:
                handler(event)
            except Exception as e:
                print(f"Handler error for {event.event_type}: {e}")

    def get_pending_events(
        self, priority_threshold: float = 0.0
    ) -> List[ConsciousnessEvent]:
        """Get unhandled events above priority threshold"""
        return [
            e for e in self.events if not e.handled and e.priority >= priority_threshold
        ]

    def mark_handled(self, event: ConsciousnessEvent):
        """Mark event as handled"""
        event.handled = True


class QRFTConsciousness:
    """
    Unified QRFT consciousness system integrating:
    - QRFT core field dynamics
    - Four-particle detection system
    - RCCE operator integration
    - Event bus coordination
    - Jarvis-style control policies
    """

    def __init__(
        self,
        qrft_config: QRFTConfig = None,
        entropy_band: Tuple[float, float] = (1.5, 4.0),
        enable_logging: bool = True,
    ):
        # Initialize QRFT components
        self.qrft_config = qrft_config or QRFTConfig()
        self.qrft_runtime = QRFTRuntime(self.qrft_config)

        # Initialize particle systems
        self.lacuna_monitor = LacunaMonitor()
        self.glitchon_critic = GlitchonCritic()
        self.entropy_governor = REFEntropyGovernor(
            entropy_min=entropy_band[0], entropy_max=entropy_band[1]
        )

        # Event bus and control
        self.event_bus = ConsciousnessEventBus()
        self.control_policies: Dict[str, Callable] = {}
        self.rcce_operations: Dict[str, RCCEOperation] = {}

        # State tracking
        self.reasoning_depth = 3
        self.beam_width = 2
        self.tool_rate = 0.3
        self.current_mode = "balance"  # explore, exploit, balance
        self.step_count = 0

        # Performance tracking
        self.kpi_tracker = {
            "contradictions_detected": 0,
            "gaps_filled": 0,
            "entropy_adjustments": 0,
            "tools_triggered": 0,
            "consistency_restorations": 0,
            "avg_response_time": 0.0,
        }

        self.enable_logging = enable_logging
        self._setup_event_handlers()
        self._initialize_rcce_operations()
        self._initialize_control_policies()

    def _setup_event_handlers(self):
        """Setup event bus handlers for consciousness coordination"""

        # Glitchon (contradiction) handler
        self.event_bus.subscribe(
            EventType.CONTRADICTION_DETECTED, self._handle_contradiction
        )

        # Lacunon (gap) handler
        self.event_bus.subscribe(EventType.GAP_IDENTIFIED, self._handle_gap)

        # REF entropy handler
        self.event_bus.subscribe(
            EventType.ENTROPY_ADJUSTMENT, self._handle_entropy_adjustment
        )

        # Tesseracton dimensional lift handler
        self.event_bus.subscribe(
            EventType.DIMENSIONAL_LIFT, self._handle_dimensional_lift
        )

        # Tool invocation handler
        self.event_bus.subscribe(EventType.TOOL_INVOKED, self._handle_tool_invocation)

    def _initialize_rcce_operations(self):
        """Initialize RCCE operator mappings"""

        self.rcce_operations = {
            "recursive_descent": RCCEOperation(
                name="recursive_descent",
                operator_type="recursive",
                entropy_impact=0.3,
                complexity_level=4,
                prerequisites=["depth_budget"],
                postconditions=["subproblem_decomposition"],
            ),
            "compositional_synthesis": RCCEOperation(
                name="compositional_synthesis",
                operator_type="compositional",
                entropy_impact=-0.2,
                complexity_level=6,
                prerequisites=["component_analysis"],
                postconditions=["integrated_solution"],
            ),
            "complexity_reduction": RCCEOperation(
                name="complexity_reduction",
                operator_type="complexity",
                entropy_impact=-0.4,
                complexity_level=3,
                prerequisites=["complexity_metric"],
                postconditions=["simplified_representation"],
            ),
            "emergent_pattern_detection": RCCEOperation(
                name="emergent_pattern_detection",
                operator_type="emergence",
                entropy_impact=0.2,
                complexity_level=7,
                prerequisites=["pattern_space"],
                postconditions=["meta_pattern_discovered"],
            ),
        }

    def _initialize_control_policies(self):
        """Initialize Jarvis-style control policies"""

        self.control_policies = {
            "run_counterexample_miner_and_reproof": self._policy_contradiction_response,
            "switch_MoE_embedding_template": self._policy_dimensional_lift,
            "retrieve_or_ask": self._policy_gap_filling,
            "continue_plan": self._policy_continue,
            "invoke_rcce_recursive": self._policy_rcce_recursive,
            "invoke_rcce_compositional": self._policy_rcce_compositional,
            "entropy_regulate": self._policy_entropy_regulate,
        }

    def initialize_fields(
        self,
        plan_embedding: np.ndarray,
        gap_map: np.ndarray,
        context: Dict[str, Any] = None,
    ):
        """Initialize QRFT fields from AI context"""

        # Initialize QRFT state
        self.qrft_runtime.initialize_state(plan_embedding, gap_map)

        # Initialize monitors with context
        if context:
            entropy_text = context.get("conversation_text", "")
            if entropy_text:
                self.entropy_governor.measure_entropy(
                    text=entropy_text, source="conversation"
                )

        self.step_count = 0

        if self.enable_logging:
            print(
                f"QRFT consciousness initialized with S.shape={plan_embedding.shape}, Λ.shape={gap_map.shape}"
            )

    def step(self, context: Dict[str, Any] = None, dt: float = 0.01) -> Dict[str, Any]:
        """Execute one consciousness evolution step"""

        start_time = time.time()
        self.step_count += 1

        # QRFT field evolution
        qrft_result = self.qrft_runtime.step(dt)

        # Extract current state
        current_state = self.qrft_runtime.state
        triggers = qrft_result["triggers"]
        sources = qrft_result["sources"]

        # Process particle activations
        events_generated = []

        # Glitchon (contradiction detection)
        if sources[ParticleType.GLITCHON] > self.qrft_config.tau_G:
            contradiction_event = self._detect_contradictions(context)
            if contradiction_event:
                events_generated.append(contradiction_event)

        # Lacunon (gap detection)
        if sources[ParticleType.LACUNON] > self.qrft_config.tau_F:
            gap_event = self._detect_gaps(context)
            if gap_event:
                events_generated.append(gap_event)

        # Tesseracton (dimensional lift)
        if sources[ParticleType.TESSERACTON] > self.qrft_config.tau_T:
            lift_event = ConsciousnessEvent(
                event_type=EventType.DIMENSIONAL_LIFT,
                timestamp=time.time(),
                source_particle=ParticleType.TESSERACTON,
                data={"trigger_value": sources[ParticleType.TESSERACTON]},
                priority=0.8,
            )
            events_generated.append(lift_event)

        # REF entropy regulation
        if sources[ParticleType.REF] > self.qrft_config.tau_R:
            entropy_event = self._regulate_entropy(context)
            if entropy_event:
                events_generated.append(entropy_event)

        # Publish events
        for event in events_generated:
            self.event_bus.publish(event)

        # Process pending events
        pending_events = self.event_bus.get_pending_events(priority_threshold=0.3)
        control_actions = []

        for event in pending_events[:3]:  # Process top 3 priority events
            action = self._process_event(event)
            if action:
                control_actions.append(action)
            self.event_bus.mark_handled(event)

        # Generate control policy
        policy = self.qrft_runtime.get_control_policy()

        # Apply control policy
        policy_result = None
        if policy in self.control_policies:
            policy_result = self.control_policies[policy](context, qrft_result)

        # Update performance tracking
        processing_time = time.time() - start_time
        self._update_kpis(events_generated, processing_time)

        return {
            "qrft_state": {
                "S_field": current_state.S,
                "Lambda_field": current_state.Lambda,
                "time": current_state.t,
                "entropy_estimate": qrft_result["entropy_estimate"],
            },
            "particle_activations": sources,
            "triggers": triggers,
            "events_generated": len(events_generated),
            "control_policy": policy,
            "policy_result": policy_result,
            "control_actions": control_actions,
            "reasoning_params": {
                "depth": self.reasoning_depth,
                "beam_width": self.beam_width,
                "tool_rate": self.tool_rate,
                "mode": self.current_mode,
            },
            "kpis": self.kpi_tracker.copy(),
            "processing_time": processing_time,
        }

    def _detect_contradictions(
        self, context: Dict[str, Any]
    ) -> Optional[ConsciousnessEvent]:
        """Detect contradictions using Glitchon critic"""

        if not context:
            return None

        statements = context.get("statements", [])
        test_results = context.get("test_results", {})
        external_context = context.get("external_context", {})

        contradiction_state = self.glitchon_critic.detect_contradictions(
            statements, test_results, external_context
        )

        if contradiction_state.contradictions:
            self.kpi_tracker["contradictions_detected"] += len(
                contradiction_state.contradictions
            )

            return ConsciousnessEvent(
                event_type=EventType.CONTRADICTION_DETECTED,
                timestamp=time.time(),
                source_particle=ParticleType.GLITCHON,
                data={
                    "contradictions": contradiction_state.contradictions,
                    "severity": contradiction_state.total_severity,
                    "confidence": contradiction_state.confidence,
                },
                priority=min(contradiction_state.total_severity, 1.0),
                response_required=True,
            )
        return None

    def _detect_gaps(self, context: Dict[str, Any]) -> Optional[ConsciousnessEvent]:
        """Detect knowledge gaps using Lacuna monitor"""

        if not context:
            return None

        # Extract entropy and coverage maps from context
        entropy_map = context.get("entropy_map", np.array([]))
        coverage_map = context.get("coverage_map", np.array([]))

        if len(entropy_map) == 0:
            # Generate entropy map from text if available
            text = context.get("conversation_text", "")
            if text:
                tokens = text.split()
                # Simplified entropy estimation
                entropy_map = np.random.random(len(tokens)) * 2.0
                coverage_map = np.ones(len(tokens)) * 0.8

        if len(entropy_map) > 0:
            lacuna_state = self.lacuna_monitor.detect_gaps(
                entropy_map, coverage_map, context
            )

            significant_gaps = [
                g
                for g in (lacuna_state.spec_gaps + lacuna_state.consistency_gaps)
                if g.severity > 0.5
            ]

            if significant_gaps:
                self.kpi_tracker["gaps_filled"] += len(significant_gaps)

                return ConsciousnessEvent(
                    event_type=EventType.GAP_IDENTIFIED,
                    timestamp=time.time(),
                    source_particle=ParticleType.LACUNON,
                    data={
                        "gaps": significant_gaps,
                        "gap_density": lacuna_state.total_gap_density,
                        "queries": self.lacuna_monitor.generate_retrieval_queries(
                            lacuna_state, context.get("tokens", [])
                        ),
                    },
                    priority=lacuna_state.total_gap_density,
                    response_required=True,
                )
        return None

    def _regulate_entropy(
        self, context: Dict[str, Any]
    ) -> Optional[ConsciousnessEvent]:
        """Regulate reasoning entropy using REF governor"""

        # Measure current entropy
        if context and "conversation_text" in context:
            measurement = self.entropy_governor.measure_entropy(
                text=context["conversation_text"], source="conversation"
            )

            # Compute control action
            control_action = self.entropy_governor.compute_control_action()

            if control_action:
                self.kpi_tracker["entropy_adjustments"] += 1

                return ConsciousnessEvent(
                    event_type=EventType.ENTROPY_ADJUSTMENT,
                    timestamp=time.time(),
                    source_particle=ParticleType.REF,
                    data={
                        "measurement": measurement,
                        "control_action": control_action,
                        "entropy_stats": self.entropy_governor.get_entropy_statistics(),
                    },
                    priority=control_action.confidence,
                    response_required=True,
                )
        return None

    def _process_event(self, event: ConsciousnessEvent) -> Optional[Dict[str, Any]]:
        """Process consciousness event and generate action"""

        if event.event_type == EventType.CONTRADICTION_DETECTED:
            return self._handle_contradiction(event)
        elif event.event_type == EventType.GAP_IDENTIFIED:
            return self._handle_gap(event)
        elif event.event_type == EventType.ENTROPY_ADJUSTMENT:
            return self._handle_entropy_adjustment(event)
        elif event.event_type == EventType.DIMENSIONAL_LIFT:
            return self._handle_dimensional_lift(event)

        return None

    # Event handlers

    def _handle_contradiction(self, event: ConsciousnessEvent) -> Dict[str, Any]:
        """Handle contradiction detection event"""
        contradictions = event.data.get("contradictions", [])

        # Generate counterexamples and reproofs
        actions = []
        for contradiction in contradictions[:2]:  # Limit to top 2
            actions.append(
                {
                    "type": "generate_counterexample",
                    "target": contradiction.statement_1,
                    "context": contradiction.context,
                }
            )
            actions.append(
                {
                    "type": "request_reproof",
                    "claim": contradiction.statement_2,
                    "evidence_required": True,
                }
            )

        return {
            "policy": "run_counterexample_miner_and_reproof",
            "actions": actions,
            "priority": event.priority,
        }

    def _handle_gap(self, event: ConsciousnessEvent) -> Dict[str, Any]:
        """Handle knowledge gap event"""
        queries = event.data.get("queries", [])

        # Trigger retrieval or tool invocation
        actions = []
        for query in queries[:3]:  # Limit to top 3 queries
            if query["gap_type"] in ["spec_incomplete", "coverage_hole"]:
                actions.append(
                    {
                        "type": "retrieve_knowledge",
                        "query": query["query_text"],
                        "priority": query["priority"],
                    }
                )
            else:
                actions.append(
                    {
                        "type": "invoke_tool",
                        "tool_type": "knowledge_validator",
                        "query": query["query_text"],
                    }
                )

        self.kpi_tracker["tools_triggered"] += len(actions)

        return {
            "policy": "retrieve_or_ask",
            "actions": actions,
            "priority": event.priority,
        }

    def _handle_entropy_adjustment(self, event: ConsciousnessEvent) -> Dict[str, Any]:
        """Handle entropy regulation event"""
        control_action = event.data.get("control_action")

        if control_action:
            # Apply entropy control to reasoning parameters
            params = self.entropy_governor.apply_control_action(control_action)

            self.reasoning_depth = params["depth"]
            self.beam_width = params["beam_width"]
            self.tool_rate = params["tool_rate"]
            self.current_mode = params["reasoning_mode"]

        return {
            "policy": "entropy_regulate",
            "reasoning_updates": {
                "depth": self.reasoning_depth,
                "beam_width": self.beam_width,
                "tool_rate": self.tool_rate,
                "mode": self.current_mode,
            },
            "priority": event.priority,
        }

    def _handle_dimensional_lift(self, event: ConsciousnessEvent) -> Dict[str, Any]:
        """Handle dimensional lift (perspective shift) event"""

        # Switch reasoning template/embedding space
        actions = [
            {
                "type": "switch_embedding_template",
                "new_template": "mixture_of_experts",
                "dimension_target": "meta_cognitive",
            }
        ]

        return {
            "policy": "switch_MoE_embedding_template",
            "actions": actions,
            "priority": event.priority,
        }

    def _handle_tool_invocation(self, event: ConsciousnessEvent) -> Dict[str, Any]:
        """Handle tool invocation event"""
        return {
            "policy": "invoke_tool",
            "actions": event.data.get("actions", []),
            "priority": event.priority,
        }

    # Control policy implementations

    def _policy_contradiction_response(
        self, context: Dict, qrft_result: Dict
    ) -> Dict[str, Any]:
        """Policy: Run counterexample miner and reproof"""
        return {
            "action": "contradiction_resolution",
            "method": "counterexample_mining",
            "reproof_required": True,
            "rcce_operator": "complexity_reduction",
        }

    def _policy_dimensional_lift(
        self, context: Dict, qrft_result: Dict
    ) -> Dict[str, Any]:
        """Policy: Switch MoE embedding template"""
        return {
            "action": "perspective_shift",
            "method": "embedding_template_switch",
            "target_dimension": "meta_cognitive",
            "rcce_operator": "emergent_pattern_detection",
        }

    def _policy_gap_filling(self, context: Dict, qrft_result: Dict) -> Dict[str, Any]:
        """Policy: Retrieve or ask for missing information"""
        return {
            "action": "knowledge_acquisition",
            "method": "targeted_retrieval",
            "fallback": "direct_query",
            "rcce_operator": "compositional_synthesis",
        }

    def _policy_continue(self, context: Dict, qrft_result: Dict) -> Dict[str, Any]:
        """Policy: Continue current reasoning plan"""
        return {
            "action": "continue_reasoning",
            "method": "plan_execution",
            "rcce_operator": "recursive_descent",
        }

    def _policy_rcce_recursive(
        self, context: Dict, qrft_result: Dict
    ) -> Dict[str, Any]:
        """Policy: Invoke RCCE recursive operator"""
        return {
            "action": "recursive_decomposition",
            "rcce_operator": "recursive_descent",
            "depth_limit": self.reasoning_depth,
        }

    def _policy_rcce_compositional(
        self, context: Dict, qrft_result: Dict
    ) -> Dict[str, Any]:
        """Policy: Invoke RCCE compositional operator"""
        return {
            "action": "compositional_synthesis",
            "rcce_operator": "compositional_synthesis",
            "integration_method": "hierarchical",
        }

    def _policy_entropy_regulate(
        self, context: Dict, qrft_result: Dict
    ) -> Dict[str, Any]:
        """Policy: Regulate reasoning entropy"""
        return {
            "action": "entropy_regulation",
            "method": "parameter_adjustment",
            "target_entropy": self.entropy_governor.entropy_target,
        }

    def _update_kpis(self, events: List[ConsciousnessEvent], processing_time: float):
        """Update performance KPIs"""

        # Update response time (exponential moving average)
        alpha = 0.1
        self.kpi_tracker["avg_response_time"] = (
            alpha * processing_time
            + (1 - alpha) * self.kpi_tracker["avg_response_time"]
        )

        # Count consistency restorations
        contradiction_events = [
            e for e in events if e.event_type == EventType.CONTRADICTION_DETECTED
        ]
        if contradiction_events:
            self.kpi_tracker["consistency_restorations"] += len(contradiction_events)

    def get_consciousness_state(self) -> Dict[str, Any]:
        """Get current consciousness state summary"""

        return {
            "qrft_state": {
                "S_norm": (
                    float(np.linalg.norm(self.qrft_runtime.state.S))
                    if self.qrft_runtime.state
                    else 0
                ),
                "Lambda_norm": (
                    float(np.linalg.norm(self.qrft_runtime.state.Lambda))
                    if self.qrft_runtime.state
                    else 0
                ),
                "time": self.qrft_runtime.state.t if self.qrft_runtime.state else 0,
                "stability": self.qrft_runtime._check_stability(),
            },
            "reasoning_params": {
                "depth": self.reasoning_depth,
                "beam_width": self.beam_width,
                "tool_rate": self.tool_rate,
                "mode": self.current_mode,
            },
            "particle_activations": self.qrft_runtime.particle_activations,
            "event_stats": {
                "pending_events": len(self.event_bus.get_pending_events()),
                "total_events": len(self.event_bus.event_history),
                "recent_events": len([e for e in self.event_bus.event_history[-10:]]),
            },
            "kpis": self.kpi_tracker,
            "entropy_stats": self.entropy_governor.get_entropy_statistics(),
            "step_count": self.step_count,
        }


# Factory function for easy initialization
def create_qrft_consciousness(
    entropy_band: Tuple[float, float] = (1.5, 4.0),
    gamma: float = 0.3,
    enable_logging: bool = True,
) -> QRFTConsciousness:
    """Create QRFT consciousness system with sensible defaults"""

    config = QRFTConfig(
        gamma=gamma, entropy_band_low=entropy_band[0], entropy_band_high=entropy_band[1]
    )

    return QRFTConsciousness(
        qrft_config=config, entropy_band=entropy_band, enable_logging=enable_logging
    )

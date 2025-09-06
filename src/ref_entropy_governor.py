# src/ref_entropy_governor.py
"""
REF Entropy Governor - Recursive Entropy Framework controller
Implements PID-like control to maintain entropy in optimal band [H_min, H_max]
Tunes depth, beam width, and tool rate for stable long reasoning chains
"""

import math
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class EntropyMeasurement:
    """Single entropy measurement with context"""

    timestamp: float
    entropy_value: float
    source: str  # 'conversation', 'plan', 'retrieval', 'tool'
    context_length: int
    complexity_estimate: float


@dataclass
class ControlState:
    """Current controller state"""

    current_entropy: float
    target_entropy: float
    error: float
    error_integral: float
    error_derivative: float


@dataclass
class ControlAction:
    """Controller output actions"""

    depth_adjustment: int  # ±1, ±2, etc.
    beam_width_adjustment: int  # ±1, ±2, etc.
    tool_rate_adjustment: float  # ±0.1, ±0.2, etc.
    reasoning_mode: str  # 'explore', 'exploit', 'balance'
    confidence: float  # Action confidence [0,1]


class REFEntropyGovernor:
    """
    Recursive Entropy Framework governor implementing QRFT particle R dynamics:
    - Monitors conversation and planning entropy
    - Maintains entropy in optimal band via PID control
    - Prevents mode collapse and explosion
    - Enables stable long-horizon reasoning
    """

    def __init__(
        self,
        entropy_min: float = 1.5,
        entropy_max: float = 4.0,
        entropy_target: float = 2.5,
        Kp: float = 0.5,  # Proportional gain
        Ki: float = 0.1,  # Integral gain
        Kd: float = 0.2,  # Derivative gain
        history_window: int = 50,
        control_period: float = 1.0,
    ):
        self.entropy_min = entropy_min
        self.entropy_max = entropy_max
        self.entropy_target = entropy_target

        # PID parameters
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        self.history_window = history_window
        self.control_period = control_period

        # State tracking
        self.entropy_history: deque = deque(maxlen=history_window)
        self.control_history: deque = deque(maxlen=history_window)
        self.last_control_time = 0.0

        # PID state
        self.error_integral = 0.0
        self.last_error = 0.0

        # Current parameters being controlled
        self.current_depth = 3
        self.current_beam_width = 2
        self.current_tool_rate = 0.3

        # Parameter bounds
        self.depth_bounds = (1, 10)
        self.beam_width_bounds = (1, 8)
        self.tool_rate_bounds = (0.0, 1.0)

        # Entropy estimation methods
        self.entropy_estimators = {
            "shannon": self._shannon_entropy,
            "renyi": self._renyi_entropy,
            "tsallis": self._tsallis_entropy,
            "differential": self._differential_entropy,
        }

    def measure_entropy(
        self,
        text: str = None,
        token_probs: np.ndarray = None,
        embeddings: np.ndarray = None,
        source: str = "conversation",
        timestamp: float = None,
    ) -> EntropyMeasurement:
        """Measure entropy from various sources"""

        if timestamp is None:
            timestamp = len(self.entropy_history)

        entropy_value = 0.0
        context_length = 0
        complexity_estimate = 0.0

        # Text-based entropy
        if text is not None:
            entropy_value += self._text_entropy(text)
            context_length = len(text.split())
            complexity_estimate = self._estimate_text_complexity(text)

        # Token probability entropy
        if token_probs is not None:
            entropy_value += self._shannon_entropy(token_probs)

        # Embedding-based entropy
        if embeddings is not None:
            entropy_value += self._differential_entropy(embeddings)

        measurement = EntropyMeasurement(
            timestamp=timestamp,
            entropy_value=entropy_value,
            source=source,
            context_length=context_length,
            complexity_estimate=complexity_estimate,
        )

        self.entropy_history.append(measurement)
        return measurement

    def compute_control_action(
        self, current_time: float = None
    ) -> Optional[ControlAction]:
        """Compute PID control action based on current entropy state"""

        if len(self.entropy_history) == 0:
            return None

        if current_time is None:
            current_time = len(self.entropy_history)

        # Check if it's time for control update
        if current_time - self.last_control_time < self.control_period:
            return None

        # Get current entropy (weighted average of recent measurements)
        current_entropy = self._compute_current_entropy()

        # Compute PID error signals
        error = self.entropy_target - current_entropy

        # Integral term with windup protection
        self.error_integral += error * self.control_period
        self.error_integral = np.clip(self.error_integral, -10.0, 10.0)

        # Derivative term
        error_derivative = (error - self.last_error) / self.control_period

        # PID output
        control_signal = (
            self.Kp * error + self.Ki * self.error_integral + self.Kd * error_derivative
        )

        # Convert control signal to parameter adjustments
        action = self._signal_to_action(control_signal, current_entropy, error)

        # Update state
        self.last_error = error
        self.last_control_time = current_time

        control_state = ControlState(
            current_entropy=current_entropy,
            target_entropy=self.entropy_target,
            error=error,
            error_integral=self.error_integral,
            error_derivative=error_derivative,
        )

        self.control_history.append((control_state, action))

        return action

    def apply_control_action(self, action: ControlAction) -> Dict[str, Any]:
        """Apply control action to current parameters"""

        # Update depth
        new_depth = self.current_depth + action.depth_adjustment
        self.current_depth = np.clip(new_depth, *self.depth_bounds)

        # Update beam width
        new_beam_width = self.current_beam_width + action.beam_width_adjustment
        self.current_beam_width = np.clip(new_beam_width, *self.beam_width_bounds)

        # Update tool rate
        new_tool_rate = self.current_tool_rate + action.tool_rate_adjustment
        self.current_tool_rate = np.clip(new_tool_rate, *self.tool_rate_bounds)

        return {
            "depth": self.current_depth,
            "beam_width": self.current_beam_width,
            "tool_rate": self.current_tool_rate,
            "reasoning_mode": action.reasoning_mode,
            "action_confidence": action.confidence,
        }

    def _compute_current_entropy(self) -> float:
        """Compute weighted current entropy from recent measurements"""
        if not self.entropy_history:
            return self.entropy_target

        # Get recent measurements (last 5)
        recent_measurements = list(self.entropy_history)[-5:]

        # Weighted average with recency bias
        total_weight = 0.0
        weighted_entropy = 0.0

        for i, measurement in enumerate(recent_measurements):
            weight = (i + 1) / len(recent_measurements)  # More recent = higher weight

            # Adjust weight by source reliability
            source_weight = {
                "conversation": 1.0,
                "plan": 0.8,
                "retrieval": 0.6,
                "tool": 0.4,
            }.get(measurement.source, 0.5)

            effective_weight = weight * source_weight
            weighted_entropy += measurement.entropy_value * effective_weight
            total_weight += effective_weight

        return weighted_entropy / max(total_weight, 1e-6)

    def _signal_to_action(
        self, control_signal: float, current_entropy: float, error: float
    ) -> ControlAction:
        """Convert PID control signal to concrete parameter adjustments"""

        # Determine adjustment magnitudes based on signal strength
        signal_magnitude = abs(control_signal)

        # Scale adjustments
        if signal_magnitude > 2.0:
            depth_adj = int(np.sign(control_signal) * 2)
            beam_adj = int(np.sign(control_signal) * 1)
            tool_adj = np.sign(control_signal) * 0.2
        elif signal_magnitude > 1.0:
            depth_adj = int(np.sign(control_signal) * 1)
            beam_adj = int(np.sign(control_signal) * 1)
            tool_adj = np.sign(control_signal) * 0.1
        else:
            depth_adj = 0
            beam_adj = int(np.sign(control_signal)) if signal_magnitude > 0.5 else 0
            tool_adj = np.sign(control_signal) * 0.05

        # Determine reasoning mode based on entropy state
        if current_entropy < self.entropy_min:
            reasoning_mode = "explore"  # Need more diversity
        elif current_entropy > self.entropy_max:
            reasoning_mode = "exploit"  # Need more focus
        else:
            reasoning_mode = "balance"  # In good range

        # Adjust based on reasoning mode
        if reasoning_mode == "explore":
            depth_adj = max(depth_adj, 1)  # Increase depth
            beam_adj = max(beam_adj, 1)  # Increase beam width
            tool_adj = max(tool_adj, 0.1)  # Increase tool usage
        elif reasoning_mode == "exploit":
            depth_adj = min(depth_adj, -1)  # Decrease depth
            beam_adj = min(beam_adj, 0)  # Keep beam width stable
            tool_adj = min(tool_adj, -0.1)  # Decrease tool usage

        confidence = min(
            signal_magnitude / 3.0, 1.0
        )  # Higher signal = higher confidence

        return ControlAction(
            depth_adjustment=depth_adj,
            beam_width_adjustment=beam_adj,
            tool_rate_adjustment=tool_adj,
            reasoning_mode=reasoning_mode,
            confidence=confidence,
        )

    # Entropy estimation methods

    def _text_entropy(self, text: str) -> float:
        """Compute Shannon entropy of text at character level"""
        if not text:
            return 0.0

        # Character frequency distribution
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1

        total_chars = len(text)
        entropy = 0.0

        for count in char_counts.values():
            p = count / total_chars
            entropy -= p * math.log2(p)

        return entropy

    def _shannon_entropy(self, probs: np.ndarray) -> float:
        """Shannon entropy H = -Σ p log p"""
        probs = np.array(probs) + 1e-12  # Avoid log(0)
        probs = probs / probs.sum()  # Normalize
        return float(-np.sum(probs * np.log2(probs)))

    def _renyi_entropy(self, probs: np.ndarray, alpha: float = 2.0) -> float:
        """Rényi entropy of order α"""
        if alpha == 1.0:
            return self._shannon_entropy(probs)

        probs = np.array(probs) + 1e-12
        probs = probs / probs.sum()

        if alpha == np.inf:
            return -math.log2(np.max(probs))  # Min entropy
        else:
            return math.log2(np.sum(probs**alpha)) / (1 - alpha)

    def _tsallis_entropy(self, probs: np.ndarray, q: float = 2.0) -> float:
        """Tsallis entropy"""
        probs = np.array(probs) + 1e-12
        probs = probs / probs.sum()

        if q == 1.0:
            return self._shannon_entropy(probs)
        else:
            return (1 - np.sum(probs**q)) / (q - 1)

    def _differential_entropy(self, data: np.ndarray) -> float:
        """Differential entropy estimate using histogram method"""
        if data.size == 0:
            return 0.0

        # Flatten if multidimensional
        if data.ndim > 1:
            data = data.flatten()

        # Create histogram
        bins = min(50, len(data) // 5)  # Adaptive bin count
        counts, bin_edges = np.histogram(data, bins=bins)

        # Convert to probabilities
        bin_width = bin_edges[1] - bin_edges[0]
        probs = counts / (len(data) * bin_width)
        probs = probs[probs > 0]  # Remove zero probabilities

        # Differential entropy
        return float(-np.sum(probs * bin_width * np.log2(probs * bin_width)))

    def _estimate_text_complexity(self, text: str) -> float:
        """Estimate text complexity using multiple heuristics"""
        if not text:
            return 0.0

        words = text.split()
        sentences = text.split(".")

        # Lexical diversity (type-token ratio)
        unique_words = len(set(word.lower() for word in words))
        lexical_diversity = unique_words / max(len(words), 1)

        # Average word length
        avg_word_length = np.mean([len(word) for word in words]) if words else 0

        # Average sentence length
        avg_sentence_length = len(words) / max(len(sentences), 1)

        # Syntactic complexity (simplified - count of conjunctions, etc.)
        complex_words = [
            "because",
            "although",
            "however",
            "therefore",
            "moreover",
            "furthermore",
        ]
        syntactic_complexity = sum(
            1 for word in words if word.lower() in complex_words
        ) / max(len(words), 1)

        # Combined complexity score
        complexity = (
            0.3 * lexical_diversity
            + 0.2 * min(avg_word_length / 6, 1)  # Normalize to [0,1]
            + 0.3 * min(avg_sentence_length / 20, 1)  # Normalize to [0,1]
            + 0.2 * syntactic_complexity
        )

        return complexity

    def get_entropy_statistics(self) -> Dict[str, float]:
        """Get entropy statistics for monitoring"""
        if not self.entropy_history:
            return {}

        entropies = [m.entropy_value for m in self.entropy_history]

        return {
            "current_entropy": entropies[-1] if entropies else 0,
            "mean_entropy": np.mean(entropies),
            "std_entropy": np.std(entropies),
            "min_entropy": np.min(entropies),
            "max_entropy": np.max(entropies),
            "entropy_trend": self._compute_trend(entropies),
            "target_entropy": self.entropy_target,
            "entropy_min": self.entropy_min,
            "entropy_max": self.entropy_max,
            "in_target_band": (
                self.entropy_min <= entropies[-1] <= self.entropy_max
                if entropies
                else False
            ),
        }

    def _compute_trend(self, values: List[float], window: int = 10) -> float:
        """Compute trend of recent values (positive = increasing)"""
        if len(values) < 2:
            return 0.0

        recent_values = values[-window:]
        if len(recent_values) < 2:
            return 0.0

        # Simple linear regression slope
        n = len(recent_values)
        x = np.arange(n)
        y = np.array(recent_values)

        slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (
            n * np.sum(x**2) - np.sum(x) ** 2
        )
        return float(slope)

    def reset_controller(self):
        """Reset controller state (for new conversation/task)"""
        self.error_integral = 0.0
        self.last_error = 0.0
        self.last_control_time = 0.0
        self.entropy_history.clear()
        self.control_history.clear()

    def tune_parameters(self, Kp: float = None, Ki: float = None, Kd: float = None):
        """Tune PID parameters"""
        if Kp is not None:
            self.Kp = Kp
        if Ki is not None:
            self.Ki = Ki
        if Kd is not None:
            self.Kd = Kd

    def compute_J_R_field(self) -> float:
        """Compute QRFT J_R field magnitude for particle R coupling"""
        if len(self.entropy_history) < 2:
            return 0.0

        # Compute entropy gradient (temporal derivative approximation)
        recent_entropies = [m.entropy_value for m in list(self.entropy_history)[-5:]]
        entropy_gradient = np.gradient(recent_entropies)

        # J^μ = S∂^μΛ - Λ∂^μS analog: entropy flow
        J_magnitude = float(np.linalg.norm(entropy_gradient))

        return J_magnitude

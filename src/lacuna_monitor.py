# src/lacuna_monitor.py
"""
Lacuna Monitor - Gap-driven control loop implementation
Maps token-level entropy, retrieval coverage, and spec gaps to Λ field
Triggers auto-retrieval/tools when X_F = |□Λ| exceeds threshold
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np


@dataclass
class GapSignal:
    """Individual gap detection signal"""

    gap_type: str  # 'entropy', 'coverage', 'spec', 'consistency'
    confidence: float  # Gap confidence [0,1]
    location: int  # Token/span location
    severity: float  # Gap severity [0,1]
    context: Dict[str, Any]  # Additional context


@dataclass
class LacunaState:
    """Current state of gap detection system"""

    entropy_map: np.ndarray  # Token-level entropy
    coverage_map: np.ndarray  # Retrieval coverage per token
    spec_gaps: List[GapSignal]  # Specification gaps
    consistency_gaps: List[GapSignal]  # Consistency violations
    total_gap_density: float  # Overall gap density


class LacunaMonitor:
    """
    Gap-driven control loop implementing Lacunon particle dynamics:
    - Monitors token-level entropy jumps
    - Tracks retrieval coverage gaps
    - Detects specification incompleteness
    - Triggers targeted retrieval/tools
    """

    def __init__(
        self,
        entropy_threshold: float = 2.5,
        coverage_threshold: float = 0.3,
        gap_window: int = 16,
        smoothing_factor: float = 0.7,
    ):
        self.entropy_threshold = entropy_threshold
        self.coverage_threshold = coverage_threshold
        self.gap_window = gap_window
        self.smoothing_factor = smoothing_factor

        # State tracking
        self.entropy_history: List[np.ndarray] = []
        self.coverage_history: List[np.ndarray] = []
        self.gap_history: List[GapSignal] = []

        # Running statistics
        self.baseline_entropy = 0.0
        self.baseline_coverage = 1.0

        # Gap classification
        self.gap_patterns = self._initialize_gap_patterns()

    def _initialize_gap_patterns(self) -> Dict[str, Dict]:
        """Initialize gap detection patterns"""
        return {
            "entropy_spike": {
                "description": "Sudden increase in token uncertainty",
                "detector": self._detect_entropy_spike,
                "severity_weight": 0.8,
            },
            "coverage_hole": {
                "description": "Low retrieval coverage region",
                "detector": self._detect_coverage_hole,
                "severity_weight": 0.7,
            },
            "spec_incomplete": {
                "description": "Incomplete specification",
                "detector": self._detect_spec_gap,
                "severity_weight": 0.9,
            },
            "consistency_break": {
                "description": "Consistency violation detected",
                "detector": self._detect_consistency_gap,
                "severity_weight": 1.0,
            },
        }

    def update_entropy_map(
        self, token_logits: np.ndarray, tokens: List[str]
    ) -> np.ndarray:
        """Update token-level entropy map from model logits"""
        # Compute entropy for each token position
        probs = self._softmax(token_logits)
        entropy = -np.sum(probs * np.log(probs + 1e-12), axis=-1)

        # Smooth with exponential moving average
        if self.entropy_history:
            prev_entropy = self.entropy_history[-1]
            if len(prev_entropy) == len(entropy):
                entropy = (
                    self.smoothing_factor * prev_entropy
                    + (1 - self.smoothing_factor) * entropy
                )

        self.entropy_history.append(entropy)
        self._update_baseline_entropy(entropy)

        return entropy

    def update_coverage_map(
        self, retrieval_scores: np.ndarray, token_spans: List[Tuple[int, int]]
    ) -> np.ndarray:
        """Update retrieval coverage map"""
        coverage = np.zeros(len(token_spans))

        for i, (start, end) in enumerate(token_spans):
            if i < len(retrieval_scores):
                # Coverage based on retrieval confidence and relevance
                coverage[i] = min(retrieval_scores[i], 1.0)

        self.coverage_history.append(coverage)
        self._update_baseline_coverage(coverage)

        return coverage

    def detect_gaps(
        self, entropy_map: np.ndarray, coverage_map: np.ndarray, context: Dict[str, Any]
    ) -> LacunaState:
        """Comprehensive gap detection across all modalities"""

        gaps = []

        # Run all gap detectors
        for gap_type, pattern in self.gap_patterns.items():
            detector = pattern["detector"]
            weight = pattern["severity_weight"]

            detected_gaps = detector(entropy_map, coverage_map, context)
            for gap in detected_gaps:
                gap.severity *= weight
                gaps.append(gap)

        # Compute Lambda field density
        total_density = self._compute_gap_density(gaps, len(entropy_map))

        return LacunaState(
            entropy_map=entropy_map,
            coverage_map=coverage_map,
            spec_gaps=[g for g in gaps if g.gap_type == "spec_incomplete"],
            consistency_gaps=[g for g in gaps if g.gap_type == "consistency_break"],
            total_gap_density=total_density,
        )

    def _detect_entropy_spike(
        self, entropy_map: np.ndarray, coverage_map: np.ndarray, context: Dict[str, Any]
    ) -> List[GapSignal]:
        """Detect sudden entropy increases indicating uncertainty"""
        gaps = []

        if len(self.entropy_history) < 2:
            return gaps

        # Compare with baseline and recent history
        entropy_delta = entropy_map - self.baseline_entropy
        spike_threshold = self.entropy_threshold

        for i, delta in enumerate(entropy_delta):
            if delta > spike_threshold:
                confidence = min(delta / (spike_threshold * 2), 1.0)
                severity = min(delta / self.entropy_threshold, 1.0)

                gaps.append(
                    GapSignal(
                        gap_type="entropy_spike",
                        confidence=confidence,
                        location=i,
                        severity=severity,
                        context={
                            "entropy_delta": float(delta),
                            "baseline_entropy": self.baseline_entropy,
                            "token_entropy": float(entropy_map[i]),
                        },
                    )
                )

        return gaps

    def _detect_coverage_hole(
        self, entropy_map: np.ndarray, coverage_map: np.ndarray, context: Dict[str, Any]
    ) -> List[GapSignal]:
        """Detect regions with poor retrieval coverage"""
        gaps = []

        low_coverage_mask = coverage_map < self.coverage_threshold

        # Find contiguous regions of low coverage
        regions = self._find_contiguous_regions(low_coverage_mask)

        for start, end in regions:
            severity = 1.0 - np.mean(coverage_map[start:end])
            confidence = min(
                len(range(start, end)) / 4.0, 1.0
            )  # Longer gaps = higher confidence

            gaps.append(
                GapSignal(
                    gap_type="coverage_hole",
                    confidence=confidence,
                    location=start + (end - start) // 2,  # Center of gap
                    severity=severity,
                    context={
                        "region_start": start,
                        "region_end": end,
                        "mean_coverage": float(np.mean(coverage_map[start:end])),
                    },
                )
            )

        return gaps

    def _detect_spec_gap(
        self, entropy_map: np.ndarray, coverage_map: np.ndarray, context: Dict[str, Any]
    ) -> List[GapSignal]:
        """Detect specification incompleteness"""
        gaps = []

        # Look for high entropy + low coverage combinations
        spec_gap_mask = (entropy_map > self.entropy_threshold) & (
            coverage_map < self.coverage_threshold
        )

        gap_positions = np.where(spec_gap_mask)[0]

        for pos in gap_positions:
            entropy_severity = min(entropy_map[pos] / (self.entropy_threshold * 2), 1.0)
            coverage_severity = 1.0 - coverage_map[pos]
            combined_severity = 0.6 * entropy_severity + 0.4 * coverage_severity

            gaps.append(
                GapSignal(
                    gap_type="spec_incomplete",
                    confidence=0.8,  # High confidence when both signals align
                    location=int(pos),
                    severity=combined_severity,
                    context={
                        "entropy": float(entropy_map[pos]),
                        "coverage": float(coverage_map[pos]),
                        "needs_retrieval": True,
                    },
                )
            )

        return gaps

    def _detect_consistency_gap(
        self, entropy_map: np.ndarray, coverage_map: np.ndarray, context: Dict[str, Any]
    ) -> List[GapSignal]:
        """Detect consistency violations from context"""
        gaps = []

        # Extract consistency signals from context
        contradictions = context.get("contradictions", [])
        failed_tests = context.get("failed_tests", [])
        logical_errors = context.get("logical_errors", [])

        # Map each consistency violation to gaps
        for contradiction in contradictions:
            location = contradiction.get("location", 0)
            severity = contradiction.get("severity", 0.8)

            gaps.append(
                GapSignal(
                    gap_type="consistency_break",
                    confidence=0.9,
                    location=location,
                    severity=severity,
                    context={
                        "violation_type": "contradiction",
                        "details": contradiction,
                    },
                )
            )

        for test_failure in failed_tests:
            location = test_failure.get("location", 0)
            severity = min(test_failure.get("failure_count", 1) / 3.0, 1.0)

            gaps.append(
                GapSignal(
                    gap_type="consistency_break",
                    confidence=0.8,
                    location=location,
                    severity=severity,
                    context={"violation_type": "test_failure", "details": test_failure},
                )
            )

        return gaps

    def compute_lambda_field(self, lacuna_state: LacunaState) -> np.ndarray:
        """Compute Λ field from gap state for QRFT coupling"""
        field_length = len(lacuna_state.entropy_map)
        lambda_field = np.zeros(field_length)

        # Map gaps to field values
        for gap in lacuna_state.spec_gaps + lacuna_state.consistency_gaps:
            pos = gap.location
            if 0 <= pos < field_length:
                # Field intensity = severity * confidence
                intensity = gap.severity * gap.confidence
                lambda_field[pos] += intensity

        # Add entropy and coverage contributions
        entropy_normalized = (
            lacuna_state.entropy_map - self.baseline_entropy
        ) / self.entropy_threshold
        entropy_contribution = np.maximum(entropy_normalized, 0) * 0.3

        coverage_contribution = (
            self.baseline_coverage - lacuna_state.coverage_map
        ) * 0.4
        coverage_contribution = np.maximum(coverage_contribution, 0)

        lambda_field += entropy_contribution + coverage_contribution

        # Smooth and normalize
        lambda_field = self._smooth_field(lambda_field)
        lambda_field = np.clip(lambda_field, 0, 2.0)  # Bounded field

        return lambda_field

    def generate_retrieval_queries(
        self, lacuna_state: LacunaState, tokens: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate targeted retrieval queries for detected gaps"""
        queries = []

        for gap in lacuna_state.spec_gaps + lacuna_state.consistency_gaps:
            if gap.severity > 0.5:  # Only high-severity gaps
                # Extract context around gap location
                start = max(0, gap.location - 3)
                end = min(len(tokens), gap.location + 4)
                context_tokens = tokens[start:end]

                query = {
                    "type": "gap_filling",
                    "query_text": " ".join(context_tokens),
                    "gap_type": gap.gap_type,
                    "priority": gap.severity * gap.confidence,
                    "location": gap.location,
                    "context": gap.context,
                }
                queries.append(query)

        # Sort by priority
        queries.sort(key=lambda x: x["priority"], reverse=True)

        return queries[:5]  # Limit to top 5 queries

    # Utility methods

    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Numerically stable softmax"""
        exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=-1, keepdims=True)

    def _update_baseline_entropy(self, entropy: np.ndarray):
        """Update baseline entropy with exponential moving average"""
        mean_entropy = np.mean(entropy)
        if self.baseline_entropy == 0.0:
            self.baseline_entropy = mean_entropy
        else:
            alpha = 0.05  # Slow adaptation
            self.baseline_entropy = (
                alpha * mean_entropy + (1 - alpha) * self.baseline_entropy
            )

    def _update_baseline_coverage(self, coverage: np.ndarray):
        """Update baseline coverage"""
        mean_coverage = np.mean(coverage)
        if self.baseline_coverage == 1.0:
            self.baseline_coverage = mean_coverage
        else:
            alpha = 0.1
            self.baseline_coverage = (
                alpha * mean_coverage + (1 - alpha) * self.baseline_coverage
            )

    def _find_contiguous_regions(self, mask: np.ndarray) -> List[Tuple[int, int]]:
        """Find contiguous True regions in boolean mask"""
        regions = []
        start = None

        for i, val in enumerate(mask):
            if val and start is None:
                start = i
            elif not val and start is not None:
                regions.append((start, i))
                start = None

        if start is not None:
            regions.append((start, len(mask)))

        return regions

    def _compute_gap_density(self, gaps: List[GapSignal], field_length: int) -> float:
        """Compute overall gap density for Lambda field intensity"""
        if not gaps:
            return 0.0

        total_severity = sum(gap.severity * gap.confidence for gap in gaps)
        return min(total_severity / field_length, 1.0)

    def _smooth_field(self, field: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        """Apply Gaussian smoothing to field"""
        if len(field) < kernel_size:
            return field

        # Simple moving average smoothing
        smoothed = np.copy(field)
        for i in range(kernel_size // 2, len(field) - kernel_size // 2):
            smoothed[i] = np.mean(
                field[i - kernel_size // 2 : i + kernel_size // 2 + 1]
            )

        return smoothed

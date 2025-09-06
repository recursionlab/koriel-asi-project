# src/glitchon_critic.py
"""
Glitchon Critic - Contradiction detection and counterexample mining
Maps inconsistencies to K = S□Λ - Λ□S signal for targeted re-proofing
Implements failure triad: {self-consistency, unit tests, external check}
"""

import re
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np


class ContradictionType(Enum):
    SELF_CONSISTENCY = "self_consistency"
    UNIT_TEST_FAILURE = "unit_test"
    EXTERNAL_CHECK = "external_check"
    LOGICAL_CONTRADICTION = "logical"
    TEMPORAL_INCONSISTENCY = "temporal"


@dataclass
class Contradiction:
    """Individual contradiction detection"""

    contradiction_type: ContradictionType
    confidence: float  # Detection confidence [0,1]
    severity: float  # Severity of contradiction [0,1]
    location: Tuple[int, int]  # (statement_1_pos, statement_2_pos)
    evidence: Dict[str, Any]  # Supporting evidence
    context: str  # Textual context
    suggested_fix: Optional[str] = None


@dataclass
class ContradictionState:
    """Current contradiction detection state"""

    contradictions: List[Contradiction]
    consistency_score: float  # Overall consistency [0,1]
    failure_count: int  # Total failures detected
    critical_failures: List[Contradiction]  # High-severity contradictions


class GlitchonCritic:
    """
    Contradiction engine implementing Glitchon particle dynamics:
    - Detects self-consistency violations
    - Monitors unit test failures
    - Performs external validation checks
    - Triggers counterexample mining and re-proofing
    """

    def __init__(
        self,
        consistency_threshold: float = 0.7,
        severity_threshold: float = 0.6,
        history_window: int = 100,
        max_contradictions: int = 20,
    ):
        self.consistency_threshold = consistency_threshold
        self.severity_threshold = severity_threshold
        self.history_window = history_window
        self.max_contradictions = max_contradictions

        # State tracking
        self.contradiction_history: deque = deque(maxlen=history_window)
        self.statement_cache: Dict[str, Any] = {}
        self.test_results: Dict[str, bool] = {}

        # Pattern matching for contradiction detection
        self.contradiction_patterns = self._initialize_patterns()

        # External validators (pluggable)
        self.external_validators: List[Callable] = []

    def _initialize_patterns(self) -> Dict[str, Dict]:
        """Initialize contradiction detection patterns"""
        return {
            "negation_contradiction": {
                "description": "Direct logical negation (A and not A)",
                "pattern": self._detect_negation_contradiction,
                "weight": 1.0,
            },
            "numerical_contradiction": {
                "description": "Conflicting numerical claims",
                "pattern": self._detect_numerical_contradiction,
                "weight": 0.9,
            },
            "temporal_contradiction": {
                "description": "Contradictory temporal statements",
                "pattern": self._detect_temporal_contradiction,
                "weight": 0.8,
            },
            "causality_violation": {
                "description": "Causal contradiction (effect before cause)",
                "pattern": self._detect_causality_violation,
                "weight": 0.9,
            },
            "definition_inconsistency": {
                "description": "Inconsistent definitions of same entity",
                "pattern": self._detect_definition_inconsistency,
                "weight": 0.8,
            },
        }

    def detect_contradictions(
        self,
        statements: List[str],
        test_results: Optional[Dict[str, bool]] = None,
        external_context: Optional[Dict[str, Any]] = None,
    ) -> ContradictionState:
        """Comprehensive contradiction detection across all modalities"""

        contradictions = []

        # 1. Self-consistency check
        self_contradictions = self._check_self_consistency(statements)
        contradictions.extend(self_contradictions)

        # 2. Unit test validation
        if test_results:
            test_contradictions = self._check_unit_tests(statements, test_results)
            contradictions.extend(test_contradictions)

        # 3. External validation
        if external_context:
            external_contradictions = self._check_external_validation(
                statements, external_context
            )
            contradictions.extend(external_contradictions)

        # Filter and rank contradictions
        contradictions = self._filter_contradictions(contradictions)

        # Update history
        self.contradiction_history.append(contradictions)

        # Compute consistency metrics
        consistency_score = self._compute_consistency_score(contradictions)
        critical_failures = [
            c for c in contradictions if c.severity > self.severity_threshold
        ]

        return ContradictionState(
            contradictions=contradictions,
            consistency_score=consistency_score,
            failure_count=len(contradictions),
            critical_failures=critical_failures,
        )

    def _check_self_consistency(self, statements: List[str]) -> List[Contradiction]:
        """Check for internal logical contradictions"""
        contradictions = []

        # Pairwise comparison of statements
        for i, stmt1 in enumerate(statements):
            for j, stmt2 in enumerate(statements[i + 1 :], i + 1):
                # Run all pattern detectors
                for pattern_name, pattern_info in self.contradiction_patterns.items():
                    detector = pattern_info["pattern"]
                    weight = pattern_info["weight"]

                    contradiction = detector(stmt1, stmt2, i, j)
                    if contradiction:
                        contradiction.severity *= weight
                        contradiction.contradiction_type = (
                            ContradictionType.SELF_CONSISTENCY
                        )
                        contradictions.append(contradiction)

        return contradictions

    def _check_unit_tests(
        self, statements: List[str], test_results: Dict[str, bool]
    ) -> List[Contradiction]:
        """Check unit test failures against statements"""
        contradictions = []

        failed_tests = {
            name: result for name, result in test_results.items() if not result
        }

        for test_name, _ in failed_tests.items():
            # Find statements that might relate to this test
            related_statements = self._find_test_related_statements(
                test_name, statements
            )

            for stmt_idx, statement in related_statements:
                contradiction = Contradiction(
                    contradiction_type=ContradictionType.UNIT_TEST_FAILURE,
                    confidence=0.8,
                    severity=0.7,
                    location=(stmt_idx, -1),  # -1 indicates test failure
                    evidence={
                        "test_name": test_name,
                        "test_result": False,
                        "statement": statement,
                    },
                    context=f"Statement contradicts failing test: {test_name}",
                    suggested_fix=f"Review statement at position {stmt_idx} against test {test_name}",
                )
                contradictions.append(contradiction)

        return contradictions

    def _check_external_validation(
        self, statements: List[str], external_context: Dict[str, Any]
    ) -> List[Contradiction]:
        """Check statements against external validation sources"""
        contradictions = []

        # Check against known facts
        known_facts = external_context.get("known_facts", [])
        for fact in known_facts:
            fact_contradictions = self._validate_against_fact(statements, fact)
            contradictions.extend(fact_contradictions)

        # Run external validators
        for validator in self.external_validators:
            try:
                validator_results = validator(statements, external_context)
                contradictions.extend(validator_results)
            except Exception:
                # Log validator error but continue
                pass

        return contradictions

    # Pattern detector implementations

    def _detect_negation_contradiction(
        self, stmt1: str, stmt2: str, pos1: int, pos2: int
    ) -> Optional[Contradiction]:
        """Detect direct logical negation patterns"""

        # Normalize statements
        norm_stmt1 = self._normalize_statement(stmt1)
        norm_stmt2 = self._normalize_statement(stmt2)

        # Look for negation patterns
        negation_words = {
            "not",
            "no",
            "never",
            "none",
            "nothing",
            "cannot",
            "isn't",
            "doesn't",
            "won't",
        }

        # Extract core claims (simplified)
        claim1 = self._extract_core_claim(norm_stmt1)
        claim2 = self._extract_core_claim(norm_stmt2)

        # Check if one negates the other
        if self._is_negation_pair(claim1, claim2):
            return Contradiction(
                contradiction_type=ContradictionType.LOGICAL_CONTRADICTION,
                confidence=0.9,
                severity=1.0,
                location=(pos1, pos2),
                evidence={
                    "claim1": claim1,
                    "claim2": claim2,
                    "pattern": "direct_negation",
                },
                context=f"Statement {pos1}: '{stmt1}' contradicts Statement {pos2}: '{stmt2}'",
                suggested_fix="Resolve logical contradiction between statements",
            )

        return None

    def _detect_numerical_contradiction(
        self, stmt1: str, stmt2: str, pos1: int, pos2: int
    ) -> Optional[Contradiction]:
        """Detect contradictory numerical claims"""

        # Extract numbers from statements
        numbers1 = self._extract_numbers(stmt1)
        numbers2 = self._extract_numbers(stmt2)

        if not (numbers1 and numbers2):
            return None

        # Look for contradictory numerical relationships
        # This is a simplified version - could be much more sophisticated
        for entity, values1 in numbers1.items():
            if entity in numbers2:
                values2 = numbers2[entity]

                # Check for direct contradictions
                if any(v1 != v2 for v1 in values1 for v2 in values2):
                    confidence = 0.8
                    severity = min(
                        abs(max(values1) - max(values2))
                        / max(max(values1), max(values2)),
                        1.0,
                    )

                    return Contradiction(
                        contradiction_type=ContradictionType.LOGICAL_CONTRADICTION,
                        confidence=confidence,
                        severity=severity,
                        location=(pos1, pos2),
                        evidence={
                            "entity": entity,
                            "values1": values1,
                            "values2": values2,
                        },
                        context=f"Numerical contradiction for '{entity}': {values1} vs {values2}",
                        suggested_fix=f"Reconcile numerical values for {entity}",
                    )

        return None

    def _detect_temporal_contradiction(
        self, stmt1: str, stmt2: str, pos1: int, pos2: int
    ) -> Optional[Contradiction]:
        """Detect temporal contradictions"""

        # Extract temporal markers
        time1 = self._extract_temporal_markers(stmt1)
        time2 = self._extract_temporal_markers(stmt2)

        if not (time1 and time2):
            return None

        # Check for temporal contradictions (simplified)
        temporal_contradiction = self._check_temporal_conflict(
            time1, time2, stmt1, stmt2
        )

        if temporal_contradiction:
            return Contradiction(
                contradiction_type=ContradictionType.TEMPORAL_INCONSISTENCY,
                confidence=temporal_contradiction["confidence"],
                severity=temporal_contradiction["severity"],
                location=(pos1, pos2),
                evidence=temporal_contradiction["evidence"],
                context=f"Temporal contradiction: {temporal_contradiction['description']}",
                suggested_fix="Resolve temporal inconsistency",
            )

        return None

    def _detect_causality_violation(
        self, stmt1: str, stmt2: str, pos1: int, pos2: int
    ) -> Optional[Contradiction]:
        """Detect causal contradictions"""

        # Extract causal relationships (simplified)
        causal1 = self._extract_causal_relations(stmt1)
        causal2 = self._extract_causal_relations(stmt2)

        if not (causal1 and causal2):
            return None

        # Check for causal violations
        violation = self._check_causal_consistency(causal1, causal2)

        if violation:
            return Contradiction(
                contradiction_type=ContradictionType.LOGICAL_CONTRADICTION,
                confidence=0.7,
                severity=0.8,
                location=(pos1, pos2),
                evidence=violation,
                context="Causal violation detected",
                suggested_fix="Review causal relationships",
            )

        return None

    def _detect_definition_inconsistency(
        self, stmt1: str, stmt2: str, pos1: int, pos2: int
    ) -> Optional[Contradiction]:
        """Detect inconsistent definitions"""

        # Extract definitions (simplified pattern matching)
        def1 = self._extract_definition(stmt1)
        def2 = self._extract_definition(stmt2)

        if not (def1 and def2):
            return None

        # Check if defining same entity differently
        if (
            def1["entity"] == def2["entity"]
            and def1["definition"] != def2["definition"]
        ):
            return Contradiction(
                contradiction_type=ContradictionType.LOGICAL_CONTRADICTION,
                confidence=0.8,
                severity=0.9,
                location=(pos1, pos2),
                evidence={
                    "entity": def1["entity"],
                    "definition1": def1["definition"],
                    "definition2": def2["definition"],
                },
                context=f"Inconsistent definitions of '{def1['entity']}'",
                suggested_fix=f"Reconcile definitions of {def1['entity']}",
            )

        return None

    # Utility methods for pattern detection

    def _normalize_statement(self, statement: str) -> str:
        """Normalize statement for comparison"""
        return re.sub(r"\s+", " ", statement.lower().strip())

    def _extract_core_claim(self, statement: str) -> str:
        """Extract core claim from statement (simplified)"""
        # Remove common sentence starters and modifiers
        cleaned = re.sub(r"^(i think|i believe|perhaps|maybe|possibly)", "", statement)
        return cleaned.strip()

    def _is_negation_pair(self, claim1: str, claim2: str) -> bool:
        """Check if two claims are logical negations"""
        # Simplified negation detection
        negation_words = {"not", "no", "never", "none", "cannot", "isn't", "doesn't"}

        words1 = set(claim1.split())
        words2 = set(claim2.split())

        # Check if one has negation and the other doesn't, but otherwise similar
        neg1 = bool(words1.intersection(negation_words))
        neg2 = bool(words2.intersection(negation_words))

        if neg1 != neg2:  # One negated, one not
            # Remove negation words and compare
            clean1 = words1 - negation_words
            clean2 = words2 - negation_words

            # Simplified similarity check
            intersection = clean1.intersection(clean2)
            union = clean1.union(clean2)

            if len(union) > 0:
                similarity = len(intersection) / len(union)
                return similarity > 0.6  # Threshold for similarity

        return False

    def _extract_numbers(self, statement: str) -> Dict[str, List[float]]:
        """Extract numerical claims from statement"""
        # Simplified number extraction
        number_pattern = r"(\w+)\s+(?:is|are|equals?|=)\s+([\d.]+)"
        matches = re.findall(number_pattern, statement.lower())

        result = defaultdict(list)
        for entity, value in matches:
            try:
                result[entity].append(float(value))
            except ValueError:
                pass

        return dict(result)

    def _extract_temporal_markers(self, statement: str) -> Dict[str, Any]:
        """Extract temporal information from statement"""
        temporal_words = {
            "past": ["yesterday", "last", "ago", "before", "previously", "earlier"],
            "present": ["now", "today", "currently", "presently"],
            "future": ["tomorrow", "next", "will", "going to", "later", "soon"],
        }

        markers = {}
        for tense, words in temporal_words.items():
            for word in words:
                if word in statement.lower():
                    markers[tense] = word

        return markers

    def _check_temporal_conflict(
        self, time1: Dict, time2: Dict, stmt1: str, stmt2: str
    ) -> Optional[Dict]:
        """Check for temporal conflicts between statements"""
        # Simplified temporal conflict detection
        if "past" in time1 and "future" in time2:
            return {
                "confidence": 0.7,
                "severity": 0.6,
                "evidence": {"time1": time1, "time2": time2},
                "description": "Past/future temporal contradiction",
            }

        return None

    def _extract_causal_relations(self, statement: str) -> List[Dict]:
        """Extract causal relationships (simplified)"""
        causal_patterns = [
            r"(\w+)\s+causes?\s+(\w+)",
            r"(\w+)\s+leads?\s+to\s+(\w+)",
            r"because\s+of\s+(\w+),\s+(\w+)",
            r"if\s+(\w+)\s+then\s+(\w+)",
        ]

        relations = []
        for pattern in causal_patterns:
            matches = re.findall(pattern, statement.lower())
            for cause, effect in matches:
                relations.append({"cause": cause, "effect": effect})

        return relations

    def _check_causal_consistency(
        self, causal1: List[Dict], causal2: List[Dict]
    ) -> Optional[Dict]:
        """Check causal consistency between relations"""
        # Simplified causal consistency check
        for rel1 in causal1:
            for rel2 in causal2:
                # Check for circular causation
                if rel1["cause"] == rel2["effect"] and rel1["effect"] == rel2["cause"]:
                    return {
                        "violation_type": "circular_causation",
                        "relation1": rel1,
                        "relation2": rel2,
                    }

        return None

    def _extract_definition(self, statement: str) -> Optional[Dict]:
        """Extract definitions from statement"""
        # Simplified definition extraction
        def_pattern = r"(\w+)\s+(?:is|means|equals?)\s+(.+)"
        match = re.search(def_pattern, statement.lower())

        if match:
            return {"entity": match.group(1), "definition": match.group(2).strip()}

        return None

    def _filter_contradictions(
        self, contradictions: List[Contradiction]
    ) -> List[Contradiction]:
        """Filter and deduplicate contradictions"""
        # Remove duplicates and low-confidence contradictions
        filtered = []
        seen_pairs = set()

        for contradiction in contradictions:
            pair = tuple(sorted(contradiction.location))
            if pair not in seen_pairs and contradiction.confidence > 0.5:
                filtered.append(contradiction)
                seen_pairs.add(pair)

        # Sort by severity and confidence
        filtered.sort(key=lambda x: (x.severity * x.confidence), reverse=True)

        return filtered[: self.max_contradictions]

    def _compute_consistency_score(self, contradictions: List[Contradiction]) -> float:
        """Compute overall consistency score"""
        if not contradictions:
            return 1.0

        # Weighted average of contradiction impacts
        total_weight = sum(c.severity * c.confidence for c in contradictions)
        return max(0.0, 1.0 - total_weight / len(contradictions))

    def _find_test_related_statements(
        self, test_name: str, statements: List[str]
    ) -> List[Tuple[int, str]]:
        """Find statements related to a failing test"""
        # Simplified test-statement matching
        related = []

        # Extract keywords from test name
        test_keywords = set(re.findall(r"\w+", test_name.lower()))

        for i, stmt in enumerate(statements):
            stmt_keywords = set(re.findall(r"\w+", stmt.lower()))

            # Simple keyword overlap
            overlap = test_keywords.intersection(stmt_keywords)
            if len(overlap) > 0:
                related.append((i, stmt))

        return related

    def _validate_against_fact(
        self, statements: List[str], fact: Dict
    ) -> List[Contradiction]:
        """Validate statements against a known fact"""
        contradictions = []

        fact_text = fact.get("text", "")
        fact_confidence = fact.get("confidence", 0.8)

        for i, stmt in enumerate(statements):
            # Simplified fact checking - could be much more sophisticated
            if self._statements_contradict(stmt, fact_text):
                contradiction = Contradiction(
                    contradiction_type=ContradictionType.EXTERNAL_CHECK,
                    confidence=fact_confidence,
                    severity=0.8,
                    location=(i, -2),  # -2 indicates external fact
                    evidence={
                        "statement": stmt,
                        "contradicting_fact": fact_text,
                        "fact_source": fact.get("source", "unknown"),
                    },
                    context="Statement contradicts known fact",
                    suggested_fix="Verify statement against external sources",
                )
                contradictions.append(contradiction)

        return contradictions

    def _statements_contradict(self, stmt1: str, stmt2: str) -> bool:
        """Simple contradiction detection between two statements"""
        # This is a placeholder - real implementation would be much more sophisticated
        norm1 = self._normalize_statement(stmt1)
        norm2 = self._normalize_statement(stmt2)

        # Look for explicit contradictions (very simplified)
        negation_words = {"not", "no", "never", "none", "cannot"}

        words1 = set(norm1.split())
        words2 = set(norm2.split())

        # If one has negation and they share many words, possible contradiction
        neg1 = bool(words1.intersection(negation_words))
        neg2 = bool(words2.intersection(negation_words))

        if neg1 != neg2:
            clean1 = words1 - negation_words
            clean2 = words2 - negation_words
            overlap = clean1.intersection(clean2)

            if len(overlap) > 2:  # Significant overlap
                return True

        return False

    def compute_K_field(self, S_field: np.ndarray, Lambda_field: np.ndarray) -> float:
        """Compute QRFT K field: K = S□Λ - Λ□S"""

        # Discrete Laplacian approximation
        def discrete_laplacian(field):
            if len(field) < 3:
                return np.zeros_like(field)

            laplacian = np.zeros_like(field)
            laplacian[1:-1] = field[2:] - 2 * field[1:-1] + field[:-2]
            return laplacian

        box_Lambda = discrete_laplacian(Lambda_field)
        box_S = discrete_laplacian(S_field)

        # Compute K = S□Λ - Λ□S
        K_field = np.mean(S_field) * box_Lambda - np.mean(Lambda_field) * box_S

        return float(np.linalg.norm(K_field))

    def generate_counterexamples(
        self, contradictions: List[Contradiction]
    ) -> List[Dict[str, Any]]:
        """Generate counterexamples for detected contradictions"""
        counterexamples = []

        for contradiction in contradictions:
            if contradiction.severity > self.severity_threshold:
                counterexample = {
                    "type": "contradiction_counterexample",
                    "contradiction_id": f"{contradiction.location[0]}_{contradiction.location[1]}",
                    "contradiction_type": contradiction.contradiction_type.value,
                    "evidence": contradiction.evidence,
                    "suggested_resolution": contradiction.suggested_fix,
                    "priority": contradiction.severity * contradiction.confidence,
                }
                counterexamples.append(counterexample)

        return counterexamples

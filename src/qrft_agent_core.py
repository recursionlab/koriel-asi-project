# src/qrft_agent_core.py
"""
QRFT-Native Deterministic Agent Core
No LLMs, no gradients - pure symbolic reasoning with QRFT control signals
"""

import re
import time
import json
import hashlib
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import uuid

# Local data utilities
try:  # pragma: no cover - import style varies between contexts
    from .data import load_corpus
except Exception:  # pragma: no cover
    from data import load_corpus

# Import math engine
try:
    from qrft_math_engine import QRFTMathEngine
    MATH_ENGINE_AVAILABLE = True
except ImportError:
    MATH_ENGINE_AVAILABLE = False
    print("Warning: QRFTMathEngine not available")

class FactPolarity(Enum):
    POSITIVE = "+"
    NEGATIVE = "-"

@dataclass
class Fact:
    """Atomic fact with polarity and source tracking"""
    predicate: str
    args: Tuple[str, ...]
    polarity: FactPolarity
    source: str
    timestamp: float
    confidence: float = 1.0
    
    def __hash__(self):
        return hash((self.predicate, self.args, self.polarity))
    
    def __str__(self):
        args_str = ", ".join(self.args) if self.args else ""
        sign = "" if self.polarity == FactPolarity.POSITIVE else "not "
        return f"{sign}{self.predicate}({args_str})"

@dataclass
class Gap:
    """Knowledge gap or constraint violation"""
    gap_type: str  # 'unbound_symbol', 'missing_fact', 'constraint_violation'
    description: str
    context: Dict[str, Any]
    priority: float = 0.5
    attempts: int = 0
    
    def __hash__(self):
        return hash((self.gap_type, self.description))

@dataclass
class PlanStep:
    """Single step in reasoning plan"""
    action: str  # 'retrieve', 'compute', 'check', 'ask', 'view_shift'
    target: str
    params: Dict[str, Any] = field(default_factory=dict)
    prerequisites: List[str] = field(default_factory=list)
    status: str = "pending"  # 'pending', 'executing', 'completed', 'failed'

class QRFTSignals:
    """QRFT control signals computed deterministically from state"""
    
    def __init__(self):
        self.X_G = 0.0  # Contradiction signal
        self.X_L = 0.0  # Lacuna/gap signal (L for Lacunon particle)
        self.X_F = 0.0  # Field novelty signal
        self.X_T = 0.0  # View mismatch/tesseracton signal
        self.last_update = time.time()
        
    def update(self, state: 'AgentState') -> None:
        """Update all signals from current state"""
        self.X_G = self._compute_contradiction_signal(state)
        self.X_L = self._compute_lacuna_signal(state)
        self.X_F = self._compute_field_novelty_signal(state)
        self.X_T = self._compute_view_mismatch_signal(state)
        self.last_update = time.time()
        
    def _compute_contradiction_signal(self, state: 'AgentState') -> float:
        """X_G = count of contradictions / total facts"""
        contradictions = state.get_contradictions()
        total_facts = len(state.facts)
        return len(contradictions) / max(total_facts, 1)
        
    def _compute_lacuna_signal(self, state: 'AgentState') -> float:
        """X_L = weighted gap urgency signal"""
        if not state.gaps:
            return 0.0
        
        gap_count = len(state.gaps)
        fact_count = len(state.facts)
        
        # Weight by gap priority and attempt count
        weighted_urgency = 0.0
        for gap in state.gaps:
            urgency = gap.priority * (1 + gap.attempts * 0.1)  # Increases with failed attempts
            weighted_urgency += urgency
        
        # Normalize by context size
        base_signal = gap_count / max(gap_count + fact_count, 1)
        priority_boost = weighted_urgency / max(gap_count, 1)  # Average priority
        
        return min(1.0, base_signal * (1 + priority_boost))
    
    def _compute_field_novelty_signal(self, state: 'AgentState') -> float:
        """X_F = novelty/entropy in current query vs known facts"""
        if not state.current_query:
            return 0.0
        
        query_terms = set(state.current_query.lower().split())
        known_terms = set()
        
        # Extract terms from facts
        for fact in state.facts:
            known_terms.add(fact.predicate.lower())
            known_terms.update(arg.lower() for arg in fact.args)
        
        if not known_terms:
            return 1.0  # All novel if no known terms
        
        novel_terms = query_terms - known_terms
        novelty_ratio = len(novel_terms) / max(len(query_terms), 1)
        
        return novelty_ratio
        
    def _compute_view_mismatch_signal(self, state: 'AgentState') -> float:
        """X_T = orthogonality between query terms and evidence terms"""
        if not state.current_query or not state.facts:
            return 0.0
            
        query_terms = set(state.current_query.lower().split())
        evidence_terms = set()
        
        for fact in state.facts:
            evidence_terms.update(fact.predicate.lower().split('_'))
            for arg in fact.args:
                evidence_terms.update(arg.lower().split())
                
        if not evidence_terms:
            return 1.0
            
        intersection = len(query_terms & evidence_terms)
        union = len(query_terms | evidence_terms)
        
        # Orthogonality = 1 - Jaccard similarity
        return 1.0 - (intersection / max(union, 1))

class ParaconsistentStore:
    """Truth maintenance system allowing contradictions"""
    
    def __init__(self):
        self.supports_positive: Dict[str, Set[Fact]] = defaultdict(set)
        self.supports_negative: Dict[str, Set[Fact]] = defaultdict(set)
        self.contradictions: Set[Tuple[Fact, Fact]] = set()
        
    def add_fact(self, fact: Fact) -> None:
        """Add fact to appropriate support set"""
        key = f"{fact.predicate}({','.join(fact.args)})"
        
        if fact.polarity == FactPolarity.POSITIVE:
            self.supports_positive[key].add(fact)
        else:
            self.supports_negative[key].add(fact)
            
        # Check for contradictions
        self._update_contradictions(key)
        
    def _update_contradictions(self, key: str) -> None:
        """Update contradiction set for given predicate key"""
        pos_facts = self.supports_positive[key]
        neg_facts = self.supports_negative[key]
        
        # Add all pos/neg pairs as contradictions (paraconsistent logic allows this)
        for pos_fact in pos_facts:
            for neg_fact in neg_facts:
                if self._facts_contradict(pos_fact, neg_fact):
                    self.contradictions.add((pos_fact, neg_fact))
    
    def _facts_contradict(self, fact1: Fact, fact2: Fact) -> bool:
        """Check if two facts contradict each other"""
        # Same predicate and args, opposite polarity
        return (fact1.predicate == fact2.predicate and 
                fact1.args == fact2.args and
                fact1.polarity != fact2.polarity)
                
    def get_contradictions(self) -> List[Tuple[Fact, Fact]]:
        """Get all contradictions"""
        return list(self.contradictions)
        
    def get_facts(self, predicate: str = None, polarity: FactPolarity = None) -> List[Fact]:
        """Get facts matching criteria"""
        results = []
        
        if predicate:
            key_pattern = f"{predicate}("
            for key, facts in self.supports_positive.items():
                if key.startswith(key_pattern):
                    if polarity is None or polarity == FactPolarity.POSITIVE:
                        results.extend(facts)
            for key, facts in self.supports_negative.items():
                if key.startswith(key_pattern):
                    if polarity is None or polarity == FactPolarity.NEGATIVE:
                        results.extend(facts)
        else:
            if polarity is None or polarity == FactPolarity.POSITIVE:
                for facts in self.supports_positive.values():
                    results.extend(facts)
            if polarity is None or polarity == FactPolarity.NEGATIVE:
                for facts in self.supports_negative.values():
                    results.extend(facts)
                    
        return results

class AgentState:
    """Complete agent state (S, Λ)"""
    
    def __init__(self):
        # S: Plan graph + facts
        self.plan_steps: List[PlanStep] = []
        self.fact_store = ParaconsistentStore()
        self.current_query: str = ""
        self.session_id: str = str(uuid.uuid4())
        
        # Λ: Gaps and constraints  
        self.gaps: Set[Gap] = set()
        self.unbound_symbols: Set[str] = set()
        self.failed_constraints: List[str] = []
        
        # Runtime state
        self.step_count: int = 0
        self.last_action: Optional[str] = None
        self.action_history: List[Dict[str, Any]] = []
        
        # Reasoning chain tracking
        self.reasoning_chains: List[Dict[str, Any]] = []
        self.current_chain_id: Optional[str] = None
        self.chain_depth: int = 0
        
    @property
    def facts(self) -> List[Fact]:
        """All facts in the store"""
        return self.fact_store.get_facts()
        
    def add_fact(self, predicate: str, args: Tuple[str, ...], polarity: FactPolarity, 
                 source: str, confidence: float = 1.0) -> Fact:
        """Add new fact to state"""
        fact = Fact(
            predicate=predicate,
            args=args, 
            polarity=polarity,
            source=source,
            timestamp=time.time(),
            confidence=confidence
        )
        self.fact_store.add_fact(fact)
        return fact
        
    def add_gap(self, gap_type: str, description: str, context: Dict[str, Any] = None) -> Gap:
        """Add knowledge gap"""
        gap = Gap(
            gap_type=gap_type,
            description=description,
            context=context or {},
            priority=0.5
        )
        self.gaps.add(gap)
        return gap
        
    def remove_gap(self, gap: Gap) -> None:
        """Remove resolved gap"""
        self.gaps.discard(gap)
        
    def add_plan_step(self, action: str, target: str, params: Dict[str, Any] = None) -> PlanStep:
        """Add step to plan"""
        step = PlanStep(
            action=action,
            target=target,
            params=params or {}
        )
        self.plan_steps.append(step)
        return step
        
    def get_contradictions(self) -> List[Tuple[Fact, Fact]]:
        """Get all contradictions"""
        return self.fact_store.get_contradictions()
        
    def get_pending_steps(self) -> List[PlanStep]:
        """Get steps that need execution"""
        return [step for step in self.plan_steps if step.status == "pending"]
    
    def start_reasoning_chain(self, query: str, chain_type: str = "general") -> str:
        """Start a new reasoning chain"""
        chain_id = str(uuid.uuid4())[:8]
        
        chain = {
            'id': chain_id,
            'type': chain_type,
            'query': query,
            'start_time': time.time(),
            'steps': [],
            'facts_at_start': len(self.facts),
            'gaps_at_start': len(self.gaps),
            'status': 'active'
        }
        
        self.reasoning_chains.append(chain)
        self.current_chain_id = chain_id
        self.chain_depth += 1
        
        return chain_id
    
    def add_reasoning_step(self, action: str, target: str, result: Any = None, 
                          reasoning: str = None) -> None:
        """Add step to current reasoning chain"""
        if not self.current_chain_id:
            return
            
        step = {
            'action': action,
            'target': target,
            'result': result,
            'reasoning': reasoning,
            'timestamp': time.time(),
            'facts_count': len(self.facts),
            'gaps_count': len(self.gaps),
            'contradictions_count': len(self.get_contradictions())
        }
        
        # Find current chain and add step
        for chain in self.reasoning_chains:
            if chain['id'] == self.current_chain_id:
                chain['steps'].append(step)
                break
    
    def complete_reasoning_chain(self, result: Any = None, success: bool = True) -> None:
        """Complete current reasoning chain"""
        if not self.current_chain_id:
            return
            
        for chain in self.reasoning_chains:
            if chain['id'] == self.current_chain_id:
                chain['status'] = 'completed' if success else 'failed'
                chain['end_time'] = time.time()
                chain['final_result'] = result
                chain['facts_gained'] = len(self.facts) - chain['facts_at_start']
                chain['gaps_resolved'] = chain['gaps_at_start'] - len(self.gaps)
                break
        
        self.current_chain_id = None
        self.chain_depth = max(0, self.chain_depth - 1)
    
    def get_reasoning_chain_summary(self) -> Dict[str, Any]:
        """Get summary of all reasoning chains"""
        return {
            'total_chains': len(self.reasoning_chains),
            'active_chains': len([c for c in self.reasoning_chains if c['status'] == 'active']),
            'completed_chains': len([c for c in self.reasoning_chains if c['status'] == 'completed']),
            'current_depth': self.chain_depth,
            'current_chain': self.current_chain_id,
            'chains': self.reasoning_chains[-5:]  # Last 5 chains
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """Serialize state for logging"""
        return {
            'session_id': self.session_id,
            'step_count': self.step_count,
            'current_query': self.current_query,
            'facts_count': len(self.facts),
            'gaps_count': len(self.gaps),
            'contradictions_count': len(self.get_contradictions()),
            'plan_steps_count': len(self.plan_steps),
            'pending_steps_count': len(self.get_pending_steps()),
            'last_action': self.last_action
        }

class QRFTPolicy:
    """QRFT control policy with event caps and cooldowns"""
    
    def __init__(self, 
                 tau_G: float = 0.3,  # Contradiction threshold
                 tau_F: float = 0.4,  # Gap threshold 
                 tau_T: float = 0.6,  # View mismatch threshold
                 event_cap: int = 1,  # Max events per turn
                 cooldown_turns: int = 3):
        
        self.tau_G = tau_G
        self.tau_F = tau_F  
        self.tau_T = tau_T
        self.event_cap = event_cap
        self.cooldown_turns = cooldown_turns
        
        # Cooldown tracking
        self.last_glitchon_turn = -999
        self.last_lacunon_turn = -999
        self.last_tesseracton_turn = -999
        
        # Event priorities (higher = more important)
        self.priorities = {
            'glitchon': 3,
            'lacunon': 2, 
            'tesseracton': 1
        }
        
    def decide_action(self, signals: QRFTSignals, state: AgentState) -> str:
        """Decide next action based on QRFT signals"""
        turn = state.step_count
        
        # Check cooldowns
        can_glitchon = (turn - self.last_glitchon_turn) >= self.cooldown_turns
        can_lacunon = (turn - self.last_lacunon_turn) >= self.cooldown_turns  
        can_tesseracton = (turn - self.last_tesseracton_turn) >= self.cooldown_turns
        
        # Collect triggered events with priorities
        events = []
        
        if signals.X_G > self.tau_G and can_glitchon:
            events.append(('glitchon', self.priorities['glitchon'], signals.X_G))
            
        if signals.X_F > self.tau_F and can_lacunon:
            events.append(('lacunon', self.priorities['lacunon'], signals.X_F))
            
        if signals.X_T > self.tau_T and can_tesseracton:
            events.append(('tesseracton', self.priorities['tesseracton'], signals.X_T))
            
        # Sort by priority, then by signal strength
        events.sort(key=lambda x: (x[1], x[2]), reverse=True)
        
        # Execute top event (respecting cap)
        if events:
            event_type = events[0][0]
            
            if event_type == 'glitchon':
                self.last_glitchon_turn = turn
                return 'counterexample'
            elif event_type == 'lacunon': 
                self.last_lacunon_turn = turn
                return 'retrieve' if state.gaps else 'ask'
            elif event_type == 'tesseracton':
                self.last_tesseracton_turn = turn
                return 'view_shift'
                
        # Default: continue plan or ask if no plan
        if state.get_pending_steps():
            return 'continue'
        else:
            return 'ask'

class QRFTAgent:
    """Main QRFT deterministic agent"""
    
    def __init__(self):
        self.state = AgentState()
        self.signals = QRFTSignals()
        self.policy = QRFTPolicy()
        
        # Mathematical reasoning engine
        self.math_engine = QRFTMathEngine() if MATH_ENGINE_AVAILABLE else None
        
        # Reasoners (will be implemented)
        self.reasoners = {}

        # Cached corpus for retrieval operations
        self._corpus_cache: Optional[List[str]] = None
        
        # Templates for rendering
        self.templates = {
            'ask': "I need more information about: {target}",
            'retrieve': "Let me search for: {target}",
            'compute': "Computing: {target}",
            'counterexample': "Found contradiction. Checking: {target}",
            'view_shift': "Switching perspective on: {target}",
            'plan': "Plan: {steps}",
            'cite': "Based on {source}: {content}",
            'abstain': "Insufficient evidence for: {target}"
        }
        
        # Event logging
        self.event_log: List[Dict[str, Any]] = []
        
    def process_input(self, user_input: str) -> str:
        """Main processing loop - deterministic with reasoning chain tracking"""
        start_time = time.time()
        
        # Start reasoning chain for complex queries
        chain_type = "mathematical" if self._is_mathematical_query(user_input) else "general"
        chain_id = self.state.start_reasoning_chain(user_input, chain_type)
        
        try:
            # Update state
            self.state.current_query = user_input
            self.state.step_count += 1
            
            # Parse input and extract facts/gaps
            self._parse_input(user_input)
            self.state.add_reasoning_step("parse", user_input, 
                                        reasoning=f"Extracted {len(self.state.facts)} facts")
            
            # Update QRFT signals
            self.signals.update(self.state)
            signal_summary = f"X_G:{self.signals.X_G:.2f} X_L:{self.signals.X_L:.2f} X_F:{self.signals.X_F:.2f} X_T:{self.signals.X_T:.2f}"
            self.state.add_reasoning_step("signals", "QRFT_computation", signal_summary,
                                        reasoning="Computed QRFT control signals")
            
            # Policy decision
            action = self.policy.decide_action(self.signals, self.state)
            self.state.last_action = action
            self.state.add_reasoning_step("decision", action, 
                                        reasoning=f"Policy selected action based on signals: {signal_summary}")
            
            # Execute action
            response = self._execute_action(action, user_input)
            self.state.add_reasoning_step("execute", action, response,
                                        reasoning=f"Executed {action} action")
            
            # Complete reasoning chain
            self.state.complete_reasoning_chain(response, success=True)
            
            # Log everything
            self._log_event(user_input, action, response, time.time() - start_time)
            
            return response
            
        except Exception as e:
            # Complete chain with failure
            self.state.complete_reasoning_chain(None, success=False)
            error_response = f"Processing error: {e}"
            self._log_event(user_input, "error", error_response, time.time() - start_time)
            return error_response
        
    def _parse_input(self, input_text: str) -> None:
        """Extract facts and identify gaps from input"""
        # Simple pattern matching for now
        # In production: proper parser with grammar
        
        # Extract potential facts
        sentences = input_text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Look for assertions
            if 'is' in sentence:
                # Handle negations
                is_negative = 'is not' in sentence or 'not' in sentence.lower()
                
                if 'is not' in sentence:
                    parts = sentence.split(' is not ')
                else:
                    parts = sentence.split(' is ')
                    
                if len(parts) == 2:
                    subject = parts[0].strip()
                    predicate = parts[1].strip()
                    
                    # Remove "not" from predicate if it's there
                    if predicate.startswith('not '):
                        predicate = predicate[4:]
                        is_negative = True
                    
                    polarity = FactPolarity.NEGATIVE if is_negative else FactPolarity.POSITIVE
                    
                    self.state.add_fact(
                        predicate='is',
                        args=(subject, predicate),
                        polarity=polarity,
                        source='user_input'
                    )
                    
        # Identify gaps (missing information)
        question_words = ['what', 'how', 'why', 'when', 'where', 'who']
        if any(word in input_text.lower() for word in question_words):
            self.state.add_gap(
                gap_type='missing_fact',
                description=f"Question about: {input_text}",
                context={'query': input_text}
            )
            
    def _execute_action(self, action: str, context: str) -> str:
        """Execute decided action and return response"""
        
        # First check if this is a mathematical query
        if self.math_engine and self._is_mathematical_query(context):
            return self._handle_mathematical_query(context)
        
        if action == 'ask':
            target = self._identify_missing_info()
            return self.templates['ask'].format(target=target)
            
        elif action == 'retrieve':
            target = self._identify_retrieval_target()
            try:
                results = self._search_corpus(target)
                if results:
                    snippet = results[0][:200]
                    self.state.add_fact(
                        predicate='retrieved_info',
                        args=(target, snippet),
                        polarity=FactPolarity.POSITIVE,
                        source='retrieval'
                    )
                    return self.templates['retrieve'].format(target=target) + f"\n{snippet}"
                else:
                    self.state.add_gap(
                        gap_type='retrieval_failure',
                        description=f"No information found for: {target}",
                        context={'query': target}
                    )
                    return self.templates['abstain'].format(target=target)
            except Exception as e:
                self.state.add_gap(
                    gap_type='retrieval_error',
                    description=f"Retrieval error for: {target}",
                    context={'query': target, 'error': str(e)}
                )
                return f"Retrieval error: {e}"
            
        elif action == 'counterexample':
            contradictions = self.state.get_contradictions()
            if contradictions:
                fact1, fact2 = contradictions[0]
                target = f"{fact1} vs {fact2}"
                return self.templates['counterexample'].format(target=target)
            else:
                return "Checking for contradictions..."
                
        elif action == 'view_shift':
            return self.templates['view_shift'].format(target=context)
            
        elif action == 'continue':
            pending_steps = self.state.get_pending_steps()
            if pending_steps:
                step = pending_steps[0]
                step.status = 'executing'
                return f"Executing: {step.action} on {step.target}"
            else:
                return "Continuing analysis..."
                
        elif action == 'compute':
            # Mathematical computation
            if self.math_engine:
                return self._handle_mathematical_query(context)
            else:
                return "Mathematical reasoning not available"
                
        else:
            return f"Processing: {action}"
            
    def _identify_missing_info(self) -> str:
        """Identify what information is missing"""
        if self.state.gaps:
            gap = next(iter(self.state.gaps))
            return gap.description
        return "clarification"
        
    def _identify_retrieval_target(self) -> str:
        """Identify what to retrieve"""
        if self.state.unbound_symbols:
            return next(iter(self.state.unbound_symbols))
        if self.state.gaps:
            gap = next(iter(self.state.gaps))
            return gap.description
        return self.state.current_query

    def _search_corpus(self, query: str) -> List[str]:
        """Search cached corpus for lines matching query"""
        if self._corpus_cache is None:
            try:
                # Use fallback corpus to keep retrieval deterministic for tests
                corpus_arrays = load_corpus(root="nonexistent")
                self._corpus_cache = []
                for arr in corpus_arrays:
                    try:
                        self._corpus_cache.append(arr.tobytes().decode('utf-8'))
                    except Exception:
                        continue
            except Exception as e:
                raise RuntimeError(f"Corpus loading failed: {e}")

        pattern = re.compile(re.escape(query), re.IGNORECASE)
        return [line.strip() for line in self._corpus_cache if pattern.search(line)]
        
    def _log_event(self, input_text: str, action: str, response: str, duration: float) -> None:
        """Log event for observability"""
        event = {
            'timestamp': time.time(),
            'session_id': self.state.session_id,
            'step': self.state.step_count,
            'input': input_text,
            'action': action,
            'response': response,
            'duration_ms': duration * 1000,
            'signals': {
                'X_G': self.signals.X_G,
                'X_F': self.signals.X_F,
                'X_T': self.signals.X_T
            },
            'state_summary': self.state.to_dict()
        }
        
        self.event_log.append(event)
    
    def _is_mathematical_query(self, query: str) -> bool:
        """Check if query requires mathematical computation"""
        math_keywords = [
            'solve', 'differentiate', 'integrate', 'limit', 'factor', 'expand', 'simplify',
            'derivative', 'integral', 'equation', 'calculate', 'compute', '=', '+', '-', '*', 
            '/', '^', 'x^', 'sin', 'cos', 'tan', 'log', 'ln', 'exp', 'sqrt'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in math_keywords)
    
    def _handle_mathematical_query(self, query: str) -> str:
        """Handle mathematical computation query"""
        if not self.math_engine or not self.math_engine.available:
            return "Mathematical reasoning not available (SymPy required)"
        
        try:
            result = self.math_engine.process_math_query(query)
            
            if result.success:
                # Store mathematical facts
                self.state.add_fact(
                    "mathematical_result",
                    (query, str(result.result)),
                    FactPolarity.POSITIVE,
                    "mathematical_computation"
                )
                
                # Format response
                response_parts = [f"Mathematical computation result: {result.result}"]
                
                if result.steps:
                    response_parts.append("Solution steps:")
                    response_parts.extend(f"  {step}" for step in result.steps)
                
                if result.computation_time > 0:
                    response_parts.append(f"Computation time: {result.computation_time:.3f}s")
                
                return "\n".join(response_parts)
            else:
                # Create gap for unsolved mathematical problem
                self.state.add_gap(
                    "mathematical_computation_failed",
                    f"Could not solve: {query}",
                    {'error': result.error, 'query': query}
                )
                
                return f"Mathematical computation failed: {result.error}"
                
        except Exception as e:
            self.state.add_gap(
                "mathematical_system_error", 
                f"Math engine error for: {query}",
                {'error': str(e), 'query': query}
            )
            return f"Mathematical system error: {e}"
        
    def get_state_summary(self) -> Dict[str, Any]:
        """Get current agent state for inspection"""
        return {
            'state': self.state.to_dict(),
            'signals': {
                'X_G': self.signals.X_G,
                'X_L': self.signals.X_L,
                'X_F': self.signals.X_F, 
                'X_T': self.signals.X_T
            },
            'facts': [str(fact) for fact in self.state.facts],
            'gaps': [gap.description for gap in self.state.gaps],
            'contradictions': [f"{f1} contradicts {f2}" for f1, f2 in self.state.get_contradictions()],
            'plan': [f"{step.action}: {step.target} ({step.status})" for step in self.state.plan_steps],
            'reasoning_chains': self.state.get_reasoning_chain_summary(),
            'math_available': self.math_engine is not None and self.math_engine.available if self.math_engine else False
        }
        
    def save_log(self, filename: str) -> None:
        """Save event log to file"""
        with open(filename, 'w') as f:
            json.dump(self.event_log, f, indent=2, default=str)

# Factory function
def create_qrft_agent() -> QRFTAgent:
    """Create QRFT agent with default configuration"""
    return QRFTAgent()
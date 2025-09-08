# src/qrft_agent_integrated.py
"""
QRFT Agent with Integrated Local Reasoners
Complete deterministic agent with BM25, SymPy, constraint solving
"""

from typing import List
from .qrft_agent_core import QRFTAgent, FactPolarity
from .qrft_reasoners import ReasonerHub, Document

class IntegratedQRFTAgent(QRFTAgent):
    """QRFT Agent with full reasoner integration"""
    
    def __init__(self):
        super().__init__()
        self.reasoners = ReasonerHub()
        
        # Enhanced templates with citations
        self.templates.update({
            'ask': "I need clarification: {target}",
            'retrieve': "Let me search my knowledge base for: {target}",
            'compute': "Computing: {operation} of {expression}",
            'counterexample': "Testing claim with counterexamples: {target}",
            'view_shift': "Reconsidering from different angle: {target}",
            'cite': "According to {source}: {content}",
            'abstain': "I don't have sufficient evidence to answer: {target}",
            'constraint_violation': "Found constraint violation: {details}",
            'contradiction_resolved': "Resolved contradiction using: {method}"
        })
        
        # Citation requirements
        self.require_citations = True
        self.uncertainty_threshold = 0.7
        
    def add_knowledge_base(self, documents: List[Document]) -> None:
        """Add documents to knowledge base"""
        self.reasoners.add_documents(documents)
        
        # Add facts from documents
        for doc in documents:
            self.state.add_fact(
                predicate='has_document',
                args=(doc.doc_id, doc.title),
                polarity=FactPolarity.POSITIVE,
                source='knowledge_base'
            )
            
    def _execute_action(self, action: str, context: str) -> str:
        """Enhanced action execution with reasoner integration"""
        
        if action == 'retrieve':
            return self._execute_retrieve(context)
            
        elif action == 'compute':
            return self._execute_compute(context)
            
        elif action == 'counterexample':
            return self._execute_counterexample(context)
            
        elif action == 'ask':
            return self._execute_ask(context)
            
        elif action == 'view_shift':
            return self._execute_view_shift(context)
            
        elif action == 'continue':
            return self._execute_continue()
            
        else:
            return super()._execute_action(action, context)
            
    def _execute_retrieve(self, query: str) -> str:
        """Execute retrieval with BM25 and citations"""
        results = self.reasoners.search(query, top_k=3)
        
        if not results:
            self.state.add_gap(
                gap_type='retrieval_failure',
                description=f"No results for: {query}",
                context={'query': query}
            )
            return self.templates['abstain'].format(target=query)
            
        # Process results and add facts
        response_parts = ["Found relevant information:"]
        
        for doc_id, score, chunk in results:
            # Add retrieved fact
            self.state.add_fact(
                predicate='retrieved_info',
                args=(query, doc_id, str(score)),
                polarity=FactPolarity.POSITIVE,
                source='retrieval'
            )
            
            # Remove gaps that this retrieval addresses
            gaps_to_remove = []
            for gap in self.state.gaps:
                if query.lower() in gap.description.lower():
                    gaps_to_remove.append(gap)
                    
            for gap in gaps_to_remove:
                self.state.remove_gap(gap)
                
            # Format with citation
            citation = self.templates['cite'].format(
                source=doc_id,
                content=chunk[:200] + "..." if len(chunk) > 200 else chunk
            )
            response_parts.append(citation)
            
        return "\n".join(response_parts)
        
    def _execute_compute(self, expression: str) -> str:
        """Execute symbolic computation"""
        # Try to identify operation and variables
        if '=' in expression:
            # Equation solving
            parts = expression.split('=')
            if len(parts) == 2:
                equation = f"Eq({parts[0].strip()}, {parts[1].strip()})"
                
                # Try to identify variable
                import re
                variables = re.findall(r'\b[a-zA-Z]\w*\b', expression)
                variables = [v for v in variables if v not in ['sin', 'cos', 'tan', 'log', 'exp']]
                
                if variables:
                    var = variables[0]  # Use first variable found
                    solutions = self.reasoners.compute('solve', equation, var)
                    
                    if solutions:
                        self.state.add_fact(
                            predicate='computed_solution',
                            args=(expression, str(solutions)),
                            polarity=FactPolarity.POSITIVE,
                            source='cas'
                        )
                        
                        return self.templates['compute'].format(
                            operation='solve',
                            expression=f"{expression} for {var}"
                        ) + f"\nSolutions: {solutions}"
                        
        elif 'd/d' in expression or "derivative" in expression.lower():
            # Differentiation
            # Extract function and variable (simplified)
            func_part = expression.replace('d/d', '').replace('derivative', '').strip()
            
            result = self.reasoners.compute('differentiate', func_part, 'x')
            if result:
                self.state.add_fact(
                    predicate='computed_derivative',
                    args=(func_part, result),
                    polarity=FactPolarity.POSITIVE,
                    source='cas'
                )
                
                return self.templates['compute'].format(
                    operation='differentiate',
                    expression=func_part
                ) + f"\nResult: {result}"
                
        else:
            # Try simplification
            result = self.reasoners.compute('simplify', expression)
            if result:
                self.state.add_fact(
                    predicate='simplified_expression',
                    args=(expression, result),
                    polarity=FactPolarity.POSITIVE,
                    source='cas'
                )
                
                return self.templates['compute'].format(
                    operation='simplify',
                    expression=expression
                ) + f"\nResult: {result}"
                
        return f"Could not compute: {expression}"
        
    def _execute_counterexample(self, claim: str) -> str:
        """Execute counterexample generation"""
        contradictions = self.state.get_contradictions()
        
        if contradictions:
            fact1, fact2 = contradictions[0]
            
            # Generate counterexamples for the contradiction
            counterexamples = self.reasoners.find_counterexamples(str(fact1))
            
            if counterexamples:
                self.state.add_fact(
                    predicate='found_counterexample',
                    args=(str(fact1), str(counterexamples[0])),
                    polarity=FactPolarity.POSITIVE,
                    source='counterexample_miner'
                )
                
                return self.templates['counterexample'].format(
                    target=f"{fact1} vs {fact2}"
                ) + f"\nCounterexample approach: {counterexamples[0]}"
            else:
                return f"Analyzing contradiction between {fact1} and {fact2}"
        else:
            # No contradictions, generate counterexamples for current query
            counterexamples = self.reasoners.find_counterexamples(claim)
            
            if counterexamples:
                return self.templates['counterexample'].format(
                    target=claim
                ) + f"\nTesting with: {counterexamples[0]}"
            else:
                return f"No counterexamples found for: {claim}"
                
    def _execute_ask(self, context: str) -> str:
        """Execute clarification request"""
        missing_info = self._identify_missing_info()
        
        # Be specific about what's needed
        if self.state.unbound_symbols:
            symbols = list(self.state.unbound_symbols)[:3]  # Top 3
            return self.templates['ask'].format(
                target=f"definitions for: {', '.join(symbols)}"
            )
            
        elif self.state.gaps:
            gap = next(iter(self.state.gaps))
            return self.templates['ask'].format(target=gap.description)
            
        else:
            return self.templates['ask'].format(target=missing_info)
            
    def _execute_view_shift(self, context: str) -> str:
        """Execute perspective shift"""
        # Analyze current approach
        current_facts = len(self.state.facts)
        current_gaps = len(self.state.gaps)
        
        if current_gaps > current_facts:
            # Too many gaps - try broader search
            return self.templates['view_shift'].format(
                target="broader information search"
            ) + "\nSwitching to higher-level concepts."
            
        elif current_facts > 10 and current_gaps == 0:
            # Lots of facts but no progress - try synthesis
            return self.templates['view_shift'].format(
                target="information synthesis"
            ) + "\nAttempting to connect established facts."
            
        else:
            # Try different reasoning approach
            return self.templates['view_shift'].format(
                target="alternative reasoning method"
            ) + "\nConsidering problem from different angle."
            
    def _execute_continue(self) -> str:
        """Execute plan continuation"""
        pending_steps = self.state.get_pending_steps()
        
        if pending_steps:
            step = pending_steps[0]
            step.status = 'executing'
            
            if step.action == 'retrieve':
                return self._execute_retrieve(step.target)
            elif step.action == 'compute':
                return self._execute_compute(step.target)
            elif step.action == 'check':
                return self._execute_constraint_check(step.target)
            else:
                return f"Executing: {step.action} on {step.target}"
        else:
            return "Plan completed. Ready for next query."
            
    def _execute_constraint_check(self, constraint: str) -> str:
        """Check constraint consistency"""
        self.reasoners.add_constraint(constraint)
        
        consistent, violations = self.reasoners.check_constraints()
        
        if consistent:
            self.state.add_fact(
                predicate='constraint_satisfied',
                args=(constraint,),
                polarity=FactPolarity.POSITIVE,
                source='constraint_solver'
            )
            return f"Constraint satisfied: {constraint}"
        else:
            self.state.add_fact(
                predicate='constraint_violated',
                args=(constraint, str(violations)),
                polarity=FactPolarity.NEGATIVE,
                source='constraint_solver'
            )
            return self.templates['constraint_violation'].format(
                details='; '.join(violations)
            )
            
    def _parse_input(self, input_text: str) -> None:
        """Enhanced input parsing with math and constraint detection"""
        super()._parse_input(input_text)
        
        # Detect mathematical expressions
        import re
        
        # Look for equations
        equation_patterns = [
            r'[\w\s\+\-\*/\^\(\)]+\s*=\s*[\w\s\+\-\*/\^\(\)]+',
            r'solve\s+[\w\s\+\-\*/\^\(\)=]+',
            r'[\w\s\+\-\*/\^\(\)]+\s*>\s*[\w\s\+\-\*/\^\(\)]+',
            r'[\w\s\+\-\*/\^\(\)]+\s*<\s*[\w\s\+\-\*/\^\(\)]+',
        ]
        
        for pattern in equation_patterns:
            matches = re.findall(pattern, input_text)
            for match in matches:
                self.state.add_plan_step(
                    action='compute',
                    target=match.strip(),
                    params={'type': 'equation'}
                )
                
        # Look for undefined variables/symbols
        symbol_pattern = r'\b[a-zA-Z]\w*\b'
        symbols = set(re.findall(symbol_pattern, input_text))
        
        # Filter out common words
        common_words = {
            'the', 'and', 'or', 'is', 'are', 'was', 'were', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'can', 'could', 'may', 'might', 'must', 'should', 'shall',
            'what', 'when', 'where', 'why', 'how', 'who', 'which',
            'solve', 'find', 'compute', 'calculate', 'show', 'prove'
        }
        
        unknown_symbols = symbols - common_words
        
        for symbol in unknown_symbols:
            if len(symbol) <= 3:  # Likely mathematical variables
                self.state.unbound_symbols.add(symbol)
                self.state.add_gap(
                    gap_type='unbound_symbol',
                    description=f"Definition needed for: {symbol}",
                    context={'symbol': symbol, 'query': input_text}
                )

def create_demo_knowledge_base() -> List[Document]:
    """Create sample knowledge base for testing"""
    documents = [
        Document(
            doc_id="math_basics",
            title="Basic Mathematics",
            content="""
            Algebra is the branch of mathematics dealing with symbols and rules for manipulating symbols.
            A quadratic equation is a second-degree polynomial equation in a single variable x.
            The general form is ax² + bx + c = 0, where a ≠ 0.
            The quadratic formula is x = (-b ± √(b² - 4ac)) / 2a.
            Derivatives measure the rate of change of a function.
            The derivative of x² is 2x. The derivative of sin(x) is cos(x).
            """
        ),
        Document(
            doc_id="physics_basics", 
            title="Basic Physics",
            content="""
            Physics is the natural science that studies matter, its motion and behavior through space and time.
            Newton's laws of motion describe the relationship between forces and motion.
            F = ma relates force, mass, and acceleration.
            Energy is conserved in isolated systems.
            Kinetic energy is KE = ½mv² where m is mass and v is velocity.
            Potential energy depends on position in a force field.
            """
        ),
        Document(
            doc_id="logic_basics",
            title="Logic and Reasoning", 
            content="""
            Logic is the systematic study of valid rules of inference.
            A contradiction occurs when a statement and its negation are both asserted.
            Modus ponens: if P implies Q, and P is true, then Q is true.
            Modus tollens: if P implies Q, and Q is false, then P is false.
            A counterexample is a specific case that contradicts a general statement.
            Proof by contradiction assumes the negation and derives a contradiction.
            """
        )
    ]
    
    return documents

# Factory function
def create_integrated_agent() -> IntegratedQRFTAgent:
    """Create integrated QRFT agent with sample knowledge"""
    agent = IntegratedQRFTAgent()
    
    # Add demo knowledge base
    kb = create_demo_knowledge_base()
    agent.add_knowledge_base(kb)
    
    return agent
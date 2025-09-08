# src/qrft_reasoners.py
"""
QRFT Local Reasoners - No LLM dependencies
BM25 retrieval, SymPy CAS, basic constraint solving
"""

import re
import math
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict, Counter
import sympy as sp
from sympy import symbols, solve, simplify, diff, integrate, expand, factor

@dataclass
class Document:
    """Local document for retrieval"""
    doc_id: str
    title: str
    content: str
    chunks: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.chunks is None:
            self.chunks = self._chunk_content()
        if self.metadata is None:
            self.metadata = {}
            
    def _chunk_content(self, chunk_size: int = 200) -> List[str]:
        """Split content into chunks for retrieval"""
        words = self.content.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
            
        return chunks

class BM25Retriever:
    """Local BM25 retrieval - no external dependencies"""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents: Dict[str, Document] = {}
        self.term_doc_freq: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.doc_lengths: Dict[str, int] = {}
        self.avg_doc_length = 0.0
        self.vocab: Set[str] = set()
        
    def add_document(self, doc: Document) -> None:
        """Add document to retrieval index"""
        self.documents[doc.doc_id] = doc
        
        # Process all chunks
        all_text = doc.title + " " + " ".join(doc.chunks)
        tokens = self._tokenize(all_text)
        
        self.doc_lengths[doc.doc_id] = len(tokens)
        
        # Update term frequencies
        term_counts = Counter(tokens)
        for term, count in term_counts.items():
            self.term_doc_freq[term][doc.doc_id] = count
            self.vocab.add(term)
            
        # Update average document length
        total_length = sum(self.doc_lengths.values())
        self.avg_doc_length = total_length / len(self.documents)
        
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        # Convert to lowercase, remove punctuation, split
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        tokens = text.split()
        return [token for token in tokens if len(token) > 2]  # Remove short words
        
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, str]]:
        """Search documents using BM25 scoring"""
        query_tokens = self._tokenize(query)
        
        if not query_tokens:
            return []
            
        # Compute BM25 scores for each document
        scores = {}
        
        for doc_id in self.documents:
            score = 0.0
            
            for term in query_tokens:
                if term in self.term_doc_freq:
                    # Term frequency in document
                    tf = self.term_doc_freq[term][doc_id]
                    
                    # Document frequency
                    df = len(self.term_doc_freq[term])
                    
                    # Inverse document frequency
                    idf = math.log((len(self.documents) - df + 0.5) / (df + 0.5))
                    
                    # Document length normalization
                    doc_len = self.doc_lengths[doc_id]
                    norm = self.k1 * ((1 - self.b) + self.b * (doc_len / self.avg_doc_length))
                    
                    # BM25 component for this term
                    term_score = idf * (tf * (self.k1 + 1)) / (tf + norm)
                    score += term_score
                    
            scores[doc_id] = score
            
        # Sort by score and return top-k
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in sorted_docs[:top_k]:
            doc = self.documents[doc_id]
            
            # Find best matching chunk
            best_chunk = self._find_best_chunk(doc, query_tokens)
            
            results.append((doc_id, score, best_chunk))
            
        return results
        
    def _find_best_chunk(self, doc: Document, query_tokens: List[str]) -> str:
        """Find chunk with most query term overlap"""
        best_chunk = doc.chunks[0] if doc.chunks else doc.content[:200]
        best_score = 0
        
        for chunk in doc.chunks:
            chunk_tokens = set(self._tokenize(chunk))
            overlap = len(set(query_tokens) & chunk_tokens)
            
            if overlap > best_score:
                best_score = overlap
                best_chunk = chunk
                
        return best_chunk

class SymPyCAS:
    """SymPy Computer Algebra System wrapper"""
    
    def __init__(self):
        self.variables: Dict[str, sp.Symbol] = {}
        self.expressions: Dict[str, sp.Expr] = {}
        
    def define_variable(self, name: str) -> sp.Symbol:
        """Define a symbolic variable"""
        var = symbols(name)
        self.variables[name] = var
        return var
        
    def define_expression(self, name: str, expr_str: str) -> Optional[sp.Expr]:
        """Define a symbolic expression"""
        try:
            # Parse expression string
            expr = sp.sympify(expr_str, locals=self.variables)
            self.expressions[name] = expr
            return expr
        except Exception as e:
            print(f"Failed to parse expression '{expr_str}': {e}")
            return None
            
    def solve_equation(self, equation_str: str, variable: str) -> List[Any]:
        """Solve equation for given variable"""
        try:
            if variable not in self.variables:
                self.define_variable(variable)
                
            eq = sp.sympify(equation_str, locals=self.variables)
            var = self.variables[variable]
            
            solutions = solve(eq, var)
            return [str(sol) for sol in solutions]
            
        except Exception as e:
            print(f"Failed to solve equation '{equation_str}': {e}")
            return []
            
    def differentiate(self, expr_str: str, variable: str) -> Optional[str]:
        """Compute derivative"""
        try:
            if variable not in self.variables:
                self.define_variable(variable)
                
            expr = sp.sympify(expr_str, locals=self.variables)
            var = self.variables[variable]
            
            derivative = diff(expr, var)
            return str(derivative)
            
        except Exception as e:
            print(f"Failed to differentiate '{expr_str}': {e}")
            return None
            
    def integrate(self, expr_str: str, variable: str) -> Optional[str]:
        """Compute integral"""
        try:
            if variable not in self.variables:
                self.define_variable(variable)
                
            expr = sp.sympify(expr_str, locals=self.variables)
            var = self.variables[variable]
            
            integral = integrate(expr, var)
            return str(integral)
            
        except Exception as e:
            print(f"Failed to integrate '{expr_str}': {e}")
            return None
            
    def simplify_expression(self, expr_str: str) -> Optional[str]:
        """Simplify expression"""
        try:
            expr = sp.sympify(expr_str, locals=self.variables)
            simplified = simplify(expr)
            return str(simplified)
        except Exception as e:
            print(f"Failed to simplify '{expr_str}': {e}")
            return None
            
    def expand_expression(self, expr_str: str) -> Optional[str]:
        """Expand expression"""
        try:
            expr = sp.sympify(expr_str, locals=self.variables)
            expanded = expand(expr)
            return str(expanded)
        except Exception as e:
            print(f"Failed to expand '{expr_str}': {e}")
            return None
            
    def factor_expression(self, expr_str: str) -> Optional[str]:
        """Factor expression"""
        try:
            expr = sp.sympify(expr_str, locals=self.variables)
            factored = factor(expr)
            return str(factored)
        except Exception as e:
            print(f"Failed to factor '{expr_str}': {e}")
            return None

class BasicConstraintSolver:
    """Simple constraint solver for basic relationships"""
    
    def __init__(self):
        self.constraints: List[str] = []
        self.variables: Set[str] = set()
        
    def add_constraint(self, constraint: str) -> None:
        """Add constraint (e.g., 'x > 0', 'x + y = 5')"""
        self.constraints.append(constraint)
        
        # Extract variables (simple pattern matching)
        variables = re.findall(r'\b[a-zA-Z]\w*\b', constraint)
        self.variables.update(variables)
        
    def check_consistency(self) -> Tuple[bool, List[str]]:
        """Check if constraints are consistent"""
        violations = []
        
        # Simple consistency checks
        for i, c1 in enumerate(self.constraints):
            for j, c2 in enumerate(self.constraints[i+1:], i+1):
                violation = self._check_constraint_pair(c1, c2)
                if violation:
                    violations.append(f"Constraint {i+1} conflicts with {j+1}: {violation}")
                    
        return len(violations) == 0, violations
        
    def _check_constraint_pair(self, c1: str, c2: str) -> Optional[str]:
        """Check if two constraints conflict"""
        # Very basic conflict detection
        # In practice, would use proper constraint solver
        
        # Look for obvious conflicts like x > 5 and x < 3
        if self._extract_bound(c1) and self._extract_bound(c2):
            var1, op1, val1 = self._extract_bound(c1)
            var2, op2, val2 = self._extract_bound(c2)
            
            if var1 == var2:  # Same variable
                if op1 == '>' and op2 == '<' and val1 >= val2:
                    return f"{var1} cannot be both > {val1} and < {val2}"
                elif op1 == '<' and op2 == '>' and val1 <= val2:
                    return f"{var1} cannot be both < {val1} and > {val2}"
                    
        return None
        
    def _extract_bound(self, constraint: str) -> Optional[Tuple[str, str, float]]:
        """Extract variable, operator, and value from bound constraint"""
        patterns = [
            r'(\w+)\s*>\s*(-?\d+(?:\.\d+)?)',
            r'(\w+)\s*<\s*(-?\d+(?:\.\d+)?)',
            r'(\w+)\s*>=\s*(-?\d+(?:\.\d+)?)',
            r'(\w+)\s*<=\s*(-?\d+(?:\.\d+)?)',
        ]
        
        ops = ['>', '<', '>=', '<=']
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, constraint)
            if match:
                var = match.group(1)
                value = float(match.group(2))
                op = ops[i]
                return var, op, value
                
        return None

class CounterexampleMiner:
    """Generate counterexamples to test claims"""
    
    def __init__(self):
        self.strategies = [
            self._boundary_cases,
            self._negation_cases,
            self._edge_cases
        ]
        
    def generate_counterexamples(self, claim: str) -> List[Dict[str, Any]]:
        """Generate potential counterexamples for claim"""
        counterexamples = []
        
        for strategy in self.strategies:
            examples = strategy(claim)
            counterexamples.extend(examples)
            
        return counterexamples
        
    def _boundary_cases(self, claim: str) -> List[Dict[str, Any]]:
        """Generate boundary case counterexamples"""
        examples = []
        
        # Look for numeric claims
        numbers = re.findall(r'-?\d+(?:\.\d+)?', claim)
        
        for num_str in numbers:
            num = float(num_str)
            
            # Test boundary values
            boundary_tests = [
                {'type': 'boundary', 'original': num, 'test': 0},
                {'type': 'boundary', 'original': num, 'test': num - 1},
                {'type': 'boundary', 'original': num, 'test': num + 1},
                {'type': 'boundary', 'original': num, 'test': -num},
            ]
            
            examples.extend(boundary_tests)
            
        return examples
        
    def _negation_cases(self, claim: str) -> List[Dict[str, Any]]:
        """Generate negation counterexamples"""
        examples = []
        
        # Simple negation patterns
        if 'all' in claim.lower():
            examples.append({
                'type': 'negation',
                'strategy': 'existential_counterexample', 
                'original_claim': claim,
                'test': 'Find case where claim fails'
            })
            
        if 'always' in claim.lower():
            examples.append({
                'type': 'negation',
                'strategy': 'exception_case',
                'original_claim': claim, 
                'test': 'Find situation where claim does not hold'
            })
            
        return examples
        
    def _edge_cases(self, claim: str) -> List[Dict[str, Any]]:
        """Generate edge case counterexamples"""
        examples = []
        
        # Common edge cases
        edge_tests = []
        
        if 'positive' in claim.lower():
            edge_tests.append({'type': 'edge', 'test': 'zero_case', 'value': 0})
            edge_tests.append({'type': 'edge', 'test': 'negative_case', 'value': -1})
            
        if 'finite' in claim.lower():
            edge_tests.append({'type': 'edge', 'test': 'infinity_case', 'value': 'infinity'})
            
        if 'continuous' in claim.lower():
            edge_tests.append({'type': 'edge', 'test': 'discontinuity_case', 'description': 'test at discontinuity'})
            
        examples.extend(edge_tests)
        
        return examples

class ReasonerHub:
    """Central hub for all local reasoners"""
    
    def __init__(self):
        self.retriever = BM25Retriever()
        self.cas = SymPyCAS()
        self.constraint_solver = BasicConstraintSolver()
        self.counterexample_miner = CounterexampleMiner()
        
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to retrieval system"""
        for doc in documents:
            self.retriever.add_document(doc)
            
    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float, str]]:
        """Search for relevant information"""
        return self.retriever.search(query, top_k)
        
    def compute(self, operation: str, expression: str, variable: str = None) -> Optional[str]:
        """Perform symbolic computation"""
        if operation == 'solve':
            if variable:
                return self.cas.solve_equation(expression, variable)
            else:
                return None
        elif operation == 'differentiate':
            if variable:
                return self.cas.differentiate(expression, variable)
        elif operation == 'integrate':
            if variable:
                return self.cas.integrate(expression, variable)
        elif operation == 'simplify':
            return self.cas.simplify_expression(expression)
        elif operation == 'expand':
            return self.cas.expand_expression(expression)
        elif operation == 'factor':
            return self.cas.factor_expression(expression)
        else:
            return None
            
    def check_constraints(self) -> Tuple[bool, List[str]]:
        """Check constraint consistency"""
        return self.constraint_solver.check_consistency()
        
    def find_counterexamples(self, claim: str) -> List[Dict[str, Any]]:
        """Generate counterexamples for claim"""
        return self.counterexample_miner.generate_counterexamples(claim)
        
    def add_constraint(self, constraint: str) -> None:
        """Add constraint to solver"""
        self.constraint_solver.add_constraint(constraint)

# Factory function
def create_reasoner_hub() -> ReasonerHub:
    """Create reasoner hub with all components"""
    return ReasonerHub()
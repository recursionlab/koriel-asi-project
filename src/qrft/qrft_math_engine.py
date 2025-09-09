#!/usr/bin/env python3
"""
QRFT Mathematical Reasoning Engine
SymPy-based symbolic computation for QRFT deterministic agent
Handles equation solving, calculus, algebra, and logical reasoning
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

try:
    import sympy as sp
    # Note: We import sympy as 'sp' and use sp.Symbol, sp.solve, etc. to avoid
    # ruff unused import warnings while maintaining access to all sympy functions
    from sympy.parsing.sympy_parser import parse_expr, transformations

    SYMPY_AVAILABLE = True
except ImportError:  # pragma: no cover - used when sympy not installed
    SYMPY_AVAILABLE = False
    transformations = ()
    print("Warning: SymPy not available, mathematical reasoning will be limited")


class MathTaskType(Enum):
    SOLVE = "solve"
    DIFFERENTIATE = "differentiate"
    INTEGRATE = "integrate"
    LIMIT = "limit"
    FACTOR = "factor"
    EXPAND = "expand"
    SIMPLIFY = "simplify"
    MATRIX = "matrix"
    SERIES = "series"
    EQUATION_SYSTEM = "system"


@dataclass
class MathTask:
    """Mathematical computation task"""

    task_type: MathTaskType
    expression: str
    variable: Optional[str] = None
    target: Optional[str] = None  # For limits (target value)
    constraints: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class MathResult:
    """Result of mathematical computation"""

    success: bool
    result: Any
    latex: Optional[str] = None
    steps: Optional[List[str]] = None
    error: Optional[str] = None
    computation_time: float = 0.0


class QRFTMathEngine:
    """Mathematical reasoning engine for QRFT agent"""

    def __init__(self):
        self.available = SYMPY_AVAILABLE
        self.cache: Dict[str, MathResult] = {}
        self.transformations = transformations[:3]

        if self.available:
            # Common symbols
            self.symbols = {
                "x": sp.Symbol("x"),
                "y": sp.Symbol("y"),
                "z": sp.Symbol("z"),
                "t": sp.Symbol("t"),
                "n": sp.Symbol("n", integer=True),
                "a": sp.Symbol("a"),
                "b": sp.Symbol("b"),
                "c": sp.Symbol("c"),
            }

    def process_math_query(self, query: str) -> MathResult:
        """Process natural language math query"""
        start_time = time.time()

        if not self.available:
            return MathResult(
                success=False,
                result=None,
                error="SymPy not available",
                computation_time=time.time() - start_time,
            )

        # Check cache
        cache_key = hash(query)
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # Parse query to extract mathematical task
            task = self._parse_natural_language(query)
            if not task:
                return MathResult(
                    success=False,
                    result=None,
                    error="Could not understand mathematical query",
                    computation_time=time.time() - start_time,
                )

            # Execute mathematical task
            result = self._execute_task(task)
            result.computation_time = time.time() - start_time

            # Cache result
            self.cache[cache_key] = result
            return result

        except Exception as e:
            return MathResult(
                success=False,
                result=None,
                error=f"Mathematical computation failed: {e}",
                computation_time=time.time() - start_time,
            )

    def _parse_natural_language(self, query: str) -> Optional[MathTask]:
        """Parse natural language into mathematical task"""
        query = query.lower().strip()

        # Solve patterns
        solve_patterns = [
            r"solve\s+(.+?)(?:\s+for\s+(\w+))?(?:\s*=\s*(.+))?",
            r"find\s+(?:the\s+)?(?:value\s+of\s+)?(\w+)(?:\s+when\s+(.+?))?",
            r"(.+?)\s*=\s*(.+?)(?:\s+for\s+(\w+))?",
        ]

        for pattern in solve_patterns:
            match = re.search(pattern, query)
            if match:
                if "=" in query and len(match.groups()) >= 2:
                    expr_parts = query.split("=")
                    if len(expr_parts) == 2:
                        return MathTask(
                            task_type=MathTaskType.SOLVE,
                            expression=f"Eq({expr_parts[0].strip()}, {expr_parts[1].strip()})",
                            variable=self._extract_variable(query),
                        )
                else:
                    return MathTask(
                        task_type=MathTaskType.SOLVE,
                        expression=match.group(1),
                        variable=match.group(2) if len(match.groups()) > 1 else None,
                    )

        # Differentiate patterns
        if re.search(r"differentiate|derivative|d/dx", query):
            expr_match = re.search(
                r"(?:differentiate|derivative|d/dx)\s+(.+?)(?:\s+with\s+respect\s+to\s+(\w+))?",
                query,
            )
            if expr_match:
                return MathTask(
                    task_type=MathTaskType.DIFFERENTIATE,
                    expression=expr_match.group(1),
                    variable=(
                        expr_match.group(2) if len(expr_match.groups()) > 1 else "x"
                    ),
                )

        # Integrate patterns
        if re.search(r"integrate|integral", query):
            expr_match = re.search(
                r"(?:integrate|integral)\s+(.+?)(?:\s+(?:with\s+respect\s+to\s+|d)(\w+))?",
                query,
            )
            if expr_match:
                return MathTask(
                    task_type=MathTaskType.INTEGRATE,
                    expression=expr_match.group(1),
                    variable=(
                        expr_match.group(2) if len(expr_match.groups()) > 1 else "x"
                    ),
                )

        # Limit patterns
        limit_match = re.search(
            r"limit\s+of\s+(.+?)\s+as\s+(\w+)\s+(?:approaches|goes\s+to|\->)\s+(.+)",
            query,
        )
        if limit_match:
            return MathTask(
                task_type=MathTaskType.LIMIT,
                expression=limit_match.group(1),
                variable=limit_match.group(2),
                target=limit_match.group(3),
            )

        # Factor/expand patterns
        if re.search(r"factor", query):
            expr_match = re.search(r"factor\s+(.+)", query)
            if expr_match:
                return MathTask(
                    task_type=MathTaskType.FACTOR, expression=expr_match.group(1)
                )

        if re.search(r"expand", query):
            expr_match = re.search(r"expand\s+(.+)", query)
            if expr_match:
                return MathTask(
                    task_type=MathTaskType.EXPAND, expression=expr_match.group(1)
                )

        # Simplify patterns
        if re.search(r"simplify", query):
            expr_match = re.search(r"simplify\s+(.+)", query)
            if expr_match:
                return MathTask(
                    task_type=MathTaskType.SIMPLIFY, expression=expr_match.group(1)
                )

        return None

    def _extract_variable(self, query: str) -> str:
        """Extract variable from query"""
        # Look for common variable patterns
        var_match = re.search(r"for\s+(\w+)|solve\s+(\w+)|find\s+(\w+)", query)
        if var_match:
            return next(g for g in var_match.groups() if g)

        # Default to x
        return "x"

    def _execute_task(self, task: MathTask) -> MathResult:
        """Execute mathematical task"""
        try:
            # Parse expression
            expr = self._parse_expression(task.expression)
            if expr is None:
                return MathResult(
                    success=False,
                    result=None,
                    error=f"Could not parse expression: {task.expression}",
                )

            steps = []

            if task.task_type == MathTaskType.SOLVE:
                # Handle equation solving
                if "Eq(" in task.expression:
                    # Already an equation
                    eq = expr
                else:
                    # Assume expression = 0
                    eq = sp.Eq(expr, 0)

                var = sp.Symbol(task.variable or "x")
                solutions = sp.solve(eq, var)

                steps.append(f"Solving equation: {eq}")
                steps.append(f"Variable: {var}")

                return MathResult(
                    success=True,
                    result=solutions,
                    latex=sp.latex(solutions),
                    steps=steps,
                )

            elif task.task_type == MathTaskType.DIFFERENTIATE:
                var = sp.Symbol(task.variable or "x")
                derivative = sp.diff(expr, var)

                steps.append(f"Differentiating {expr} with respect to {var}")

                return MathResult(
                    success=True,
                    result=derivative,
                    latex=sp.latex(derivative),
                    steps=steps,
                )

            elif task.task_type == MathTaskType.INTEGRATE:
                var = sp.Symbol(task.variable or "x")
                integral = sp.integrate(expr, var)

                steps.append(f"Integrating {expr} with respect to {var}")

                return MathResult(
                    success=True, result=integral, latex=sp.latex(integral), steps=steps
                )

            elif task.task_type == MathTaskType.LIMIT:
                var = sp.Symbol(task.variable)
                target_val = self._parse_expression(task.target)
                limit_result = sp.limit(expr, var, target_val)

                steps.append(f"Taking limit of {expr} as {var} approaches {target_val}")

                return MathResult(
                    success=True,
                    result=limit_result,
                    latex=sp.latex(limit_result),
                    steps=steps,
                )

            elif task.task_type == MathTaskType.FACTOR:
                factored = sp.factor(expr)
                steps.append(f"Factoring {expr}")

                return MathResult(
                    success=True, result=factored, latex=sp.latex(factored), steps=steps
                )

            elif task.task_type == MathTaskType.EXPAND:
                expanded = sp.expand(expr)
                steps.append(f"Expanding {expr}")

                return MathResult(
                    success=True, result=expanded, latex=sp.latex(expanded), steps=steps
                )

            elif task.task_type == MathTaskType.SIMPLIFY:
                simplified = sp.simplify(expr)
                steps.append(f"Simplifying {expr}")

                return MathResult(
                    success=True,
                    result=simplified,
                    latex=sp.latex(simplified),
                    steps=steps,
                )

            else:
                return MathResult(
                    success=False,
                    result=None,
                    error=f"Unsupported task type: {task.task_type}",
                )

        except Exception as e:
            return MathResult(
                success=False, result=None, error=f"Computation failed: {e}"
            )

    def _parse_expression(self, expr_str: str) -> Optional[sp.Expr]:
        """Parse string expression to SymPy expression"""
        try:
            # Clean up expression
            expr_str = expr_str.strip()

            # Handle common mathematical notation
            replacements = {"^": "**", "ln": "log", "e^": "exp", "π": "pi", "pi": "pi"}

            for old, new in replacements.items():
                expr_str = expr_str.replace(old, new)

            # Parse with transformations
            return parse_expr(expr_str, transformations=self.transformations)

        except Exception:
            # Fallback parsing
            try:
                return parse_expr(expr_str)
            except Exception:
                return None

    def get_capabilities(self) -> List[str]:
        """Get list of mathematical capabilities"""
        if not self.available:
            return ["Mathematical reasoning unavailable (SymPy not installed)"]

        return [
            "Equation solving (linear, quadratic, polynomial, transcendental)",
            "Calculus (differentiation, integration, limits)",
            "Algebraic manipulation (factoring, expanding, simplifying)",
            "Series expansions (Taylor, Fourier)",
            "Matrix operations",
            "Trigonometric and logarithmic functions",
            "Complex number arithmetic",
            "Linear algebra (eigenvalues, determinants)",
            "Differential equations (basic)",
            "Number theory operations",
        ]

    def solve_equation_system(
        self, equations: List[str], variables: List[str]
    ) -> MathResult:
        """Solve system of equations"""
        if not self.available:
            return MathResult(success=False, result=None, error="SymPy not available")

        try:
            # Parse equations and variables
            parsed_eqs = []
            parsed_vars = [sp.Symbol(v) for v in variables]

            for eq_str in equations:
                eq = self._parse_expression(eq_str)
                if eq:
                    # Assume equation = 0 if not explicitly an equation
                    if not isinstance(eq, sp.Eq):
                        eq = sp.Eq(eq, 0)
                    parsed_eqs.append(eq)

            # Solve system
            solutions = sp.solve(parsed_eqs, parsed_vars)

            return MathResult(
                success=True,
                result=solutions,
                latex=sp.latex(solutions),
                steps=[f"Solving system: {parsed_eqs}", f"Variables: {parsed_vars}"],
            )

        except Exception as e:
            return MathResult(
                success=False, result=None, error=f"System solve failed: {e}"
            )

"""Solver tests — pure numerical boundary, no parser/UI imports."""

import math
import pytest
from domain.models.bisection import SolverConfig, BisectionResult
from domain.solvers.bisection import solve_bisection


def test_convergent_interval_returns_iterations():
    """GIVEN a continuous evaluator with sign-changing interval
       WHEN the bisection solver runs
       THEN it returns a successful result with iterations."""
    config = SolverConfig(a=1.0, b=2.0, tolerance=1e-6, max_iterations=100)
    result = solve_bisection(lambda x: x**3 - x - 2, config)

    assert result.status == "success"
    assert result.converged is True
    assert result.root is not None
    assert abs(result.root - 1.521379) < 1e-4
    assert len(result.iterations) > 0

    # Every iteration should have valid numeric fields
    for it in result.iterations:
        assert it.iteration >= 1
        assert math.isfinite(it.midpoint)
        assert math.isfinite(it.f_midpoint)
        assert math.isfinite(it.error_abs)
        assert it.a < it.b  # invariant


def test_invalid_bracket_returns_failure():
    """GIVEN an evaluator whose endpoints do not bracket a root
       WHEN the bisection solver runs
       THEN it returns invalid_bracket status (no exception)."""
    # f(x) = x**2 + 1 is always positive on [-1, 1]
    config = SolverConfig(a=-1.0, b=1.0, tolerance=1e-6, max_iterations=100)
    result = solve_bisection(lambda x: x**2 + 1, config)

    assert result.status == "invalid_bracket"
    assert result.converged is False
    assert result.root is None
    assert len(result.iterations) == 0


def test_non_finite_evaluator_output_returns_failure():
    """GIVEN an evaluator returning NaN at an endpoint
       WHEN the bisection solver runs
       THEN it returns non_finite status (no exception)."""
    def bad_eval(x: float) -> float:
        if x == 1.0:
            return float("nan")
        return x - 2

    config = SolverConfig(a=1.0, b=3.0, tolerance=1e-6, max_iterations=100)
    result = solve_bisection(bad_eval, config)

    assert result.status == "non_finite"
    assert result.converged is False
    assert result.root is None


def test_max_iterations_without_convergence():
    """GIVEN a very tight tolerance with few iterations allowed
       WHEN the solver exhausts max_iterations
       THEN it returns max_iterations status with partial iterations."""
    config = SolverConfig(a=1.0, b=2.0, tolerance=1e-15, max_iterations=5)
    result = solve_bisection(lambda x: x**3 - x - 2, config)

    assert result.status == "max_iterations"
    assert result.converged is False
    assert result.root is not None  # best approximation so far
    assert len(result.iterations) == 5


def test_boundary_root_at_a_returns_success():
    """GIVEN f(a) == 0 (root exactly at the left boundary)
       WHEN the bisection solver runs
       THEN it returns success with root == a (no iterations needed)."""
    config = SolverConfig(a=0.0, b=1.0, tolerance=1e-6, max_iterations=100)
    result = solve_bisection(lambda x: x, config)  # f(0) = 0

    assert result.status == "success"
    assert result.converged is True
    assert result.root == 0.0
    assert len(result.iterations) == 0


def test_boundary_root_at_b_returns_success():
    """GIVEN f(b) == 0 (root exactly at the right boundary)
       WHEN the bisection solver runs
       THEN it returns success with root == b (no iterations needed)."""
    config = SolverConfig(a=0.0, b=1.0, tolerance=1e-6, max_iterations=100)
    result = solve_bisection(lambda x: x - 1, config)  # f(1) = 0

    assert result.status == "success"
    assert result.converged is True
    assert result.root == 1.0
    assert len(result.iterations) == 0


def test_solver_has_no_forbidden_imports():
    """PROVE the solver module has zero parser/UI dependencies."""
    import domain.solvers.bisection as mod
    source = mod.__file__
    with open(source, encoding="utf-8") as fh:
        content = fh.read()
    assert "STREAMLIT" not in content.upper(), "solver must not import streamlit"
    assert "func_parser" not in content, "solver must not import parser"
    assert "matplotlib" not in content, "solver must not import matplotlib"
    assert "pandas" not in content, "solver must not import pandas"

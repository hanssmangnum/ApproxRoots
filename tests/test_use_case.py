"""Use-case tests — fake parser/solver collaborators verify orchestration."""

import pytest
from domain.models.bisection import (
    BisectionRequest,
    SolverConfig,
    BisectionResult,
    BisectionIteration,
)
from application.use_cases.run_bisection import run_bisection


def _make_compile_fn(_expr: str):
    """Fake compile — ignores expression, returns a hard-coded evaluator."""
    return lambda x: x**3 - x - 2


def _success_solver(evaluator, config):
    """Fake solver returning a hard-coded success."""
    return BisectionResult(
        iterations=[
            BisectionIteration(1, 1.0, 2.0, 1.5, -0.875, 0.5, float("inf")),
            BisectionIteration(2, 1.5, 2.0, 1.75, 1.609, 0.25, 0.142857),
        ],
        root=1.75,
        converged=True,
        status="success",
    )


def _failing_compile_fn(_expr: str):
    raise ValueError("Syntax error at line 1")


class TestRunBisection:
    """Orchestration boundary — parse before solve, failures skip solver."""

    def test_successful_run_calls_parse_then_solve(self):
        """GIVEN a valid request and successful fakes
           WHEN run_bisection executes
           THEN it returns the solver result."""
        request = BisectionRequest("x**3 - x - 2", 1.0, 2.0, 1e-6, 100)
        result = run_bisection(request, compile_fn=_make_compile_fn, solve_fn=_success_solver)

        assert result.status == "success"
        assert result.converged is True
        assert result.root == 1.75
        assert len(result.iterations) == 2

    def test_parser_failure_skips_solver(self):
        """GIVEN a request with an invalid expression
           WHEN run_bisection executes
           THEN parse_error is returned and solver is NOT called."""
        solver_called = False

        def _never_called(_evaluator, _config):
            nonlocal solver_called
            solver_called = True
            return _success_solver(_evaluator, _config)

        request = BisectionRequest("invalid!!!", 1.0, 2.0, 1e-6, 100)
        result = run_bisection(request, compile_fn=_failing_compile_fn, solve_fn=_never_called)

        assert result.status == "parse_error"
        assert result.converged is False
        assert result.root is None
        assert solver_called is False, "Solver was called despite parse failure"

    def test_parse_before_solve_ordering(self):
        """PROVE that the use case always parses before passing to solver."""
        parse_order = []
        solve_order = []

        def _track_parse(expr: str):
            parse_order.append("parse")
            return _make_compile_fn(expr)

        def _track_solve(eval_fn, config):
            solve_order.append("solve")
            return _success_solver(eval_fn, config)

        request = BisectionRequest("x**2", 0.0, 1.0, 1e-6, 50)
        run_bisection(request, compile_fn=_track_parse, solve_fn=_track_solve)

        assert parse_order == ["parse"]
        assert solve_order == ["solve"]

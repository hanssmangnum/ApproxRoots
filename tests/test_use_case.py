"""Pruebas del caso de uso — parches mock verifican la orquestación sin callable injection."""

from unittest.mock import Mock, patch

import pytest
from domain.models.bisection import (
    BisectionRequest,
    SolverConfig,
    BisectionResult,
    BisectionIteration,
)
from domain.models.newton import (
    NewtonRequest,
    NewtonConfig,
    NewtonResult,
    NewtonIteration,
)
from domain.models.comparison import (
    ComparisonRequest,
    ComparisonResult,
)
from application.use_cases.run_bisection import run_bisection
from application.use_cases.run_newton import run_newton
from application.use_cases.run_comparison import run_comparison
from application.services.parser_service import ParserService
from application.services.bisection_solver import BisectionSolver
from application.services.newton_solver import NewtonSolver


def _compile_fn(_expr: str):
    return lambda x: x**3 - x - 2


def _newton_compile_fn(_expr: str):
    return lambda x: x**2 - 4


def _derive_fn(_expr: str):
    return lambda x: 2.0


def _newton_derive_fn(_expr: str):
    return lambda x: 2 * x


def _success_solver(evaluator, config):
    return BisectionResult(
        iterations=[
            BisectionIteration(1, 1.0, 2.0, 1.5, -0.875, 0.5, float("inf")),
            BisectionIteration(2, 1.5, 2.0, 1.75, 1.609, 0.25, 0.142857),
        ],
        root=1.75,
        converged=True,
        status="success",
    )


def _newton_success_solver(f, df, config):
    return NewtonResult(
        iterations=[
            NewtonIteration(1, 3.0, 1.8333, 5.0, 6.0, 1.1667, 0.6364, 6.0, -13.0),
            NewtonIteration(2, 1.8333, 2.0069, -0.6392, 3.6667, 0.1736, 0.0865, 3.6667, -7.3583),
        ],
        root=2.0069,
        converged=True,
        status="success",
    )


_REAL_PARSE_ERROR = ValueError("Syntax error at line 1")
_REAL_DERIVE_ERROR = ValueError("Derivative error")


class TestRunBisection:
    """Frontera de orquestación — parse antes de solve, los fallos evitan al solver."""

    def test_successful_run_calls_parse_then_solve(self):
        request = BisectionRequest("x**3 - x - 2", 1.0, 2.0, 1e-6, 100)
        with patch.object(ParserService, "compile_expression", return_value=lambda x: 1.0):
            with patch.object(BisectionSolver, "solve", side_effect=_success_solver):
                result = run_bisection(request, ParserService(), BisectionSolver())

        assert result.status == "success"
        assert result.converged is True
        assert result.root == 1.75
        assert len(result.iterations) == 2

    def test_parser_failure_skips_solver(self):
        request = BisectionRequest("invalid!!!", 1.0, 2.0, 1e-6, 100)
        with patch.object(ParserService, "compile_expression", side_effect=_REAL_PARSE_ERROR):
            with patch.object(BisectionSolver, "solve") as mock_solve:
                result = run_bisection(request, ParserService(), BisectionSolver())

        assert result.status == "parse_error"
        assert result.converged is False
        assert result.root is None
        mock_solve.assert_not_called()

    def test_parse_before_solve_ordering(self):
        mock_parse = Mock(return_value=lambda x: x**2)
        mock_solve = Mock(return_value=_success_solver(None, None))

        request = BisectionRequest("x**2", 0.0, 1.0, 1e-6, 50)
        with patch.object(ParserService, "compile_expression", mock_parse):
            with patch.object(BisectionSolver, "solve", mock_solve):
                run_bisection(request, ParserService(), BisectionSolver())

        mock_parse.assert_called_once()
        mock_solve.assert_called_once()


# ═════════════════════════════════════════════════════════════════════════════
# Newton use-case tests
# ═════════════════════════════════════════════════════════════════════════════


class TestRunNewton:
    """Frontera de orquestación — compilar f, compilar df, luego resolver."""

    def test_successful_run_calls_parse_then_solve(self):
        request = NewtonRequest("x**2 - 4", 3.0, 1e-6, 100)
        with patch.object(ParserService, "compile_expression", return_value=_newton_compile_fn("")):
            with patch.object(ParserService, "compile_derivative", return_value=_newton_derive_fn("")):
                with patch.object(NewtonSolver, "solve", side_effect=_newton_success_solver):
                    result = run_newton(request, ParserService(), NewtonSolver())

        assert result.status == "success"
        assert result.converged is True
        assert abs(result.root - 2.0069) < 1e-4
        assert len(result.iterations) == 2

    def test_compile_failure_skips_solver(self):
        request = NewtonRequest("invalid!!!", 3.0, 1e-6, 100)
        with patch.object(ParserService, "compile_expression", side_effect=_REAL_PARSE_ERROR):
            with patch.object(NewtonSolver, "solve") as mock_solve:
                result = run_newton(request, ParserService(), NewtonSolver())

        assert result.status == "parse_error"
        assert result.converged is False
        assert result.root is None
        mock_solve.assert_not_called()

    def test_derive_failure_skips_solver(self):
        request = NewtonRequest("x**2 - 4", 3.0, 1e-6, 100)
        with patch.object(ParserService, "compile_expression", return_value=_newton_compile_fn("")):
            with patch.object(ParserService, "compile_derivative", side_effect=_REAL_DERIVE_ERROR):
                with patch.object(NewtonSolver, "solve") as mock_solve:
                    result = run_newton(request, ParserService(), NewtonSolver())

        assert result.status == "parse_error"
        assert result.converged is False
        assert result.root is None
        mock_solve.assert_not_called()

    def test_parse_f_before_parse_df_before_solve(self):
        calls = []

        def _track_compile(expr):
            calls.append("compile_f")
            return _newton_compile_fn(expr)

        def _track_derivative(expr):
            calls.append("compile_df")
            return _newton_derive_fn(expr)

        def _track_solve(f, df, config):
            calls.append("solve")
            return _newton_success_solver(f, df, config)

        request = NewtonRequest("x**2 - 4", 3.0, 1e-6, 50)
        with patch.object(ParserService, "compile_expression", side_effect=_track_compile):
            with patch.object(ParserService, "compile_derivative", side_effect=_track_derivative):
                with patch.object(NewtonSolver, "solve", side_effect=_track_solve):
                    run_newton(request, ParserService(), NewtonSolver())

        assert calls == ["compile_f", "compile_df", "solve"]


# ═════════════════════════════════════════════════════════════════════════════
# Comparison use-case tests
# ═════════════════════════════════════════════════════════════════════════════


def _bisection_success_uc(request, parser, solver):
    return BisectionResult(
        iterations=[
            BisectionIteration(1, 1.0, 2.0, 1.5, -0.875, 0.5, float("inf")),
            BisectionIteration(2, 1.5, 2.0, 1.75, 1.609, 0.25, 0.142857),
        ],
        root=1.75,
        converged=True,
        status="success",
    )


def _newton_success_uc(request, parser, solver):
    return NewtonResult(
        iterations=[
            NewtonIteration(1, 3.0, 1.8333, 5.0, 6.0, 1.1667, 0.6364, 6.0, -13.0),
            NewtonIteration(2, 1.8333, 2.0069, -0.6392, 3.6667, 0.1736, 0.0865, 3.6667, -7.3583),
        ],
        root=2.0069,
        converged=True,
        status="success",
    )


def _bisection_failing_uc(request, parser, solver):
    return BisectionResult(
        iterations=[],
        root=None,
        converged=False,
        status="invalid_bracket",
        error_message="No sign change in interval",
    )


def _newton_failing_uc(request, parser, solver):
    return NewtonResult(
        iterations=[],
        root=None,
        converged=False,
        status="derivative_zero",
        error_message="Derivative is zero",
    )


class TestRunComparison:
    """Orquestación de comparación — ejecuta ambos métodos, envuelve los resultados."""

    # Parser + service helpers usados por todos los tests de comparación
    _PARSER = ParserService()
    _BIS_SOLVER = BisectionSolver()
    _NWT_SOLVER = NewtonSolver()

    @classmethod
    def _run_with_fakes(cls, request, bis_fn, nwt_fn):
        """Ejecuta run_comparison con las funciones de caso deuso parcheadas."""
        patchers = [
            patch("application.use_cases.run_comparison.run_bisection", side_effect=bis_fn),
            patch("application.use_cases.run_comparison.run_newton", side_effect=nwt_fn),
        ]
        for p in patchers:
            p.start()
        try:
            return run_comparison(request, cls._PARSER, cls._BIS_SOLVER, cls._NWT_SOLVER)
        finally:
            for p in patchers:
                p.stop()

    def test_both_methods_succeed(self):
        request = ComparisonRequest(
            expression="x**2 - 4",
            bisection_a=1.0, bisection_b=3.0,
            newton_x0=3.0,
            tolerance=1e-6, max_iterations=100,
        )
        result = self._run_with_fakes(request, _bisection_success_uc, _newton_success_uc)

        assert result.status == "success"
        assert result.bisection.converged is True
        assert result.bisection.root == 1.75
        assert result.newton.converged is True
        assert abs(result.newton.root - 2.0069) < 1e-4

    def test_one_method_fails(self):
        request = ComparisonRequest(
            expression="x**2 - 4",
            bisection_a=1.0, bisection_b=3.0,
            newton_x0=3.0,
            tolerance=1e-6, max_iterations=100,
        )
        result = self._run_with_fakes(request, _bisection_failing_uc, _newton_success_uc)

        assert result.bisection.converged is False
        assert result.bisection.root is None
        assert result.bisection.error_message == "No sign change in interval"
        assert result.newton.converged is True
        assert abs(result.newton.root - 2.0069) < 1e-4

    def test_both_methods_fail(self):
        request = ComparisonRequest(
            expression="x**2 - 4",
            bisection_a=1.0, bisection_b=3.0,
            newton_x0=3.0,
            tolerance=1e-6, max_iterations=100,
        )
        result = self._run_with_fakes(request, _bisection_failing_uc, _newton_failing_uc)

        assert result.bisection.converged is False
        assert result.newton.converged is False
        assert result.bisection.error_message == "No sign change in interval"
        assert result.newton.error_message == "Derivative is zero"

    def test_parse_error_both_methods(self):
        """Sin parche — usa la función real; el parser falla en compile_expression."""
        request = ComparisonRequest(
            expression="invalid!!!",
            bisection_a=1.0, bisection_b=3.0,
            newton_x0=3.0,
            tolerance=1e-6, max_iterations=100,
        )
        with patch.object(ParserService, "compile_expression", side_effect=_REAL_PARSE_ERROR):
            result = run_comparison(request, ParserService(), BisectionSolver(), NewtonSolver())

        assert result.status == "parse_error"
        assert result.bisection.converged is False
        assert result.bisection.root is None
        assert "Syntax error" in (result.bisection.error_message or "")
        assert result.newton.converged is False
        assert result.newton.root is None
        assert "Syntax error" in (result.newton.error_message or "")

    def test_method_summary_fields(self):
        request = ComparisonRequest(
            expression="x**2 - 4",
            bisection_a=1.0, bisection_b=3.0,
            newton_x0=3.0,
            tolerance=1e-6, max_iterations=100,
        )
        result = self._run_with_fakes(request, _bisection_success_uc, _newton_success_uc)

        for summary in (result.bisection, result.newton):
            assert summary.method_name in ("Bisección", "Newton-Raphson")
            assert isinstance(summary.converged, bool)
            assert isinstance(summary.iterations_count, int)
            assert summary.root is not None or not summary.converged

    def test_bisection_succeeds_newton_fails_summary(self):
        request = ComparisonRequest(
            expression="x**2 - 4",
            bisection_a=1.0, bisection_b=3.0,
            newton_x0=3.0,
            tolerance=1e-6, max_iterations=100,
        )
        result = self._run_with_fakes(request, _bisection_success_uc, _newton_failing_uc)

        assert result.bisection.converged is True
        assert result.bisection.root == 1.75
        assert result.bisection.error_message is None
        assert result.bisection.iterations_count == 2

        assert result.newton.converged is False
        assert result.newton.root is None
        assert result.newton.error_message == "Derivative is zero"
        assert result.newton.iterations_count == 0

    def test_newton_succeeds_bisection_fails_summary(self):
        request = ComparisonRequest(
            expression="x**2 - 4",
            bisection_a=1.0, bisection_b=3.0,
            newton_x0=3.0,
            tolerance=1e-6, max_iterations=100,
        )
        result = self._run_with_fakes(request, _bisection_failing_uc, _newton_success_uc)

        assert result.bisection.converged is False
        assert result.bisection.root is None
        assert result.bisection.error_message == "No sign change in interval"
        assert result.bisection.iterations_count == 0

        assert result.newton.converged is True
        assert result.newton.root is not None
        assert result.newton.error_message is None
        assert result.newton.iterations_count == 2

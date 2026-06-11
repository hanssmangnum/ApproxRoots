"""Pruebas del caso de uso — colaboradores fake (parser/solver) verifican la orquestación."""

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
from application.use_cases.run_bisection import run_bisection
from application.use_cases.run_newton import run_newton


def _make_compile_fn(_expr: str):
    """Fake compile — ignora la expresión, retorna un evaluador fijo."""
    return lambda x: x**3 - x - 2


def _success_solver(evaluator, config):
    """Fake solver que retorna un éxito fijo."""
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
    """Frontera de orquestación — parse antes de solve, los fallos evitan al solver."""

    def test_successful_run_calls_parse_then_solve(self):
        """DADO una solicitud válida y fakes exitosos
           CUANDO run_bisection se ejecuta
           ENTONCES retorna el resultado del solver."""
        request = BisectionRequest("x**3 - x - 2", 1.0, 2.0, 1e-6, 100)
        result = run_bisection(request, compile_fn=_make_compile_fn, solve_fn=_success_solver)

        assert result.status == "success"
        assert result.converged is True
        assert result.root == 1.75
        assert len(result.iterations) == 2

    def test_parser_failure_skips_solver(self):
        """DADO una solicitud con una expresión inválida
           CUANDO run_bisection se ejecuta
           ENTONCES se retorna parse_error y el solver NO es llamado."""
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
        assert solver_called is False, "El solver fue llamado a pesar del fallo de parseo"

    def test_parse_before_solve_ordering(self):
        """PRUEBA que el caso de uso siempre parsea antes de pasar al solver."""
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


# ═════════════════════════════════════════════════════════════════════════════
# Newton use-case tests
# ═════════════════════════════════════════════════════════════════════════════


def _make_newton_compile_fn(_expr: str):
    """Fake compile — ignora la expresión, retorna un evaluador fijo."""
    return lambda x: x**2 - 4


def _make_newton_derive_fn(_expr: str):
    """Fake derive — ignora la expresión, retorna una derivada fija."""
    return lambda x: 2 * x


def _newton_success_solver(f, df, config):
    """Fake solver que retorna un éxito fijo."""
    return NewtonResult(
        iterations=[
            NewtonIteration(1, 3.0, 1.8333, 5.0, 6.0, 1.1667, 0.6364, 6.0, -13.0),
            NewtonIteration(2, 1.8333, 2.0069, -0.6392, 3.6667, 0.1736, 0.0865, 3.6667, -7.3583),
        ],
        root=2.0069,
        converged=True,
        status="success",
    )


def _failing_newton_compile_fn(_expr: str):
    raise ValueError("Syntax error at line 1")


def _failing_newton_derive_fn(_expr: str):
    raise ValueError("Derivative error")


class TestRunNewton:
    """Frontera de orquestación — compilar f, compilar df, luego resolver."""

    def test_successful_run_calls_parse_then_solve(self):
        """DADO una solicitud válida y fakes exitosos
           CUANDO run_newton se ejecuta
           ENTONCES retorna el resultado del solver."""
        request = NewtonRequest("x**2 - 4", 3.0, 1e-6, 100)
        result = run_newton(
            request,
            compile_fn=_make_newton_compile_fn,
            derive_fn=_make_newton_derive_fn,
            solve_fn=_newton_success_solver,
        )

        assert result.status == "success"
        assert result.converged is True
        assert abs(result.root - 2.0069) < 1e-4
        assert len(result.iterations) == 2

    def test_compile_failure_skips_solver(self):
        """DADO una solicitud con una expresión inválida para f
           CUANDO run_newton se ejecuta
           ENTONCES se retorna parse_error y el solver NO es llamado."""
        solver_called = False

        def _never_called(_f, _df, _config):
            nonlocal solver_called
            solver_called = True
            return _newton_success_solver(_f, _df, _config)

        request = NewtonRequest("invalid!!!", 3.0, 1e-6, 100)
        result = run_newton(
            request,
            compile_fn=_failing_newton_compile_fn,
            derive_fn=_make_newton_derive_fn,
            solve_fn=_never_called,
        )

        assert result.status == "parse_error"
        assert result.converged is False
        assert result.root is None
        assert solver_called is False, "El solver fue llamado a pesar del fallo de compilación"

    def test_derive_failure_skips_solver(self):
        """DADO una solicitud donde la compilación de la derivada falla
           CUANDO run_newton se ejecuta
           ENTONCES se retorna parse_error y el solver NO es llamado."""
        solver_called = False

        def _never_called(_f, _df, _config):
            nonlocal solver_called
            solver_called = True
            return _newton_success_solver(_f, _df, _config)

        request = NewtonRequest("x**2 - 4", 3.0, 1e-6, 100)
        result = run_newton(
            request,
            compile_fn=_make_newton_compile_fn,
            derive_fn=_failing_newton_derive_fn,
            solve_fn=_never_called,
        )

        assert result.status == "parse_error"
        assert result.converged is False
        assert result.root is None
        assert solver_called is False, "El solver fue llamado a pesar del fallo de derivación"

    def test_parse_f_before_parse_df_before_solve(self):
        """PRUEBA que el caso de uso compila f, luego df, luego pasa al solver."""
        order = []

        def _track_parse(expr: str):
            order.append("compile_f")
            return _make_newton_compile_fn(expr)

        def _track_derive(expr: str):
            order.append("compile_df")
            return _make_newton_derive_fn(expr)

        def _track_solve(f, df, config):
            order.append("solve")
            return _newton_success_solver(f, df, config)

        request = NewtonRequest("x**2 - 4", 3.0, 1e-6, 50)
        run_newton(request, compile_fn=_track_parse, derive_fn=_track_derive, solve_fn=_track_solve)

        assert order == ["compile_f", "compile_df", "solve"]


# ═════════════════════════════════════════════════════════════════════════════
# Comparison use-case tests
# ═════════════════════════════════════════════════════════════════════════════

from domain.models.comparison import (  # noqa: E402
    ComparisonRequest,
    ComparisonResult,
)
from application.use_cases.run_comparison import run_comparison  # noqa: E402


def _bisection_success_use_case(request, compile_fn, solve_fn):
    """Fake caso de uso de bisección que retorna un resultado exitoso."""
    return BisectionResult(
        iterations=[
            BisectionIteration(1, 1.0, 2.0, 1.5, -0.875, 0.5, float("inf")),
            BisectionIteration(2, 1.5, 2.0, 1.75, 1.609, 0.25, 0.142857),
        ],
        root=1.75,
        converged=True,
        status="success",
    )


def _newton_success_use_case(request, compile_fn, derive_fn, solve_fn):
    """Fake caso de uso de Newton que retorna un resultado exitoso."""
    return NewtonResult(
        iterations=[
            NewtonIteration(1, 3.0, 1.8333, 5.0, 6.0, 1.1667, 0.6364, 6.0, -13.0),
            NewtonIteration(2, 1.8333, 2.0069, -0.6392, 3.6667, 0.1736, 0.0865, 3.6667, -7.3583),
        ],
        root=2.0069,
        converged=True,
        status="success",
    )


def _bisection_failing_use_case(request, compile_fn, solve_fn):
    """Fake caso de uso de bisección que retorna un fallo invalid_bracket."""
    return BisectionResult(
        iterations=[],
        root=None,
        converged=False,
        status="invalid_bracket",
        error_message="No sign change in interval",
    )


def _newton_failing_use_case(request, compile_fn, derive_fn, solve_fn):
    """Fake caso de uso de Newton que retorna un fallo derivative_zero."""
    return NewtonResult(
        iterations=[],
        root=None,
        converged=False,
        status="derivative_zero",
        error_message="Derivative is zero",
    )


class TestRunComparison:
    """Orquestación de comparación — ejecuta ambos métodos, envuelve los resultados."""

    def test_both_methods_succeed(self):
        """DADO configuración válida y ambos métodos exitosos
           CUANDO run_comparison se ejecuta
           ENTONCES ambos registros MethodSummary muestran éxito."""
        request = ComparisonRequest(
            expression="x**2 - 4",
            bisection_a=1.0, bisection_b=3.0,
            newton_x0=3.0,
            tolerance=1e-6, max_iterations=100,
        )
        result = run_comparison(
            request,
            compile_fn=_make_compile_fn,
            derive_fn=_make_newton_compile_fn,
            run_bisection_fn=_bisection_success_use_case,
            run_newton_fn=_newton_success_use_case,
            bisection_solve_fn=lambda ev, cfg: _bisection_success_use_case(None, None, None),
            newton_solve_fn=lambda f, df, cfg: _newton_success_use_case(None, None, None, None),
        )

        assert result.status == "success"
        assert result.bisection.converged is True
        assert result.bisection.root == 1.75
        assert result.newton.converged is True
        assert abs(result.newton.root - 2.0069) < 1e-4

    def test_one_method_fails(self):
        """DADO un método que falla y el otro que tiene éxito
           CUANDO run_comparison se ejecuta
           ENTONCES el método que falla tiene info de error y el exitoso se conserva."""
        request = ComparisonRequest(
            expression="x**2 - 4",
            bisection_a=1.0, bisection_b=3.0,
            newton_x0=3.0,
            tolerance=1e-6, max_iterations=100,
        )
        result = run_comparison(
            request,
            compile_fn=_make_compile_fn,
            derive_fn=_make_newton_compile_fn,
            run_bisection_fn=_bisection_failing_use_case,
            run_newton_fn=_newton_success_use_case,
            bisection_solve_fn=lambda ev, cfg: _bisection_failing_use_case(None, None, None),
            newton_solve_fn=lambda f, df, cfg: _newton_success_use_case(None, None, None, None),
        )

        # Bisection failed
        assert result.bisection.converged is False
        assert result.bisection.root is None
        assert result.bisection.error_message == "No sign change in interval"

        # Newton still succeeded
        assert result.newton.converged is True
        assert abs(result.newton.root - 2.0069) < 1e-4

    def test_both_methods_fail(self):
        """DADO ambos métodos fallando
           CUANDO run_comparison se ejecuta
           ENTONCES ambos registros muestran info de fallo."""
        request = ComparisonRequest(
            expression="x**2 - 4",
            bisection_a=1.0, bisection_b=3.0,
            newton_x0=3.0,
            tolerance=1e-6, max_iterations=100,
        )
        result = run_comparison(
            request,
            compile_fn=_make_compile_fn,
            derive_fn=_make_newton_compile_fn,
            run_bisection_fn=_bisection_failing_use_case,
            run_newton_fn=_newton_failing_use_case,
            bisection_solve_fn=lambda ev, cfg: _bisection_failing_use_case(None, None, None),
            newton_solve_fn=lambda f, df, cfg: _newton_failing_use_case(None, None, None, None),
        )

        assert result.bisection.converged is False
        assert result.newton.converged is False
        assert result.bisection.error_message == "No sign change in interval"
        assert result.newton.error_message == "Derivative is zero"

    def test_parse_error_both_methods(self):
        """DADO una expresión inválida
           CUANDO run_comparison se ejecuta con casos de uso reales
           ENTONCES ambos métodos muestran estado parse_error (el error de compilación se propaga)."""
        request = ComparisonRequest(
            expression="invalid!!!",
            bisection_a=1.0, bisection_b=3.0,
            newton_x0=3.0,
            tolerance=1e-6, max_iterations=100,
        )
        result = run_comparison(
            request,
            compile_fn=_failing_compile_fn,
            derive_fn=_failing_newton_compile_fn,
            run_bisection_fn=run_bisection,   # real use case — catches ValueError
            run_newton_fn=run_newton,          # real use case — catches ValueError
            bisection_solve_fn=lambda _ev, _cfg: None,  # never called
            newton_solve_fn=lambda _f, _df, _cfg: None,  # never called
        )

        assert result.status == "parse_error"
        assert result.bisection.converged is False
        assert result.bisection.root is None
        assert "Syntax error" in (result.bisection.error_message or "")
        assert result.newton.converged is False
        assert result.newton.root is None
        assert "Syntax error" in (result.newton.error_message or "")

    def test_method_summary_fields(self):
        """PRUEBA que MethodSummary contiene todos los campos requeridos."""
        request = ComparisonRequest(
            expression="x**2 - 4",
            bisection_a=1.0, bisection_b=3.0,
            newton_x0=3.0,
            tolerance=1e-6, max_iterations=100,
        )
        result = run_comparison(
            request,
            compile_fn=_make_compile_fn,
            derive_fn=_make_newton_compile_fn,
            run_bisection_fn=_bisection_success_use_case,
            run_newton_fn=_newton_success_use_case,
            bisection_solve_fn=lambda ev, cfg: _bisection_success_use_case(None, None, None),
            newton_solve_fn=lambda f, df, cfg: _newton_success_use_case(None, None, None, None),
        )

        for summary in (result.bisection, result.newton):
            assert summary.method_name in ("Bisección", "Newton-Raphson")
            assert isinstance(summary.converged, bool)
            assert isinstance(summary.iterations_count, int)
            # root, final_error, error_message son Optional[float] — pueden ser None
            assert summary.root is not None or not summary.converged

    def test_bisection_succeeds_newton_fails_summary(self):
        """DADO bisección exitosa y Newton fallando
           CUANDO run_comparison se ejecuta
           ENTONCES el resumen de Newton incluye error_message y bisección está completa."""
        request = ComparisonRequest(
            expression="x**2 - 4",
            bisection_a=1.0, bisection_b=3.0,
            newton_x0=3.0,
            tolerance=1e-6, max_iterations=100,
        )
        result = run_comparison(
            request,
            compile_fn=_make_compile_fn,
            derive_fn=_make_newton_compile_fn,
            run_bisection_fn=_bisection_success_use_case,
            run_newton_fn=_newton_failing_use_case,
            bisection_solve_fn=lambda ev, cfg: _bisection_success_use_case(None, None, None),
            newton_solve_fn=lambda f, df, cfg: _newton_failing_use_case(None, None, None, None),
        )

        # Bisection successful
        assert result.bisection.converged is True
        assert result.bisection.root == 1.75
        assert result.bisection.error_message is None
        assert result.bisection.iterations_count == 2

        # Newton failed
        assert result.newton.converged is False
        assert result.newton.root is None
        assert result.newton.error_message == "Derivative is zero"
        assert result.newton.iterations_count == 0

    def test_newton_succeeds_bisection_fails_summary(self):
        """DADO Newton exitoso y bisección fallando
           CUANDO run_comparison se ejecuta
           ENTONCES el resumen de bisección incluye error_message y Newton está completo."""
        request = ComparisonRequest(
            expression="x**2 - 4",
            bisection_a=1.0, bisection_b=3.0,
            newton_x0=3.0,
            tolerance=1e-6, max_iterations=100,
        )
        result = run_comparison(
            request,
            compile_fn=_make_compile_fn,
            derive_fn=_make_newton_compile_fn,
            run_bisection_fn=_bisection_failing_use_case,
            run_newton_fn=_newton_success_use_case,
            bisection_solve_fn=lambda ev, cfg: _bisection_failing_use_case(None, None, None),
            newton_solve_fn=lambda f, df, cfg: _newton_success_use_case(None, None, None, None),
        )

        # Bisection failed
        assert result.bisection.converged is False
        assert result.bisection.root is None
        assert result.bisection.error_message == "No sign change in interval"
        assert result.bisection.iterations_count == 0

        # Newton successful
        assert result.newton.converged is True
        assert result.newton.root is not None
        assert result.newton.error_message is None
        assert result.newton.iterations_count == 2

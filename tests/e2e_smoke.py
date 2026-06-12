"""Prueba de humo de integración rápida de extremo a extremo para la arquitectura separada de la aplicación.

Se ejecuta bajo pytest (descubierta mediante el patrón e2e_*.py) o directamente::

    python tests/e2e_smoke.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from domain.models.bisection import BisectionRequest
from domain.solvers.bisection import solve_bisection
from application.use_cases.run_bisection import run_bisection
from ui.presenters.bisection_presenter import present_bisection_result
from application.services.parser_service import ParserService
from application.services.bisection_solver import BisectionSolver


def test_e2e_smoke() -> None:
    parser = ParserService()
    solver = BisectionSolver()
    request = BisectionRequest("x**3 - x - 2", 1.0, 2.0, 1e-6, 100)
    result = run_bisection(request, parser, solver)
    assert result.status == "success", f"Expected success, got {result.status}"
    assert result.converged is True
    assert abs(result.root - 1.521379) < 1e-4
    assert len(result.iterations) == 20

    data = present_bisection_result(result)
    assert data["session"]["raiz"] == result.root
    assert data["metrics"]["root"] == result.root
    assert len(data["iterations"]) == 20


# ═════════════════════════════════════════════════════════════════════════════
# Prueba de humo e2e de Newton-Raphson
# ═════════════════════════════════════════════════════════════════════════════

from domain.models.newton import NewtonRequest
from domain.solvers.newton import solve_newton
from application.use_cases.run_newton import run_newton
from ui.presenters.newton_presenter import present_newton_result
from application.services.newton_solver import NewtonSolver


def test_e2e_newton_smoke() -> None:
    parser = ParserService()
    solver = NewtonSolver()
    request = NewtonRequest("x**2 - 4", x0=3.0, tolerance=1e-6, max_iterations=100)
    result = run_newton(request, parser, solver)
    assert result.status == "success", f"Expected success, got {result.status}"
    assert result.converged is True
    assert abs(result.root - 2.0) < 1e-4
    assert len(result.iterations) > 0

    data = present_newton_result(result)
    assert data["session"]["raiz"] == result.root
    assert data["metrics"]["root"] == result.root
    assert len(data["iterations"]) == len(result.iterations)


# ═════════════════════════════════════════════════════════════════════════════
# Prueba de humo e2e de comparación
# ═════════════════════════════════════════════════════════════════════════════

from domain.models.comparison import ComparisonRequest  # noqa: E402
from application.use_cases.run_comparison import run_comparison  # noqa: E402
from ui.presenters.comparison_presenter import present_comparison_result  # noqa: E402


def test_e2e_comparison_smoke() -> None:
    parser = ParserService()
    bisection_solver = BisectionSolver()
    newton_solver = NewtonSolver()
    request = ComparisonRequest(
        expression="x**2 - 4",
        bisection_a=1.0, bisection_b=3.0,
        newton_x0=3.0,
        tolerance=1e-6, max_iterations=100,
    )
    result = run_comparison(
        request,
        parser=parser,
        bisection_solver=bisection_solver,
        newton_solver=newton_solver,
    )
    assert result.status == "success", f"Expected success, got {result.status}"

    assert result.bisection.converged is True
    assert result.bisection.root is not None
    assert abs(result.bisection.root - 2.0) < 1e-4
    assert result.bisection.iterations_count > 0

    assert result.newton.converged is True
    assert result.newton.root is not None
    assert abs(result.newton.root - 2.0) < 1e-4
    assert result.newton.iterations_count > 0

    data = present_comparison_result(result)
    assert "Bisección" in data["metrics"]
    assert "Newton-Raphson" in data["metrics"]
    assert data["session"]["metodo_activo"] == "Comparación"
    assert len(data["session"]["iters_bis"]) > 0
    assert len(data["session"]["iters_nwt"]) > 0


def test_e2e_comparison_one_missing() -> None:
    parser = ParserService()
    bisection_solver = BisectionSolver()
    newton_solver = NewtonSolver()
    request = ComparisonRequest(
        expression="x**2 + 1",
        bisection_a=0.0, bisection_b=1.0,
        newton_x0=3.0,
        tolerance=1e-6, max_iterations=100,
    )
    result = run_comparison(
        request,
        parser=parser,
        bisection_solver=bisection_solver,
        newton_solver=newton_solver,
    )
    assert result.bisection.converged is False
    assert result.bisection.root is None
    assert result.newton.iterations_count > 0


def test_e2e_comparison_partial_bisection_only() -> None:
    parser = ParserService()
    bisection_solver = BisectionSolver()
    newton_solver = NewtonSolver()
    request = ComparisonRequest(
        expression="x**2 - 1",
        bisection_a=0.5, bisection_b=3.0,
        newton_x0=0.0,
        tolerance=1e-6, max_iterations=100,
    )
    result = run_comparison(
        request,
        parser=parser,
        bisection_solver=bisection_solver,
        newton_solver=newton_solver,
    )

    assert result.bisection.converged is True
    assert result.bisection.root is not None
    assert abs(result.bisection.root - 1.0) < 1e-4
    assert result.bisection.iterations_count > 0
    assert result.bisection.error_message is None

    assert result.newton.converged is False
    assert result.newton.root is None
    assert result.newton.iterations_count == 0
    assert "derivada" in (result.newton.error_message or "").lower()

    data = present_comparison_result(result)
    assert data["metrics"]["Bisección"]["converged"] is True
    assert data["metrics"]["Bisección"]["root"] is not None
    assert data["metrics"]["Newton-Raphson"]["converged"] is False
    assert data["metrics"]["Newton-Raphson"]["root"] is None
    assert data["metrics"]["Newton-Raphson"]["error_message"] is not None


def test_e2e_comparison_partial_newton_only() -> None:
    parser = ParserService()
    bisection_solver = BisectionSolver()
    newton_solver = NewtonSolver()
    request = ComparisonRequest(
        expression="x**2 - 1",
        bisection_a=5.0, bisection_b=10.0,
        newton_x0=3.0,
        tolerance=1e-6, max_iterations=100,
    )
    result = run_comparison(
        request,
        parser=parser,
        bisection_solver=bisection_solver,
        newton_solver=newton_solver,
    )

    assert result.bisection.converged is False
    assert result.bisection.root is None
    assert result.bisection.iterations_count == 0
    assert result.bisection.error_message is not None

    assert result.newton.converged is True
    assert result.newton.root is not None
    assert abs(result.newton.root - 1.0) < 1e-4
    assert result.newton.iterations_count > 0
    assert result.newton.error_message is None

    data = present_comparison_result(result)
    assert data["metrics"]["Bisección"]["converged"] is False
    assert data["metrics"]["Bisección"]["root"] is None
    assert data["metrics"]["Bisección"]["error_message"] is not None
    assert data["metrics"]["Newton-Raphson"]["converged"] is True
    assert data["metrics"]["Newton-Raphson"]["root"] is not None


if __name__ == "__main__":
    test_e2e_smoke()
    test_e2e_newton_smoke()
    test_e2e_comparison_smoke()
    test_e2e_comparison_one_missing()
    test_e2e_comparison_partial_bisection_only()
    test_e2e_comparison_partial_newton_only()
    print("=== TODAS LAS VERIFICACIONES E2E PASARON ===")

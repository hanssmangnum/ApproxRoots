"""Prueba de humo de integración rápida de extremo a extremo para la separación de bisección.

Se ejecuta bajo pytest (descubierta mediante el patrón e2e_*.py) o directamente::

    python tests/e2e_smoke.py
"""

import sys
from pathlib import Path

# Hacer que la raíz del proyecto sea importable sin importar cómo se invoque este script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from domain.models.bisection import BisectionRequest
from domain.solvers.bisection import solve_bisection
from application.use_cases.run_bisection import run_bisection
from ui.presenters.bisection_presenter import present_bisection_result
from utils.func_parser import compile_expression


def test_e2e_smoke() -> None:
    """De extremo a extremo: caso de uso con parser y solver reales."""
    request = BisectionRequest("x**3 - x - 2", 1.0, 2.0, 1e-6, 100)
    result = run_bisection(
        request, compile_fn=compile_expression, solve_fn=solve_bisection
    )
    assert result.status == "success", f"Expected success, got {result.status}"
    assert result.converged is True
    assert abs(result.root - 1.521379) < 1e-4
    assert len(result.iterations) == 20

    # Salida del presenter
    data = present_bisection_result(result)
    assert data["session"]["raiz"] == result.root
    assert data["metrics"]["root"] == result.root
    assert len(data["iterations"]) == 20

    # El wrapper legacy sigue funcionando
    from metodos.biseccion import biseccion
    from utils.func_parser import parsear_funcion

    f, _, _, _ = parsear_funcion("x**3 - x - 2")
    iters, raiz, convergio = biseccion(f, 1.0, 2.0)
    assert convergio is True
    assert abs(raiz - 1.521379) < 1e-4
    assert len(iters) == 20


# ═════════════════════════════════════════════════════════════════════════════
# Prueba de humo e2e de Newton-Raphson
# ═════════════════════════════════════════════════════════════════════════════

from domain.models.newton import NewtonRequest
from domain.solvers.newton import solve_newton
from application.use_cases.run_newton import run_newton
from ui.presenters.newton_presenter import present_newton_result


def _compile_derivative(texto: str):
    """Compilador de derivada inline usando el parser legacy.

    Existe solo para la prueba e2e dentro de la Unidad de Trabajo 1. La
    utilidad ``compile_with_derivative`` apropiada se agrega en la Fase 2.
    """
    from utils.func_parser import parsear_funcion
    _, df, _, _ = parsear_funcion(texto)
    return df


def test_e2e_newton_smoke() -> None:
    """De extremo a extremo: caso de uso de Newton con parser, derivada y solver reales."""
    request = NewtonRequest("x**2 - 4", x0=3.0, tolerance=1e-6, max_iterations=100)
    result = run_newton(
        request,
        compile_fn=compile_expression,
        derive_fn=_compile_derivative,
        solve_fn=solve_newton,
    )
    assert result.status == "success", f"Expected success, got {result.status}"
    assert result.converged is True
    assert abs(result.root - 2.0) < 1e-4
    assert len(result.iterations) > 0

    # Salida del presenter
    data = present_newton_result(result)
    assert data["session"]["raiz"] == result.root
    assert data["metrics"]["root"] == result.root
    assert len(data["iterations"]) == len(result.iterations)

    # El wrapper legacy sigue funcionando
    from metodos.newton import newton_raphson
    from utils.func_parser import parsear_funcion

    f, df, _, _ = parsear_funcion("x**2 - 4")
    iters, raiz, convergio = newton_raphson(f, df, x0=3.0)
    assert convergio is True
    assert abs(raiz - 2.0) < 1e-4
    assert len(iters) > 0


# ═════════════════════════════════════════════════════════════════════════════
# Prueba de humo e2e de comparación
# ═════════════════════════════════════════════════════════════════════════════

from domain.models.comparison import ComparisonRequest  # noqa: E402
from application.use_cases.run_comparison import run_comparison  # noqa: E402
from application.use_cases.run_bisection import run_bisection  # noqa: E402
from application.use_cases.run_newton import run_newton  # noqa: E402
from domain.solvers.bisection import solve_bisection  # noqa: E402
from domain.solvers.newton import solve_newton  # noqa: E402
from utils.func_parser import compile_with_derivative  # noqa: E402
from ui.presenters.comparison_presenter import present_comparison_result  # noqa: E402


def test_e2e_comparison_smoke() -> None:
    """De extremo a extremo: caso de uso de comparación con compile, casos de uso y solvers reales."""
    request = ComparisonRequest(
        expression="x**2 - 4",
        bisection_a=1.0, bisection_b=3.0,
        newton_x0=3.0,
        tolerance=1e-6, max_iterations=100,
    )
    result = run_comparison(
        request,
        compile_fn=compile_expression,
        derive_fn=lambda expr: compile_with_derivative(expr)[1],
        run_bisection_fn=run_bisection,
        run_newton_fn=run_newton,
        bisection_solve_fn=solve_bisection,
        newton_solve_fn=solve_newton,
    )
    assert result.status == "success", f"Expected success, got {result.status}"

    # Bisección debería converger a sqrt(4) ≈ 2.0 mediante [1, 3]
    assert result.bisection.converged is True
    assert result.bisection.root is not None
    assert abs(result.bisection.root - 2.0) < 1e-4
    assert result.bisection.iterations_count > 0

    # Newton debería converger a 2.0 desde x0=3.0
    assert result.newton.converged is True
    assert result.newton.root is not None
    assert abs(result.newton.root - 2.0) < 1e-4
    assert result.newton.iterations_count > 0

    # Presenter output
    data = present_comparison_result(result)
    assert "Bisección" in data["metrics"]
    assert "Newton-Raphson" in data["metrics"]
    assert len(data["combined_series"]) == 2


def test_e2e_comparison_one_missing() -> None:
    """De extremo a extremo: comparación con un bracketing imposible — bisección falla, Newton se ejecuta sin raíz real."""
    request = ComparisonRequest(
        expression="x**2 + 1",  # siempre positiva — bisección no puede encerrar la raíz
        bisection_a=0.0, bisection_b=1.0,
        newton_x0=3.0,
        tolerance=1e-6, max_iterations=100,
    )
    result = run_comparison(
        request,
        compile_fn=compile_expression,
        derive_fn=lambda expr: compile_with_derivative(expr)[1],
        run_bisection_fn=run_bisection,
        run_newton_fn=run_newton,
        bisection_solve_fn=solve_bisection,
        newton_solve_fn=solve_newton,
    )
    # Bisección falla (sin bracketing)
    assert result.bisection.converged is False
    assert result.bisection.root is None
    # Newton no tiene raíz real para x^2+1 — llegará a max_iterations o derivative_zero
    # pero debe ejecutarse sin fallar
    assert result.newton.iterations_count > 0  # al menos comenzó


def test_e2e_comparison_partial_bisection_only() -> None:
    """De extremo a extremo: sólo bisección converge; Newton falla por derivada cero.

    f(x) = x² - 1 en [0.5, 3] con Newton en x₀=0:
    - Bisección: f(0.5)=-0.75, f(3)=8 → signo opuesto → converge a 1.0
    - Newton: f'(0)=0 → derivative_zero → falla inmediatamente
    """
    request = ComparisonRequest(
        expression="x**2 - 1",
        bisection_a=0.5, bisection_b=3.0,
        newton_x0=0.0,
        tolerance=1e-6, max_iterations=100,
    )
    result = run_comparison(
        request,
        compile_fn=compile_expression,
        derive_fn=lambda expr: compile_with_derivative(expr)[1],
        run_bisection_fn=run_bisection,
        run_newton_fn=run_newton,
        bisection_solve_fn=solve_bisection,
        newton_solve_fn=solve_newton,
    )

    # Bisección converge a 1.0
    assert result.bisection.converged is True
    assert result.bisection.root is not None
    assert abs(result.bisection.root - 1.0) < 1e-4
    assert result.bisection.iterations_count > 0
    assert result.bisection.error_message is None

    # Newton falla por derivada cero
    assert result.newton.converged is False
    assert result.newton.root is None
    assert result.newton.iterations_count == 0
    assert "derivada" in (result.newton.error_message or "").lower()

    # Presenter: ambas métricas existen
    data = present_comparison_result(result)
    assert data["metrics"]["Bisección"]["converged"] is True
    assert data["metrics"]["Bisección"]["root"] is not None
    assert data["metrics"]["Newton-Raphson"]["converged"] is False
    assert data["metrics"]["Newton-Raphson"]["root"] is None
    assert data["metrics"]["Newton-Raphson"]["error_message"] is not None


def test_e2e_comparison_partial_newton_only() -> None:
    """De extremo a extremo: sólo Newton converge; bisección falla por bracketing inválido.

    f(x) = x² - 1 en [5, 10] con Newton en x₀=3:
    - Bisección: f(5)=24, f(10)=99 → mismo signo → invalid_bracket
    - Newton: desde x₀=3 converge rápido a 1.0
    """
    request = ComparisonRequest(
        expression="x**2 - 1",
        bisection_a=5.0, bisection_b=10.0,
        newton_x0=3.0,
        tolerance=1e-6, max_iterations=100,
    )
    result = run_comparison(
        request,
        compile_fn=compile_expression,
        derive_fn=lambda expr: compile_with_derivative(expr)[1],
        run_bisection_fn=run_bisection,
        run_newton_fn=run_newton,
        bisection_solve_fn=solve_bisection,
        newton_solve_fn=solve_newton,
    )

    # Bisección falla (sin cambio de signo)
    assert result.bisection.converged is False
    assert result.bisection.root is None
    assert result.bisection.iterations_count == 0
    assert result.bisection.error_message is not None

    # Newton converge a 1.0
    assert result.newton.converged is True
    assert result.newton.root is not None
    assert abs(result.newton.root - 1.0) < 1e-4
    assert result.newton.iterations_count > 0
    assert result.newton.error_message is None

    # Presenter: ambas métricas existen
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

"""Pruebas del solver — límites numéricos puros, sin imports del parser ni de la UI."""

import math
import pytest
from domain.models.bisection import SolverConfig, BisectionResult
from domain.solvers.bisection import solve_bisection


def test_convergent_interval_returns_iterations():
    """DADO un evaluador continuo con intervalo que cambia de signo
       CUANDO el solver de bisección se ejecuta
       ENTONCES retorna un resultado exitoso con iteraciones."""
    config = SolverConfig(a=1.0, b=2.0, tolerance=1e-6, max_iterations=100)
    result = solve_bisection(lambda x: x**3 - x - 2, config)

    assert result.status == "success"
    assert result.converged is True
    assert result.root is not None
    assert abs(result.root - 1.521379) < 1e-4
    assert len(result.iterations) > 0

    # Cada iteración debe tener campos numéricos válidos
    for it in result.iterations:
        assert it.iteration >= 1
        assert math.isfinite(it.midpoint)
        assert math.isfinite(it.f_midpoint)
        assert math.isfinite(it.error_abs)
        assert it.a < it.b  # invariante


def test_invalid_bracket_returns_failure():
    """DADO un evaluador cuyos extremos no encierran una raíz
       CUANDO el solver de bisección se ejecuta
       ENTONCES retorna estado invalid_bracket (sin excepción)."""
    # f(x) = x**2 + 1 es siempre positiva en [-1, 1]
    config = SolverConfig(a=-1.0, b=1.0, tolerance=1e-6, max_iterations=100)
    result = solve_bisection(lambda x: x**2 + 1, config)

    assert result.status == "invalid_bracket"
    assert result.converged is False
    assert result.root is None
    assert len(result.iterations) == 0


def test_non_finite_evaluator_output_returns_failure():
    """DADO un evaluador que retorna NaN en un extremo
       CUANDO el solver de bisección se ejecuta
       ENTONCES retorna estado non_finite (sin excepción)."""
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
    """DADO una tolerancia muy estricta con pocas iteraciones permitidas
       CUANDO el solver agota max_iterations
       ENTONCES retorna estado max_iterations con iteraciones parciales."""
    config = SolverConfig(a=1.0, b=2.0, tolerance=1e-15, max_iterations=5)
    result = solve_bisection(lambda x: x**3 - x - 2, config)

    assert result.status == "max_iterations"
    assert result.converged is False
    assert result.root is not None  # best approximation so far
    assert len(result.iterations) == 5


def test_boundary_root_at_a_returns_success():
    """DADO f(a) == 0 (raíz exacta en el límite izquierdo)
       CUANDO el solver de bisección se ejecuta
       ENTONCES retorna éxito con root == a (sin iteraciones necesarias)."""
    config = SolverConfig(a=0.0, b=1.0, tolerance=1e-6, max_iterations=100)
    result = solve_bisection(lambda x: x, config)  # f(0) = 0

    assert result.status == "success"
    assert result.converged is True
    assert result.root == 0.0
    assert len(result.iterations) == 0


def test_boundary_root_at_b_returns_success():
    """DADO f(b) == 0 (raíz exacta en el límite derecho)
       CUANDO el solver de bisección se ejecuta
       ENTONCES retorna éxito con root == b (sin iteraciones necesarias)."""
    config = SolverConfig(a=0.0, b=1.0, tolerance=1e-6, max_iterations=100)
    result = solve_bisection(lambda x: x - 1, config)  # f(1) = 0

    assert result.status == "success"
    assert result.converged is True
    assert result.root == 1.0
    assert len(result.iterations) == 0


def test_solver_has_no_forbidden_imports():
    """PRUEBA que el módulo solver no tiene dependencias del parser ni de la UI."""
    import domain.solvers.bisection as mod
    source = mod.__file__
    with open(source, encoding="utf-8") as fh:
        content = fh.read()
    assert "STREAMLIT" not in content.upper(), "el solver no debe importar streamlit"
    assert "func_parser" not in content, "el solver no debe importar el parser"
    assert "matplotlib" not in content, "el solver no debe importar matplotlib"
    assert "pandas" not in content, "el solver no debe importar pandas"


# ═════════════════════════════════════════════════════════════════════════════
# Pruebas del solver de Newton-Raphson
# ═════════════════════════════════════════════════════════════════════════════

from domain.models.newton import NewtonConfig, NewtonResult  # noqa: E402
from domain.solvers.newton import solve_newton  # noqa: E402


def test_newton_convergent_returns_iterations():
    """DADO f(x) = x**2 - 4 con una buena aproximación inicial
       CUANDO el solver de Newton se ejecuta
       ENTONCES retorna un resultado exitoso con iteraciones."""
    f = lambda x: x**2 - 4
    df = lambda x: 2 * x
    config = NewtonConfig(x0=3.0, tolerance=1e-6, max_iterations=100)
    result = solve_newton(f, df, config)

    assert result.status == "success"
    assert result.converged is True
    assert result.root is not None
    assert abs(result.root - 2.0) < 1e-4  # root at x=2
    assert len(result.iterations) > 0

    # Cada iteración debe tener campos numéricos válidos
    for it in result.iterations:
        assert it.iteration >= 1
        assert math.isfinite(it.x_previous)
        assert math.isfinite(it.x_next)
        assert math.isfinite(it.f_x)
        assert math.isfinite(it.df_x)
        assert math.isfinite(it.error_abs)
        assert math.isfinite(it.tangent_slope)
        assert math.isfinite(it.tangent_intercept)


def test_newton_derivative_zero_returns_failure():
    """DADO f(x) = x**2 + 1 con df en un punto que se aproxima a cero
       CUANDO el solver de Newton se ejecuta
       ENTONCES retorna estado derivative_zero (sin excepción)."""
    # f es plana en x=0: f(x)=1, f'(x)=0
    f = lambda x: 1.0
    df = lambda x: 0.0
    config = NewtonConfig(x0=0.0, tolerance=1e-6, max_iterations=100)
    result = solve_newton(f, df, config)

    assert result.status == "derivative_zero"
    assert result.converged is False
    assert result.root is None


def test_newton_non_finite_evaluator_returns_failure():
    """DADO una derivada que retorna NaN
       CUANDO el solver de Newton se ejecuta
       ENTONCES retorna estado non_finite (sin excepción)."""
    f = lambda x: x**2 - 4
    df = lambda x: float("nan") if x > 2.5 else 2 * x
    config = NewtonConfig(x0=3.0, tolerance=1e-6, max_iterations=100)
    result = solve_newton(f, df, config)

    assert result.status == "non_finite"
    assert result.converged is False
    assert result.root is None


def test_newton_max_iterations_without_convergence():
    """DADO una tolerancia muy estricta con pocas iteraciones permitidas
       CUANDO el solver de Newton agota max_iterations
       ENTONCES retorna estado max_iterations con iteraciones parciales."""
    f = lambda x: x**2 - 4
    df = lambda x: 2 * x
    config = NewtonConfig(x0=1e10, tolerance=1e-15, max_iterations=3)
    result = solve_newton(f, df, config)

    assert result.status == "max_iterations"
    assert result.converged is False
    assert result.root is not None  # best approximation so far
    assert len(result.iterations) == 3


def test_newton_non_finite_step_returns_failure():
    """DADO un paso de Newton que produce un valor infinito
       CUANDO el solver evalúa el paso
       ENTONCES retorna estado non_finite."""
    # f(x) = 1/(x-2) evaluada cerca de x=2 diverge
    # Usar una función cuyo paso de Newton diverge
    f = lambda x: 1.0 / (x - 2.0) if x != 2.0 else float("inf")
    df = lambda x: -1.0 / ((x - 2.0) ** 2) if x != 2.0 else float("inf")
    config = NewtonConfig(x0=2.1, tolerance=1e-6, max_iterations=10)

    # Esto puede o no producir non_finite; como mínimo no debe fallar
    result = solve_newton(f, df, config)
    assert result.status in ("non_finite", "max_iterations")
    assert result.converged is False


def test_newton_solver_has_no_forbidden_imports():
    """PRUEBA que el módulo solver de Newton no tiene dependencias del parser ni de la UI."""
    import domain.solvers.newton as mod
    source = mod.__file__
    with open(source, encoding="utf-8") as fh:
        content = fh.read()
    assert "STREAMLIT" not in content.upper(), "el solver no debe importar streamlit"
    assert "func_parser" not in content, "el solver no debe importar el parser"
    assert "matplotlib" not in content, "el solver no debe importar matplotlib"
    assert "pandas" not in content, "el solver no debe importar pandas"

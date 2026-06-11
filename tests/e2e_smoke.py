"""Quick end-to-end integration smoke test for the bisection separation.

Runs under pytest (discovered via e2e_*.py pattern) or directly::

    python tests/e2e_smoke.py
"""

import sys
from pathlib import Path

# Make the project root importable regardless of how this script is invoked
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from domain.models.bisection import BisectionRequest
from domain.solvers.bisection import solve_bisection
from application.use_cases.run_bisection import run_bisection
from ui.presenters.bisection_presenter import present_bisection_result
from utils.func_parser import compile_expression


def test_e2e_smoke() -> None:
    """End-to-end: use case with real parser and solver."""
    request = BisectionRequest("x**3 - x - 2", 1.0, 2.0, 1e-6, 100)
    result = run_bisection(
        request, compile_fn=compile_expression, solve_fn=solve_bisection
    )
    assert result.status == "success", f"Expected success, got {result.status}"
    assert result.converged is True
    assert abs(result.root - 1.521379) < 1e-4
    assert len(result.iterations) == 20

    # Presenter output
    data = present_bisection_result(result)
    assert data["session"]["raiz"] == result.root
    assert data["metrics"]["root"] == result.root
    assert len(data["iterations"]) == 20

    # Legacy wrapper still works
    from metodos.biseccion import biseccion
    from utils.func_parser import parsear_funcion

    f, _, _, _ = parsear_funcion("x**3 - x - 2")
    iters, raiz, convergio = biseccion(f, 1.0, 2.0)
    assert convergio is True
    assert abs(raiz - 1.521379) < 1e-4
    assert len(iters) == 20


if __name__ == "__main__":
    test_e2e_smoke()
    print("=== ALL E2E CHECKS PASSED ===")

# application/use_cases/run_bisection.py

"""Caso de uso de bisección que coordina el parsing y la resolución."""

from typing import Callable

from domain.models.bisection import (
    BisectionRequest,
    SolverConfig,
    BisectionResult,
)


def run_bisection(
    request: BisectionRequest,
    compile_fn: Callable[[str], Callable[[float], float]],
    solve_fn: Callable[
        [Callable[[float], float], SolverConfig],
        BisectionResult,
    ],
) -> BisectionResult:
    """Orquesta una ejecución de bisección.

    1. Compila la expresión mediante *compile_fn*.
    2. Si la compilación falla, retorna un resultado ``parse_error``.
    3. Construye un ``SolverConfig`` a partir de la solicitud.
    4. Resuelve mediante *solve_fn*.
    5. Retorna el resultado tipificado.

    Los argumentos de función/callable hacen que el caso de uso sea testeable con fakes.
    """
    # Paso 1 — parse
    try:
        evaluator = compile_fn(request.expression)
    except ValueError as exc:
        return BisectionResult(
            iterations=[],
            root=None,
            converged=False,
            status="parse_error",
            error_message=str(exc),
        )

    # Paso 2 — solve
    config = SolverConfig(
        a=request.a,
        b=request.b,
        tolerance=request.tolerance,
        max_iterations=request.max_iterations,
    )
    return solve_fn(evaluator, config)

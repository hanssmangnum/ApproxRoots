# application/use_cases/run_newton.py

"""Caso de uso de Newton que coordina el parsing y la resolución."""

from typing import Callable

from domain.models.newton import (
    NewtonRequest,
    NewtonConfig,
    NewtonResult,
)


def run_newton(
    request: NewtonRequest,
    compile_fn: Callable[[str], Callable[[float], float]],
    derive_fn: Callable[[str], Callable[[float], float]],
    solve_fn: Callable[
        [Callable[[float], float], Callable[[float], float], NewtonConfig],
        NewtonResult,
    ],
) -> NewtonResult:
    """Orquesta una ejecución de Newton-Raphson.

    1. Compila la expresión y su derivada mediante *compile_fn* y *derive_fn*.
    2. Si alguna compilación falla, retorna un resultado ``parse_error``.
    3. Construye un ``NewtonConfig`` a partir de la solicitud.
    4. Resuelve mediante *solve_fn*.
    5. Retorna el resultado tipificado.

    Los argumentos de función/callable hacen que el caso de uso sea testeable con fakes.
    """
    # Paso 1 — compilar función
    try:
        evaluator = compile_fn(request.expression)
    except ValueError as exc:
        return NewtonResult(
            iterations=[],
            root=None,
            converged=False,
            status="parse_error",
            error_message=str(exc),
        )

    # Paso 2 — compilar derivada
    try:
        derivative = derive_fn(request.expression)
    except ValueError as exc:
        return NewtonResult(
            iterations=[],
            root=None,
            converged=False,
            status="parse_error",
            error_message=str(exc),
        )

    # Paso 3 — resolver
    config = NewtonConfig(
        x0=request.x0,
        tolerance=request.tolerance,
        max_iterations=request.max_iterations,
    )
    return solve_fn(evaluator, derivative, config)

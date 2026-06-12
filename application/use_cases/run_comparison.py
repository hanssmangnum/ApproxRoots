# application/use_cases/run_comparison.py

"""Caso de uso de comparación que orquesta bisección y Newton en paralelo."""

from typing import Callable

from domain.models.bisection import (
    BisectionRequest,
    SolverConfig,
    BisectionResult,
)
from domain.models.newton import (
    NewtonRequest,
    NewtonConfig,
    NewtonResult,
)
from domain.models.comparison import (
    ComparisonRequest,
    MethodSummary,
    ComparisonResult,
)


def _summarise(
    name: str,
    result: BisectionResult | NewtonResult,
) -> MethodSummary:
    """Envuelve un resultado tipificado del solver en un *MethodSummary* normalizado."""
    final_error = (
        result.iterations[-1].error_abs
        if result.iterations and result.status == "success"
        else None
    )
    return MethodSummary(
        method_name=name,
        root=result.root,
        converged=result.converged,
        iterations_count=len(result.iterations),
        final_error=final_error,
        error_message=result.error_message,
        status=result.status,
    )


def run_comparison(
    request: ComparisonRequest,
    compile_fn: Callable[[str], Callable[[float], float]],
    derive_fn: Callable[[str], Callable[[float], float]],
    run_bisection_fn: Callable[
        [BisectionRequest, Callable, Callable],
        BisectionResult,
    ],
    run_newton_fn: Callable[
        [NewtonRequest, Callable, Callable, Callable],
        NewtonResult,
    ],
    bisection_solve_fn: Callable[
        [Callable[[float], float], SolverConfig],
        BisectionResult,
    ],
    newton_solve_fn: Callable[
        [Callable[[float], float], Callable[[float], float], NewtonConfig],
        NewtonResult,
    ],
) -> ComparisonResult:
    """Orquesta una ejecución de comparación.

    1. Ejecuta bisección y Newton a través de sus casos de uso (no los solvers directamente).
    2. Envuelve cada resultado en un ``MethodSummary`` normalizado.
    3. Retorna el ``ComparisonResult`` combinado.

    Los argumentos callable hacen que el caso de uso sea testeable con fakes para
    cada colaborador (compile, derive, use-case y solver).
    """
    # Construir solicitudes hijas
    bisection_request = BisectionRequest(
        expression=request.expression,
        a=request.bisection_a,
        b=request.bisection_b,
        tolerance=request.tolerance,
        max_iterations=request.max_iterations,
    )
    newton_request = NewtonRequest(
        expression=request.expression,
        x0=request.newton_x0,
        tolerance=request.tolerance,
        max_iterations=request.max_iterations,
    )

    # Ejecutar ambos métodos — cada caso de uso hijo maneja su propia compilación
    bisection_result = run_bisection_fn(
        bisection_request, compile_fn, bisection_solve_fn,
    )
    newton_result = run_newton_fn(
        newton_request, compile_fn, derive_fn, newton_solve_fn,
    )

    # Resumir y retornar
    overall_status = "success"
    error_message = None
    if bisection_result.status == "parse_error" and newton_result.status == "parse_error":
        overall_status = "parse_error"
        error_message = bisection_result.error_message or newton_result.error_message

    return ComparisonResult(
        bisection=_summarise("Bisección", bisection_result),
        newton=_summarise("Newton-Raphson", newton_result),
        expression=request.expression,
        status=overall_status,
        error_message=error_message,
        bisection_result=bisection_result,
        newton_result=newton_result,
    )

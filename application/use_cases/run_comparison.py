"""Caso de uso de comparación que orquesta bisección y Newton en paralelo."""

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
from application.use_cases.run_bisection import run_bisection
from application.use_cases.run_newton import run_newton
from application.services.parser_service import ParserService
from application.services.bisection_solver import BisectionSolver
from application.services.newton_solver import NewtonSolver


def _summarise(
    name: str,
    result: BisectionResult | NewtonResult,
) -> MethodSummary:
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
    parser: ParserService,
    bisection_solver: BisectionSolver,
    newton_solver: NewtonSolver,
) -> ComparisonResult:
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

    bisection_result = run_bisection(
        bisection_request, parser, bisection_solver,
    )
    newton_result = run_newton(
        newton_request, parser, newton_solver,
    )

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

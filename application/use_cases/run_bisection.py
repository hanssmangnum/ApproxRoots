"""Caso de uso de bisección que coordina el parsing y la resolución."""

from domain.models.bisection import (
    BisectionRequest,
    SolverConfig,
    BisectionResult,
)
from application.services.parser_service import ParserService
from application.services.bisection_solver import BisectionSolver


def run_bisection(
    request: BisectionRequest,
    parser: ParserService,
    solver: BisectionSolver,
) -> BisectionResult:
    try:
        evaluator = parser.compile_expression(request.expression)
    except ValueError as exc:
        return BisectionResult(
            iterations=[],
            root=None,
            converged=False,
            status="parse_error",
            error_message=str(exc),
        )

    config = SolverConfig(
        a=request.a,
        b=request.b,
        tolerance=request.tolerance,
        max_iterations=request.max_iterations,
    )
    return solver.solve(evaluator, config)

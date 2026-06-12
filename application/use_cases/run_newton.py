"""Caso de uso de Newton que coordina el parsing y la resolución."""

from domain.models.newton import (
    NewtonRequest,
    NewtonConfig,
    NewtonResult,
)
from application.services.parser_service import ParserService
from application.services.newton_solver import NewtonSolver


def run_newton(
    request: NewtonRequest,
    parser: ParserService,
    solver: NewtonSolver,
) -> NewtonResult:
    try:
        evaluator = parser.compile_expression(request.expression)
    except ValueError as exc:
        return NewtonResult(
            iterations=[],
            root=None,
            converged=False,
            status="parse_error",
            error_message=str(exc),
        )

    try:
        derivative = parser.compile_derivative(request.expression)
    except ValueError as exc:
        return NewtonResult(
            iterations=[],
            root=None,
            converged=False,
            status="parse_error",
            error_message=str(exc),
        )

    config = NewtonConfig(
        x0=request.x0,
        tolerance=request.tolerance,
        max_iterations=request.max_iterations,
    )
    return solver.solve(evaluator, derivative, config)

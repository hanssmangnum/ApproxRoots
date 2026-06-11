# application/use_cases/run_bisection.py

"""Bisection use case that coordinates parsing and solving."""

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
    """Orchestrate a bisection execution.

    1. Compile the expression via *compile_fn*.
    2. If compilation fails, return a ``parse_error`` result.
    3. Build a ``SolverConfig`` from the request.
    4. Solve via *solve_fn*.
    5. Return the typed result.

    The function/callable arguments make the use case testable with fakes.
    """
    # Step 1 — parse
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

    # Step 2 — solve
    config = SolverConfig(
        a=request.a,
        b=request.b,
        tolerance=request.tolerance,
        max_iterations=request.max_iterations,
    )
    return solve_fn(evaluator, config)

from typing import Callable

from domain.models.bisection import SolverConfig, BisectionResult
from domain.solvers.bisection import solve_bisection


class BisectionSolver:
    """Envuelve el solver de bisección puro para los casos de uso."""

    def solve(
        self,
        evaluator: Callable[[float], float],
        config: SolverConfig,
    ) -> BisectionResult:
        return solve_bisection(evaluator, config)

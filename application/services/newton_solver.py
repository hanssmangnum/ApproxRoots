from typing import Callable

from domain.models.newton import NewtonConfig, NewtonResult
from domain.solvers.newton import solve_newton


class NewtonSolver:
    """Envuelve el solver de Newton-Raphson puro para los casos de uso."""

    def solve(
        self,
        f: Callable[[float], float],
        df: Callable[[float], float],
        config: NewtonConfig,
    ) -> NewtonResult:
        return solve_newton(f, df, config)

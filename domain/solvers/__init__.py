# domain/solvers/__init__.py

from .bisection import solve_bisection
from .newton import solve_newton

__all__ = ["solve_bisection", "solve_newton"]

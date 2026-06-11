# domain/models/bisection.py

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class BisectionRequest:
    """Raw input from the UI before parsing."""

    expression: str
    a: float
    b: float
    tolerance: float
    max_iterations: int


@dataclass(frozen=True)
class SolverConfig:
    """Numeric-only configuration for the bisection solver (no expression)."""

    a: float
    b: float
    tolerance: float
    max_iterations: int


@dataclass(frozen=True)
class BisectionIteration:
    """A single step of the bisection numerical loop."""

    iteration: int
    a: float
    b: float
    midpoint: float
    f_midpoint: float
    error_abs: float
    error_rel: float


@dataclass(frozen=True)
class BisectionResult:
    """Typed outcome of a bisection solver run.

    ``status`` describes the final state:
      - ``"success"`` — converged within tolerance
      - ``"invalid_bracket"`` — f(a) and f(b) do not bracket a root
      - ``"non_finite"`` — evaluator returned NaN or infinity
      - ``"max_iterations"`` — did not converge within the iteration limit
      - ``"parse_error"`` — expression could not be compiled (set by use case)
    """

    iterations: list[BisectionIteration]
    root: Optional[float]
    converged: bool
    status: str
    error_message: Optional[str] = None

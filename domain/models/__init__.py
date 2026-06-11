# domain/models/__init__.py

from .bisection import (
    BisectionRequest,
    SolverConfig,
    BisectionIteration,
    BisectionResult,
)
from .newton import (
    NewtonRequest,
    NewtonConfig,
    NewtonIteration,
    NewtonResult,
)
from .comparison import (
    ComparisonRequest,
    MethodSummary,
    ComparisonResult,
)

__all__ = [
    "BisectionRequest",
    "SolverConfig",
    "BisectionIteration",
    "BisectionResult",
    "NewtonRequest",
    "NewtonConfig",
    "NewtonIteration",
    "NewtonResult",
    "ComparisonRequest",
    "MethodSummary",
    "ComparisonResult",
]

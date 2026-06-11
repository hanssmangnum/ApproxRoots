# domain/models/comparison.py

"""Modelos de dominio para la orquestación de comparación bisección vs Newton."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ComparisonRequest:
    """Entrada cruda para una ejecución de comparación combinando ambos métodos."""

    expression: str
    bisection_a: float
    bisection_b: float
    newton_x0: float
    tolerance: float
    max_iterations: int


@dataclass(frozen=True)
class MethodSummary:
    """Resumen normalizado del resultado de un método dentro de una comparación."""

    method_name: str
    root: Optional[float]
    converged: bool
    iterations_count: int
    final_error: Optional[float]
    error_message: Optional[str]


@dataclass(frozen=True)
class ComparisonResult:
    """Resultado tipificado de una ejecución de comparación.

    ``status`` describe el estado general:
      - ``"success"`` — ambos métodos se ejecutaron (uno o ambos pueden haber convergido).
      - ``"parse_error"`` — la expresión no pudo compilarse.
    """

    bisection: MethodSummary
    newton: MethodSummary
    expression: str
    status: str
    error_message: Optional[str] = None

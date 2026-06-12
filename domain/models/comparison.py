# domain/models/comparison.py

"""Modelos de dominio para la orquestación de comparación bisección vs Newton."""

from dataclasses import dataclass, field
from typing import Any, Optional


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
    status: str = "success"


@dataclass(frozen=True)
class ComparisonResult:
    """Resultado tipificado de una ejecución de comparación.

    ``status`` describe el estado general:
      - ``"success"`` — ambos métodos se ejecutaron (uno o ambos pueden haber convergido).
      - ``"parse_error"`` — la expresión no pudo compilarse.

    ``bisection_result`` / ``newton_result`` llevan los objetos de resultado completos
    del dominio de cada método, necesarios para que el presenter genere datos
    detallados de iteración para la UI.
    """

    bisection: MethodSummary
    newton: MethodSummary
    expression: str
    status: str
    error_message: Optional[str] = None
    bisection_result: Any = None
    newton_result: Any = None

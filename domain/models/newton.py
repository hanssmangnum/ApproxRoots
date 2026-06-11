# domain/models/newton.py

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class NewtonRequest:
    """Entrada cruda desde la UI antes del parsing."""

    expression: str
    x0: float
    tolerance: float
    max_iterations: int


@dataclass(frozen=True)
class NewtonConfig:
    """Configuración solo numérica para el solver de Newton (sin expresión)."""

    x0: float
    tolerance: float
    max_iterations: int


@dataclass(frozen=True)
class NewtonIteration:
    """Un paso individual del bucle numérico de Newton-Raphson."""

    iteration: int
    x_previous: float
    x_next: float
    f_x: float
    df_x: float
    error_abs: float
    error_rel: float
    tangent_slope: float
    tangent_intercept: float


@dataclass(frozen=True)
class NewtonResult:
    """Resultado tipificado de una ejecución del solver de Newton-Raphson.

    ``status`` describe el estado final:
      - ``"success"`` — convergió dentro de la tolerancia
      - ``"derivative_zero"`` — la derivada llegó a casi cero (división por cero)
      - ``"non_finite"`` — el evaluador devolvió NaN o infinito
      - ``"max_iterations"`` — no convergió dentro del límite de iteraciones
      - ``"parse_error"`` — la expresión no pudo compilarse (asignado por el caso de uso)
    """

    iterations: list[NewtonIteration]
    root: Optional[float]
    converged: bool
    status: str
    error_message: Optional[str] = None

# ui/view_models/charts.py

"""Dataclasses congeladas como payload para cada tipo de gráfico.

Estos reemplazan el desempaquetado ad-hoc de dicts en ``utils/graficas.py`` con
contenedores tipificados e inmutables. El callable dentro de cada view-model es
el evaluador **compilado** (derivado de la expresión del usuario al momento de la
solicitud, no sobrescrito por entradas posteriores). Esto previene problemas de
estado obsoleto donde el gráfico lee una función que ya no coincide con los
datos de iteración.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass(frozen=True)
class BisectionChartVM:
    """View-model para ``graficar_iteracion_biseccion``.

    Campos extraídos de un dict de iteración de bisección más el callable
    de función usado para renderizar la curva.
    """

    function_callable: Callable[[float], float]
    iteration: dict
    a: float
    b: float
    xm: float


@dataclass(frozen=True)
class NewtonChartVM:
    """View-model para ``graficar_iteracion_newton``.

    Campos extraídos de un dict de iteración de Newton más el callable
    de función para renderizar.
    """

    function_callable: Callable[[float], float]
    iteration: dict
    x_previous: float
    x_next: float
    tangent: dict  # {pendiente, intercepto, x_tangente}


@dataclass(frozen=True)
class ConvergenceChartVM:
    """View-model para ``graficar_convergencia``.

    *series* es una lista de dicts ``{"iteration": int, "error_abs": float}``
    (opcionalmente con una clave ``"method"`` para gráficos de comparación).
    """

    series: list[dict]
    title: str


@dataclass(frozen=True)
class FunctionChartVM:
    """View-model para ``graficar_funcion``."""

    function_callable: Callable[[float], float]
    x_min: float
    x_max: float
    root: Optional[float]
    title: str


@dataclass(frozen=True)
class ComparisonChartVM:
    """View-model para ``graficar_comparacion``.

    ``bisection_series`` y ``newton_series`` son listas de dicts
    ``{"iteration": int, "error_abs": float}`` normalizadas.
    """

    bisection_series: list[dict]
    newton_series: list[dict]

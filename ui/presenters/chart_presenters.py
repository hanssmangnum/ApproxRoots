# ui/presenters/chart_presenters.py

"""Funciones constructoras que crean view-models de gráficos a partir de datos del presenter.

Cada función toma datos del dominio o del presenter y retorna un view-model
tipificado y congelado listo para ``utils/graficas.py``. Esto mantiene la
construcción de gráficos testeable sin Streamlit ni matplotlib.
"""

from __future__ import annotations

from typing import Callable, Optional

from ui.view_models.charts import (
    BisectionChartVM,
    ConvergenceChartVM,
    FunctionChartVM,
    NewtonChartVM,
)


def build_bisection_chart_vm(
    fn_callable: Callable[[float], float],
    iteration: dict,
) -> BisectionChartVM:
    """Construye un ``BisectionChartVM`` desde un callable de función y un dict de iteración.

    Se espera que el dict de iteración tenga las claves ``a``, ``b``, ``xm``
    (producidas por ``present_bisection_result``).
    """
    return BisectionChartVM(
        function_callable=fn_callable,
        iteration=iteration,
        a=iteration["a"],
        b=iteration["b"],
        xm=iteration["xm"],
    )


def build_newton_chart_vm(
    fn_callable: Callable[[float], float],
    iteration: dict,
) -> NewtonChartVM:
    """Construye un ``NewtonChartVM`` desde un callable de función y un dict de iteración.

    Se espera que el dict de iteración tenga las claves ``x_anterior``, ``x_nuevo``,
    ``tangente`` (producidas por ``present_newton_result``).
    """
    return NewtonChartVM(
        function_callable=fn_callable,
        iteration=iteration,
        x_previous=iteration["x_anterior"],
        x_next=iteration["x_nuevo"],
        tangent=iteration["tangente"],
    )


def build_convergence_chart_vm(
    iterations: list[dict],
    metodo: str = "Método",
) -> ConvergenceChartVM:
    """Construye un ``ConvergenceChartVM`` desde dicts de iteración estilo presenter.

    Se espera que cada dict tenga las claves ``iteracion`` y ``error_abs``.
    """
    series = [
        {"iteration": it["iteracion"], "error_abs": it["error_abs"]}
        for it in iterations
    ]
    return ConvergenceChartVM(series=series, title=metodo)


def build_function_chart_vm(
    fn_callable: Callable[[float], float],
    x_min: float,
    x_max: float,
    root: Optional[float],
    titulo: str = "f(x)",
) -> FunctionChartVM:
    """Construye un ``FunctionChartVM`` desde un callable de función e información de rango."""
    return FunctionChartVM(
        function_callable=fn_callable,
        x_min=x_min,
        x_max=x_max,
        root=root,
        title=titulo,
    )


def build_comparison_series(
    iters_bis: list[dict],
    iters_nwt: list[dict],
) -> tuple[list[dict], list[dict]]:
    """Normaliza los dicts de iteración de bisección y Newton para el gráfico de comparación.

    Retorna ``(bis_series, nwt_series)`` donde cada serie es una lista de
    ``{"iteration": int, "error_abs": float}`` apta para ``graficar_comparacion``.
    """
    bis_series = [
        {"iteration": it["iteracion"], "error_abs": it["error_abs"]}
        for it in iters_bis
    ]
    nwt_series = [
        {"iteration": it["iteracion"], "error_abs": it["error_abs"]}
        for it in iters_nwt
    ]
    return bis_series, nwt_series

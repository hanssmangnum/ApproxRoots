# ui/view_models/__init__.py

"""View-models de gráficos estables que desacoplan los plots de los callables en vivo y del estado de sesión.

Cada view-model es una dataclass congelada que lleva un **callable** de función
derivado de la expresión parseada — no la cadena de expresión original, y no una
referencia cruda a ``st.session_state``. Esto hace que cada payload de gráfico
sea testeable unitariamente sin Streamlit ni un evaluador de sesión en vivo.
"""

from .charts import (
    BisectionChartVM,
    NewtonChartVM,
    ConvergenceChartVM,
    FunctionChartVM,
)

__all__ = [
    "BisectionChartVM",
    "NewtonChartVM",
    "ConvergenceChartVM",
    "FunctionChartVM",
]

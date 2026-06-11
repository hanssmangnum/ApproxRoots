# ui/presenters/newton_presenter.py

"""Presenter / adaptador — convierte el NewtonResult del dominio a formas aptas para la UI."""

import math

from domain.models.newton import NewtonResult


def _fmt(v: float, decimales: int = 8) -> str:
    """Formateo mínimo que aproxima el formateo de app.py sin numpy."""
    if not math.isfinite(v):
        return "\u221e"  # ∞
    if abs(v) < 1e-4 or abs(v) > 1e6:
        return f"{v:.4e}"
    txt = f"{v:.{decimales}f}".rstrip("0").rstrip(".")
    return txt if txt else "0"


def present_newton_result(
    result: NewtonResult,
) -> dict:
    """Convierte un *NewtonResult* del dominio en datos compatibles con Streamlit.

    Retorna un dict con las claves:
      - ``iterations`` – lista de dicts que coincide con el formato legacy de ``metodos/newton.py``
        (``iteracion``, ``x_anterior``, ``x_nuevo``, ``f(x)``, ``f'(x)``,
         ``error_abs``, ``error_rel``, ``tangente``).
      - ``metrics`` – dict con ``root``, ``iterations_count``, ``final_error``, ``converged``.
      - ``session`` – dict que puede volcarse en ``st.session_state``
        (``iteraciones``, ``raiz``, ``convergio``).
    """
    # Filas de iteración estilo legacy
    iter_rows = []
    for it in result.iterations:
        iter_rows.append({
            "iteracion": it.iteration,
            "x_anterior": it.x_previous,
            "x_nuevo": it.x_next,
            "f(x)": it.f_x,
            "f'(x)": it.df_x,
            "error_abs": it.error_abs,
            "error_rel": it.error_rel,
            "tangente": {
                "pendiente": it.tangent_slope,
                "intercepto": it.tangent_intercept,
                "x_tangente": it.x_previous,
            },
        })

    # Métricas para la barra superior
    final_error = (
        result.iterations[-1].error_abs
        if result.iterations and result.status == "success"
        else float("nan")
    )

    metrics = {
        "root": result.root,
        "iterations_count": len(result.iterations),
        "final_error": final_error,
        "converged": result.converged,
    }

    # Payload del estado de sesión (coincide con lo que lee app.py)
    session = {
        "iteraciones": iter_rows,
        "raiz": result.root,
        "convergio": result.converged,
    }

    return {
        "iterations": iter_rows,
        "metrics": metrics,
        "session": session,
    }

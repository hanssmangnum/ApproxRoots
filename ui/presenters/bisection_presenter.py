# ui/presenters/bisection_presenter.py

"""Presenter / adaptador — convierte el BisectionResult del dominio a formas aptas para la UI."""

import math

from domain.models.bisection import BisectionResult, BisectionIteration


def _fmt(v: float, decimales: int = 8) -> str:
    """Formateo mínimo que aproxima el ``fmt`` de app.py sin numpy."""
    if not math.isfinite(v):
        return "\u221e"  # ∞
    if abs(v) < 1e-4 or abs(v) > 1e6:
        return f"{v:.4e}"
    txt = f"{v:.{decimales}f}".rstrip("0").rstrip(".")
    return txt if txt else "0"


def present_bisection_result(
    result: BisectionResult,
) -> dict:
    """Convierte un *BisectionResult* del dominio en datos compatibles con Streamlit.

    Retorna un dict con las claves:
      - ``iterations`` – lista de dicts con el formato
        (``iteracion``, ``a``, ``b``, ``xm``, ``f(xm)``, ``error_abs``, ``error_rel``).
      - ``metrics`` – dict con ``root``, ``f_root``, ``iterations_count``, ``final_error``.
      - ``session`` – dict que puede volcarse en ``st.session_state``
        (``iteraciones``, ``raiz``, ``convergio``).
    """
    # Filas de iteración estilo legacy
    iter_rows = []
    for it in result.iterations:
        iter_rows.append({
            "iteracion": it.iteration,
            "a": it.a,
            "b": it.b,
            "xm": it.midpoint,
            "f(xm)": it.f_midpoint,
            "error_abs": it.error_abs,
            "error_rel": it.error_rel,
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

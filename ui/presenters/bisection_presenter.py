# ui/presenters/bisection_presenter.py

"""Presenter / adapter — converts domain BisectionResult to UI-friendly shapes."""

import math

from domain.models.bisection import BisectionResult, BisectionIteration


def _fmt(v: float, decimales: int = 8) -> str:
    """Minimal formatting approximating app.py's ``fmt`` without numpy."""
    if not math.isfinite(v):
        return "\u221e"  # ∞
    if abs(v) < 1e-4 or abs(v) > 1e6:
        return f"{v:.4e}"
    txt = f"{v:.{decimales}f}".rstrip("0").rstrip(".")
    return txt if txt else "0"


def present_bisection_result(
    result: BisectionResult,
) -> dict:
    """Convert a domain *BisectionResult* into Streamlit-compatible data.

    Returns a dict with keys:
      - ``iterations`` – list of dicts matching the legacy ``metodos/biseccion.py`` format
        (``iteracion``, ``a``, ``b``, ``xm``, ``f(xm)``, ``error_abs``, ``error_rel``).
      - ``metrics`` – dict with ``root``, ``f_root``, ``iterations_count``, ``final_error``.
      - ``session`` – dict that can be spread into ``st.session_state``
        (``iteraciones``, ``raiz``, ``convergio``).
    """
    # Legacy-style iteration rows
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

    # Metrics for the top bar
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

    # Session state payload (matches what app.py reads)
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

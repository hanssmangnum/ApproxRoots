# ui/presenters/comparison_presenter.py

"""Presenter / adaptador — convierte el ComparisonResult del dominio a formas aptas para la UI."""

from domain.models.comparison import ComparisonResult


def present_comparison_result(
    result: ComparisonResult,
) -> dict:
    """Convierte un *ComparisonResult* del dominio en datos compatibles con Streamlit.

    Retorna un dict con las claves:

      - ``metrics`` – instantáneas de métricas por método::

            {
              "Bisección": {"root": …, "iterations": …, "error": …, "converged": …},
              "Newton-Raphson": {"root": …, "iterations": …, "error": …, "converged": …},
            }

      - ``chart_data`` – lista normalizada de ``{"method": str, "iteration": int, "error_abs": float}``
        apta para ``graficar_comparacion`` (ambas series en una lista).

      - ``session`` – dict que puede volcarse en ``st.session_state``
        (``bisection_metrics``, ``newton_metrics``, ``comparison_chart_data``).
    """
    metrics = {}
    for summary in (result.bisection, result.newton):
        metrics[summary.method_name] = {
            "root": summary.root,
            "iterations": summary.iterations_count,
            "error": summary.final_error,
            "converged": summary.converged,
            "error_message": summary.error_message,
        }

    # Series de convergencia listas para graficar (normalizadas entre métodos)
    chart_data = {"bisection": [], "newton": []}
    # No tenemos detalles por iteración dentro de MethodSummary, así que
    # construimos lo que podemos desde los campos del resumen. Los payloads
    # detallados de gráficos de iteración vienen de chart_presenters (Fase 3).
    # Para el gráfico de convergencia comparativo emitimos el snapshot escalar.
    if result.bisection.final_error is not None:
        chart_data["bisection"] = [
            {"method": "Bisección", "iteration": result.bisection.iterations_count, "error_abs": result.bisection.final_error},
        ]
    if result.newton.final_error is not None:
        chart_data["newton"] = [
            {"method": "Newton-Raphson", "iteration": result.newton.iterations_count, "error_abs": result.newton.final_error},
        ]

    # Series combinadas para graficar_comparacion
    combined_series = chart_data["bisection"] + chart_data["newton"]

    # Payload de sesión
    session = {
        "bisection_metrics": metrics.get("Bisección", {}),
        "newton_metrics": metrics.get("Newton-Raphson", {}),
        "comparison_chart_data": combined_series,
    }

    return {
        "metrics": metrics,
        "chart_data": chart_data,
        "combined_series": combined_series,
        "session": session,
    }

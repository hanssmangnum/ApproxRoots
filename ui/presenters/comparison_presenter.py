# ui/presenters/comparison_presenter.py

"""Presenter / adaptador — convierte el ComparisonResult del dominio a formas aptas para la UI."""

from domain.models.comparison import ComparisonResult
from ui.presenters.bisection_presenter import present_bisection_result
from ui.presenters.newton_presenter import present_newton_result


def present_comparison_result(
    result: ComparisonResult,
) -> dict:
    """Convierte un *ComparisonResult* del dominio en datos compatibles con Streamlit.

    Cuando el ``ComparisonResult`` incluye los resultados completos de cada método
    (``bisection_result`` / ``newton_result``), se usan los sub-presenters para generar
    los dicts de iteración detallados que necesita la UI de comparación.

    Retorna un dict con las claves:

      - ``metrics`` – instantáneas de métricas por método::

            {
              "Bisección": {"root": …, "iterations": …, "error": …, "converged": …},
              "Newton-Raphson": {"root": …, "iterations": …, "error": …, "converged": …},
            }

      - ``session`` – dict que puede volcarse en ``st.session_state`` con las claves
        que la UI de comparación lee (``iters_bis``, ``iters_nwt``, ``raiz_bis``,
        ``raiz_nwt``, ``conv_bis``, ``conv_nwt``, ``metodo_activo``, ``ejecutado``).
    """
    # Generar dicts de iteración detallados usando los sub-presenters
    if result.bisection_result is not None:
        bis_presenter = present_bisection_result(result.bisection_result)
        bis_iterations = bis_presenter["iterations"]
    else:
        bis_iterations = []

    if result.newton_result is not None:
        nwt_presenter = present_newton_result(result.newton_result)
        nwt_iterations = nwt_presenter["iterations"]
    else:
        nwt_iterations = []

    # Métricas escalares por método
    metrics = {}
    for summary in (result.bisection, result.newton):
        metrics[summary.method_name] = {
            "root": summary.root,
            "iterations": summary.iterations_count,
            "error": summary.final_error,
            "converged": summary.converged,
            "error_message": summary.error_message,
        }

    # Payload de sesión — claves que lee la UI de comparación en app.py
    session = {
        "iters_bis": bis_iterations,
        "iters_nwt": nwt_iterations,
        "raiz_bis": result.bisection.root,
        "raiz_nwt": result.newton.root,
        "conv_bis": result.bisection.converged,
        "conv_nwt": result.newton.converged,
        "metodo_activo": "Comparación",
        "ejecutado": True,
    }

    return {
        "metrics": metrics,
        "session": session,
    }

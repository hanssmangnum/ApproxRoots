# metodos/newton.py

"""Wrapper legacy de compatibilidad alrededor del solver de dominio nuevo.

Retorna la tupla antigua ``(iteraciones, raiz, convergio)`` de dicts planos para
que el modo Comparación y app.py sigan funcionando sin cambios.
"""

from domain.models.newton import NewtonConfig
from domain.solvers.newton import solve_newton


def newton_raphson(f, df, x0: float, tol: float = 1e-6, max_iter: int = 100):
    """
    Wrapper legacy — delega en el solver de dominio puro y convierte
    el resultado tipificado de vuelta a ``(list[dict], root, converged)``.

    Parámetros:
        f        : función evaluable (resultado de lambdify)
        df       : derivada de f (resultado de lambdify)
        x0       : valor inicial
        tol      : tolerancia de error deseada
        max_iter : número máximo de iteraciones

    Retorna:
        iteraciones : lista de dicts con el estado de cada paso
        raiz        : aproximación final de la raíz
        convergio   : bool indicando si se cumplió la tolerancia

    Raises:
        ValueError : si la derivada es cero, el evaluador produce
                     valores no finitos, o la expresión no pudo compilarse.
    """
    config = NewtonConfig(x0=x0, tolerance=tol, max_iterations=max_iter)
    result = solve_newton(f, df, config)

    if result.status == "derivative_zero":
        raise ValueError(
            result.error_message
            or f"La derivada es prácticamente cero en x = {x0:.6f}."
        )
    if result.status == "non_finite":
        raise ValueError(
            result.error_message or "La función produjo valores no finitos."
        )
    if result.status == "parse_error":
        raise ValueError(
            result.error_message or "Error de compilación de la expresión."
        )

    # Convertir iteraciones tipificadas a dicts legacy
    iters = [
        {
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
        }
        for it in result.iterations
    ]

    return iters, result.root, result.converged

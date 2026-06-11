# metodos/biseccion.py

"""Wrapper legacy de compatibilidad alrededor del solver de dominio nuevo.

Retorna la tupla antigua ``(iters, raiz, convergio)`` de dicts planos para que
el modo Comparación y Newton-Raphson sigan funcionando sin cambios.
"""

from domain.models.bisection import SolverConfig
from domain.solvers.bisection import solve_bisection


def biseccion(f, a: float, b: float, tol: float = 1e-6, max_iter: int = 100):
    """
    Wrapper legacy — delega en el solver de dominio puro y convierte
    el resultado tipificado de vuelta a ``(list[dict], root, converged)``.

    Parámetros:
        f        : función evaluable (resultado de lambdify)
        a, b     : extremos del intervalo inicial
        tol      : tolerancia de error deseada
        max_iter : número máximo de iteraciones

    Retorna:
        iteraciones : lista de dicts con el estado de cada paso
        raiz        : aproximación final de la raíz
        convergio   : bool indicando si se cumplió la tolerancia

    Raises:
        ValueError : si el intervalo no cambia de signo o el evaluador
                     produce valores no finitos.
    """
    config = SolverConfig(a=a, b=b, tolerance=tol, max_iterations=max_iter)
    result = solve_bisection(f, config)

    if result.status == "invalid_bracket":
        raise ValueError(result.error_message or "El intervalo no cambia de signo.")
    if result.status == "non_finite":
        raise ValueError(result.error_message or "La función produjo valores no finitos.")
    if result.status == "parse_error":
        raise ValueError(result.error_message or "Error de compilación de la expresión.")

    # Convertir iteraciones tipificadas a dicts legacy
    iters = [
        {
            "iteracion": it.iteration,
            "a"        : it.a,
            "b"        : it.b,
            "xm"       : it.midpoint,
            "f(xm)"    : it.f_midpoint,
            "error_abs": it.error_abs,
            "error_rel": it.error_rel,
        }
        for it in result.iterations
    ]

    return iters, result.root, result.converged

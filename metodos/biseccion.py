# metodos/biseccion.py

import numpy as np
from utils.func_parser import validar_evaluacion


def biseccion(f, a: float, b: float, tol: float = 1e-6, max_iter: int = 100):
    """
    Método de bisección para aproximación de raíces.

    Parámetros:
        f        : función evaluable (resultado de lambdify)
        a, b     : extremos del intervalo inicial
        tol      : tolerancia de error deseada
        max_iter : número máximo de iteraciones

    Retorna:
        iteraciones : lista de dicts con el estado de cada paso
        raiz        : aproximación final de la raíz
        convergio   : bool indicando si se cumplió la tolerancia
    """

    fa = validar_evaluacion(f, a, "a")
    fb = validar_evaluacion(f, b, "b")

    if fa * fb >= 0:
        raise ValueError(
            f"f(a) y f(b) deben tener signos opuestos.\n"
            f"f({a}) = {fa:.6f},  f({b}) = {fb:.6f}"
        )

    iteraciones = []
    xm_anterior = None
    convergio   = False

    for i in range(1, max_iter + 1):
        xm  = (a + b) / 2
        fxm = validar_evaluacion(f, xm, "xm")

        if xm_anterior is None:
            error_abs = abs(b - a) / 2
            error_rel = float("inf")
        else:
            error_abs = abs(xm - xm_anterior)
            error_rel = error_abs / abs(xm) if xm != 0 else float("inf")

        iteraciones.append({
            "iteracion"  : i,
            "a"          : a,
            "b"          : b,
            "xm"         : xm,
            "f(xm)"      : fxm,
            "error_abs"  : error_abs,
            "error_rel"  : error_rel,
        })

        if error_abs <= tol or abs(fxm) <= tol:
            convergio = True
            break

        fa = validar_evaluacion(f, a, "a")
        if fa * fxm < 0:
            b = xm
        else:
            a = xm

        xm_anterior = xm

    return iteraciones, xm, convergio
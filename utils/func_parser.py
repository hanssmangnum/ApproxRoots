# utils/parser.py

import sympy as sp
import numpy as np

def parsear_funcion(texto: str):
    x = sp.Symbol('x')
    try:
        expr = sp.sympify(texto, locals={"x": x})
    except Exception:
        raise ValueError(f"No se pudo interpretar la función: '{texto}'. Verifica la sintaxis.")
    if not expr.free_symbols.issubset({x}):
        raise ValueError("La función solo puede contener la variable 'x'.")
    d_expr = sp.diff(expr, x)
    try:
        f  = sp.lambdify(x, expr,  modules=["numpy"])
        df = sp.lambdify(x, d_expr, modules=["numpy"])
    except Exception:
        raise ValueError("No se pudo convertir la función a forma numérica.")
    return f, df, expr, d_expr


def validar_evaluacion(f, valor: float, nombre: str = "x"):
    try:
        resultado = float(f(valor))
    except Exception:
        raise ValueError(f"La función no pudo evaluarse en {nombre} = {valor}.")
    if np.isnan(resultado) or np.isinf(resultado):
        raise ValueError(f"La función produce un valor no válido en {nombre} = {valor} (NaN o infinito).")
    return resultado
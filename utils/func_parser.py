# utils/parser.py

import sympy as sp
import numpy as np

def parsear_funcion(texto: str):
    """Parse function and derivative (legacy API for Newton-Raphson)."""
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
    """Evaluate *f* at *valor* and validate result is finite.

    Retained for legacy compatibility (metodos/biseccion.py wrapper).
    """
    try:
        resultado = float(f(valor))
    except Exception:
        raise ValueError(f"La función no pudo evaluarse en {nombre} = {valor}.")
    if np.isnan(resultado) or np.isinf(resultado):
        raise ValueError(f"La función produce un valor no válido en {nombre} = {valor} (NaN o infinito).")
    return resultado


def compile_expression(texto: str):
    """Compile a user expression into a callable evaluator.

    This is the bisection-only entry point — no derivative, no sign checks,
    no interval validation. Returns a callable ``float -> float`` or raises
    ``ValueError`` on invalid syntax.
    """
    x = sp.Symbol("x")
    try:
        expr = sp.sympify(texto, locals={"x": x})
    except Exception:
        raise ValueError(
            f"No se pudo interpretar la función: '{texto}'. Verifica la sintaxis."
        )
    if not expr.free_symbols.issubset({x}):
        raise ValueError("La función solo puede contener la variable 'x'.")
    try:
        f = sp.lambdify(x, expr, modules=["numpy"])
    except Exception:
        raise ValueError("No se pudo convertir la función a forma numérica.")
    return f
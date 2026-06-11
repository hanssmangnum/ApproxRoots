# utils/parser.py

import sympy as sp
import numpy as np

def parsear_funcion(texto: str):
    """Compila función y derivada (API legacy para Newton-Raphson)."""
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
    """Evalúa *f* en *valor* y valida que el resultado sea finito.

    Se conserva para compatibilidad legacy (metodos/biseccion.py).
    """
    try:
        resultado = float(f(valor))
    except Exception:
        raise ValueError(f"La función no pudo evaluarse en {nombre} = {valor}.")
    if np.isnan(resultado) or np.isinf(resultado):
        raise ValueError(f"La función produce un valor no válido en {nombre} = {valor} (NaN o infinito).")
    return resultado


def compile_with_derivative(texto: str):
    """Compila *texto* y retorna un par de callables ``(f, df)``.

    Este es el punto de entrada para Newton / comparación — compila tanto la
    función como su derivada simbólica en una sola pasada. Retorna
    ``(f_callable, df_callable)`` o lanza ``ValueError``.

    Los callables retornados son independientes de la cadena de expresión
    original y pueden pasarse a cualquier solver o caso de uso.
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
    d_expr = sp.diff(expr, x)
    try:
        f = sp.lambdify(x, expr, modules=["numpy"])
        df = sp.lambdify(x, d_expr, modules=["numpy"])
    except Exception:
        raise ValueError("No se pudo convertir la función a forma numérica.")
    return f, df


def compile_expression(texto: str):
    """Compila una expresión de usuario en un evaluador callable.

    Este es el punto de entrada solo para bisección — sin derivada, sin
    verificación de signos, sin validación de intervalo. Retorna un callable
    ``float -> float`` o lanza ``ValueError`` en sintaxis inválida.
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
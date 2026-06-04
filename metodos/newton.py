import numpy as np
from utils.func_parser import validar_evaluacion
 
 
def newton_raphson(f, df, x0: float, tol: float = 1e-6, max_iter: int = 100):
    """
    Método de Newton-Raphson para aproximación de raíces.
 
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
    """
 
    iteraciones = []
    x = x0
    convergio = False
 
    for i in range(1, max_iter + 1):
        fx  = validar_evaluacion(f,  x, f"x_{i-1}")
        dfx = validar_evaluacion(df, x, f"x'_{i-1}")
 
        if abs(dfx) < 1e-14:
            raise ValueError(
                f"La derivada es prácticamente cero en x = {x:.6f}.\n"
                f"El método de Newton-Raphson no puede continuar (división por cero)."
            )
 
        x_nuevo = x - fx / dfx
 
        error_abs = abs(x_nuevo - x)
        error_rel = error_abs / abs(x_nuevo) if x_nuevo != 0 else float("inf")
 
        # Pendiente e intercepto de la recta tangente: y = fx + dfx*(t - x)
        # Guardamos para graficar la tangente en la UI
        tangente = {
            "pendiente"  : dfx,
            "intercepto" : fx - dfx * x,   # b en y = m*t + b
            "x_tangente" : x,               # punto de tangencia
        }
 
        iteraciones.append({
            "iteracion"  : i,
            "x_anterior" : x,
            "x_nuevo"    : x_nuevo,
            "f(x)"       : fx,
            "f'(x)"      : dfx,
            "error_abs"  : error_abs,
            "error_rel"  : error_rel,
            "tangente"   : tangente,
        })
 
        x = x_nuevo
 
        if error_abs <= tol or abs(validar_evaluacion(f, x, "x")) <= tol:
            convergio = True
            break
 
    return iteraciones, x, convergio
 
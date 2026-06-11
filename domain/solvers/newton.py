# domain/solvers/newton.py

"""Solver de Newton-Raphson puro, sin imports del parser ni de la capa de UI."""

from typing import Callable
import numpy as np

from domain.models.newton import (
    NewtonConfig,
    NewtonIteration,
    NewtonResult,
)


def _safe_evaluate(
    evaluator: Callable[[float], float],
    x: float,
    label: str,
) -> float:
    """Evalúa *evaluator* en *x* y rechaza resultados no finitos."""
    try:
        val = float(evaluator(x))
    except Exception:
        raise ValueError(
            f"El evaluador lanzó una excepción en {label} = {x}."
        )
    if not np.isfinite(val):
        raise ValueError(
            f"El evaluador devolvió un valor no finito ({val}) en {label} = {x}."
        )
    return val


def solve_newton(
    f: Callable[[float], float],
    df: Callable[[float], float],
    config: NewtonConfig,
) -> NewtonResult:
    """Ejecuta el método numérico de Newton-Raphson.

    Parámetros
    ----------
    f :
        Un callable ``float -> float`` para la función.
    df :
        Un callable ``float -> float`` para la derivada de *f*.
    config :
        Punto inicial numérico y configuración de convergencia.

    Retorna
    -------
    NewtonResult
        Resultado tipificado con registros de iteración, raíz y estado.
    """
    x = config.x0
    iterations: list[NewtonIteration] = []

    for i in range(1, config.max_iterations + 1):
        # ── Evaluate f(x) and f'(x) ──────────────────────────────────
        try:
            fx = _safe_evaluate(f, x, f"x_{i-1}")
            dfx = _safe_evaluate(df, x, f"x'_{i-1}")
        except ValueError as exc:
            return NewtonResult(
                iterations=[],
                root=None,
                converged=False,
                status="non_finite",
                error_message=str(exc),
            )

        # ── Check for zero derivative ────────────────────────────────
        if abs(dfx) < 1e-14:
            return NewtonResult(
                iterations=iterations,
                root=None,
                converged=False,
                status="derivative_zero",
            error_message=(
                f"La derivada es prácticamente cero en x = {x:.6f}.\n"
                f"Newton-Raphson no puede continuar (división por cero)."
            ),
            )

        # ── Newton step ──────────────────────────────────────────────
        x_next = x - fx / dfx

        error_abs = abs(x_next - x)
        error_rel = error_abs / abs(x_next) if x_next != 0.0 else float("inf")

        # Tangent line: y = fx + dfx * (t - x) → y = m*t + b
        # m = dfx, b = fx - dfx * x
        tangent_slope = dfx
        tangent_intercept = fx - dfx * x

        iterations.append(NewtonIteration(
            iteration=i,
            x_previous=x,
            x_next=x_next,
            f_x=fx,
            df_x=dfx,
            error_abs=error_abs,
            error_rel=error_rel,
            tangent_slope=tangent_slope,
            tangent_intercept=tangent_intercept,
        ))

        x = x_next

        # ── Check for non-finite new value ──────────────────────────
        if not np.isfinite(x):
            return NewtonResult(
                iterations=iterations,
                root=None,
                converged=False,
                status="non_finite",
                error_message=f"El paso de Newton produjo un valor no finito: {x}.",
            )

        # ── Convergence check ────────────────────────────────────────
        try:
            fx_next = _safe_evaluate(f, x, "x")
        except ValueError as exc:
            return NewtonResult(
                iterations=iterations,
                root=x,
                converged=False,
                status="non_finite",
                error_message=str(exc),
            )

        if error_abs <= config.tolerance or abs(fx_next) <= config.tolerance:
            return NewtonResult(
                iterations=iterations,
                root=x,
                converged=True,
                status="success",
            )

    # Reached max iterations without convergence
    return NewtonResult(
        iterations=iterations,
        root=x,
        converged=False,
        status="max_iterations",
        error_message=(
            f"No convergió en {config.max_iterations} iteraciones. "
            f"Última aproximación: x = {x:.8f}."
        ),
    )

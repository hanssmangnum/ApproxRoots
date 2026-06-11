# domain/solvers/bisection.py

"""Solver de bisección puro, sin imports del parser ni de la capa de UI."""

from typing import Callable
import numpy as np

from domain.models.bisection import (
    SolverConfig,
    BisectionIteration,
    BisectionResult,
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


def solve_bisection(
    evaluator: Callable[[float], float],
    config: SolverConfig,
) -> BisectionResult:
    """Ejecuta el método numérico de bisección.

    Parámetros
    ----------
    evaluator :
        Un callable ``float -> float`` producido por un parser de expresiones.
    config :
        Intervalo numérico y configuración de convergencia.

    Retorna
    -------
    BisectionResult
        Resultado tipificado con registros de iteración, raíz y estado.
    """
    # ── Validate bracket ──────────────────────────────────────────────
    try:
        fa = _safe_evaluate(evaluator, config.a, "a")
        fb = _safe_evaluate(evaluator, config.b, "b")
    except ValueError as exc:
        return BisectionResult(
            iterations=[],
            root=None,
            converged=False,
            status="non_finite",
            error_message=str(exc),
        )

    # ── Boundary root check ───────────────────────────────────────────
    if fa == 0.0:
        return BisectionResult(
            iterations=[],
            root=config.a,
            converged=True,
            status="success",
        )
    if fb == 0.0:
        return BisectionResult(
            iterations=[],
            root=config.b,
            converged=True,
            status="success",
        )

    if fa * fb >= 0:
        return BisectionResult(
            iterations=[],
            root=None,
            converged=False,
            status="invalid_bracket",
            error_message=(
                f"f(a) y f(b) deben tener signos opuestos.\n"
                f"f({config.a}) = {fa:.6f},  f({config.b}) = {fb:.6f}"
            ),
        )

    # ── Main loop ─────────────────────────────────────────────────────
    a, b = config.a, config.b
    iterations: list[BisectionIteration] = []
    xm_previous: float | None = None

    for i in range(1, config.max_iterations + 1):
        xm = (a + b) / 2.0

        try:
            fxm = _safe_evaluate(evaluator, xm, "xm")
        except ValueError as exc:
            return BisectionResult(
                iterations=[],
                root=None,
                converged=False,
                status="non_finite",
                error_message=str(exc),
            )

        if xm_previous is None:
            error_abs = abs(b - a) / 2.0
            error_rel = float("inf")
        else:
            error_abs = abs(xm - xm_previous)
            error_rel = error_abs / abs(xm) if xm != 0.0 else float("inf")

        iterations.append(BisectionIteration(
            iteration=i,
            a=a,
            b=b,
            midpoint=xm,
            f_midpoint=fxm,
            error_abs=error_abs,
            error_rel=error_rel,
        ))

        if error_abs <= config.tolerance or abs(fxm) <= config.tolerance:
            return BisectionResult(
                iterations=iterations,
                root=xm,
                converged=True,
                status="success",
            )

        # Update interval for next iteration
        fa = fa if a == config.a else _safe_evaluate(evaluator, a, "a")
        if fa * fxm < 0:
            b = xm
        else:
            a = xm

        xm_previous = xm

    # Reached max iterations without convergence
    return BisectionResult(
        iterations=iterations,
        root=xm,
        converged=False,
        status="max_iterations",
        error_message=f"No convergió en {config.max_iterations} iteraciones.",
    )

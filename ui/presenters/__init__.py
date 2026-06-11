# ui/presenters/__init__.py

from .bisection_presenter import present_bisection_result
from .newton_presenter import present_newton_result
from .comparison_presenter import present_comparison_result
from .chart_presenters import (
    build_bisection_chart_vm,
    build_newton_chart_vm,
    build_convergence_chart_vm,
    build_function_chart_vm,
    build_comparison_series,
)

__all__ = [
    "present_bisection_result",
    "present_newton_result",
    "present_comparison_result",
    "build_bisection_chart_vm",
    "build_newton_chart_vm",
    "build_convergence_chart_vm",
    "build_function_chart_vm",
    "build_comparison_series",
]

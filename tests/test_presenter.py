"""Pruebas del presenter — mapeo dominio→UI sin Streamlit."""

import math
from domain.models.bisection import (
    BisectionResult,
    BisectionIteration,
)
from domain.models.newton import (
    NewtonResult,
    NewtonIteration,
)
from ui.presenters.bisection_presenter import present_bisection_result
from ui.presenters.newton_presenter import present_newton_result


def _sample_success_result():
    return BisectionResult(
        iterations=[
            BisectionIteration(1, 1.0, 2.0, 1.5, -0.875, 0.5, float("inf")),
            BisectionIteration(2, 1.5, 2.0, 1.75, 1.609375, 0.25, 0.142857),
            BisectionIteration(3, 1.5, 1.75, 1.625, 0.166015, 0.125, 0.076923),
        ],
        root=1.625,
        converged=True,
        status="success",
    )


class TestPresenterSuccess:
    """Mapeo de resultado exitoso."""

    def test_iterations_have_legacy_keys(self):
        """DADO un resultado exitoso del dominio
           CUANDO se llama a present_bisection_result
           ENTONCES las filas de iteración tienen claves legacy de dict."""
        data = present_bisection_result(_sample_success_result())

        for row in data["iterations"]:
            assert "iteracion" in row
            assert "a" in row
            assert "b" in row
            assert "xm" in row
            assert "f(xm)" in row
            assert "error_abs" in row
            assert "error_rel" in row

    def test_iteration_count_matches(self):
        """DADO un resultado bisection con 3 iteraciones
           CUANDO se presenta
           ENTONCES se producen 3 filas."""
        data = present_bisection_result(_sample_success_result())
        assert len(data["iterations"]) == 3

    def test_metrics_dict(self):
        """DADO un resultado exitoso
           CUANDO se presenta
           ENTONCES metrics contiene las claves esperadas."""
        data = present_bisection_result(_sample_success_result())
        assert data["metrics"]["root"] == 1.625
        assert data["metrics"]["iterations_count"] == 3
        assert data["metrics"]["converged"] is True
        assert math.isfinite(data["metrics"]["final_error"])

    def test_session_payload(self):
        """DADO un resultado exitoso
           CUANDO se presenta
           ENTONCES el payload de sesión tiene las claves que app.py espera."""
        data = present_bisection_result(_sample_success_result())
        assert "iteraciones" in data["session"]
        assert "raiz" in data["session"]
        assert "convergio" in data["session"]
        assert data["session"]["raiz"] == 1.625
        assert data["session"]["convergio"] is True


class TestPresenterFailure:
    """Mapeo de resultado no exitoso."""

    def test_empty_iterations_on_failure(self):
        """DADO un resultado fallido sin iteraciones
           CUANDO se presenta
           ENTONCES se retorna una lista de iteraciones vacía."""
        result = BisectionResult(
            iterations=[],
            root=None,
            converged=False,
            status="invalid_bracket",
            error_message="No sign change",
        )
        data = present_bisection_result(result)
        assert len(data["iterations"]) == 0
        assert data["session"]["raiz"] is None
        assert data["session"]["convergio"] is False

    def test_metrics_nan_on_empty_result(self):
        """DADO un resultado fallido sin iteraciones
           CUANDO se presenta
           ENTONCES final_error es NaN."""
        result = BisectionResult(
            iterations=[],
            root=None,
            converged=False,
            status="invalid_bracket",
            error_message="No sign change",
        )
        data = present_bisection_result(result)
        assert math.isnan(data["metrics"]["final_error"])


class TestPresenterZeroIterations:
    """Resultado exitoso con cero iteraciones (raíz en un límite)."""

    def _make_boundary_result(self, root: float) -> BisectionResult:
        return BisectionResult(
            iterations=[],
            root=root,
            converged=True,
            status="success",
        )

    def test_empty_iterations_list(self):
        """DADO un éxito con raíz en el límite
           CUANDO se presenta
           ENTONCES la lista de iteraciones está vacía."""
        result = self._make_boundary_result(0.0)
        data = present_bisection_result(result)
        assert len(data["iterations"]) == 0

    def test_metrics_for_boundary_root(self):
        """DADO un éxito con raíz en el límite
           CUANDO se presenta
           ENTONCES final_error es NaN (sin iteraciones de donde derivar el error)."""
        result = self._make_boundary_result(2.0)
        data = present_bisection_result(result)
        assert data["metrics"]["root"] == 2.0
        assert data["metrics"]["iterations_count"] == 0
        assert data["metrics"]["converged"] is True
        assert math.isnan(data["metrics"]["final_error"])

    def test_session_payload_for_boundary_root(self):
        """DADO un éxito con raíz en el límite
           CUANDO se presenta
           ENTONCES el payload de sesión tiene iteraciones vacías y raiz correcta."""
        result = self._make_boundary_result(-1.0)
        data = present_bisection_result(result)
        assert data["session"]["iteraciones"] == []
        assert data["session"]["raiz"] == -1.0
        assert data["session"]["convergio"] is True


# ═════════════════════════════════════════════════════════════════════════════
# Newton presenter tests
# ═════════════════════════════════════════════════════════════════════════════


def _newton_success_result():
    return NewtonResult(
        iterations=[
            NewtonIteration(1, 3.0, 1.8333, 5.0, 6.0, 1.1667, 0.6364, 6.0, -13.0),
            NewtonIteration(2, 1.8333, 2.0069, -0.6392, 3.6667, 0.1736, 0.0865, 3.6667, -7.3583),
            NewtonIteration(3, 2.0069, 2.0000, 0.0276, 4.0138, 0.0069, 0.0035, 4.0138, -8.0247),
        ],
        root=2.0000,
        converged=True,
        status="success",
    )


class TestNewtonPresenterSuccess:
    """Mapeo de resultado exitoso de Newton."""

    def test_iterations_have_legacy_keys(self):
        """DADO un resultado exitoso de Newton del dominio
           CUANDO se llama a present_newton_result
           ENTONCES las filas de iteración tienen claves legacy de dict."""
        data = present_newton_result(_newton_success_result())

        for row in data["iterations"]:
            assert "iteracion" in row
            assert "x_anterior" in row
            assert "x_nuevo" in row
            assert "f(x)" in row
            assert "f'(x)" in row
            assert "error_abs" in row
            assert "error_rel" in row
            assert "tangente" in row
            assert "pendiente" in row["tangente"]
            assert "intercepto" in row["tangente"]
            assert "x_tangente" in row["tangente"]

    def test_iteration_count_matches(self):
        """DADO un resultado Newton con 3 iteraciones
           CUANDO se presenta
           ENTONCES se producen 3 filas."""
        data = present_newton_result(_newton_success_result())
        assert len(data["iterations"]) == 3

    def test_metrics_dict(self):
        """DADO un resultado exitoso de Newton
           CUANDO se presenta
           ENTONCES metrics contiene las claves esperadas."""
        data = present_newton_result(_newton_success_result())
        assert data["metrics"]["root"] == 2.0
        assert data["metrics"]["iterations_count"] == 3
        assert data["metrics"]["converged"] is True
        assert math.isfinite(data["metrics"]["final_error"])

    def test_session_payload(self):
        """DADO un resultado exitoso de Newton
           CUANDO se presenta
           ENTONCES el payload de sesión tiene las claves que app.py espera."""
        data = present_newton_result(_newton_success_result())
        assert "iteraciones" in data["session"]
        assert "raiz" in data["session"]
        assert "convergio" in data["session"]
        assert data["session"]["raiz"] == 2.0
        assert data["session"]["convergio"] is True


class TestNewtonPresenterFailure:
    """Mapeo de resultado no exitoso de Newton."""

    def test_empty_iterations_on_failure(self):
        """DADO un resultado fallido de Newton sin iteraciones
           CUANDO se presenta
           ENTONCES se retorna una lista de iteraciones vacía."""
        result = NewtonResult(
            iterations=[],
            root=None,
            converged=False,
            status="derivative_zero",
            error_message="Derivative is zero",
        )
        data = present_newton_result(result)
        assert len(data["iterations"]) == 0
        assert data["session"]["raiz"] is None
        assert data["session"]["convergio"] is False

    def test_metrics_nan_on_empty_result(self):
        """DADO un resultado fallido de Newton sin iteraciones
           CUANDO se presenta
           ENTONCES final_error es NaN."""
        result = NewtonResult(
            iterations=[],
            root=None,
            converged=False,
            status="derivative_zero",
            error_message="Derivative is zero",
        )
        data = present_newton_result(result)
        assert math.isnan(data["metrics"]["final_error"])


class TestNewtonPresenterMaxIterations:
    """Resultado de máximas iteraciones — iteraciones parciales pero sin convergencia."""

    def _make_max_iter_result(self):
        return NewtonResult(
            iterations=[
                NewtonIteration(1, 3.0, 1.8333, 5.0, 6.0, 1.1667, 0.6364, 6.0, -13.0),
            ],
            root=1.8333,
            converged=False,
            status="max_iterations",
            error_message="Did not converge within limit.",
        )

    def test_partial_iterations_returned(self):
        """DADO un resultado max_iterations con iteraciones parciales
           CUANDO se presenta
           ENTONCES las iteraciones aún se retornan."""
        data = present_newton_result(self._make_max_iter_result())
        assert len(data["iterations"]) == 1
        assert data["session"]["raiz"] == 1.8333
        assert data["session"]["convergio"] is False

    def test_metrics_nan_on_max_iterations(self):
        """DADO un resultado max_iterations
           CUANDO se presenta
           ENTONCES final_error es NaN (no es un resultado exitoso)."""
        data = present_newton_result(self._make_max_iter_result())
        assert math.isnan(data["metrics"]["final_error"])


# ═════════════════════════════════════════════════════════════════════════════
# Comparison presenter tests
# ═════════════════════════════════════════════════════════════════════════════

from domain.models.comparison import (  # noqa: E402
    ComparisonRequest,
    ComparisonResult,
    MethodSummary,
)
from ui.presenters.comparison_presenter import present_comparison_result  # noqa: E402


def _comparison_both_success():
    return ComparisonResult(
        bisection=MethodSummary(
            method_name="Bisección",
            root=1.521379,
            converged=True,
            iterations_count=20,
            final_error=5.7e-7,
            error_message=None,
        ),
        newton=MethodSummary(
            method_name="Newton-Raphson",
            root=2.0,
            converged=True,
            iterations_count=6,
            final_error=3.2e-9,
            error_message=None,
        ),
        expression="x**2 - 4",
        status="success",
    )


def _comparison_one_fails():
    return ComparisonResult(
        bisection=MethodSummary(
            method_name="Bisección",
            root=1.521379,
            converged=True,
            iterations_count=20,
            final_error=5.7e-7,
            error_message=None,
        ),
        newton=MethodSummary(
            method_name="Newton-Raphson",
            root=None,
            converged=False,
            iterations_count=0,
            final_error=None,
            error_message="Derivative is zero",
        ),
        expression="x**2 - 4",
        status="success",
    )


class TestComparisonPresenter:
    """Mapeo de resultado de comparación → dict de UI."""

    def test_metrics_contains_both_methods(self):
        """DADO un resultado de comparación con ambos métodos exitosos
           CUANDO se llama a present_comparison_result
           ENTONCES el dict metrics tiene entradas para ambos métodos."""
        data = present_comparison_result(_comparison_both_success())
        assert "Bisección" in data["metrics"]
        assert "Newton-Raphson" in data["metrics"]

    def test_metrics_values(self):
        """DADO un resultado de comparación
           CUANDO se presenta
           ENTONCES las métricas escalares coinciden con los datos fuente."""
        data = present_comparison_result(_comparison_both_success())

        b = data["metrics"]["Bisección"]
        assert b["root"] == 1.521379
        assert b["iterations"] == 20
        assert b["converged"] is True

        n = data["metrics"]["Newton-Raphson"]
        assert n["root"] == 2.0
        assert n["iterations"] == 6
        assert n["converged"] is True

    def test_one_method_failure(self):
        """DADO un resultado de comparación con Newton fallando
           CUANDO se presenta
           ENTONCES las métricas de Newton muestran el error y bisección está intacta."""
        data = present_comparison_result(_comparison_one_fails())

        b = data["metrics"]["Bisección"]
        assert b["root"] == 1.521379
        assert b["converged"] is True

        n = data["metrics"]["Newton-Raphson"]
        assert n["root"] is None
        assert n["converged"] is False
        assert n["error_message"] == "Derivative is zero"

    def test_chart_data_present(self):
        """DADO un resultado de comparación
           CUANDO se presenta
           ENTONCES chart_data contiene las claves bisection y newton."""
        data = present_comparison_result(_comparison_both_success())
        assert "bisection" in data["chart_data"]
        assert "newton" in data["chart_data"]

    def test_combined_series(self):
        """DADO un resultado de comparación
           CUANDO se presenta
           ENTONCES combined_series tiene entradas para ambos métodos."""
        data = present_comparison_result(_comparison_both_success())
        assert len(data["combined_series"]) == 2
        methods = {entry["method"] for entry in data["combined_series"]}
        assert methods == {"Bisección", "Newton-Raphson"}

    def test_session_payload(self):
        """DADO un resultado de comparación
           CUANDO se presenta
           ENTONCES el payload de sesión tiene las claves esperadas."""
        data = present_comparison_result(_comparison_both_success())
        assert "bisection_metrics" in data["session"]
        assert "newton_metrics" in data["session"]
        assert "comparison_chart_data" in data["session"]


# ═════════════════════════════════════════════════════════════════════════════
# Chart view-model tests
# ═════════════════════════════════════════════════════════════════════════════

from ui.view_models import (  # noqa: E402
    BisectionChartVM,
    NewtonChartVM,
    ConvergenceChartVM,
    FunctionChartVM,
)


class TestBisectionChartVM:
    """Construcción de BisectionChartVM."""

    def test_frozen_dataclass(self):
        """DADO un callable de función y un dict de iteración
           CUANDO se construye un BisectionChartVM
           ENTONCES tiene los campos esperados."""
        fn = lambda x: x**2 - 4
        iteration = {"a": 1.0, "b": 3.0, "xm": 2.0, "iteracion": 1}
        vm = BisectionChartVM(
            function_callable=fn,
            iteration=iteration,
            a=iteration["a"],
            b=iteration["b"],
            xm=iteration["xm"],
        )
        assert vm.a == 1.0
        assert vm.b == 3.0
        assert vm.xm == 2.0
        assert vm.function_callable(2.0) == 0.0


class TestNewtonChartVM:
    """Construcción de NewtonChartVM."""

    def test_frozen_dataclass(self):
        """DADO un callable de función y un dict de iteración
           CUANDO se construye un NewtonChartVM
           ENTONCES tiene los campos esperados."""
        fn = lambda x: x**2 - 4
        tangent = {"pendiente": 4.0, "intercepto": -8.0, "x_tangente": 2.0}
        iteration = {
            "x_anterior": 3.0, "x_nuevo": 2.1667,
            "tangente": tangent,
            "iteracion": 1,
        }
        vm = NewtonChartVM(
            function_callable=fn,
            iteration=iteration,
            x_previous=iteration["x_anterior"],
            x_next=iteration["x_nuevo"],
            tangent=tangent,
        )
        assert vm.x_previous == 3.0
        assert vm.x_next == 2.1667
        assert vm.tangent["pendiente"] == 4.0


class TestConvergenceChartVM:
    """Construcción de ConvergenceChartVM."""

    def test_series_and_title(self):
        """DADO una lista de dicts de iteración
           CUANDO se construye un ConvergenceChartVM
           ENTONCES series y title se almacenan."""
        series = [
            {"iteration": 1, "error_abs": 1.0},
            {"iteration": 2, "error_abs": 0.5},
        ]
        vm = ConvergenceChartVM(series=series, title="Newton-Raphson")
        assert len(vm.series) == 2
        assert vm.title == "Newton-Raphson"
        assert vm.series[0]["error_abs"] == 1.0


class TestFunctionChartVM:
    """Construcción de FunctionChartVM."""

    def test_with_root(self):
        """DADO un callable, rango y raíz
           CUANDO se construye un FunctionChartVM
           ENTONCES todos los campos se almacenan."""
        fn = lambda x: x**2 - 4
        vm = FunctionChartVM(
            function_callable=fn,
            x_min=0.0,
            x_max=4.0,
            root=2.0,
            title="f(x)",
        )
        assert vm.root == 2.0
        assert vm.function_callable(vm.root) == 0.0

    def test_without_root(self):
        """DADO un callable sin raíz
           CUANDO se construye un FunctionChartVM
           ENTONCES root es None."""
        fn = lambda x: x**2 + 1
        vm = FunctionChartVM(
            function_callable=fn,
            x_min=-2.0,
            x_max=2.0,
            root=None,
            title="No root",
        )
        assert vm.root is None


# ═════════════════════════════════════════════════════════════════════════════
# Chart presenter tests
# ═════════════════════════════════════════════════════════════════════════════

from utils.graficas import (  # noqa: E402
    graficar_funcion_vm,
    graficar_iteracion_biseccion_vm,
    graficar_iteracion_newton_vm,
    graficar_convergencia_vm,
)
from ui.presenters.chart_presenters import (  # noqa: E402
    build_bisection_chart_vm,
    build_newton_chart_vm,
    build_convergence_chart_vm,
    build_function_chart_vm,
    build_comparison_series,
)


class TestBuildBisectionChartVM:
    """Constructor build_bisection_chart_vm."""

    def test_builds_correct_vm(self):
        """DADO un callable y dict de iteración con claves a, b, xm
           CUANDO se llama a build_bisection_chart_vm
           ENTONCES se retorna un BisectionChartVM válido."""
        fn = lambda x: x**2 - 4
        iteration = {"a": 1.0, "b": 3.0, "xm": 2.0, "iteracion": 3, "error_abs": 0.5}
        vm = build_bisection_chart_vm(fn, iteration)
        assert isinstance(vm, BisectionChartVM)
        assert vm.a == 1.0
        assert vm.b == 3.0
        assert vm.xm == 2.0


class TestBuildNewtonChartVM:
    """Constructor build_newton_chart_vm."""

    def test_builds_correct_vm(self):
        """DADO un callable y dict de iteración con x_anterior, x_nuevo, tangente
           CUANDO se llama a build_newton_chart_vm
           ENTONCES se retorna un NewtonChartVM válido."""
        fn = lambda x: x**2 - 4
        tangent = {"pendiente": 4.0, "intercepto": -8.0, "x_tangente": 3.0}
        iteration = {
            "x_anterior": 3.0, "x_nuevo": 2.1667,
            "tangente": tangent,
            "iteracion": 1,
        }
        vm = build_newton_chart_vm(fn, iteration)
        assert isinstance(vm, NewtonChartVM)
        assert vm.x_previous == 3.0
        assert vm.x_next == 2.1667
        assert vm.tangent["pendiente"] == 4.0


class TestBuildConvergenceChartVM:
    """Constructor build_convergence_chart_vm."""

    def test_builds_series_from_iterations(self):
        """DADO una lista de dicts de iteración con iteracion y error_abs
           CUANDO se llama a build_convergence_chart_vm
           ENTONCES se retorna un ConvergenceChartVM con las series extraídas."""
        iterations = [
            {"iteracion": 1, "error_abs": 1.0},
            {"iteracion": 2, "error_abs": 0.1},
            {"iteracion": 3, "error_abs": 0.01},
        ]
        vm = build_convergence_chart_vm(iterations, metodo="Bisección")
        assert isinstance(vm, ConvergenceChartVM)
        assert vm.title == "Bisección"
        assert len(vm.series) == 3
        assert vm.series[0] == {"iteration": 1, "error_abs": 1.0}

    def test_empty_iterations(self):
        """DADO una lista de iteraciones vacía
           CUANDO se llama a build_convergence_chart_vm
           ENTONCES se retorna una serie vacía."""
        vm = build_convergence_chart_vm([], metodo="Newton-Raphson")
        assert vm.series == []


class TestBuildFunctionChartVM:
    """Constructor build_function_chart_vm."""

    def test_builds_with_root(self):
        """DADO un callable y raíz
           CUANDO se llama a build_function_chart_vm
           ENTONCES se retorna un FunctionChartVM con campos correctos."""
        fn = lambda x: x**2 - 4
        vm = build_function_chart_vm(fn, 0.0, 4.0, 2.0, titulo="Test")
        assert isinstance(vm, FunctionChartVM)
        assert vm.root == 2.0
        assert vm.x_min == 0.0
        assert vm.x_max == 4.0
        assert vm.title == "Test"

    def test_builds_without_root(self):
        """DADO un callable pero sin raíz
           CUANDO se llama a build_function_chart_vm
           ENTONCES root es None."""
        fn = lambda x: x**2 + 1
        vm = build_function_chart_vm(fn, -2.0, 2.0, None)
        assert vm.root is None


class TestBuildComparisonSeries:
    """Constructor build_comparison_series."""

    def test_both_series(self):
        """DADO listas de iteración de bisección y Newton
           CUANDO se llama a build_comparison_series
           ENTONCES ambas series normalizadas se retornan."""
        iters_bis = [
            {"iteracion": 1, "error_abs": 1.0},
            {"iteracion": 2, "error_abs": 0.5},
        ]
        iters_nwt = [
            {"iteracion": 1, "error_abs": 0.1},
        ]
        bis_series, nwt_series = build_comparison_series(iters_bis, iters_nwt)
        assert len(bis_series) == 2
        assert len(nwt_series) == 1
        assert bis_series[0]["iteration"] == 1
        assert bis_series[0]["error_abs"] == 1.0
        assert nwt_series[0]["error_abs"] == 0.1


# ═════════════════════════════════════════════════════════════════════════════
# graficas.py VM overload tests
# ═════════════════════════════════════════════════════════════════════════════


class TestGraficasVMOverloads:
    """Las funciones VM-aware en utils/graficas.py delegan correctamente."""

    def test_graficar_funcion_vm_returns_figure(self):
        """DADO un FunctionChartVM
           CUANDO se llama a graficar_funcion_vm
           ENTONCES se retorna una Figure de matplotlib."""
        fn = lambda x: x**2 - 4
        vm = FunctionChartVM(
            function_callable=fn,
            x_min=-3.0, x_max=3.0,
            root=2.0,
            title="f(x) = x² - 4",
        )
        fig = graficar_funcion_vm(vm)
        assert fig is not None
        import matplotlib.pyplot as plt
        plt.close(fig)

    def test_graficar_biseccion_vm_returns_figure(self):
        """DADO un BisectionChartVM
           CUANDO se llama a graficar_iteracion_biseccion_vm
           ENTONCES se retorna una Figure de matplotlib."""
        fn = lambda x: x**3 - x - 2
        iteration = {"a": 1.0, "b": 2.0, "xm": 1.5, "iteracion": 1,
                     "f(xm)": -0.875, "error_abs": 0.5, "error_rel": float("inf")}
        vm = BisectionChartVM(
            function_callable=fn,
            iteration=iteration,
            a=1.0, b=2.0, xm=1.5,
        )
        fig = graficar_iteracion_biseccion_vm(vm)
        assert fig is not None
        import matplotlib.pyplot as plt
        plt.close(fig)

    def test_graficar_newton_vm_returns_figure(self):
        """DADO un NewtonChartVM
           CUANDO se llama a graficar_iteracion_newton_vm
           ENTONCES se retorna una Figure de matplotlib."""
        fn = lambda x: x**2 - 4
        tangent = {"pendiente": 6.0, "intercepto": -13.0, "x_tangente": 3.0}
        iteration = {
            "x_anterior": 3.0, "x_nuevo": 2.1667, "tangente": tangent,
            "iteracion": 1, "f(x)": 5.0, "f'(x)": 6.0,
            "error_abs": 0.8333, "error_rel": 0.2778,
        }
        vm = NewtonChartVM(
            function_callable=fn,
            iteration=iteration,
            x_previous=3.0, x_next=2.1667,
            tangent=tangent,
        )
        fig = graficar_iteracion_newton_vm(vm)
        assert fig is not None
        import matplotlib.pyplot as plt
        plt.close(fig)

    def test_graficar_convergencia_vm_returns_figure(self):
        """DADO un ConvergenceChartVM
           CUANDO se llama a graficar_convergencia_vm
           ENTONCES se retorna una Figure de matplotlib."""
        series = [
            {"iteration": 1, "error_abs": 1.0},
            {"iteration": 2, "error_abs": 0.1},
            {"iteration": 3, "error_abs": 0.01},
        ]
        vm = ConvergenceChartVM(series=series, title="Bisección")
        fig = graficar_convergencia_vm(vm)
        assert fig is not None
        import matplotlib.pyplot as plt
        plt.close(fig)

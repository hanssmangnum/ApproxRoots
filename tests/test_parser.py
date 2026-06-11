"""Pruebas del parser — solo compilación, sin mezcla con solver o UI."""

import pytest
from utils.func_parser import compile_expression, compile_with_derivative, parsear_funcion


class TestCompileExpression:
    """Endpoint de compilación solo para bisección."""

    def test_valid_expression_returns_callable(self):
        """DADO una expresión sintácticamente válida
           CUANDO se llama a compile_expression
           ENTONCES retorna un evaluador callable."""
        f = compile_expression("x**3 - x - 2")
        assert callable(f)
        result = f(2.0)
        assert isinstance(result, (int, float))
        assert abs(result - 4.0) < 1e-10  # 2^3 - 2 - 2 = 4

    def test_invalid_syntax_raises_value_error(self):
        """DADO una expresión mal formada
           CUANDO se llama a compile_expression
           ENTONCES se lanza un ValueError."""
        with pytest.raises(ValueError, match="No se pudo interpretar"):
            compile_expression("x***2 +")

    def test_invalid_variable_raises_value_error(self):
        """DADO una expresión con variables no válidas
           CUANDO se llama a compile_expression
           ENTONCES se lanza un ValueError."""
        with pytest.raises(ValueError, match="solo puede contener"):
            compile_expression("y**2 + 1")

    def test_no_interval_validation(self):
        """PRUEBA que el parser NO hace validación de intervalo/signo —
           solo compila."""
        f = compile_expression("x**2 + 1")  # always positive
        assert callable(f)
        # Evaluar es trabajo del solver; el parser acepta cualquier expresión
        assert f(0.0) == 1.0


class TestParsearFuncion:
    """API legacy conservada para Newton-Raphson."""

    def test_returns_f_df_expr_d_expr(self):
        """DADO una expresión válida
           CUANDO se llama a parsear_funcion
           ENTONCES retorna una tupla de 4 con evaluadores y expresiones simbólicas."""
        f, df, expr, d_expr = parsear_funcion("x**2")
        assert callable(f)
        assert callable(df)
        assert abs(f(3.0) - 9.0) < 1e-10
        assert abs(df(3.0) - 6.0) < 1e-10


class TestCompileWithDerivative:
    """Endpoint de compilación con derivada para casos de uso de Newton / comparación."""

    def test_returns_f_and_df_callables(self):
        """DADO una expresión válida
           CUANDO se llama a compile_with_derivative
           ENTONCES retorna un par de callables (f, df)."""
        f, df = compile_with_derivative("x**2 - 4")
        assert callable(f)
        assert callable(df)
        assert abs(f(2.0) - 0.0) < 1e-10    # 2^2 - 4 = 0
        assert abs(df(2.0) - 4.0) < 1e-10   # 2*2 = 4
        assert abs(f(3.0) - 5.0) < 1e-10    # 3^2 - 4 = 5
        assert abs(df(3.0) - 6.0) < 1e-10   # 2*3 = 6

    def test_derivative_of_const(self):
        """DADO una expresión constante
           CUANDO se llama a compile_with_derivative
           ENTONCES df es cero."""
        f, df = compile_with_derivative("42")
        assert callable(f)
        assert callable(df)
        assert abs(f(10.0) - 42.0) < 1e-10
        assert abs(df(10.0) - 0.0) < 1e-10

    def test_derivative_of_polynomial(self):
        """DADO una expresión polinómica
           CUANDO se llama a compile_with_derivative
           ENTONCES df coincide con la derivada simbólica."""
        # d/dx of x**3 - x - 2 = 3x**2 - 1
        f, df = compile_with_derivative("x**3 - x - 2")
        assert abs(f(1.0) - (-2.0)) < 1e-10   # 1 - 1 - 2 = -2
        assert abs(df(1.0) - 2.0) < 1e-10     # 3 - 1 = 2
        assert abs(df(2.0) - 11.0) < 1e-10    # 12 - 1 = 11

    def test_derivative_of_trig(self):
        """DADO una expresión trigonométrica
           CUANDO se llama a compile_with_derivative
           ENTONCES df coincide con la derivada simbólica."""
        # d/dx of sin(x) = cos(x)
        import math
        f, df = compile_with_derivative("sin(x)")
        assert abs(f(0.0) - 0.0) < 1e-10
        assert abs(df(0.0) - 1.0) < 1e-10   # cos(0) = 1
        assert abs(df(math.pi / 2) - 0.0) < 1e-10  # cos(pi/2) = 0

    def test_invalid_syntax_raises_value_error(self):
        """DADO una expresión mal formada
           CUANDO se llama a compile_with_derivative
           ENTONCES se lanza un ValueError."""
        with pytest.raises(ValueError, match="No se pudo interpretar"):
            compile_with_derivative("x***2 +")

    def test_invalid_variable_raises_value_error(self):
        """DADO una expresión con variables no válidas
           CUANDO se llama a compile_with_derivative
           ENTONCES se lanza un ValueError."""
        with pytest.raises(ValueError, match="solo puede contener"):
            compile_with_derivative("y**2 + 1")

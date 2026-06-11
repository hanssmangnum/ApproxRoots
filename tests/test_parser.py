"""Parser boundary tests — compile-only, no solver or UI mixing."""

import pytest
from utils.func_parser import compile_expression, parsear_funcion


class TestCompileExpression:
    """Bisection-only compile endpoint."""

    def test_valid_expression_returns_callable(self):
        """GIVEN a syntactically valid expression
           WHEN compile_expression is called
           THEN it returns a callable evaluator."""
        f = compile_expression("x**3 - x - 2")
        assert callable(f)
        result = f(2.0)
        assert isinstance(result, (int, float))
        assert abs(result - 4.0) < 1e-10  # 2^3 - 2 - 2 = 4

    def test_invalid_syntax_raises_value_error(self):
        """GIVEN a malformed expression
           WHEN compile_expression is called
           THEN a ValueError is raised."""
        with pytest.raises(ValueError, match="No se pudo interpretar"):
            compile_expression("x***2 +")

    def test_invalid_variable_raises_value_error(self):
        """GIVEN an expression with invalid variables
           WHEN compile_expression is called
           THEN a ValueError is raised."""
        with pytest.raises(ValueError, match="solo puede contener"):
            compile_expression("y**2 + 1")

    def test_no_interval_validation(self):
        """PROVE the parser does NOT do interval/sign validation —
           it only compiles."""
        f = compile_expression("x**2 + 1")  # always positive
        assert callable(f)
        # Evaluating is the solver's job; the parser accepts any expression
        assert f(0.0) == 1.0


class TestParsearFuncion:
    """Legacy API preserved for Newton-Raphson."""

    def test_returns_f_df_expr_d_expr(self):
        """GIVEN a valid expression
           WHEN parsear_funcion is called
           THEN it returns 4-tuple with evaluators and symbolic expressions."""
        f, df, expr, d_expr = parsear_funcion("x**2")
        assert callable(f)
        assert callable(df)
        assert abs(f(3.0) - 9.0) < 1e-10
        assert abs(df(3.0) - 6.0) < 1e-10

"""Presenter tests — domain-to-UI mapping without Streamlit."""

import math
from domain.models.bisection import (
    BisectionResult,
    BisectionIteration,
)
from ui.presenters.bisection_presenter import present_bisection_result


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
    """Successful result mapping."""

    def test_iterations_have_legacy_keys(self):
        """GIVEN a successful domain result
           WHEN present_bisection_result is called
           THEN iteration rows have legacy dict keys."""
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
        """GIVEN a result with 3 iterations
           WHEN presented
           THEN 3 rows are produced."""
        data = present_bisection_result(_sample_success_result())
        assert len(data["iterations"]) == 3

    def test_metrics_dict(self):
        """GIVEN a successful result
           WHEN presented
           THEN metrics contains expected keys."""
        data = present_bisection_result(_sample_success_result())
        assert data["metrics"]["root"] == 1.625
        assert data["metrics"]["iterations_count"] == 3
        assert data["metrics"]["converged"] is True
        assert math.isfinite(data["metrics"]["final_error"])

    def test_session_payload(self):
        """GIVEN a successful result
           WHEN presented
           THEN session payload has keys app.py expects."""
        data = present_bisection_result(_sample_success_result())
        assert "iteraciones" in data["session"]
        assert "raiz" in data["session"]
        assert "convergio" in data["session"]
        assert data["session"]["raiz"] == 1.625
        assert data["session"]["convergio"] is True


class TestPresenterFailure:
    """Non-success result mapping."""

    def test_empty_iterations_on_failure(self):
        """GIVEN a failed result with no iterations
           WHEN presented
           THEN empty iterations list is returned."""
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
        """GIVEN a failed result with no iterations
           WHEN presented
           THEN final_error is NaN."""
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
    """Successful result with zero iterations (root at a boundary)."""

    def _make_boundary_result(self, root: float) -> BisectionResult:
        return BisectionResult(
            iterations=[],
            root=root,
            converged=True,
            status="success",
        )

    def test_empty_iterations_list(self):
        """GIVEN a boundary-root success
           WHEN presented
           THEN iterations list is empty."""
        result = self._make_boundary_result(0.0)
        data = present_bisection_result(result)
        assert len(data["iterations"]) == 0

    def test_metrics_for_boundary_root(self):
        """GIVEN a boundary-root success
           WHEN presented
           THEN final_error is NaN (no iterations to derive error from)."""
        result = self._make_boundary_result(2.0)
        data = present_bisection_result(result)
        assert data["metrics"]["root"] == 2.0
        assert data["metrics"]["iterations_count"] == 0
        assert data["metrics"]["converged"] is True
        assert math.isnan(data["metrics"]["final_error"])

    def test_session_payload_for_boundary_root(self):
        """GIVEN a boundary-root success
           WHEN presented
           THEN session payload has empty iteraciones and correct raiz."""
        result = self._make_boundary_result(-1.0)
        data = present_bisection_result(result)
        assert data["session"]["iteraciones"] == []
        assert data["session"]["raiz"] == -1.0
        assert data["session"]["convergio"] is True

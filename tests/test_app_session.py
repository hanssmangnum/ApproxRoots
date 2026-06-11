"""Pruebas del state management de session en app.py — helpers sin Streamlit.
"""
from unittest.mock import MagicMock
import sys


class FakeSession(dict):
    """Dict que emula st.session_state."""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value


def _build_mock_st():
    """Crea un mock de streamlit para poder importar app.py sin Streamlit."""
    mock_st = MagicMock()

    # Session state inicial — ejecutado=True, metodo_activo="Bisección"
    # evita las ramas st.stop() y de comparación durante la importación.
    mock_st.session_state = FakeSession({
        "iteraciones": [{"iteracion": 1, "xm": 1.5, "a": 1.0, "b": 2.0,
                         "f(xm)": -0.875, "error_abs": 0.5, "error_rel": float("inf")}],
        "iter_actual": 0,
        "metodo_activo": "Bisección",
        "fn_texto": "x**3 - x - 2",
        "f": lambda x: x**3 - x - 2,
        "df": None,
        "expr": None,
        "raiz": 1.5,
        "convergio": True,
        "ejecutado": True,
        "historial": [],
        "err_bis": None,
        "err_nwt": None,
    })

    # st.columns(n) debe devolver una tupla de n MagicMock's
    def _columns(n):
        if isinstance(n, list):
            n = len(n)
        return tuple(MagicMock() for _ in range(n))

    mock_st.stop = MagicMock()
    mock_st.button = MagicMock(return_value=False)
    mock_st.rerun = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.error = MagicMock()
    mock_st.warning = MagicMock()
    mock_st.info = MagicMock()
    mock_st.success = MagicMock()
    mock_st.caption = MagicMock()
    mock_st.radio = MagicMock(return_value="Bisección")
    mock_st.text_input = MagicMock(return_value="x**3 - x - 2")
    mock_st.number_input = MagicMock(return_value=1.0)
    mock_st.columns = _columns
    mock_st.tabs = lambda *a: tuple(MagicMock() for _ in range(3))
    mock_st.dataframe = MagicMock()
    mock_st.download_button = MagicMock()
    mock_st.metric = MagicMock()
    mock_st.slider = MagicMock(return_value=1)
    mock_st.set_page_config = MagicMock()
    mock_st.pyplot = MagicMock()
    mock_st.close = MagicMock()
    mock_st.fragment = lambda x: x
    return mock_st


sys.modules["streamlit"] = _build_mock_st()

from app import _apply_comparison_session, _clear_failed_run_state


class TestApplyComparisonSession:
    """_apply_comparison_session actualiza correctamente el estado de sesión."""

    def _sample_bis_data(self):
        return {
            "iterations": [{"iteracion": 1, "xm": 1.5}],
            "session": {"raiz": 1.5, "convergio": True},
            "metrics": {},
        }

    def _sample_nwt_data(self):
        return {
            "iterations": [{"iteracion": 1, "x_nuevo": 2.0}],
            "session": {"raiz": 2.0, "convergio": True},
            "metrics": {},
        }

    def test_sets_comparison_keys(self):
        import streamlit as st
        st.session_state.clear()
        st.session_state["ejecutado"] = False
        bis = self._sample_bis_data()
        nwt = self._sample_nwt_data()

        _apply_comparison_session(bis, nwt)

        ss = st.session_state
        assert ss["iters_bis"] == bis["iterations"]
        assert ss["iters_nwt"] == nwt["iterations"]
        assert ss["raiz_bis"] == bis["session"]["raiz"]
        assert ss["raiz_nwt"] == nwt["session"]["raiz"]
        assert ss["conv_bis"] == bis["session"]["convergio"]
        assert ss["conv_nwt"] == nwt["session"]["convergio"]
        assert ss["metodo_activo"] == "Comparación"
        assert ss["ejecutado"] is True

    def test_does_not_clear_errors(self):
        """DADO error_keys existentes de ejecución anterior
           CUANDO _apply_comparison_session
           ENTONCES err_bis/err_nwt NO se tocan."""
        import streamlit as st
        st.session_state.clear()
        st.session_state["err_bis"] = "Error anterior de bisección"
        st.session_state["err_nwt"] = "Error anterior de Newton"
        bis = self._sample_bis_data()
        nwt = self._sample_nwt_data()

        _apply_comparison_session(bis, nwt)

        assert st.session_state["err_bis"] == "Error anterior de bisección"
        assert st.session_state["err_nwt"] == "Error anterior de Newton"


class TestClearFailedRunState:
    """_clear_failed_run_state limpia todas las claves de sesión de comparación."""

    def test_clears_all_comparison_keys(self):
        import streamlit as st
        st.session_state.clear()
        st.session_state["ejecutado"] = True
        st.session_state["iters_bis"] = [1, 2]
        st.session_state["iters_nwt"] = [3]
        st.session_state["raiz_bis"] = 1.5
        st.session_state["raiz_nwt"] = 2.0
        st.session_state["conv_bis"] = True
        st.session_state["conv_nwt"] = True
        st.session_state["err_bis"] = "Algo falló"
        st.session_state["err_nwt"] = None

        _clear_failed_run_state()

        ss = st.session_state
        assert ss["ejecutado"] is False
        for key in ("iters_bis", "iters_nwt", "raiz_bis", "raiz_nwt",
                     "conv_bis", "conv_nwt", "err_bis", "err_nwt"):
            assert key not in ss, f"{key} debería haber sido eliminado"

    def test_idempotent_when_no_comparison_keys(self):
        import streamlit as st
        st.session_state.clear()
        st.session_state["ejecutado"] = True
        _clear_failed_run_state()
        assert st.session_state["ejecutado"] is False

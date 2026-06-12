# app.py

import streamlit as st

try:
    import streamlit.components.v1 as components
except Exception:  # pragma: no cover - compatibilidad para tests con mocks simples
    components = None
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np
import sympy as sp

from domain.models.bisection import BisectionRequest
from domain.models.newton import NewtonRequest
from domain.models.comparison import ComparisonRequest
from application.services.parser_service import ParserService
from application.services.bisection_solver import BisectionSolver
from application.services.newton_solver import NewtonSolver
from application.use_cases.run_bisection import run_bisection
from application.use_cases.run_newton import run_newton
from application.use_cases.run_comparison import run_comparison
from ui.presenters.bisection_presenter import present_bisection_result
from ui.presenters.newton_presenter import present_newton_result
from ui.presenters.comparison_presenter import present_comparison_result
from ui.presenters.chart_presenters import (
    build_bisection_chart_vm,
    build_newton_chart_vm,
    build_convergence_chart_vm,
    build_function_chart_vm,
    build_comparison_chart_vm,
)
from utils.graficas import (
    graficar_funcion_vm,
    graficar_iteracion_biseccion_vm,
    graficar_iteracion_newton_vm,
    graficar_convergencia_vm,
    graficar_comparacion_vm,
)

# ══════════════════════════════════════════════
# Configuración de página
# ══════════════════════════════════════════════

st.set_page_config(
    page_title="ApproxRoots",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════
# CSS personalizado
# ══════════════════════════════════════════════

st.markdown("""
<style>
    :root {
        --ar-surface: var(--secondary-background-color);
        --ar-surface-border: rgba(148, 163, 184, 0.22);
        --ar-muted: color-mix(in srgb, var(--text-color) 58%, transparent);
        --ar-info-bg: color-mix(in srgb, var(--primary-color) 14%, var(--background-color));
        --ar-info-border: color-mix(in srgb, var(--primary-color) 34%, transparent);
        --ar-info-text: color-mix(in srgb, var(--primary-color) 78%, var(--text-color));
        --ar-badge-ok-bg: color-mix(in srgb, #22c55e 18%, var(--background-color));
        --ar-badge-ok-text: color-mix(in srgb, #16a34a 72%, var(--text-color));
        --ar-badge-fail-bg: color-mix(in srgb, #ef4444 18%, var(--background-color));
        --ar-badge-fail-text: color-mix(in srgb, #dc2626 72%, var(--text-color));
    }

    /* Fuente y fondo general */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* Header principal */
    .app-header {
        background: linear-gradient(135deg, #1a2a4a 0%, #2d4a7a 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .app-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .app-header p {
        margin: 0.3rem 0 0;
        opacity: 0.75;
        font-size: 0.95rem;
    }

    /* Tarjetas de resultados */
    .metric-card {
        background: var(--ar-surface);
        border: 1px solid var(--ar-surface-border);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .metric-card .label {
        font-size: 0.75rem;
        color: var(--ar-muted);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-card .value {
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--text-color);
        font-family: 'Courier New', monospace;
        margin-top: 4px;
    }

    /* Badge convergencia */
    .badge-ok {
        background: var(--ar-badge-ok-bg);
        color: var(--ar-badge-ok-text);
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-fail {
        background: var(--ar-badge-fail-bg);
        color: var(--ar-badge-fail-text);
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* Iteración actual */
    .iter-display {
        background: var(--ar-info-bg);
        border: 1px solid var(--ar-info-border);
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-size: 0.9rem;
        color: var(--ar-info-text);
        font-weight: 500;
        text-align: center;
        margin: 0.5rem 0;
    }

    /* Tabla */
    .stDataFrame { border-radius: 8px; overflow: hidden; }

    /* Barra lateral */
    section[data-testid="stSidebar"] {
        background: var(--ar-surface);
    }

    section[data-testid="stSidebar"] * {
        color: var(--text-color);
    }

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stCaption {
        color: var(--text-color) !important;
    }

    /* Separador con texto */
    .section-divider {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 1rem 0 0.5rem;
        color: var(--ar-muted);
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .section-divider::before,
    .section-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--ar-surface-border);
    }

    /* Chips de ejemplo */
    .stButton > button {
        border-radius: 8px;
        font-size: 0.85rem;
    }

    /* Eliminar padding extra en columnas ajustadas */
    .block-container { padding-top: 1rem; }

    /* Ocultar elementos decorativos no deseados */
    [data-testid="stDecoration"],
    footer {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

if components is not None:
    components.html(
        """
        <script>
        const hiddenTexts = [
          "Deploy",
          "Rerun",
          "Clear cache",
          "Auto rerun",
          "Made with Streamlit"
        ];

        function textMatches(node, expected) {
          const value = (node.textContent || "").trim();
          return value === expected || value.startsWith(expected + " ");
        }

        function forceVisibleCoreUi() {
          const header = window.parent.document.querySelector('header[data-testid="stHeader"]');
          const toolbar = window.parent.document.querySelector('[data-testid="stToolbar"]');
          const statusWidget = window.parent.document.querySelector('[data-testid="stStatusWidget"]');

          [header, toolbar, statusWidget].forEach((node) => {
            if (!node) return;
            node.style.display = "";
            node.style.visibility = "visible";
            node.style.height = "";
          });
        }

        function hideMenuEntry(expectedText) {
          const nodes = window.parent.document.querySelectorAll('li, div[role="menuitem"], button, span, p');
          nodes.forEach((node) => {
            if (!textMatches(node, expectedText)) return;

            const target = node.closest('li, div[role="menuitem"], button') || node;
            if (!target) return;

            target.style.display = 'none';
            target.style.visibility = 'hidden';
          });
        }

        function hideNativeUi() {
          forceVisibleCoreUi();

          hideMenuEntry('Deploy');
          hideMenuEntry('Rerun');
          hideMenuEntry('Clear cache');
          hideMenuEntry('Auto rerun');
          hideMenuEntry('Made with Streamlit');
        }

        hideNativeUi();
        const observer = new MutationObserver(hideNativeUi);
        observer.observe(window.parent.document.body, { childList: true, subtree: true });
        </script>
        """,
        height=0,
    )


# ══════════════════════════════════════════════
# Estado de sesión
# ══════════════════════════════════════════════

def init_state():
    defaults = {
        "iteraciones"    : [],
        "iter_actual"    : 0,
        "metodo_activo"  : None,
        "fn_texto"       : "x**3 - x - 2",
        "f"              : None,
        "df"             : None,
        "expr"           : None,
        "raiz"           : None,
        "convergio"      : None,
        "ejecutado"      : False,
        "historial"      : [],
        "err_bis"        : None,
        "err_nwt"        : None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ══════════════════════════════════════════════
# Funciones auxiliares
# ══════════════════════════════════════════════

def fmt(v, decimales=8):
    if not np.isfinite(v):
        return "∞"
    if abs(v) < 1e-4 or abs(v) > 1e6:
        return f"{v:.4e}"
    return f"{v:.{decimales}f}".rstrip("0").rstrip(".")


def guardar_historial(fn_texto, metodo, raiz, iters):
    entrada = {
        "funcion" : fn_texto,
        "metodo"  : metodo,
        "raiz"    : raiz,
        "iters"   : iters,
    }
    hist = st.session_state["historial"]
    # Evitar duplicados consecutivos
    if not hist or hist[-1]["funcion"] != fn_texto or hist[-1]["metodo"] != metodo:
        hist.append(entrada)
        if len(hist) > 10:
            hist.pop(0)


def _apply_newton_session(data: dict) -> None:
    """Escribe el payload de sesión del presenter de Newton y las claves de renderizado en el estado de sesión."""
    st.session_state.update(data["session"])  # iteraciones, raiz, convergio
    st.session_state["metodo_activo"] = "Newton-Raphson"
    st.session_state["iter_actual"]   = 0
    st.session_state["ejecutado"]     = True


def _apply_comparison_session(
    bis_data: dict,
    nwt_data: dict,
) -> None:
    """Escribe los datos del presenter de cada caso de uso en las claves de renderizado de comparación."""
    st.session_state["iters_bis"] = bis_data["iterations"]
    st.session_state["iters_nwt"] = nwt_data["iterations"]
    st.session_state["raiz_bis"]  = bis_data["session"]["raiz"]
    st.session_state["raiz_nwt"]  = nwt_data["session"]["raiz"]
    st.session_state["conv_bis"]  = bis_data["session"]["convergio"]
    st.session_state["conv_nwt"]  = nwt_data["session"]["convergio"]
    st.session_state["metodo_activo"] = "Comparación"
    st.session_state["ejecutado"]     = True


def _clear_failed_run_state() -> None:
    """Limpia el estado de sesión de una ejecución exitosa previa para que
    resultados obsoletos no aparezcan bajo un banner de error tras un fallo.

    Seguro de llamar múltiples veces — limpia solo las claves necesarias
    para la guarda de estado vacío y los residuos de comparación.
    """
    st.session_state["ejecutado"] = False
    # Las claves de comparación pueden persistir de una ejecución previa exitosa.
    for key in ("iters_bis", "iters_nwt", "raiz_bis", "raiz_nwt", "conv_bis", "conv_nwt", "err_bis", "err_nwt"):
        st.session_state.pop(key, None)


# ══════════════════════════════════════════════
# Barra lateral
# ══════════════════════════════════════════════

with st.sidebar:
    st.markdown("## ⚙️ Configuración")

    # ── Función ──────────────────────────────
    st.markdown('<div class="section-divider">Función</div>', unsafe_allow_html=True)

    fn_texto = st.text_input(
        "f(x)",
        value=st.session_state["fn_texto"],
        placeholder="ej: x**3 - x - 2",
        help="Usa sintaxis Python/SymPy: ** para potencias, exp(x), sin(x), cos(x), log(x)…",
    )
    st.session_state["fn_texto"] = fn_texto

    # Ejemplos rápidos
    st.caption("Ejemplos rápidos:")
    ejemplos = {
        "x³−x−2"       : "x**3 - x - 2",
        "e⁻ˣ−x"        : "exp(-x) - x",
        "cos(x)−x"     : "cos(x) - x",
        "x²−2"         : "x**2 - 2",
        "sin(x)−x/2"   : "sin(x) - x/2",
        "ln(x)−1"      : "log(x) - 1",
    }
    cols_ej = st.columns(2)
    for i, (lbl, expr_txt) in enumerate(ejemplos.items()):
        with cols_ej[i % 2]:
            if st.button(lbl, key=f"ej_{i}", use_container_width=True):
                st.session_state["fn_texto"] = expr_txt
                st.rerun()

    # ── Método ───────────────────────────────
    st.markdown('<div class="section-divider">Método</div>', unsafe_allow_html=True)

    metodo = st.radio(
        "Selecciona el método",
        ["Bisección", "Newton-Raphson", "Comparación"],
        horizontal=False,
    )

    # ── Parámetros ───────────────────────────
    st.markdown('<div class="section-divider">Parámetros</div>', unsafe_allow_html=True)

    tol      = st.number_input("Tolerancia",           value=1e-6, format="%.2e", min_value=1e-15, max_value=0.1)
    max_iter = st.number_input("Máx. iteraciones",     value=50,   min_value=1,   max_value=500,   step=1)

    if metodo in ("Bisección", "Comparación"):
        col_a, col_b = st.columns(2)
        with col_a:
            bis_a = st.number_input("a", value=1.0, format="%.4f")
        with col_b:
            bis_b = st.number_input("b", value=2.0, format="%.4f")

    if metodo in ("Newton-Raphson", "Comparación"):
        nwt_x0 = st.number_input("x₀ (valor inicial)", value=1.5, format="%.4f")

    # ── Ejecutar ─────────────────────────────
    st.markdown("")
    ejecutar = st.button("▶ Ejecutar", type="primary", use_container_width=True)

    # ── Historial ────────────────────────────
    if st.session_state["historial"]:
        st.markdown('<div class="section-divider">Historial</div>', unsafe_allow_html=True)
        for h in reversed(st.session_state["historial"][-5:]):
            st.caption(f"**{h['metodo']}** `{h['funcion']}` → raíz ≈ {fmt(h['raiz'], 5)}")


# ══════════════════════════════════════════════
# Lógica de ejecución
# ══════════════════════════════════════════════

error_msg = None

if ejecutar:
    try:
        if metodo == "Bisección":
            request = BisectionRequest(
                expression=st.session_state["fn_texto"],
                a=bis_a,
                b=bis_b,
                tolerance=tol,
                max_iterations=int(max_iter),
            )
            parser = ParserService()
            bisection_solver = BisectionSolver()
            result = run_bisection(request, parser, bisection_solver)
            presenter_data = present_bisection_result(result)

            if result.status == "success":
                evaluator = ParserService().compile_expression(st.session_state["fn_texto"])
                st.session_state["f"]    = evaluator
                st.session_state["df"]   = None
                st.session_state["expr"] = sp.sympify(st.session_state["fn_texto"])
                st.session_state["iteraciones"]   = presenter_data["session"]["iteraciones"]
                st.session_state["raiz"]          = result.root
                st.session_state["convergio"]     = result.converged
                st.session_state["metodo_activo"] = "Bisección"
                st.session_state["iter_actual"]   = 0
                st.session_state["ejecutado"]     = True
                guardar_historial(
                    st.session_state["fn_texto"],
                    "Bisección",
                    result.root,
                    len(result.iterations),
                )
            else:
                _clear_failed_run_state()
                error_msg = result.error_message or "Bisección falló."

        elif metodo == "Newton-Raphson":
            request = NewtonRequest(
                expression=st.session_state["fn_texto"],
                x0=nwt_x0,
                tolerance=tol,
                max_iterations=int(max_iter),
            )
            parser = ParserService()
            newton_solver = NewtonSolver()
            result = run_newton(request, parser, newton_solver)
            presenter_data = present_newton_result(result)

            if result.status == "success":
                f, df = ParserService().compile_with_derivative(st.session_state["fn_texto"])
                st.session_state["f"]    = f
                st.session_state["df"]   = df
                st.session_state["expr"] = sp.sympify(st.session_state["fn_texto"])
                _apply_newton_session(presenter_data)
                guardar_historial(
                    st.session_state["fn_texto"],
                    "Newton-Raphson",
                    result.root,
                    len(result.iterations),
                )
            else:
                _clear_failed_run_state()
                error_msg = result.error_message or "Newton-Raphson falló."

        elif metodo == "Comparación":
            f, df = ParserService().compile_with_derivative(st.session_state["fn_texto"])
            st.session_state["f"]  = f
            st.session_state["df"] = df

            request = ComparisonRequest(
                expression=st.session_state["fn_texto"],
                bisection_a=bis_a,
                bisection_b=bis_b,
                newton_x0=nwt_x0,
                tolerance=tol,
                max_iterations=int(max_iter),
            )

            result = run_comparison(
                request,
                parser=ParserService(),
                bisection_solver=BisectionSolver(),
                newton_solver=NewtonSolver(),
            )

            if result.status == "parse_error":
                _clear_failed_run_state()
                error_msg = result.error_message or "Error de compilación en la expresión."
            else:
                presenter_data = present_comparison_result(result)
                bis_ok = result.bisection.status == "success"
                nwt_ok = result.newton.status == "success"

                # Limpiar claves de advertencia obsoletas de ejecuciones de comparación previas
                st.session_state.pop("err_bis", None)
                st.session_state.pop("err_nwt", None)

                if bis_ok and nwt_ok:
                    st.session_state.update(presenter_data["session"])
                elif bis_ok and not nwt_ok:
                    st.session_state.update(presenter_data["session"])
                    st.session_state["err_nwt"] = result.newton.error_message or "Error desconocido"
                elif not bis_ok and nwt_ok:
                    st.session_state.update(presenter_data["session"])
                    st.session_state["err_bis"] = result.bisection.error_message or "Error desconocido"
                else:
                    _clear_failed_run_state()
                    error_msg = (
                        "Comparación: ambos métodos fallaron. "
                        f"Bisección: {result.bisection.error_message or 'Error desconocido'}. "
                        f"Newton-Raphson: {result.newton.error_message or 'Error desconocido'}."
                    )

    except ValueError as e:
        _clear_failed_run_state()
        error_msg = str(e)
    except Exception as e:
        _clear_failed_run_state()
        error_msg = f"Error inesperado: {e}"


# ══════════════════════════════════════════════
# Encabezado
# ══════════════════════════════════════════════

st.markdown("""
<div class="app-header">
    <h1>📐 ApproxRoots</h1>
    <p>Visualización paso a paso de métodos numéricos: Bisección y Newton-Raphson</p>
</div>
""", unsafe_allow_html=True)

if error_msg:
    st.error(f"⚠️ {error_msg}")

# ══════════════════════════════════════════════
# Vista: sin ejecución
# ══════════════════════════════════════════════

if not st.session_state["ejecutado"]:
    st.info("👈 Ingresa una función, selecciona el método y los parámetros en el panel izquierdo, luego presiona **▶ Ejecutar**.")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Método de Bisección")
        st.markdown("""
        Divide el intervalo **[a, b]** a la mitad en cada paso y conserva
        el subintervalo donde la función cambia de signo.

        - Requiere que f(a)·f(b) < 0
        - Convergencia garantizada pero lenta (lineal)
        - No necesita derivada
        """)
    with col2:
        st.markdown("### Método de Newton-Raphson")
        st.markdown("""
        Usa la recta **tangente** en cada punto para aproximarse a la raíz.

        - Requiere un valor inicial cercano a la raíz
        - Convergencia cuadrática (muy rápida)
        - Necesita la derivada f'(x)
        """)
    st.stop()


# ══════════════════════════════════════════════
# Vista: Comparación
# ══════════════════════════════════════════════

if st.session_state["metodo_activo"] == "Comparación":
    iters_bis = st.session_state.get("iters_bis", [])
    iters_nwt = st.session_state.get("iters_nwt", [])
    f         = st.session_state["f"]
    err_bis   = st.session_state.get("err_bis")
    err_nwt   = st.session_state.get("err_nwt")
    raiz_bis  = st.session_state.get("raiz_bis")
    raiz_nwt  = st.session_state.get("raiz_nwt")

    st.markdown("## Comparación: Bisección vs Newton-Raphson")

    # ── Banners de advertencia para métodos fallidos ──
    if err_bis:
        st.warning(f"⚠️ **Bisección no disponible:** {err_bis}")
    if err_nwt:
        st.warning(f"⚠️ **Newton-Raphson no disponible:** {err_nwt}")

    # ── Métricas ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        val = fmt(raiz_bis) if raiz_bis is not None else "—"
        st.markdown(f"""<div class="metric-card"><div class="label">Raíz (Bisección)</div>
        <div class="value">{val}</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card"><div class="label">Iters. Bisección</div>
        <div class="value">{len(iters_bis)}</div></div>""", unsafe_allow_html=True)
    with c3:
        val = fmt(raiz_nwt) if raiz_nwt is not None else "—"
        st.markdown(f"""<div class="metric-card"><div class="label">Raíz (Newton-R.)</div>
        <div class="value">{val}</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card"><div class="label">Iters. Newton-R.</div>
        <div class="value">{len(iters_nwt)}</div></div>""", unsafe_allow_html=True)

    st.markdown("")

    # ── Gráfica y tablas ────────────────────────
    bis_has_data = len(iters_bis) > 0
    nwt_has_data = len(iters_nwt) > 0

    if bis_has_data or nwt_has_data:
        col_g, col_t = st.columns([3, 2])
        with col_g:
            if bis_has_data and nwt_has_data:
                vm = build_comparison_chart_vm(iters_bis, iters_nwt)
                fig = graficar_comparacion_vm(vm)
            elif bis_has_data:
                vm = build_convergence_chart_vm(iters_bis, metodo="Bisección")
                fig = graficar_convergencia_vm(vm)
            else:
                vm = build_convergence_chart_vm(iters_nwt, metodo="Newton-Raphson")
                fig = graficar_convergencia_vm(vm)
            st.pyplot(fig)
            plt.close(fig)

        with col_t:
            import pandas as pd

            if bis_has_data:
                st.markdown("#### Bisección")
                df_bis = pd.DataFrame([{
                    "Iter."     : it["iteracion"],
                    "xₘ"        : fmt(it["xm"], 6),
                    "f(xₘ)"     : fmt(it["f(xm)"], 4),
                    "Error abs.": fmt(it["error_abs"], 4),
                } for it in iters_bis])
                st.dataframe(df_bis, use_container_width=True, hide_index=True, height=220)

            if nwt_has_data:
                st.markdown("#### Newton-Raphson")
                df_nwt = pd.DataFrame([{
                    "Iter."     : it["iteracion"],
                    "x₁"        : fmt(it["x_nuevo"], 6),
                    "f(x)"      : fmt(it["f(x)"], 4),
                    "Error abs.": fmt(it["error_abs"], 4),
                } for it in iters_nwt])
                st.dataframe(df_nwt, use_container_width=True, hide_index=True, height=220)

    st.stop()


# ══════════════════════════════════════════════
# Vista: Bisección / Newton-Raphson
# ══════════════════════════════════════════════

iteraciones   = st.session_state["iteraciones"]
iter_actual   = st.session_state["iter_actual"]
metodo_activo = st.session_state["metodo_activo"]
f             = st.session_state["f"]
raiz          = st.session_state["raiz"]
convergio     = st.session_state["convergio"]
expr          = st.session_state["expr"]

n_iters = len(iteraciones)

    # ── Guarda de éxito con cero iteraciones ─────────────
# La raíz se encontró en un límite (f(a)=0 o f(b)=0); no se registraron iteraciones.
if n_iters == 0 and convergio:
    badge = '<span class="badge-ok">✔ Convergió</span>'
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""<div class="metric-card"><div class="label">Raíz aproximada</div>
        <div class="value">{fmt(raiz, 7)}</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card"><div class="label">f(raíz)</div>
        <div class="value">{fmt(float(f(raiz)), 4)}</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card"><div class="label">Total iteraciones</div>
        <div class="value">0</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card"><div class="label">Error final</div>
        <div class="value">0</div></div>""", unsafe_allow_html=True)
    with c5:
        st.markdown(f"""<div class="metric-card"><div class="label">Estado</div>
        <div class="value" style="font-size:1rem;margin-top:6px">{badge}</div></div>""",
        unsafe_allow_html=True)
    st.success("La raíz exacta se encuentra en el límite del intervalo. No se requirieron iteraciones.")
    st.stop()

if n_iters == 0:
    st.warning("No hay iteraciones disponibles para mostrar. Ejecuta nuevamente el método.")
    st.session_state["ejecutado"] = False
    st.stop()

# ── Métricas superiores ───────────────────────

badge = (
    '<span class="badge-ok">✔ Convergió</span>'
    if convergio else
    '<span class="badge-fail">✘ No convergió</span>'
)
iter_info = iteraciones[iter_actual]

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f"""<div class="metric-card"><div class="label">Raíz aproximada</div>
    <div class="value">{fmt(raiz, 7)}</div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card"><div class="label">f(raíz)</div>
    <div class="value">{fmt(float(f(raiz)), 4)}</div></div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card"><div class="label">Total iteraciones</div>
    <div class="value">{n_iters}</div></div>""", unsafe_allow_html=True)
with c4:
    err_final = iteraciones[-1]["error_abs"]
    st.markdown(f"""<div class="metric-card"><div class="label">Error final</div>
    <div class="value">{fmt(err_final, 3)}</div></div>""", unsafe_allow_html=True)
with c5:
    st.markdown(f"""<div class="metric-card"><div class="label">Estado</div>
    <div class="value" style="font-size:1rem;margin-top:6px">{badge}</div></div>""",
    unsafe_allow_html=True)

st.markdown("")

# ── Pestañas principales ─────────────────────────

tab_grafica, tab_tabla, tab_convergencia = st.tabs(
    ["📊 Gráfica iterativa", "📋 Tabla de iteraciones", "📈 Convergencia"]
)

# ── Tab: Gráfica ─────────────────────────────

with tab_grafica:

    # Controles de navegación
    st.markdown(
        f'<div class="iter-display">Iteración {iter_actual + 1} de {n_iters} &nbsp;|&nbsp; '
        f'Aproximación actual: <strong>{fmt(iter_info["xm"] if metodo_activo == "Bisección" else iter_info["x_nuevo"], 7)}</strong>'
        f'</div>',
        unsafe_allow_html=True,
    )

    nav1, nav2, nav3, nav4, nav5, _ = st.columns([1, 1, 1, 1, 1, 3])

    with nav1:
        if st.button("⏮", help="Primera iteración", use_container_width=True):
            st.session_state["iter_actual"] = 0
            st.rerun()
    with nav2:
        if st.button("◀", help="Iteración anterior", use_container_width=True,
                     disabled=(iter_actual == 0)):
            st.session_state["iter_actual"] = iter_actual - 1
            st.rerun()
    with nav3:
        if st.button("▶", help="Siguiente iteración", use_container_width=True,
                     disabled=(iter_actual == n_iters - 1)):
            st.session_state["iter_actual"] = iter_actual + 1
            st.rerun()
    with nav4:
        if st.button("⏭", help="Última iteración", use_container_width=True):
            st.session_state["iter_actual"] = n_iters - 1
            st.rerun()
    with nav5:
        if st.button("↺ Reiniciar", use_container_width=True):
            st.session_state["iter_actual"] = 0
            st.rerun()

    # Slider de iteración
    if n_iters > 1:
        nueva_iter = st.slider(
            "Navegar entre iteraciones",
            min_value=1, max_value=n_iters,
            value=iter_actual + 1,
            label_visibility="collapsed",
        )
        if nueva_iter - 1 != iter_actual:
            st.session_state["iter_actual"] = nueva_iter - 1
            st.rerun()

    st.markdown("")

    # Gráfica principal
    col_chart, col_info = st.columns([3, 1])

    with col_chart:
        iter_info = iteraciones[iter_actual]
        if metodo_activo == "Bisección":
            vm = build_bisection_chart_vm(f, iter_info)
            fig = graficar_iteracion_biseccion_vm(vm)
        else:
            vm = build_newton_chart_vm(f, iter_info)
            fig = graficar_iteracion_newton_vm(vm)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with col_info:
        st.markdown("##### Valores actuales")
        if metodo_activo == "Bisección":
            st.metric("a", fmt(iter_info["a"], 6))
            st.metric("b", fmt(iter_info["b"], 6))
            st.metric("xₘ", fmt(iter_info["xm"], 6))
            st.metric("f(xₘ)", fmt(iter_info["f(xm)"], 6))
        else:
            st.metric("x₀", fmt(iter_info["x_anterior"], 6))
            st.metric("f(x₀)", fmt(iter_info["f(x)"], 6))
            st.metric("f'(x₀)", fmt(iter_info["f'(x)"], 6))
            st.metric("x₁", fmt(iter_info["x_nuevo"], 6))
        st.metric("Error abs.", fmt(iter_info["error_abs"], 4))
        st.metric("Error rel.", fmt(iter_info["error_rel"], 4) if np.isfinite(iter_info["error_rel"]) else "∞")


# ── Tab: Tabla ───────────────────────────────

with tab_tabla:
    import pandas as pd

    if metodo_activo == "Bisección":
        filas = [{
            "Iter."      : it["iteracion"],
            "a"          : fmt(it["a"], 6),
            "b"          : fmt(it["b"], 6),
            "xₘ"         : fmt(it["xm"], 7),
            "f(xₘ)"      : fmt(it["f(xm)"], 6),
            "Error abs." : fmt(it["error_abs"]),
            "Error rel." : fmt(it["error_rel"]) if np.isfinite(it["error_rel"]) else "∞",
        } for it in iteraciones]
    else:
        filas = [{
            "Iter."      : it["iteracion"],
            "x₀"         : fmt(it["x_anterior"], 7),
            "f(x₀)"      : fmt(it["f(x)"], 6),
            "f'(x₀)"     : fmt(it["f'(x)"], 6),
            "x₁"         : fmt(it["x_nuevo"], 7),
            "Error abs." : fmt(it["error_abs"]),
            "Error rel." : fmt(it["error_rel"]) if np.isfinite(it["error_rel"]) else "∞",
        } for it in iteraciones]

    df_tabla = pd.DataFrame(filas)

    # Resaltar fila actual
    def resaltar_fila(row):
        if row["Iter."] == iter_actual + 1:
            return [
                "background-color: color-mix(in srgb, var(--primary-color) 12%, var(--background-color)); font-weight: bold"
            ] * len(row)
        return [""] * len(row)

    st.dataframe(
        df_tabla.style.apply(resaltar_fila, axis=1),
        use_container_width=True,
        hide_index=True,
        height=min(50 + 35 * n_iters, 500),
    )

    # Exportar CSV
    csv = df_tabla.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Descargar tabla CSV",
        data=csv,
        file_name=f"iteraciones_{metodo_activo.lower().replace('-','_')}.csv",
        mime="text/csv",
    )


# ── Tab: Convergencia ────────────────────────

with tab_convergencia:
    col_cv, col_fx = st.columns(2)

    with col_cv:
        vm_conv = build_convergence_chart_vm(iteraciones, metodo=metodo_activo)
        fig_conv = graficar_convergencia_vm(vm_conv)
        st.pyplot(fig_conv, use_container_width=True)
        plt.close(fig_conv)

    with col_fx:
        # Gráfica de f(x) con la raíz encontrada
        x_key = "xm" if metodo_activo == "Bisección" else "x_nuevo"
        primer_x = iteraciones[0]["a"] if metodo_activo == "Bisección" else iteraciones[0]["x_anterior"]
        ultimo_x = iteraciones[-1][x_key]
        pad = max(abs(ultimo_x - primer_x) * 0.8, 1.0)
        vm_fn = build_function_chart_vm(
            f, ultimo_x - pad, ultimo_x + pad, raiz,
            titulo=f"f(x) con raíz ≈ {fmt(raiz, 5)}",
        )
        fig_fn = graficar_funcion_vm(vm_fn)
        st.pyplot(fig_fn, use_container_width=True)
        plt.close(fig_fn)

    # Análisis de convergencia
    st.markdown("#### Análisis")
    col_a1, col_a2, col_a3 = st.columns(3)

    errores = [it["error_abs"] for it in iteraciones if it["error_abs"] > 0]
    if len(errores) >= 2:
        tasas = [errores[i+1] / errores[i] for i in range(len(errores)-1) if errores[i] > 0]
        tasa_media = np.mean(tasas) if tasas else float("nan")
        reduccion  = errores[0] / errores[-1] if errores[-1] > 0 else float("inf")

        with col_a1:
            st.markdown(f"""<div class="metric-card"><div class="label">Tasa de convergencia media</div>
            <div class="value">{fmt(tasa_media, 4)}</div></div>""", unsafe_allow_html=True)
        with col_a2:
            st.markdown(f"""<div class="metric-card"><div class="label">Reducción del error</div>
            <div class="value">{fmt(reduccion, 2)}×</div></div>""", unsafe_allow_html=True)
        with col_a3:
            tipo = "Cuadrática" if metodo_activo == "Newton-Raphson" else "Lineal"
            st.markdown(f"""<div class="metric-card"><div class="label">Tipo de convergencia</div>
            <div class="value" style="font-size:1rem">{tipo}</div></div>""", unsafe_allow_html=True)

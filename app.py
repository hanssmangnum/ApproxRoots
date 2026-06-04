# app.py

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np
import sympy as sp

from utils.func_parser import parsear_funcion
from metodos.biseccion import biseccion
from metodos.newton import newton_raphson
from utils.graficas import (
    graficar_funcion,
    graficar_iteracion_biseccion,
    graficar_iteracion_newton,
    graficar_convergencia,
    graficar_comparacion,
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
        background: #f8f9fc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .metric-card .label {
        font-size: 0.75rem;
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-card .value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1e293b;
        font-family: 'Courier New', monospace;
        margin-top: 4px;
    }

    /* Badge convergencia */
    .badge-ok {
        background: #dcfce7;
        color: #166534;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-fail {
        background: #fee2e2;
        color: #991b1b;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* Iteración actual */
    .iter-display {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-size: 0.9rem;
        color: #1e40af;
        font-weight: 500;
        text-align: center;
        margin: 0.5rem 0;
    }

    /* Tabla */
    .stDataFrame { border-radius: 8px; overflow: hidden; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #f8fafc;
    }

    /* Separador con texto */
    .section-divider {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 1rem 0 0.5rem;
        color: #64748b;
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
        background: #e2e8f0;
    }

    /* Chips de ejemplo */
    .stButton > button {
        border-radius: 8px;
        font-size: 0.85rem;
    }

    /* Eliminar padding extra en columnas ajustadas */
    .block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)


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
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ══════════════════════════════════════════════
# Helpers
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


# ══════════════════════════════════════════════
# Sidebar
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
        f, df, expr, d_expr = parsear_funcion(st.session_state["fn_texto"])
        st.session_state["f"]    = f
        st.session_state["df"]   = df
        st.session_state["expr"] = expr

        if metodo == "Bisección":
            iters, raiz, convergio = biseccion(f, bis_a, bis_b, tol=tol, max_iter=max_iter)
            st.session_state["iteraciones"]   = iters
            st.session_state["raiz"]          = raiz
            st.session_state["convergio"]     = convergio
            st.session_state["metodo_activo"] = "Bisección"
            st.session_state["iter_actual"]   = 0
            st.session_state["ejecutado"]     = True
            guardar_historial(st.session_state["fn_texto"], "Bisección", raiz, len(iters))

        elif metodo == "Newton-Raphson":
            iters, raiz, convergio = newton_raphson(f, df, nwt_x0, tol=tol, max_iter=max_iter)
            st.session_state["iteraciones"]   = iters
            st.session_state["raiz"]          = raiz
            st.session_state["convergio"]     = convergio
            st.session_state["metodo_activo"] = "Newton-Raphson"
            st.session_state["iter_actual"]   = 0
            st.session_state["ejecutado"]     = True
            guardar_historial(st.session_state["fn_texto"], "Newton-Raphson", raiz, len(iters))

        elif metodo == "Comparación":
            iters_bis, raiz_bis, conv_bis = biseccion(f, bis_a, bis_b, tol=tol, max_iter=max_iter)
            iters_nwt, raiz_nwt, conv_nwt = newton_raphson(f, df, nwt_x0, tol=tol, max_iter=max_iter)
            st.session_state["iters_bis"]     = iters_bis
            st.session_state["iters_nwt"]     = iters_nwt
            st.session_state["raiz_bis"]      = raiz_bis
            st.session_state["raiz_nwt"]      = raiz_nwt
            st.session_state["conv_bis"]      = conv_bis
            st.session_state["conv_nwt"]      = conv_nwt
            st.session_state["metodo_activo"] = "Comparación"
            st.session_state["ejecutado"]     = True

    except ValueError as e:
        error_msg = str(e)
    except Exception as e:
        error_msg = f"Error inesperado: {e}"


# ══════════════════════════════════════════════
# Header
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
    iters_bis = st.session_state["iters_bis"]
    iters_nwt = st.session_state["iters_nwt"]
    f         = st.session_state["f"]

    st.markdown("## Comparación: Bisección vs Newton-Raphson")

    # Métricas
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card"><div class="label">Raíz (Bisección)</div>
        <div class="value">{fmt(st.session_state['raiz_bis'])}</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card"><div class="label">Iters. Bisección</div>
        <div class="value">{len(iters_bis)}</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card"><div class="label">Raíz (Newton-R.)</div>
        <div class="value">{fmt(st.session_state['raiz_nwt'])}</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card"><div class="label">Iters. Newton-R.</div>
        <div class="value">{len(iters_nwt)}</div></div>""", unsafe_allow_html=True)

    st.markdown("")

    col_g, col_t = st.columns([3, 2])
    with col_g:
        fig = graficar_comparacion(iters_bis, iters_nwt)
        st.pyplot(fig)
        plt.close(fig)

    with col_t:
        st.markdown("#### Bisección")
        import pandas as pd
        df_bis = pd.DataFrame([{
            "Iter."     : it["iteracion"],
            "xₘ"        : fmt(it["xm"], 6),
            "f(xₘ)"     : fmt(it["f(xm)"], 4),
            "Error abs.": fmt(it["error_abs"], 4),
        } for it in iters_bis])
        st.dataframe(df_bis, use_container_width=True, hide_index=True, height=220)

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

# ── Tabs principales ─────────────────────────

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
            fig = graficar_iteracion_biseccion(f, iter_info)
        else:
            fig = graficar_iteracion_newton(f, iter_info)
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
            return ["background-color: #eff6ff; font-weight: bold"] * len(row)
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
        fig_conv = graficar_convergencia(iteraciones, metodo=metodo_activo)
        st.pyplot(fig_conv, use_container_width=True)
        plt.close(fig_conv)

    with col_fx:
        # Gráfica de f(x) con la raíz encontrada
        x_key = "xm" if metodo_activo == "Bisección" else "x_nuevo"
        primer_x = iteraciones[0]["a"] if metodo_activo == "Bisección" else iteraciones[0]["x_anterior"]
        ultimo_x = iteraciones[-1][x_key]
        pad = max(abs(ultimo_x - primer_x) * 0.8, 1.0)
        fig_fn = graficar_funcion(f, ultimo_x - pad, ultimo_x + pad,
                                  titulo=f"f(x) con raíz ≈ {fmt(raiz, 5)}",
                                  raiz=raiz)
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
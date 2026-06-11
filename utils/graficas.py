# utils/graficas.py
 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
 
 
# ──────────────────────────────────────────────
# Paleta compartida
# ──────────────────────────────────────────────
COLOR_FUNCION   = "#3266AD"
COLOR_RAIZ      = "#1D9E75"
COLOR_INTERVALO = "#BA7517"
COLOR_TANGENTE  = "#E24B4A"
COLOR_PUNTO     = "#7F77DD"
COLOR_CERO      = "#888888"
 
 
def _rango_seguro(f, x_min: float, x_max: float, n: int = 500):
    """
    Genera arreglos x, y filtrando valores no finitos o demasiado grandes.
    Retorna (xs, ys) listos para graficar.
    """
    xs = np.linspace(x_min, x_max, n)
    ys = []
    for x in xs:
        try:
            v = float(f(x))
            ys.append(v if np.isfinite(v) and abs(v) < 1e8 else np.nan)
        except Exception:
            ys.append(np.nan)
    return xs, np.array(ys)
 
 
def _estilo_base(ax, titulo: str = ""):
    """Aplica estilo limpio y consistente a un objeto Axes."""
    ax.axhline(0, color=COLOR_CERO, linewidth=0.8, linestyle="--", alpha=0.6)
    ax.axvline(0, color=COLOR_CERO, linewidth=0.8, linestyle="--", alpha=0.6)
    ax.grid(True, alpha=0.2, linewidth=0.5)
    ax.spines[["top", "right"]].set_visible(False)
    if titulo:
        ax.set_title(titulo, fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("x", fontsize=10)
    ax.set_ylabel("f(x)", fontsize=10)
 
 
# ══════════════════════════════════════════════
# 1. Gráfica general de la función
# ══════════════════════════════════════════════
 
def graficar_funcion(f, x_min: float, x_max: float,
                     titulo: str = "f(x)",
                     raiz: float = None,
                     ax=None) -> plt.Figure:
    """
    Grafica la función en [x_min, x_max].
    Si se provee raíz, la marca con un punto verde.
    """
    fig_creada = ax is None
    if fig_creada:
        fig, ax = plt.subplots(figsize=(8, 4))
    else:
        fig = ax.figure
 
    xs, ys = _rango_seguro(f, x_min, x_max)
    ax.plot(xs, ys, color=COLOR_FUNCION, linewidth=2, label="f(x)")
 
    if raiz is not None:
        try:
            yr = float(f(raiz))
            if np.isfinite(yr):
                ax.scatter([raiz], [yr], color=COLOR_RAIZ, zorder=5, s=80,
                           label=f"Raíz ≈ {raiz:.6f}")
        except Exception:
            pass
 
    _estilo_base(ax, titulo)
    ax.legend(fontsize=9)
 
    if fig_creada:
        fig.tight_layout()
    return fig
 
 
# ══════════════════════════════════════════════
# 2. Iteración de Bisección
# ══════════════════════════════════════════════
 
def graficar_iteracion_biseccion(f, iteracion: dict,
                                  x_min: float = None,
                                  x_max: float = None,
                                  ax=None) -> plt.Figure:
    """
    Visualiza una iteración del método de bisección:
    - Función en el rango [a, b] extendido
    - Marcas en a, b y xm
    - Sombreado del intervalo activo
    """
    a, b, xm = iteracion["a"], iteracion["b"], iteracion["xm"]
 
    pad = (b - a) * 0.6
    xlo = (x_min if x_min is not None else a) - pad
    xhi = (x_max if x_max is not None else b) + pad
 
    fig_creada = ax is None
    if fig_creada:
        fig, ax = plt.subplots(figsize=(8, 4))
    else:
        fig = ax.figure
 
    xs, ys = _rango_seguro(f, xlo, xhi)
    ax.plot(xs, ys, color=COLOR_FUNCION, linewidth=2, label="f(x)")
 
    # Sombreado del intervalo [a, b]
    xs_int, ys_int = _rango_seguro(f, a, b, n=200)
    ax.fill_between(xs_int, ys_int, 0,
                    where=np.isfinite(ys_int),
                    alpha=0.12, color=COLOR_INTERVALO)
 
    # Líneas verticales en a, b, xm
    for val, color, etiq in [
        (a,  COLOR_INTERVALO, f"a = {a:.4f}"),
        (b,  COLOR_INTERVALO, f"b = {b:.4f}"),
        (xm, COLOR_RAIZ,      f"xₘ = {xm:.6f}"),
    ]:
        try:
            fv = float(f(val))
            ax.axvline(val, color=color, linewidth=1.2, linestyle="--", alpha=0.7)
            ax.scatter([val], [fv], color=color, zorder=5, s=70)
            ax.annotate(etiq, (val, fv),
                        textcoords="offset points", xytext=(6, 6),
                        fontsize=8, color=color)
        except Exception:
            pass
 
    _estilo_base(ax, f"Bisección — Iteración {iteracion['iteracion']}")
    leyenda = [
        Line2D([0], [0], color=COLOR_FUNCION,   linewidth=2, label="f(x)"),
        Line2D([0], [0], color=COLOR_INTERVALO, linewidth=1.2, linestyle="--", label="Intervalo [a, b]"),
        Line2D([0], [0], color=COLOR_RAIZ,      linewidth=1.2, linestyle="--", label=f"Punto medio xₘ"),
    ]
    ax.legend(handles=leyenda, fontsize=9)
 
    if fig_creada:
        fig.tight_layout()
    return fig
 
 
# ══════════════════════════════════════════════
# 3. Iteración de Newton-Raphson
# ══════════════════════════════════════════════
 
def graficar_iteracion_newton(f, iteracion: dict,
                               x_min: float = None,
                               x_max: float = None,
                               ax=None) -> plt.Figure:
    """
    Visualiza una iteración del método de Newton-Raphson:
    - Función
    - Punto (x_anterior, f(x_anterior))
    - Recta tangente en ese punto
    - Nuevo punto x_nuevo en el eje x
    """
    x_ant  = iteracion["x_anterior"]
    x_new  = iteracion["x_nuevo"]
    tang   = iteracion["tangente"]
    m, b_t = tang["pendiente"], tang["intercepto"]
 
    radio = max(abs(x_new - x_ant) * 2, 1.5)
    xlo = (x_min if x_min is not None else x_ant - radio) 
    xhi = (x_max if x_max is not None else x_ant + radio)
    xlo = min(xlo, x_ant - radio)
    xhi = max(xhi, x_ant + radio)
 
    fig_creada = ax is None
    if fig_creada:
        fig, ax = plt.subplots(figsize=(8, 4))
    else:
        fig = ax.figure
 
    xs, ys = _rango_seguro(f, xlo, xhi)
    ax.plot(xs, ys, color=COLOR_FUNCION, linewidth=2, label="f(x)")
 
    # Recta tangente
    yt = m * xs + b_t
    mascara = np.isfinite(yt) & (np.abs(yt) < 1e6)
    ax.plot(xs[mascara], yt[mascara],
            color=COLOR_TANGENTE, linewidth=1.5, linestyle="--",
            label=f"Tangente en x={x_ant:.4f}")
 
    # Punto de tangencia
    try:
        fx_ant = float(f(x_ant))
        ax.scatter([x_ant], [fx_ant], color=COLOR_PUNTO, zorder=6, s=80,
                   label=f"x₀ = {x_ant:.6f}")
        ax.annotate(f"({x_ant:.4f}, {fx_ant:.4f})", (x_ant, fx_ant),
                    textcoords="offset points", xytext=(6, 6), fontsize=8,
                    color=COLOR_PUNTO)
    except Exception:
        pass
 
    # Nuevo punto en el eje x
    ax.scatter([x_new], [0], color=COLOR_RAIZ, zorder=6, s=90, marker="^",
               label=f"x₁ = {x_new:.6f}")
    ax.axvline(x_new, color=COLOR_RAIZ, linewidth=0.8, linestyle=":", alpha=0.5)
 
    # Flecha desde x_ant hasta x_new en y=0
    ax.annotate("", xy=(x_new, 0), xytext=(x_ant, 0),
                arrowprops=dict(arrowstyle="->", color=COLOR_RAIZ, lw=1.2))
 
    _estilo_base(ax, f"Newton-Raphson — Iteración {iteracion['iteracion']}")
    ax.legend(fontsize=9)
 
    if fig_creada:
        fig.tight_layout()
    return fig
 
 
# ══════════════════════════════════════════════
# 4. Gráfica de convergencia (error vs iteración)
# ══════════════════════════════════════════════
 
def graficar_convergencia(iteraciones: list,
                           metodo: str = "Método",
                           ax=None) -> plt.Figure:
    """
    Grafica el error absoluto en escala logarítmica por iteración.
    """
    fig_creada = ax is None
    if fig_creada:
        fig, ax = plt.subplots(figsize=(7, 3.5))
    else:
        fig = ax.figure
 
    nums   = [it["iteracion"] for it in iteraciones]
    errors = [it["error_abs"] for it in iteraciones]
    errors_plot = [max(e, 1e-16) for e in errors]   # evitar log(0)
 
    ax.semilogy(nums, errors_plot,
                color=COLOR_FUNCION, linewidth=2, marker="o",
                markersize=5, markerfacecolor=COLOR_RAIZ, label="Error absoluto")
    ax.set_xlabel("Iteración", fontsize=10)
    ax.set_ylabel("Error absoluto (log)", fontsize=10)
    ax.set_title(f"Convergencia — {metodo}", fontsize=12, fontweight="bold", pad=10)
    ax.grid(True, alpha=0.25, which="both")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=9)
 
    if fig_creada:
        fig.tight_layout()
    return fig
 
 
# ══════════════════════════════════════════════
# 5. Comparación Bisección vs Newton-Raphson
# ══════════════════════════════════════════════
 
def graficar_comparacion(iters_bis: list, iters_nwt: list) -> plt.Figure:
    """
    Grafica el error absoluto de ambos métodos en el mismo eje (escala log).
    """
    fig, ax = plt.subplots(figsize=(8, 4))
 
    def _plot(iters, color, label):
        nums   = [it["iteracion"] for it in iters]
        errors = [max(it["error_abs"], 1e-16) for it in iters]
        ax.semilogy(nums, errors, color=color, linewidth=2,
                    marker="o", markersize=5, label=label)
 
    _plot(iters_bis, COLOR_INTERVALO, "Bisección")
    _plot(iters_nwt, COLOR_TANGENTE,  "Newton-Raphson")
 
    ax.set_xlabel("Iteración", fontsize=10)
    ax.set_ylabel("Error absoluto (log)", fontsize=10)
    ax.set_title("Comparación de convergencia", fontsize=12,
                 fontweight="bold", pad=10)
    ax.grid(True, alpha=0.25, which="both")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=10)
    fig.tight_layout()
    return fig
 
 
# ══════════════════════════════════════════════
# 1b–5b. Sobrecargas que aceptan View-Models
# ══════════════════════════════════════════════
#
# Estas funciones aceptan view-models de gráficos estables en lugar de
# callables crudos + dicts de iteración. El renderizado interno es idéntico
# — el VM provee un wrapper tipificado que desacopla ``app.py`` de las
# claves de diccionario ad-hoc.
#
# Las firmas legacy basadas en dicts se mantienen sin cambios para
# compatibilidad hacia atrás.
#
# ══════════════════════════════════════════════


def graficar_funcion_vm(vm: "FunctionChartVM") -> plt.Figure:
    """Sobrecarga VM-aware — delega en ``graficar_funcion``."""
    return graficar_funcion(
        vm.function_callable,
        vm.x_min,
        vm.x_max,
        titulo=vm.title,
        raiz=vm.root,
    )


def graficar_iteracion_biseccion_vm(vm: "BisectionChartVM") -> plt.Figure:
    """Sobrecarga VM-aware — delega en ``graficar_iteracion_biseccion``."""
    return graficar_iteracion_biseccion(
        vm.function_callable,
        vm.iteration,
        x_min=vm.a,
        x_max=vm.b,
    )


def graficar_iteracion_newton_vm(vm: "NewtonChartVM") -> plt.Figure:
    """Sobrecarga VM-aware — delega en ``graficar_iteracion_newton``."""
    return graficar_iteracion_newton(
        vm.function_callable,
        vm.iteration,
        x_min=vm.x_previous,
        x_max=vm.x_next,
    )


def graficar_convergencia_vm(vm: "ConvergenceChartVM") -> plt.Figure:
    """Sobrecarga VM-aware — construye la lista de iteraciones desde la serie del VM."""
    # Reconstruct the iteration-dict format expected by the legacy function.
    iteraciones = [
        {"iteracion": entry["iteration"], "error_abs": entry["error_abs"]}
        for entry in vm.series
    ]
    return graficar_convergencia(iteraciones, metodo=vm.title)


# ══════════════════════════════════════════════
# 6. Secuencia completa de iteraciones
# ══════════════════════════════════════════════
 
def graficar_secuencia_biseccion(f, iteraciones: list,
                                  cols: int = 3) -> plt.Figure:
    """
    Genera una cuadrícula con todas las iteraciones de bisección.
    Útil para exportar o revisar el proceso completo de un vistazo.
    """
    n    = len(iteraciones)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 3.5))
    axes = np.array(axes).flatten()
 
    for idx, it in enumerate(iteraciones):
        graficar_iteracion_biseccion(f, it, ax=axes[idx])
 
    for idx in range(n, len(axes)):
        axes[idx].set_visible(False)
 
    fig.suptitle("Bisección — todas las iteraciones",
                 fontsize=13, fontweight="bold", y=1.01)
    fig.tight_layout()
    return fig
 
 
def graficar_secuencia_newton(f, iteraciones: list,
                               cols: int = 3) -> plt.Figure:
    """
    Genera una cuadrícula con todas las iteraciones de Newton-Raphson.
    """
    n    = len(iteraciones)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 3.5))
    axes = np.array(axes).flatten()
 
    for idx, it in enumerate(iteraciones):
        graficar_iteracion_newton(f, it, ax=axes[idx])
 
    for idx in range(n, len(axes)):
        axes[idx].set_visible(False)
 
    fig.suptitle("Newton-Raphson — todas las iteraciones",
                 fontsize=13, fontweight="bold", y=1.01)
    fig.tight_layout()
    return fig
 
# Mapa de arquitectura — ApproxRoots

Mapa completo de archivos y responsabilidades. Cada capa tiene una función concreta y dependencias controladas.

## Vista general

```
approxroots/
├── app.py                          ← Punto de entrada (Streamlit)
├── domain/
│   ├── models/
│   │   ├── bisection.py            ← Modelos de bisección
│   │   ├── newton.py               ← Modelos de Newton-Raphson
│   │   └── comparison.py           ← Modelos de comparación
│   └── solvers/
│       ├── bisection.py            ← Algoritmo de bisección
│       └── newton.py               ← Algoritmo de Newton-Raphson
├── application/
│   └── use_cases/
│       ├── run_bisection.py        ← Orquestación parse → solve (bisección)
│       ├── run_newton.py           ← Orquestación parse → solve (Newton)
│       └── run_comparison.py       ← Orquestación de ambos métodos
├── ui/
│   ├── presenters/
│   │   ├── bisection_presenter.py   ← BisectionResult → dicts para UI
│   │   ├── newton_presenter.py      ← NewtonResult → dicts para UI
│   │   ├── comparison_presenter.py  ← ComparisonResult → dicts para UI
│   │   └── chart_presenters.py      ← Construcción de view-models de gráficos
│   └── view_models/
│       └── charts.py                ← Dataclasses congeladas para gráficos
├── utils/
│   ├── func_parser.py              ← Compilación de expresiones (SymPy)
│   └── graficas.py                 ← Renderizado matplotlib
├── metodos/
│   ├── biseccion.py                ← Wrapper legacy de bisección
│   └── newton.py                   ← Wrapper legacy de Newton-Raphson
└── tests/
    ├── test_solver.py              ← Pruebas de solvers
    ├── test_use_case.py            ← Pruebas de casos de uso
    ├── test_presenter.py           ← Pruebas de presenters
    ├── test_parser.py              ← Pruebas del parser
    ├── test_app_session.py         ← Pruebas de helpers de sesión
    └── e2e_smoke.py                ← Prueba de integración
```

---

## `domain/models/bisection.py`

Estructuras de datos para el método de bisección.

| Elemento | Responsabilidad |
|---|---|
| `BisectionRequest` | Datos crudos desde la UI: expresión, `[a, b]`, tolerancia, máximo de iteraciones. |
| `SolverConfig` | Configuración numérica separada de la expresión. |
| `BisectionIteration` | Un paso del bucle numérico: número, `a`, `b`, punto medio, `f(xm)`, errores. |
| `BisectionResult` | Resultado tipificado: iteraciones, raíz, convergencia, status (`success`, `invalid_bracket`, `non_finite`, `max_iterations`, `parse_error`). |

---

## `domain/models/newton.py`

Estructuras de datos para Newton-Raphson.

| Elemento | Responsabilidad |
|---|---|
| `NewtonRequest` | Datos crudos desde la UI: expresión, `x0`, tolerancia, máximo de iteraciones. |
| `NewtonConfig` | Configuración numérica separada de la expresión. |
| `NewtonIteration` | Un paso del bucle: `x_previous`, `x_next`, `f(x)`, `df(x)`, errores, pendiente/intercepto de tangente. |
| `NewtonResult` | Resultado tipificado: iteraciones, raíz, convergencia, status (`success`, `derivative_zero`, `non_finite`, `max_iterations`, `parse_error`). |

---

## `domain/models/comparison.py`

Estructuras de datos para el flujo de comparación.

| Elemento | Responsabilidad |
|---|---|
| `ComparisonRequest` | Entrada combinada: expresión, `a`, `b` para bisección, `x0` para Newton. |
| `MethodSummary` | Resumen normalizado de un método dentro de la comparación. |
| `ComparisonResult` | Resultado combinado: resúmenes de ambos métodos, status global. |

---

## `domain/solvers/bisection.py`

Algoritmo de bisección puro. No sabe de Streamlit, parsing ni presentación.

| Función | Responsabilidad |
|---|---|
| `solve_bisection(evaluator, config)` | Valida el bracket, itera, calcula punto medio, detecta convergencia, retorna `BisectionResult`. |
| `_safe_evaluate(evaluator, x, label)` | Evalúa la función y rechaza NaN o infinito. |

No importa `streamlit`, `func_parser`, `matplotlib` ni `pandas`.

---

## `domain/solvers/newton.py`

Algoritmo de Newton-Raphson puro.

| Función | Responsabilidad |
|---|---|
| `solve_newton(f, df, config)` | Itera con paso de Newton, detecta derivada cero, evalúa convergencia, retorna `NewtonResult`. |
| `_safe_evaluate(evaluator, x, label)` | Evalúa la función y rechaza NaN o infinito. |

Mismas reglas de dependencia que el solver de bisección.

---

## `application/use_cases/run_bisection.py`

Coordina el flujo de bisección: compila la expresión, luego ejecuta el solver.

| Función | Responsabilidad |
|---|---|
| `run_bisection(request, compile_fn, solve_fn)` | 1) Compila con `compile_fn`. Si falla → `parse_error`. 2) Construye `SolverConfig`. 3) Llama a `solve_fn`. 4) Retorna `BisectionResult`. |

Acepta `compile_fn` y `solve_fn` como parámetros para testear con fakes.

---

## `application/use_cases/run_newton.py`

Coordina el flujo de Newton-Raphson.

| Función | Responsabilidad |
|---|---|
| `run_newton(request, compile_fn, derive_fn, solve_fn)` | 1) Compila función. 2) Compila derivada. 3) Construye `NewtonConfig`. 4) Llama a `solve_fn`. 5) Retorna `NewtonResult`. |

---

## `application/use_cases/run_comparison.py`

Coordina la ejecución de ambos métodos de forma secuencial dentro de una misma orquestación.

| Función | Responsabilidad |
|---|---|
| `run_comparison(request, ...)` | Recibe un `ComparisonRequest` con `bisection_a`, `bisection_b` y `newton_x0`, construye `BisectionRequest` y `NewtonRequest`, ejecuta ambos casos de uso, envuelve resultados en `MethodSummary`, retorna `ComparisonResult`. Hoy funciona como capa disponible de orquestación, pero `app.py` todavía compone `run_bisection` y `run_newton` directamente para renderizar comparación con todo el detalle de iteraciones. |

---

## `ui/presenters/bisection_presenter.py`

Adapta `BisectionResult` para la UI.

| Función | Responsabilidad |
|---|---|
| `present_bisection_result(result)` | Retorna dict con `iterations` (filas legacy), `metrics` (raíz, conteo, error, convergencia), `session` (para `st.session_state`). |

---

## `ui/presenters/newton_presenter.py`

Adapta `NewtonResult` para la UI.

| Función | Responsabilidad |
|---|---|
| `present_newton_result(result)` | Retorna dict con `iterations` (filas legacy con tangente), `metrics`, `session`. |

---

## `ui/presenters/comparison_presenter.py`

Adapta `ComparisonResult` para la UI.

| Función | Responsabilidad |
|---|---|
| `present_comparison_result(result)` | Retorna dict con `metrics` por método, `chart_data` normalizado, `combined_series` y `session`. Existe como pieza de arquitectura, aunque la vista principal de comparación todavía se apoya más en los presenters individuales. |

---

## `ui/presenters/chart_presenters.py`

Funciones constructoras de view-models para gráficos.

| Función | Responsabilidad |
|---|---|
| `build_bisection_chart_vm(fn, iteration)` | Construye `BisectionChartVM` desde callable de función y dict de iteración. |
| `build_newton_chart_vm(fn, iteration)` | Construye `NewtonChartVM` desde callable de función y dict de iteración. |
| `build_convergence_chart_vm(iterations, metodo)` | Construye `ConvergenceChartVM` con serie de error absoluto. |
| `build_function_chart_vm(fn, x_min, x_max, root)` | Construye `FunctionChartVM` para gráfica general. |
| `build_comparison_series(iters_bis, iters_nwt)` | Normaliza series de ambos métodos para gráfico de comparación. |

Estos builders ya ordenan mejor la arquitectura, pero la UI actual todavía consume en varios puntos los datos legacy directamente desde `app.py`.

---

## `ui/view_models/charts.py`

Dataclasses congeladas como payload para cada tipo de gráfico.

| View-model | Uso |
|---|---|
| `BisectionChartVM` | Datos para `graficar_iteracion_biseccion`: callable, `a`, `b`, `xm`. |
| `NewtonChartVM` | Datos para `graficar_iteracion_newton`: callable, `x_previous`, `x_next`, tangente. |
| `ConvergenceChartVM` | Serie de error absoluto por iteración para `graficar_convergencia`. |
| `FunctionChartVM` | Callable, rango, raíz para `graficar_funcion`. |

---

## `utils/func_parser.py`

Compilación de expresiones del usuario en callables numéricos.

| Función | Responsabilidad |
|---|---|
| `compile_expression(texto)` | Convierte `"x**3 - x - 2"` en `callable float → float`. Valida sintaxis y variable. |
| `compile_with_derivative(texto)` | Retorna `(f, df)` como callables. |
| `parsear_funcion(texto)` | API legacy: retorna `(f, df, expr, d_expr)`. |
| `validar_evaluacion(f, valor, nombre)` | Helper legacy para compatibilidad. |

---

## `utils/graficas.py`

Renderizado matplotlib. Cada función recibe datos ya calculados y produce una figura.

| Función | Responsabilidad |
|---|---|
| `graficar_funcion(f, x_min, x_max, ...)` | Gráfica general de `f(x)` con raíz marcada. |
| `graficar_iteracion_biseccion(f, iteracion, ...)` | Visualiza una iteración: función, marcas en `a`, `b`, `xm`. |
| `graficar_iteracion_newton(f, iteracion, ...)` | Visualiza una iteración: función, tangente, punto, nuevo `x`. |
| `graficar_convergencia(iteraciones, metodo)` | Error absoluto en escala logarítmica. |
| `graficar_comparacion(iters_bis, iters_nwt)` | Convergencia de ambos métodos en un mismo gráfico. |
| `graficar_secuencia_biseccion(f, iteraciones)` | Cuadrícula con todas las iteraciones de bisección. |
| `graficar_secuencia_newton(f, iteraciones)` | Cuadrícula con todas las iteraciones de Newton-Raphson. |

---

## `app.py`

Archivo principal de Streamlit. Conecta todas las capas:

1. Lee configuración del usuario (sidebar)
2. Construye request según el método seleccionado
3. Ejecuta el caso de uso correspondiente
4. Usa el presenter para obtener datos formateados
5. Renderiza con `st.metric`, `st.dataframe`, `st.pyplot` y las funciones de `graficas.py`

Incluye tres modos de vista:
- **Bisección** y **Newton-Raphson**: navegación iteración por iteración, tabla, gráfico de convergencia.
- **Comparación**: ambos métodos lado a lado con métricas y gráfico comparativo.

Importante: aunque `app.py` quedó bastante más fino que antes, sigue siendo el archivo más cargado del sistema. La arquitectura ya está separada en capas, pero la integración visual todavía conserva partes legacy para no romper comportamiento.

---

## `metodos/biseccion.py` y `metodos/newton.py`

Wrappers legacy que envuelven los solvers nuevos para compatibilidad.

Convierten resultados tipificados a la antigua firma `(list[dict], root, converged)`. Hoy sirven sobre todo para compatibilidad y pruebas, no como la ruta principal deseada de la UI.

---

## Pruebas (`tests/`)

| Archivo | Qué prueba |
|---|---|
| `test_solver.py` | Solvers: convergencia, intervalos sin signo, valores no finitos, máx. iteraciones, ausencia de imports prohibidos. |
| `test_use_case.py` | Casos de uso: flujo exitoso, fallo de parser (no llama al solver), orden parse → solve. Usa fakes. |
| `test_presenter.py` | Presenters: mapeo de claves legacy, métricas, payload de sesión, resultados vacíos. |
| `test_parser.py` | Parser: expresiones válidas, sintaxis inválida, variable no permitida. |
| `test_app_session.py` | Helpers de sesión de app.py: `_apply_comparison_session`, `_clear_failed_run_state`. |
| `e2e_smoke.py` | Flujo completo real: parse → solve → presenter → wrapper legacy. |

---

## Flujo de datos

```
Usuario escribe f(x) y parámetros
        │
        ▼
app.py construye requests por método
        │
        ├── BisectionRequest → run_bisection → present_bisection_result
        ├── NewtonRequest    → run_newton    → present_newton_result
        └── (arquitectura disponible) ComparisonRequest → run_comparison → present_comparison_result
        │
        ▼
app.py decide la vista final:
  - método individual
  - comparación completa
  - comparación parcial
  - error
        │
        ▼
app.py renderiza con:
  - st.metric / st.dataframe
  - graficar_iteracion_biseccion / graficar_iteracion_newton
  - graficar_convergencia / graficar_comparacion
```

## Reglas de dependencia

```
app.py
  → application/use_cases/
  → domain/models/
  → ui/presenters/
  → utils/
  → metodos/ (legacy)

application/use_cases/
  → domain/models/
  → utils/ (solo compile_fn/derive_fn, inyectadas)

domain/solvers/
  → domain/models/

ui/presenters/
  → domain/models/

ui/view_models/
  → (ninguna)

utils/func_parser.py
  → sympy, numpy

utils/graficas.py
  → numpy, matplotlib
```

Ninguna capa de dominio importa `streamlit`, `pandas` ni `matplotlib`. El solver nunca llama al parser ni viceversa.

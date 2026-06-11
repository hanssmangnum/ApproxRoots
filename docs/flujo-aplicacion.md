# Flujo de la aplicación — ApproxRoots

Cómo se mueven los datos a través del sistema para cada modo: bisección, Newton-Raphson y comparación.

## Flujo general

```
[Sidebar]                         app.py
    │
    ├── f(x), a, b, tol, max_iter  ──→  BisectionRequest
    ├── f(x), x₀, tol, max_iter    ──→  NewtonRequest
    └── f(x), a, b, x₀, tol,       ──→  requests por método para comparación
         max_iter
                              │
                              ▼
                      Caso de uso por método
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
              func_parser          domain/solvers/
           (compile_expression)    (solve_bisection
            compile_with_           solve_newton)
            derivative)                 │
                    │                   │
                    └─────────┬─────────┘
                              ▼
                       *Result
                              │
                              ▼
                       Presenter
                    (present_*_result)
                              │
                              ▼
                   app.py decide la vista:
                   completa, parcial o error
```

Nota: la arquitectura ya tiene `ComparisonRequest`, `run_comparison()` y `present_comparison_result()`, pero el flujo activo de la UI todavía compone bisección y Newton por separado para conservar el detalle completo de iteraciones.

## Bisección

```
app.py (sidebar)
  │  fn_texto, a, b, tol, max_iter
  ▼
BisectionRequest(expression, a, b, tolerance, max_iter)
  │
  ▼
run_bisection(request, compile_fn=compile_expression, solve_fn=solve_bisection)
  │
  ├── compile_expression(texto) → evaluador callable (float → float)
  │     Si falla → BisectionResult(status="parse_error")
  │
  └── solve_bisection(evaluator, SolverConfig(a, b, tol, max_iter))
        │
        ├── Valida: f(a)·f(b) < 0
        ├── Edge case: f(a)=0 o f(b)=0 → raíz exacta sin iteraciones
        ├── Bucle: midpoint = (a+b)/2, evalúa, ajusta intervalo
        └── Retorna: BisectionResult(iterations, root, converged, status)
  │
  ▼
present_bisection_result(result)
  │
  └── dict { iterations, metrics, session }
        │
        ▼
app.py:
  - st.metric: raíz, f(raíz), total iteraciones, error final, badge
  - st.dataframe: tabla de iteraciones
  - graficar_iteracion_biseccion(): navegación paso a paso
  - graficar_convergencia(): escala logarítmica del error
```

## Newton-Raphson

```
app.py (sidebar)
  │  fn_texto, x₀, tol, max_iter
  ▼
NewtonRequest(expression, x0, tolerance, max_iter)
  │
  ▼
run_newton(request, compile_fn=compile_expression, derive_fn=compile_with_derivative, solve_fn=solve_newton)
  │
  ├── compile_expression(texto) → evaluador f
  ├── compile_with_derivative(texto)[1] → evaluador df
  │     Si falla → NewtonResult(status="parse_error")
  │
  └── solve_newton(f, df, NewtonConfig(x0, tol, max_iter))
        │
        ├── Bucle: x_next = x - f(x)/df(x)
        ├── Valida: df(x) ≈ 0 → status="derivative_zero"
        ├── Valida: valores finitos → status="non_finite"
        └── Retorna: NewtonResult(iterations, root, converged, status)
  │
  ▼
present_newton_result(result)
  │
  └── dict { iterations (con tangente), metrics, session }
        │
        ▼
app.py:
  - st.metric: raíz, f(raíz), iteraciones, error, badge
  - graficar_iteracion_newton(): curva + tangente + punto
  - graficar_convergencia(): escala logarítmica
```

## Comparación

```
app.py (sidebar)
  │  fn_texto, a, b, x₀, tol, max_iter
  ▼
Construye BisectionRequest y NewtonRequest
  │
  ├── run_bisection(...)
  │     └── present_bisection_result(...)
  │
  └── run_newton(...)
        └── present_newton_result(...)
  │
  ▼
app.py decide el estado visual:
  - comparación completa (ambos exitosos)
  - comparación parcial (uno exitoso, otro falla)
  - error total (ambos fallan)
  │
  ▼
app.py:
  - st.metric: raíces, conteos, estados
  - graficar_comparacion() o gráfico individual según el caso
  - st.dataframe: tabla del método disponible
  - st.warning / st.error: explicación del método que falló
```

Nota: `run_comparison()` y `present_comparison_result()` ya existen como piezas de arquitectura separada. `ComparisonRequest` usa los campos `bisection_a`, `bisection_b` y `newton_x0`, pero la app actual todavía usa la composición directa de ambos métodos para conservar el detalle completo de iteraciones en pantalla.

## Mapa de tipos entre capas

| Capa origen | Tipo | Capa destino | Tipo |
|---|---|---|---|
| UI (sidebar) | `float`, `str` | Caso de uso | `*Request` |
| Caso de uso | `*Request` | Parser | `str` |
| Caso de uso | `SolverConfig` / `NewtonConfig` | Solver | `*Config` |
| Parser | `callable float→float` | Solver | `callable` |
| Solver | `*Result` | Caso de uso | `*Result` |
| Caso de uso | `*Result` | Presenter | `*Result` |
| Presenter | `dict` | app.py | `dict` |
| app.py | `dict` | `graficas.py` | `dict` + `callable` |

## Estados de salida

### BisectionResult

| status | Significado |
|---|---|
| `success` | Convergió dentro de la tolerancia |
| `invalid_bracket` | f(a) y f(b) no cambian de signo |
| `non_finite` | Evaluador devolvió NaN o infinito |
| `max_iterations` | No convergió en el límite de iteraciones |
| `parse_error` | La expresión no pudo compilarse |

### NewtonResult

| status | Significado |
|---|---|
| `success` | Convergió dentro de la tolerancia |
| `derivative_zero` | La derivada es prácticamente cero |
| `non_finite` | Evaluador devolvió NaN o infinito |
| `max_iterations` | No convergió en el límite de iteraciones |
| `parse_error` | La expresión no pudo compilarse |

### ComparisonResult

| status | Significado |
|---|---|
| `success` | Ambos métodos se ejecutaron (pueden haber convergido o no) |
| `parse_error` | La expresión no pudo compilarse para ningún método |

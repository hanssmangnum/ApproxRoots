# Arquitectura de ApproxRoots

## Idea central

Cada parte del sistema hace **un solo trabajo** y lo hace bien. La UI no calcula raíces, el solver no construye tablas, el parser no decide reglas numéricas.

## Por qué está separada así

Cuando la interfaz, el parsing, el cálculo y la presentación viven mezclados:

- cuesta saber dónde corregir un error,
- un cambio visual puede romper la matemática,
- probar una parte sin ejecutar toda la app se vuelve complicado,
- y agregar un método nuevo implica tocar código existente con riesgo alto.

Separar por capas resuelve eso: cada pieza tiene dependencias controladas y se puede entender, cambiar y probar de forma aislada.

## Capas

```
[ Usuario ]
     |
     v
[ app.py ]  ← Punto de entrada (Streamlit)
     |
     +---> [ Casos de uso ]  ← Coordinan el flujo
     |          |
     |          +---> [ Parser ]      ← Compila la expresión
     |          +---> [ Solvers ]     ← Algoritmo numérico puro
     |
     +---> [ Presenters ]  ← Transforman dominio → UI
     |
     +---> [ Chart VMs ]   ← View-models tipificados para gráficos
     |
     +---> [ utils/graficas.py ]  ← Renderizado matplotlib
```

### 1. Modelos de dominio (`domain/models/`)

Dataclasses congeladas que definen los contratos entre capas. No contienen lógica.

- `BisectionRequest`, `SolverConfig`, `BisectionIteration`, `BisectionResult`
- `NewtonRequest`, `NewtonConfig`, `NewtonIteration`, `NewtonResult`
- `ComparisonRequest`, `MethodSummary`, `ComparisonResult`

Regla: no importan nada de `application/`, `ui/` ni `metodos/`.

### 2. Solvers (`domain/solvers/`)

Algoritmos numéricos **puros**. Reciben un evaluador de función (callable) y config, y devuelven un resultado tipificado.

- `solve_bisection(evaluator, config)` — reduce el intervalo por bisección y converge de forma lineal.
- `solve_newton(f, df, config)` — Newton-Raphson: paso tangente, convergencia cuadrática.

Regla: no importan `streamlit`, `matplotlib`, `pandas` ni el parser. Se verifica en tests.

### 3. Parser (`utils/func_parser.py`)

Compila la expresión del usuario en callables numéricos usando SymPy. No sabe nada de métodos numéricos.

- `compile_expression(texto)` → `callable float → float` (para bisección)
- `compile_with_derivative(texto)` → `(f_callable, df_callable)` (para Newton)
- `parsear_funcion(texto)` — API legacy que retorna tupla completa

Regla: no valida intervalos, signos ni convergencia. Eso es trabajo del solver.

### 4. Casos de uso (`application/use_cases/`)

Coordinan el flujo: reciben un request, llaman al parser, llaman al solver, devuelven el resultado. No contienen lógica de negocio ni de presentación.

- `run_bisection(request, compile_fn, solve_fn)`
- `run_newton(request, compile_fn, derive_fn, solve_fn)`
- `run_comparison(`
  `request, compile_fn, derive_fn, run_bisection_fn, run_newton_fn, bisection_solve_fn, newton_solve_fn` `)`

Aceptan las funciones colaboradoras como parámetros para poder probarse con fakes.

En el caso de `run_comparison`, eso significa que el caso de uso recibe explícitamente:

- el compilador de función,
- el compilador de derivada,
- el caso de uso de bisección,
- el caso de uso de Newton,
- el solver de bisección,
- y el solver de Newton.

Nota importante: en la app actual, el modo **Comparación** todavía arma la vista final ejecutando `run_bisection` y `run_newton` por separado para conservar todas las iteraciones, tablas y métricas. `run_comparison` ya existe como contrato de arquitectura y como base de evolución, pero no es todavía la única ruta activa de render.

### 5. Presenters (`ui/presenters/`)

Adaptan el resultado del dominio al formato que la UI necesita. Convierten objetos tipados en diccionarios planos.

- `present_bisection_result(result)` → dict con `iterations`, `metrics`, `session`
- `present_newton_result(result)` → dict con `iterations`, `metrics`, `session`
- `present_comparison_result(result)` → dict con `metrics`, `chart_data`, `combined_series`, `session`

En la práctica actual, `present_comparison_result` complementa la arquitectura, pero la vista principal de comparación todavía se apoya sobre los presenters individuales de bisección y Newton para mostrar el detalle completo.

### 6. Chart view-models (`ui/view_models/`)

Dataclasses congeladas que encapsulan los datos que cada gráfico necesita. Separan la construcción de los datos de su renderizado.

- `BisectionChartVM`, `NewtonChartVM`, `ConvergenceChartVM`, `FunctionChartVM`

### 7. Chart presenters (`ui/presenters/chart_presenters.py`)

Funciones que construyen view-models a partir de datos del presenter y callables de función. Puente entre los datos de iteración y los gráficos.

- `build_bisection_chart_vm(fn, iteration)` → `BisectionChartVM`
- `build_newton_chart_vm(fn, iteration)` → `NewtonChartVM`
- `build_convergence_chart_vm(iterations, metodo)` → `ConvergenceChartVM`
- `build_function_chart_vm(fn, x_min, x_max, root)` → `FunctionChartVM`

### 8. Gráficas (`utils/graficas.py`)

Renderizado matplotlib puro. Cada función recibe datos ya preparados y produce una figura.

Nota importante: esta capa ya tiene soporte para view-models, pero `app.py` todavía usa en varios puntos las rutas legacy basadas en diccionarios de iteración. La abstracción ya está creada; la integración visual todavía no migró al 100%.

### 9. Punto de entrada (`app.py`)

Orquesta todo: recibe datos del usuario, construye requests, llama a casos de uso, usa presenters, renderiza con Streamlit + matplotlib. Es la única capa que conoce Streamlit.

### 10. Wrappers legacy (`metodos/`)

Puente de compatibilidad que envuelve los nuevos solvers para conservar compatibilidad con pruebas, utilidades heredadas y posibles flujos antiguos.

- `biseccion(f, a, b, tol, max_iter)` → tupla `(iters, root, converged)`
- `newton_raphson(f, df, x0, tol, max_iter)` → tupla `(iters, root, converged)`

En la app actual, la ruta principal ya intenta apoyarse en casos de uso y presenters. Los wrappers quedan como compatibilidad, no como ruta principal ideal.

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
  → utils/ (inyectado como callable)

domain/solvers/
  → domain/models/

ui/presenters/
  → domain/models/

ui/view_models/
  → (ninguna — son dataclasses puras)

ui/presenters/chart_presenters.py
  → ui/view_models/

utils/func_parser.py
  → sympy, numpy

utils/graficas.py
  → numpy, matplotlib
```

Ninguna capa de dominio importa `streamlit`, `pandas` ni `matplotlib`. El solver nunca llama al parser ni viceversa.

## Qué métodos cubre

| Método | Solvers | Casos de uso | Presenters |
|--------|---------|-------------|------------|
| Bisección | `domain/solvers/bisection.py` | `run_bisection` | `bisection_presenter.py` |
| Newton-Raphson | `domain/solvers/newton.py` | `run_newton` | `newton_presenter.py` |
| Comparación | (usa ambos solvers) | `run_comparison` | `comparison_presenter.py` |

## Lo que se gana

- **Claridad:** cada archivo tiene un propósito que se explica en una línea.
- **Aislamiento:** cambiar la UI no rompe la matemática.
- **Testeabilidad:** cada capa se prueba con fakes sin Streamlit.
- **Extensibilidad:** agregar un método nuevo implica crear su modelo, solver, caso de uso y presenter sin tocar el resto.

# Mapa de arquitectura — Bisección

Mapa de archivos y responsabilidades del método de bisección en ApproxRoots. Cada capa tiene una función concreta y dependencias controladas.

## Vista general de directorios

```
approxroots/
├── app.py                              ← Punto de entrada (UI Streamlit)
├── domain/models/bisection.py          ← Tipos y contratos
├── domain/solvers/bisection.py         ← Algoritmo numérico puro
├── application/use_cases/run_bisection.py  ← Orquestación parse → solve
├── ui/presenters/bisection_presenter.py    ← Adaptación dominio → UI
├── utils/
│   ├── func_parser.py                  ← Compilación de expresiones
│   └── graficas.py                     ← Visualización (Matplotlib)
├── metodos/
│   ├── biseccion.py                    ← Wrapper legacy (tuplas → dominio)
│   └── newton.py                       ← Newton-Raphson (sin refactor)
└── tests/
    ├── test_solver.py                  ← Pruebas del solver
    ├── test_use_case.py                ← Pruebas del caso de uso
    ├── test_presenter.py               ← Pruebas del presenter
    ├── test_parser.py                  ← Pruebas del parser
    └── e2e_smoke.py                    ← Prueba de integración
```

---

## Capa 1: Modelos de dominio (`domain/models/bisection.py`)

Define las estructuras de datos que todas las demás capas usan para comunicarse. No contiene lógica de negocios ni algoritmos.

| Elemento | Responsabilidad |
|---|---|
| `BisectionRequest` | Datos crudos que llegan desde la UI: expresión, intervalo `[a, b]`, tolerancia, máximo de iteraciones. |
| `SolverConfig` | Configuración numérica ya separada de la expresión. Solo contiene `a`, `b`, `tolerance`, `max_iterations`. |
| `BisectionIteration` | Una iteración individual del bucle numérico: número de paso, `a`, `b`, punto medio, `f(xm)`, errores. |
| `BisectionResult` | Resultado tipado del solver: lista de iteraciones, raíz aproximada, si convergió, estado (`success`, `invalid_bracket`, `non_finite`, `max_iterations`, `parse_error`) y mensaje de error opcional. |

Regla: estas clases **no importan** nada de `application/`, `ui/` ni `metodos/`.

---

## Capa 2: Solver numérico (`domain/solvers/bisection.py`)

Contiene el algoritmo de bisección como código **puramente matemático**. No sabe nada de Streamlit, de parsing, ni de cómo se van a mostrar los resultados.

| Función | Responsabilidad |
|---|---|
| `solve_bisection(evaluator, config)` | Ejecuta el bucle numérico. Valida el cambio de signo, itera, calcula punto medio, evalúa la función, detecta convergencia y devuelve un `BisectionResult`. |
| `_safe_evaluate(evaluator, x, label)` | Evalúa la función en un punto y rechaza valores `NaN` o infinito. |

Regla: este archivo **no puede importar** `streamlit`, `func_parser`, `matplotlib` ni `pandas`. Se verifica en `test_solver.py`.

---

## Capa 3: Caso de uso (`application/use_cases/run_bisection.py`)

Coordina el flujo: primero compila la expresión, luego ejecuta el solver. No contiene lógica de parsing ni de visualización.

| Función | Responsabilidad |
|---|---|
| `run_bisection(request, compile_fn, solve_fn)` | 1) Compila la expresión con `compile_fn`. Si falla, devuelve `parse_error`. 2) Construye un `SolverConfig`. 3) Llama a `solve_fn`. 4) Retorna el `BisectionResult`. |

Acepta `compile_fn` y `solve_fn` como parámetros para poder probarse con dobles de prueba (fakes) sin tocar el parser real ni el solver real.

---

## Capa 4: Presenter (`ui/presenters/bisection_presenter.py`)

Transforma el `BisectionResult` del dominio en un formato que la UI puede consumir directamente. No contiene lógica matemática ni de navegación.

| Función | Responsabilidad |
|---|---|
| `present_bisection_result(result)` | Devuelve un diccionario con: `iterations` (filas con claves legacy como `iteracion`, `a`, `b`, `xm`, `f(xm)`), `metrics` (raíz, conteo, error final, convergencia), y `session` (datos listos para volcar en `st.session_state`). |

---

## Capa 5: Utilidades (`utils/`)

### `utils/func_parser.py`

Compila la expresión escrita por el usuario en una función numérica evaluable. No decide reglas del método.

| Función | Responsabilidad |
|---|---|
| `compile_expression(texto)` | Entrada para bisección: convierte texto como `"x**3 - x - 2"` en un callable `float → float`. Solo valida sintaxis y variable, **no** valida intervalos ni signos. |
| `parsear_funcion(texto)` | API legacy para Newton-Raphson: devuelve `(f, df, expr, d_expr)`. |
| `validar_evaluacion(f, valor, nombre)` | Helper legacy que evalúa y verifica que el resultado sea finito. |

### `utils/graficas.py`

Funciones de visualización con Matplotlib. Cada una recibe los datos ya calculados y produce una figura.

| Función | Responsabilidad |
|---|---|
| `graficar_funcion(f, x_min, x_max, ...)` | Gráfica general de `f(x)` en un rango. |
| `graficar_iteracion_biseccion(f, iteracion, ...)` | Visualiza una iteración de bisección: función, marcas en `a`, `b`, `xm`, sombreado del intervalo. |
| `graficar_iteracion_newton(f, iteracion, ...)` | Visualiza una iteración de Newton-Raphson: función, punto de tangencia, recta tangente, nuevo `x`. |
| `graficar_convergencia(iteraciones, metodo)` | Error absoluto en escala logarítmica por iteración. |
| `graficar_comparacion(iters_bis, iters_nwt)` | Compara convergencia de ambos métodos en un mismo gráfico. |
| `graficar_secuencia_biseccion(f, iteraciones)` | Cuadrícula con todas las iteraciones de bisección. |
| `graficar_secuencia_newton(f, iteraciones)` | Cuadrícula con todas las iteraciones de Newton-Raphson. |

---

## Capa 6: Punto de entrada (`app.py`)

Archivo principal de Streamlit. Conecta todas las capas: recibe datos del usuario, construye un `BisectionRequest`, llama a `run_bisection`, usa `present_bisection_result` para obtener datos formateados, y los muestra con las funciones de `graficas.py`.

Aunque `app.py` usa la nueva arquitectura de bisección, también conserva las rutas legacy para Newton-Raphson y el modo Comparación mediante `metodos/biseccion.py` y `metodos/newton.py`.

---

## Capa 7: Compatibilidad legacy (`metodos/biseccion.py`)

Envuelve el solver nuevo para que el modo Comparación y Newton-Raphson sigan funcionando sin cambios. Convierte `SolverConfig` + `solve_bisection()` a la antigua firma `(list[dict], root, converged)`.

---

## Capa 8: Pruebas (`tests/`)

| Archivo | Qué prueba |
|---|---|
| `test_solver.py` | Límites del solver: convergencia, intervalo sin cambio de signo, valores no finitos, máximo de iteraciones, ausencia de imports prohibidos. |
| `test_use_case.py` | Orquestación del caso de uso: flujo exitoso, fallo de parser (no llama al solver), orden parse → solve. Usa fakes. |
| `test_presenter.py` | Mapeo de datos: claves legacy, conteo de iteraciones, métricas, payload de sesión, resultados vacíos. |
| `test_parser.py` | Compilación: expresiones válidas, sintaxis inválida, variable no permitida, ausencia de validación de intervalo. |
| `e2e_smoke.py` | Flujo completo real: parse → solve → presenter → wrapper legacy. |

---

## Flujo de datos

```
Usuario escribe f(x) y parámetros
        │
        ▼
app.py construye BisectionRequest
        │
        ▼
run_bisection(request, compile_expression, solve_bisection)
        │
        ├── compile_expression(texto)  →  callable evaluator
        │
        └── solve_bisection(evaluator, SolverConfig)  →  BisectionResult
        │
        ▼
present_bisection_result(result)  →  dict con iterations + metrics + session
        │
        ▼
app.py renderiza con:
  - st.metric / st.dataframe
  - graficar_iteracion_biseccion()
  - graficar_convergencia()
```

---

## Reglas de dependencia

```
app.py
  → application/use_cases/
  → ui/presenters/
  → utils/
  → metodos/ (legacy)

application/use_cases/
  → domain/models/
  → utils/ (solo compile_fn, inyectada)

domain/solvers/
  → domain/models/

ui/presenters/
  → domain/models/

utils/func_parser.py
  → sympy, numpy

utils/graficas.py
  → numpy, matplotlib
```

Ninguna capa de dominio importa `streamlit`, `pandas` ni `matplotlib`. El solver nunca llama al parser ni viceversa.

# Resumen del cambio: separación de bisección

Este cambio reorganiza la parte del método de bisección para que sea más clara, más fácil de mantener y mucho más fácil de probar.

Antes, una misma parte del sistema hacía demasiadas cosas al mismo tiempo:

- mostraba la interfaz,
- interpretaba la función escrita por el usuario,
- ejecutaba el cálculo numérico,
- y preparaba los datos para la tabla y los gráficos.

Ahora esas responsabilidades están separadas.

## ¿Qué se buscó resolver?

El problema principal era el acoplamiento.

Cuando la interfaz, el parsing y el cálculo viven juntos:

- cuesta entender el flujo,
- es más fácil introducir errores,
- y probar una parte sin tocar la otra se vuelve difícil.

En términos simples: si una sola pieza hace todo, cualquier cambio pequeño puede romper varias cosas a la vez.

## ¿Qué cambió?

La ruta de bisección ahora se divide en partes más claras:

### 1. Interfaz
La interfaz sigue encargándose de lo visual:

- recibir datos del usuario,
- mostrar resultados,
- renderizar tablas y gráficos.

### 2. Parsing
El parsing ahora se enfoca en una sola tarea:

- tomar la expresión ingresada por el usuario,
- validarla como expresión,
- y dejarla lista para ser evaluada.

No decide reglas del método numérico.

### 3. Cálculo numérico
La lógica de bisección quedó separada como cálculo puro.

Su responsabilidad es:

- revisar el intervalo,
- calcular iteraciones,
- determinar si hay convergencia,
- devolver el resultado.

### 4. Presentación de resultados
También se agregó una capa que transforma el resultado del cálculo al formato que la interfaz necesita.

Esto evita que el algoritmo tenga que “pensar” en tablas o gráficos.

## ¿Por qué esto es mejor?

Porque cada parte tiene una responsabilidad clara.

Eso permite:

- entender más rápido el sistema,
- cambiar una parte con menos riesgo,
- probar el cálculo sin depender de la interfaz,
- y reutilizar mejor la lógica en el futuro.

## Ejemplo sencillo

Antes:

> La misma ruta recibía la función, la procesaba, calculaba la bisección y armaba la salida visual.

Ahora:

> La interfaz pide el cálculo, el parser prepara la función, el caso de uso coordina, el solver resuelve y el presenter adapta el resultado para mostrarlo.

## Diagrama simple del flujo

```text
Usuario
  |
  v
Interfaz (Streamlit)
  |
  v
Caso de uso de bisección
  |
  +--> Parser
  |      - interpreta la expresión
  |      - la deja lista para evaluar
  |
  +--> Solver de bisección
         - valida el intervalo
         - calcula iteraciones
         - decide convergencia
  |
  v
Presenter
  |
  v
Tabla + métricas + gráficos
```

## Tests agregados

Se agregaron pruebas para cubrir las partes más importantes:

- pruebas del solver de bisección,
- pruebas del parser,
- pruebas del caso de uso,
- pruebas del presenter,
- y una prueba de humo del flujo completo.

## ¿Qué protegen esos tests?

- Que la matemática siga funcionando bien.
- Que el parser no empiece a hacer trabajo que no le corresponde.
- Que la coordinación entre capas mantenga el orden correcto.
- Que la interfaz siga recibiendo datos en el formato esperado.

## Qué quedó fuera de este cambio

Este trabajo se concentró en bisección.

No se buscó todavía:

- refactorizar Newton-Raphson con la misma profundidad,
- rehacer todo el modo comparación,
- ni rediseñar toda la aplicación.

## En una frase

Este cambio hace que bisección sea más fácil de entender, de probar y de evolucionar, porque separa claramente la interfaz, el parsing, el cálculo y la presentación.

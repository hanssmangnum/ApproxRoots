# Arquitectura de bisección explicada de forma simple

## Idea principal

La arquitectura nueva busca algo muy sencillo:

**que cada parte del sistema haga solo el trabajo que le corresponde.**

Eso puede sonar obvio, pero es una de las diferencias más importantes entre un sistema frágil y uno que se puede mantener con tranquilidad.

## El problema de antes

Cuando una sola parte mezcla muchas responsabilidades, pasan estas cosas:

- cuesta saber dónde corregir un error,
- cuesta agregar mejoras sin miedo,
- cuesta probar la lógica real,
- y el código empieza a depender demasiado de la interfaz.

Es como tener una oficina donde la misma persona atiende, calcula, archiva, valida y además prepara los reportes. Puede funcionar por un tiempo, pero no escala bien y cualquier cambio genera confusión.

## La idea de la separación

Para evitar eso, se separó la bisección en capas fáciles de entender.

## Diagrama de arquitectura

```text
[ Usuario ]
     |
     v
[ UI / Streamlit ]
  Recibe datos y muestra resultados
     |
     v
[ Use case / run_bisection ]
  Coordina el flujo
     |
     +-------------------+
     |                   |
     v                   v
[ Parser ]           [ Solver ]
Interpreta           Calcula la
la expresión         bisección
     |                   |
     +---------+---------+
               |
               v
        [ BisectionResult ]
               |
               v
         [ Presenter ]
  Adapta el resultado para la UI
               |
               v
     [ tablas, métricas, gráficos ]
```

## Cómo leer este diagrama

- La **UI** habla con el caso de uso, no con toda la lógica interna.
- El **caso de uso** coordina el trabajo.
- El **parser** interpreta la expresión, pero no decide reglas matemáticas del método.
- El **solver** resuelve bisección y valida lo que le corresponde al método.
- El **presenter** convierte el resultado a un formato cómodo para mostrar.

## 1. UI: la parte visible

La interfaz tiene que encargarse de lo que el usuario ve y usa:

- campos de entrada,
- botones,
- mensajes,
- tablas,
- gráficos.

La UI no debería contener la lógica matemática del método.

### ¿Por qué?

Porque la interfaz cambia por razones visuales o de experiencia de usuario.
La matemática cambia por reglas numéricas.

Son motivos distintos. Si ambas cosas están mezcladas, cualquier ajuste visual puede tocar lógica sensible.

## 2. Parsing: entender la expresión

El parsing debería hacer una sola cosa: entender la expresión escrita por el usuario y dejarla lista para usarse.

Por ejemplo:

- recibir `x**3 - x - 2`,
- verificar que la expresión tenga sentido,
- prepararla para evaluación.

### ¿Por qué no debería hacer más?

Porque decidir si un intervalo sirve para bisección, o si el método converge, ya no es parsing. Eso pertenece al método numérico.

Si el parser empieza a decidir reglas matemáticas, deja de ser una pieza simple y clara.

## 3. Solver: resolver el problema numérico

El solver es la parte que realmente sabe hacer bisección.

Se encarga de:

- validar el intervalo desde la lógica del método,
- iterar,
- calcular aproximaciones,
- detectar convergencia,
- devolver un resultado confiable.

### ¿Por qué debe estar aislado?

Porque esta es la parte más importante desde el punto de vista matemático.

Si está aislada:

- se prueba mejor,
- se entiende mejor,
- y no depende de detalles de pantalla o de presentación.

## 4. Use case: coordinar el flujo

El caso de uso hace de coordinador.

No muestra cosas y no hace todo el cálculo por sí mismo. Su trabajo es ordenar el proceso:

1. recibe la solicitud,
2. llama al parsing,
3. llama al solver,
4. devuelve el resultado.

### ¿Por qué es útil?

Porque deja el flujo de negocio en un solo lugar.

Así la UI no necesita saber demasiados detalles internos.

## 5. Presenter: adaptar la salida

El presenter toma el resultado del dominio y lo convierte al formato que la interfaz necesita.

### ¿Por qué no hacerlo dentro del solver?

Porque el solver debería pensar en resultados matemáticos, no en tablas o gráficos.

Si mezcla ambas cosas, la lógica numérica queda atada a una forma específica de mostrar datos.

## ¿Por qué esta arquitectura debería mantenerse así?

Porque da beneficios concretos:

### Más claridad
Cada parte tiene un propósito fácil de explicar.

### Menos riesgo
Un cambio visual no debería romper la matemática.

### Mejor testeo
Se puede probar cada parte de forma aislada.

### Mejor evolución
En el futuro se puede aplicar la misma idea a otros métodos, como Newton-Raphson.

## Qué se gana a nivel práctico

- detectar errores más rápido,
- incorporar mejoras con menos miedo,
- mantener el proyecto más ordenado,
- facilitar que otras personas entiendan el flujo.

## Regla simple para recordar

Si una parte del sistema empieza a hacer trabajo de otra, el diseño se empieza a degradar.

Una forma simple de recordarlo es esta:

- **UI**: muestra
- **Parser**: interpreta
- **Use case**: coordina
- **Solver**: calcula
- **Presenter**: adapta

Si esas fronteras se respetan, el sistema sigue sano.

## Cierre

Esta arquitectura no existe para “hacer el proyecto más complejo”.

Existe para que el proyecto sea **más entendible, más estable y más fácil de mantener**.

Ese es el motivo real por el que vale la pena sostener esta separación.

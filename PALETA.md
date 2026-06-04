## 🎨 Paleta de Colores y Guía de Interfaz (UI)

Para garantizar una experiencia visual clara, interactiva y de alto contraste en el modo oscuro del visualizador, se definió la siguiente estructura y jerarquía de colores:

### 🕋 Capas de Fondo y Contenedores

| Color | Código Hex | Uso en la Interfaz |
| :---: | :--- | :--- |
| ![#1C1C1E](https://img.shields.io/badge/-1C1C1E-1C1C1E?style=flat-square) | `#1C1C1E` | **Fondo Oscuro Principal:** Lienzo general de toda la aplicación. Reduce la fatiga visual durante la simulación de las iteraciones. |
| ![#2B2B2E](https://img.shields.io/badge/-2B2B2E-2B2B2E?style=flat-square) | `#2B2B2E` | **Superficie Gris:** Tarjetas contenedoras, paneles de configuración lateral (sidebar), bordes secundarios y marcos de los gráficos. |

### 🔮 Identidad del Sistema (Tonos Morados)

* **![#68097E](https://img.shields.io/badge/-68097E-68097E?style=flat-square) `#68097E` (Morado Base):** Color de marca del proyecto. Aplicado en barras de navegación, encabezados de secciones y estados activos del menú.
* **![#C91CCA](https://img.shields.io/badge/-C91CCA-C91CCA?style=flat-square) `#C91CCA` (Acento Morado):** Utilizado para resaltar elementos interactivos secundarios, efectos *hover* al pasar el mouse sobre los botones y textos destacados.

### 📈 Componentes del Gráfico Matemático

* **![#FFCA06](https://img.shields.io/badge/-FFCA06-FFCA06?style=flat-square) `#FFCA06` (Amarillo de Alto Contraste):** El color de mayor jerarquía visual. Se usa exclusivamente para renderizar la **curva de la función principal $f(x)$** y el punto exacto de la **aproximación de la raíz**.
* **![#E8675C](https://img.shields.io/badge/-E8675C-E8675C?style=flat-square) `#E8675C` (Coral / Rojo):** Representa de forma gráfica los límites del intervalo $[a, b]$ en el método de Bisección y las **rectas tangentes** en el método de Newton-Raphson.
* **![#00E5CC](https://img.shields.io/badge/-00E5CC-00E5CC?style=flat-square) `#00E5CC` (Cian / Azul):** Indica visualmente las líneas de proyección hacia el eje X que marcan la convergencia y los mensajes de éxito cuando el algoritmo encuentra la raíz.

### 📊 Datos y Estados del Sistema

* **![#FFFFFFEB](https://img.shields.io/badge/-FFFFFFEB-FFFFFF?style=flat-square) `#FFFFFFEB` (Blanco Semitransparente - 92%):** Fondo exclusivo para el **panel de la tabla de iteraciones**. Al ser claro y traslúcido, rompe con la oscuridad general para ofrecer una lectura limpia de las columnas numéricas (errores absolutos, relativos, etc.).
* **![#E8675C](https://img.shields.io/badge/-E8675C-E8675C?style=flat-square) `#E8675C` (Alerta):** Fuera del gráfico, este tono se reutiliza para los banners o notificaciones de error (por ejemplo: cuando el usuario ingresa una función inválida, división por cero o un intervalo sin cambio de signo).
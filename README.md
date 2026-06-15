# Optimizador de imágenes de seguridad nocturnas

Este proyecto implementa una solución de procesamiento digital de imágenes orientada a optimizar capturas provenientes de cámaras de seguridad nocturnas o en condiciones de baja luminosidad. La aplicación recibe imágenes con poco contraste y visibilidad deficiente, mejora su brillo y contraste y detecta los contornos de los objetos relevantes marcándolos con rectángulos verdes.

---

## 1. Descripción del problema

Las cámaras de seguridad en entornos nocturnos capturan imágenes con bajo contraste y poca visibilidad, lo que dificulta la identificación de objetos y personas.
Algunos de los desafíos a los que se enfrentan las cámaras de seguridad en entornos nocturnos son:

* **Bajo contraste:** La falta de luz dificulta la identificación de objetos y personas, ya que se confundan con el fondo. 
* **Ruido sensor:** El ruido del sensor puede dificultar la detección de objetos. Para compensar la falta de luz, los sensores elevan la ganancia (ISO), introduciendo ruido en la imagen, del tipo "sal y pimienta" o gaussiano, dependiendo del tipo de sensor. Para eliminar el ruido, se pueden utilizar filtros, aunque estos también pueden eliminar detalles de la imagen.
* **Iluminación irregular:** La iluminación puede ser irregular, con zonas muy iluminadas y zonas muy oscuras, lo que dificulta la detección de objetos. Por ejemplo, puede haber objetos cercanos que reflejen la luz de la cámara, mientras que los objetos lejanos estén en la sombra.

Este proyecto resuelve dicho problema mediante el uso de técnicas de procesamiento digital de imágenes. Para esto, construimos un pipeline de procesamiento que recibe imágenes en formato JPG, las procesa y devuelve un resultado donde se destacan los contornos de los objetos relevantes con rectángulos verdes.

---

## 2. Tecnologías elegidas y justificación

### Etapa 1: Mejora del contraste con CLAHE

Para mejorar el contraste de la imagen, utilizamos la librería OpenCV y la función `cv2.CLAHE()`. Esta función aplica un filtro de ecualización de histograma adaptativo a una imagen, lo que resulta en una imagen con mayor contraste.

CLAHE (Contrast Limited Adaptive Histogram Equalization) divide la imagen en sectores y ecualiza el histograma de cada uno por separado, evitando la sobreexposición de zonas ya iluminadas. A diferencia de la ecualización global, CLAHE respeta las diferencias locales de brillo, lo que lo hace especialmente útil en escenas nocturnas con iluminación irregular.

Los parámetros utilizados son:
- `clipLimit = 2.0`: limita la amplificación del contraste para evitar saturación en zonas brillantes.
- `tileGridSize = (8, 8)`: divide la imagen en 64 sectores para procesamiento localizado.

### Etapa 1b: Suavizado gaussiano

Antes de detectar bordes, se aplica un filtro Gaussiano (`GaussianBlur`) para reducir el ruido introducido por el sensor nocturno. Este paso es fundamental porque los detectores de bordes como Canny amplifican el ruido: sin suavizado previo, pequeñas variaciones de brillo generan bordes falsos que luego se interpretan como contornos de objetos.

### Etapa 2: Detección de bordes con Canny

Para detectar los bordes de los objetos, utilizamos el algoritmo de Canny (`cv2.Canny()`). Este algoritmo detecta cambios abruptos de intensidad en la imagen, que corresponden a los bordes de los objetos.

Los parámetros utilizados son:
- `umbral_inferior = 50`: cambios de brillo menores a este valor se ignoran.
- `umbral_superior = 150`: cambios mayores a este valor se consideran bordes seguros.

### Etapa 2b: Cierre morfológico

Después de Canny, se aplica una operación de cierre morfológico (`MORPH_CLOSE`) para unir bordes fragmentados que pertenecen al mismo objeto. Sin esta etapa, objetos grandes como arbustos aparecen divididos en múltiples contornos independientes.

### Etapa 2c: Detección de regiones brillantes

Como complemento a Canny, se implementó una segunda estrategia de detección basada en umbralización binaria. Esta etapa captura objetos con alta luminosidad (como animales en movimiento) cuyos bordes son difusos para Canny debido al motion blur propio de las cámaras nocturnas.

El proceso es:
1. Umbralización binaria sobre el valor de brillo del píxel.
2. Erosión para separar regiones brillantes cercanas.
3. Cierre morfológico para rellenar huecos internos.

Ambas estrategias (bordes y brillo) se aplican de forma independiente y sus resultados se combinan en la etapa de filtrado.

### Etapa 3: Extracción y filtrado de contornos

A partir de los bordes detectados, se extraen los contornos con `cv2.findContours()`. No todos los contornos representan objetos relevantes, por lo que se aplican los siguientes filtros:

- **Área mínima:** se descartan contornos menores a 250 px² para eliminar ruido visual.
- **Área máxima:** se descartan contornos mayores a 50000 px² que corresponden al fondo o regiones demasiado grandes.
- **Proporción:** se descartan contornos con relación ancho/alto fuera del rango 0.2–5.0, eliminando fragmentos con formas extremas que no corresponden a objetos reales.
- **Posición vertical:** se descartan contornos cuyo centro supera el 92% de la altura de la imagen, reduciendo falsos positivos generados por el césped en el borde inferior.

---

## 3. Estructura del proyecto

```
proyecto_final/
├── entrada/
│   └── test1.jpg
├── procesamiento/
│   ├── __init__.py
│   ├── configuracion.py
│   ├── deteccion.py
│   └── mejora.py
├── pruebas/
│   └── debug/
├── salida/
│   └── resultado.jpg
├── main.py
└── README.md
```

---

## 4. Configuración de parámetros

Todos los parámetros de la pipeline son configurables. Los valores por defecto se encuentran en `procesamiento/configuracion.py` y pueden sobreescribirse desde la línea de comandos:

```bash
python main.py --area_minima 300 --umbral_brillo 160 --canny_inferior 40
```

| Parámetro | Valor por defecto | Descripción |
|---|---|---|
| `clahe_clip_limit` | 2.0 | Límite de amplificación de contraste |
| `clahe_tile_grid` | 8 | Tamaño de la grilla de sectores |
| `blur_kernel` | 5 | Tamaño del kernel de suavizado gaussiano |
| `canny_inferior` | 50 | Umbral inferior de Canny |
| `canny_superior` | 150 | Umbral superior de Canny |
| `area_minima` | 250 | Área mínima de contorno en px² |
| `area_maxima` | 50000 | Área máxima de contorno en px² |
| `proporcion_minima` | 0.2 | Proporción mínima ancho/alto |
| `proporcion_maxima` | 5.0 | Proporción máxima ancho/alto |
| `umbral_brillo` | 160 | Umbral de luminosidad para detección por brillo |

### Ajuste automático

La aplicación analiza cada imagen antes de procesarla y ajusta automáticamente algunos parámetros según su contenido:

- **Imagen oscura** (brillo promedio < 50): aumenta `clahe_clip_limit` para amplificar más el contraste.
- **Imagen ruidosa** (desviación estándar > 60): aumenta `area_minima` y `canny_inferior` para reducir falsos positivos.
- **Imagen sobreexpuesta** (brillo promedio > 180): aumenta `canny_superior` para evitar saturación de bordes.

---

## 5. Instalación

### Requisitos previos
- Python 3.11.9

### Crear y activar el entorno virtual

```bash
# Crear el entorno virtual
python -m venv .venv

# Activar en macOS/Linux
source .venv/bin/activate

# Activar en Windows
.venv\Scripts\activate
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

### Contenido de requirements.txt

``` txt
numpy==2.4.6
opencv-python==4.13.0.92
```

---

## 6. Cómo ejecutar

```bash
# Con parámetros por defecto
python main.py

# Sobreescribiendo parámetros específicos
python main.py --area_minima 300 --umbral_brillo 150
```

Las imágenes intermedias de cada etapa se guardan en `pruebas/debug/` para inspección y análisis.

---

## 7. Limitaciones conocidas

- La pipeline detecta regiones delimitadas por bordes o brillo, no clasifica semánticamente los objetos. Vegetación con textura densa puede generar falsos positivos similares a objetos de interés.
- Objetos en movimiento con bordes muy difusos (motion blur) pueden no ser detectados por Canny y dependen exclusivamente de la detección por brillo.
- Cuando un objeto brillante está físicamente adyacente a vegetación densa, ambas regiones pueden fusionarse en un único contorno.
- Los parámetros óptimos varían según las condiciones de cada cámara y escena. El ajuste automático cubre casos comunes pero no garantiza resultados perfectos en todas las situaciones.



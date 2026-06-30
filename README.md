# Optimizador de Imágenes de Seguridad Nocturnas

Aplicación de procesamiento digital de imágenes orientada al monitoreo nocturno
de estacionamientos. Recibe imágenes con baja luminosidad, mejora su visibilidad
y detecta vehículos marcándolos con rectángulos verdes.

---

## 1. Descripción del problema

Las cámaras de seguridad en estacionamientos nocturnos capturan imágenes con bajo
contraste y poca visibilidad, dificultando la identificación de vehículos y personas.
Los principales desafíos son:

- **Bajo contraste:** los vehículos oscuros se confunden con el fondo
- **Ruido del sensor:** al compensar la falta de luz, los sensores introducen ruido visual
- **Iluminación irregular:** zonas muy iluminadas conviven con zonas completamente oscuras

---

## 2. Decisión de diseño: caso de uso acotado

Durante las pruebas iniciales con imágenes de distintos entornos comprobamos que
no existe un conjunto de parámetros que funcione bien para todas las escenas. Al
variar el tipo de imagen (vegetación, calles, interiores), los resultados eran
inconsistentes.

Por eso decidimos acotar el proyecto a un caso de uso real y fijo: el monitoreo
nocturno de estacionamientos con cámara fija. Esto nos permitió calibrar el
pipeline con precisión y obtener resultados consistentes.

El beneficio concreto del sistema es detectar vehículos y personas en el
estacionamiento para identificar posibles intrusos o vehículos en zonas no
autorizadas durante la noche.

---

## 3. Dataset

Las imágenes de prueba provienen del dataset **NDISPark** (Night and Day Instance
Segmented Park), un conjunto de imágenes de estacionamientos reales tomadas de
día y de noche con siete cámaras distintas, bajo distintas condiciones climáticas
y ángulos de visión.

- **Fuente:** <https://zenodo.org/records/6560823>
- **Autores:** Ciampi, L., Santiago, C., Costeira, J., Gennaro, C., Amato, G.
- **Licencia:** Open Data Commons Attribution License v1.0

---

## 4. Técnicas utilizadas

### Etapa 1 — Mejora de visibilidad (`mejora.py`)

**Conversión a escala de grises**
La imagen original en color se convierte a escala de grises porque las técnicas
de detección de bordes operan sobre un solo canal de información.

**CLAHE (Contrast Limited Adaptive Histogram Equalization)**
Divide la imagen en sectores y mejora el contraste de cada uno por separado.
A diferencia de una simple subida de brillo, CLAHE respeta las diferencias
locales de iluminación evitando que las zonas ya brillantes se saturen.

Parámetros:

- `clipLimit = 2.0`: limita la amplificación para evitar saturación
- `tileGridSize = (8,8)`: divide la imagen en 64 sectores

**Suavizado gaussiano**
Reduce el ruido del sensor antes de detectar bordes. Sin este paso, el detector
interpreta el granulado de la imagen como bordes reales.

### Etapa 2 — Detección de objetos (`deteccion.py`)

**Detección de bordes con Canny**
Detecta cambios bruscos de intensidad que corresponden a los bordes de los objetos.

Parámetros:

- `umbral_inferior = 30`: cambios menores se ignoran
- `umbral_superior = 150`: cambios mayores se consideran bordes seguros

**Cierre morfológico**
Une bordes fragmentados que pertenecen al mismo objeto. Se usa un kernel de
`(2,2)` para evitar que autos cercanos se fusionen en un solo rectángulo.

**Detección de regiones brillantes**
Estrategia complementaria a Canny que detecta zonas con alta luminosidad
mediante umbralización binaria. Permite capturar vehículos claros cuyos
bordes son difusos.

### Etapa 3 — Filtrado y resultado

Los contornos se filtran por:

- **Área mínima** (`6000 px²`): descarta ruido y objetos muy pequeños
- **Área máxima** (`70000 px²`): descarta regiones demasiado grandes
- **Proporción ancho/alto** (`0.3 a 4.0`): descarta formas que no corresponden a vehículos
- **Posición vertical**: descarta contornos en el borde inferior de la imagen

---

## 5. Estructura del proyecto

```text
proyecto_final/
├── entrada/               — imágenes de prueba del dataset NDISPark
├── procesamiento/
│   ├── __init__.py
│   ├── configuracion.py   — parámetros centralizados y ajuste automático
│   ├── mejora.py          — lógica de mejora de visibilidad
│   └── deteccion.py       — lógica de detección de objetos
├── pruebas/
│   └── debug/             — imágenes intermedias de cada etapa del pipeline
├── salida/                — imágenes procesadas resultantes
└── main.py                — coordinador del pipeline completo
```

---

## 6. Configuración de parámetros

Todos los parámetros son configurables desde la línea de comandos:

```bash
python main.py --area_minima 8000 --umbral_brillo 160
```

| Parámetro | Valor por defecto | Descripción |
| --- | --- | --- |
| `clahe_clip_limit` | 2.0 | Límite de amplificación de contraste |
| `clahe_tile_grid` | 8 | Tamaño de la grilla de sectores |
| `blur_kernel` | 5 | Tamaño del kernel de suavizado gaussiano |
| `canny_inferior` | 30 | Umbral inferior de Canny |
| `canny_superior` | 150 | Umbral superior de Canny |
| `area_minima` | 6000 | Área mínima de contorno en px² |
| `area_maxima` | 70000 | Área máxima de contorno en px² |
| `proporcion_minima` | 0.3 | Proporción mínima ancho/alto |
| `proporcion_maxima` | 4.0 | Proporción máxima ancho/alto |
| `umbral_brillo` | 160 | Umbral de luminosidad para detección por brillo |

---

## 7. Instalación

### Requisitos previos

- Python 3.11.9

### Crear y activar el entorno virtual

```bash
# Crear el entorno virtual
python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en macOS/Linux
source venv/bin/activate
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 8. Cómo ejecutar

```bash
# Con parámetros por defecto
python main.py

# Sobreescribiendo parámetros específicos
python main.py --area_minima 8000 --umbral_brillo 160
```

Las imágenes intermedias de cada etapa se guardan en `pruebas/debug/` para
inspección y análisis.

---

## 9. Limitaciones conocidas

- Los vehículos oscuros tienen poco contraste con el fondo nocturno, lo que dificulta su detección tanto por bordes como por brillo
- Los parámetros están calibrados para este tipo de escena específica y pueden no funcionar bien en otros entornos
- Cuando dos vehículos están muy próximos, sus contornos pueden fusionarse en un solo rectángulo

---

## 10. Mejoras futuras

- Implementar un modelo de detección de objetos entrenado específicamente para reconocer vehículos, lo que permitiría detectar autos oscuros independientemente del contraste
- Agregar un contador de vehículos para medir la disponibilidad de espacios en tiempo real
- Implementar zonas de exclusión para ignorar áreas fijas de la imagen que siempre generan falsos positivos

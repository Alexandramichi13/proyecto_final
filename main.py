import cv2
import os
import argparse
from procesamiento import MejoradorDeImagen, DetectorDeObjetos, Configuracion


def parsear_argumentos():
    """
    Define y parsear los argumentos de línea de comandos.
    Todos los parámetros son opcionales. Si no se especifican, se utilizan los valores por defecto definidos en Configuracion.
    """
    parser = argparse.ArgumentParser(description="Optimizador de imágenes de seguridad nocturnas")
    parser.add_argument("--canny_inferior", type=int)
    parser.add_argument("--canny_superior", type=int)
    parser.add_argument("--area_minima", type=int)
    parser.add_argument("--area_maxima", type=int)
    parser.add_argument("--clahe_clip_limit", type=float)
    parser.add_argument("--clahe_tile_grid", type=float)
    parser.add_argument("--blur_kernel", type=int)
    parser.add_argument("--umbral_brillo", type=int)

    return parser.parse_args()

def main():
    # Paths de entrada y salida
    PATH_ENTRADA = "./entrada/prueba2.jpg"
    DIR_DEBUG = "./pruebas/debug"
    PATH_SALIDA = "salida/resultado.jpg"

    # Crear directorios si no existen
    os.makedirs(DIR_DEBUG, exist_ok=True)
    os.makedirs("./salida", exist_ok=True)

    # Parsear argumentos de consola y construir la configuración
    args = parsear_argumentos()
    config = Configuracion(args_consola=args)

    # Cargar imagen de entrada
    imagen = cv2.imread(PATH_ENTRADA)
    if imagen is None:
        print(f"Error: no se encontró la imagen en {PATH_ENTRADA}")
        return

    cv2.imwrite(f"{DIR_DEBUG}/01_original.jpg", imagen)
    print("01 - original guardada.")

    # Analizar imagen y ajustar parámetros automáticamente según su contenido (brillo promedio, nivel de ruido, sobreexposición)
    config.ajustar_segun_imagen(imagen)

    # Inicializar herramientas con la configuración final
    mejorador = MejoradorDeImagen(config)
    detector = DetectorDeObjetos(config)

    # Etapa 1: Mejorar imagen

    # Convertir a escala de grises para que CLAHE opere sobre un solo canal
    gris = mejorador._convertir_a_grises(imagen)
    cv2.imwrite(f"{DIR_DEBUG}/02_grises.jpg", gris)

    # Aplicar CLAHE para mejorar el contraste de forma localizada
    clahe = mejorador._aplicar_clahe(gris)
    cv2.imwrite(f"{DIR_DEBUG}/03_clahe.jpg", clahe)

    # Suavizar la imagen para reducir el ruido antes de detectar bordes
    suavizada = mejorador._suavizar_imagen(clahe)
    cv2.imwrite(f"{DIR_DEBUG}/04_blur.jpg", suavizada)

    # Etapa 2: Detectar objetos

    # Detección de bordes con Canny sobre la imagen suavizada
    bordes = detector._detectar_bordes(suavizada)
    cv2.imwrite(f"{DIR_DEBUG}/05_canny.jpg", bordes)

    # Aplicar cierre morfológico para unir bordes fragmentados del mismo objeto
    bordes_cerrados = detector._cerrar_bordes(bordes)
    cv2.imwrite(f"{DIR_DEBUG}/06_morfologico.jpg", bordes_cerrados)

    # Detectar regiones brillantes como estrategia complementaria a Canny
    # Útil para objetos en movimiento cuyos bordes son difusos
    brillantes = detector._detectar_regiones_brillantes(suavizada)
    cv2.imwrite(f"{DIR_DEBUG}/06b_brillo.jpg", brillantes)    
    
    # Combinar bordes y regiones brillantes en una sola imagen
    combinado = cv2.bitwise_or(bordes_cerrados, brillantes)
    cv2.imwrite(f"{DIR_DEBUG}/07_combinado.jpg", combinado)
   

    # Etapa 3: Detección final y resultado

    # Ejecutar la pipeline completa de detección:
    # Aplica ambas estrategias (bordes y brillo) de forma independiente, 
    # filtra los contornos por área, proporción y posición, y dibuja los rectángulos sobre los objetos detectados
    resultado = detector.detectar(suavizada)
    cv2.imwrite(f"{DIR_DEBUG}/09_resultado.jpg", resultado)
    cv2.imwrite(PATH_SALIDA, resultado)
    print("09 - resultado final guardado.")

if __name__ == "__main__":
    main()


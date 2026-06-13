import cv2
import os
from procesamiento.mejora import MejoradorDeImagen
from procesamiento.deteccion import DetectorDeObjetos


def main():
    # Paths de entrada y salida
    PATH_ENTRADA = "./entrada/test1.jpg"
    PATH_MEJORA = "./pruebas/mejora1.jpg"
    PATH_DETECCION = "./pruebas/deteccion1.jpg"
    PATH_SALIDA = "salida/resultado.jpg"
    
    # Inicializar herramientas
    mejorador = MejoradorDeImagen()
    detector = DetectorDeObjetos()

    # Cargamos la imagen
    if not os.path.exists(PATH_ENTRADA):
        print(f"Error: No se encontró la imagen en {PATH_ENTRADA}")
        return

    imagen = cv2.imread(PATH_ENTRADA)
    print("Imagen cargada correctamente.")

    # Paso 1: Mejorar la imagen
    imagen_mejorada = mejorador.mejorar(imagen)
    cv2.imwrite(PATH_MEJORA, imagen_mejorada)
    print("Imagen mejorada correctamente.")

    # Paso 2: Detectar las manchas
    detalles = detector.detectar(imagen_mejorada)
    cv2.imwrite(PATH_DETECCION, detalles)
    print("Manchas detectadas correctamente.")

    # Paso 3: Guardar la imagen con los detalles
    cv2.imwrite(PATH_SALIDA, detalles)
    print("Imagen guardada correctamente.")

if __name__ == "__main__":
    main()


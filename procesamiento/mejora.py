import cv2
import numpy as np

class MejoradorDeImagen:

    def __init__(self):
        # Configuramos CLAHE para mejorar el contraste de forma localizada
        # clipLimit=2.0 evita que las zonas brillantes se saturen
        # tileGridSize=(8,8) divide la imagen en sectores para procesarlos por separado
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def mejorar(self, imagen):
        # Convertimos a escala de grises porque CLAHE opera sobre un solo canal
        imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        
        # Aplicamos CLAHE para mejorar visibilidad en zonas oscuras
        imagen_mejorada = self.clahe.apply(imagen_gris)
        
        return imagen_mejorada
import cv2

class DetectorDeObjetos:

    def __init__(self):
        # Umbrales para el detector de bordes Canny
        # 50 es el umbral inferior: cambios de brillo menores a esto se ignoran
        # 150 es el umbral superior: cambios mayores a esto se consideran bordes seguros
        self.umbral_inferior = 50
        self.umbral_superior = 150

    def detectar(self, imagen):
        # Aplicamos Canny para detectar bordes en la imagen mejorada
        bordes = cv2.Canny(imagen, self.umbral_inferior, self.umbral_superior)

        # Buscamos los contornos a partir de los bordes detectados
        # RETR_EXTERNAL significa que solo nos interesan los contornos exteriores
        # CHAIN_APPROX_SIMPLE reduce la cantidad de puntos guardados por contorno
        contornos, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Convertimos la imagen de escala de grises a color para poder dibujar
        # los rectángulos en verde, que es un color que se ve bien sobre grises
        imagen_resultado = cv2.cvtColor(imagen, cv2.COLOR_GRAY2BGR)

        for contorno in contornos:
            # Ignoramos contornos menores a 500 píxeles para evitar ruido visual
            if cv2.contourArea(contorno) > 500:
                x, y, ancho, alto = cv2.boundingRect(contorno)
                cv2.rectangle(imagen_resultado, (x, y), (x + ancho, y + alto), (0, 255, 0), 2)

        return imagen_resultado

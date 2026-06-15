import cv2

class DetectorDeObjetos:
    """
    Detecta objetos en una imagen de seguridad nocturna utilizando dos estrategias
    complementarias: detección de bordes con Canny y detección de regiones brillantes
    por umbralización. Los objetos detectados se marcan con rectángulos verdes.
    """

    def __init__(self, config):
        """
        Inicializa el detector con los parámetros definidos en la configuración.

        Args:
            config (Configuracion): objeto de configuración con los parámetros de la pipeline.
        """
        # Umbrales para el detector de bordes Canny
        # 50 es el umbral inferior: cambios de brillo menores a esto se ignoran
        # 150 es el umbral superior: cambios mayores a esto se consideran bordes seguros
        p = config.params
        self.umbral_inferior = p["canny_inferior"]
        self.umbral_superior = p["canny_superior"]
        self.area_minima = p["area_minima"]
        self.area_maxima = p["area_maxima"]
        self.proporcion_minima = p["proporcion_minima"]
        self.proporcion_maxima = p["proporcion_maxima"]
        self.umbral_brillo = p["umbral_brillo"]

    def detectar(self, imagen):
        """
        Ejecuta la pipeline completa de detección sobre la imagen recibida.
        Aplica detección por bordes y por brillo de forma independiente,
        combina los resultados y dibuja los rectángulos sobre los objetos detectados.

        Args:
            imagen (numpy.ndarray): imagen en escala de grises ya mejorada.
        Returns:
            numpy.ndarray: imagen en color BGR con los objetos marcados.
        """
        bordes = self._detectar_bordes(imagen)
        bordes = self._cerrar_bordes(bordes)
        brillantes = self._detectar_regiones_brillantes(imagen)

        contornos_bordes = self._extraer_contornos(bordes)
        contornos_brillo = self._extraer_contornos(brillantes)
        todos = contornos_bordes + contornos_brillo

        return self._dibujar_resultados(imagen, todos)

    def _detectar_bordes(self, imagen):
        """
        Aplica el algoritmo de Canny para detectar bordes en la imagen.
        Los umbrales controlan qué cambios de intensidad se consideran bordes.

        Args:
            imagen (numpy.ndarray): imagen en escala de grises.
        Returns:
            numpy.ndarray: imagen binaria con los bordes detectados.
        """
        return cv2.Canny(imagen, self.umbral_inferior, self.umbral_superior)

    def _cerrar_bordes(self, bordes):
        """
        Aplica cierre morfológico para unir bordes fragmentados que pertenecen
        al mismo objeto. Sin esta etapa, objetos grandes pueden aparecer divididos
        en múltiples contornos independientes.

        Args:
            bordes (numpy.ndarray): imagen binaria con bordes detectados.
        Returns:
            numpy.ndarray: imagen binaria con bordes cerrados.
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))

        return cv2.morphologyEx(bordes, cv2.MORPH_CLOSE, kernel)

    def _detectar_regiones_brillantes(self, imagen):
        """
        Detecta regiones con alta luminosidad mediante umbralización binaria.
        Esta estrategia complementa a Canny para capturar objetos en movimiento
        cuyos bordes son difusos por motion blur y no son bien detectados por Canny.

        El proceso es:
        1. Umbralización binaria: píxeles más brillantes que umbral_brillo → blanco.
        2. Erosión: separa regiones brillantes cercanas para evitar fusiones.
        3. Cierre morfológico: rellena huecos internos de cada región.

        Args:
            imagen (numpy.ndarray): imagen en escala de grises.
        Returns:
            numpy.ndarray: máscara binaria con las regiones brillantes detectadas.
        """
        _, mascara = cv2.threshold(imagen, self.umbral_brillo, 255, cv2.THRESH_BINARY)
        # erosión para separar regiones cercanas
        kernel_erosion = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mascara = cv2.erode(mascara, kernel_erosion, iterations=1)
        # cierre pequeño para rellenar huecos internos
        kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel_close)
        return mascara

    def _extraer_contornos(self, bordes):
        """
        Extrae los contornos de la imagen de bordes y aplica filtros para
        descartar regiones que no corresponden a objetos relevantes.

        Filtros aplicados:
        - Área mínima: descarta contornos pequeños (ruido visual).
        - Área máxima: descarta contornos demasiado grandes (fondo o regiones enormes).
        - Proporción: descarta contornos con formas extremas (muy alargados o muy cuadrados).
        - Posición vertical: descarta contornos en el borde inferior de la imagen (césped).

        Args:
            bordes (numpy.ndarray): imagen binaria con bordes o máscara de brillo.
        Returns:
            list: lista de contornos que pasaron todos los filtros.
        """
        alto_imagen = bordes.shape[0]
        contornos, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        resultado = []
        for c in contornos:
            area = cv2.contourArea(c)
            if not (self.area_minima < area < self.area_maxima):
                continue
            x, y, ancho, alto = cv2.boundingRect(c)
            proporcion = ancho / alto if alto > 0 else 0
            if not (self.proporcion_minima < proporcion < self.proporcion_maxima):
                continue
            centro_y = y + alto / 2
            if centro_y > alto_imagen * 0.92:
                continue
            resultado.append(c)
        return resultado

    def _dibujar_resultados(self, imagen, contornos):
        """
        Convierte la imagen a color y dibuja un rectángulo verde alrededor
        de cada contorno detectado.

        Args:
            imagen (numpy.ndarray): imagen en escala de grises.
            contornos (list): lista de contornos a marcar.
        Returns:
            numpy.ndarray: imagen en color BGR con los rectángulos dibujados.
        """
        resultado = cv2.cvtColor(imagen, cv2.COLOR_GRAY2BGR)

        for contorno in contornos:
            x, y, ancho, alto = cv2.boundingRect(contorno)
            cv2.rectangle(resultado, (x, y), (x + ancho, y + alto), (0, 255, 0), 2)

        return resultado

import cv2

class MejoradorDeImagen:
    """
    Recibe una imagen BGR en condiciones de baja luminosidad y la prepara
    para la etapa de detección aplicando mejora de contraste localizada (CLAHE)
    y suavizado gaussiano para reducir el ruido del sensor nocturno.
    """

    def __init__(self, config):
        """
        Inicializa el mejorador con los parámetros definidos en la configuración.

        Args:
            config (Configuracion): objeto de configuración con los parámetros de la pipeline.
        """
        # CLAHE: mejora el contraste localmente
        # clipLimit=2.0 evita que las zonas brillantes se saturen
        # tileGridSize=(8,8) divide la imagen en sectores para procesarlos por separado
        p = config.params
        self.clahe = cv2.createCLAHE(
            clipLimit=p["clahe_clip_limit"],
            tileGridSize=(p["clahe_tile_grid"], p["clahe_tile_grid"])
        )
        self.kernel_blur = (p["blur_kernel"], p["blur_kernel"])

    def mejorar(self, imagen):
        """
        Recibe una imagen en formato BGR y le aplica CLAHE para mejorar el brillo y contraste,
        luego la suaviza para reducir el ruido.
        
        Args:
            imagen (numpy.ndarray): Imagen en formato BGR.

        Returns:
            numpy.ndarray: Imagen en escala de grises con CLAHE.
        """
        # Convertimos a escala de grises porque CLAHE opera sobre un solo canal
        imagen_gris = self._convertir_a_grises(imagen)
        
        # Aplicamos CLAHE para mejorar visibilidad en zonas oscuras
        imagen_mejorada = self._aplicar_clahe(imagen_gris)
        
        # Suavizamos la imagen para reducir el ruido antes de detectar bordes
        imagen_suavizada = self._suavizar_imagen(imagen_mejorada)

        return imagen_suavizada

    def _convertir_a_grises(self, imagen):
        """
        Recibe una imagen BGR y devuelve una imagen en escala de grises.
        
        Args:
            imagen (numpy.ndarray): Imagen en formato BGR.

        Returns:
            numpy.ndarray: Imagen en escala de grises.
        """
        return cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    def _aplicar_clahe(self, imagen):
        """
        Aplica CLAHE a la imagen en escala de grises.
        
        Args:
            imagen (numpy.ndarray): Imagen en escala de grises.

        Returns:
            numpy.ndarray: Imagen en escala de grises con CLAHE.
        """
        return self.clahe.apply(imagen)

    def _suavizar_imagen(self, imagen):
        """
        Suaviza la imagen en escala de grises.
        
        Args:
            imagen (numpy.ndarray): Imagen en escala de grises.

        Returns:
            numpy.ndarray: Imagen en escala de grises suavizada.
        """
        return cv2.GaussianBlur(imagen, self.kernel_blur, 0)
import argparse
import numpy as np

DEFAULTS = {
    "clahe_clip_limit": 2.0,
    "clahe_tile_grid": 8,
    "blur_kernel": 5,
    "canny_inferior": 50,
    "canny_superior": 150,
    "area_minima": 500,
    "area_maxima": 50000,
    "proporcion_minima": 0.2,
    "proporcion_maxima": 5.0,
    "umbral_brillo": 180
}

class Configuracion:
    def __init__(self, args_consola=None):
        self.params = DEFAULTS.copy()
        if args_consola:
            self._aplicar_consola(args_consola)

    def _aplicar_consola(self, args):
        for key, value in vars(args).items():
            if value is not None and key in self.params:
                self.params[key] = value
                print(f"Parámetro sobreescrito por consola: {key} = {value}")

    def ajustar_segun_imagen(self, imagen):
        brillo = float(np.mean(imagen))
        ruido = float(np.std(imagen))
        print(f"Análisis de imagen → brillo promedio: {brillo:.1f}, ruido (std): {ruido:.1f}")

        if brillo < 50:
            self.params["clahe_clip_limit"] = min(self.params["clahe_clip_limit"] + 1.5, 6.0)
            print(f"  Imagen oscura → clipLimit ajustado a {self.params['clahe_clip_limit']}")

        if ruido > 60:
            self.params["area_minima"] = max(self.params["area_minima"], 1000)
            self.params["canny_inferior"] = min(self.params["canny_inferior"] + 20, 100)
            print(f"  Imagen ruidosa → area_minima={self.params['area_minima']}, canny_inferior={self.params['canny_inferior']}")

        if brillo > 180:
            self.params["canny_superior"] = min(self.params["canny_superior"] + 50, 300)
            print(f"  Imagen sobreexpuesta → canny_superior ajustado a {self.params['canny_superior']}")
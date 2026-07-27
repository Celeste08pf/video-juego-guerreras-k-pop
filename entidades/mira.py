"""
entidades/mira.py
==================
Mira: guerrera del Nivel 2. Hereda TODO el comportamiento de Personaje
(movimiento, ataques, vida, física de salto) y sólo redefine
cargar_imagenes(), porque su animación de ataque especial ("ataque 2_1"
... "ataque 2_4") tiene 4 frames en vez de los 3 que usan Zoey y Rumi.

Es el ejemplo más directo de herencia + polimorfismo del proyecto: en
todo el resto del código (Juego, colisiones, HUD) una instancia de Mira se
trata exactamente igual que cualquier otro Personaje.
"""
import pygame

from config import constantes as C
from entidades.personaje import Personaje


class Mira(Personaje):
    """Guerrera del Nivel 2: mismo comportamiento que Personaje, distintos sprites."""

    def cargar_imagenes(self):
        try:
            self._animaciones["estandar"].append(self.cargar_y_escalar("estandar 2"))

            for i in range(1, 4):  # caminar 2_1, 2_2, 2_3
                self._animaciones["caminar"].append(self.cargar_y_escalar(f"caminar 2_{i}"))

            for i in range(1, 4):  # puño 2_1, 2_2, 2_3
                self._animaciones["golpear"].append(self.cargar_y_escalar(f"puño 2_{i}"))

            for i in range(1, 4):  # patada 2_1, 2_2, 2_3
                self._animaciones["patear"].append(self.cargar_y_escalar(f"patada 2_{i}"))

            for i in range(1, 5):  # ataque 2_1 .. 2_4 (Mira usa 4, no 3)
                self._animaciones["lanzar"].append(self.cargar_y_escalar(f"ataque 2_{i}"))

            self._animaciones["saltar"].append(self.cargar_y_escalar("salto 2_1"))
            self._animaciones["agacharse"].append(self.cargar_y_escalar("agacharse 2_1"))

            try:
                self._animaciones["bloquear"].append(self.cargar_y_escalar("bloquear 2"))
            except (FileNotFoundError, pygame.error):
                self._animaciones["bloquear"].append(self._animaciones["estandar"][0])

        except (FileNotFoundError, pygame.error) as e:
            print(f"[Mira] No se pudieron cargar todas las imágenes: {e}")
            self._cargar_colores_de_respaldo(C.AZUL_ELECTRICO, frames_lanzar=4)

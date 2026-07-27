"""
entidades/objeto.py
====================
Objetos recolectables que aparecen aleatoriamente en el suelo del nivel.
- "moneda": suma puntaje.
- "corazon": suma puntaje Y recarga la barra de vida actual de la jugadora.
"""
import math
import random

import pygame

from config import constantes as C
from core.utils import cargar_imagen_flexible


class Objeto(pygame.sprite.Sprite):
    """Recolectable con animación de flote y tiempo de vida limitado."""

    # Tabla de configuración por tipo: encapsula en un solo lugar qué
    # archivo/color usa cada tipo y cuánto puntaje otorga.
    INFO_TIPOS = {
        "moneda": {"archivo": "objeto_moneda", "color_respaldo": C.DORADO, "puntaje": 20},
        "corazon": {"archivo": "objeto_corazon", "color_respaldo": C.ROJO, "puntaje": 30},
    }

    def __init__(self, x, y, tipo="moneda"):
        super().__init__()
        self._tipo = tipo
        info = self.INFO_TIPOS[tipo]

        try:
            self.image = cargar_imagen_flexible(info["archivo"], C.TAMANO_OBJETO)
        except (FileNotFoundError, pygame.error):
            self.image = pygame.Surface(C.TAMANO_OBJETO, pygame.SRCALPHA)
            radio = C.TAMANO_OBJETO[0] // 2
            pygame.draw.circle(self.image, info["color_respaldo"], (radio, radio), radio)
            pygame.draw.circle(self.image, C.BLANCO_BRILLANTE, (radio, radio), radio, 2)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self._y_base = y
        self.rect.y = y
        self._puntaje_otorgado = info["puntaje"]

        self._tiempo_inicio = pygame.time.get_ticks()
        self._tiempo_vida_ms = 9000  # desaparece solo si nadie lo recoge en ~9 segundos

    @property
    def tipo(self):
        return self._tipo

    @property
    def puntaje_otorgado(self):
        return self._puntaje_otorgado

    def _tiempo_agotado(self):
        return pygame.time.get_ticks() - self._tiempo_inicio > self._tiempo_vida_ms

    def update(self):
        # Pequeño movimiento de flotación para que se note que es interactivo.
        transcurrido = pygame.time.get_ticks() - self._tiempo_inicio
        offset = int(6 * math.sin(transcurrido / 200))
        self.rect.y = self._y_base + offset

        if self._tiempo_agotado():
            self.kill()

    @staticmethod
    def generar_aleatorio():
        """Crea un objeto (moneda, la mayoría de las veces, o corazón raro)."""
        tipo = "corazon" if random.random() < 0.2 else "moneda"
        x = random.randint(40, C.ANCHO - C.TAMANO_OBJETO[0] - 40)
        y = 320  # a la altura del suelo, alcanzable caminando
        return Objeto(x, y, tipo)

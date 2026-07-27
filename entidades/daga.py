"""
entidades/daga.py
==================
Proyectil que dispara Zoey con su ataque especial. Es la única guerrera con
arma a distancia; Mira y Rumi atacan cuerpo a cuerpo con espada.
"""
import pygame

from config import constantes as C
from core.utils import cargar_imagen_flexible


class Daga(pygame.sprite.Sprite):
    """Proyectil simple: viaja en línea recta y se autodestruye al salir de pantalla."""

    def __init__(self, x, y, direccion):
        super().__init__()
        try:
            self.image = cargar_imagen_flexible("dagas", (100, 40))
        except (FileNotFoundError, pygame.error) as e:
            print(f"[Daga] No se pudo cargar la imagen 'dagas': {e}")
            self.image = pygame.Surface((100, 40))
            self.image.fill(C.DORADO)

        if direccion == -1:
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()
        if direccion == 1:
            self.rect.left = x + C.TARGET_WIDTH - 20
        else:
            self.rect.right = x + 20

        self.rect.centery = y + int(C.TARGET_HEIGHT * 0.45)
        self._direccion = direccion
        self._velocidad = 14

    def update(self):
        self.rect.x += self._velocidad * self._direccion
        if self.rect.right < 0 or self.rect.left > C.ANCHO:
            self.kill()

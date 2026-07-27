"""
entidades/entidad_base.py
==========================
Clase base para TODAS las entidades animadas del juego: tanto las guerreras
jugables (Personaje) como los enemigos (Demonio) comparten la misma lógica
de "tengo varios estados, cada estado tiene una lista de frames, y voy
avanzando de frame cada cierto tiempo". Esa lógica se escribe una sola vez
acá y se hereda, en vez de repetirla en cada clase (principio DRY aplicado
mediante herencia).

EntidadAnimada no se usa nunca directamente en el juego: es una base
pensada para ser heredada (equivalente a una clase abstracta).
"""
import pygame


class EntidadAnimada(pygame.sprite.Sprite):
    """Sprite con animación por estados y encapsulamiento del frame actual."""

    def __init__(self, x, y, tamano, cooldown_animacion=150):
        super().__init__()

        # --- Atributos "privados" (prefijo _) ----------------------------
        # No se acceden directamente desde fuera de la clase: el resto del
        # código los consulta o modifica a través de las properties y
        # métodos definidos más abajo. Esto es encapsulamiento: la clase
        # decide cómo se puede cambiar su propio estado interno.
        self._tamano = tamano
        self._animaciones = {}            # estado (str) -> lista de Surface
        self._estado_actual = "estandar"
        self._frame_index = 0
        self._direccion = 1                # 1 = mira a la derecha, -1 = izquierda
        self._cooldown_animacion = cooldown_animacion
        self._ultimo_update = pygame.time.get_ticks()

        self.image = pygame.Surface(tamano)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    # ---------------- Properties: acceso controlado al estado interno ---
    @property
    def estado_actual(self):
        return self._estado_actual

    @property
    def direccion(self):
        return self._direccion

    @direccion.setter
    def direccion(self, valor):
        # Normaliza cualquier valor a 1 o -1: encapsula la regla de negocio
        # de que la dirección sólo puede ser "izquierda" o "derecha".
        self._direccion = 1 if valor >= 0 else -1

    # ---------------- Métodos comunes reutilizados por las subclases ----
    def cargar_y_escalar(self, nombre_base):
        """Carga un sprite desde 'multimedia' ya escalado al tamaño propio."""
        from core.utils import cargar_imagen_flexible
        return cargar_imagen_flexible(nombre_base, self._tamano)

    def cambiar_estado(self, nuevo_estado):
        """Cambia de estado de animación (ej: 'caminar' -> 'golpear')."""
        if nuevo_estado not in self._animaciones or not self._animaciones[nuevo_estado]:
            return
        if self._estado_actual != nuevo_estado:
            self._estado_actual = nuevo_estado
            self._frame_index = 0
            self._ultimo_update = pygame.time.get_ticks()

    def _debe_avanzar_frame(self):
        """
        True si ya pasó el tiempo de cooldown y corresponde avanzar al
        siguiente frame de la animación actual.
        """
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self._ultimo_update >= self._cooldown_animacion:
            self._ultimo_update = tiempo_actual
            return True
        return False

    def _frames_de(self, estado):
        return self._animaciones.get(estado, [])

    def _aplicar_flip(self, imagen_base):
        """Voltea horizontalmente la imagen según hacia dónde mira la entidad."""
        if self._direccion == -1:
            return pygame.transform.flip(imagen_base, True, False)
        return imagen_base

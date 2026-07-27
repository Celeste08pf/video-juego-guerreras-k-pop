"""
entidades/demonio.py
=====================
Demonio: enemigo de los niveles 1, 2 y 3. Hereda de EntidadAnimada (misma
base que Personaje) y agrega su propia IA de combate y su vida encapsulada.

Demonio2 (ver entidades/demonio2.py) hereda de esta clase para los niveles
4 y 5: reutiliza toda la vida/daño/estructura de la IA y sólo sobrescribe
la carga de sprites y el método actualizar_ia() para agregar el esquive
saltando y el ataque especial con espada.
"""
import random

import pygame

from config import constantes as C
from entidades.entidad_base import EntidadAnimada


class Demonio(EntidadAnimada):
    """Enemigo con IA de esquive/ataque y vida encapsulada en una barra de HP."""

    VIDA_MAXIMA = 100

    def __init__(self, x, y):
        super().__init__(x, y, C.TARGET_SIZE, cooldown_animacion=120)

        for estado in ("caminar", "patear", "esquivar", "golpear"):
            self._animaciones[estado] = []
        self._estado_actual = "caminar"  # los demonios no tienen pose "estandar"

        self.cargar_imagenes()
        self.image = self._frames_de(self._estado_actual)[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self._direccion = -1  # Mira a la izquierda por defecto

        # --- Vida encapsulada: sólo se modifica vía recibir_golpe()/curar_completo() ---
        self._vida = self.VIDA_MAXIMA

        # --- Parámetros de la IA de combate ---
        self._velocidad_base = 4
        self._distancia_seguridad = 130
        self._rango_ataque = 90
        self._rango_reaccion_esquiva = 180

        self._esquivando = False
        self._cooldown_ataque = 0

        self._probabilidad_esquivar = 0.65
        self._probabilidad_atacar = 0.85

    # ---------------- Vida: acceso controlado -----------------------------
    @property
    def vida(self):
        return self._vida

    @property
    def fraccion_vida(self):
        """Vida actual como fracción 0.0-1.0, lista para dibujar una barra."""
        return max(0, self._vida) / self.VIDA_MAXIMA

    def recibir_golpe(self, dano):
        """Descuenta daño; devuelve True si el demonio quedó eliminado."""
        self._vida -= dano
        return self._vida <= 0

    def reiniciar_vida(self):
        self._vida = self.VIDA_MAXIMA

    # ---------------- Carga de sprites (Demonio2 la redefine) --------------
    def cargar_imagenes(self):
        try:
            for i in range(1, 4):
                self._animaciones["caminar"].append(self.cargar_y_escalar(f"demonio caminar {i}"))
            for i in range(1, 4):
                self._animaciones["patear"].append(self.cargar_y_escalar(f"demonio patada {i}"))
            for i in range(1, 3):
                self._animaciones["esquivar"].append(self.cargar_y_escalar(f"demonio esquivar {i}"))
            for i in range(1, 4):
                self._animaciones["golpear"].append(self.cargar_y_escalar(f"demonio puño {i}"))
        except (FileNotFoundError, pygame.error) as e:
            print(f"[Demonio] No se pudieron cargar las imágenes desde 'multimedia': {e}")
            self._cargar_colores_de_respaldo()

    def _cargar_colores_de_respaldo(self):
        for estado in self._animaciones:
            self._animaciones[estado] = []
        frames_count = {"caminar": 3, "patear": 3, "esquivar": 2, "golpear": 3}
        for estado_nombre, num_frames in frames_count.items():
            for _ in range(num_frames):
                surf = pygame.Surface(C.TARGET_SIZE)
                surf.fill(C.TURQUESA if estado_nombre == "caminar" else C.ROJO)
                self._animaciones[estado_nombre].append(surf)

    def reiniciar_combate(self):
        """Se llama al empezar/reiniciar un nivel o al reaparecer."""
        self._esquivando = False
        self._cooldown_ataque = 0
        self.cambiar_estado("caminar")

    def _mover(self, delta):
        self.rect.x += delta

    def actualizar_ia(self, jugador, jugador_ataco, nivel):
        """
        IA de combate. Devuelve un diccionario:
          - 'ataco': True SOLO en el frame en que el demonio lanza un nuevo
                     golpe/patada real (para chequear colisión/daño afuera).
          - 'esquivando': True mientras el demonio está esquivando.
        """
        resultado = {'ataco': False, 'esquivando': False}

        distancia_centro_x = jugador.rect.centerx - self.rect.centerx
        abs_distancia = abs(distancia_centro_x)
        self.direccion = 1 if distancia_centro_x > 0 else -1

        velocidad_ajustada = self._velocidad_base + (nivel * 0.9)
        prob_esquivar = min(0.92, self._probabilidad_esquivar + (nivel * 0.07))
        prob_atacar = min(0.97, self._probabilidad_atacar + (nivel * 0.05))

        # --- ¿ESQUIVA UN GOLPE/PATADA CERCANO DE LA GUERRERA? (aleatorio) ---
        if (not self._esquivando and jugador_ataco
                and jugador.estado_actual in ("golpear", "patear")
                and abs_distancia < self._rango_reaccion_esquiva
                and random.random() < prob_esquivar):
            self.cambiar_estado("esquivar")
            self._esquivando = True
            self._cooldown_ataque = 0

        if self._esquivando:
            resultado['esquivando'] = True
            if distancia_centro_x > 0:
                self._mover(-velocidad_ajustada)
            else:
                self._mover(velocidad_ajustada)

            if self.estado_actual != "esquivar":
                self._esquivando = False
                contraataque = random.choice(["golpear", "patear"])
                self.cambiar_estado(contraataque)
                resultado['ataco'] = True
                self._cooldown_ataque = random.randint(15, 35)

        else:
            if self._cooldown_ataque > 0:
                self._cooldown_ataque -= 1

            # Mientras está en medio de un golpe/patada/esquive no se
            # interrumpe con otra decisión de movimiento, o la animación
            # nunca llegaría a verse completa.
            if self.estado_actual in ("golpear", "patear", "esquivar"):
                pass
            elif abs_distancia > self._distancia_seguridad:
                self.cambiar_estado("caminar")
                if distancia_centro_x > 0:
                    self._mover(velocidad_ajustada)
                else:
                    self._mover(-velocidad_ajustada)

            elif abs_distancia < self._rango_ataque and self._cooldown_ataque == 0:
                if random.random() < prob_atacar:
                    ataque_elegido = random.choice(["golpear", "patear"])
                    self.cambiar_estado(ataque_elegido)
                    resultado['ataco'] = True
                    if random.random() < 0.35:
                        self._cooldown_ataque = random.randint(8, 18)
                    else:
                        self._cooldown_ataque = random.randint(20, 45)
                else:
                    self.cambiar_estado("esquivar")
                    if distancia_centro_x > 0:
                        self._mover(-velocidad_ajustada * 1.3)
                    else:
                        self._mover(velocidad_ajustada * 1.3)
                    self._cooldown_ataque = random.randint(10, 25)
            else:
                self.cambiar_estado("caminar")

        self.rect.x = max(0, min(self.rect.x, C.ANCHO - C.TARGET_WIDTH))
        return resultado

    def update(self):
        if self._debe_avanzar_frame():
            self._frame_index += 1
            frames = self._frames_de(self._estado_actual)
            if self._frame_index >= len(frames):
                if self.estado_actual in ("golpear", "patear", "esquivar"):
                    self._estado_actual = "caminar"
                self._frame_index = 0

        imagen_base = self._frames_de(self._estado_actual)[self._frame_index]
        # El demonio original voltea al revés que la jugadora (su spritesheet
        # ya mira hacia la izquierda por defecto).
        if self._direccion == 1:
            self.image = pygame.transform.flip(imagen_base, True, False)
        else:
            self.image = imagen_base

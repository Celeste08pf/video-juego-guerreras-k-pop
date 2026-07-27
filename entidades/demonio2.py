"""
entidades/demonio2.py
=======================
Demonio2: rival exclusivo de los niveles 4 y 5. Hereda de Demonio (reutiliza
vida, daño, cooldowns y la estructura general de la IA) y extiende el
comportamiento con:
  - Un esquive alternativo saltando verticalmente (además de retroceder
    caminando), con su propia física simple de salto.
  - Un ataque especial con espada de 5 frames ("ataque"), más lento y
    amenazante, que usa con menor frecuencia que golpe/patada.

Al heredar de Demonio en vez de reescribir todo desde cero, Demonio2 no
duplica la carga de vida ni la lógica de recibir_golpe(): sólo agrega lo
que le es propio.
"""
import random

import pygame

from config import constantes as C
from entidades.demonio import Demonio


class Demonio2(Demonio):
    """Enemigo de los niveles 4-5: IA de Demonio + esquive con salto + espada."""

    def __init__(self, x, y):
        # Se guarda antes de llamar a super().__init__ porque cargar_imagenes()
        # (llamado dentro del __init__ de Demonio) ya necesita que existan
        # las claves "salto" y "ataque" en el diccionario de animaciones.
        self._suelo_y = y
        super().__init__(x, y)

        self._velocidad_y = 0
        self._gravedad = 1.2
        self._potencia_salto = -16
        self._saltando = False
        self._contador_retroceso = 0
        self._probabilidad_ataque_especial = 0.25  # ~1 de cada 4 ataques es el especial

    def cargar_imagenes(self):
        # Se agregan los estados propios de Demonio2 antes de cargarlos.
        self._animaciones.setdefault("salto", [])
        self._animaciones.setdefault("ataque", [])
        try:
            for i in range(1, 4):
                self._animaciones["caminar"].append(self.cargar_y_escalar(f"demonio caminar 2_{i}"))
            for i in range(1, 4):
                self._animaciones["golpear"].append(self.cargar_y_escalar(f"demonio puño 2_{i}"))
            for i in range(1, 4):
                self._animaciones["patear"].append(self.cargar_y_escalar(f"demonio patada 2_{i}"))
            for i in range(1, 4):
                self._animaciones["salto"].append(self.cargar_y_escalar(f"demonio salto 2_{i}"))
            for i in range(1, 6):
                self._animaciones["ataque"].append(self.cargar_y_escalar(f"demonio ataque 2_{i}"))
        except (FileNotFoundError, pygame.error) as e:
            print(f"[Demonio2] No se pudieron cargar las imágenes desde 'multimedia': {e}")
            for estado in self._animaciones:
                self._animaciones[estado] = []
            frames_count = {"caminar": 3, "golpear": 3, "patear": 3, "salto": 3, "ataque": 5}
            for estado_nombre, num_frames in frames_count.items():
                for _ in range(num_frames):
                    surf = pygame.Surface(C.TARGET_SIZE)
                    surf.fill(C.TURQUESA if estado_nombre == "caminar" else C.MORADO_BRILLANTE)
                    self._animaciones[estado_nombre].append(surf)
        # Sin esta clave "esquivar"/"patear" propias de Demonio no se usan
        # acá, pero deben existir vacías para que cambiar_estado() no falle.
        self._animaciones.setdefault("esquivar", [])

    def reiniciar_combate(self):
        super().reiniciar_combate()
        self._saltando = False
        self._contador_retroceso = 0
        self._velocidad_y = 0
        self.rect.y = self._suelo_y

    def actualizar_ia(self, jugador, jugador_ataco, nivel):
        """Misma firma que Demonio.actualizar_ia (mismo diccionario de resultado)."""
        resultado = {'ataco': False, 'esquivando': False}

        distancia_centro_x = jugador.rect.centerx - self.rect.centerx
        abs_distancia = abs(distancia_centro_x)
        self.direccion = 1 if distancia_centro_x > 0 else -1

        velocidad_ajustada = self._velocidad_base + (nivel * 0.9)
        prob_esquivar = min(0.92, self._probabilidad_esquivar + (nivel * 0.07))
        prob_atacar = min(0.97, self._probabilidad_atacar + (nivel * 0.05))

        # --- Física del salto-esquive: se resuelve antes que cualquier otra decisión ---
        if self._saltando:
            self._velocidad_y += self._gravedad
            self.rect.y += self._velocidad_y
            if self.rect.y >= self._suelo_y:
                self.rect.y = self._suelo_y
                self._velocidad_y = 0
                self._saltando = False
                self._esquivando = False
                self.cambiar_estado(random.choice(["golpear", "patear"]))
                resultado['ataco'] = True
                self._cooldown_ataque = random.randint(15, 35)
            else:
                resultado['esquivando'] = True
            self.rect.x = max(0, min(self.rect.x, C.ANCHO - C.TARGET_WIDTH))
            return resultado

        # --- ¿ESQUIVA? A diferencia de Demonio, decide al azar entre
        # retroceder caminando o saltar. ---
        if (not self._esquivando and jugador_ataco
                and jugador.estado_actual in ("golpear", "patear")
                and abs_distancia < self._rango_reaccion_esquiva
                and random.random() < prob_esquivar):
            self._esquivando = True
            if random.random() < 0.5:
                self._saltando = True
                self._velocidad_y = self._potencia_salto
                self.cambiar_estado("salto")
                resultado['esquivando'] = True
                self.rect.x = max(0, min(self.rect.x, C.ANCHO - C.TARGET_WIDTH))
                return resultado
            else:
                self.cambiar_estado("caminar")
                self._contador_retroceso = 0

        if self._esquivando and not self._saltando:
            resultado['esquivando'] = True
            if distancia_centro_x > 0:
                self._mover(-velocidad_ajustada)
            else:
                self._mover(velocidad_ajustada)

            self._contador_retroceso += 1
            if self._contador_retroceso > 12:
                self._esquivando = False
                self.cambiar_estado(random.choice(["golpear", "patear"]))
                resultado['ataco'] = True
                self._cooldown_ataque = random.randint(15, 35)

        else:
            if self._cooldown_ataque > 0:
                self._cooldown_ataque -= 1

            # Mientras esté en medio de golpe/patada/ataque especial, no se
            # interrumpe con otra decisión de movimiento.
            if self.estado_actual in ("golpear", "patear", "ataque"):
                pass
            elif abs_distancia > self._distancia_seguridad:
                self.cambiar_estado("caminar")
                if distancia_centro_x > 0:
                    self._mover(velocidad_ajustada)
                else:
                    self._mover(-velocidad_ajustada)

            elif abs_distancia < self._rango_ataque and self._cooldown_ataque == 0:
                if random.random() < prob_atacar:
                    if random.random() < self._probabilidad_ataque_especial:
                        self.cambiar_estado("ataque")
                    else:
                        self.cambiar_estado(random.choice(["golpear", "patear"]))
                    resultado['ataco'] = True
                    self._cooldown_ataque = random.randint(25, 50)
                else:
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
                if self.estado_actual in ("golpear", "patear", "ataque"):
                    self._estado_actual = "caminar"
                    self._frame_index = 0
                elif self.estado_actual == "salto":
                    self._frame_index = len(self._frames_de("salto")) - 1
                else:
                    self._frame_index = 0

        imagen_base = self._frames_de(self._estado_actual)[self._frame_index]
        if self._direccion == 1:
            self.image = pygame.transform.flip(imagen_base, True, False)
        else:
            self.image = imagen_base

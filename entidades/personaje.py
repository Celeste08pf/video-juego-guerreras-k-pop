"""
entidades/personaje.py
========================
Personaje: la guerrera jugable base (usada tal cual para Zoey y Rumi).
Hereda de EntidadAnimada, así que no repite la lógica de manejo de frames;
sólo agrega lo propio de una jugadora: inputs de teclado, física de salto y
la vida/vidas, encapsuladas detrás de properties y métodos.

Mira (ver entidades/mira.py) hereda de Personaje y sólo redefine
cargar_imagenes(), porque su animación de ataque especial tiene 4 frames
en vez de 3: es un ejemplo directo de polimorfismo, ya que el resto del
código (el bucle principal, la clase Juego) trata a Mira exactamente igual
que a cualquier otro Personaje, sin necesitar saber que es una subclase.
"""
import pygame

from config import constantes as C
from entidades.entidad_base import EntidadAnimada
from entidades.daga import Daga


class Personaje(EntidadAnimada):
    """Guerrera jugable: movimiento, ataques, vida y vidas encapsuladas."""

    SUELO_Y = C.SUELO_Y
    VIDA_MAXIMA = C.VIDA_MAXIMA_POR_VIDA

    def __init__(self, x, y, grupo_dagas, personaje_id=1, nombre="ZOEY"):
        super().__init__(x, y, C.TARGET_SIZE, cooldown_animacion=150)

        self._grupo_dagas = grupo_dagas
        self._personaje_id = personaje_id
        self._nombre = nombre

        # --- Estado privado de combate/vida: sólo se toca a través de
        # recibir_golpe(), curar() y reiniciar_para_nuevo_intento(). ---
        self._vida_actual = self.VIDA_MAXIMA
        self._vidas_restantes = C.VIDAS_INICIALES

        # --- Estado privado de física/movimiento ---
        self._velocidad = 6
        self._velocidad_y = 0
        self._gravedad = 1.2
        self._potencia_salto = -18
        self._en_el_suelo = True
        self._daga_disparada = False

        for estado in ("estandar", "caminar", "golpear", "patear", "lanzar",
                       "saltar", "agacharse", "bloquear"):
            self._animaciones[estado] = []

        self.cargar_imagenes()

        if self._animaciones[self._estado_actual]:
            self.image = self._animaciones[self._estado_actual][0]
        else:
            self.image = pygame.Surface(C.TARGET_SIZE)
            self.image.fill(C.ROSA_NEON)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = self.SUELO_Y

    # ---------------- Properties: acceso controlado ----------------------
    @property
    def nombre(self):
        return self._nombre

    @property
    def personaje_id(self):
        return self._personaje_id

    @property
    def vida_actual(self):
        return self._vida_actual

    @property
    def vidas_restantes(self):
        return self._vidas_restantes

    @property
    def en_el_suelo(self):
        return self._en_el_suelo

    # ---------------- Vida y vidas: encapsulado en métodos -----------------
    def esta_viva(self):
        return self._vidas_restantes > 0

    def recibir_golpe(self, dano):
        """
        Descuenta daño de la barra de vida actual. Si se agota, consume una
        vida completa y reinicia la barra (si aún le quedan vidas).
        Devuelve True si, tras este golpe, ya no le queda ninguna vida
        (game over) — así quien llama no necesita conocer los detalles
        internos del cálculo, sólo el resultado.
        """
        self._vida_actual -= dano
        if self._vida_actual <= 0:
            self._vidas_restantes -= 1
            self._vida_actual = self.VIDA_MAXIMA
            if self._vidas_restantes <= 0:
                return True
        return False

    def curar(self, cantidad):
        """Recarga la barra de vida actual (al recolectar un corazón)."""
        curo_algo = self._vida_actual < self.VIDA_MAXIMA
        self._vida_actual = min(self.VIDA_MAXIMA, self._vida_actual + cantidad)
        return curo_algo

    def reiniciar_para_nuevo_intento(self):
        """Se llama al empezar/reiniciar un nivel: vida y vidas al máximo."""
        self._vidas_restantes = C.VIDAS_INICIALES
        self._vida_actual = self.VIDA_MAXIMA
        self.rect.x = 100
        self.rect.y = self.SUELO_Y

    def empujar_atras(self):
        """Retrocede a la jugadora al recibir un golpe."""
        self.rect.x = 100

    def cambiar_estado(self, nuevo_estado):
        """Extiende el cambio de estado base: al empezar 'lanzar', reinicia
        la bandera que controla si ya se disparó la daga en este ataque."""
        estado_anterior = self._estado_actual
        super().cambiar_estado(nuevo_estado)
        if nuevo_estado == "lanzar" and estado_anterior != "lanzar":
            self._daga_disparada = False

    # ---------------- Carga de sprites (Mira la redefine) ------------------
    def cargar_imagenes(self):
        pid = self._personaje_id
        try:
            self._animaciones["estandar"].append(self.cargar_y_escalar(f"estandar {pid}"))
            for i in range(1, 4):
                self._animaciones["caminar"].append(self.cargar_y_escalar(f"caminar {pid}_{i}"))
            for i in range(1, 4):
                self._animaciones["golpear"].append(self.cargar_y_escalar(f"puño {pid}_{i}"))
            for i in range(1, 4):
                self._animaciones["patear"].append(self.cargar_y_escalar(f"patada {pid}_{i}"))
            for i in range(1, 4):
                self._animaciones["lanzar"].append(self.cargar_y_escalar(f"ataque {pid}_{i}"))
            self._animaciones["saltar"].append(self.cargar_y_escalar(f"salto {pid}_1"))
            self._animaciones["agacharse"].append(self.cargar_y_escalar(f"agacharse {pid}_1"))
            try:
                self._animaciones["bloquear"].append(self.cargar_y_escalar(f"bloquear {pid}"))
            except (FileNotFoundError, pygame.error):
                self._animaciones["bloquear"].append(self._animaciones["estandar"][0])
        except (FileNotFoundError, pygame.error) as e:
            print(f"[Personaje {pid}] No se pudieron cargar todas las imágenes: {e}")
            self._cargar_colores_de_respaldo(C.ROSA_NEON)

    def _cargar_colores_de_respaldo(self, color, frames_lanzar=3):
        """Genera superficies de color plano si faltan los archivos de imagen.
        frames_lanzar permite que Mira pida 4 frames (su ataque especial
        real tiene 4, no 3) en vez de tener que duplicar todo el método."""
        frames_por_estado = {
            "estandar": 1, "caminar": 3, "golpear": 3, "patear": 3,
            "lanzar": frames_lanzar, "saltar": 1, "agacharse": 1,
        }
        for estado in self._animaciones:
            self._animaciones[estado] = []
        for estado, num_frames in frames_por_estado.items():
            for _ in range(num_frames):
                surf = pygame.Surface(C.TARGET_SIZE)
                surf.fill(color)
                self._animaciones[estado].append(surf)
        surf_bloq = pygame.Surface(C.TARGET_SIZE)
        surf_bloq.fill(C.AZUL_ELECTRICO)
        self._animaciones["bloquear"].append(surf_bloq)

    # ---------------- Inputs, física y animación ---------------------------
    def manejar_inputs(self, estados_juego):
        teclas = pygame.key.get_pressed()

        if self._estado_actual in ("golpear", "patear", "lanzar"):
            return estados_juego

        if self._en_el_suelo and teclas[pygame.K_a] and teclas[pygame.K_s]:
            self._estado_actual = "BLOQUEO"
            estados_juego['bloqueando'] = True
            return estados_juego
        else:
            estados_juego['bloqueando'] = False
            if self._estado_actual == "BLOQUEO":
                self._estado_actual = "estandar"

        if self._en_el_suelo and teclas[pygame.K_s]:
            self._estado_actual = "CROUCH"
            vel_actual = self._velocidad // 2
        else:
            if self._estado_actual == "CROUCH":
                self._estado_actual = "estandar"
            vel_actual = self._velocidad

        moviendose = False
        if teclas[pygame.K_a] and self.rect.x > 0:
            self.rect.x -= vel_actual
            self.direccion = -1
            moviendose = True
            if self._en_el_suelo and self._estado_actual != "CROUCH":
                self.cambiar_estado("caminar")
        elif teclas[pygame.K_d] and self.rect.x < C.ANCHO - C.TARGET_WIDTH:
            self.rect.x += vel_actual
            self.direccion = 1
            moviendose = True
            if self._en_el_suelo and self._estado_actual != "CROUCH":
                self.cambiar_estado("caminar")

        if teclas[pygame.K_w] and self._en_el_suelo and self._estado_actual != "CROUCH":
            self._velocidad_y = self._potencia_salto
            self._en_el_suelo = False

        if self._en_el_suelo:
            if teclas[pygame.K_z]:
                self.cambiar_estado("golpear")
                estados_juego['texto'] = "¡Puñetazo!"
                estados_juego['tiempo'] = 25
                estados_juego['ataco'] = True
            elif teclas[pygame.K_x]:
                self.cambiar_estado("patear")
                estados_juego['texto'] = "¡Patada!"
                estados_juego['tiempo'] = 25
                estados_juego['ataco'] = True
            elif teclas[pygame.K_c]:
                # Las tres guerreras usan C, pero cada una con su arma:
                # Zoey lanza una daga (proyectil); Mira y Rumi golpean con
                # espada cuerpo a cuerpo (sin proyectil).
                self.cambiar_estado("lanzar")
                if self._personaje_id == 1:
                    estados_juego['texto'] = "¡Ataque con Daga!"
                else:
                    estados_juego['texto'] = "¡Ataque con Espada!"
                estados_juego['tiempo'] = 30
                estados_juego['ataco'] = True
            elif not moviendose and self._estado_actual != "CROUCH":
                self.cambiar_estado("estandar")

        return estados_juego

    def aplicar_gravedad(self):
        self._velocidad_y += self._gravedad
        self.rect.y += self._velocidad_y
        if self.rect.y >= self.SUELO_Y:
            self.rect.y = self.SUELO_Y
            self._velocidad_y = 0
            self._en_el_suelo = True

    def actualizar_animacion(self):
        if self._estado_actual == "BLOQUEO":
            imagen_base = self._frames_de("bloquear")[0] if self._frames_de("bloquear") \
                else self._frames_de("estandar")[0]
        elif self._estado_actual == "CROUCH":
            imagen_base = self._frames_de("agacharse")[0] if self._frames_de("agacharse") \
                else self._frames_de("estandar")[0]
        elif not self._en_el_suelo and self._estado_actual not in ("golpear", "patear", "lanzar"):
            # Salto: cada guerrera usa su propia imagen de salto.
            imagen_base = self._frames_de("saltar")[0] if self._frames_de("saltar") \
                else self._frames_de("caminar")[1]
        else:
            # "estandar" reproduce el mismo ciclo de "caminar" como pose de
            # reposo (igual que el demonio), para que se vea un ligero
            # movimiento constante en vez de quedar congelada.
            frames_ciclo = (
                self._frames_de("caminar")
                if self._estado_actual == "estandar" and self._frames_de("caminar")
                else self._frames_de(self._estado_actual)
            )

            if self._debe_avanzar_frame():
                self._frame_index += 1

                if self._estado_actual == "lanzar" and self._frame_index == 2 and not self._daga_disparada:
                    # Sólo Zoey (personaje_id == 1) dispara una daga física:
                    # es la única guerrera con arma a distancia. Mira y
                    # Rumi resuelven su daño por colisión directa.
                    if self._personaje_id == 1:
                        nueva_daga = Daga(self.rect.x, self.rect.y, self._direccion)
                        self._grupo_dagas.add(nueva_daga)
                    self._daga_disparada = True

                if self._frame_index >= len(frames_ciclo):
                    if self._estado_actual in ("golpear", "patear", "lanzar"):
                        self._estado_actual = "estandar"
                        frames_ciclo = self._frames_de("caminar") or self._frames_de("estandar")
                    self._frame_index = 0

            imagen_base = frames_ciclo[self._frame_index]

        self.image = self._aplicar_flip(imagen_base)

    def update(self, estados_juego):
        nuevos_estados = self.manejar_inputs(estados_juego)
        self.aplicar_gravedad()
        self.actualizar_animacion()
        return nuevos_estados

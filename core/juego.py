"""
core/juego.py
==============
Clase Juego: encapsula TODO el estado que en el script original vivía en
variables globales (nivel actual, puntaje, niveles desbloqueados, sprites,
etc.) como atributos privados de un único objeto. El bucle principal pasa
a ser un método de esta clase (ejecutar()), y cada responsabilidad grande
(entrada de un nivel, resolución de colisiones, aparición de objetos) es
su propio método privado, en vez de un bloque enorme de código suelto.
"""
import random
import sys

import pygame

from config import constantes as C
from core.utils import cambiar_musica_nivel, cargar_fondo_nivel
from entidades.mira import Mira
from entidades.personaje import Personaje
from entidades.demonio import Demonio
from entidades.demonio2 import Demonio2
from entidades.objeto import Objeto
from ui.hud import HUD
from ui.menus import MenuNiveles, MenuSeleccionPersonaje


class Juego:
    """Coordina pantalla, entidades, menús y el bucle principal del juego."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self._pantalla = pygame.display.set_mode((C.ANCHO, C.ALTO))
        pygame.display.set_caption("Las Guerreras K-Pop - Selección de Niveles")
        self._clock = pygame.time.Clock()

        # --- Estado privado del juego (antes eran variables globales) -----
        self._niveles_desbloqueados = {
            1: True,
            2: C.MODO_PRUEBA_DESBLOQUEAR_TODO,
            3: C.MODO_PRUEBA_DESBLOQUEAR_TODO,
            4: C.MODO_PRUEBA_DESBLOQUEAR_TODO,
            5: C.MODO_PRUEBA_DESBLOQUEAR_TODO,
        }
        self._nivel_actual = 1
        self._demonios_eliminados = 0
        self._puntaje = 0
        self._nombre_personaje_actual = "ZOEY"
        self._imagen_fondo_nivel = None

        self._jugador = None
        self._demonio_malo = None

        self._sprites_dagas = pygame.sprite.Group()
        self._todos_los_sprites = pygame.sprite.Group()
        self._sprites_objetos = pygame.sprite.Group()
        self._temporizador_objeto = random.randint(C.INTERVALO_MIN_OBJETO, C.INTERVALO_MAX_OBJETO)

        self._estados_juego = {'texto': "", 'tiempo': 0, 'ataco': False, 'bloqueando': False}

        self._hud = HUD()
        self._menu_niveles = MenuNiveles(self._pantalla, self._clock)
        self._menu_personaje = MenuSeleccionPersonaje(self._pantalla, self._clock)

    # ---------------- Creación de entidades ---------------------------------
    def _crear_jugador(self, personaje_id, nombre, x, y):
        """
        Usa la clase Mira cuando corresponde (personaje_id == 2); en
        cualquier otro caso, la clase Personaje genérica. Este es el punto
        del código donde se aprovecha el polimorfismo: quien llama no
        necesita distinguir después entre Personaje y Mira.
        """
        if personaje_id == 2:
            return Mira(x, y, self._sprites_dagas, personaje_id=2, nombre="MIRA")
        return Personaje(x, y, self._sprites_dagas, personaje_id, nombre)

    def _crear_demonio_para_nivel(self, nivel, x=600, y=300):
        """Niveles 1-3 -> Demonio | Niveles 4-5 -> Demonio2."""
        if nivel >= 4:
            return Demonio2(x, y)
        return Demonio(x, y)

    def _obtener_personaje_para_nivel(self, nivel):
        """Nivel 1 -> Zoey | Nivel 2 -> Mira | Nivel 3 -> Rumi | 4 y 5 -> elegir."""
        if nivel == 1:
            return 1, "ZOEY"
        elif nivel == 2:
            return 2, "MIRA"
        elif nivel == 3:
            return 3, "RUMI"
        return self._menu_personaje.mostrar(nivel)

    def _iniciar_nivel(self, nivel):
        """Se llama al entrar a un nivel: recrea jugador y enemigo, limpia objetos."""
        personaje_id, nombre = self._obtener_personaje_para_nivel(nivel)
        self._nombre_personaje_actual = nombre

        if self._jugador is not None:
            self._todos_los_sprites.remove(self._jugador)
        self._jugador = self._crear_jugador(personaje_id, nombre, 100, 300)
        self._todos_los_sprites.add(self._jugador)

        if self._demonio_malo is not None:
            self._todos_los_sprites.remove(self._demonio_malo)
        self._demonio_malo = self._crear_demonio_para_nivel(nivel)
        self._todos_los_sprites.add(self._demonio_malo)

        self._sprites_objetos.empty()
        self._temporizador_objeto = random.randint(C.INTERVALO_MIN_OBJETO, C.INTERVALO_MAX_OBJETO)

        cambiar_musica_nivel(nivel)
        self._imagen_fondo_nivel = cargar_fondo_nivel(nivel)

    def _reiniciar_intento_y_volver_al_menu(self):
        """Reinicia el progreso del intento actual y vuelve al menú de niveles."""
        self._demonios_eliminados = 0
        self._nivel_actual = self._menu_niveles.mostrar(self._niveles_desbloqueados)
        self._iniciar_nivel(self._nivel_actual)

    # ---------------- Colisiones y reglas de combate -------------------------
    def _resolver_ataque_del_demonio(self, resultado_ia):
        """Aplica daño de un ataque conectado del demonio sobre la jugadora."""
        if not (resultado_ia['ataco'] and self._demonio_malo.rect.colliderect(self._jugador.rect)):
            return

        if self._estados_juego['bloqueando']:
            self._estados_juego['texto'] = " ¡Bloqueado! "
            self._estados_juego['tiempo'] = 30
            return

        game_over = self._jugador.recibir_golpe(C.DAÑO_GOLPE_DEMONIO)
        self._estados_juego['texto'] = f" ¡{self._nombre_personaje_actual} recibió un golpe! "
        self._estados_juego['tiempo'] = 40
        self._jugador.empujar_atras()

        if game_over:
            self._mostrar_game_over()

    def _resolver_ataque_de_la_jugadora(self, resultado_ia):
        """
        Aplica daño de golpe, patada, daga o espada sobre el demonio. Todos
        usan colliderect real (golpe/patada/espada con un pequeño inflate
        para darles algo más de alcance).
        """
        if self._estados_juego['ataco'] and not resultado_ia['esquivando']:
            estado = self._jugador.estado_actual
            if estado == "golpear" and self._jugador.rect.colliderect(self._demonio_malo.rect):
                self._infligir_dano_al_demonio(20, C.PUNTOS_GOLPE)
            elif estado == "patear":
                alcance = self._demonio_malo.rect.inflate(40, 0)
                if self._jugador.rect.colliderect(alcance):
                    self._infligir_dano_al_demonio(25, C.PUNTOS_PATADA)
            elif estado == "lanzar" and self._jugador.personaje_id != 1:
                # Ataque con espada de Mira/Rumi: cuerpo a cuerpo, sin daga.
                alcance = self._demonio_malo.rect.inflate(50, 0)
                if self._jugador.rect.colliderect(alcance):
                    self._infligir_dano_al_demonio(25, C.PUNTOS_ESPADA)

        # Sólo Zoey genera sprites de Daga; para las demás nunca hay colisión acá.
        for daga in list(self._sprites_dagas):
            if daga.rect.colliderect(self._demonio_malo.rect):
                self._infligir_dano_al_demonio(20, C.PUNTOS_DAGA)
                daga.kill()

    def _infligir_dano_al_demonio(self, dano, puntos):
        eliminado = self._demonio_malo.recibir_golpe(dano)
        self._puntaje += puntos
        if eliminado:
            self._demonio_eliminado()

    def _demonio_eliminado(self):
        self._demonios_eliminados += 1
        self._puntaje += C.PUNTOS_DEMONIO_ELIMINADO
        self._demonio_malo.reiniciar_vida()
        self._demonio_malo.rect.x = random.randint(450, 700)
        self._demonio_malo.reiniciar_combate()
        self._estados_juego['texto'] = "¡Demonio Eliminado! 💀"
        self._estados_juego['tiempo'] = 30

        objetivo = C.OBJETIVO_DEMONIOS_POR_NIVEL.get(self._nivel_actual, 3)
        if self._demonios_eliminados >= objetivo:
            self._resolver_victoria_de_nivel()

    def _resolver_victoria_de_nivel(self):
        siguiente = self._nivel_actual + 1
        if siguiente in self._niveles_desbloqueados:
            if not self._niveles_desbloqueados[siguiente]:
                self._niveles_desbloqueados[siguiente] = True
                self._estados_juego['texto'] = (
                    f"🎉 ¡Nivel {self._nivel_actual} ganado! ¡Nivel {siguiente} desbloqueado! 🎉"
                )
        else:
            self._estados_juego['texto'] = "🏆 ¡Has completado todos los niveles del juego! 🏆"

        pygame.mixer.music.stop()
        self._hud.mostrar_mensaje_pantalla_completa(self._pantalla, self._estados_juego['texto'], C.DORADO)

        self._jugador.reiniciar_para_nuevo_intento()
        self._reiniciar_intento_y_volver_al_menu()

    def _mostrar_game_over(self):
        pygame.mixer.music.stop()
        self._hud.mostrar_mensaje_pantalla_completa(
            self._pantalla, "💀 ¡GAME OVER! 💀", C.ROJO, puntaje_final=self._puntaje
        )
        self._jugador.reiniciar_para_nuevo_intento()
        self._reiniciar_intento_y_volver_al_menu()

    # ---------------- Objetos recolectables -----------------------------------
    def _actualizar_aparicion_de_objetos(self):
        self._temporizador_objeto -= 1
        if self._temporizador_objeto <= 0 and len(self._sprites_objetos) < C.MAX_OBJETOS_EN_PANTALLA:
            self._sprites_objetos.add(Objeto.generar_aleatorio())
            self._temporizador_objeto = random.randint(C.INTERVALO_MIN_OBJETO, C.INTERVALO_MAX_OBJETO)

    def _resolver_recoleccion_de_objetos(self):
        for obj in list(self._sprites_objetos):
            if not self._jugador.rect.colliderect(obj.rect):
                continue

            self._puntaje += obj.puntaje_otorgado
            if obj.tipo == "corazon":
                if self._jugador.curar(C.CURACION_CORAZON):
                    self._estados_juego['texto'] = f" ¡Vida recargada! (+{obj.puntaje_otorgado} pts) "
                else:
                    self._estados_juego['texto'] = f" ¡Corazón recolectado! (+{obj.puntaje_otorgado} pts) "
            else:
                self._estados_juego['texto'] = f" ¡Moneda recolectada! (+{obj.puntaje_otorgado} pts) "
            self._estados_juego['tiempo'] = 30
            obj.kill()

    # ---------------- Eventos --------------------------------------------------
    def _procesar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_p:
                # Salir del nivel actual y volver al menú (tecla P).
                pygame.mixer.music.stop()
                self._jugador.reiniciar_para_nuevo_intento()
                self._reiniciar_intento_y_volver_al_menu()

    # ---------------- Dibujado --------------------------------------------------
    def _dibujar_escena(self):
        pantalla = self._pantalla
        pantalla.fill(C.NEGRO_PROFUNDO)
        pantalla.blit(self._imagen_fondo_nivel, (0, 0))

        pygame.draw.line(pantalla, C.ROSA_NEON, (0, C.LINEA_SUELO_Y), (C.ANCHO, C.LINEA_SUELO_Y), 5)
        pygame.draw.line(pantalla, C.MORADO_BRILLANTE, (0, C.LINEA_SUELO_Y + 5), (C.ANCHO, C.LINEA_SUELO_Y + 5), 2)

        self._sprites_objetos.draw(pantalla)
        self._sprites_dagas.draw(pantalla)
        self._todos_los_sprites.draw(pantalla)

        self._hud.dibujar_barra_vida_demonio(pantalla, self._demonio_malo)
        self._hud.dibujar_barra_vida_jugador(pantalla, self._jugador)
        self._hud.dibujar(
            pantalla, self._nombre_personaje_actual, self._nivel_actual,
            self._jugador, self._demonios_eliminados, self._puntaje, self._estados_juego,
        )

        pygame.display.flip()

    # ---------------- Bucle principal --------------------------------------------
    def ejecutar(self):
        """Punto de entrada: muestra el menú inicial y corre el bucle del juego."""
        self._nivel_actual = self._menu_niveles.mostrar(self._niveles_desbloqueados)
        self._iniciar_nivel(self._nivel_actual)

        while True:
            self._procesar_eventos()

            self._estados_juego['ataco'] = False
            self._estados_juego = self._jugador.update(self._estados_juego)
            self._sprites_dagas.update()
            self._sprites_objetos.update()
            self._demonio_malo.update()

            resultado_ia = self._demonio_malo.actualizar_ia(
                self._jugador, self._estados_juego['ataco'], self._nivel_actual
            )

            self._resolver_ataque_del_demonio(resultado_ia)
            self._resolver_ataque_de_la_jugadora(resultado_ia)
            self._actualizar_aparicion_de_objetos()
            self._resolver_recoleccion_de_objetos()

            if self._estados_juego['tiempo'] > 0:
                self._estados_juego['tiempo'] -= 1

            self._dibujar_escena()
            self._clock.tick(C.FPS)

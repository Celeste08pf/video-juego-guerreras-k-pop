"""
ui/hud.py
=========
Clase HUD: agrupa todo el dibujo de la interfaz superior del juego (panel
de estado, corazones de vida, barra de vida flotante y texto emergente de
combate) en un solo objeto, en vez de funciones sueltas con la pantalla
como parámetro repetido en cada llamada. Encapsula sus propias fuentes.
"""
import pygame

from config import constantes as C
from core.utils import obtener_fuente, renderizar_texto_contorno

HEART_BITMAP = [
    "0110110",
    "1111111",
    "1111111",
    "0111110",
    "0011100",
    "0001000",
]


class HUD:
    """Dibuja toda la interfaz de juego sobre una superficie de pantalla dada."""

    ANCHO_BARRA_VIDA_JUGADOR = 80
    ALTO_BARRA_VIDA_JUGADOR = 8

    def __init__(self):
        self._fuente_hud = obtener_fuente(20)
        self._fuente_combate = obtener_fuente(26)

    # ---------------- Corazones y barra de vida de la jugadora ------------
    def _dibujar_corazon(self, pantalla, x, y, pixel, color, color_borde=(0, 0, 0)):
        for fila_idx, fila in enumerate(HEART_BITMAP):
            for col_idx, celda in enumerate(fila):
                if celda == "1":
                    rect = (x + col_idx * pixel, y + fila_idx * pixel, pixel, pixel)
                    pygame.draw.rect(pantalla, color, rect)
                    pygame.draw.rect(pantalla, color_borde, rect, 1)

    def _dibujar_corazones_jugador(self, pantalla, x, y, vidas):
        pixel = 3
        ancho_corazon = 7 * pixel
        espacio_corazon = ancho_corazon + 5
        for i in range(vidas):
            cx = x + i * espacio_corazon
            self._dibujar_corazon(pantalla, cx, y, pixel, C.ROJO)

    def dibujar_barra_vida_jugador(self, pantalla, jugador):
        """Barra de vida flotando sobre la cabeza de la guerrera (tamaño fijo)."""
        pos_x = jugador.rect.x + (C.TARGET_WIDTH - self.ANCHO_BARRA_VIDA_JUGADOR) // 2
        pos_y = jugador.rect.y - 15
        fraccion = max(0.0, min(1.0, jugador.vida_actual / jugador.VIDA_MAXIMA))

        pygame.draw.rect(pantalla, (100, 0, 0),
                          (pos_x, pos_y, self.ANCHO_BARRA_VIDA_JUGADOR, self.ALTO_BARRA_VIDA_JUGADOR))
        pygame.draw.rect(pantalla, C.ROJO,
                          (pos_x, pos_y, self.ANCHO_BARRA_VIDA_JUGADOR * fraccion, self.ALTO_BARRA_VIDA_JUGADOR))

    def dibujar_barra_vida_demonio(self, pantalla, demonio):
        pygame.draw.rect(pantalla, (100, 0, 0), (demonio.rect.x + 40, demonio.rect.y - 15, 80, 8))
        pygame.draw.rect(pantalla, C.AZUL_ELECTRICO,
                          (demonio.rect.x + 40, demonio.rect.y - 15, 80 * demonio.fraccion_vida, 8))

    # ---------------- Panel superior (HUD) ---------------------------------
    def dibujar(self, pantalla, nombre_personaje, nivel, jugador, kills, puntaje_actual, estado_juego):
        """Dibuja el panel translúcido con nombre, vidas, objetivo, puntaje y controles."""
        panel_hud = pygame.Surface((C.ANCHO, 92), pygame.SRCALPHA)
        panel_hud.fill((0, 0, 0, 130))
        pantalla.blit(panel_hud, (0, 0))

        txt_titulo = self._fuente_hud.render(f"{nombre_personaje}  •  NIVEL {nivel}", True, C.ROSA_NEON)
        txt_vidas = self._fuente_hud.render("VIDAS:", True, C.ROJO)
        objetivo_nivel = C.OBJETIVO_DEMONIOS_POR_NIVEL.get(nivel, 3)
        txt_kills = self._fuente_hud.render(
            f"OBJETIVO: {kills}/{objetivo_nivel} DEMONIOS   •   PUNTAJE: {puntaje_actual}", True, C.AZUL_ELECTRICO
        )
        txt_controles = self._fuente_hud.render("MOVER: W A S D  |  ATAQUES: Z X C", True, C.DORADO)

        pantalla.blit(txt_titulo, (20, 10))
        pantalla.blit(txt_vidas, (20, 38))
        self._dibujar_corazones_jugador(pantalla, 20 + txt_vidas.get_width() + 10, 38, jugador.vidas_restantes)
        pantalla.blit(txt_kills, (20, 64))
        pantalla.blit(txt_controles, (C.ANCHO - txt_controles.get_width() - 20, 38))

        if estado_juego['tiempo'] > 0:
            render_pop = renderizar_texto_contorno(self._fuente_combate, estado_juego['texto'], C.MORADO_BRILLANTE)
            pantalla.blit(render_pop, (C.ANCHO // 2 - render_pop.get_width() // 2, 180))

    # ---------------- Pantallas de victoria / derrota -----------------------
    def mostrar_mensaje_pantalla_completa(self, pantalla, texto, color, puntaje_final=None):
        """Pantalla negra con un mensaje centrado (usada para victoria y game over).
        Si se pasa puntaje_final, agrega una segunda línea debajo con el puntaje."""
        pantalla.fill(C.NEGRO_PROFUNDO)
        render_texto = renderizar_texto_contorno(self._fuente_combate, texto, color)
        pos_y = C.ALTO // 2 - 20 if puntaje_final is not None else C.ALTO // 2
        pantalla.blit(render_texto, (C.ANCHO // 2 - render_texto.get_width() // 2, pos_y))

        if puntaje_final is not None:
            render_puntaje = renderizar_texto_contorno(
                self._fuente_hud, f"Puntaje final: {puntaje_final}", C.BLANCO_BRILLANTE
            )
            pantalla.blit(render_puntaje, (C.ANCHO // 2 - render_puntaje.get_width() // 2, C.ALTO // 2 + 30))

        pygame.display.flip()
        pygame.time.wait(3000)

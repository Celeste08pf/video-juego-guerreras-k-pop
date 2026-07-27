"""
ui/menus.py
===========
Pantallas de menú del juego, encapsuladas como clases:
- MenuNiveles: selección de nivel, con miniaturas y estado bloqueado/desbloqueado.
- MenuSeleccionPersonaje: elegir guerrera en los niveles 4 y 5.

Cada clase administra su propio bucle de eventos y sus propias fuentes,
en vez de depender de funciones sueltas que reciben la pantalla como
parámetro en cada llamada.
"""
import sys

import pygame

from config import constantes as C
from core.utils import (
    cargar_imagen_menu,
    cargar_miniaturas_niveles,
    obtener_fuente,
    renderizar_texto_contorno,
)


class MenuNiveles:
    """Pantalla de selección de nivel con panel de previsualización."""

    def __init__(self, pantalla, clock):
        self._pantalla = pantalla
        self._clock = clock
        self._imagen_menu = cargar_imagen_menu()
        self._miniaturas = cargar_miniaturas_niveles()
        self._fuente_titulo = obtener_fuente(36)
        self._fuente_opciones = obtener_fuente(20)
        self._fuente_aviso = obtener_fuente(18)
        self._fuente_preview = obtener_fuente(18)

    def mostrar(self, niveles_desbloqueados):
        """
        Bucle del menú. Recibe el dict {nivel: bool} de niveles
        desbloqueados y devuelve el número de nivel elegido por la jugadora.
        """
        seleccionado = 1
        aviso_bloqueado = False
        aviso_timer = 0

        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_UP:
                        seleccionado = seleccionado - 1 if seleccionado > 1 else 5
                        aviso_bloqueado = False
                    elif evento.key == pygame.K_DOWN:
                        seleccionado = seleccionado + 1 if seleccionado < 5 else 1
                        aviso_bloqueado = False
                    elif evento.key == pygame.K_RETURN:
                        if niveles_desbloqueados[seleccionado]:
                            return seleccionado
                        aviso_bloqueado = True
                        aviso_timer = 40

            self._dibujar(niveles_desbloqueados, seleccionado, aviso_bloqueado, aviso_timer)
            if aviso_bloqueado and aviso_timer > 0:
                aviso_timer -= 1

            pygame.display.flip()
            self._clock.tick(C.FPS)

    def _dibujar(self, niveles_desbloqueados, seleccionado, aviso_bloqueado, aviso_timer):
        pantalla = self._pantalla
        pantalla.fill(C.NEGRO_PROFUNDO)
        pantalla.blit(self._imagen_menu, (0, 0))

        txt_titulo = renderizar_texto_contorno(self._fuente_titulo, "MENÚ DE NIVELES", C.ROSA_NEON)
        pantalla.blit(txt_titulo, (C.ANCHO // 2 - txt_titulo.get_width() // 2, 25))

        self._dibujar_lista_niveles(niveles_desbloqueados, seleccionado)
        self._dibujar_preview(niveles_desbloqueados, seleccionado)

        if aviso_bloqueado and aviso_timer > 0:
            txt_bloqueo = renderizar_texto_contorno(
                self._fuente_aviso,
                "⚠️ ¡Este nivel está bloqueado! Completa el anterior para desbloquearlo.",
                C.ROJO,
            )
            pantalla.blit(txt_bloqueo, (C.ANCHO // 2 - txt_bloqueo.get_width() // 2, C.ALTO - 60))

    def _dibujar_lista_niveles(self, niveles_desbloqueados, seleccionado):
        pantalla = self._pantalla
        pos_x_lista = 40
        for i in range(1, 6):
            desbloqueado = niveles_desbloqueados[i]
            estado_texto = "🟢 DISPONIBLE" if desbloqueado else "🔒 BLOQUEADO"
            color_texto = C.BLANCO_BRILLANTE if desbloqueado else C.GRIS_BLOQUEADO

            personaje_texto = C.PERSONAJE_POR_NIVEL_TEXTO.get(i, "")
            texto_nivel = f"Nivel {i} ({personaje_texto})"

            if i == seleccionado:
                color_texto = C.AZUL_ELECTRICO if desbloqueado else C.ROJO
                texto_nivel = f"> {texto_nivel}"

            render_opcion = renderizar_texto_contorno(self._fuente_opciones, texto_nivel, color_texto)
            render_estado = renderizar_texto_contorno(self._fuente_opciones, estado_texto, color_texto)
            pos_y = 110 + (i * 48)
            pantalla.blit(render_opcion, (pos_x_lista, pos_y))
            pantalla.blit(render_estado, (pos_x_lista, pos_y + 22))

    def _dibujar_preview(self, niveles_desbloqueados, seleccionado):
        pantalla = self._pantalla
        pos_preview = (C.ANCHO - C.TAMANO_PREVIEW[0] - 40, 90)
        pantalla.blit(self._miniaturas[seleccionado], pos_preview)

        desbloqueado_sel = niveles_desbloqueados[seleccionado]
        color_borde = C.AZUL_ELECTRICO if desbloqueado_sel else C.GRIS_BLOQUEADO
        pygame.draw.rect(pantalla, color_borde, (*pos_preview, *C.TAMANO_PREVIEW), 4)

        if not desbloqueado_sel:
            overlay = pygame.Surface(C.TAMANO_PREVIEW, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            pantalla.blit(overlay, pos_preview)
            txt_candado = renderizar_texto_contorno(self._fuente_titulo, "🔒", C.GRIS_BLOQUEADO)
            pantalla.blit(
                txt_candado,
                (
                    pos_preview[0] + C.TAMANO_PREVIEW[0] // 2 - txt_candado.get_width() // 2,
                    pos_preview[1] + C.TAMANO_PREVIEW[1] // 2 - txt_candado.get_height() // 2,
                ),
            )

        txt_preview_nombre = renderizar_texto_contorno(
            self._fuente_preview,
            f"NIVEL {seleccionado}: {C.PERSONAJE_POR_NIVEL_TEXTO.get(seleccionado, '')}",
            C.DORADO,
        )
        pantalla.blit(txt_preview_nombre, (pos_preview[0], pos_preview[1] + C.TAMANO_PREVIEW[1] + 10))


class MenuSeleccionPersonaje:
    """Pantalla de elección de guerrera, usada en los niveles 4 y 5."""

    OPCIONES = {
        1: ("ZOEY", C.ROSA_NEON),
        2: ("MIRA", C.AZUL_ELECTRICO),
        3: ("RUMI", C.MORADO_BRILLANTE),
    }

    def __init__(self, pantalla, clock):
        self._pantalla = pantalla
        self._clock = clock
        self._fuente_titulo = obtener_fuente(30)
        self._fuente_opciones = obtener_fuente(24)
        self._fuente_aviso = obtener_fuente(18)

    def mostrar(self, nivel):
        """Devuelve (personaje_id, nombre) elegido con las teclas 1, 2 o 3."""
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key in (pygame.K_1, pygame.K_KP1):
                        return 1, self.OPCIONES[1][0]
                    elif evento.key in (pygame.K_2, pygame.K_KP2):
                        return 2, self.OPCIONES[2][0]
                    elif evento.key in (pygame.K_3, pygame.K_KP3):
                        return 3, self.OPCIONES[3][0]

            self._dibujar(nivel)
            pygame.display.flip()
            self._clock.tick(C.FPS)

    def _dibujar(self, nivel):
        pantalla = self._pantalla
        pantalla.fill(C.NEGRO_PROFUNDO)

        txt_titulo = renderizar_texto_contorno(
            self._fuente_titulo, f"NIVEL {nivel} - ELIGE TU GUERRERA", C.DORADO
        )
        pantalla.blit(txt_titulo, (C.ANCHO // 2 - txt_titulo.get_width() // 2, 60))

        pos_y = 170
        for pid, (nombre, color) in self.OPCIONES.items():
            texto = f"[{pid}]  {nombre}"
            render_txt = renderizar_texto_contorno(self._fuente_opciones, texto, color)
            pantalla.blit(render_txt, (C.ANCHO // 2 - render_txt.get_width() // 2, pos_y))
            pos_y += 55

        aviso = renderizar_texto_contorno(
            self._fuente_aviso, "Presiona 1, 2 o 3 para elegir a tu guerrera", C.BLANCO_BRILLANTE
        )
        pantalla.blit(aviso, (C.ANCHO // 2 - aviso.get_width() // 2, pos_y + 30))

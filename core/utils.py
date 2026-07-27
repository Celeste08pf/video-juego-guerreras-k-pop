"""
core/utils.py
=============
Funciones de apoyo que usan varias partes del juego (fuentes, texto con
contorno, y carga de imágenes/música desde la carpeta 'multimedia'). Se
mantienen como funciones sueltas -y no como clases- porque no guardan
estado propio: son simples utilidades reutilizables.
"""
import os
import pygame

from config import constantes as C


def obtener_fuente(tamano, negrita=True):
    """Devuelve la fuente oficial del juego en el tamaño solicitado."""
    return pygame.font.SysFont(C.NOMBRE_FUENTE, tamano, bold=negrita)


def renderizar_texto_contorno(fuente_obj, texto, color_texto, color_contorno=(0, 0, 0), grosor=2):
    """
    Renderiza un texto con un contorno oscuro alrededor para que resalte
    con más fuerza sin importar qué haya de fondo.
    """
    base = fuente_obj.render(texto, True, color_texto)
    superficie = pygame.Surface(
        (base.get_width() + grosor * 2, base.get_height() + grosor * 2), pygame.SRCALPHA
    )
    contorno = fuente_obj.render(texto, True, color_contorno)
    for dx in (-grosor, 0, grosor):
        for dy in (-grosor, 0, grosor):
            if dx == 0 and dy == 0:
                continue
            superficie.blit(contorno, (dx + grosor, dy + grosor))
    superficie.blit(base, (grosor, grosor))
    return superficie


def _ruta_multimedia(*partes):
    """Arma una ruta absoluta dentro de la carpeta 'multimedia' del proyecto."""
    raiz_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(raiz_proyecto, "multimedia", *partes)


def cambiar_musica_nivel(nivel):
    """Carga y reproduce en bucle la música correspondiente al nivel."""
    try:
        ruta_musica = _ruta_multimedia(f"nivel{nivel}.mpeg")
        if not os.path.exists(ruta_musica):
            ruta_musica = _ruta_multimedia("nivel1.mpeg")

        pygame.mixer.music.load(ruta_musica)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.6)
    except pygame.error:
        print(f"Advertencia de Audio: No se pudo reproducir la música para el Nivel {nivel}.")


def cargar_imagen_menu():
    """Carga la imagen de fondo del menú principal ('menu.png/.jpg/...')."""
    extensiones = ['.png', '.jpg', '.jpeg', '.webp', '.bmp']
    for ext in extensiones:
        ruta_imagen = _ruta_multimedia("menu" + ext)
        if os.path.isfile(ruta_imagen):
            try:
                imagen = pygame.image.load(ruta_imagen).convert_alpha()
                return pygame.transform.scale(imagen, (C.ANCHO, C.ALTO))
            except pygame.error:
                pass

    fondo_respaldo = pygame.Surface((C.ANCHO, C.ALTO))
    fondo_respaldo.fill(C.NEGRO_PROFUNDO)
    return fondo_respaldo


def cargar_fondo_nivel(nivel):
    """Carga la imagen de fondo de un nivel ('fondo{n}.png/.jpg/...')."""
    extensiones = ['.png', '.jpg', '.jpeg', '.webp', '.bmp']
    for ext in extensiones:
        ruta_imagen = _ruta_multimedia(f"fondo{nivel}" + ext)
        if os.path.isfile(ruta_imagen):
            try:
                imagen = pygame.image.load(ruta_imagen).convert_alpha()
                return pygame.transform.scale(imagen, (C.ANCHO, C.ALTO))
            except pygame.error:
                pass

    fondo_respaldo = pygame.Surface((C.ANCHO, C.ALTO))
    fondo_respaldo.fill(C.NEGRO_PROFUNDO)
    return fondo_respaldo


def cargar_imagen_flexible(nombre_base, tamano):
    """
    Busca en 'multimedia' un archivo llamado nombre_base + extensión
    (probando .png, .jpg, .jpeg, .webp, .bmp) y devuelve la imagen ya
    escalada al tamaño indicado. Si no encuentra nada, lanza
    FileNotFoundError para que quien llama use su color de respaldo.
    """
    extensiones = ['.png', '.jpg', '.jpeg', '.webp', '.bmp']
    for ext in extensiones:
        ruta_imagen = _ruta_multimedia(nombre_base + ext)
        if os.path.isfile(ruta_imagen):
            imagen = pygame.image.load(ruta_imagen).convert_alpha()
            return pygame.transform.scale(imagen, tamano)

    raise FileNotFoundError(
        f"No se encontró la imagen '{nombre_base}' en la carpeta multimedia "
        f"(se probaron las extensiones: {', '.join(extensiones)})"
    )


def cargar_miniaturas_niveles():
    """Carga una miniatura del fondo real de cada uno de los 5 niveles."""
    miniaturas = {}
    for n in range(1, 6):
        fondo_completo = cargar_fondo_nivel(n)
        miniaturas[n] = pygame.transform.scale(fondo_completo, C.TAMANO_PREVIEW)
    return miniaturas

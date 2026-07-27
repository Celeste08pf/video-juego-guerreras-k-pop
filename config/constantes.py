"""
config/constantes.py
=====================
Todos los valores fijos del juego en un solo lugar: dimensiones de pantalla,
paleta de colores, tamaños de sprites y tablas de configuración por nivel.

Mantener las constantes separadas del resto del código es lo que permite que
las demás clases (Personaje, Demonio, HUD, etc.) no dependan unas de otras
directamente, sino de este único módulo compartido.
"""

# --- PANTALLA ---
ANCHO = 800
ALTO = 500
FPS = 60

# --- TAMAÑO OBJETIVO DE LOS SPRITES (25% de la pantalla) ---
TARGET_WIDTH = int(ANCHO * 0.25)
TARGET_HEIGHT = int(ALTO * 0.25)
TARGET_SIZE = (TARGET_WIDTH, TARGET_HEIGHT)

# --- COLORES OFICIALES DEL GDD ---
NEGRO_PROFUNDO = (18, 18, 18)       # Fondo
ROSA_NEON = (255, 45, 210)          # Interfaz / Zoey
MORADO_BRILLANTE = (168, 60, 255)   # Energía / Habilidades / Rumi
AZUL_ELECTRICO = (20, 210, 255)     # UI / Efectos / Mira
TURQUESA = (0, 255, 213)            # Demonios
BLANCO_BRILLANTE = (255, 255, 255)  # Texto
DORADO = (255, 225, 40)             # Barra Definitiva / Controles
ROJO = (255, 40, 40)                # Vidas / alertas
GRIS_BLOQUEADO = (150, 150, 165)    # Niveles bloqueados

# --- FUENTE ÚNICA DEL JUEGO ---
NOMBRE_FUENTE = "Silkscreen"

# --- MODO DE PRUEBA ---
# Ponerlo en False antes de entregar el proyecto: mientras esté en True, el
# menú arranca con los 5 niveles desbloqueados.
MODO_PRUEBA_DESBLOQUEAR_TODO = True

# --- INFORMACIÓN DE PERSONAJE POR NIVEL (texto informativo del menú) ---
PERSONAJE_POR_NIVEL_TEXTO = {
    1: "Zoey",
    2: "Mira",
    3: "Rumi",
    4: "Elige tu guerrera",
    5: "Elige tu guerrera",
}

# --- OBJETIVO DE DEMONIOS A ELIMINAR POR NIVEL ---
OBJETIVO_DEMONIOS_POR_NIVEL = {
    1: 5,
    2: 7,
    3: 10,
    4: 15,
    5: 20,
}

# --- VIDA Y COMBATE ---
VIDA_MAXIMA_POR_VIDA = 100
DAÑO_GOLPE_DEMONIO = 34       # ~3 golpes agotan una vida (100 / 34 ≈ 2.9)
CURACION_CORAZON = 50         # cuánto recarga un corazón la barra de vida actual
VIDAS_INICIALES = 3
VIDAS_MAXIMAS = 5

# --- PUNTAJE ---
PUNTOS_GOLPE = 10
PUNTOS_PATADA = 15
PUNTOS_DAGA = 15
PUNTOS_ESPADA = 25
PUNTOS_DEMONIO_ELIMINADO = 50

# --- OBJETOS RECOLECTABLES ---
TAMANO_OBJETO = (20, 20)
INTERVALO_MIN_OBJETO = 240
INTERVALO_MAX_OBJETO = 420
MAX_OBJETOS_EN_PANTALLA = 2

# --- MINIATURAS DE PREVISUALIZACIÓN DEL MENÚ DE NIVELES ---
TAMANO_PREVIEW = (280, 175)  # misma proporción 800x500 (1.6) que la pantalla

# --- SUELO ---
SUELO_Y = 300
LINEA_SUELO_Y = 430

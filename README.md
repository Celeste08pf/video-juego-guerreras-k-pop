# Las Guerreras K-Pop

## Cómo correrlo

1. Copiá tu carpeta `multimedia/` (con todos los sprites, fondos y música)
   dentro de esta carpeta del proyecto, reemplazando la carpeta `multimedia/`
   vacía que ya viene incluida.
2. Instalá pygame si no lo tenés: `pip install pygame`
3. Ejecutá: `python main.py` (desde esta carpeta, **no** desde adentro de
   ningún subpaquete).

## Estructura de carpetas

```
guerreras_kpop/
├── main.py                  Punto de entrada
├── config/
│   └── constantes.py        Colores, tamaños, tablas de configuración por nivel
├── core/
│   ├── utils.py             Fuentes, texto con contorno, carga de assets
│   └── juego.py             Clase Juego: todo el estado + el bucle principal
├── entidades/
│   ├── entidad_base.py      EntidadAnimada (clase base común, animación por estados)
│   ├── personaje.py         Personaje(EntidadAnimada)  -> Zoey y Rumi
│   ├── mira.py              Mira(Personaje)            -> Nivel 2
│   ├── demonio.py           Demonio(EntidadAnimada)    -> niveles 1-3
│   ├── demonio2.py          Demonio2(Demonio)          -> niveles 4-5
│   ├── daga.py              Daga (proyectil de Zoey)
│   └── objeto.py            Objeto (monedas y corazones recolectables)
├── ui/
│   ├── hud.py                Clase HUD (interfaz superior, barras de vida)
│   └── menus.py              MenuNiveles, MenuSeleccionPersonaje
└── multimedia/                Assets del juego (poné acá tus imágenes/audio)
```

## Cómo se aplica la POO

**Herencia:**
- `EntidadAnimada` es la clase base de la que heredan **todas** las
  entidades con animación por estados: tanto `Personaje` como `Demonio`.
  Ahí vive, una sola vez, la lógica de "tengo varios estados, cada estado
  tiene una lista de frames, avanzo de frame cada cierto tiempo".
- `Mira(Personaje)` hereda todo el comportamiento de una guerrera jugable
  y sólo redefine `cargar_imagenes()`, porque su ataque especial tiene 4
  frames en vez de 3. El resto del juego (colisiones, HUD, bucle
  principal) trata a una instancia de `Mira` exactamente igual que a
  cualquier otro `Personaje`: eso es **polimorfismo**.
- `Demonio2(Demonio)` hereda vida, daño y la estructura general de la IA
  de `Demonio`, y sólo agrega lo propio de los niveles 4 y 5 (esquive
  saltando, ataque especial con espada).

**Encapsulamiento:**
- Los atributos internos de cada clase (vida, estado de animación,
  velocidad, banderas de la IA, etc.) llevan guion bajo (`_vida`,
  `_estado_actual`, `_esquivando`...) y sólo se leen o modifican desde
  afuera a través de `@property` o de métodos pensados para eso
  (`recibir_golpe()`, `curar()`, `cambiar_estado()`), nunca tocando el
  atributo directamente. Por ejemplo, nadie fuera de `Personaje` puede
  poner la vida en un valor inválido: sólo puede pedirle
  `jugador.recibir_golpe(daño)` y la clase decide qué hacer.
- La clase `Juego` (en `core/juego.py`) encapsula **todo** el estado que
  en la versión anterior vivía en variables globales sueltas (nivel
  actual, puntaje, sprites, niveles desbloqueados, etc.) como atributos
  privados de un único objeto, con métodos privados para cada
  responsabilidad (`_resolver_ataque_del_demonio`,
  `_resolver_recoleccion_de_objetos`, etc.) en vez de un único bloque de
  código gigante.

**Nota sobre el modo de prueba:** `MODO_PRUEBA_DESBLOQUEAR_TODO` en
`config/constantes.py` sigue en `True` (arranca con los 5 niveles
desbloqueados). Ponelo en `False` antes de entregar el proyecto.

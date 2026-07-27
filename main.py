"""
main.py
=======
Punto de entrada del proyecto. Toda la lógica del juego vive organizada en
paquetes (config, core, entidades, ui); este archivo sólo crea el objeto
Juego y le pide que se ejecute.

Estructura del proyecto:
    guerreras_kpop/
    ├── main.py                  <- este archivo
    ├── config/
    │   └── constantes.py        colores, tamaños, tablas de configuración
    ├── core/
    │   ├── utils.py             fuentes, texto con contorno, carga de assets
    │   └── juego.py             clase Juego: estado + bucle principal
    ├── entidades/
    │   ├── entidad_base.py      EntidadAnimada (clase base común)
    │   ├── personaje.py         Personaje(EntidadAnimada)  -> Zoey y Rumi
    │   ├── mira.py               Mira(Personaje)            -> Nivel 2
    │   ├── demonio.py           Demonio(EntidadAnimada)     -> niveles 1-3
    │   ├── demonio2.py          Demonio2(Demonio)           -> niveles 4-5
    │   ├── daga.py               Daga (proyectil de Zoey)
    │   └── objeto.py            Objeto (monedas y corazones)
    ├── ui/
    │   ├── hud.py                clase HUD
    │   └── menus.py              MenuNiveles, MenuSeleccionPersonaje
    └── multimedia/               (assets: imágenes y música del juego)
"""
from core.juego import Juego


def main():
    juego = Juego()
    juego.ejecutar()


if __name__ == "__main__":
    main()

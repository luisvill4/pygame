"""
Enemigos. Cada archivo define un tipo y se anota solo en TIPOS_ENEMIGO.
Para agregar uno nuevo, ver las instrucciones en enemigos/base.py.
"""
from juego.enemigos.base import Enemigo, TIPOS_ENEMIGO, registrar_enemigo, crear_enemigo, crear_enemigos

# Importarlos es lo que los anota en el registro
from juego.enemigos import perseguidor, rebotador, embestidor, divisor, enjambre  # noqa: F401

__all__ = ["Enemigo", "TIPOS_ENEMIGO", "registrar_enemigo", "crear_enemigo", "crear_enemigos"]

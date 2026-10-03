"""
Power-ups. Se anotan solos en TIPOS_POWERUP.
Para agregar uno nuevo, ver las instrucciones en powerups/base.py.
"""
from juego.powerups.base import (PowerUp, Capsula, TIPOS_POWERUP, HASTA_PERDER_VIDA,
                                 registrar_powerup)

# Importarlos es lo que los anota en el registro
from juego.powerups import tipos  # noqa: F401

__all__ = ["PowerUp", "Capsula", "TIPOS_POWERUP", "HASTA_PERDER_VIDA", "registrar_powerup"]

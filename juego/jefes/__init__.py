"""
Jefes. Cada archivo define uno y se anota solo en TIPOS_JEFE.
Para agregar uno nuevo, ver las instrucciones en jefes/base.py.
"""
from juego.jefes.base import Jefe, TIPOS_JEFE, registrar_jefe, crear_jefe

# Importarlos es lo que los anota en el registro
from juego.jefes import ojo, fortaleza  # noqa: F401

__all__ = ["Jefe", "TIPOS_JEFE", "registrar_jefe", "crear_jefe"]

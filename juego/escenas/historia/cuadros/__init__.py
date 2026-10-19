"""
Los CUADROS: los dibujos animados de las escenas del modo historia (el prologo y los dialogos).

Cada dibujo es una funcion con @cuadro (base.py) y se arma con las piezas del kit (kit.py). Estan
repartidos por archivo: los del prologo, los comunes (la Umbral, el rescate, el plano...) y uno
por mision. Para usar uno en un dialogo, se lo nombra entre los renglones:

    antes = [
        ("cuadro", "cinturon"),             # desde aqui se ve el Cinturon Exterior
        ("ines", "AHI ESTAN LAS MONEDAS..."),
        ("cuadro", "moneda_blanca", "F01"), # (tambien con condicion, como cualquier renglon)
        ...
    ]

Para sumar uno: la funcion con @cuadro en el archivo de su mision. Los tests revisan solos que
cada cuadro nombrado exista, que calce en la grilla de 2 px y que se dibuje en cualquier momento.
"""
from juego.escenas.historia.cuadros.base import CUADROS, NOCHE, cuadro, dibujar, rotulo, sonido
# Importarlos es lo que los anota en el registro
from juego.escenas.historia.cuadros import (prologo, comunes, mision_1, mision_2, mision_3,  # noqa: F401
                                            mision_4, mision_5, mision_6)

__all__ = ["CUADROS", "NOCHE", "cuadro", "dibujar", "rotulo", "sonido"]

"""
Estadisticas de UNA partida: lo que se muestra en el Game Over y lo que revisan los logros.

La Partida va sumando a medida que pasan las cosas (monedas, dash, enemigos...).
Los rangos de cada sector y las mejoras elegidas tambien quedan anotados aca.
"""


class Estadisticas:
    def __init__(self):
        self.monedas = 0            # monedas recogidas
        self.enemigos = 0           # enemigos destruidos (con el dash, una onda, una nova...)
        self.dashes = 0             # veces que se uso el dash
        self.perfectos = 0          # dash perfectos (atravesar un peligro con el dash)
        self.powerups = 0           # power-ups recogidos
        self.desafios = 0           # desafios cumplidos
        self.anomalias_limpias = 0  # anomalias aguantadas sin recibir un golpe
        self.rangos = []            # una letra por sector cerrado ("S", "A"...)
        self.colores_rangos = []    # el color de cada uno de esos sectores (para dibujarlos)
        self.mejoras = []           # tipos de mejora elegidos, en orden

    def mejor_rango(self):
        # La mejor letra conseguida (None si no se cerro ningun sector)
        for letra in ("S", "A", "B", "C"):
            if letra in self.rangos:
                return letra
        return None

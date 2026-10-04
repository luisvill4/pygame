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
        self.sectores_limpios = 0   # sectores cerrados sin recibir un golpe
        self.rangos = []            # una letra por sector cerrado ("S", "A"...)
        self.mejoras = []           # tipos de mejora elegidos, en orden

"""
Estadisticas de UNA partida: lo que se muestra en el Game Over y lo que revisan los logros.

La Partida va sumando a medida que pasan las cosas (monedas, dash, enemigos...).
Los rangos de cada sector y las mejoras elegidas tambien quedan anotados aca.
"""


class Estadisticas:
    def __init__(self):
        self.monedas = 0            # monedas recogidas
        self.creditos = 0           # creditos ganados (los gastados no se restan)
        self.enemigos = 0           # enemigos destruidos (con el dash, una onda, una nova...)
        self.dashes = 0             # veces que se uso el dash
        self.perfectos = 0          # dash perfectos (romper o interceptar enemigos con el dash)
        self.mejor_cadena = 0       # mas perfectos seguidos (ver CADENA_PERFECTOS)
        self.interceptados = 0      # embestidores frenados con el dash
        self.recuperadas = 0        # monedas recuperadas de un ladron
        self.escuadrones = 0        # escuadrones eliminados enteros
        self.fragmentos = 0         # modo historia: fragmentos del Archivo encontrados en esta partida
        self.powerups = 0           # power-ups recogidos
        self.desafios = 0           # desafios cumplidos
        self.sectores_limpios = 0   # sectores cerrados sin recibir un golpe
        self.rangos = []            # una letra por sector cerrado ("S", "A"...)
        self.mejoras = []           # tipos de mejora elegidos, en orden

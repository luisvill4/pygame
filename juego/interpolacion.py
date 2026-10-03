"""
Interpolacion: movimiento suave por encima de 60 FPS.

La logica avanza a 60 pasos por segundo, pero se puede dibujar mas seguido (90, 120,
144 FPS...). Entre un paso y el siguiente, las cosas se dibujan en un punto intermedio
entre donde estaban en el paso anterior y donde estan ahora:

    dibujado = anterior + (actual - anterior) * fraccion       (fraccion de 0 a 1)

Asi se ve fluido sin cambiar nada de la logica. Se usa asi:

    interpolador.guardar(objetos)                  # al empezar cada paso de logica
    with interpolador.aplicar(objetos, fraccion):  # al dibujar
        ... dibujar normalmente ...

Dentro del 'with' los objetos estan movidos a su posicion intermedia; al salir vuelven
a su posicion real (la logica nunca ve las posiciones intermedias).
Sirve para cualquier objeto con atributos x e y.
"""
from contextlib import contextmanager

SALTO_MAXIMO = 80       # px: si algo se movio mas que esto en un paso, se teletransporto (no se interpola)


class Interpolador:
    def __init__(self):
        self.anteriores = {}        # id del objeto -> (x, y) en el paso anterior

    def guardar(self, objetos):
        self.anteriores = {id(objeto): (objeto.x, objeto.y) for objeto in objetos}

    @contextmanager
    def aplicar(self, objetos, fraccion):
        movidos = []                # (objeto, x real, y real) para devolverlos despues
        if fraccion < 1:
            for objeto in objetos:
                anterior = self.anteriores.get(id(objeto))
                if anterior is None:
                    continue        # recien creado: todavia no tiene posicion anterior
                anterior_x, anterior_y = anterior
                if abs(objeto.x - anterior_x) > SALTO_MAXIMO or abs(objeto.y - anterior_y) > SALTO_MAXIMO:
                    continue        # reaparecio en otro lado: no se dibuja "viajando"
                movidos.append((objeto, objeto.x, objeto.y))
                objeto.x = anterior_x + (objeto.x - anterior_x) * fraccion
                objeto.y = anterior_y + (objeto.y - anterior_y) * fraccion
        try:
            yield
        finally:
            for objeto, x_real, y_real in movidos:
                objeto.x, objeto.y = x_real, y_real

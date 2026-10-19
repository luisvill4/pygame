"""
El registro de los cuadros (patron Registry, como los enemigos y los jefes).

Un CUADRO es un dibujo animado hecho con codigo: una funcion con el decorador @cuadro.

    @cuadro("cinturon", "CINTURON EXTERIOR")
    def cinturon(pantalla, zona, t, paso, datos):
        ...

    zona    el rectangulo del escenario (se dibuja adentro: lo que se pasa no se ve)
    t       pasos desde que aparecio el cuadro (avanza en actualizar: igual a cualquier FPS)
    paso    cuantos renglones (o paginas) van desde que aparecio: el dibujo puede cambiar
            mientras se habla ("SIGUE" se escribe en el segundo renglon)
    datos   lo que manda quien abre la escena: los años de la Umbral, el modulo nuevo,
            quien esta hablando ("quien")...

El rotulo es el nombre del lugar: la escena lo escribe en la esquina, como en el cine. El
sonido (si tiene) suena cuando el cuadro aparece (un sonido que ya existe: el compas...).
Todo se dibuja en la grilla de 2 px (el kit tiene las ayudas: kit.py).
"""
NOCHE = (4, 6, 16)          # el cielo del escenario (un poco mas azul que el fondo de los menus)
CUADROS = {}                # nombre -> (funcion, rotulo, sonido)


def cuadro(nombre, rotulo="", sonido=None):
    # El decorador: anota el dibujo con su nombre (y el lugar y el sonido, si tiene)
    def anotar(funcion):
        if nombre in CUADROS:
            raise ValueError("Ya hay un cuadro " + nombre)
        CUADROS[nombre] = (funcion, rotulo, sonido)
        return funcion
    return anotar


def rotulo(nombre):
    return CUADROS[nombre][1]


def sonido(nombre):
    return CUADROS[nombre][2]


def dibujar(pantalla, nombre, zona, t, paso=0, datos=None):
    # El cielo, el dibujo recortado al escenario y nada mas (el marco lo pone la escena)
    funcion = CUADROS[nombre][0]
    pantalla.fill(NOCHE, zona)
    anterior = pantalla.get_clip()
    pantalla.set_clip(zona)
    funcion(pantalla, zona, t, paso, datos if datos is not None else {})
    pantalla.set_clip(anterior)

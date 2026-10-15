"""
Los glifos de los Cantores: su escritura hecha de ritmos (ver HISTORIA.md, seccion 7).

Cada letra es una serie de pulsos cortos (".") y largos ("-"), con un espacio entre letras.
Es Morse, pero en el juego nadie lo llama asi: el jugador lo descubre al encontrar la clave
del compas (el fragmento CLAVE_DE_LOS_GLIFOS). Con la clave, el Archivo traduce los glifos.
"""
from juego import dibujo

CLAVE_DE_LOS_GLIFOS = "F06"         # el fragmento que ensena a leerlos (mision 3)

RITMOS = {
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E", "..-.": "F", "--.": "G", "....": "H",
    "..": "I", ".---": "J", "-.-": "K", ".-..": "L", "--": "M", "-.": "N", "---": "O", ".--.": "P",
    "--.-": "Q", ".-.": "R", "...": "S", "-": "T", "..-": "U", "...-": "V", ".--": "W", "-..-": "X",
    "-.--": "Y", "--..": "Z",
}


def traducir(glifo):
    # ".- .-.. -... .-" -> "ALBA" (lo que no se entiende queda como "?")
    return "".join(RITMOS.get(letra, "?") for letra in glifo.split(" "))


def dibujar_glifo(pantalla, glifo, izquierda, centro_y, color):
    # Cada pulso corto es un rombito y cada largo una raya, en la grilla de 2 px; entre
    # letras, mas aire. Devuelve el ancho dibujado
    x = dibujo.en_grilla(izquierda)
    arriba = dibujo.en_grilla(centro_y) - 4
    for letra in glifo.split(" "):
        for pulso in letra:
            if pulso == ".":
                pantalla.fill(color, (x + 2, arriba, 4, 8))
                pantalla.fill(color, (x, arriba + 2, 8, 4))
                x += 12
            else:
                pantalla.fill(color, (x, arriba + 2, 20, 4))
                x += 24
        x += 14
    return x - izquierda

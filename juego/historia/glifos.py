"""
Los glifos de El Ultimo (al que Ines llama "los Cantores"): su escritura hecha de ritmos (HISTORIA.md, seccion 8).

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


LETRAS = {letra: ritmo for ritmo, letra in RITMOS.items()}

# El compas en el tiempo: un pulso corto dura 1 unidad, uno largo 3; entre pulsos 1 unidad
# de silencio, entre letras 3 y al final de la palabra 7 (antes de que vuelva a empezar)
CORTO, LARGO, ENTRE_PULSOS, ENTRE_LETRAS, FIN_DE_PALABRA = 1, 3, 1, 3, 7


def traducir(glifo):
    # ".- .-.. -... .-" -> "ALBA" (lo que no se entiende queda como "?")
    return "".join(RITMOS.get(letra, "?") for letra in glifo.split(" "))


def escribir(palabra):
    # "ALBA" -> ".- .-.. -... .-" (para escribir los glifos de los fragmentos sin errores)
    return " ".join(LETRAS[letra] for letra in palabra)


def ritmo(glifo, unidad):
    # Cuando suena cada pulso: ([(inicio, largo, es_largo), ...], cuanto dura la vuelta), en ms.
    # Lo usan todos los que "tocan" el compas: la baliza, los pulsos de la niebla y el mapa
    pulsos = []
    tiempo = 0
    letras = glifo.split(" ")
    for i, letra in enumerate(letras):
        for j, pulso in enumerate(letra):
            largo = (LARGO if pulso == "-" else CORTO) * unidad
            pulsos.append((tiempo, largo, pulso == "-"))
            tiempo += largo + (ENTRE_PULSOS * unidad if j < len(letra) - 1 else 0)
        tiempo += (ENTRE_LETRAS if i < len(letras) - 1 else FIN_DE_PALABRA) * unidad
    return pulsos, tiempo


def sonando(glifo, unidad, momento):
    # ¿En este momento (ms, da la vuelta) hay un pulso encendido? (para lo que titila a ritmo)
    pulsos, vuelta = ritmo(glifo, unidad)
    momento %= vuelta
    return any(inicio <= momento < inicio + largo for inicio, largo, _ in pulsos)


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


def ancho_glifo(glifo):
    # Lo que ocupa un glifo dibujado (la misma cuenta que dibujar_glifo): para centrarlo
    pulsos, _ = ritmo(glifo, 1)
    letras = glifo.split(" ")
    cortos = sum(1 for _, _, es_largo in pulsos if not es_largo)
    largos = len(pulsos) - cortos
    return cortos * 12 + largos * 24 + len(letras) * 14 - 14

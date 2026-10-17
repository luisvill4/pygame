"""
El RELOJ DE LA UMBRAL: la relatividad del tiempo en la historia.

Para Alba un viaje dura horas; en la Estacion Umbral pasan años (viaja casi a la velocidad de
la luz y, cerca del Abismo, la gravedad estira su tiempo todavia mas: galaxia.py). Lo que
cuenta es el tiempo de la Umbral: progreso.anios. La Marea llega en MAREA_ANIOS.

    - Cada año que pasa, Ines manda un mensaje (MENSAJES): ella envejece, Alba no.
    - El frente de la Marea avanza por el mapa de la galaxia (se ve) y a los MAREA_ANIOS se
      traga la Umbral: desde ahi es TARDE. La historia sigue, pero cambia (los renglones con
      "T6": ver mision.filtrar) y el final tambien.
    - Con la mision final cumplida el reloj se detiene: la historia termino (se puede seguir
      explorando).
Solo reglas chicas sobre el progreso guardado: las usan la galaxia, los pasajes y los tests.
"""
from juego.config import MAREA_ANIOS, MAREA_FRENTE_INICIO, MAREA_FRENTE_POR_ANIO
from juego.historia.mision import misiones_en_orden

# Los años en que la historia cambia (los renglones con "T3", "T6": mision.filtrar). Si un viaje
# cruza uno, la galaxia avisa antes de salir (un test vigila que esten todos los que se usan)
HITOS = [(3, "INES VA A PEDIRTE QUE TE DES PRISA."),
         (MAREA_ANIOS, "LA UMBRAL CAE. LA HISTORIA CAMBIA.")]

MENSAJES = [        # (años, lo que dice Ines cuando pasan)
    (1, [("ines", "ALBA, PARA TI FUERON UNAS HORAS. AQUI PASO UN AÑO ENTERO."),
         ("ines", "LA MAREA YA SE VE DE NOCHE, COMO UNA MANCHA ROJA. LA GENTE SALE A MIRARLA.")]),
    (2, [("ines", "DOS AÑOS. EVACUARON LOS PLANETAS DE AFUERA. NO HAY A DONDE IR, PERO LA GENTE SE MUEVE DE TODOS MODOS.")]),
    (3, [("ines", "TRES AÑOS. ME SALIERON CANAS. TU SIGUES IGUAL QUE EL DIA QUE TE FUISTE."),
         ("ines", "NO TE LO DIGO PARA QUE TE DES PRISA. BUENO... UN POCO SI.")]),
    (4, [("ines", "CUATRO AÑOS. LA MAREA YA TAPA MEDIO CIELO. LAS ORBITAS EMPIEZAN A TEMBLAR.")]),
    (5, [("ines", "CINCO AÑOS. LA UMBRAL ES LO UNICO QUE QUEDA EN PIE DE ESTE LADO. ME QUEDO HASTA QUE VUELVAS.")]),
    (6, [("ines", "LA MAREA LLEGO. LA UMBRAL NO AGUANTA. SUBIMOS A LOS QUE PUDIMOS A LAS NAVES."),
         ("ines", "VAMOS HACIA EL ABISMO, DETRAS DE TI. ALBA... TERMINA LO QUE EMPEZASTE.")]),
]


def historia_terminada(progreso):
    return any(clase.final and clase.numero in progreso.misiones for clase in misiones_en_orden())


def pasar(progreso, anios):
    # El tiempo de la Umbral avanza (si la historia no termino)
    if not historia_terminada(progreso):
        progreso.anios += anios


def restante(progreso):
    return max(0.0, MAREA_ANIOS - progreso.anios)


def tarde(progreso):
    return progreso.anios >= MAREA_ANIOS


def mensajes_pendientes(progreso):
    # Los mensajes de Ines de los años que ya pasaron y todavia no se vieron
    return [(anio, renglones) for anio, renglones in MENSAJES
            if anio <= progreso.anios and anio not in progreso.mensajes]


def hitos_que_cruza(progreso, anios_de_viaje):
    # Lo que cambia en la historia si pasan esos años (nada si la historia ya termino)
    if historia_terminada(progreso):
        return []
    llegada = progreso.anios + anios_de_viaje
    return [texto for anio, texto in HITOS if progreso.anios < anio <= llegada]


def frente_de_la_marea(anios):
    # Hasta donde llega la Marea en el mapa de la galaxia (x)
    return MAREA_FRENTE_INICIO + anios * MAREA_FRENTE_POR_ANIO


def tragado(uno, anios):
    # ¿La Marea ya cubrio este sistema? (no se puede ir)
    return uno.lugar[0] < frente_de_la_marea(anios)

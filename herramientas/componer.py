"""
Compone la musica y los efectos del juego con el estudio (herramientas/estudio/).

Uso (desde la carpeta del juego):
    python herramientas/componer.py                         todo
    python herramientas/componer.py musica_juego moneda_1   solo esos
    python herramientas/componer.py moneda --escuchar       los que empiezan con "moneda", y suenan
    python herramientas/componer.py --efectos               todos los efectos (sin los temas, que tardan)
    python herramientas/componer.py --lista                 que se puede componer
    python herramientas/componer.py --fichas                rehace efectos/fichas.json (sin componer)

Cada archivo que compone anota su "ficha" en efectos/fichas.json: cuanto suena (la envolvente
de un efecto, el nivel de un tema). El mezclador del juego la usa para que la suma de todo lo
que suena no se pase del maximo (ver juego/sonido.py).

Todo se guarda en OGG Vorbis, en la carpeta de su familia: efectos/musica/, ambiente/, interfaz/,
juego/, enemigos/, director/ y jefes/ (la del modulo donde se compone: obras/__init__.py). Un
efecto armonico va en su propia carpeta con un archivo por color (juego/moneda_1/moneda_1_fa.ogg).
El juego busca cada archivo por su nombre en cualquier subcarpeta (juego/sonido.py). Por cada
uno muestra cuanto dura y como quedo: volumen percibido (LUFS), pico, brillo (el
"centroide": arriba de ~2500 Hz empieza a sonar chillon) y que tan abierto es el estereo.
Necesita numpy, numba (para que sea rapido) y soundfile (para el OGG): ver requirements.txt.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np  # noqa: E402

from herramientas.estudio import procesos  # noqa: E402
from herramientas.estudio.base import FS  # noqa: E402
from herramientas.estudio.obras import cargar_todas, ARMONICOS, ruta_relativa  # noqa: E402
from herramientas.estudio import armonia  # noqa: E402

CARPETA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "efectos")


def guardar(nombre, audio, color=None, carpeta=CARPETA):
    # En OGG Vorbis (un WAV pesa 6 veces mas y no se oye la diferencia), en la carpeta de su
    # familia. Devuelve la ruta del archivo
    import soundfile
    archivo = os.path.join(carpeta, ruta_relativa(nombre, color))
    os.makedirs(os.path.dirname(archivo), exist_ok=True)
    datos = np.ascontiguousarray(audio.T)
    # De a bloques: el codificador de Vorbis se queda sin pila (y se cae sin avisar en Windows)
    # si recibe un tema entero de una vez
    # compression_level: 0 = la mejor calidad, 1 = el archivo mas chico (0.4: alta calidad)
    with soundfile.SoundFile(archivo, "w", FS, 2, format="OGG", subtype="VORBIS",
                             compression_level=0.4) as salida:
        for desde in range(0, len(datos), 32768):
            salida.write(datos[desde:desde + 32768])
    return archivo


def archivos_de_sonido(carpeta=CARPETA):
    # {nombre del archivo: ruta}: todos los OGG de efectos/ y sus subcarpetas
    encontrados = {}
    for raiz, _, archivos in os.walk(carpeta):
        for archivo in archivos:
            if archivo.endswith(".ogg"):
                encontrados[archivo] = os.path.join(raiz, archivo)
    return encontrados


ARCHIVO_FICHAS = os.path.join(CARPETA, "fichas.json")
BLOQUE_FICHA = 0.05         # s: la envolvente de un efecto se anota cada 50 ms (la lee juego/sonido.py)


def ficha(audio, es_tema):
    # Lo que el mezclador del juego necesita saber de un archivo sin abrirlo: cuanto suena.
    # Efectos: el pico de cada bloque de 50 ms (la "envolvente"). Temas: su nivel tipico (el
    # percentil 95 de los picos de sus bloques: un golpe suelto no cuenta)
    bloque = int(BLOQUE_FICHA * FS)
    cuantos = max(1, -(-audio.shape[1] // bloque))
    relleno = np.zeros((audio.shape[0], cuantos * bloque))
    relleno[:, :audio.shape[1]] = audio
    picos = np.max(np.abs(relleno).reshape(audio.shape[0], cuantos, bloque), axis=(0, 2))
    if es_tema:
        return {"nivel": round(float(np.percentile(picos, 95)), 3)}
    return {"envolvente": [round(float(pico), 3) for pico in picos]}


def leer_fichas():
    import json
    try:
        with open(ARCHIVO_FICHAS, encoding="utf-8") as archivo:
            return json.load(archivo)
    except (OSError, ValueError):
        return {}


def escribir_fichas(fichas):
    import json
    with open(ARCHIVO_FICHAS, "w", encoding="utf-8") as archivo:
        json.dump(dict(sorted(fichas.items())), archivo, separators=(",", ":"))


def rehacer_fichas(carpeta=CARPETA):
    # Las fichas de TODOS los archivos de efectos/ (lee cada uno; ~10 s). Conserva lo que no
    # sale del archivo (la armonia de los temas, que la anota quien compone el tema)
    import soundfile
    viejas = leer_fichas()
    fichas = {}
    for archivo, lugar in sorted(archivos_de_sonido(carpeta).items()):
        audio, _ = soundfile.read(lugar, always_2d=True)
        nueva = dict(viejas.get(archivo, {}))
        # Los temas (dan la vuelta): la musica, los ambientes y el laser. Los OGG de los
        # colores de un efecto armonico son efectos
        es_tema = archivo.startswith(("musica_", "amb_")) or archivo == "laser.ogg"
        nueva.update(ficha(audio.T, es_tema))
        if "acordes" in nueva:
            nueva["colores"] = [armonia.color_de_acorde(acorde) for acorde in nueva["acordes"]]
        fichas[archivo] = nueva
    escribir_fichas(fichas)
    return fichas


def informe(audio, es_tema):
    volumen = procesos.loudness(audio) if es_tema else procesos.loudness_maximo(audio)
    return "%5.2f s  %6.1f LUFS  pico %5.1f dB  brillo %5d Hz  estereo %.2f" % (
        audio.shape[1] / FS, volumen, procesos.a_db_pico(audio), procesos.centroide(audio),
        procesos.correlacion(audio))


def escuchar(audio):
    import pygame
    if not pygame.mixer.get_init():
        pygame.mixer.init(FS, -16, 2, 512)
    datos = (np.clip(audio.T, -1, 1) * 32767).astype(np.int16)
    sonido = pygame.sndarray.make_sound(np.ascontiguousarray(datos))
    sonido.play()
    pygame.time.wait(int(sonido.get_length() * 1000) + 200)


def pedidos(argumentos, obras):
    # Nombres exactos o prefijos ("moneda" -> moneda_1 ... moneda_5); sin nada, todo
    if not argumentos:
        return list(obras)
    elegidos = []
    for pedido in argumentos:
        coinciden = [nombre for nombre in obras if nombre == pedido or nombre.startswith(pedido)]
        if not coinciden:
            sys.exit("No existe '%s'. Usar --lista para ver que se puede componer." % pedido)
        elegidos += [nombre for nombre in coinciden if nombre not in elegidos]
    return elegidos


def main():
    obras = cargar_todas()
    argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--lista" in sys.argv:
        print("\n".join(sorted(obras)))
        return
    elegidos = pedidos(argumentos, obras)
    if "--fichas" in sys.argv:
        print("%d fichas en %s" % (len(rehacer_fichas()), os.path.basename(ARCHIVO_FICHAS)))
        return
    if "--efectos" in sys.argv:
        elegidos = [nombre for nombre in obras if not nombre.startswith("musica")]
    fichas = leer_fichas()
    for nombre in elegidos:
        # Un efecto armonico se compone una vez por color (moneda_1_do.ogg, moneda_1_fa.ogg...)
        colores = list(armonia.COLORES) if nombre in ARMONICOS else [None]
        for color in colores:
            inicio = time.time()
            with armonia.en_color(color):
                obra = obras[nombre]()
                audio = obra.mezclar()
            archivo = guardar(nombre, audio, color)
            fichas[os.path.basename(archivo)] = ficha(audio, obra.vuelta)
            if obra.vuelta and obra.acordes:
                # La armonia del tema: el color de cada compas (lo usa el juego para elegir el
                # archivo de un efecto armonico) y cuanto dura un compas
                fichas[os.path.basename(archivo)].update(
                    {"acordes": obra.acordes, "colores": [armonia.color_de_acorde(a) for a in obra.acordes],
                     "compas_ms": round(obra.segundo(16) * 1000, 3)})
            print("%-24s %s  (%.1f s)  -> %s" % (nombre, informe(audio, obra.vuelta), time.time() - inicio,
                                                os.path.relpath(archivo, CARPETA)))
            if "--escuchar" in sys.argv:
                escuchar(audio)
    escribir_fichas(fichas)


if __name__ == "__main__":
    main()

"""
Lo que se guarda en disco: la tabla de records, las opciones y el progreso (logros y nave).

Nunca hacen caer el juego:
- si el archivo no existe, se crea con los valores de fabrica;
- si esta dañado, se usan los valores de fabrica (y se sobrescribe al guardar);
- si no se puede escribir (carpeta de solo lectura...), se sigue jugando sin guardar.
"""
import json

from juego.config import (VOLUMEN_MAX, FILAS_RECORDS, FRECUENCIAS, ORDEN_DIFICULTADES, NAVES, ORDEN_VIBRACION,
                          ORDEN_TEMBLOR, ORDEN_DESTELLOS, ORDEN_CRT, ORDEN_NEON, ORDEN_ESCALADO)


def _escribir_json(archivo, datos):
    try:
        with open(archivo, "w", encoding="utf-8") as abierto:
            json.dump(datos, abierto, indent=2)
    except OSError:
        pass    # no se pudo guardar: el juego sigue igual


def _volumen(valor):
    # Un volumen guardado, entre 0 y VOLUMEN_MAX (lanza error si no es un numero)
    return min(max(int(valor), 0), VOLUMEN_MAX)


def _limpiar_tabla(datos):
    # Lista de {"nombre": "ABC", "puntos": 123}, de mayor a menor (lanza error si esta dañada)
    tabla = [{"nombre": str(fila["nombre"])[:3], "puntos": int(fila["puntos"])} for fila in datos]
    tabla.sort(key=lambda fila: fila["puntos"], reverse=True)
    return tabla[:FILAS_RECORDS]


class TablaRecords:
    # Los mejores puntajes, una tabla por dificultad. En el archivo:
    #   {"FACIL": [...], "NORMAL": [...], "DIFICIL": [...], "PESADILLA": [...]}
    # Un records.json viejo (una sola lista) pasa a ser la tabla de NORMAL

    def __init__(self, archivo):
        self.archivo = archivo
        self.tablas = {dificultad: [] for dificultad in ORDEN_DIFICULTADES}
        self._cargar()

    def _cargar(self):
        try:
            with open(self.archivo, encoding="utf-8") as abierto:
                datos = json.load(abierto)
        except FileNotFoundError:
            self._guardar()
            return
        except ValueError:
            return      # archivo dañado: se sobrescribe al guardar el proximo record
        if isinstance(datos, list):
            datos = {"NORMAL": datos}       # formato viejo
        if not isinstance(datos, dict):
            return
        for dificultad in ORDEN_DIFICULTADES:
            try:
                self.tablas[dificultad] = _limpiar_tabla(datos.get(dificultad, []))
            except (KeyError, TypeError, ValueError):
                pass    # esa tabla esta dañada: queda vacia

    def _guardar(self):
        _escribir_json(self.archivo, self.tablas)

    def filas(self, dificultad):
        return self.tablas[dificultad]

    def maximo(self, dificultad):
        filas = self.tablas[dificultad]
        return filas[0]["puntos"] if filas else 0

    def entra(self, puntos, dificultad):
        # ¿Este puntaje entra en la tabla de esa dificultad?
        filas = self.tablas[dificultad]
        return puntos > 0 and (len(filas) < FILAS_RECORDS or puntos > filas[-1]["puntos"])

    def agregar(self, nombre, puntos, dificultad):
        # Agrega el puntaje, deja los mejores, guarda y devuelve su posicion (-1 si no quedo)
        filas = self.tablas[dificultad]
        nueva = {"nombre": nombre, "puntos": puntos}
        filas.append(nueva)
        filas.sort(key=lambda fila: fila["puntos"], reverse=True)
        del filas[FILAS_RECORDS:]
        self._guardar()
        for posicion, fila in enumerate(filas):
            if fila is nueva:
                return posicion
        return -1


class Progreso:
    # Lo que se gana jugando y queda entre partidas. En el archivo:
    #   {"logros": ["primer_jefe", ...], "nave": "CIAN", "partidas": 12,
    #    "misiones": [1, 2], "fragmentos": ["F01", ...], "fichas": ["enemigo:perseguidor", ...]}
    #   (las tres ultimas: el modo historia)

    def __init__(self, archivo):
        self.archivo = archivo
        self.logros = set()             # ids de los logros desbloqueados (ver logros.py)
        self.nave = NAVES[0][0]         # nombre de la nave elegida
        self.partidas = 0               # partidas terminadas
        self.misiones = set()           # modo historia: las misiones cumplidas (1 a 5)
        self.fragmentos = set()         # modo historia: los fragmentos del Archivo encontrados
        self.fichas = set()             # modo historia: las fichas del Archivo (lo que ya viste)
        self._cargar()

    def _cargar(self):
        try:
            with open(self.archivo, encoding="utf-8") as abierto:
                datos = json.load(abierto)
            self.logros = {str(logro) for logro in datos.get("logros", [])}
            self.partidas = max(0, int(datos.get("partidas", 0)))
            self.misiones = {int(numero) for numero in datos.get("misiones", [])}
            self.fragmentos = {str(fragmento) for fragmento in datos.get("fragmentos", [])}
            self.fichas = {str(ficha) for ficha in datos.get("fichas", [])}
            if datos.get("nave") in [nombre for nombre, _, _ in self.naves_disponibles()]:
                self.nave = datos["nave"]
        except FileNotFoundError:
            self.guardar()
        except (ValueError, TypeError, AttributeError):
            pass        # dañado: se empieza de cero (y se sobrescribe al guardar)

    def guardar(self):
        _escribir_json(self.archivo, {"logros": sorted(self.logros), "nave": self.nave,
                                      "partidas": self.partidas, "misiones": sorted(self.misiones),
                                      "fragmentos": sorted(self.fragmentos), "fichas": sorted(self.fichas)})

    def cumplir_mision(self, numero):
        self.misiones.add(numero)
        self.guardar()

    def encontrar_fragmento(self, id_fragmento):
        # Devuelve True si es nuevo (lo encontrado, encontrado queda: aunque despues pierdas)
        if id_fragmento in self.fragmentos:
            return False
        self.fragmentos.add(id_fragmento)
        self.guardar()
        return True

    def anotar_ficha(self, id_ficha):
        # Devuelve True si es nueva
        if id_ficha in self.fichas:
            return False
        self.fichas.add(id_ficha)
        self.guardar()
        return True

    def desbloquear(self, id_logro):
        self.logros.add(id_logro)
        self.guardar()

    def naves_disponibles(self):
        # Las naves (nombre, color, logro) que ya se pueden usar
        return [nave for nave in NAVES if nave[2] is None or nave[2] in self.logros]

    def color_nave(self):
        for nombre, color, _ in NAVES:
            if nombre == self.nave:
                return color
        return None


class Opciones:
    # Opciones elegidas en el menu. La resolucion es su nombre ("1280x720"); si ya no existe
    # o no entra en el monitor, la App la cambia por una que si

    def __init__(self, archivo):
        self.archivo = archivo
        # Valores de fabrica
        self.resolucion = None      # None = la primera de la lista
        self.fps = 60               # cuadros por segundo al dibujar (0 = sin limite)
        self.volumen = VOLUMEN_MAX              # el general (multiplica a los otros dos)
        self.volumen_musica = VOLUMEN_MAX
        self.volumen_efectos = VOLUMEN_MAX      # efectos, interfaz y ambiente
        self.silencio = False       # la tecla M: todo callado sin tocar los volumenes
        self.audio_mono = False     # todo igual por los dos lados (sin paneo: para un solo oido)
        self.latido = True          # un latido suave cuando queda una sola vida
        self.aviso_jefe = True      # el jefe muestra hacia donde van a salir sus balas
        self.vibracion = "NORMAL"   # intensidad de la vibracion del mando (ORDEN_VIBRACION)
        self.crt = "NORMAL"         # lineas de pantalla vieja (ORDEN_CRT)
        self.neon = "NORMAL"        # brillo de balas, moneda y explosiones (ORDEN_NEON)
        self.escalado = "NITIDO"    # como se agranda a la ventana (ORDEN_ESCALADO)
        self.temblor = "NORMAL"     # cuanto tiembla la pantalla en los golpes (ORDEN_TEMBLOR)
        self.destellos = "NORMALES"  # "REDUCIDOS": sin destellos ni parpadeos rapidos (ORDEN_DESTELLOS)
        self.dificultad = "NORMAL"   # la ultima elegida (el selector arranca en esa)
        self.cargar()

    def cargar(self):
        # Si falta una clave usa el valor de fabrica; si el archivo esta dañado, usa todos los de fabrica
        try:
            with open(self.archivo, encoding="utf-8") as abierto:
                datos = json.load(abierto)
            if isinstance(datos.get("resolucion"), str):
                self.resolucion = datos["resolucion"]
            if type(datos.get("fps")) is int and datos["fps"] in FRECUENCIAS:
                self.fps = datos["fps"]
            self.volumen = _volumen(datos.get("volumen", VOLUMEN_MAX))
            # Un config.json viejo tenia "musica" y "efectos" en SI/NO: NO pasa a volumen 0
            musica_vieja = VOLUMEN_MAX if datos.get("musica", True) else 0
            efectos_viejos = VOLUMEN_MAX if datos.get("efectos", True) else 0
            self.volumen_musica = _volumen(datos.get("volumen_musica", musica_vieja))
            self.volumen_efectos = _volumen(datos.get("volumen_efectos", efectos_viejos))
            self.silencio = bool(datos.get("silencio", False))
            self.audio_mono = bool(datos.get("audio_mono", False))
            self.latido = bool(datos.get("latido", True))
            self.aviso_jefe = bool(datos.get("aviso_jefe", True))
            if datos.get("vibracion") in ORDEN_VIBRACION:
                self.vibracion = datos["vibracion"]
            if datos.get("crt") in ORDEN_CRT:
                self.crt = datos["crt"]
            if datos.get("neon") in ORDEN_NEON:
                self.neon = datos["neon"]
            if datos.get("escalado") in ORDEN_ESCALADO:
                self.escalado = datos["escalado"]
            if datos.get("temblor") in ORDEN_TEMBLOR:
                self.temblor = datos["temblor"]
            if datos.get("destellos") in ORDEN_DESTELLOS:
                self.destellos = datos["destellos"]
            if datos.get("dificultad") in ORDEN_DIFICULTADES:
                self.dificultad = datos["dificultad"]
        except FileNotFoundError:
            self.guardar()
        except (ValueError, TypeError, AttributeError):
            pass

    def guardar(self):
        _escribir_json(self.archivo, {
            "resolucion": self.resolucion,
            "fps": self.fps,
            "volumen": self.volumen,
            "volumen_musica": self.volumen_musica,
            "volumen_efectos": self.volumen_efectos,
            "silencio": self.silencio,
            "audio_mono": self.audio_mono,
            "latido": self.latido,
            "aviso_jefe": self.aviso_jefe,
            "vibracion": self.vibracion,
            "crt": self.crt,
            "neon": self.neon,
            "escalado": self.escalado,
            "temblor": self.temblor,
            "destellos": self.destellos,
            "dificultad": self.dificultad,
        })

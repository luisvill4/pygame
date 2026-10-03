"""
Lo que se guarda en disco: la tabla de records y las opciones.

Nunca hacen caer el juego:
- si el archivo no existe, se crea con los valores de fabrica;
- si esta dañado, se usan los valores de fabrica (y se sobrescribe al guardar);
- si no se puede escribir (carpeta de solo lectura...), se sigue jugando sin guardar.
"""
import json

from juego.config import VOLUMEN_MAX, FILAS_RECORDS, FORMATOS, FRECUENCIAS, ORDEN_DIFICULTADES


def _escribir_json(archivo, datos):
    try:
        with open(archivo, "w", encoding="utf-8") as abierto:
            json.dump(datos, abierto, indent=2)
    except OSError:
        pass    # no se pudo guardar: el juego sigue igual


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


class Opciones:
    # Opciones elegidas en el menu. La resolucion es su nombre ("800x600"); si no sirve
    # para el formato o el monitor, la App la cambia por una que si

    def __init__(self, archivo):
        self.archivo = archivo
        # Valores de fabrica
        self.formato = "4:3"
        self.resolucion = None      # None = la primera del formato
        self.fps = 60               # cuadros por segundo al dibujar (0 = sin limite)
        self.volumen = VOLUMEN_MAX
        self.musica = True
        self.efectos = True
        self.aviso_jefe = True      # el jefe muestra hacia donde van a salir sus balas
        self.dificultad = "NORMAL"   # la ultima elegida (el selector arranca en esa)
        self.cargar()

    def cargar(self):
        # Si falta una clave usa el valor de fabrica; si el archivo esta dañado, usa todos los de fabrica
        try:
            with open(self.archivo, encoding="utf-8") as abierto:
                datos = json.load(abierto)
            if datos.get("formato") in FORMATOS:
                self.formato = datos["formato"]
            if isinstance(datos.get("resolucion"), str):
                self.resolucion = datos["resolucion"]
            if type(datos.get("fps")) is int and datos["fps"] in FRECUENCIAS:
                self.fps = datos["fps"]
            self.volumen = min(max(int(datos.get("volumen", VOLUMEN_MAX)), 0), VOLUMEN_MAX)
            self.musica = bool(datos.get("musica", True))
            self.efectos = bool(datos.get("efectos", True))
            self.aviso_jefe = bool(datos.get("aviso_jefe", True))
            if datos.get("dificultad") in ORDEN_DIFICULTADES:
                self.dificultad = datos["dificultad"]
        except FileNotFoundError:
            self.guardar()
        except (ValueError, TypeError, AttributeError):
            pass

    def guardar(self):
        _escribir_json(self.archivo, {
            "formato": self.formato,
            "resolucion": self.resolucion,
            "fps": self.fps,
            "volumen": self.volumen,
            "musica": self.musica,
            "efectos": self.efectos,
            "aviso_jefe": self.aviso_jefe,
            "dificultad": self.dificultad,
        })

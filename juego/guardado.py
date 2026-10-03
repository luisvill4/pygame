"""
Lo que se guarda en disco: la tabla de records y las opciones.

Nunca hacen caer el juego:
- si el archivo no existe, se crea con los valores de fabrica;
- si esta dañado, se usan los valores de fabrica (y se sobrescribe al guardar);
- si no se puede escribir (carpeta de solo lectura...), se sigue jugando sin guardar.
"""
import json

from juego.config import VOLUMEN_MAX, FILAS_RECORDS


def _escribir_json(archivo, datos):
    try:
        with open(archivo, "w", encoding="utf-8") as abierto:
            json.dump(datos, abierto, indent=2)
    except OSError:
        pass    # no se pudo guardar: el juego sigue igual


class TablaRecords:
    # Los mejores puntajes: lista de {"nombre": "ABC", "puntos": 123}, de mayor a menor

    def __init__(self, archivo):
        self.archivo = archivo
        self.filas = self._cargar()

    def _cargar(self):
        try:
            with open(self.archivo, encoding="utf-8") as abierto:
                datos = json.load(abierto)
            tabla = [{"nombre": str(fila["nombre"])[:3], "puntos": int(fila["puntos"])} for fila in datos]
            tabla.sort(key=lambda fila: fila["puntos"], reverse=True)
            return tabla[:FILAS_RECORDS]
        except FileNotFoundError:
            _escribir_json(self.archivo, [])
            return []
        except (ValueError, KeyError, TypeError):
            return []   # archivo dañado: se sobrescribe al guardar el proximo record

    @property
    def maximo(self):
        return self.filas[0]["puntos"] if self.filas else 0

    def entra(self, puntos):
        # ¿Este puntaje entra en la tabla?
        return puntos > 0 and (len(self.filas) < FILAS_RECORDS or puntos > self.filas[-1]["puntos"])

    def agregar(self, nombre, puntos):
        # Agrega el puntaje, deja los mejores, guarda y devuelve su posicion (-1 si no quedo)
        nueva = {"nombre": nombre, "puntos": puntos}
        self.filas.append(nueva)
        self.filas.sort(key=lambda fila: fila["puntos"], reverse=True)
        del self.filas[FILAS_RECORDS:]
        _escribir_json(self.archivo, self.filas)
        for posicion, fila in enumerate(self.filas):
            if fila is nueva:
                return posicion
        return -1


class Opciones:
    # Opciones elegidas en el menu. La resolucion se guarda por nombre ("800x600") y
    # en memoria es la posicion en la lista de resoluciones disponibles

    def __init__(self, archivo, nombres_resoluciones):
        self.archivo = archivo
        self.nombres_resoluciones = nombres_resoluciones
        # Valores de fabrica
        self.resolucion = 0
        self.volumen = VOLUMEN_MAX
        self.musica = True
        self.efectos = True
        self.aviso_jefe = True      # el jefe muestra hacia donde van a salir sus balas
        self.cargar()

    def cargar(self):
        # Si falta una clave usa el valor de fabrica; si el archivo esta dañado, usa todos los de fabrica
        try:
            with open(self.archivo, encoding="utf-8") as abierto:
                datos = json.load(abierto)
            if datos.get("resolucion") in self.nombres_resoluciones:
                self.resolucion = self.nombres_resoluciones.index(datos["resolucion"])
            self.volumen = min(max(int(datos.get("volumen", VOLUMEN_MAX)), 0), VOLUMEN_MAX)
            self.musica = bool(datos.get("musica", True))
            self.efectos = bool(datos.get("efectos", True))
            self.aviso_jefe = bool(datos.get("aviso_jefe", True))
        except FileNotFoundError:
            self.guardar()
        except (ValueError, TypeError, AttributeError):
            pass

    def guardar(self):
        _escribir_json(self.archivo, {
            "resolucion": self.nombres_resoluciones[self.resolucion],
            "volumen": self.volumen,
            "musica": self.musica,
            "efectos": self.efectos,
            "aviso_jefe": self.aviso_jefe,
        })

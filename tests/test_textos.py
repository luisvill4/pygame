"""Los textos del juego estan en espanol neutro (pedido del usuario: nada de voseo argentino).

Se leen TODOS los textos en mayusculas del paquete juego/ (con tokenize, asi los comentarios no
cuentan) y se buscan las palabras que delatan el voseo. Si una palabra nueva se cuela, sumarla aqui.
"""
import ast
import glob
import re
import tokenize

from juego.config import ruta

PROHIBIDAS = ["VOS", "SOS", "ACA", "TENES", "PODES", "QUERES", "SEGUI", "SEGUIS", "SALI", "SALIS",
              "ELEGI", "CUMPLI", "VENI", "DECI", "DECILE", "DECILO", "ACORDATE", "VOLVE", "VOLVES", "PERDES",
              "RENDIS", "APURATE", "APURES", "CORRETE", "PEGALE", "PARTILO", "DESTRUILOS", "ENCONTRA",
              "TITILA", "PRENDE", "PRENDIDA", "AGARRA", "CHIQUITA", "CHIQUITO", "TIRONEA", "TIRONEAR",
              "NOMAS", "CERQUITA"]


def textos_del_juego():
    for archivo in glob.glob(ruta("juego/**/*.py"), recursive=True):
        with open(archivo, "rb") as codigo:
            for pieza in tokenize.tokenize(codigo.readline):
                if pieza.type != tokenize.STRING:
                    continue
                texto = ast.literal_eval(pieza.string)
                # Solo lo que se ve en pantalla: en mayusculas (las claves y rutas van en minusculas)
                if isinstance(texto, str) and texto.isupper():
                    yield archivo, pieza.start[0], texto


def test_ningun_texto_usa_voseo():
    patron = re.compile(r"\b(" + "|".join(PROHIBIDAS) + r")\b")
    encontrados = ["%s:%d %s" % (archivo, linea, texto) for archivo, linea, texto in textos_del_juego()
                   if patron.search(texto) and texto != "SOS"]      # "SOS" solo: el pedido de auxilio en Morse
    assert not encontrados, "\n".join(encontrados)

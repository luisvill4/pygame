"""Los cuadros (los dibujos animados de la historia) y la Narracion que comparten el prologo y los
dialogos: cada cuadro nombrado existe y se usa, se dibuja en cualquier momento, calza en la grilla
de 2 px y no parpadea rapido; saltear pide confirmacion, se puede volver atras y la velocidad del
texto sale de las opciones."""
import os

import numpy
import pygame
import pytest

from juego import accesibilidad
from juego.config import PIXEL_ARTE, ruta, SALTEAR_CONFIRMA, PARPADEO_MINIMO, MS_POR_FRAME, ESCENA_TITULO
from juego.escenas.historia import cuadros
from juego.escenas.historia.cuadros import kit
from juego.escenas.historia.dialogo import Dialogo, ESCENARIO, CAJA, armar_paginas
from juego.escenas.historia.prologo import Prologo, CUADROS as CUADROS_DEL_PROLOGO, ESCENARIO as ESCENARIO_PROLOGO
from juego.escenas.historia import pasajes
from juego.historia.mision import misiones_en_orden, filtrar, ids_de_fragmentos
from tests.ayudas import avanzar, tecla, saltear

DATOS = {"anios": 2.5, "modulo": "filtro", "nivel": 2, "color": (60, 255, 120), "piezas": 80,
         "encontrados": {"F06"}, "quien": "ines"}


def marcas_de_las_misiones():
    # Todos los ("cuadro", nombre[, condicion]) de los dialogos de antes y despues
    for clase in misiones_en_orden():
        for renglon in clase.antes + clase.despues:
            if renglon[0] == "cuadro":
                yield clase, renglon


def codigo_del_juego():
    # Todo el codigo de juego/ menos los propios cuadros (para ver donde se usa cada uno)
    textos = []
    for carpeta, _, archivos in os.walk(ruta("juego")):
        if "cuadros" in carpeta or "__pycache__" in carpeta:
            continue
        for archivo in archivos:
            if archivo.endswith(".py"):
                with open(os.path.join(carpeta, archivo), encoding="utf-8") as abierto:
                    textos.append(abierto.read())
    return "\n".join(textos)


def test_cada_cuadro_nombrado_existe():
    for clase, renglon in marcas_de_las_misiones():
        assert renglon[1] in cuadros.CUADROS, (clase.titulo, renglon)
        if len(renglon) > 2:        # (las condiciones, con fragmentos que existen)
            for parte in renglon[2].split("+"):
                nombre = parte.lstrip("!")
                assert nombre in ids_de_fragmentos() or nombre[0] == "T", renglon
    for nombre, _ in CUADROS_DEL_PROLOGO:
        assert nombre == "titulo" or nombre in cuadros.CUADROS


def test_cada_cuadro_se_usa_en_algun_lado():
    # Un dibujo que nadie nombra es trabajo perdido (o un nombre mal escrito)
    codigo = codigo_del_juego()
    for nombre in cuadros.CUADROS:
        assert '"%s"' % nombre in codigo, nombre


def test_cada_mision_cuenta_con_cuadros_antes_y_despues():
    # Pedido del usuario: los dialogos se cuentan como el prologo, con animaciones
    for clase in misiones_en_orden():
        for lista in (clase.antes, clase.despues):
            paginas = armar_paginas(filtrar(lista, set(), 0))
            assert paginas and all(pagina["cuadro"] for pagina in paginas), clase.titulo
            con_todo = armar_paginas(filtrar(lista, set(ids_de_fragmentos()), 9))
            assert all(pagina["cuadro"] for pagina in con_todo), clase.titulo


def columnas_que_no_calzan(pantalla, zona):
    # Las x donde cambia el color en una x impar (algo corrido medio pixel de arte)
    pixeles = pygame.surfarray.array2d(pantalla.subsurface(zona))
    cambios = pixeles[1:, :] != pixeles[:-1, :]
    columnas = numpy.nonzero(cambios.any(axis=1))[0] + zona.left + 1
    return [int(x) for x in columnas if x % PIXEL_ARTE]


@pytest.mark.parametrize("nombre", sorted(cuadros.CUADROS))
def test_cada_cuadro_se_dibuja_y_calza_en_la_grilla(app, nombre):
    app.opciones.neon = "NORMAL"
    pantalla = pygame.Surface(app.pantalla.get_size())
    for zona in (ESCENARIO, ESCENARIO_PROLOGO):
        for t in (0, 1, 37, 160, 433, 1500):
            for paso in (0, 3, 6):
                pantalla.fill((0, 0, 0))
                cuadros.dibujar(pantalla, nombre, zona, t, paso, dict(DATOS))
                assert not columnas_que_no_calzan(pantalla, zona), (nombre, zona.size, t, paso)


def test_titila_nunca_va_mas_rapido_que_lo_permitido(app):
    app.opciones.destellos = "REDUCIDOS"
    minimo = PARPADEO_MINIMO / MS_POR_FRAME           # pasos que dura como minimo cada estado
    for periodo in (6, 10, 20, 40):
        estados = [kit.titila(t, periodo) for t in range(200)]
        cambios = [t for t in range(1, 200) if estados[t] != estados[t - 1]]
        assert all(b - a >= minimo - 1 for a, b in zip(cambios, cambios[1:])), periodo


# ---------- El dialogo con cuadros ----------

def dialogo(app, renglones, **opciones):
    escena = Dialogo(app, renglones, lambda: app.terminados.append(True), "MISION 1", "LA SEÑAL", **opciones)
    app.terminados = []
    app.cambiar_escena(escena, transicion=False)
    avanzar(app)
    return escena


def test_los_cuadros_no_son_renglones_y_cambian_el_dibujo(app):
    escena = dialogo(app, [("cuadro", "cinturon"), ("ines", "UNO."), ("alba", "DOS."),
                           ("cuadro", "despegue"), ("alba", "TRES.")])
    assert escena.renglones == [("ines", "UNO."), ("alba", "DOS."), ("alba", "TRES.")]
    assert [p["cuadro"] for p in escena.paginas] == ["cinturon", "cinturon", "despegue"]
    assert [p["paso"] for p in escena.paginas] == [0, 1, 0]
    for _ in range(4):                  # (completa y pasa dos veces)
        tecla(pygame.K_RETURN)
        avanzar(app)
    assert escena.cuadro_actual() == "despegue" and escena.pasos_en_cuadro < 5   # (su reloj volvio a empezar)


def test_un_dialogo_puede_empezar_con_el_cuadro_que_le_pasan(app):
    escena = dialogo(app, [("ines", "HOLA.")], cuadro="rescate")
    assert escena.cuadro_actual() == "rescate" and escena.con_cuadros
    sin = dialogo(app, [("ines", "HOLA.")])
    assert not sin.con_cuadros          # (sin cuadros se ve como antes)
    for escena in (escena, sin):
        for pasos in (1, ESCENA_TITULO // 2, ESCENA_TITULO + 5):
            escena.pasos = escena.pasos_en_cuadro = pasos
            escena.dibujar(app.pantalla)


def test_el_escenario_y_la_caja_entran_sin_pisarse(app):
    assert ESCENARIO.bottom < CAJA.top
    assert app.pantalla.get_rect().contains(ESCENARIO.inflate(8, 8))


def test_saltear_pide_confirmacion(app):
    escena = dialogo(app, [("cuadro", "cinturon"), ("ines", "UNO."), ("alba", "DOS.")])
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert not app.terminados and escena.confirmar      # (pregunta)
    avanzar(app, SALTEAR_CONFIRMA + 1)
    assert not escena.confirmar                         # (si no se confirma, se olvida)
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    tecla(pygame.K_RETURN)                              # seguir leyendo tambien cancela la pregunta
    avanzar(app)
    assert not escena.confirmar and not app.terminados
    saltear(app)
    assert app.terminados == [True]


def test_se_puede_volver_al_renglon_anterior(app):
    escena = dialogo(app, [("cuadro", "cinturon"), ("ines", "UNO."), ("cuadro", "despegue"), ("alba", "DOS.")])
    for _ in range(2):
        tecla(pygame.K_RETURN)
        avanzar(app)
    assert escena.indice == 1
    tecla(pygame.K_LEFT)
    avanzar(app)
    assert escena.indice == 0 and escena.cuadro_actual() == "cinturon"
    assert escena.pagina_completa()                     # (ya leido: aparece entero)
    tecla(pygame.K_LEFT)                                # (en el primero no hace nada)
    avanzar(app)
    assert escena.indice == 0


@pytest.mark.parametrize("velocidad", ["LENTO", "NORMAL", "RAPIDO", "AL INSTANTE"])
def test_la_velocidad_del_texto_sale_de_las_opciones(app, velocidad):
    app.opciones.texto = velocidad
    escena = dialogo(app, [("ines", "UN RENGLON DE PRUEBA CON VARIAS PALABRAS ADENTRO.")])
    avanzar(app, 9)
    escritas = escena.letras
    if velocidad == "AL INSTANTE":
        assert escena.pagina_completa()
    else:
        assert escritas == pytest.approx(10 * accesibilidad.letras_por_paso())
    assert app.opciones.texto == velocidad


def test_con_texto_lento_la_radio_dura_mas(app):
    from juego.radio import Mensaje
    mensaje = Mensaje("ines", "UN MENSAJE DE RADIO BASTANTE LARGO PARA QUE SE NOTE.", 0)
    normal = mensaje.duracion()
    app.opciones.texto = "LENTO"
    assert mensaje.duracion() > normal


def test_el_prologo_tambien_pide_confirmacion(app):
    prologo = Prologo(app, al_terminar=lambda: app.terminados.append(True))
    app.terminados = []
    app.cambiar_escena(prologo, transicion=False)
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert not app.terminados and not app.progreso.prologo
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert app.terminados == [True] and app.progreso.prologo


def test_el_plano_muestra_el_modulo_que_se_puede_fabricar(app):
    datos = pasajes.datos_del_plano(app.progreso, "escudo_termico")
    assert datos == {"modulo": "escudo_termico", "nivel": 1}
    app.progreso.hangar["escudo_termico"] = 1
    assert pasajes.datos_del_plano(app.progreso, "escudo_termico")["nivel"] == 2
    assert pasajes.datos_del_plano(app.progreso, None) == {}

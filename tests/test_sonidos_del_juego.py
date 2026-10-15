"""Cada cosa que pasa en el juego pide su sonido (MAPA_DE_AUDIO.md) y todo sale del estudio."""
import os

import pygame
import pytest

from juego.config import ruta, MS_POR_FRAME
from juego.sonido import CATALOGO, MUSICAS, AMBIENTES, BLOQUE_FICHA, cargar_fichas, ruta_del_sonido
from tests.ayudas import avanzar, tecla, jugar


@pytest.fixture
def pedidos(app):
    # Anota cada sonido que se pide (los inmediatos y los programados) en vez de solo tocarlo
    lista = []
    tocar, luego = app.sonidos.reproducir, app.sonidos.reproducir_luego
    app.sonidos.reproducir = lambda nombre, x=None: lista.append(nombre) or tocar(nombre, x)
    app.sonidos.reproducir_luego = lambda nombre, ms, x=None: lista.append(nombre) or luego(nombre, ms, x)
    return lista


# ---------- Todo sale del estudio ----------

def todos_los_archivos():
    # [(carpeta relativa a efectos/, archivo)] de efectos/ y sus subcarpetas (sin fichas.json)
    return [(os.path.relpath(raiz, ruta("efectos")).replace(os.sep, "/"), archivo)
            for raiz, _, archivos in os.walk(ruta("efectos")) for archivo in archivos if archivo != "fichas.json"]


def archivos_de_audio():
    # Los nombres de los sonidos de efectos/ (en cualquier subcarpeta)
    return {archivo for _, archivo in todos_los_archivos()}


def test_cada_sonido_esta_en_la_carpeta_de_su_familia():
    # efectos/ ordenada como el estudio: la carpeta de la familia (el modulo donde se compone) y,
    # un armonico, su propia carpeta con sus colores. Todo en OGG y sin nombres repetidos: el
    # juego busca cada archivo por su nombre
    from herramientas.estudio.obras import cargar_todas, ARMONICOS, ruta_relativa
    cargar_todas()
    archivos = todos_los_archivos()
    assert len(archivos) == len(archivos_de_audio())                    # sin nombres repetidos
    for carpeta, archivo in archivos:
        assert archivo.endswith(".ogg"), archivo
        nombre = archivo[:-4]
        obra, _, color = nombre.rpartition("_")
        esperada = ruta_relativa(obra, color) if obra in ARMONICOS else ruta_relativa(nombre)
        assert "%s/%s" % (carpeta, archivo) == esperada, archivo


def test_todo_el_sonido_sale_del_estudio():
    # Cada archivo de efectos/ sale de una obra del estudio: todo se puede volver a generar y
    # cambiar desde el codigo (los colores de un efecto armonico, moneda_1_fa.ogg, de su obra)
    from herramientas.estudio.obras import cargar_todas, ARMONICOS
    from herramientas.estudio.armonia import COLORES as COLORES_DEL_ESTUDIO
    obras = set(cargar_todas())
    for archivo in archivos_de_audio():
        nombre = archivo.rsplit(".", 1)[0]
        obra, _, color = nombre.rpartition("_")
        assert nombre in obras or (obra in ARMONICOS and color in COLORES_DEL_ESTUDIO), archivo


def test_el_catalogo_y_los_archivos_coinciden():
    usados = ({a for efecto in CATALOGO.values() for a in efecto.archivos} | set(MUSICAS.values())
              | set(AMBIENTES.values()))
    assert usados == archivos_de_audio()          # nada falta y nada sobra


def test_cada_archivo_tiene_su_ficha(app):          # (app: abre el mixer)
    # El limitador del mezclador lee cuanto suena cada archivo de efectos/fichas.json (lo
    # escribe herramientas/componer.py): un archivo sin ficha o con una vieja lo engaña
    fichas = cargar_fichas()
    for archivo in archivos_de_audio():
        es_tema = archivo.startswith(("musica_", "amb_")) or archivo == "laser.ogg"
        clave = "nivel" if es_tema else "envolvente"
        assert clave in fichas.get(archivo, {}), archivo
        if clave == "envolvente":
            # una envolvente por cada 50 ms del archivo
            segundos = pygame.mixer.Sound(ruta_del_sonido(archivo)).get_length()
            assert abs(len(fichas[archivo][clave]) - segundos * 1000 / BLOQUE_FICHA) <= 1.5, archivo


# ---------- La partida ----------

def test_la_moneda_sube_de_tono_con_el_combo(partida, pedidos):
    for _ in range(7):
        partida.moneda.x, partida.moneda.y = partida.nave.x, partida.nave.y
        jugar(partida)
    monedas = [p for p in pedidos if p.startswith("moneda_")]
    assert monedas[0] == "moneda_1" and monedas[-1] == "moneda_3"      # 7 monedas: x3
    assert "combo_sube_1" in pedidos and "combo_sube_2" in pedidos


def test_el_dash_suena(partida, pedidos):
    jugar(partida, dash=True)
    assert "nave_dash" in pedidos


def test_los_golpes_suenan_distinto_y_avisan_la_ultima_vida(partida, pedidos):
    partida.activar("escudo", 5000)
    partida.danar_jugador(partida.nave.x, partida.nave.y)
    assert pedidos[-1] == "escudo_roto"
    partida.vidas = 2
    partida.nave.invulnerable_hasta = 0
    partida.danar_jugador(partida.nave.x, partida.nave.y)
    assert "nave_golpe" in pedidos and "ultima_vida" in pedidos
    partida.danar_jugador(partida.nave.x, partida.nave.y)
    assert pedidos[-1] == "nave_muerte"


def test_la_cadena_de_perfectos_arma_el_acorde(partida, pedidos):
    for _ in range(3):
        partida.perfecto_en_este_dash = False
        partida._dash_perfecto(100, 100)
        partida.tiempo += 100
    assert [p for p in pedidos if p.startswith("perfecto_")] == ["perfecto_1", "perfecto_2", "perfecto_3"]


def test_el_jefe_llega_con_alerta_y_avisa_la_ventana(partida, pedidos):
    partida.iniciar_jefe("ojo")
    assert "alerta" in pedidos and "presentacion_nombre" in pedidos
    jefe = partida.jefe
    jefe.cambiar_fase("cansado", 3000, partida.tiempo)
    jefe.actualizar(partida)
    assert "vulnerable" not in pedidos          # (la fase ya estaba puesta antes del paso)
    jefe.cambiar_fase("flotar", 10, partida.tiempo)
    jefe.fase_hasta = partida.tiempo - 1
    jefe.actualizar(partida)                    # flotar -> atacar
    assert "ojo_carga" in pedidos


def test_el_asedio_suena_a_peligro(partida, pedidos):
    partida.director.empezar_asedio()
    assert "oleada" in pedidos


# ---------- Menus ----------

def test_los_menus_suenan(app, pedidos):
    avanzar(app)
    tecla(pygame.K_DOWN)
    avanzar(app)
    assert pedidos[-1] == "ui_mover"
    tecla(pygame.K_RETURN)                      # LOGROS
    avanzar(app)
    assert "ui_aceptar" in pedidos


def test_la_pausa_suena_al_entrar_y_al_salir(app, partida, pedidos):
    avanzar(app, 100)                           # (pasa el READY y el GO: ya en el juego)
    partida.pausa_pendiente = True
    avanzar(app, 2)
    assert "pausa" in pedidos
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert "seguir" in pedidos


def test_la_gasolinera_cobra_y_niega(app, partida, pedidos):
    from juego.escenas.gasolinera import Gasolinera, PASOS_SIN_ELEGIR
    partida.creditos = 0
    tienda = Gasolinera(app, app.escena)
    app.cambiar_escena(tienda)
    avanzar(app, PASOS_SIN_ELEGIR + 1)
    assert "tienda" in pedidos and "carta_1" in pedidos
    tecla(pygame.K_RETURN)                      # sin creditos: no alcanza
    avanzar(app)
    assert "ui_error" in pedidos
    partida.creditos = 10000
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert "caja" in pedidos


def test_el_latido_con_una_vida_y_su_opcion(partida, pedidos):
    partida.vidas = 1
    jugar(partida, 200)                         # ~3.3 s: late cada 1.6 s
    assert pedidos.count("latido") == 3
    partida.opciones.latido = False
    pedidos.clear()
    jugar(partida, 200)
    assert "latido" not in pedidos


def test_el_dash_sin_recarga_suena_a_vacio(partida, pedidos):
    jugar(partida, dash=True)
    jugar(partida, 15)                          # termino el dash (180 ms), pero falta para recargar
    jugar(partida, dash=True)
    assert "dash_vacio" in pedidos


def test_el_game_over_cuenta_el_puntaje(app, partida, pedidos):
    from juego.escenas.fin import Fin, MS_CONTADOR
    partida.puntaje = 500
    app.cambiar_escena(Fin(app, partida, fila_nueva=-1))
    avanzar(app, int(MS_CONTADOR / MS_POR_FRAME) + 10)
    assert [p for p in pedidos if p.startswith("contador_")][:8] == ["contador_%d" % n for n in range(1, 9)]
    assert "contador_fin" in pedidos and "teclear" in pedidos

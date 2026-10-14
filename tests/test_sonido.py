"""El mezclador (sonido.py): catalogo, voces, enfriamiento, prioridades, paneo, ducking y volumenes."""
import pygame
import pytest

from juego import sonido
from juego.sonido import (Sonidos, Efecto, CATALOGO, MUSICAS, AMBIENTES, MUSICA, EFECTOS, DETALLE, PELIGRO,
                          MOMENTO, PRIMER_CANAL_EFECTOS, paneo)
from juego.config import (ruta, ANCHO, CANALES_AUDIO, MEZCLA, PANEO_MINIMO, ATENUAR_MUSICA, ATENUAR_VUELTA,
                          TECHO_MEZCLA, PISO_DETALLES, RECUPERACION_MEZCLA)
from juego.escenas.opciones import Opciones as PantallaOpciones
from tests.ayudas import avanzar, tecla, ir_al_ajuste

CANALES_EFECTOS = CANALES_AUDIO - PRIMER_CANAL_EFECTOS


@pytest.fixture
def reloj():
    return [0]


def mezclador(reloj, catalogo, **otros):
    # Un mezclador con su propio catalogo y un reloj que se mueve a mano
    sonidos = Sonidos(catalogo=catalogo, **otros)
    sonidos.reloj = lambda: reloj[0]
    return sonidos


def test_todos_los_archivos_existen():
    archivos = [a for efecto in CATALOGO.values() for a in efecto.archivos]
    for archivo in archivos + list(MUSICAS.values()) + list(AMBIENTES.values()):
        with open(ruta("efectos/" + archivo), "rb"):
            pass


def test_el_paneo_sigue_a_la_x_sin_apagar_un_lado():
    assert paneo(ANCHO / 2) == (1.0, 1.0)              # al centro, los dos enteros
    izquierda, derecha = paneo(0)
    assert izquierda == 1.0 and derecha == pytest.approx(PANEO_MINIMO)
    izquierda, derecha = paneo(ANCHO)
    assert izquierda == pytest.approx(PANEO_MINIMO) and derecha == 1.0
    assert paneo(ANCHO * 0.25)[1] < paneo(ANCHO * 0.4)[1]     # se mueve de a poco
    assert paneo(None) == (1.0, 1.0) and paneo(0, mono=True) == (1.0, 1.0)


def test_el_enfriamiento_no_deja_repetir_enseguida(app, reloj):
    sonidos = mezclador(reloj, {"tic": Efecto("ui_error.wav", enfriamiento=100, voces=5)})
    assert sonidos.reproducir("tic") is not None
    reloj[0] += 60
    assert sonidos.reproducir("tic") is None
    reloj[0] += 40
    assert sonidos.reproducir("tic") is not None


def test_las_voces_cortan_al_mas_viejo(app, reloj):
    sonidos = mezclador(reloj, {"largo": Efecto("game_over.wav", voces=2)})
    primero = sonidos.reproducir("largo")
    reloj[0] += 10
    sonidos.reproducir("largo")
    reloj[0] += 10
    tercero = sonidos.reproducir("largo")
    assert sonidos.sonando("largo") == 2
    assert tercero is primero           # uso el canal del mas viejo


def test_lo_importante_le_gana_el_canal_a_lo_menos_importante(app, reloj):
    catalogo = {"detalle": Efecto("game_over.wav", prioridad=DETALLE, voces=99),
                "peligro": Efecto("game_over.wav", prioridad=PELIGRO, voces=99),
                "momento": Efecto("game_over.wav", prioridad=MOMENTO, voces=99)}
    sonidos = mezclador(reloj, catalogo)
    for _ in range(CANALES_EFECTOS):
        assert sonidos.reproducir("peligro") is not None
        reloj[0] += 1
    assert sonidos.reproducir("detalle") is None            # lleno de cosas mas importantes
    assert sonidos.reproducir("momento") is not None        # un momento le gana a un peligro
    assert sonidos.sonando("peligro") == CANALES_EFECTOS - 1
    assert sonidos.reproducir("peligro") is not None        # entre iguales, corta al mas viejo
    assert sonidos.sonando("momento") == 1


def test_las_variantes_no_se_repiten(app, reloj):
    sonidos = mezclador(reloj, {"v": Efecto(["ui_error.wav", "escudo_roto.wav", "nave_golpe.wav"], voces=9)})
    elegidas = [sonidos._elegir_variante("v", sonidos.catalogo["v"]) for _ in range(30)]
    assert all(a is not b for a, b in zip(elegidas, elegidas[1:]))
    assert len({id(e) for e in elegidas}) == 3


def test_un_momento_baja_la_musica_y_despues_vuelve(app, reloj):
    sonidos = mezclador(reloj, {"fanfarria": Efecto("record.wav", prioridad=MOMENTO)})
    assert sonidos.factor_musica() == 1.0
    sonidos.reproducir("fanfarria")
    dura = sonidos.variantes["fanfarria"][0].get_length() * 1000
    assert sonidos.factor_musica() == ATENUAR_MUSICA
    reloj[0] += dura + ATENUAR_VUELTA / 2
    assert ATENUAR_MUSICA < sonidos.factor_musica() < 1.0      # volviendo de a poco
    reloj[0] += ATENUAR_VUELTA / 2
    assert sonidos.factor_musica() == 1.0


def test_el_ducking_baja_solo_el_tema_que_suena(app, reloj):
    sonidos = mezclador(reloj, {"fanfarria": Efecto("record.wav", prioridad=MOMENTO)})
    sonidos.tocar_musica("menu")
    tema, otro = sonidos.musica.temas["menu"], sonidos.musica.temas["jefe"]
    sonidos.reproducir("fanfarria")
    assert tema.get_volume() < otro.get_volume()
    reloj[0] += 5000
    sonidos.actualizar()
    assert tema.get_volume() == pytest.approx(otro.get_volume())


def test_los_loops_no_se_duplican_y_se_paran(app, reloj):
    catalogo = {"laser": Efecto("nave_golpe.wav"), "sirena": Efecto("escudo_roto.wav"), "otro": Efecto("ui_error.wav")}
    sonidos = mezclador(reloj, catalogo)
    sonidos.tocar_loop("laser")
    sonidos.tocar_loop("laser")
    assert sonidos.en_loop.count("laser") == 1
    sonidos.tocar_loop("sirena")
    sonidos.tocar_loop("otro")                  # los dos canales de loop ocupados: no entra
    assert "otro" not in sonidos.en_loop
    sonidos.parar_loop("laser")
    assert "laser" not in sonidos.en_loop
    sonidos.parar_loops()
    assert sonidos.en_loop == [None, None]


def test_el_ambiente_tiene_su_propio_tocadiscos(app, reloj):
    sonidos = mezclador(reloj, {}, ambientes={"bosque": "musica_menu.ogg"})
    sonidos.tocar_musica("juego")
    sonidos.tocar_ambiente("bosque")
    assert sonidos.ambiente.actual == "bosque" and sonidos.actual == "juego"
    assert sonidos.ambiente.canal not in sonidos.musica.canales
    sonidos.parar_ambiente()
    assert sonidos.ambiente.actual is None and sonidos.actual == "juego"


def test_el_volumen_de_cada_categoria(app):
    opciones, sonidos = app.opciones, app.sonidos
    opciones.volumen, opciones.volumen_musica, opciones.volumen_efectos = 5, 10, 4
    sonidos.aplicar_volumen(opciones)
    assert sonidos.nivel(EFECTOS) == pytest.approx(0.5 * 0.4 * MEZCLA[EFECTOS])
    assert sonidos.nivel(MUSICA) == pytest.approx(0.5 * MEZCLA[MUSICA])
    assert sonidos.variantes["moneda_1"][0].get_volume() == pytest.approx(sonidos.nivel(EFECTOS), abs=0.01)
    opciones.silencio = True
    sonidos.aplicar_volumen(opciones)
    assert sonidos.nivel(EFECTOS) == 0 and sonidos.variantes["moneda_1"][0].get_volume() == 0


def test_el_audio_mono_no_panea(app, reloj, monkeypatch):
    pedidos = []
    monkeypatch.setattr(sonido, "paneo", lambda x, mono=False: pedidos.append((x, mono)) or (1.0, 1.0))
    sonidos = mezclador(reloj, {"tic": Efecto("ui_error.wav"), "menu": Efecto("ui_error.wav", paneo=False)})
    sonidos.aplicar_volumen(app.opciones)
    sonidos.reproducir("tic", 100)
    app.opciones.audio_mono = True
    reloj[0] += 100
    sonidos.reproducir("tic", 100)
    sonidos.reproducir("menu", 100)          # la interfaz va siempre al centro
    assert pedidos == [(100, False), (100, True), (None, True)]


def test_en_pausa_un_efecto_igual_toma_canal(app, reloj):
    sonidos = mezclador(reloj, {"pausa": Efecto("ui_error.wav")})
    sonidos.pausar_todo()
    canal = sonidos.reproducir("pausa")
    sonidos.reanudar_todo()
    assert canal is not None


def test_en_opciones_cada_volumen_cambia_lo_suyo_y_saca_el_silencio(app):
    app.opciones.silencio = True
    app.cambiar_escena(PantallaOpciones(app, volver_a=app.escena))
    ir_al_ajuste(app, "MUSICA")
    tecla(pygame.K_LEFT)
    avanzar(app)
    opciones = app.opciones
    assert opciones.volumen_musica == 9 and opciones.volumen_efectos == 10
    assert not opciones.silencio and app.sonidos.nivel(MUSICA) > 0


def test_audio_mono_se_prende_en_accesibilidad(app):
    app.cambiar_escena(PantallaOpciones(app, volver_a=app.escena))
    ir_al_ajuste(app, "AUDIO MONO")
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert app.opciones.audio_mono


# ---------- El limitador: la suma nunca satura ----------

def test_si_todo_entra_nada_baja_y_si_no_bajan_primero_los_detalles():
    assert Sonidos._cuanto_bajar(0.8, 0.3, 0.4) == {"detalles": 1.0, "importantes": 1.0}
    bajan = Sonidos._cuanto_bajar(0.8, 0.5, 0.6)          # sobra 0.3: los detalles bajan a la mitad
    assert bajan["importantes"] == 1.0 and bajan["detalles"] == pytest.approx(0.5)
    bajan = Sonidos._cuanto_bajar(0.8, 1.0, 1.0)          # ni con los detalles al piso entra
    assert bajan["detalles"] == pytest.approx(PISO_DETALLES * bajan["importantes"])
    assert 1.0 * bajan["importantes"] + 1.0 * bajan["detalles"] == pytest.approx(0.8)


def suma(sonidos, ahora):
    # Cuanto suena todo junto (lo que cuenta el limitador) con lo que bajo cada grupo
    total = sonidos.carga_del_fondo()
    for sonando in sonidos.en_canal:
        if sonando is not None:
            grupo = "importantes" if sonando.prioridad >= PELIGRO else "detalles"
            total += sonando.carga(ahora) * sonidos.bus[grupo]
    return total


def test_muchos_efectos_juntos_no_pasan_del_techo(app, reloj):
    catalogo = {"golpe": Efecto("game_over.wav", prioridad=PELIGRO, voces=99),
                "detalle": Efecto("game_over.wav", prioridad=DETALLE, voces=99)}
    sonidos = mezclador(reloj, catalogo)
    assert sonidos.reproducir("golpe") is not None
    assert sonidos.bus == {"detalles": 1.0, "importantes": 1.0}         # uno solo entra entero
    for nombre in ["detalle"] * 4:
        sonidos.reproducir(nombre)
        assert suma(sonidos, reloj[0]) <= TECHO_MEZCLA + 1e-6
    assert sonidos.bus["detalles"] < 1.0 and sonidos.bus["importantes"] == 1.0     # primero, los detalles
    while sonidos.bus["importantes"] == 1.0:
        assert sonidos.reproducir("golpe") is not None
        assert suma(sonidos, reloj[0]) <= TECHO_MEZCLA + 1e-6
    assert sonidos.bus["detalles"] < sonidos.bus["importantes"] < 1.0    # si no alcanza, todos


def test_cuando_se_despeja_el_volumen_vuelve_de_a_poco(app, reloj):
    sonidos = mezclador(reloj, {"golpe": Efecto("game_over.wav", prioridad=PELIGRO, voces=99)})
    for _ in range(6):
        sonidos.reproducir("golpe")
    assert sonidos.bus["importantes"] < 1.0
    for canal in sonidos.canales_efectos:       # se callan todos de golpe
        canal.stop()
    sonidos.en_canal = [None] * len(sonidos.en_canal)
    sonidos.bus = {"detalles": 0.2, "importantes": 0.2}
    reloj[0] += 16                              # un paso: sube un poquito, no de golpe
    sonidos.actualizar()
    assert sonidos.bus["importantes"] == pytest.approx(0.2 + 16 / RECUPERACION_MEZCLA)
    reloj[0] += RECUPERACION_MEZCLA
    sonidos.actualizar()
    assert sonidos.bus == {"detalles": 1.0, "importantes": 1.0}


def test_cada_efecto_tiene_su_envolvente(app):
    # Sin ficha el limitador supone lo peor (y bajaria todo de mas)
    sonidos = Sonidos()
    for nombre, lista in sonidos.variantes.items():
        if nombre != "laser":
            assert all(s in sonidos.envolventes for s in lista), nombre

"""La galaxia del modo historia: el mapa, el peligro, el reloj de la Umbral (la relatividad),
los viajes, la Marea, las puertas menores, los sistemas libres, el hangar y los ecos."""
import math

import pygame
import pytest

from juego import carteles, dibujo, recursos
from juego.config import (MAREA_ANIOS, ESTADIA_ANIOS, PUERTA_ANIOS, IMPULSOR_DESCUENTO, HANGAR_PRECIOS, VIAJE_LARGO_ANIOS,
                          PIEZAS_POR_PELIGRO, PIEZAS_POR_CREDITO, AVISO_TRAMO, MS_POR_FRAME)
from juego.anomalias import TIPOS_ANOMALIA
from juego.enemigos import TIPOS_ENEMIGO
from juego.escuadrones import FORMACIONES
from juego.objetivos import crear_objetivo
from juego.guardado import Progreso
from juego.historia import galaxia, tiempo, hangar
from juego.historia.galaxia import todos_los_sistemas, sistema, peligro, costo_viaje, UMBRAL
from juego.historia.exploracion import ModoExploracion, ruta_del_sistema
from juego.historia.ecos import ECOS
from juego.historia.mision import misiones_en_orden, mision, filtrar
from juego.historia.modo import ModoHistoria
from juego.historia.personajes import PERSONAJES
from juego.escenas.historia.galaxia import Galaxia, VIAJE_PASOS
from juego.escenas.historia.hangar import Hangar
from juego.escenas.historia.dialogo import Dialogo, ANCHO_TEXTO
from juego.escenas.historia.archivo import Archivo, DETALLE, LISTA, PESTANAS, ALTO_GLIFO, acomodar
from juego.escenas.historia.final import Final
from tests.ayudas import avanzar, tecla, jugar, entrar_a_la_historia


# ---------- El mapa ----------

def test_los_sistemas_estan_en_la_galaxia_y_no_se_repiten():
    ids = [uno.id for uno in todos_los_sistemas()]
    assert len(ids) == len(set(ids)) and UMBRAL in ids
    for uno in todos_los_sistemas():
        x, y = uno.lugar
        assert 40 <= x <= galaxia.ANCHO_GALAXIA - 40 and 40 <= y <= galaxia.ALTO_GALAXIA - 40, uno.id
        assert 1 <= uno.sector <= 5
        assert len(uno.nombre) <= 20, uno.nombre


def test_cuanto_mas_lejos_mas_peligro():
    casa = sistema(UMBRAL)
    por_distancia = sorted(todos_los_sistemas(), key=lambda uno: galaxia.distancia(casa, uno))
    peligros = [peligro(uno) for uno in por_distancia]
    assert peligros == sorted(peligros) and peligros[0] == 1 and peligros[-1] == 5


def test_cada_eco_esta_en_un_sistema_y_las_puertas_van_de_a_pares():
    ecos = [uno.eco for uno in galaxia.SISTEMAS if uno.eco]
    assert sorted(ecos) == sorted(eco.id for eco in ECOS)
    for uno in galaxia.SISTEMAS:
        if uno.puerta:
            assert sistema(uno.puerta).puerta == uno.id, uno.id


def test_los_textos_de_la_galaxia_entran(app):
    for eco in ECOS:
        assert not set(" ".join(eco.texto)) & set("ÁÉÍÓÚ"), eco.nombre
        _, alto = acomodar(eco.texto, DETALLE.width - 32, False)
        assert alto + (ALTO_GLIFO if eco.glifo else 0) <= DETALLE.height - 40, eco.nombre
        assert recursos.fuente(dibujo.CHICA).size(eco.nombre)[0] <= LISTA.width - 40, eco.nombre
        for quien, texto in eco.reaccion:
            assert quien in PERSONAJES and len(carteles.lineas_radio(texto)) <= 3, texto
    for _, renglones in tiempo.MENSAJES:
        for quien, texto in renglones:
            assert quien in PERSONAJES and len(dibujo.partir_lineas(texto, dibujo.CHICA, ANCHO_TEXTO)) <= 4, texto
    for uno in galaxia.SISTEMAS:
        for renglones in uno.radio.values():
            for _, texto in renglones:
                assert len(carteles.lineas_radio(texto)) <= 3, texto


# ---------- El reloj de la Umbral ----------

def test_el_camino_de_la_historia_deja_tiempo_para_explorar(tmp_path):
    # Umbral -> 1 -> 2 -> 3 -> 4 -> 5, sin desvios: llega a tiempo, con margen para explorar
    progreso = Progreso(str(tmp_path / "p.json"))
    camino = [UMBRAL, "M1", "M2", "M3", "M4", "M5"]
    total = sum(costo_viaje(sistema(a), sistema(b), progreso) for a, b in zip(camino, camino[1:]))
    assert MAREA_ANIOS - 2.5 <= total <= MAREA_ANIOS - 1.5


def test_el_viaje_cuesta_la_distancia_la_estadia_y_la_dilatacion(tmp_path):
    progreso = Progreso(str(tmp_path / "p.json"))
    casa, lejos, abismo = sistema(UMBRAL), sistema("S12"), sistema("M5")
    assert costo_viaje(lejos, lejos, progreso) == pytest.approx(ESTADIA_ANIOS)          # quedarse: solo la estadia
    assert costo_viaje(abismo, abismo, progreso) == pytest.approx(ESTADIA_ANIOS + abismo.gravedad)
    sin_impulsor = costo_viaje(casa, lejos, progreso)
    progreso.hangar["impulsor"] = 2
    con_impulsor = costo_viaje(casa, lejos, progreso)
    viaje = sin_impulsor - ESTADIA_ANIOS
    assert con_impulsor == pytest.approx(ESTADIA_ANIOS + viaje * (1 - 2 * IMPULSOR_DESCUENTO))


def test_una_puerta_menor_conocida_es_un_atajo(tmp_path):
    progreso = Progreso(str(tmp_path / "p.json"))
    uno = next(s for s in galaxia.SISTEMAS if s.puerta)
    otro = sistema(uno.puerta)
    caro = costo_viaje(uno, otro, progreso)
    progreso.puertas.add(otro.id)           # (se conoce desde cualquiera de sus lados)
    atajo = costo_viaje(uno, otro, progreso)
    assert atajo == pytest.approx(PUERTA_ANIOS + ESTADIA_ANIOS + otro.gravedad) and atajo < caro


def test_la_marea_avanza_y_se_traga_la_umbral_a_su_tiempo(tmp_path):
    progreso = Progreso(str(tmp_path / "p.json"))
    casa = sistema(UMBRAL)
    assert not tiempo.tragado(casa, MAREA_ANIOS - 0.1) and tiempo.tragado(casa, MAREA_ANIOS + 0.1)
    tiempo.pasar(progreso, 2.5)
    assert tiempo.restante(progreso) == pytest.approx(MAREA_ANIOS - 2.5) and not tiempo.tarde(progreso)
    assert [anio for anio, _ in tiempo.mensajes_pendientes(progreso)] == [1, 2]
    tiempo.pasar(progreso, 4)
    assert tiempo.tarde(progreso)


def test_con_la_historia_terminada_el_reloj_se_detiene(tmp_path):
    progreso = Progreso(str(tmp_path / "p.json"))
    progreso.cumplir_mision(next(clase.numero for clase in misiones_en_orden() if clase.final))
    tiempo.pasar(progreso, 3)
    assert progreso.anios == 0


def test_los_renglones_de_tiempo(tmp_path):
    antes = mision(5).despues
    a_tiempo = [texto for _, texto in filtrar(antes, set(), 2.0)]
    tarde = [texto for _, texto in filtrar(antes, set(), 6.5)]
    assert any("PREPAREN TODAS LAS NAVES" in texto for texto in a_tiempo)       # a tiempo se van todos
    assert not any("PREPAREN TODAS LAS NAVES" in texto for texto in tarde)
    assert any("LLEGAMOS TARDE" in texto for texto in tarde)


# ---------- La escena: elegir, viajar, llegar ----------

def ir_a_la_galaxia(app):
    entrar_a_la_historia(app)           # (saltea el prologo)
    assert isinstance(app.escena, Galaxia)
    return app.escena


def viajar(app, escena, id_sistema):
    escena.elegida = id_sistema
    tecla(pygame.K_RETURN)
    avanzar(app, VIAJE_PASOS + 2)


def test_las_flechas_eligen_el_sistema_de_ese_lado(app):
    escena = ir_a_la_galaxia(app)
    tecla(pygame.K_RIGHT)
    avanzar(app)
    assert escena.elegida == "M1"
    tecla(pygame.K_UP)
    avanzar(app)
    assert sistema(escena.elegida).lugar[1] < sistema("M1").lugar[1]
    tecla(pygame.K_LEFT)
    avanzar(app, 30)                    # (la camara lo sigue)
    assert escena.elegida != "M1"


def test_viajar_gasta_años_en_la_umbral_y_deja_la_nave_alla(app):
    escena = ir_a_la_galaxia(app)
    app.progreso.hangar["escudo_termico"] = 1       # (Piedra Roja quema)
    costo = escena.costo(sistema("S02"))
    viajar(app, escena, "S02")
    assert app.progreso.anios == pytest.approx(costo) and app.progreso.ubicacion == "S02"
    assert isinstance(app.escena.partida.modo, ModoExploracion)


def test_al_pasar_un_año_ines_manda_su_mensaje(app):
    escena = ir_a_la_galaxia(app)
    app.progreso.anios = 0.95
    viajar(app, escena, "M1")
    assert isinstance(app.escena, Dialogo) and app.escena.titulo == "AÑO 1"
    assert 1 in app.progreso.mensajes
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert isinstance(app.escena, Dialogo) and app.escena.titulo == mision(1).titulo     # y despues, la mision


@pytest.mark.parametrize("id_sistema", ["UMBRAL", "M3"])
def test_no_se_puede_ir_a_casa_ni_a_una_mision_bloqueada(app, id_sistema):
    escena = ir_a_la_galaxia(app)
    viajar(app, escena, id_sistema)
    assert app.escena is escena and app.progreso.anios == 0


def test_lo_que_se_trago_la_marea_no_se_puede_visitar(app):
    escena = ir_a_la_galaxia(app)
    app.progreso.anios = 7.5                # el frente ya paso la Vega del Sur
    assert escena.por_que_no(sistema("S01")) is not None
    viajar(app, escena, "S01")
    assert app.escena is escena


def test_la_galaxia_y_el_hangar_se_dibujan_en_todos_los_tiempos(app):
    escena = ir_a_la_galaxia(app)
    for anios in (0, 3.2, 6.4):
        app.progreso.anios = anios
        for id_ in ("UMBRAL", "M1", "S04", "S16", "M5"):
            escena.elegida = id_
            avanzar(app, 3)
    app.progreso.puertas.add("S04")
    avanzar(app)
    tecla(pygame.K_p)                   # el hangar
    avanzar(app)
    assert isinstance(app.escena, Hangar)
    avanzar(app, 5)


# ---------- Los sistemas libres ----------

def test_las_rutas_de_los_sistemas_libres_siguen_las_reglas():
    for uno in galaxia.SISTEMAS:
        if uno.tipo != "libre":
            continue
        tramos = ruta_del_sistema(uno)
        assert tramos == ruta_del_sistema(uno)              # siempre la misma
        assert len(tramos) == 4
        for numero, tramo in enumerate(tramos, start=1):
            assert len(tramo["nombre"]) <= 16
            tipos = {tipo for tipo, _, _ in tramo["escuadrones"]}
            for tipo, cantidad, formacion in tramo["escuadrones"]:
                assert tipo in TIPOS_ENEMIGO and formacion in FORMACIONES and cantidad >= 1
            objetivo = crear_objetivo(tramo["objetivo"])
            if objetivo.tipo == "romper":
                assert objetivo.enemigo in tipos and TIPOS_ENEMIGO[objetivo.enemigo].destruible
            elif objetivo.tipo == "perfectos":
                assert any(TIPOS_ENEMIGO[tipo].destruible for tipo in tipos)
            assert bool(tramo.get("asedio")) == (numero == 4 and peligro(uno) >= 3)
            assert tramo.get("anomalia") is None or tramo["anomalia"] in TIPOS_ANOMALIA


def explorar(app, id_sistema):
    app.nueva_partida(modo=ModoExploracion(id_sistema))
    avanzar(app, 101)
    partida = app.escena.partida
    partida.nave.invulnerable_hasta = math.inf
    partida.director.con_escuadrones = False
    partida.proximo_powerup = math.inf
    return partida


def test_el_peligro_agranda_los_escuadrones_y_no_hay_taller(app):
    cerca, lejos = explorar(app, "S02"), None
    escuadrones_cerca = cerca.reglas["escuadrones"]
    lejos = explorar(app, "S16")
    assert lejos.reglas["escuadrones"] > escuadrones_cerca and lejos.reglas["velocidad"] > cerca.reglas["velocidad"]
    assert not lejos.modo.hay_jefe() and not lejos.modo.abre_el_taller(lejos.director)


def despejar(app, partida):
    while partida.director.numero_tramo < 4:
        partida.subir_nivel()
    partida.director.cumplir_objetivo()
    jugar(partida, 2)
    avanzar(app, int(AVISO_TRAMO / MS_POR_FRAME) + 10)


def test_despejar_un_sistema_da_piezas_su_eco_y_su_puerta(app):
    partida = explorar(app, "S04")          # (tiene puerta, no eco)
    partida.creditos = 200
    despejar(app, partida)
    assert isinstance(app.escena, Dialogo) and app.escena.rotulo == "SISTEMA DESPEJADO"
    primera = round(200 * PIEZAS_POR_CREDITO) + PIEZAS_POR_PELIGRO * peligro(sistema("S04"))
    assert app.progreso.piezas == primera
    assert "S04" in app.progreso.sistemas and "S04" in app.progreso.puertas
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert isinstance(app.escena, Galaxia) and app.escena.elegida == "S04"
    partida = explorar(app, "S04")          # repetirlo: solo lo de las monedas
    partida.creditos = 200
    despejar(app, partida)
    assert app.progreso.piezas == primera + round(200 * PIEZAS_POR_CREDITO)
    partida = explorar(app, "S01")          # (tiene eco)
    despejar(app, partida)
    assert "E01" in app.progreso.fragmentos


def test_si_explota_ines_rescata_la_mitad(app):
    partida = explorar(app, "S02")
    partida.creditos = 310
    partida.nave.invulnerable_hasta = 0
    partida.vidas = 1
    partida.danar_jugador(*partida.nave.centro())
    avanzar(app, 140)
    assert isinstance(app.escena, Dialogo) and app.progreso.piezas == round(310 * PIEZAS_POR_CREDITO) // 2
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert isinstance(app.escena, Galaxia) and app.escena.elegida == "S02"


# ---------- El hangar ----------

def test_el_hangar_vende_niveles_con_piezas(tmp_path):
    progreso = Progreso(str(tmp_path / "p.json"))
    assert not hangar.comprar(progreso, "recarga")          # sin piezas
    progreso.piezas = 1000
    for precio in HANGAR_PRECIOS["recarga"]:
        assert hangar.comprar(progreso, "recarga")
    assert not hangar.comprar(progreso, "recarga")          # al maximo
    assert progreso.piezas == 1000 - sum(HANGAR_PRECIOS["recarga"])
    assert Progreso(str(tmp_path / "p.json")).hangar == {"recarga": len(HANGAR_PRECIOS["recarga"])}


def test_lo_instalado_va_desde_el_despegue(app):
    app.progreso.hangar = {"recarga": 2, "corazon": 1}
    app.nueva_partida(modo=ModoHistoria(1))
    partida = app.escena.partida
    assert partida.mejora("recarga") == 2 and partida.vidas_max == partida.reglas["vidas"] + 1


def test_el_hangar_compra_con_aceptar(app):
    app.progreso.piezas = 500
    escena = Hangar(app, volver_a=None)
    app.cambiar_escena(escena, transicion=False)
    tecla(pygame.K_RETURN)                  # el impulsor
    avanzar(app)
    assert app.progreso.hangar.get("impulsor") == 1


# ---------- Los ecos en el Archivo y el final tarde ----------

def test_los_ecos_tienen_su_pestaña(app):
    archivo = Archivo(app, volver_a=None)
    archivo.pestana = PESTANAS.index("ECOS")
    assert [entrada.id for entrada in archivo.entradas()] == [eco.id for eco in ECOS]
    app.progreso.encontrar_fragmento("E08")
    app.cambiar_escena(archivo, transicion=False)
    for _ in range(len(ECOS)):
        tecla(pygame.K_DOWN)
        avanzar(app)


def test_el_final_cambia_si_se_llego_tarde(app):
    app.progreso.anios = 6.3
    final = Final(app, lambda: None)
    assert final.tarde
    app.cambiar_escena(final, transicion=False)
    avanzar(app, 260)


# ---------- Elegir bien (accesibilidad) y el aviso del viaje largo ----------

def test_desde_cualquier_sistema_se_llega_a_todos(app):
    escena = ir_a_la_galaxia(app)
    app.progreso.misiones = {1, 2, 3, 4, 5}
    app.progreso.fragmentos |= {"F02", "F04", "F07"}            # (la oculta tambien)
    vecinos = {}
    for uno in escena.sistemas():
        vecinos[uno.id] = {otro.id for otro in (escena.vecino(dx, dy, desde=uno)
                                                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) if otro}
    for inicio in vecinos:
        vistos, pendientes = {inicio}, [inicio]
        while pendientes:
            for otro in vecinos[pendientes.pop()] - vistos:
                vistos.add(otro)
                pendientes.append(otro)
        assert vistos == set(vecinos), inicio


def test_lb_y_rb_saltan_a_donde_se_puede_ir(app):
    escena = ir_a_la_galaxia(app)
    tecla(pygame.K_e)
    avanzar(app)
    assert escena.elegida == "M1"                   # al principio, lo unico abierto
    app.progreso.hangar["escudo_termico"] = 1
    tecla(pygame.K_e)
    avanzar(app)
    assert escena.elegida != "M1" and escena.por_que_no(sistema(escena.elegida)) is None


def test_al_principio_todo_esta_bloqueado_menos_la_primera_mision(app):
    escena = ir_a_la_galaxia(app)
    abiertos = [uno.id for uno in escena.sistemas() if escena.por_que_no(uno) is None]
    assert abiertos == ["M1"]
    assert all(uno.ambiente is not None for uno in galaxia.SISTEMAS if uno.tipo == "libre")


def test_un_viaje_largo_pregunta_antes_y_por_defecto_te_quedas(app):
    escena = ir_a_la_galaxia(app)
    app.progreso.hangar["filtro"] = 1
    lejos = sistema("S12")                          # (Miel: mas de un año de viaje)
    costo = escena.costo(lejos)
    assert costo >= VIAJE_LARGO_ANIOS
    viajar(app, escena, "S12")
    assert app.escena is escena and escena.aviso is not None and app.progreso.anios == 0
    tecla(pygame.K_RETURN)                          # QUEDARME
    avanzar(app)
    assert escena.aviso is None and app.progreso.anios == 0
    viajar(app, escena, "S12")
    tecla(pygame.K_RIGHT)                           # VIAJAR
    avanzar(app)
    tecla(pygame.K_RETURN)
    avanzar(app, VIAJE_PASOS + 2)
    assert app.progreso.ubicacion == "S12" and app.progreso.anios == pytest.approx(costo)


def test_un_viaje_corto_que_cambia_la_historia_tambien_avisa(app):
    escena = ir_a_la_galaxia(app)
    app.progreso.anios = 2.8
    lineas = escena.aviso_del_viaje(sistema("M1"))
    assert lineas and any("PRISA" in linea for linea in lineas)
    app.progreso.anios = 0
    assert escena.aviso_del_viaje(sistema("M1")) is None       # corto y sin cambios: sale directo


def test_cada_año_que_cambia_la_historia_tiene_su_aviso():
    anios = {anio for anio, _ in tiempo.HITOS}
    for clase in misiones_en_orden():
        for renglon in list(clase.antes) + list(clase.despues) + [r for lista in clase.radio.values() for r in lista]:
            for parte in (renglon[2].split("+") if len(renglon) > 2 and renglon[2] else []):
                if parte.lstrip("!").startswith("T"):
                    assert int(parte.lstrip("!")[1:]) in anios, parte


def test_el_aviso_del_viaje_entra_sin_cortarse(app):
    from juego.escenas.historia.galaxia import AVISO
    escena = ir_a_la_galaxia(app)
    app.progreso.hangar.update({"escudo_termico": 2, "filtro": 2, "casco_panal": 2, "compensador": 2})
    app.progreso.anios = 2.9                        # (cruza los dos años que cambian la historia)
    lineas = escena.aviso_del_viaje(sistema("S16"))
    assert len(lineas) == 4
    for linea in lineas:
        assert recursos.fuente(dibujo.CHICA).size(linea)[0] <= AVISO.width - 32, linea
    assert recursos.fuente(dibujo.CHICA).size("¿VIAJAR A %s?" % max(
        (uno.nombre for uno in todos_los_sistemas()), key=len))[0] <= AVISO.width - 100

"""Opciones con pestañas y las opciones de accesibilidad (temblor, destellos y CRT)."""
import json

import pygame

from juego import accesibilidad, dibujo, recursos
from juego.config import ROJO, NIVELES_CRT, PARPADEO_MINIMO, RESOLUCIONES, PIXEL_ARTE
from juego.dibujo import MEDIA, CHICA
from juego.efectos import Efectos, ZONA_TEXTOS
from juego.escenas.opciones import (Opciones, AJUSTES, PESTANAS, ajustes_de, Interruptor, Volumen, FILA_Y,
                                    ALTO_FILA, LINEA_Y, PANEL, DESCRIPCION_Y, ANCHO_DESCRIPCION, NOMBRE_X, VALOR_X,
                                    SEPARACION_FLECHA)
from tests.ayudas import avanzar, tecla, ir_al_ajuste


# ---------- El menu ----------

def test_todo_entra_en_el_panel(app):
    for pestana in PESTANAS:
        # Las filas (ajustes + VOLVER) quedan arriba de la linea de la descripcion
        ultima = FILA_Y + len(ajustes_de(pestana)) * ALTO_FILA
        assert ultima + 12 < LINEA_Y, pestana
    fuente = recursos.fuente(MEDIA)
    for ajuste in AJUSTES:
        # La descripcion entra en dos renglones dentro del panel
        lineas = dibujo.partir_lineas(ajuste.descripcion, CHICA, ANCHO_DESCRIPCION)
        assert len(lineas) <= 2, ajuste.nombre
        assert DESCRIPCION_Y + (len(lineas) - 1) * 24 + 8 < PANEL.bottom - 7
        # El nombre no choca con su valor mas ancho
        fin_del_nombre = NOMBRE_X + fuente.size(ajuste.nombre)[0]
        assert fin_del_nombre + 24 < VALOR_X - _ancho_maximo(ajuste, fuente), ajuste.nombre


def _ancho_maximo(ajuste, fuente):
    # Lo mas ancho que puede ocupar el valor de un ajuste a la derecha
    if isinstance(ajuste, Interruptor):
        return 56 + 16 + fuente.size("SI")[0]           # la llave y el texto
    if isinstance(ajuste, Volumen):
        return 22 + 10 * 16 + 22                        # flechas y 10 cuadritos
    if callable(ajuste.valores):
        textos = [nombre for nombre, _, _ in RESOLUCIONES]
    else:
        textos = [ajuste.nombres.get(valor, str(valor)) for valor in ajuste.valores]
    return max(fuente.size(t)[0] for t in textos) + 2 * SEPARACION_FLECHA + 8     # el texto y las dos flechas


def test_las_secciones_se_cambian_con_lb_rb_y_q_e(app):
    from juego.config import BOTON_LB, BOTON_RB
    from tests.ayudas import boton
    app.cambiar_escena(Opciones(app, volver_a=app.escena))
    opciones = app.escena
    tecla(pygame.K_e)                   # SONIDO
    avanzar(app)
    assert PESTANAS[opciones.pestana] == "SONIDO" and opciones.fila == 0
    assert opciones.filas()[opciones.fila].nombre == "VOLUMEN"
    tecla(pygame.K_LEFT)                # IZQ/DER cambia el valor, no la seccion
    avanzar(app)
    assert PESTANAS[opciones.pestana] == "SONIDO" and app.opciones.volumen == 9
    boton(BOTON_RB)                     # con el mando: RB la siguiente...
    avanzar(app)
    assert PESTANAS[opciones.pestana] == "ACCESIBILIDAD"
    boton(BOTON_LB)                     # ...y LB la anterior
    tecla(pygame.K_q)                   # (Q tambien)
    avanzar(app)
    assert PESTANAS[opciones.pestana] == "VIDEO"
    # Hacia arriba desde el primer ajuste se llega a VOLVER
    tecla(pygame.K_UP)
    avanzar(app)
    assert opciones.en_volver()


def test_las_opciones_de_accesibilidad_se_cambian_y_se_guardan(app, tmp_path):
    app.cambiar_escena(Opciones(app, volver_a=app.escena))
    ir_al_ajuste(app, "TEMBLOR")
    tecla(pygame.K_LEFT)
    avanzar(app)
    assert app.opciones.temblor == "SUAVE"
    tecla(pygame.K_DOWN)                # DESTELLOS
    tecla(pygame.K_RIGHT)
    avanzar(app)
    assert app.opciones.destellos == "REDUCIDOS"
    guardado = json.loads((tmp_path / "config.json").read_text())
    assert guardado["temblor"] == "SUAVE" and guardado["destellos"] == "REDUCIDOS"


def test_crt_se_cambia_y_no_da_la_vuelta(app):
    app.cambiar_escena(Opciones(app, volver_a=app.escena))
    ir_al_ajuste(app, "CRT")
    for _ in range(5):
        tecla(pygame.K_LEFT)
    avanzar(app)
    assert app.opciones.crt == "NO"


# ---------- Accesibilidad ----------

def test_temblor_no_quieta_la_pantalla(app):
    app.opciones.temblor = "NO"
    efectos = Efectos()
    efectos.sacudir(30)
    for _ in range(29):
        efectos.actualizar()
        assert efectos.desplazamiento == (0, 0)


def test_el_temblor_se_mueve_de_a_2_px_y_se_calma(app):
    app.opciones.temblor = "NORMAL"
    efectos = Efectos()
    efectos.sacudir(40)
    movidas = set()
    for _ in range(39):
        efectos.actualizar()
        dx, dy = efectos.desplazamiento
        assert dx % 2 == 0 and dy % 2 == 0 and abs(dx) <= 6 and abs(dy) <= 6
        movidas.add((dx, dy))
    assert len(movidas) > 3
    efectos.actualizar()
    assert efectos.desplazamiento == (0, 0)


def test_destellos_reducidos_frenan_los_parpadeos(app, monkeypatch):
    app.opciones.destellos = "REDUCIDOS"
    reloj = [0]
    monkeypatch.setattr(pygame.time, "get_ticks", lambda: reloj[0])
    vistos = []
    for reloj[0] in range(0, PARPADEO_MINIMO):
        vistos.append(dibujo.parpadeo(60))
    assert len(set(vistos)) == 1            # en menos de PARPADEO_MINIMO no cambia
    app.opciones.destellos = "NORMALES"
    vistos = [dibujo.parpadeo(60) for reloj[0] in range(0, PARPADEO_MINIMO)]
    assert len(set(vistos)) == 2


def test_destellos_reducidos_sin_destello_de_pantalla(app):
    app.opciones.destellos = "REDUCIDOS"
    efectos = Efectos()
    efectos.sacudir(10, ROJO)
    pantalla = pygame.Surface((100, 100))
    efectos.dibujar_temblor_y_destello(pantalla)
    assert pantalla.get_at((50, 50))[:3] == (0, 0, 0)
    app.opciones.destellos = "NORMALES"
    efectos.dibujar_temblor_y_destello(pantalla)
    assert pantalla.get_at((50, 50))[:3] != (0, 0, 0)


def test_las_lineas_crt_calzan_con_los_pixeles_de_arte(app):
    # Una linea oscura al pie de cada fila de pixeles de arte (PIXEL_ARTE filas del lienzo)
    lienzo = pygame.Surface((1066, 600))
    lienzo.fill((200, 200, 200))
    ventana = app.ventana
    app.opciones.crt = "NORMAL"
    # Sin escalar: fila clara, fila oscura (cada pixel de arte mide 2)
    ventana.mostrar(lienzo)
    filas = [ventana.superficie.get_at((10, y))[0] for y in range(12)]
    oscura = filas[1]
    assert abs(oscura - 200 * NIVELES_CRT["NORMAL"] / 255) <= 1
    assert filas == [200, oscura] * 6
    # Agrandada 1.8 veces (1920x1080): cada fila de arte ocupa 3 o 4 filas de la ventana,
    # pero tiene UNA sola linea, en su ultima fila. Para verlo, cada fila de arte se pinta
    # de un tono distinto y se compara con y sin CRT
    for fila in range(0, 600, PIXEL_ARTE):
        lienzo.fill((200 if fila // PIXEL_ARTE % 2 else 120, 0, 0), (0, fila, 1066, PIXEL_ARTE))
    ventana.superficie = pygame.Surface((1920, 1080))
    app.opciones.crt = "NO"
    ventana.mostrar(lienzo)
    sin_crt = [ventana.superficie.get_at((960, y))[0] for y in range(1080)]
    app.opciones.crt = "NORMAL"
    ventana.mostrar(lienzo)
    con_crt = [ventana.superficie.get_at((960, y))[0] for y in range(1080)]
    tramos = []         # [filas de la ventana] de cada fila de arte
    for y in range(1080):
        if y == 0 or sin_crt[y] != sin_crt[y - 1]:
            tramos.append([])
        tramos[-1].append(y)
    assert len(tramos) == 600 // PIXEL_ARTE
    for tramo in tramos:
        oscuras = [y for y in tramo if con_crt[y] < sin_crt[y]]
        assert oscuras == [tramo[-1]]               # una sola, la ultima


def test_sin_opciones_todo_funciona_como_siempre(monkeypatch):
    monkeypatch.setattr(accesibilidad, "opciones", None)
    assert accesibilidad.temblor_maximo() == 3
    assert not accesibilidad.destellos_reducidos()
    assert accesibilidad.brillo_crt() == NIVELES_CRT["NORMAL"]


# ---------- El HUD y los textos flotantes ----------

def test_el_hud_no_tiembla(app, partida):
    escena = app.escena
    pantalla = app.pantalla

    def pixeles_rojos():
        # Donde esta la palabra PUNTOS (roja), arriba a la izquierda
        return {(x, y) for x in range(0, 140) for y in range(8, 36) if pantalla.get_at((x, y))[:3] == ROJO}

    escena.dibujar_partida(pantalla, partida)
    quieto = pixeles_rojos()
    assert quieto
    app.efectos.temblor, app.efectos.desplazamiento = 10, (6, 6)
    escena.dibujar_partida(pantalla, partida)
    assert pixeles_rojos() == quieto


def test_los_textos_flotantes_no_se_pisan_ni_se_salen(app):
    efectos = Efectos()
    for _ in range(6):
        efectos.texto_flotante("¡PERFECTO! +30", 500, 300, ROJO)
    efectos.texto_flotante("+5", 1060, 20, ROJO)        # en la esquina, encima del HUD
    _sin_pisarse(efectos)


def test_los_textos_no_se_pisan_mientras_suben(app):
    # Como en el juego: van naciendo en el mismo lugar con unos pasos de diferencia (los
    # nuevos suben mas rapido que los viejos, que ya frenaron) y cerca del techo
    efectos = Efectos()
    for paso in range(80):
        if paso % 4 == 0 and paso < 40:
            efectos.texto_flotante("+" + str(paso), 300, 150, ROJO)
        efectos.actualizar()
        _sin_pisarse(efectos)


def _sin_pisarse(efectos):
    cajas = [texto.caja() for texto in efectos.textos]
    for i, caja in enumerate(cajas):
        assert ZONA_TEXTOS.contains(caja)
        for otra in cajas[i + 1:]:
            assert not caja.colliderect(otra)

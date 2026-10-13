"""Efectos visuales: neon (halos), ondas de choque, fogonazos, estelas, giro de la nave,
salto al hiperespacio y escalado suave de la ventana."""
import math

import pygame

from juego import dibujo, nave
from juego.config import MAGENTA, CIAN, PIXEL_ARTE
from juego.efectos import Efectos
from juego.fondo import Fondo, HIPERESPACIO_PASOS
from juego.jefes import crear_jefe
from juego.proyectiles import Bala, Escombro, dibujar_balas
from tests.ayudas import jugar


# ---------- Neon ----------

def test_el_halo_suma_luz_y_respeta_la_opcion_neon(app):
    pantalla = pygame.Surface((100, 100))
    app.opciones.neon = "NORMAL"
    dibujo.halo(pantalla, 50, 50, 30, MAGENTA)
    centro = pantalla.get_at((50, 50))[:3]
    assert centro[0] > 0 and centro[2] > 0 and centro[1] == 0       # se tiño del color
    pantalla.fill((0, 0, 0))
    app.opciones.neon = "NO"
    dibujo.halo(pantalla, 50, 50, 30, MAGENTA)
    assert pantalla.get_at((50, 50))[:3] == (0, 0, 0)


def test_las_balas_brillan_y_dejan_estela_menos_el_metal(app):
    app.opciones.neon = "NORMAL"
    pantalla = pygame.Surface((200, 200))
    bala = Bala(100, 100, 0, 4)                 # va hacia abajo: la estela queda arriba
    dibujar_balas(pantalla, [bala])
    assert pantalla.get_at((100, 100 - 4 * 3))[:3] != (0, 0, 0)        # estela detras
    assert pantalla.get_at((100 + 14, 100))[:3] != (0, 0, 0)           # resplandor alrededor
    pantalla.fill((0, 0, 0))
    dibujar_balas(pantalla, [Escombro(100, 100, 0, 4)])
    assert pantalla.get_at((100 + 22, 100))[:3] == (0, 0, 0)           # el metal no brilla


# ---------- Ondas de choque y fogonazos ----------

def test_la_onda_de_choque_crece_y_se_va():
    efectos = Efectos()
    efectos.onda_de_choque(100, 100, 80, CIAN, pasos=10)
    pantalla = pygame.Surface((200, 200))
    for _ in range(9):
        efectos.actualizar()
    efectos.dibujar(pantalla)
    # Ya crecio: hay algo dibujado lejos del centro y nada en el centro
    assert any(pantalla.get_at((100 + r, 100))[:3] != (0, 0, 0) for r in range(60, 82))
    efectos.actualizar()
    assert not efectos.ondas


def test_cada_bala_del_jefe_nace_con_un_fogonazo(partida):
    partida.jefe = crear_jefe("ojo", partida)
    partida.jefe.y = partida.jefe.y_final
    partida.jefe.al_terminar_de_entrar(partida)
    ondas_antes = len(partida.efectos.ondas)
    for _ in range(600):
        jugar(partida)
        if partida.balas:
            break
    assert partida.balas
    assert len(partida.efectos.ondas) > ondas_antes


# ---------- La nave al girar ----------

def test_la_nave_girada_se_guarda_y_conserva_el_tamano(app):
    girada = nave.girada("nave", 45)
    assert girada is nave.girada("nave", 46)        # mismo paso de 5 grados: la misma imagen
    diagonal = math.ceil(50 * math.sqrt(2))
    assert abs(girada.get_width() - diagonal) <= 2
    derecha = nave.girada("nave", 0)
    assert derecha.get_size() == (50, 50)


def test_los_giros_se_preparan_de_a_poco(app):
    nave.cambiar_color(None)                        # (vacia la cache)
    nave.preparar_giros(5)
    assert len(nave._giradas) == 5
    nave.preparar_giros(3)
    assert len(nave._giradas) == 8


# ---------- Hiperespacio ----------

def test_el_salto_al_hiperespacio_acelera_y_frena(app):
    fondo = Fondo()
    assert fondo.velocidad_salto() == 0
    fondo.saltar_al_hiperespacio()
    velocidades = []
    for _ in range(HIPERESPACIO_PASOS):
        velocidades.append(fondo.velocidad_salto())
        fondo.mover()
    assert max(velocidades) > 10                    # en el medio va muy rapido...
    assert velocidades[0] < 1 and fondo.velocidad_salto() == 0      # ...y empieza y termina quieto


# ---------- Escalado suave ----------

def test_el_escalado_suave_deja_los_pixeles_parejos(app):
    lienzo = pygame.Surface((1066, 600))
    lienzo.fill((0, 0, 0))
    for x in range(0, 1066, 2):                     # rayas de 1 px: con 1.8x salen desparejas
        lienzo.fill((255, 255, 255), (x, 0, 1, 600))
    ventana = app.ventana
    ventana.superficie = pygame.Surface((1920, 1080))
    app.opciones.crt = "NO"

    def luz_de_cada_raya():
        # Agrandado 1.8 veces, un pixel ocupa 1.8 de la ventana: ninguno puede medir lo
        # mismo exacto. Lo que tiene que ser parejo es cuanta luz lleva cada raya (la suma
        # de su brillo en su tramo de la ventana)
        luces = []
        for x in range(60, 300, 2):
            desde = round(1 + (x - 0.5) * 1.8)
            hasta = round(1 + (x + 1.5) * 1.8)
            luces.append(sum(ventana.superficie.get_at((px, 500))[0] for px in range(desde, hasta)))
        return luces

    app.opciones.escalado = "NITIDO"
    ventana.mostrar(lienzo)
    nitido = luz_de_cada_raya()
    assert max(nitido) - min(nitido) >= 255         # unas de 1 px y otras de 2: el doble de luz
    app.opciones.escalado = "SUAVE"
    ventana.mostrar(lienzo)
    suave = luz_de_cada_raya()
    assert max(suave) - min(suave) < 100            # todas parecidas


# ---------- La grilla de pixeles de arte ----------

def test_todo_calza_en_la_grilla_de_pixeles_de_arte(app):
    # Halos, balas, estelas, particulas y ondas puestos en lugares impares a proposito:
    # todo cambio de color tiene que caer en el borde de un pixel de arte (PIXEL_ARTE)
    app.opciones.neon = "NORMAL"
    pantalla = pygame.Surface((240, 240))
    dibujar_balas(pantalla, [Bala(61.3, 77.7, 3, 1)])
    dibujo.halo(pantalla, 151, 63, 30, CIAN)
    efectos = Efectos()
    efectos.explosion(121, 171, [MAGENTA, CIAN], 20, 4, 3)
    efectos.onda_de_choque(171, 151, 50, MAGENTA, pasos=10)
    for _ in range(5):
        efectos.actualizar()
    efectos.dibujar(pantalla)
    ancho, alto = pantalla.get_size()
    for y in range(alto):
        for x in range(1, ancho):
            if pantalla.get_at((x, y)) != pantalla.get_at((x - 1, y)):
                assert x % PIXEL_ARTE == 0, (x, y)
    for x in range(ancho):
        for y in range(1, alto):
            if pantalla.get_at((x, y)) != pantalla.get_at((x, y - 1)):
                assert y % PIXEL_ARTE == 0, (x, y)

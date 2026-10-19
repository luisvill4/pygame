"""
Los cuadros de la MISION 5: EL FIN DE LA LUZ (el Abismo Azul). El final de la historia.

    antes:    umbral_caida (tarde: la Umbral ya no existe) → agujero_negro (con dos relojes: cerca
              del borde el tiempo casi no pasa) → anillo (todo va hacia ahi) → descenso_lejos
              (la Alondra cae hacia el borde y la radio de Ines se estira)
    despues:  anillo_abierto → refugio (una luz pegada al borde, miles de monedas) → el_ultimo (sale
              de la oscuridad) → galaxia_perdida (la Marea se traga la suya) → posta (viaja delante
              de ella, de galaxia en galaxia) → una_hora (una hora son mil años) → mateo_vivo →
              vengan (o vengan_tarde) → primera_bitacora (F11) → relevo (F11: ahora las deja Alba)
"""
import math
import random

import pygame

from juego import dibujo, recursos
from juego.config import BLANCO, ROJO, AMARILLO, CIAN, VIOLETA, HIELO, NARANJA, TEXTO, TEXTO_SUAVE, GRIS
from juego.historia.glifos import escribir
from juego.historia.personajes import RETRATOS
from juego.escenas.historia.cuadros.base import cuadro, NOCHE
from juego.escenas.historia.cuadros import kit
from juego.escenas.historia.cuadros.kit import g, rotulo, mezclar, NUESTRA, MAREA, SUYA
from juego.escenas.historia.cuadros.mision_2 import glifo_grande

# Mateo de verdad, vivo: el mismo dibujo del retrato con color (por la radio era gris)
MATEO_VIVO = dict(RETRATOS["mateo"], paleta={"X": (40, 70, 140), "v": (20, 30, 60), "s": (236, 196, 160),
                                             "o": (40, 40, 50), "m": (170, 80, 80), "b": (120, 80, 50),
                                             "u": (50, 90, 160), "y": (255, 221, 0)})


def asteroides_del_anillo(pantalla, cx, cy, radio, t, hueco=0.0, achatado=0.34):
    # El anillo de rocas que cuida la puerta (los sprites del jefe). 'hueco' (0 a 1) lo abre por
    # delante: las rocas de abajo se apartan a los costados
    rocas = recursos.hoja("singularidad_asteroide.png", 32)
    for i in range(18):
        a = t * 0.004 + i * math.tau / 18
        frente = math.sin(a)
        separa = hueco * max(0.0, frente) * 0.9 * (1 if math.cos(a) > 0 else -1)
        x = cx + math.cos(a + separa) * radio
        y = cy + math.sin(a + separa) * radio * achatado
        if rocas:
            imagen = rocas[i % 2]
            if frente < 0:
                imagen = kit.apagada(imagen, 0.6)
            dibujo.pegar(pantalla, imagen, x, y, centrado=True)
        else:
            kit.disco(pantalla, x, y, 12, (110, 120, 150))


@cuadro("umbral_caida", "LO QUE QUEDA DE LA UMBRAL")
def umbral_caida(pantalla, zona, t, paso, datos):
    # Tarde: la Marea ya paso por la Umbral. Pedazos de la estacion y tres naves que se alejan
    kit.estrellas(pantalla, zona, 71, 80)
    cx, cy = zona.left + 300, zona.centery + 10
    kit.estacion(pantalla, cx, cy, t, pixel=3, luces=False)
    kit.frente_de_la_marea(pantalla, zona, cx + 10 + math.sin(t / 60) * 6, t, hacia="derecha")
    azar = random.Random(72)
    for i in range(14):         # los pedazos que se desprenden y se alejan
        x = cx + 30 + azar.randint(0, 60) + t * azar.uniform(0.05, 0.25)
        y = cy + azar.randint(-70, 70) + math.sin(t / 50 + i) * 6
        pantalla.fill((150, 156, 190) if i % 3 else (28, 56, 130), (g(x), g(y), azar.choice((4, 6, 8)), 4))
    for i in range(3):
        x = zona.left + 520 + i * 90 + t * 0.6
        y = zona.centery + (i - 1) * 46
        kit.pintar(pantalla, ["XX....", "XXXXX.", "XXXXXX", "XXXXX.", "XX...."], {"X": (190, 196, 220)}, x, y, 4)
        pantalla.fill(NARANJA, (g(x) - 20, g(y) - 2, 6, 4))


@cuadro("agujero_negro", "ABISMO AZUL")
def agujero_negro(pantalla, zona, t, paso, datos):
    # El agujero negro y, desde el segundo renglon, dos relojes: el de cerca del borde casi no
    # se mueve; el de lejos vuela
    kit.estrellas(pantalla, zona, 73, 140)
    cx, cy = zona.centerx, zona.centery + 6
    kit.agujero_negro(pantalla, cx, cy, 56, t)
    if paso >= 1:
        kit.reloj(pantalla, cx + 120, cy - 70, 26, t * 0.002, HIELO)
        rotulo(pantalla, "CERCA", cx + 120, cy - 24, HIELO)
        kit.reloj(pantalla, zona.right - 120, cy, 46, t * 0.2, AMARILLO)
        rotulo(pantalla, "LEJOS", zona.right - 120, cy + 70, AMARILLO)


@cuadro("anillo", "EL ANILLO")
def anillo(pantalla, zona, t, paso, datos):
    # El anillo de rocas alrededor del agujero; monedas y ladrones van todos hacia adentro
    kit.estrellas(pantalla, zona, 74, 120)
    cx, cy = zona.centerx + 120, zona.centery + 10
    kit.agujero_negro(pantalla, cx, cy, 30, t)
    asteroides_del_anillo(pantalla, cx, cy, 170, t)
    azar = random.Random(75)
    for i in range(10):         # lo que cae hacia el centro, en espiral
        fase = (t * 0.003 + i / 10) % 1
        a = azar.uniform(0, math.tau) + fase * 3
        r = 420 * (1 - fase) + 40
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r * 0.34
        if i % 4 == 0:
            kit.enemigo(pantalla, "ladron", x, y, t)
        else:
            pantalla.fill(AMARILLO, (g(x) - 2, g(y) - 2, 4, 4))


@cuadro("descenso_lejos", "ABISMO AZUL")
def descenso_lejos(pantalla, zona, t, paso, datos):
    # La Alondra va hacia el borde. La radio de Ines llega estirada: amarilla de su lado y cada
    # vez mas roja del lado de Alba (la gravedad le estira el tiempo)
    kit.estrellas(pantalla, zona, 76, 100)
    cx, cy = zona.right - 170, zona.centery + 20
    kit.agujero_negro(pantalla, cx, cy, 50, t)
    f = kit.avance(t, 0, 400)
    x = zona.left + 220 + (cx - 140 - zona.left - 220) * f
    y = zona.centery - 40 + (cy - zona.centery + 30) * f
    largo = math.hypot(x - zona.left - 30, y - zona.top - 30)
    pasos = int(largo / 6)
    for i in range(pasos):
        k = i / max(1, pasos)
        px = zona.left + 30 + (x - zona.left - 30) * k
        py = zona.top + 30 + (y - zona.top - 30) * k
        if (i + t // 3) % 3:
            pantalla.fill(mezclar(AMARILLO, ROJO, k), (g(px), g(py), 2, 2))
    kit.alondra(pantalla, x, y, t, escala=2 if f < 0.5 else 1, mira="derecha")


@cuadro("anillo_abierto", "EL ANILLO")
def anillo_abierto(pantalla, zona, t, paso, datos):
    # Las rocas se apartan y por el hueco sale la luz de adentro
    kit.estrellas(pantalla, zona, 77, 120)
    cx, cy = zona.centerx, zona.centery + 10
    hueco = kit.avance(t, 10, 150)
    kit.agujero_negro(pantalla, cx, cy, 34, t)
    if hueco > 0.2:
        for i, color in enumerate((mezclar(HIELO, NOCHE, 0.6), mezclar(HIELO, NOCHE, 0.3), BLANCO)):
            mitad = g(30 * hueco * (1 - i * 0.3))
            pantalla.fill(color, (g(cx) - mitad, g(cy) + 40, mitad * 2, zona.bottom - g(cy) - 40))
    asteroides_del_anillo(pantalla, cx, cy, 200, t, hueco=hueco)


@cuadro("refugio", "EL BORDE")
def refugio(pantalla, zona, t, paso, datos):
    # De cerca, el borde del agujero: una franja de luz que gira, una estacion violeta pegada a
    # ella y miles de monedas en orbita. La Alondra baja
    kit.estrellas(pantalla, pygame.Rect(zona.left, zona.top, zona.width, 120), 78, 60)
    horizonte = zona.bottom - 50
    for i, (color, alto) in enumerate(((mezclar(HIELO, NOCHE, 0.6), 40), (HIELO, 18), (BLANCO, 6))):
        y = horizonte - alto // 2 - 10
        for x in range(zona.left, zona.right, 4):
            onda = math.sin(x / 40 + t / 20 + i) * 4
            pantalla.fill(color, (x, g(y + onda), 4, g(alto)))
    pantalla.fill((0, 0, 0), (zona.left, horizonte, zona.width, zona.bottom - horizonte))
    azar = random.Random(79)
    for i in range(160):        # las monedas en orbita, en elipses a distintas alturas
        r = azar.uniform(0.2, 1.0)
        a = azar.uniform(0, math.tau) + t * 0.01 / r
        x = zona.centerx + math.cos(a) * zona.width * 0.55 * r
        y = horizonte - 60 - r * 90 + math.sin(a) * 14
        pantalla.fill(AMARILLO if i % 5 else BLANCO, (g(x), g(y), 2, 2))
    estacion = ["....XX....", "...XXXX...", "..XoXXoX..", "XXXXXXXXXX", "..XXXXXX..", "...X..X..."]
    sx, sy = zona.centerx + 160, horizonte - 40
    kit.pintar(pantalla, estacion, {"X": (110, 70, 180), "o": (255, 236, 255)}, sx, sy, 6)
    dibujo.halo(pantalla, sx, sy, 50, VIOLETA)
    baja = kit.avance(t, 0, 300)
    kit.alondra(pantalla, zona.centerx - 120 + baja * 200, zona.top + 40 + baja * 120, t, escala=1, mira="abajo",
                llama=0.4)
    if paso >= 1:       # "HAY ALGUIEN": una figura en la ventana de la estacion
        kit.pintar(pantalla, kit.RETRATO_ULTIMO_SILUETA, {"X": VIOLETA}, sx, sy - 70, 2)


@cuadro("el_ultimo", "EL REFUGIO", sonido="fragmento")
def el_ultimo(pantalla, zona, t, paso, datos):
    # El Ultimo sale de la oscuridad: su retrato aparece de arriba hacia abajo, los ojos primero
    kit.estrellas(pantalla, zona, 80, 40)
    kit.brasas(pantalla, zona, t // 2, [(220, 180, 255), VIOLETA, (80, 50, 140)], cuantas=30, semilla=81)
    pixel = 16
    x, y = zona.centerx - 6 * pixel, zona.centery - 6 * pixel + 8
    filas = min(12, t // 8)
    lienzo = pygame.Surface((12 * pixel, 12 * pixel))
    lienzo.fill(NOCHE)
    kit.retrato(lienzo, "ultimo", 0, 0, pixel)
    if filas:
        pantalla.blit(lienzo, (g(x), g(y)), (0, 0, 12 * pixel, filas * pixel))
    if t > 30:      # los ojos, que brillan (una vez que se lo ve)
        dibujo.halo(pantalla, x + 3.5 * pixel, y + 4.5 * pixel, 20, VIOLETA, 0.4 + 0.3 * math.sin(t / 40))
        dibujo.halo(pantalla, x + 7.5 * pixel, y + 4.5 * pixel, 20, VIOLETA, 0.4 + 0.3 * math.sin(t / 40))
    if paso >= 3:       # "SOY EL ULTIMO DE LOS MIOS"
        rotulo(pantalla, "EL ULTIMO DE LOS SUYOS", zona.centerx, zona.bottom - 22, VIOLETA)


@cuadro("galaxia_perdida", "HACE MILLONES DE AÑOS")
def galaxia_perdida(pantalla, zona, t, paso, datos):
    # Su galaxia (violeta) y la Marea que llega y la deshace. Una chispa sola escapa hacia arriba
    kit.estrellas(pantalla, zona, 82, 70)
    tiron = kit.avance(t, 30, 400)
    kit.galaxia(pantalla, zona.centerx - 100, zona.centery, 140, t * 0.004, SUYA, 83, estirar=tiron)
    x = zona.right - 140 - tiron * 160
    if tiron > 0.3:     # el frente de la Marea pasa por encima de lo que se traga
        kit.frente_de_la_marea(pantalla, zona, zona.right - (tiron - 0.3) * zona.width, t)
    kit.nube(pantalla, x, zona.centery - 10, 50, MAREA, 84)
    if t > 200:
        f = kit.avance(t, 200, 200)
        sx, sy = zona.centerx - 100 + f * 40, zona.centery - f * 120
        pantalla.fill(BLANCO, (g(sx) - 2, g(sy) - 2, 4, 4))
        dibujo.halo(pantalla, sx, sy, 14, VIOLETA)


@cuadro("posta", "UN CAMINO HASTA AQUI")
def posta(pantalla, zona, t, paso, datos):
    # Una fila de galaxias. Una chispa violeta va de una a otra dejando monedas, y la Marea la
    # sigue: las que quedan atras se apagan
    kit.estrellas(pantalla, zona, 85, 70)
    centros = [zona.left + 110 + i * (zona.width - 220) / 4 for i in range(5)]
    vuelta = 900
    momento = t % vuelta
    viaje = momento / vuelta * (len(centros) - 0.6)
    frente = zona.left + (viaje - 1.1) * (zona.width - 220) / 4 + 110
    for i, cx in enumerate(centros):
        colores = NUESTRA if i == len(centros) - 1 else SUYA if i == 0 else [mezclar(c, HIELO, 0.4) for c in SUYA]
        tragada = cx < frente
        if tragada:
            colores = [mezclar(c, (60, 10, 30), 0.7) for c in colores]
        kit.galaxia(pantalla, cx, zona.centery + (i % 2) * 20 - 10, 56, t * 0.004 + i, colores, 90 + i, puntos=260)
    kit.frente_de_la_marea(pantalla, zona, max(zona.left, frente), t, hacia="derecha")
    hasta = int(viaje)
    f = viaje - hasta
    x = centros[min(hasta, 4)] + (centros[min(hasta + 1, 4)] - centros[min(hasta, 4)]) * f
    y = zona.centery - 60 - math.sin(f * math.pi) * 40
    for k in range(1, 8):       # las monedas que deja detras
        mx = x - k * 18
        if mx > max(zona.left, frente) + 10:
            pantalla.fill(AMARILLO, (g(mx), g(zona.centery - 60 - math.sin(((x - mx) / 200) * math.pi) * 10), 2, 2))
    pantalla.fill(BLANCO, (g(x) - 2, g(y) - 2, 4, 4))
    dibujo.halo(pantalla, x, y, 16, VIOLETA)
    rotulo(pantalla, "NOSOTROS", centros[-1], zona.bottom - 24, (110, 170, 255))


@cuadro("una_hora", "EL BORDE")
def una_hora(pantalla, zona, t, paso, datos):
    # Mas abajo, en el borde mismo, una hora. Arriba pasan mil años: la Marea cruza y se va, y las
    # estrellas quedan quietas otra vez
    kit.estrellas(pantalla, zona, 86, 90)
    pasa = kit.avance(t, 60, 360)
    borde = zona.right - (zona.width + 300) * pasa
    if 0 < pasa < 1:
        kit.frente_de_la_marea(pantalla, pygame.Rect(zona.left, zona.top, zona.width, 90), borde, t)
    pantalla.fill((0, 0, 0), (zona.left, zona.bottom - 60, zona.width, 60))
    pantalla.fill(HIELO, (zona.left, zona.bottom - 62, zona.width, 2))
    kit.reloj(pantalla, zona.left + 220, zona.centery + 20, 60, t * 0.0008, HIELO)
    rotulo(pantalla, "MAS ABAJO", zona.left + 220, zona.centery + 104, HIELO)
    anios = int(1000 * kit.avance(t, 0, 420))
    kit.texto_grande(pantalla, "%d AÑOS" % anios, AMARILLO, zona.right - 240, zona.centery + 16, escala=3)
    rotulo(pantalla, "ARRIBA", zona.right - 240, zona.centery + 72, AMARILLO)


@cuadro("mateo_vivo", "EL REFUGIO")
def mateo_vivo(pantalla, zona, t, paso, datos):
    # Mateo, vivo y con color (por la radio siempre fue gris), y la capsula de la Errante
    kit.estrellas(pantalla, zona, 87, 50)
    x, y = zona.left + 120, zona.top + 48
    lienzo_retrato(pantalla, MATEO_VIVO, x, y, 14)
    kit.capsula(pantalla, zona.left + 660, zona.centery, 12, t=t)
    rotulo(pantalla, "LA CAPSULA DE LA ERRANTE", zona.left + 660, zona.bottom - 30, TEXTO_SUAVE)
    rotulo(pantalla, "MATEO, ROCIO Y TOMAS", x + 84, zona.bottom - 18, TEXTO)


def lienzo_retrato(pantalla, retrato, x, y, pixel):
    # Un retrato de personajes.py dibujado con otra paleta (sin tocar el original)
    pantalla.fill((8, 10, 26), (g(x), g(y), 12 * pixel, 12 * pixel))
    for fila, renglon in enumerate(retrato["dibujo"]):
        for columna, letra in enumerate(renglon):
            color = retrato["paleta"].get(letra)
            if color is not None:
                pantalla.fill(color, (g(x) + columna * pixel, g(y) + fila * pixel, pixel, pixel))


@cuadro("vengan", "ESTACION UMBRAL")
def vengan(pantalla, zona, t, paso, datos):
    # La Umbral se vacia: las naves salen de a una hacia el Abismo. Arriba, la palabra nueva
    kit.estrellas(pantalla, zona, 88, 100)
    caja = kit.estacion(pantalla, zona.left + 150, zona.centery + 66, t, pixel=3)
    for i in range(12):
        sale = i * 40
        if t < sale:
            continue
        f = (t - sale) * 0.004
        x = caja.centerx + 60 + f * 700
        y = caja.centery + (i % 3 - 1) * 30 - f * 40
        if x > zona.right + 20:
            continue
        kit.pintar(pantalla, ["XX..", "XXXX", "XX.."], {"X": (190, 196, 220)}, x, y, 4)
        pantalla.fill(NARANJA, (g(x) - 14, g(y) - 2, 6, 4))
    glifo_grande(pantalla, "VENGAN", zona.centerx + 60, zona.top + 60, VIOLETA, traducidas=min(6, max(0, (t - 30) // 20)))


@cuadro("vengan_tarde", "LO QUE QUEDA")
def vengan_tarde(pantalla, zona, t, paso, datos):
    # Tarde: tres naves escapan de la Marea hacia el Abismo
    kit.estrellas(pantalla, zona, 89, 100)
    kit.frente_de_la_marea(pantalla, zona, zona.left + 140 + t * 0.15, t, hacia="derecha")
    for i in range(3):
        x = zona.left + 300 + i * 70 + t * 0.4
        y = zona.centery + 50 + (i - 1) * 36
        kit.pintar(pantalla, ["XX..", "XXXX", "XX.."], {"X": (190, 196, 220)}, x, y, 6)
        pantalla.fill(NARANJA, (g(x) - 20, g(y) - 2, 8, 4))
    glifo_grande(pantalla, "VENGAN", zona.centerx + 100, zona.top + 60, VIOLETA, traducidas=6)


@cuadro("primera_bitacora", "SIN FECHA")
def primera_bitacora(pantalla, zona, t, paso, datos):
    # El cielo de su planeta, millones de años antes: dos soles y monedas que brillan. Y el, joven
    for i, color in enumerate(((40, 20, 70), (70, 30, 90), (110, 50, 100))):
        pantalla.fill(color, (zona.left, zona.top + 80 + i * 50, zona.width, 50))
    kit.estrellas(pantalla, pygame.Rect(zona.left, zona.top, zona.width, 80), 91, 30)
    kit.disco(pantalla, zona.right - 200, zona.top + 110, 30, (255, 230, 200))
    kit.disco(pantalla, zona.right - 120, zona.top + 150, 18, (255, 180, 220))
    for i in range(6):
        x = zona.left + 340 + i * 80
        y = zona.top + 60 + (i % 2) * 30 + kit.vaiven(t + i * 30, 180, 4)
        kit.moneda(pantalla, x, y, t + i * 4)
    pantalla.fill((20, 10, 30), (zona.left, zona.bottom - 50, zona.width, 50))
    kit.retrato(pantalla, "voz", zona.left + 60, zona.top + 60, 12, VIOLETA)


@cuadro("relevo", "EL PRINCIPIO")
def relevo(pantalla, zona, t, paso, datos):
    # La Alondra sale delante de la Marea, hacia la galaxia que sigue, dejando monedas detras
    kit.estrellas(pantalla, zona, 92, 110)
    kit.frente_de_la_marea(pantalla, zona, zona.left + 60 + math.sin(t / 50) * 6, t, hacia="derecha")
    kit.galaxia(pantalla, zona.right - 130, zona.centery - 10, 90, t * 0.004, [mezclar(c, AMARILLO, 0.3) for c in NUESTRA],
                93, puntos=400)
    x = zona.left + 360 + kit.avance(t, 0, 300) * 120
    y = zona.centery + 20 + kit.vaiven(t, 160, 4)
    for k in range(1, 9):
        mx = x - 40 - k * 28
        if mx > zona.left + 80:
            kit.moneda(pantalla, mx, y + math.sin(k) * 10, t + k * 5)
    kit.alondra(pantalla, x, y, t, escala=2, mira="derecha")
    if paso >= 3:       # "QUIERE DECIR AMANECER": la galaxia que sigue se ilumina
        dibujo.halo(pantalla, zona.right - 130, zona.centery - 10, 140, AMARILLO, 0.8)

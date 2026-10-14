"""
Gasolinera espacial: la parada despues de cada jefe (lo que se vende esta en tienda.py).

Usa todo el ancho:
- Arriba, los creditos (cuentan hacia abajo al gastar), el nombre y a donde vas.
- La estacion "LA ULTIMA GOTA" sobre una plataforma de lado a lado: el cartel de neon,
  el vendedor en la ventana y el surtidor cargando combustible en tu nave.
- El mostrador: una carta por articulo (interfaz.carta) con su precio abajo; la elegida
  sube y brilla, lo vendido lleva un sello.
- Abajo, el detalle de lo elegido: que hace, cuanto cuesta y cuanto te queda o te falta.

    IZQ/DER   elegir
    ENTER     comprar (se puede comprar todo lo que alcance)
    ESC       seguir viaje al sector nuevo (lo que no gastes queda para la proxima)

El juego queda quieto mientras tanto, como en el Taller. Todo se dibuja con codigo
(rectangulos y pixel art): no usa sprites nuevos, salvo la nave de siempre.
"""
import math
import random

import pygame

from juego import dibujo, nave, hud, recursos, interfaz
from juego.dibujo import texto, MINI, CHICA, MEDIA
from juego.config import (ANCHO, CENTRO_X, ANCHO_MENU, FONDO, BLANCO, GRIS, AMARILLO, CIAN, MAGENTA, ROJO, VERDE,
                          NARANJA, ORO, TEXTO_SUAVE)
from juego.efectos import Efectos
from juego.entrada import ACEPTAR, VOLVER, IZQUIERDA, DERECHA
from juego.escenas.base import Escena
from juego.sonido import SILENCIO
from juego.tienda import Tienda
from juego.config import SECTORES

PASOS_SIN_ELEGIR = 30       # pasos (medio segundo) en que se ignoran las teclas
PASOS_ENTRE_CARTAS = 4      # cada carta cae este numero de pasos despues de la anterior
PASOS_TANQUE = 150          # pasos que tarda en llenarse el tanque de la nave
PASOS_TEMBLOR = 14          # pasos que tiembla una carta si no se puede comprar

ANCHO_CARTA, ALTO_CARTA = 140, 184
SEPARACION = 14
ARRIBA_CARTAS = 262         # y de las cartas del mostrador
DETALLE = pygame.Rect(48, 462, ANCHO - 96, 88)      # el panel de abajo con lo elegido
ANCHO_DESCRIPCION = 680     # la descripcion, a la izquierda del precio

# La estacion se dibuja en su propia imagen de 800 de ancho (sus coordenadas de siempre)
# y se pega centrada y un poco mas arriba
PISO_Y = 262                # el piso de la estacion (en la imagen de la estacion)
SUBIDA_ESTACION = 40        # cuanto mas arriba se pega en la pantalla
ESTACION_X = (ANCHO - ANCHO_MENU) // 4 * 2        # (par: la grilla de pixeles de arte)

# Colores del metal (oscuro -> claro)
BORDE = (16, 16, 36)
ACERO = (44, 48, 86)
ACERO_CLARO = (90, 100, 150)
PANEL = (30, 32, 62)
APAGADO = (60, 60, 90)

VENDEDOR = [".XXXXX.",
            "X.....X",
            "X.X.X.X",
            "X.....X",
            "X.XXX.X",
            ".XXXXX.",
            "..X.X.."]


class Gasolinera(Escena):
    ambiente = SILENCIO
    musica = "gasolinera"

    def __init__(self, app, escena_juego):
        super().__init__(app)
        self.escena_juego = escena_juego
        self.partida = escena_juego.partida
        self.tienda = Tienda(self.partida)
        self.elegido = 0                    # indice en tienda.articulos()
        self.cursor = interfaz.Cursor(0)    # donde se ve "levantada" la carta (se desliza)
        self.pasos = 0                      # pasos desde que se abrio (animaciones)
        self.desde_sorteo = 0               # paso del ultimo sorteo (las cartas vuelven a caer)
        self.temblor = 0                    # pasos que le quedan al temblor de la elegida
        self.creditos_visibles = self.partida.creditos      # los del encabezado: cuentan de a poco
        self.paso_compra = -100             # cuando se compro algo (el numero destella)
        self.efectos = Efectos()            # propios: las particulas del juego quedan quietas
        self.estacion = pygame.Surface((ANCHO_MENU, 300), pygame.SRCALPHA)
        app.sonidos.reproducir("tienda")
        app.sonidos.reproducir_luego("surtidor", 300)      # el tanque se llena (PASOS_TANQUE)
        self.neon_apagado = False

    def elegido_actual(self):
        return self.tienda.articulos()[self.elegido]

    # ---------- Logica ----------

    def actualizar(self, entrada):
        self.mover_fondo()
        self.efectos.actualizar()
        self.cursor.avanzar()
        self.pasos += 1
        if self.temblor > 0:
            self.temblor -= 1
        # Los creditos del encabezado cuentan hacia los de verdad
        diferencia = self.partida.creditos - self.creditos_visibles
        if diferencia:
            paso = max(1, abs(diferencia) // 5)
            self.creditos_visibles += paso if diferencia > 0 else -paso
        self._sonar_cartas_que_caen()
        self._sonar_neon()
        if self.pasos < PASOS_SIN_ELEGIR:
            return
        cantidad = len(self.tienda.articulos())
        if entrada.pulso(VOLVER):
            self._seguir_viaje()
        elif entrada.pulso(IZQUIERDA) and cantidad:
            self._elegir((self.elegido - 1) % cantidad)
        elif entrada.pulso(DERECHA) and cantidad:
            self._elegir((self.elegido + 1) % cantidad)
        elif entrada.pulso(ACEPTAR) and cantidad:
            self._comprar()

    def _sonar_neon(self):
        # El cartel GAS titila (_dibujar_cartel, con el mismo reloj): cuando vuelve a prender, zumba
        ticks = pygame.time.get_ticks()
        apagado = ticks % 2600 < 90 or 300 < ticks % 2600 < 360
        if self.neon_apagado and not apagado:
            self.app.sonidos.reproducir("neon")
        self.neon_apagado = apagado

    def _sonar_cartas_que_caen(self):
        # Cada articulo que cae al mostrador suena (como en _dibujar_carta: las cartas despues
        # de cada sorteo, los servicios una vez), una nota mas arriba cada uno
        for indice, articulo in enumerate(self.tienda.articulos()):
            desde = self.desde_sorteo if articulo in self.tienda.cartas else 0
            if self.pasos - desde - indice * PASOS_ENTRE_CARTAS == 1:     # (pasos ya sumo este paso)
                self.app.sonidos.reproducir("carta_%d" % min(indice + 1, 6))

    def _elegir(self, indice):
        self.elegido = indice
        self.cursor.ir_a(indice)
        self.app.sonidos.reproducir("ui_mover")

    def _comprar(self):
        articulo = self.elegido_actual()
        cartas_antes = self.tienda.cartas
        precio = articulo.precio(self.tienda)
        if not self.tienda.comprar(articulo):
            # No alcanza (o ya esta vendido): la carta tiembla
            self.temblor = PASOS_TEMBLOR
            self.app.sonidos.reproducir("ui_error")
            self.app.sonidos.reproducir_luego("vendedor_no", 120)
            return
        # "Ka-ching" y lo que compraste: la carta (y su sello de VENDIDA), el escudo, la vida
        # o el mazo que se baraja
        self.app.sonidos.reproducir("caja")
        tipo = getattr(articulo, "tipo", None)
        if tipo == "sortear":
            self.app.sonidos.reproducir_luego("barajar", 150)
        elif tipo == "escudo":
            self.app.sonidos.reproducir_luego("pw_escudo", 150)
        elif tipo == "reparar":
            self.app.sonidos.reproducir_luego("pw_vida", 150)
        else:
            self.app.sonidos.reproducir_luego("mejora_elegida", 120)
            self.app.sonidos.reproducir_luego("sello", 420)
        self.app.entrada.vibrar("mejora")
        self.paso_compra = self.pasos
        carta_x, carta_y = self._centro_carta(self.elegido)
        self.efectos.anillo(carta_x, carta_y, [(60, 40, 0), articulo.color, BLANCO], 24, 5)
        self.efectos.explosion(carta_x, carta_y, ORO, 16, 4, 3)
        self.efectos.texto_flotante("-" + str(precio), carta_x, ARRIBA_CARTAS - 14, AMARILLO)
        nave_x, nave_y = self._centro_nave()
        self.efectos.anillo(nave_x + ESTACION_X, nave_y - SUBIDA_ESTACION, [(40, 40, 60), articulo.color, BLANCO],
                            24, 4)
        if self.tienda.cartas is not cartas_antes:
            # Se sortearon cartas nuevas: vuelven a caer (y pueden ser menos que antes)
            self.desde_sorteo = self.pasos
            self.elegido = min(self.elegido, len(self.tienda.articulos()) - 1)
            self.cursor.saltar_a(self.elegido)

    def _seguir_viaje(self):
        self.partida.director.gasolinera = False
        self.app.fondo.saltar_al_hiperespacio()     # rumbo al sector nuevo
        self.app.sonidos.reproducir("ui_volver")
        self.app.sonidos.reproducir("hiperespacio")
        # Y al llegar, el acorde del sector nuevo (con su cartel)
        numero = SECTORES.index(self.partida.director.sector) + 1
        self.app.sonidos.reproducir_luego("sector_nuevo_%d" % numero, 700)
        self.app.cambiar_escena(self.escena_juego)

    # ---------- Dibujo ----------

    def dibujar(self, pantalla):
        self.dibujar_fondo(pantalla)
        self._dibujar_encabezado(pantalla)
        self._dibujar_piso(pantalla, PISO_Y - SUBIDA_ESTACION)
        self.estacion.fill((0, 0, 0, 0))
        self._dibujar_estacion(self.estacion)
        pantalla.blit(self.estacion, (ESTACION_X, -SUBIDA_ESTACION))
        self._dibujar_mostrador(pantalla)
        self._dibujar_detalle(pantalla)
        self.efectos.dibujar(pantalla)
        if self.pasos >= PASOS_SIN_ELEGIR:
            interfaz.ayudas(pantalla, self.app.entrada, [("cambiar", "ELEGIR"), ("aceptar", "COMPRAR"),
                                                         ("volver", "SEGUIR VIAJE")])

    def _dibujar_encabezado(self, pantalla):
        # Creditos (izquierda), el nombre (centro) y a donde vas (derecha)
        texto(pantalla, "CREDITOS", MINI, TEXTO_SUAVE, 48, 16, alinear="izquierda")
        hud.icono_credito(pantalla, 58, 40)
        recien = self.pasos - self.paso_compra < 12
        texto(pantalla, str(self.creditos_visibles), MEDIA, BLANCO if recien else AMARILLO, 76, 41,
              alinear="izquierda")
        dibujo.texto_3d(pantalla, "GASOLINERA", MEDIA, AMARILLO, MAGENTA, 26, 3)
        texto(pantalla, "ESTELAR", MINI, CIAN, CENTRO_X, 50)
        director = self.partida.director
        texto(pantalla, "PROXIMO", MINI, TEXTO_SUAVE, ANCHO - 48, 16, alinear="derecha")
        texto(pantalla, "SECTOR " + str(director.numero_sector), MEDIA, director.sector["color"], ANCHO - 48, 41,
              alinear="derecha")
        texto(pantalla, "LO QUE NO GASTES QUEDA PARA LA PROXIMA", MINI, TEXTO_SUAVE, ANCHO - 48, 64, alinear="derecha")

    # ----- La estacion (se dibuja en self.estacion, con sus coordenadas de 800 de ancho) -----

    def _dibujar_estacion(self, estacion):
        self._dibujar_edificio(estacion)
        self._dibujar_cartel(estacion)
        self._dibujar_surtidor(estacion)
        self._dibujar_manguera(estacion)
        self._dibujar_nave(estacion)
        self._dibujar_tanque(estacion)

    def _dibujar_piso(self, pantalla, piso_y):
        # Una plataforma de metal de lado a lado, con remaches y luces que se prenden en ola
        pantalla.fill(BORDE, (0, piso_y, ANCHO, 24))
        pantalla.fill(PANEL, (0, piso_y + 4, ANCHO, 16))
        pantalla.fill(ACERO_CLARO, (0, piso_y, ANCHO, 4))
        for remache_x in range(24, ANCHO, 32):
            pantalla.fill(ACERO_CLARO, (remache_x, piso_y + 10, 4, 4))
        for i, luz_x in enumerate(range(32, ANCHO, 64)):
            prendida = (self.pasos // 8 - i) % 17 == 0
            pantalla.fill(AMARILLO if prendida else (70, 50, 0), (luz_x, piso_y + 20, 8, 4))

    def _dibujar_edificio(self, pantalla):
        # La tienda: techo, ventana con el vendedor (un robot que parpadea) y la puerta
        pantalla.fill(BORDE, (66, 144, 244, PISO_Y - 144))
        pantalla.fill(ACERO, (70, 152, 236, PISO_Y - 152))
        pantalla.fill(ACERO_CLARO, (58, 140, 260, 8))           # techo
        pantalla.fill(BORDE, (58, 148, 260, 4))
        # Antena con su luz roja
        pantalla.fill(ACERO_CLARO, (286, 100, 4, 40))
        if dibujo.parpadeo(500):
            pantalla.fill(ROJO, (284, 94, 8, 8))
        # Ventana con el vendedor
        ventana = pygame.Rect(88, 172, 96, 60)
        pantalla.fill(BORDE, ventana.inflate(8, 8))
        pantalla.fill((0, 50, 80), ventana)
        pantalla.fill((0, 90, 130), (ventana.left, ventana.top, ventana.width, 8))     # reflejo
        dibujo.pixel_art(pantalla, VENDEDOR, ventana.centerx, ventana.centery + 6, CIAN, 4)
        ojos_cerrados = (pygame.time.get_ticks() // 100) % 30 == 0
        for ojo_x in (ventana.centerx - 8, ventana.centerx + 8):
            alto_ojo = 2 if ojos_cerrados else 6
            pantalla.fill(AMARILLO, (ojo_x - 2, ventana.centery - 2, 4, alto_ojo))
        # Puerta con su lucecita
        pantalla.fill(BORDE, (214, 192, 56, PISO_Y - 192))
        pantalla.fill(PANEL, (218, 196, 48, PISO_Y - 196))
        pantalla.fill(VERDE if dibujo.parpadeo(700) else (0, 90, 40), (256, 222, 4, 4))
        texto(pantalla, "LA ULTIMA GOTA", MINI, CIAN, 188, 162)

    def _dibujar_cartel(self, pantalla):
        # Cartel de neon arriba del techo: "GAS" (cada tanto titila, como los de verdad)
        ticks = pygame.time.get_ticks()
        apagado = ticks % 2600 < 90 or 300 < ticks % 2600 < 360
        color = (70, 0, 50) if apagado else MAGENTA
        cartel = pygame.Rect(96, 86, 152, 46)
        pantalla.fill(BORDE, cartel)
        pygame.draw.rect(pantalla, color, cartel, 2)
        pygame.draw.rect(pantalla, color, cartel.inflate(-8, -8), 2)
        texto(pantalla, "GAS", MEDIA, (70, 70, 90) if apagado else AMARILLO, cartel.centerx - 22, cartel.centery + 1,
              sombra=None)
        texto(pantalla, "24H", MINI, (0, 70, 110) if apagado else CIAN, cartel.right - 30, cartel.centery + 1,
              sombra=None)
        # Patas del cartel
        for pata_x in (120, 220):
            pantalla.fill(ACERO_CLARO, (pata_x, cartel.bottom, 4, 8))

    def _dibujar_surtidor(self, pantalla):
        # El surtidor: cuerpo naranja, pantallita con los litros y la luz de arriba
        cuerpo = pygame.Rect(360, 168, 48, PISO_Y - 168)
        pantalla.fill(BORDE, cuerpo.inflate(8, 8))
        pantalla.fill(NARANJA, cuerpo)
        pantalla.fill((150, 70, 0), (cuerpo.left, cuerpo.bottom - 16, cuerpo.width, 16))
        pantalla.fill(BORDE, (cuerpo.left + 6, cuerpo.top + 10, 36, 20))
        litros = int(self.tanque() * 99)
        texto(pantalla, str(litros).zfill(2), MINI, VERDE, cuerpo.centerx, cuerpo.top + 20, sombra=None)
        pantalla.fill(BORDE, (cuerpo.left + 10, cuerpo.top + 40, 28, 4))
        pantalla.fill(BORDE, (cuerpo.left + 10, cuerpo.top + 50, 28, 4))
        luz = VERDE if self.tanque() >= 1 else (ROJO if dibujo.parpadeo(200) else (90, 0, 20))
        pantalla.fill(luz, (cuerpo.centerx - 6, cuerpo.top - 10, 12, 6))

    def _dibujar_manguera(self, pantalla):
        # Una manguera que cuelga (una curva de cuadraditos) del surtidor a la nave
        desde_x, desde_y = 412, 214
        hasta_x, hasta_y = self._centro_nave()[0] - 30, PISO_Y - 26
        for paso in range(25):
            avance = paso / 24
            punto_x = desde_x + (hasta_x - desde_x) * avance
            punto_y = desde_y + (hasta_y - desde_y) * avance + math.sin(math.pi * avance) * 26
            pantalla.fill((24, 24, 40), (int(punto_x) // 2 * 2, int(punto_y) // 2 * 2, 6, 6))
        # El combustible que viaja por la manguera mientras carga
        if self.tanque() < 1:
            avance = (self.pasos % 20) / 20
            punto_x = desde_x + (hasta_x - desde_x) * avance
            punto_y = desde_y + (hasta_y - desde_y) * avance + math.sin(math.pi * avance) * 26
            pantalla.fill(VERDE, (int(punto_x) // 2 * 2 + 2, int(punto_y) // 2 * 2 + 2, 2, 2))

    def _centro_nave(self):
        # (en las coordenadas de la imagen de la estacion)
        flotar = round(math.sin(pygame.time.get_ticks() / 400)) * 2
        return 560, PISO_Y - 52 + flotar

    def _dibujar_nave(self, pantalla):
        # Tu nave (el doble de grande, sin suavizar) estacionada sobre la plataforma
        imagen = nave.imagen("nave")
        grande = pygame.transform.scale(imagen, (imagen.get_width() * 2, imagen.get_height() * 2))
        pantalla.blit(grande, grande.get_rect(center=self._centro_nave()))

    def tanque(self):
        # Cuanto se lleno el tanque (0 a 1)
        return min(1, self.pasos / PASOS_TANQUE)

    def _dibujar_tanque(self, pantalla):
        # El medidor de combustible, al lado de la nave
        medidor = pygame.Rect(640, 160, 20, 92)
        texto(pantalla, "TANQUE", MINI, GRIS, medidor.centerx, medidor.top - 10)
        pygame.draw.rect(pantalla, GRIS, medidor, 2)
        bloques = int(self.tanque() * 21)
        for i in range(bloques):
            color = VERDE if self.tanque() >= 1 else AMARILLO
            pantalla.fill(color, (medidor.left + 4, medidor.bottom - 6 - i * 4, 12, 2))
        if self.tanque() >= 1 and dibujo.parpadeo(300):
            texto(pantalla, "LLENO", MINI, VERDE, medidor.centerx + 46, medidor.centery)

    # ----- El mostrador -----

    def _x_carta(self, indice):
        cantidad = len(self.tienda.articulos())
        ancho_total = cantidad * ANCHO_CARTA + (cantidad - 1) * SEPARACION
        return CENTRO_X - ancho_total // 2 + indice * (ANCHO_CARTA + SEPARACION)

    def _centro_carta(self, indice):
        return self._x_carta(indice) + ANCHO_CARTA // 2, ARRIBA_CARTAS + ALTO_CARTA // 2

    def _dibujar_mostrador(self, pantalla):
        articulos = self.tienda.articulos()
        if not articulos:
            texto(pantalla, "NO QUEDA NADA PARA VENDER", CHICA, GRIS, CENTRO_X, ARRIBA_CARTAS + 60)
            return
        for indice, articulo in enumerate(articulos):
            self._dibujar_carta(pantalla, indice, articulo)

    def _dibujar_carta(self, pantalla, indice, articulo):
        # Cae desde arriba (las cartas despues de cada sorteo, los servicios una vez). La
        # elegida sube (de a poco, siguiendo al cursor) y brilla
        es_carta = articulo in self.tienda.cartas
        desde = self.desde_sorteo if es_carta else 0
        pasos_carta = self.pasos - desde - indice * PASOS_ENTRE_CARTAS
        if pasos_carta < 0:
            return
        caida = max(0, 6 - pasos_carta) * 10
        activa = self.pasos >= PASOS_SIN_ELEGIR
        elegida = indice == self.elegido and activa
        x = self._x_carta(indice)
        if elegida and self.temblor:
            x += random.randint(-2, 2) * 2
        subida = round(max(0, 1 - abs(self.cursor.valor - indice)) * 12) // 2 * 2 if activa else 0
        carta = pygame.Rect(x, ARRIBA_CARTAS - caida - subida, ANCHO_CARTA, ALTO_CARTA)
        tienda = self.tienda
        a_la_venta = tienda.a_la_venta(articulo)
        nivel = None
        if es_carta:
            tenes = self.partida.mejora(articulo.tipo)
            nivel = (tenes, articulo.mejora.maximo)
        pie = interfaz.carta(pantalla, carta, articulo.color, articulo.icono, articulo.nombre, (),
                             elegida=elegida, apagada=not a_la_venta, rara=articulo.rara, nivel=nivel)
        if not es_carta:
            texto(pantalla, "SERVICIO", MINI, TEXTO_SUAVE, carta.centerx, carta.top + 116)

        # Abajo: el precio (amarillo si alcanza, rojo si no) o por que no se vende
        if articulo.vendido:
            sello = pygame.Rect(carta.left - 6, carta.top + 44, ANCHO_CARTA + 12, 26)
            pantalla.fill(ROJO, sello)
            pantalla.fill(FONDO, sello.inflate(0, -20))
            texto(pantalla, "VENDIDA", CHICA, BLANCO, sello.centerx, sello.centery + 1)
        elif not a_la_venta:
            texto(pantalla, "NO HACE FALTA", MINI, GRIS, pie.centerx, pie.centery)
        else:
            precio = articulo.precio(tienda)
            color = AMARILLO if tienda.alcanza(articulo) else ROJO
            ancho = recursos.fuente(CHICA).size(str(precio))[0]
            izquierda = pie.centerx - (ancho + 22) // 2
            hud.icono_credito(pantalla, izquierda + 8, pie.centery)
            texto(pantalla, str(precio), CHICA, color, izquierda + 22, pie.centery + 1, alinear="izquierda")

    def _dibujar_detalle(self, pantalla):
        # El panel de abajo: que hace lo elegido, cuanto cuesta y si alcanza la plata
        articulos = self.tienda.articulos()
        if not articulos or self.pasos < PASOS_SIN_ELEGIR:
            return
        articulo = articulos[self.elegido]
        tienda = self.tienda
        adentro = interfaz.panel(pantalla, DETALLE, articulo.color, articulo.nombre)
        descripcion = " ".join(articulo.descripcion)
        for i, linea in enumerate(dibujo.partir_lineas(descripcion, CHICA, ANCHO_DESCRIPCION)[:2]):
            texto(pantalla, linea, CHICA, BLANCO, adentro.left + 4, adentro.top + 4 + i * 22, alinear="izquierda")
        # A la derecha: el precio y como queda la billetera
        derecha = adentro.right - 8
        if articulo.vendido:
            texto(pantalla, "¡COMPRADA!", MEDIA, VERDE, derecha, adentro.top + 14, alinear="derecha")
            return
        if not tienda.a_la_venta(articulo):
            texto(pantalla, "NO HACE FALTA", CHICA, GRIS, derecha, adentro.top + 14, alinear="derecha")
            return
        precio = articulo.precio(tienda)
        alcanza = tienda.alcanza(articulo)
        texto(pantalla, str(precio), MEDIA, AMARILLO if alcanza else ROJO, derecha, adentro.top + 6, alinear="derecha")
        hud.icono_credito(pantalla, derecha - recursos.fuente(MEDIA).size(str(precio))[0] - 16, adentro.top + 5)
        if alcanza:
            resto = "TE QUEDAN " + str(self.partida.creditos - precio)
            texto(pantalla, resto, CHICA, TEXTO_SUAVE, derecha, adentro.top + 30, alinear="derecha")
        else:
            faltan = "TE FALTAN " + str(precio - self.partida.creditos)
            texto(pantalla, faltan, CHICA, ROJO, derecha, adentro.top + 30, alinear="derecha")


"""
Jugando: avanza la partida un frame, con hit-stop y pausa.

Hit-stop: mientras partida.congelar_frames > 0 no se actualiza ni se redibuja
nada (la pantalla queda quieta un instante despues de un impacto).
Si el director ofrece mejoras, se abre el Taller (y al elegir, se vuelve aca); despues
de cada jefe, la Gasolinera (y al seguir viaje, se vuelve aca).
F1 abre el panel del modo desarrollador (si MODO_DESARROLLADOR esta prendido en config).
"""
from juego import hud
from juego.config import MODO_DESARROLLADOR, SECTORES, JEFE_CADA_NIVELES
from juego.sonido import SILENCIO, MUSICAS
from juego.entrada import PAUSA, DASH, DESARROLLADOR
from juego.escenas.base import Escena
from juego.escenas.desarrollador import Desarrollador
from juego.escenas.pausa import Pausa
from juego.escenas.explosion import Explosion
from juego.escenas.arcade.gasolinera import Gasolinera
from juego.escenas.taller import Taller
from juego.escenas.pasajes import pasajes_de


def musica_del_sector(partida):
    # "Neon en ruta" con el color del sector (sonido.MUSICAS: "juego", "juego_2"...)
    numero = SECTORES.index(partida.director.sector) + 1
    return "juego" if numero == 1 else "juego_%d" % numero


class Juego(Escena):
    def __init__(self, app, partida):
        super().__init__(app)
        self.partida = partida
        self.saltar_dibujo = False
        self.dash_pendiente = False     # dash apretado durante el hit-stop (sale al terminar)
        self.nivel_visto = partida.nivel    # para el aceleron del fondo al pasar de tramo

    @property
    def musica(self):
        # Al morir la nave, None (la corto la Partida y sigue el silencio). Con un jefe: en la
        # ¡ALERTA! silencio (suena la sirena) y su musica entra con el nombre; el golpe final
        # la corta. En el cierre del sector (¡JEFE VENCIDO! y el rango), silencio: la fanfarria
        # y el sello suenan solos. Si no, la del juego
        partida = self.partida
        if partida.termino:
            return None
        jefe = partida.jefe
        if jefe is not None:
            if jefe.muriendo() or partida.tiempo - jefe.creado_en < hud.MS_ALERTA:
                return SILENCIO
            propia = "jefe_" + jefe.tipo         # cada jefe su tema (el Ojo, el de siempre)
            return propia if propia in MUSICAS else "jefe"
        if partida.director.cerrando_sector():
            return SILENCIO
        if partida.nivel % JEFE_CADA_NIVELES == JEFE_CADA_NIVELES - 1:
            return "tension"            # el nivel antes del jefe: algo se acerca
        return musica_del_sector(partida)

    @property
    def ambiente(self):
        # El del bioma, salvo en la pelea y en el cierre del sector
        partida = self.partida
        if partida.termino or partida.jefe is not None or partida.director.cerrando_sector():
            return SILENCIO
        return partida.director.sector["ambiente"]

    def actualizar(self, entrada):
        partida = self.partida
        if partida.termino:
            self.app.cambiar_escena(Explosion(self.app, partida), transicion=False)
            return
        # Si la ventana pierde el foco o se desconecta el mando, se pausa solo
        if entrada.foco_perdido or entrada.mando_desconectado:
            partida.pausa_pendiente = True

        self.saltar_dibujo = False
        if partida.congelar_frames > 0:
            # Hit-stop: el juego no avanza, pero lo que se aprieta no se pierde (la App borra
            # las acciones en cada paso): el dash sale y la pausa se abre apenas termina.
            # En el golpe final al jefe se dibuja el cuadro de impacto; si no, la imagen queda quieta
            partida.congelar_frames -= 1
            self.saltar_dibujo = partida.impacto is None
            if partida.congelar_frames == 0:
                partida.impacto = None
            self._guardar_lo_apretado(entrada)
            return
        if partida.camara_lenta > 0:
            # Camara lenta (despues del golpe final): un paso si y uno no
            partida.camara_lenta -= 1
            if partida.camara_lenta % 2:
                self._guardar_lo_apretado(entrada)
                return

        if partida.pausa_pendiente or entrada.pulso(PAUSA):
            partida.pausa_pendiente = False
            self.app.sonidos.pausar_todo()
            self.app.sonidos.reproducir("pausa")    # (despues de pausar: suena igual)
            self.app.entrada.haptica.parar()        # en la pausa el mando no vibra
            self.app.cambiar_escena(Pausa(self.app, self, self.captura_del_mundo(partida)), transicion=False)
            return

        if MODO_DESARROLLADOR and entrada.pulso(DESARROLLADOR):
            self.app.sonidos.pausar_todo()
            self.app.entrada.haptica.parar()
            self.app.cambiar_escena(Desarrollador(self.app, self, self.captura_del_mundo(partida)), transicion=False)
            return

        dx, dy = entrada.direccion()
        pidio_dash = entrada.pulso(DASH) or self.dash_pendiente
        self.dash_pendiente = False
        partida.actualizar(dx, dy, pidio_dash)
        if partida.nivel != self.nivel_visto:
            # Tramo nuevo (no el del jefe): las estrellas pegan un aceleron, la nave avanza
            self.nivel_visto = partida.nivel
            if partida.jefe is None:
                self.app.fondo.acelerar()
        self.mover_fondo(partida)       # con paralaje: el fondo se corre al reves de la nave

        if partida.termino:
            self.app.cambiar_escena(Explosion(self.app, partida), transicion=False)
        elif partida.cumplida:
            pasajes_de(partida).al_cumplir(self.app, partida)     # (el modo decide que sigue)
        elif partida.director.ofertas:
            # Hay cartas para elegir: se abre el Taller con la imagen del juego de fondo
            self.app.cambiar_escena(Taller(self.app, self, self.captura_del_mundo(partida)))
        elif partida.director.gasolinera:
            # Termino el cierre del sector: parada en la gasolinera antes del sector nuevo
            self.app.cambiar_escena(Gasolinera(self.app, self))

    def _guardar_lo_apretado(self, entrada):
        self.dash_pendiente = self.dash_pendiente or entrada.pulso(DASH)
        if entrada.pulso(PAUSA):
            self.partida.pausa_pendiente = True

    def dibujar(self, pantalla):
        if self.saltar_dibujo:
            return
        self.dibujar_partida(pantalla, self.partida, con_nave=True)

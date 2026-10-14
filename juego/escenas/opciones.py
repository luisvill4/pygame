"""
Menu de opciones. Se abre desde Inicio o desde Pausa y al salir vuelve a esa escena.

Usa todo el ancho: a la izquierda las secciones (VIDEO, SONIDO, ACCESIBILIDAD) con la
nave como cursor; a la derecha el panel con los ajustes de la seccion y, abajo, que
hace el ajuste elegido. Cada cambio se aplica al instante y se guarda en config.json.

    LB/RB (Q/E)     cambiar de seccion
    ARRIBA/ABAJO    elegir un ajuste (la ultima fila es VOLVER)
    IZQ/DER         cambiar el valor (ENTER tambien prende y apaga los SI/NO)
    B (ESC)         volver

Cada fila es un Ajuste (patron Template Method): la clase base sabe dibujar la fila y
las subclases dicen como cambian y como se ve su valor:
    Lista        elige entre valores: "< NORMAL >" (las escalas, con puntitos de posicion)
    Interruptor  una llave SI / NO
    Volumen      una barra de cuadritos
Para agregar una opcion:
1. sumarla a guardado.Opciones (valor de fabrica, cargar y guardar), y
2. agregar una linea en AJUSTES con su seccion y su descripcion. Nada mas.
Si es un efecto visual, que consulte accesibilidad.py (no las opciones directamente).
"""
import pygame

from juego import dibujo, interfaz, recursos
from juego.dibujo import texto, CHICA, MEDIA
from juego.config import (ANCHO, CIAN, AMARILLO, BLANCO, GRIS, VERDE, VOLUMEN_MAX, FRECUENCIAS, ORDEN_VIBRACION,
                          ORDEN_TEMBLOR, ORDEN_DESTELLOS, ORDEN_CRT, ORDEN_NEON, ORDEN_ESCALADO,
                          TEXTO_SUAVE, LINEA_APAGADA, FILA_ELEGIDA)
from juego.entrada import (ACEPTAR, VOLVER, ARRIBA, ABAJO, IZQUIERDA, DERECHA, PESTANA_ANTERIOR,
                           PESTANA_SIGUIENTE)
from juego.escenas.base import Escena

PESTANAS = ["VIDEO", "SONIDO", "ACCESIBILIDAD"]
ICONOS = [
    ["XXXXXXX",         # un monitor
     "X.....X",
     "X.....X",
     "X.....X",
     "XXXXXXX",
     "...X...",
     "..XXX.."],
    ["...X...",         # un parlante
     "..XX.X.",
     "XXXX..X",
     "XXXX..X",
     "XXXX..X",
     "..XX.X.",
     "...X..."],
    ["...X...",         # una persona con los brazos abiertos (el simbolo de accesibilidad)
     ".......",
     "XXXXXXX",
     "...X...",
     "...X...",
     "..X.X..",
     ".X...X."],
]
DESCRIPCION_PESTANA = {"VIDEO": "VENTANA Y PANTALLA", "SONIDO": "MUSICA Y EFECTOS",
                       "ACCESIBILIDAD": "PARA JUGAR COMODO"}

# Disposicion
PANEL = pygame.Rect(400, 128, ANCHO - 448, 400)
PANEL_SECCIONES = pygame.Rect(40, 176, 344, 248)
SECCIONES_X, SECCIONES_Y, ALTO_SECCION = 124, 280, 56
FILA_Y = 210            # centro de la primera fila de ajustes
ALTO_FILA = 40          # cuanto baja cada fila (con 5 ajustes en una seccion, 46 ya no entraba)
LINEA_Y = 440           # separador entre las filas y la descripcion
DESCRIPCION_Y = 466     # primer renglon de la descripcion
ANCHO_DESCRIPCION = PANEL.width - 48
NOMBRE_X = PANEL.left + 40      # donde empiezan los nombres...
VALOR_X = PANEL.right - 36      # ...y donde terminan los valores
SEPARACION_FLECHA = 24          # px entre cada flecha y el valor
CIAN_OSCURO = (0, 70, 110)


# ---------- Los ajustes ----------

class Ajuste:
    # Una fila del menu: su nombre, en que seccion va, que dato de las opciones cambia
    # y una descripcion. Las subclases escriben cambiar() y, si hace falta, como se ve
    interruptor = False         # True: ENTER tambien lo cambia (los SI/NO)

    def __init__(self, nombre, pestana, atributo, descripcion, al_cambiar=None):
        self.nombre = nombre
        self.pestana = pestana
        self.atributo = atributo            # el nombre del dato en guardado.Opciones
        self.descripcion = descripcion
        self.al_cambiar = al_cambiar        # funcion(app) para aplicar el cambio (o None)

    def valor(self, app):
        return getattr(app.opciones, self.atributo)

    def poner(self, app, valor):
        setattr(app.opciones, self.atributo, valor)
        if self.al_cambiar is not None:
            self.al_cambiar(app)

    def cambiar(self, app, direccion):
        raise NotImplementedError

    def texto_valor(self, app):
        return str(self.valor(app))

    def apagado(self, app):
        # Los valores "apagados" (NO, sin sonido...) se ven en gris
        return self.valor(app) in ("NO", False, 0)

    def dibujar_valor(self, pantalla, app, y, color, elegida):
        # Por defecto: el valor con una flecha a cada lado. Devuelve donde empieza la
        # flecha de la izquierda (lo usan las escalas para su indicador)
        color = GRIS if self.apagado(app) else color
        mensaje = self.texto_valor(app)
        ancho = recursos.fuente(MEDIA).size(mensaje)[0]
        texto(pantalla, mensaje, MEDIA, color, VALOR_X - SEPARACION_FLECHA, y, alinear="derecha")
        flecha = AMARILLO if elegida else GRIS
        izquierda = VALOR_X - 2 * SEPARACION_FLECHA - ancho
        dibujo.flecha(pantalla, VALOR_X, y - 2, 8, 1, flecha)
        dibujo.flecha(pantalla, izquierda, y - 2, 8, -1, flecha)
        return izquierda


class Lista(Ajuste):
    # Elige entre una lista de valores. 'vuelta': despues del ultimo vuelve al primero
    # (sirve para listas sin orden, como las resoluciones); sin vuelta se queda en la punta
    # (para escalas como NO / SUAVE / NORMAL, que ademas muestran puntitos de posicion).
    # 'nombres' cambia como se muestra un valor
    def __init__(self, nombre, pestana, atributo, valores, descripcion, vuelta=False, nombres=None,
                 al_cambiar=None):
        super().__init__(nombre, pestana, atributo, descripcion, al_cambiar)
        self.valores = valores              # una lista, o una funcion(app) que la devuelve
        self.vuelta = vuelta
        self.nombres = nombres or {}

    def lista(self, app):
        return self.valores(app) if callable(self.valores) else self.valores

    def cambiar(self, app, direccion):
        valores = self.lista(app)
        posicion = valores.index(self.valor(app)) + direccion
        if self.vuelta:
            posicion %= len(valores)
        else:
            posicion = min(max(posicion, 0), len(valores) - 1)
        self.poner(app, valores[posicion])

    def texto_valor(self, app):
        valor = self.valor(app)
        return self.nombres.get(valor, str(valor))

    def dibujar_valor(self, pantalla, app, y, color, elegida):
        if self.vuelta:
            super().dibujar_valor(pantalla, app, y, color, elegida)
            return
        izquierda = super().dibujar_valor(pantalla, app, y - 6, color, elegida)
        # Escala: debajo, un segmento por valor (de flecha a flecha), lleno hasta el elegido
        valores = self.lista(app)
        posicion = valores.index(self.valor(app))
        ancho = (VALOR_X - izquierda + 4) / len(valores)
        for i in range(len(valores)):
            segmento = pygame.Rect(round(izquierda + i * ancho), y + 16, round(ancho) - 4, 4)
            pantalla.fill(color if i <= posicion and not self.apagado(app) else LINEA_APAGADA, segmento)


class Interruptor(Ajuste):
    # SI / NO (izquierda, derecha o ENTER lo dan vuelta). Se dibuja como una llave
    interruptor = True

    def cambiar(self, app, direccion):
        self.poner(app, not self.valor(app))

    def texto_valor(self, app):
        return "SI" if self.valor(app) else "NO"

    def dibujar_valor(self, pantalla, app, y, color, elegida):
        prendido = self.valor(app)
        llave = pygame.Rect(VALOR_X - 56, y - 12, 56, 24)
        pantalla.fill(VERDE if prendido else LINEA_APAGADA, llave)
        pygame.draw.rect(pantalla, BLANCO if elegida else GRIS, llave, 2)
        perilla = pygame.Rect(0, 0, 20, 16)
        perilla.center = (llave.right - 14 if prendido else llave.left + 14, y)
        pantalla.fill(BLANCO if prendido else GRIS, perilla)
        texto(pantalla, self.texto_valor(app), MEDIA, color if prendido else GRIS, llave.left - 16, y,
              alinear="derecha")


class Volumen(Ajuste):
    # Una barra de cuadritos de 0 a VOLUMEN_MAX. Tocarla saca el silencio de la tecla M
    # (si estas subiendo el volumen, lo queres oir). Con el silencio puesto se ve en gris
    def cambiar(self, app, direccion):
        app.opciones.silencio = False
        self.poner(app, min(max(self.valor(app) + direccion, 0), VOLUMEN_MAX))

    def dibujar_valor(self, pantalla, app, y, color, elegida):
        if app.opciones.silencio:
            color = GRIS
        inicio_barra = VALOR_X - 22 - VOLUMEN_MAX * 16
        flecha = AMARILLO if elegida else GRIS
        dibujo.flecha(pantalla, VALOR_X, y, 6, 1, flecha)
        dibujo.flecha(pantalla, inicio_barra - 16, y, 6, -1, flecha)
        for paso in range(VOLUMEN_MAX):
            alto = 8 + paso * 14 // VOLUMEN_MAX              # cada cuadrito un poco mas alto
            cuadrito = pygame.Rect(inicio_barra + paso * 16, y + 10 - alto, 12, alto)
            if paso < self.valor(app):
                pantalla.fill(color, cuadrito)
            else:
                pygame.draw.rect(pantalla, LINEA_APAGADA, cuadrito, 2)


def _aplicar_resolucion(app):
    app.ventana.aplicar(app.opciones.resolucion)


def _probar_vibracion(app):
    app.entrada.vibrar("prueba")        # para sentir como queda (cada motor por turno)


AJUSTES = [
    Lista("RESOLUCION", "VIDEO", "resolucion", lambda app: app.ventana.nombres(),
          "EL TAMAÑO DE LA VENTANA. F11 PASA A PANTALLA COMPLETA Y VUELVE.",
          vuelta=True, al_cambiar=_aplicar_resolucion),
    Lista("FPS", "VIDEO", "fps", FRECUENCIAS,
          "CUADROS POR SEGUNDO. EL JUEGO VA SIEMPRE A LA MISMA VELOCIDAD.",
          vuelta=True, nombres={0: "SIN LIMITE"}),
    Lista("CRT", "VIDEO", "crt", ORDEN_CRT,
          "LINEAS DE PANTALLA ANTIGUA. BAJALAS SI TE CUESTA LEER."),
    Lista("ESCALADO", "VIDEO", "escalado", ORDEN_ESCALADO,
          "SUAVE: TODOS LOS PIXELES IGUALES EN PANTALLAS GRANDES (MAS LENTO).", vuelta=True),
    Lista("NEON", "VIDEO", "neon", ORDEN_NEON,
          "EL BRILLO DE LAS BALAS, LA MONEDA, LAS CAPSULAS Y LAS EXPLOSIONES."),
    Volumen("VOLUMEN", "SONIDO", "volumen",
            "EL VOLUMEN DE TODO. LA TECLA M APAGA Y PRENDE EL SONIDO."),
    Volumen("MUSICA", "SONIDO", "volumen_musica", "LA MUSICA DE FONDO. EN 0 NO SUENA."),
    Volumen("EFECTOS", "SONIDO", "volumen_efectos", "LOS SONIDOS DEL JUEGO: MONEDAS, GOLPES, MENUS..."),
    Interruptor("LATIDO", "SONIDO", "latido", "UN LATIDO SUAVE CUANDO TE QUEDA UNA SOLA VIDA."),
    Lista("TEMBLOR", "ACCESIBILIDAD", "temblor", ORDEN_TEMBLOR,
          "CUANTO SE SACUDE LA PANTALLA. EL MARCADOR NUNCA TIEMBLA."),
    Lista("DESTELLOS", "ACCESIBILIDAD", "destellos", ORDEN_DESTELLOS,
          "REDUCIDOS: NADA DESTELLA NI PARPADEA RAPIDO (FOTOSENSIBILIDAD)."),
    Interruptor("AVISO JEFE", "ACCESIBILIDAD", "aviso_jefe",
                "LOS JEFES MARCAN HACIA DONDE VAN A DISPARAR ANTES DE HACERLO."),
    Lista("VIBRACION", "ACCESIBILIDAD", "vibracion", ORDEN_VIBRACION,
          "QUE TAN FUERTE VIBRA EL MANDO.", al_cambiar=_probar_vibracion),
    Interruptor("AUDIO MONO", "ACCESIBILIDAD", "audio_mono",
                "TODO SUENA IGUAL POR LOS DOS LADOS (PARA UN SOLO AURICULAR U OIDO)."),
]


def ajustes_de(pestana):
    return [ajuste for ajuste in AJUSTES if ajuste.pestana == pestana]


# ---------- La escena ----------

class Opciones(Escena):
    def __init__(self, app, volver_a):
        super().__init__(app)
        self.volver_a = volver_a        # escena a la que se regresa al salir
        self.pestana = 0                # seccion, en PESTANAS
        self.fila = 0                   # los ajustes (0, 1...) y despues VOLVER
        self.cursor_seccion = interfaz.Cursor(0)
        self.cursor_fila = interfaz.Cursor(0)

    def filas(self):
        # Los ajustes de la seccion actual (VOLVER es la fila que sigue al ultimo)
        return ajustes_de(PESTANAS[self.pestana])

    def en_volver(self):
        return self.fila == len(self.filas())

    def actualizar(self, entrada):
        self.mover_fondo()
        self.cursor_seccion.avanzar()
        self.cursor_fila.avanzar()
        # Cada accion se procesa en orden
        for accion in entrada.acciones:
            if self.app.escena is not self:
                break
            if accion in (PESTANA_ANTERIOR, PESTANA_SIGUIENTE):
                self._cambiar_pestana(1 if accion == PESTANA_SIGUIENTE else -1)
            elif accion in (ARRIBA, ABAJO):
                # Da la vuelta: de VOLVER se pasa al primer ajuste
                self.fila = (self.fila + (1 if accion == ABAJO else -1)) % (len(self.filas()) + 1)
                self.cursor_fila.ir_a(self.fila)
                self.app.sonidos.reproducir("ui_mover")
            elif accion in (IZQUIERDA, DERECHA) and not self.en_volver():
                self._cambiar(self.filas()[self.fila], 1 if accion == DERECHA else -1)
            elif accion == ACEPTAR and not self.en_volver() and self.filas()[self.fila].interruptor:
                self._cambiar(self.filas()[self.fila], 1)
            elif accion == VOLVER or (accion == ACEPTAR and self.en_volver()):
                self.app.sonidos.reproducir("ui_volver")
                self.app.cambiar_escena(self.volver_a)

    def _cambiar_pestana(self, direccion):
        self.pestana = (self.pestana + direccion) % len(PESTANAS)
        self.cursor_seccion.ir_a(self.pestana)
        self.fila = 0
        self.cursor_fila.saltar_a(0)
        self.app.sonidos.reproducir("ui_pestana")

    def _cambiar(self, ajuste, direccion):
        # Cambia el valor (direccion: -1 o 1), lo aplica al instante y lo guarda
        ajuste.cambiar(self.app, direccion)
        self.app.sonidos.aplicar_volumen(self.app.opciones)
        self.app.opciones.guardar()
        # (despues de aplicar el volumen: sirve de muestra de como quedo)
        if ajuste.interruptor:
            self.app.sonidos.reproducir("ui_llave_si" if ajuste.valor(self.app) else "ui_llave_no")
        else:
            self.app.sonidos.reproducir("ui_valor_sube" if direccion > 0 else "ui_valor_baja")

    # ---------- Dibujo ----------

    def dibujar(self, pantalla):
        self.dibujar_fondo(pantalla)
        interfaz.titulo(pantalla, "OPCIONES", 64, 76, CIAN, CIAN_OSCURO)
        self._dibujar_secciones(pantalla)

        pestana = PESTANAS[self.pestana]
        interfaz.panel(pantalla, PANEL, CIAN, pestana)
        texto(pantalla, DESCRIPCION_PESTANA[pestana], CHICA, TEXTO_SUAVE, PANEL.right - 80, PANEL.top + 17,
              alinear="derecha")
        self._dibujar_filas(pantalla)
        interfaz.separador(pantalla, PANEL.left + 28, LINEA_Y, PANEL.width - 56)
        self._dibujar_descripcion(pantalla)

        interfaz.ayudas(pantalla, self.app.entrada, [("elegir", "ELEGIR"), ("cambiar", "CAMBIAR"),
                                                     ("pestanas", "SECCION"), ("volver", "VOLVER")])

    def _dibujar_secciones(self, pantalla):
        # Las secciones a la izquierda, en su panel, cada una con su icono; la nave marca
        # en cual estas. Arriba, los botones para cambiar (LB/RB o Q/E)
        interfaz.panel(pantalla, PANEL_SECCIONES, CIAN)
        izquierdo, derecho = interfaz.GLIFOS["pestanas"][1 if self.app.entrada.usando_mando() else 0]
        x, y = PANEL_SECCIONES.left + 24, PANEL_SECCIONES.top + 32
        x += interfaz.boton(pantalla, izquierdo, x, y) + 6
        x += interfaz.boton(pantalla, derecho, x, y) + 12
        texto(pantalla, "CAMBIAR", CHICA, TEXTO_SUAVE, x, y + 1, alinear="izquierda")
        interfaz.separador(pantalla, PANEL_SECCIONES.left + 24, y + 30, PANEL_SECCIONES.width - 48)
        interfaz.menu(pantalla, PESTANAS, self.cursor_seccion, SECCIONES_X, SECCIONES_Y, 250, ALTO_SECCION,
                      tamano=CHICA, color=CIAN, iconos=ICONOS)

    def _dibujar_filas(self, pantalla):
        # Franja que se desliza detras de la fila elegida, y las filas
        franja_y = round(FILA_Y + self.cursor_fila.valor * ALTO_FILA)
        franja = pygame.Rect(PANEL.left + 16, franja_y - ALTO_FILA // 2 + 4, PANEL.width - 32, ALTO_FILA - 8)
        pantalla.fill(FILA_ELEGIDA, franja)
        pantalla.fill(AMARILLO, (franja.left, franja.top, 4, franja.height))
        filas = self.filas()
        for i, ajuste in enumerate(filas):
            elegida = i == self.fila
            y = FILA_Y + i * ALTO_FILA
            texto(pantalla, ajuste.nombre, MEDIA, AMARILLO if elegida else TEXTO_SUAVE, NOMBRE_X, y, alinear="izquierda")
            ajuste.dibujar_valor(pantalla, self.app, y, AMARILLO if elegida else BLANCO, elegida)
        y = FILA_Y + len(filas) * ALTO_FILA
        texto(pantalla, "VOLVER", MEDIA, AMARILLO if self.en_volver() else TEXTO_SUAVE, NOMBRE_X, y,
              alinear="izquierda")

    def _dibujar_descripcion(self, pantalla):
        if self.en_volver():
            descripcion = "VOLVER A LA PANTALLA ANTERIOR. LOS CAMBIOS YA ESTAN GUARDADOS."
        else:
            descripcion = self.filas()[self.fila].descripcion
        for i, linea in enumerate(dibujo.partir_lineas(descripcion, CHICA, ANCHO_DESCRIPCION)):
            texto(pantalla, linea, CHICA, BLANCO, PANEL.left + 32, DESCRIPCION_Y + i * 24, alinear="izquierda")

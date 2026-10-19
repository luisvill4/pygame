"""
FINAL: la pantalla despues del dialogo de la ultima mision (Mision.final).

Hay dos finales, segun lo encontrado (HISTORIA.md), y los dos cambian si se llego TARDE (la
Marea ya se trago la Umbral: tiempo.py):
    - el de siempre: "LA MAREA - FIN", con la musica del Game Over (melancolica) y la cuenta
      de lo que encontraste ("TODAVIA HAY COSAS QUE NO ENCONTRASTE");
    - el verdadero (con la Bitacora sin fecha): "EL PRINCIPIO", con la musica en mayor y el
      mensaje del compas traducido. Alba toma el lugar de El Ultimo: ahora las monedas las deja
      ella, en la galaxia que sigue.
Las lineas aparecen de a una (avanzan en actualizar: funciona igual a cualquier FPS). ACEPTAR
sigue (lo decide quien la abrio, con 'al_terminar').
"""
from juego import dibujo, interfaz
from juego.dibujo import texto, CHICA, MEDIA, TITULO
from juego.config import CENTRO_X, FONDO, VIOLETA, ROJO, AMARILLO, TEXTO, TEXTO_SUAVE, VERDE
from juego.entrada import ACEPTAR
from juego.escenas.base import Escena
from juego.historia.mision import misiones_en_orden, ids_de_fragmentos
from juego.historia.glifos import escribir, dibujar_glifo, ancho_glifo
from juego.historia import fichas, tiempo
from juego.sonido import SILENCIO

VERDAD = "F11"              # el fragmento que abre el final verdadero (la Bitacora sin fecha)
MENSAJE = ["SIGUE", "LAS", "MONEDAS"]
PASOS_POR_LINEA = 40        # cada cuantos pasos aparece una linea mas


class Final(Escena):
    ambiente = SILENCIO

    def __init__(self, app, al_terminar):
        super().__init__(app)
        self.al_terminar = al_terminar
        self.verdadero = VERDAD in app.progreso.fragmentos
        self.tarde = tiempo.tarde(app.progreso)
        self.pasos = 0

    @property
    def musica(self):
        return "iniciales" if self.verdadero else "fin"

    def lineas_visibles(self):
        return self.pasos // PASOS_POR_LINEA

    def actualizar(self, entrada):
        self.mover_fondo()
        self.pasos += 1
        if entrada.pulso(ACEPTAR):
            if self.lineas_visibles() < 5:
                self.pasos = 5 * PASOS_POR_LINEA        # (primero muestra todo)
            else:
                self.app.sonidos.reproducir("ui_aceptar")
                self.al_terminar()

    # ---------- Dibujo ----------

    def dibujar(self, pantalla):
        self.dibujar_fondo(pantalla)
        lineas = self.lineas_visibles()
        color = AMARILLO if self.verdadero else ROJO
        texto(pantalla, "LA MAREA", MEDIA, TEXTO_SUAVE, CENTRO_X, 72)
        anio = "AÑO %.1f EN LA UMBRAL" % self.app.progreso.anios
        texto(pantalla, anio + ("  -  LLEGASTE TARDE" if self.tarde else ""), CHICA, ROJO if self.tarde else TEXTO_SUAVE,
              CENTRO_X, 104)
        if lineas >= 1:
            dibujo.texto_3d(pantalla, "EL PRINCIPIO" if self.verdadero else "FIN", TITULO, color,
                            interfaz.mezclar(color, FONDO, 0.6), 150)
        if lineas >= 2:
            self._dibujar_mensaje(pantalla, 250)
        if lineas >= 3:
            self._dibujar_cuentas(pantalla, 350)
        if lineas >= 4:
            if self.verdadero:
                frase, color_frase = "AHORA LAS MONEDAS LAS DEJA ALBA.", VIOLETA
            elif self.tarde:
                frase, color_frase = "LA MAREA LLEGO PRIMERO. PERO ALGUNOS BAJARON A TIEMPO.", ROJO
            elif self._todo_encontrado():
                frase, color_frase = "EL ULTIMO TODAVIA TIENE ALGO PARA CONTARTE.", TEXTO_SUAVE
            else:
                frase, color_frase = "TODAVIA HAY COSAS QUE NO ENCONTRASTE.", TEXTO_SUAVE
            texto(pantalla, frase, CHICA, color_frase, CENTRO_X, 470)
        if lineas >= 5:
            interfaz.ayudas(pantalla, self.app.entrada, [("aceptar", "CONTINUAR")])

    def _todo_encontrado(self):
        # Todo menos la Bitacora: solo falta volver a cruzar la puerta
        return all(id_ in self.app.progreso.fragmentos for id_ in ids_de_fragmentos() if id_ != VERDAD)

    def _dibujar_mensaje(self, pantalla, y):
        # El mensaje del compas en glifos, palabra por palabra; en el final verdadero, traducido
        glifos = [escribir(palabra) for palabra in MENSAJE]
        anchos = [ancho_glifo(glifo) for glifo in glifos]
        x = CENTRO_X - (sum(anchos) + 40 * (len(glifos) - 1)) // 2
        for glifo, ancho in zip(glifos, anchos):
            dibujar_glifo(pantalla, glifo, x, y, VIOLETA)
            x += ancho + 40
        if self.verdadero:
            texto(pantalla, " ".join(MENSAJE), CHICA, AMARILLO, CENTRO_X, y + 34)

    def _dibujar_cuentas(self, pantalla, y):
        progreso = self.app.progreso
        misiones = [clase.numero for clase in misiones_en_orden()]
        ids = ids_de_fragmentos()
        cuentas = [("MISIONES", len(progreso.misiones & set(misiones)), len(misiones)),
                   ("FRAGMENTOS", len(progreso.fragmentos & set(ids)), len(ids)),
                   ("FICHAS", len(progreso.fichas & set(fichas.POR_ID)), len(fichas.FICHAS))]
        for i, (nombre, tengo, total) in enumerate(cuentas):
            centro = CENTRO_X + (i - 1) * 300
            texto(pantalla, nombre, CHICA, TEXTO_SUAVE, centro, y)
            texto(pantalla, "%d/%d" % (tengo, total), MEDIA, VERDE if tengo == total else TEXTO, centro, y + 34)


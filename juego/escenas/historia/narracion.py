"""
NARRACION: lo que comparten el PROLOGO y el DIALOGO (patron Template Method).

Las dos escenas son una lista de PAGINAS que se escriben solas, cada una con su CUADRO (el
dibujo animado de arriba: escenas/historia/cuadros/). Esta base resuelve lo que se repite:
    - el texto se escribe solo, a la velocidad de Opciones > TEXTO (accesibilidad.letras_por_paso)
    - ACEPTAR completa la pagina o pasa a la siguiente
    - IZQUIERDA (o ARRIBA) vuelve a la pagina anterior, ya escrita: para releer
    - VOLVER pregunta, y saltea todo si se aprieta otra vez antes de SALTEAR_CONFIRMA (antes un
      toque sin querer se llevaba la escena entera, y no se puede volver a ver)
    - el reloj del cuadro (pasos_en_cuadro) vuelve a cero cuando cambia el dibujo, y suena el
      sonido del cuadro si tiene (cuadros.sonido)
Cada pagina es un diccionario {"cuadro": nombre o None, "texto": ..., "paso": n}, donde 'paso'
cuenta las paginas desde que aparecio ese cuadro (el Dialogo suma "quien"). Las subclases arman
sus paginas y dibujan; al terminar se llama a terminar() (que llama a 'al_terminar').
"""
from juego import accesibilidad, interfaz
from juego.config import SALTEAR_CONFIRMA, AMARILLO
from juego.dibujo import texto, CHICA
from juego.entrada import ACEPTAR, VOLVER, IZQUIERDA, ARRIBA
from juego.escenas.base import Escena
from juego.escenas.historia import cuadros

AVISO_SALTEAR = "¿SALTEAR? APRIETA OTRA VEZ"


class Narracion(Escena):

    def __init__(self, app, paginas, al_terminar):
        super().__init__(app)
        self.paginas = paginas
        self.al_terminar = al_terminar
        self.indice = 0
        self.letras = 0.0
        self.pasos = 0                  # desde que empezo la escena (el titulo de apertura)
        self.pasos_en_cuadro = 0        # desde que aparecio el dibujo de ahora (lo anima)
        self.confirmar = 0              # pasos que quedan para confirmar el salto (0 = no pregunto)
        self.terminado = False

    # ---------- Consultas ----------

    def pagina(self):
        return self.paginas[self.indice]

    def texto_actual(self):
        return self.pagina()["texto"]

    def cuadro_actual(self):
        return self.pagina()["cuadro"]

    def pagina_completa(self):
        return self.letras >= len(self.texto_actual())

    # ---------- Logica ----------

    def actualizar(self, entrada):
        self.mover_fondo()
        if self.terminado:
            return
        self.pasos += 1
        self.pasos_en_cuadro += 1
        self.confirmar = max(0, self.confirmar - 1)
        if self.pasos_en_cuadro == 1 and self.cuadro_actual() in cuadros.CUADROS:
            sonido = cuadros.sonido(self.cuadro_actual())
            if sonido:
                self.app.sonidos.reproducir(sonido)
        self._escribir()
        if entrada.pulso(VOLVER):
            self._saltear()
        elif entrada.pulso(ACEPTAR):
            self._seguir()
        elif (entrada.pulso(IZQUIERDA) or entrada.pulso(ARRIBA)) and self.indice > 0:
            self.ir_a(self.indice - 1)
            self.letras = len(self.texto_actual())          # (ya la leiste: aparece entera)
            self.app.sonidos.reproducir("ui_mover")

    def _escribir(self):
        antes = int(self.letras)
        self.letras += accesibilidad.letras_por_paso()
        if int(self.letras) > antes and not self.pagina_completa() and int(self.letras) % 3 == 0:
            self.app.sonidos.reproducir("teclear")      # el teletipo (con enfriamiento)

    def _seguir(self):
        # Completa la pagina; si ya estaba, la siguiente; si no hay mas, termina
        self.confirmar = 0
        if not self.pagina_completa():
            self.letras = len(self.texto_actual())
        elif self.indice + 1 < len(self.paginas):
            self.ir_a(self.indice + 1)
            self.app.sonidos.reproducir("ui_mover")
        else:
            self.app.sonidos.reproducir("ui_aceptar")
            self.terminar()

    def _saltear(self):
        if self.confirmar > 0:
            self.app.sonidos.reproducir("ui_volver")
            self.terminar()
        else:
            self.confirmar = SALTEAR_CONFIRMA
            self.app.sonidos.reproducir("ui_mover")

    def ir_a(self, indice):
        # Otra pagina; si cambia el dibujo, su reloj vuelve a empezar (y entra con el corte)
        cambia = self.paginas[indice]["cuadro"] != self.cuadro_actual()
        self.indice = indice
        self.letras = 0
        if cambia:
            self.pasos_en_cuadro = 0

    def terminar(self):
        self.terminado = True
        self.al_terminar()

    # ---------- Dibujo ----------

    def dibujar_ayudas(self, pantalla, seguir="SEGUIR"):
        # La barra de abajo; mientras pregunta si saltear, lo dice en amarillo a la izquierda
        pares = [("volver", "SALTEAR"), ("aceptar", seguir)]
        if self.indice > 0:
            pares.insert(0, ("anterior", "ATRAS"))
        interfaz.ayudas(pantalla, self.app.entrada, pares)
        if self.confirmar:
            alto = pantalla.get_height()
            texto(pantalla, AVISO_SALTEAR, CHICA, AMARILLO, 28, alto - interfaz.ALTO_AYUDAS // 2 + 2, alinear="izquierda")

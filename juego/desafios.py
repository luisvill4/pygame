"""
Desafios: un reto opcional por sector ("SIN DASH", "SIN CORTAR EL COMBO"...).

Al llegar a un sector se propone uno al azar. No hace falta cumplirlo: si lo cumplis
ganas puntos y un power-up, y suma una estrella al rango del sector (ver rango.py).

Hay dos clases de desafios:
- De AGUANTAR (meta = None): se cumplen si llegas al jefe sin hacer algo
  (SIN DASH, INTOCABLE, SIN AYUDA). Se fallan apenas lo haces.
- De LOGRAR (con meta): se cumplen apenas juntas la meta (12 monedas seguidas,
  6 enemigos destruidos). Se fallan si llega el jefe antes.

La Partida le avisa al director lo que pasa (al_usar_dash, al_recibir_golpe...) y el
director se lo pasa al desafio. Cada desafio escucha solo los avisos que le importan:
los demas son metodos vacios de la clase base (patron Template Method, otra vez).

Para agregar uno: una clase con @registrar_desafio, su 'tipo', 'nombre', 'pista' y
'color', y los avisos que necesite (llamando a self.fallar() o self.avanzar()).
"""
from juego.config import (CIAN, AMARILLO, ROJO, VERDE, MAGENTA, BLANCO, DESAFIO_COMBO, DESAFIO_CAZADOR,
                          DESAFIO_INTERCEPTAR, DESBLOQUEO_ENEMIGO)

TIPOS_DESAFIO = {}          # nombre -> clase


def registrar_desafio(clase):
    TIPOS_DESAFIO[clase.tipo] = clase
    return clase


class Desafio:
    tipo = None
    nombre = ""             # corto: entra en el HUD
    pista = ""              # que hay que hacer
    color = CIAN
    meta = None             # None = de aguantar; un numero = de lograr

    def __init__(self):
        self.estado = "en_curso"        # "en_curso", "cumplido" o "fallado"
        self.progreso = 0               # en los de lograr: cuanto llevas

    @classmethod
    def disponible(cls, partida):
        # Para los que no se pueden en cualquier momento (ej: sin enemigos destruibles)
        return True

    def en_curso(self):
        return self.estado == "en_curso"

    def texto_progreso(self):
        if self.meta is None:
            return ""
        return str(self.progreso) + "/" + str(self.meta)

    # ---------- Cambios de estado ----------

    def fallar(self):
        self.estado = "fallado"

    def avanzar(self, progreso):
        # En los de lograr: anota cuanto llevas y si llegaste a la meta, se cumple
        self.progreso = min(progreso, self.meta)
        if self.progreso >= self.meta:
            self.estado = "cumplido"

    def al_llegar_el_jefe(self):
        # Los de aguantar se cumplen (aguantaste); los de lograr que no se lograron, se fallan
        if self.meta is None:
            self.estado = "cumplido"
        else:
            self.fallar()

    # ---------- Avisos (cada desafio usa los que le importan) ----------

    def al_usar_dash(self):
        pass

    def al_recibir_golpe(self):
        pass

    def al_agarrar_powerup(self):
        pass

    def al_recoger_moneda(self, combo):
        pass

    def al_destruir_enemigo(self):
        pass

    def al_interceptar(self):
        pass


@registrar_desafio
class SinDash(Desafio):
    tipo = "sin_dash"
    nombre = "SIN DASH"
    pista = "LLEGA AL JEFE SIN USAR EL DASH"
    color = CIAN

    def al_usar_dash(self):
        self.fallar()


@registrar_desafio
class Intocable(Desafio):
    tipo = "intocable"
    nombre = "INTOCABLE"
    pista = "LLEGA AL JEFE SIN RECIBIR GOLPES"
    color = ROJO

    def al_recibir_golpe(self):
        self.fallar()


@registrar_desafio
class SinAyuda(Desafio):
    tipo = "sin_ayuda"
    nombre = "SIN AYUDA"
    pista = "LLEGA AL JEFE SIN AGARRAR POWER-UPS"
    color = MAGENTA

    def al_agarrar_powerup(self):
        self.fallar()


@registrar_desafio
class SinCortarElCombo(Desafio):
    tipo = "combo"
    nombre = "SIN CORTAR EL COMBO"
    pista = str(DESAFIO_COMBO) + " MONEDAS SEGUIDAS"
    color = AMARILLO
    meta = DESAFIO_COMBO

    def al_recoger_moneda(self, combo):
        # El progreso es el combo actual: si se corta, vuelve a empezar
        self.avanzar(combo)


@registrar_desafio
class Cazador(Desafio):
    tipo = "cazador"
    nombre = "CAZADOR"
    pista = "DESTRUI " + str(DESAFIO_CAZADOR) + " ENEMIGOS CON EL DASH"
    color = VERDE
    meta = DESAFIO_CAZADOR

    @classmethod
    def disponible(cls, partida):
        # Solo si ya hay enemigos que el dash destruye (el divisor es el primero)
        return partida.nivel >= DESBLOQUEO_ENEMIGO["divisor"]

    def al_destruir_enemigo(self):
        self.avanzar(self.progreso + 1)


@registrar_desafio
class Interceptor(Desafio):
    tipo = "interceptor"
    nombre = "INTERCEPTOR"
    pista = "FRENA " + str(DESAFIO_INTERCEPTAR) + " EMBESTIDAS CON EL DASH"
    color = BLANCO
    meta = DESAFIO_INTERCEPTAR

    @classmethod
    def disponible(cls, partida):
        # Solo si ya hay embestidores
        return partida.nivel >= DESBLOQUEO_ENEMIGO["embestidor"]

    def al_interceptar(self):
        self.avanzar(self.progreso + 1)

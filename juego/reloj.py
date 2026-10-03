"""
Limitador de cuadros por segundo (preciso).

pygame.time.Clock.tick() solo espera milisegundos enteros: a 144 FPS (6.94 ms por
cuadro) termina dibujando ~151. Este limitador duerme casi todo el tiempo que falta
(sin gastar CPU) y espera "activamente" solo el ultimo milisegundo y medio, que es
donde el sleep del sistema no es exacto.
"""
import time

ESPERA_ACTIVA = 0.0015      # segundos finales que se esperan sin dormir (para ser exacto)


class LimitadorFPS:
    def __init__(self):
        self.ultimo = time.perf_counter()

    def esperar(self, fps):
        # Espera lo necesario para no pasar 'fps' (0 = sin limite) y devuelve cuantos
        # milisegundos reales pasaron desde el cuadro anterior
        if fps:
            objetivo = self.ultimo + 1 / fps
            restante = objetivo - time.perf_counter()
            if restante > ESPERA_ACTIVA:
                time.sleep(restante - ESPERA_ACTIVA)
            while time.perf_counter() < objetivo:
                pass
        ahora = time.perf_counter()
        milisegundos = (ahora - self.ultimo) * 1000
        self.ultimo = ahora
        return milisegundos

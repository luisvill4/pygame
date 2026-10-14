"""El compositor (herramientas/componer_musica.py): las herramientas para hacer efectos."""
import math

import pytest

from herramientas import componer_musica as c

FS = c.FRECUENCIA


def cruces(muestras):
    # Cuantas veces la onda cruza el cero (el doble de su frecuencia, por segundo)
    return sum(1 for a, b in zip(muestras, muestras[1:]) if a < 0 <= b or b < 0 <= a)


def tramo(muestras, desde, hasta):
    return muestras[int(desde * FS):int(hasta * FS)]


def test_las_curvas_unen_los_puntos():
    puntos = [(0, 100), (1, 400)]
    assert c.curva(puntos, -1) == 100 and c.curva(puntos, 2) == 400       # afuera: el borde
    assert c.curva(puntos, 0.5) == pytest.approx(250)                       # recta
    assert c.curva(puntos, 0.5, exponencial=True) == pytest.approx(200)     # pareja para el oido
    assert c.curva([(0, 0), (0.1, 1), (0.3, 0)], 0.2) == pytest.approx(0.5)
    assert c.a_hertz("A4") == pytest.approx(440) and c.a_hertz(123) == 123


def test_el_barrido_cambia_de_altura():
    efecto = c.nuevo_efecto("prueba", 1)
    efecto.barrido([(0, "A3"), (1, "A5")], c.BAJO, 1.0)            # dos octavas: 220 a 880 Hz
    muestras = efecto.mezclar()
    al_principio = cruces(tramo(muestras, 0.05, 0.15))
    al_final = cruces(tramo(muestras, 0.85, 0.95))
    # a los 0.1 s va por 220 * 4^0.1 = 252 Hz y a los 0.9 s por 220 * 4^0.9 = 767 Hz
    assert al_final / al_principio == pytest.approx(767 / 252, rel=0.1)


def test_la_secuencia_respeta_los_tiempos_y_los_silencios():
    efecto = c.nuevo_efecto("prueba", 0.5)
    efecto.secuencia("C5:100 -:150 C5+E5+G5:100", c.PULSO_FINO, 1.0)
    muestras = efecto.mezclar()
    suena = max(abs(m) for m in tramo(muestras, 0.0, 0.09))
    callado = max(abs(m) for m in tramo(muestras, 0.16, 0.245))      # (despues de la liberacion de 50 ms)
    acorde = max(abs(m) for m in tramo(muestras, 0.25, 0.34))
    assert suena > 0.05 and callado < 0.001 and acorde > 0.05


def test_el_filtro_del_ruido_apaga_los_agudos():
    def agudos(filtro):
        efecto = c.nuevo_efecto("prueba", 0.3)
        efecto.ruido(0.3, 1.0, filtro=filtro, forma=[(0, 1), (0.3, 1)])
        muestras = efecto.mezclar()
        # lo que cambia de una muestra a la otra es lo agudo
        return sum(abs(b - a) for a, b in zip(muestras, muestras[1:]))
    assert agudos([(0, 8000)]) > 2 * agudos([(0, 400)])


def test_el_filtro_se_mueve_con_su_curva():
    efecto = c.nuevo_efecto("prueba", 0.4)
    efecto.ruido(0.4, 1.0, filtro=[(0, 300), (0.4, 9000)], forma=[(0, 1), (0.4, 1)])
    muestras = efecto.mezclar()
    oscuro, brillante = tramo(muestras, 0.02, 0.1), tramo(muestras, 0.3, 0.38)
    assert cruces(brillante) > 3 * cruces(oscuro)


def test_los_chasquidos_dejan_silencios_entre_medio():
    efecto = c.nuevo_efecto("prueba", 0.5)
    efecto.ruido(0.5, 1.0, chasquidos=20, forma=[(0, 1), (0.5, 1)])
    muestras = efecto.mezclar()
    callados = sum(1 for m in muestras if abs(m) < 0.0001)
    assert callados > len(muestras) * 0.5


def test_el_tremolo_hace_temblar_el_volumen():
    def subidas_y_bajadas(tremolo):
        efecto = c.nuevo_efecto("prueba", 0.6)
        efecto.barrido([(0, "A4"), (0.6, "A4")], c.PULSO_REDONDO, 1.0, tremolo=tremolo)
        muestras = tramo(efecto.mezclar(), 0.1, 0.5)
        ventanas = [max(abs(m) for m in muestras[i:i + 441]) for i in range(0, len(muestras) - 441, 441)]
        return max(ventanas) - min(ventanas)
    assert subidas_y_bajadas((12, 12, 0.9)) > 3 * subidas_y_bajadas(None)


def test_la_dinamica_decide_que_tan_fuerte_queda():
    for dinamica in ("pp", "mf", "ff"):
        efecto = c.nuevo_efecto("prueba", 0.2, dinamica)
        efecto.secuencia("A4:200", c.PULSO_MEDIO, 1.0)
        pico = max(abs(m) for m in efecto.mezclar())
        assert pico == pytest.approx(c.DINAMICAS[dinamica], rel=0.02)


def test_el_efecto_se_recorta_al_terminar():
    efecto = c.nuevo_efecto("prueba", 0.2)
    efecto.secuencia("A4:150", c.PULSO_FINO, 1.0)
    assert len(efecto.mezclar()) / FS < 0.35         # sin los 2 s de cola


def test_medir_da_duracion_pico_y_rms():
    seno = [0.5 * math.sin(2 * math.pi * 440 * i / FS) for i in range(FS)]
    segundos, pico, rms = c.medir(seno)
    assert segundos == pytest.approx(1)
    assert pico == pytest.approx(-6.02, abs=0.05) and rms == pytest.approx(-9.03, abs=0.05)

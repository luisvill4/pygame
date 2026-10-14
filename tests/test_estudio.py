"""El estudio (herramientas/estudio/): sintesis, procesos, obras y el registro."""
import numpy as np
import pytest

from herramientas.estudio import procesos, instrumentos, armonia
from herramientas.estudio.base import FS, midi, hertz, leer_acorde, curva, db, muestras
from herramientas.estudio.sintesis import onda, adsr, filtrar, ruido
from herramientas.estudio.obra import Obra, Efecto, Pista, eventos, pasos_de, leer_simbolo
from herramientas.estudio.obras import cargar_todas, ARMONICOS


def energia_arriba_de(senal, hz):
    # Que parte de la energia esta por encima de 'hz' (0 a 1)
    mono = senal if senal.ndim == 1 else senal.mean(axis=0)
    potencia = np.abs(np.fft.rfft(mono)) ** 2
    frecuencias = np.fft.rfftfreq(len(mono), 1 / FS)
    return potencia[frecuencias > hz].sum() / potencia.sum()


# ---------- Base ----------

def test_notas_y_acordes():
    assert midi("A4") == 69 and midi("C#5") == 73 and hertz("A4") == pytest.approx(440)
    assert leer_acorde("Am7") == (9, [0, 3, 7, 10], None)
    assert leer_acorde("C/E") == (0, [0, 4, 7], 4)
    assert leer_acorde("Esus4")[1] == [0, 5, 7]


def test_las_curvas_exponenciales_suenan_parejas():
    valores = curva([(0, 100), (1, 400)], FS + 1, exponencial=True)
    assert valores[FS // 2] == pytest.approx(200, rel=0.01)          # a mitad de camino, una octava
    assert curva([(0, 0), (1, 1)], FS + 1)[FS // 2] == pytest.approx(0.5, abs=0.001)


# ---------- Sintesis ----------

def test_la_sierra_no_tiene_aliasing():
    # Una sierra "ingenua" de 3 kHz dobla sus armonicos por debajo de la fundamental (suena
    # aspera); con PolyBLEP casi no queda nada ahi
    frecuencia = np.full(FS // 2, 3000.0)
    limpia = onda("sierra", frecuencia)
    fase = np.cumsum(frecuencia) / FS % 1
    ingenua = 2 * fase - 1
    assert energia_arriba_de(limpia, 0) == pytest.approx(1)
    debajo = lambda s: 1 - energia_arriba_de(s, 2500)       # noqa: E731 (lo que cae debajo de la fundamental)
    assert debajo(limpia) < debajo(ingenua) / 3


def test_la_envolvente_sube_baja_y_termina_en_cero():
    envolvente = adsr(0.5, 0.01, 0.1, 0.6, 0.1)
    assert envolvente[0] == 0 and envolvente[-1] == 0
    assert envolvente.max() == pytest.approx(1, abs=0.01)
    assert envolvente[muestras(0.45)] == pytest.approx(0.6, abs=0.02)      # en el sostenido
    assert len(envolvente) == muestras(0.5) + muestras(0.5)                # la nota + 5 liberaciones


def test_el_filtro_redondea_los_agudos():
    azar = np.random.default_rng(1)
    blanco = azar.uniform(-1, 1, FS // 2)
    assert energia_arriba_de(filtrar(blanco, 500.0), 3000) < energia_arriba_de(blanco, 3000) / 50
    assert energia_arriba_de(filtrar(blanco, 3000.0, modo="altos"), 3000) > 0.8


def test_ningun_instrumento_es_chillon():
    # El "centro de gravedad" del espectro de un La3 queda abajo de 2 kHz (los efectos viejos
    # andaban entre 4 y 7 kHz)
    for nombre in ("PAD_CALIDO", "PAD_OSCURO", "PAD_SUAVE", "PLUCK", "LEAD_CALIDO", "LEAD_HUECO", "EPIANO",
                   "CAMPANA", "CRISTAL", "MARIMBA", "METAL"):
        sonido = getattr(instrumentos, nombre).tocar("A3", 0.6, 0.9)
        assert procesos.centroide(sonido) < 2000, nombre
        assert not np.isnan(sonido).any()


def test_el_ruido_sigue_su_curva_de_filtro():
    sonido = ruido(0.6, filtro=[(0, 300), (0.6, 9000)], forma=[(0, 1), (0.6, 1)])
    oscuro, brillante = sonido[:, :muestras(0.1)], sonido[:, -muestras(0.1):]
    assert energia_arriba_de(brillante, 3000) > 5 * energia_arriba_de(oscuro, 3000)


# ---------- Procesos ----------

def test_el_limitador_no_deja_pasar_el_techo():
    azar = np.random.default_rng(2)
    fuerte = azar.uniform(-3, 3, (2, FS // 2))
    assert np.max(np.abs(procesos.limitar(fuerte, -1.0))) <= db(-1.0) + 1e-9


def test_el_ecualizador_de_un_efecto_no_ensucia_el_final():
    # La FFT es circular: sin relleno, el "adelanto" del filtro caia al final del efecto
    golpe = np.zeros((2, FS))
    golpe[:, 100:2000] = np.random.default_rng(3).uniform(-1, 1, (2, 1900))
    ecualizado = procesos.ecualizar(golpe, [("corte_graves", 30)], vuelta=False)
    assert np.max(np.abs(ecualizado[:, -muestras(0.3):])) < 1e-4


def test_la_reverb_de_un_tema_da_la_vuelta():
    # Un golpe al final de un tema: su cola tiene que sonar al principio (sin costura)
    senal = np.zeros((2, FS * 2))
    senal[:, -100] = 1.0
    mojada = procesos.reverb(senal, 1.5, vuelta=True)
    assert np.max(np.abs(mojada[:, :muestras(0.3)])) > 0.01


def test_el_bombeo_baja_en_cada_golpe_y_vuelve():
    ganancia = procesos.bombeo(FS, [0, FS // 2], profundidad=0.6, liberacion=0.1)
    assert ganancia[muestras(0.006)] == pytest.approx(0.4, abs=0.05)
    assert ganancia[muestras(0.4)] == pytest.approx(1, abs=0.01)
    assert ganancia[FS // 2 + muestras(0.006)] < 0.5


def test_el_loudness_de_un_seno_conocido():
    # Un seno de 1 kHz a -20 dBFS en los dos canales mide ~-20 LUFS (con la ponderacion K, +0.7)
    t = np.arange(FS * 3) / FS
    seno = db(-20) * np.sin(2 * np.pi * 1000 * t)
    assert procesos.loudness(np.array([seno, seno])) == pytest.approx(-20, abs=1.0)


# ---------- Notacion ----------

def test_la_grilla_se_lee_como_un_tracker():
    assert eventos(pasos_de("A4 . . - C5+E5! | . - G4?")) == [(0, 3, "A4"), (4, 2, "C5+E5!"), (7, 1, "G4?")]
    assert leer_simbolo("C5+E5!") == (["C5", "E5"], 1.0)
    assert leer_simbolo("G4?")[1] < leer_simbolo("G4")[1]


def test_los_acordes_se_mueven_lo_menos_posible():
    # Conduccion de voces: de un acorde al siguiente, ninguna voz salta mas de una tercera
    # mayor (4 semitonos); sin esto, los pads "saltan" y suenan a teclado de juguete
    tema = Obra("prueba", acordes=["C", "Am", "F", "G", "Em", "Dm", "Esus4", "E"])
    anterior = None
    for compas in range(len(tema.acordes)):
        voces = tema.voces_del_acorde(compas, ("A3", "E5"), anterior)
        if anterior:
            assert max(abs(a - b) for a, b in zip(sorted(voces), sorted(anterior))) <= 4, tema.acordes[compas]
        anterior = voces


# ---------- Obras ----------

def test_un_tema_da_la_vuelta_y_llega_a_su_volumen():
    tema = Obra("prueba", bpm=120, acordes=["Am", "F"], objetivo=-16.0)
    tema.pista("pad", instrumentos.PAD_SUAVE, reverb=0.3).acordes("X . . . . . . . . . . . . . . .")
    tema.bateria("bombo").grilla("K - - - K - - - K - - - K - - - | K - - - K - - - K - - - K - - -")
    audio = tema.mezclar()
    assert audio.shape[1] == muestras(4.0)                      # 2 compases de 4/4 a 120 bpm
    assert procesos.loudness(audio) == pytest.approx(-16, abs=1.0)
    assert np.max(np.abs(audio)) <= db(-1.0) + 1e-9


def test_un_efecto_se_recorta_y_no_suena_eterno():
    efecto = Efecto("prueba", 0.3, "mf", sala=(2.0, 0.5))
    efecto.pista("campana", instrumentos.CAMPANA, reverb=0.8).secuencia("C5:300")
    audio = efecto.mezclar()
    assert audio.shape[1] <= muestras(0.3 + 2.0 * 0.6) + 1     # su duracion + la cola maxima
    assert np.max(np.abs(audio[:, -50:])) < 0.01                # termina apagado
    assert procesos.loudness_maximo(audio) == pytest.approx(Efecto.DINAMICAS["mf"], abs=1.0)


def _acorde(volumen, clase=Efecto, **datos):
    # El mismo acorde de piano, mas fuerte o mas suave desde la pista
    obra = clase("prueba", **datos)
    obra.pista("piano", instrumentos.EPIANO, volumen=volumen, reverb=0.3).secuencia("C4+E4+G4+C5:400")
    return obra.mezclar()


def test_el_master_no_ensucia_un_acorde_fuerte():
    # Lo que saturaba las monedas, los menus y los premios: la cinta del master recibia la mezcla
    # sin nivelar, y un acorde (varias notas sumadas) llegaba tan fuerte que la curva lo aplastaba
    # y mezclaba sus notas entre ellas. Ahora el master no depende del nivel con que llegan las
    # pistas: 10 dB mas fuerte sale igual (el volumen lo pone la dinamica)
    efecto = dict(segundos=0.4, dinamica="mf")
    assert np.allclose(_acorde(-10.0, **efecto), _acorde(0.0, **efecto), atol=1e-4)
    tema = dict(segundos=2.0, vuelta=True, objetivo=-16.0)
    assert np.allclose(_acorde(-10.0, Obra, **tema), _acorde(0.0, Obra, **tema), atol=1e-4)


def _notas_de(nombre, color="do"):
    # Las notas (midi, ya en su color) que toca una obra, sin sintetizarlas: (nota, inicio,
    # segundos, pista)
    tocadas = []

    def anotar(pista, nota, inicio, segundos, fuerza=0.8, tremolo=None):
        tocadas.append((armonia.armonizar(nota, pista.obra.color), inicio, segundos, pista.nombre))

    with pytest.MonkeyPatch.context() as parche:
        parche.setattr(Pista, "nota", anotar)
        parche.setattr(Pista, "poner", lambda *datos: None)
        with armonia.en_color(color):
            obra = cargar_todas()[nombre]()
    return tocadas, obra


def test_la_moneda_suma_capas_con_el_combo():
    # El combo se escucha sin mirar el HUD: cada multiplicador, la nota principal mas aguda y mas
    # capas (una segunda voz, el brillo de la octava, una nota mas en la subida, un destello)
    anterior = None
    for numero in range(1, 6):
        notas, obra = _notas_de("moneda_%d" % numero)
        principal = max(nota for nota, _, _, pista in notas if pista == obra.pistas[0].nombre)   # el cristal
        riqueza = (len(notas), len(obra.pistas))
        if anterior:
            assert principal > anterior[0] and riqueza > anterior[1], numero
        anterior = (principal, riqueza)


def test_los_efectos_armonicos_no_apilan_notas_que_raspan():
    # Dos notas que suenan juntas a un semitono, un tono o un tritono raspan (asi sonaban las
    # escalas rapidas de cristal, los acordes de 6/9 y el Taller contra las cartas). En TODOS los
    # colores: el La de un efecto, sobre un acorde con septima, pasa a ser la septima, y La + Mi
    # se vuelve un tritono. Por eso los acordes se arman con Do, Re y Sol
    raspan = {1: "semitono", 2: "tono", 6: "tritono"}
    for nombre in sorted(ARMONICOS):
        for color in armonia.COLORES:
            notas, _ = _notas_de(nombre, color)
            for i, (a, desde_a, largo_a, _) in enumerate(notas):
                for b, desde_b, largo_b, _ in notas[i + 1:]:
                    juntas = abs(desde_a - desde_b) < 0.12 or desde_a <= desde_b < desde_a + largo_a
                    assert not (juntas and abs(a - b) in raspan), (nombre, color, raspan.get(abs(a - b)))


def test_los_efectos_registrados_se_componen():
    # Una muestra (uno de cada seis, en orden alfabetico: todas las familias): componer los
    # 200 y pico tarda un minuto, y eso es trabajo de componer.py. Los temas tampoco (tardan)
    obras = cargar_todas()
    assert "musica_juego" in obras
    efectos = sorted(nombre for nombre in obras if not nombre.startswith("musica"))
    for nombre in efectos[::6]:
        audio = obras[nombre]().mezclar()
        assert audio.shape[0] == 2 and audio.shape[1] > 0 and not np.isnan(audio).any(), nombre
        assert procesos.centroide(audio) < 4000, nombre        # nada chillon

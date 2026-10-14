"""La armonia: los efectos de premio siguen al acorde de la musica (estudio/armonia.py y sonido.py)."""
import pytest

from herramientas.estudio import armonia
from herramientas.estudio.base import midi
from herramientas.estudio.obras import ARMONICOS as ARMONICOS_DEL_ESTUDIO
from juego import sonido
from juego.sonido import CATALOGO, MUSICAS, COLORES, ARMONICOS, MUSICA, cargar, cargar_fichas
from juego.config import ADELANTO_ACORDE


# ---------- El estudio: colores y re-armonizacion ----------

def test_cada_acorde_tiene_el_color_de_su_pentatonica():
    assert armonia.color_de_acorde("C") == "do"
    assert armonia.color_de_acorde("Am") == "do"            # menor: la de su relativo mayor
    assert armonia.color_de_acorde("Dm7") == "fa"
    assert armonia.color_de_acorde("Bb") == "sib"
    assert armonia.color_de_acorde("E") == "mi"
    assert armonia.color_de_acorde("E7") == "mi7"           # con septima: sin la sexta
    assert armonia.color_de_acorde("Esus4") == "misus"      # suspendido: sin la tercera
    assert armonia.color_de_acorde("F/E") == "fa"           # con barra: manda el acorde


def test_cada_color_es_consonante_con_su_acorde():
    # Ninguna nota del color esta a un semitono de una nota del acorde (eso es lo que choca)
    for acorde in ["C", "Am", "F", "G", "Em", "E", "Esus4", "Dm", "Bb", "A", "Gm", "C7", "D7", "E7", "Bbm7"]:
        fundamental, intervalos, _ = armonia.leer_acorde(acorde)
        del_acorde = {(fundamental + i) % 12 for i in intervalos}
        raiz, forma = armonia.COLORES[armonia.color_de_acorde(acorde)]
        for grado in armonia.FORMAS[forma]:
            nota = (raiz + grado) % 12
            assert all(min((nota - otra) % 12, (otra - nota) % 12) != 1 for otra in del_acorde), (acorde, nota)


def test_rearmonizar_conserva_la_escalera_de_la_moneda():
    escalera = [midi(n) for n in ("C6", "D6", "E6", "G6", "A6")]       # la moneda x1 a x5
    for color in armonia.COLORES:
        nueva = [armonia.armonizar(n, color) for n in escalera]
        assert nueva == sorted(nueva) and len(set(nueva)) == 5          # sigue subiendo, grado a grado
        assert all(abs(a - b) <= 6 for a, b in zip(nueva, escalera))   # casi en el mismo registro
    assert [armonia.armonizar(n, "do") for n in escalera] == escalera
    assert armonia.armonizar(midi("C6"), "sib") == midi("Bb5")
    assert armonia.armonizar(midi("A6"), "mi7") == midi("D7")           # el 5to grado de Mi7: la septima


def test_un_efecto_armonico_no_puede_salirse_de_la_pentatonica():
    with pytest.raises(armonia.FueraDeLaPentatonica):
        armonia.armonizar(midi("F5"), "sol")


def test_el_estudio_y_el_juego_tienen_los_mismos_colores_y_armonicos():
    assert set(COLORES) == set(armonia.COLORES)
    assert ARMONICOS == ARMONICOS_DEL_ESTUDIO
    del_catalogo = {archivo.rsplit("_", 1)[0] for efecto in CATALOGO.values() if efecto.armonico
                    for archivo in efecto.archivos}
    assert del_catalogo == ARMONICOS             # todos estan en el catalogo, con sus colores


def test_cada_tema_sabe_el_color_de_cada_compas(app):          # (app: abre el mixer)
    fichas = cargar_fichas()
    for nombre, archivo in MUSICAS.items():
        ficha = fichas[archivo]
        assert ficha["colores"] == [armonia.color_de_acorde(a) for a in ficha["acordes"]], nombre
        assert set(ficha["colores"]) <= set(COLORES), nombre
        # el tema dura justo sus compases (si no, el juego pierde la cuenta al dar la vuelta)
        largo = cargar(archivo).get_length() * 1000
        assert largo == pytest.approx(len(ficha["colores"]) * ficha["compas_ms"], abs=30), nombre


# ---------- El juego: el efecto suena en el color del compas ----------

def colores_de(nombre):
    return cargar_fichas()[MUSICAS[nombre]]["colores"]


def compas_ms(nombre):
    return cargar_fichas()[MUSICAS[nombre]]["compas_ms"]


def ir_al_compas(app, tema, compas):
    # Deja el reloj en la mitad de ese compas del tema
    app.reloj_falso = app.sonidos.musica.inicio + (compas + 0.5) * compas_ms(tema)


def test_el_color_sigue_al_compas_del_tema(app):
    app.sonidos.tocar_musica("juego")
    colores = colores_de("juego")
    for compas in range(len(colores)):
        ir_al_compas(app, "juego", compas)
        assert app.sonidos.color_actual() == colores[compas]
    ir_al_compas(app, "juego", len(colores) + 1)             # da la vuelta
    assert app.sonidos.color_actual() == colores[1]


def test_justo_antes_del_cambio_ya_suena_el_acorde_que_viene(app):
    app.sonidos.tocar_musica("juego")
    colores = colores_de("juego")
    compas = next(i for i in range(len(colores) - 1) if colores[i] != colores[i + 1])
    app.reloj_falso = app.sonidos.musica.inicio + (compas + 1) * compas_ms("juego") - ADELANTO_ACORDE / 2
    assert app.sonidos.color_actual() == colores[compas + 1]


def test_la_moneda_suena_en_el_color_del_acorde(app):
    app.sonidos.tocar_musica("juego")
    colores = colores_de("juego")
    compas = colores.index("mi")                # el Mi mayor: el de la moneda en Do chocaba
    ir_al_compas(app, "juego", compas)
    canal = app.sonidos.reproducir("moneda_1")
    lugar = app.sonidos.canales_efectos.index(canal)
    assert app.sonidos.en_canal[lugar].sonido is cargar("moneda_1_mi.ogg")


def test_en_la_pausa_la_musica_no_avanza(app):
    app.sonidos.tocar_musica("juego")
    colores = colores_de("juego")
    compas = next(i for i in range(len(colores) - 1) if colores[i] != colores[i + 1])
    ir_al_compas(app, "juego", compas)
    app.sonidos.pausar_todo()
    app.reloj_falso += 5 * compas_ms("juego")       # una pausa larga
    assert app.sonidos.color_actual() == colores[compas]
    app.sonidos.reanudar_todo()
    assert app.sonidos.color_actual() == colores[compas]
    app.reloj_falso += compas_ms("juego")
    assert app.sonidos.color_actual() == colores[(compas + 1) % len(colores)]


def test_sin_musica_suena_en_do(app):
    assert app.sonidos.color_actual() == "do"                   # nada sonando
    app.sonidos.tocar_musica("juego")
    ir_al_compas(app, "juego", colores_de("juego").index("mi"))
    app.opciones.volumen_musica = 0                              # la musica apagada en Opciones
    assert app.sonidos.nivel(MUSICA) == 0 and app.sonidos.color_actual() == "do"


def test_los_efectos_que_no_son_armonicos_suenan_siempre_igual(app):
    app.sonidos.tocar_musica("juego")
    ir_al_compas(app, "juego", colores_de("juego").index("mi"))
    canal = app.sonidos.reproducir("nave_golpe")
    lugar = app.sonidos.canales_efectos.index(canal)
    assert app.sonidos.en_canal[lugar].sonido is cargar("nave_golpe.ogg")
    assert not sonido.CATALOGO["nave_golpe"].armonico


def test_un_color_que_se_abre_tarde_tiene_el_volumen_de_las_opciones(app):
    # Los colores se abren la primera vez que suenan: tienen que respetar el volumen elegido
    app.opciones.volumen_efectos = 3
    app.sonidos.aplicar_volumen(app.opciones)
    app.sonidos.tocar_musica("juego")
    ir_al_compas(app, "juego", colores_de("juego").index("sol"))
    canal = app.sonidos.reproducir("moneda_2")
    lugar = app.sonidos.canales_efectos.index(canal)
    assert app.sonidos.en_canal[lugar].sonido.get_volume() == pytest.approx(app.sonidos.nivel("EFECTOS"), abs=0.01)

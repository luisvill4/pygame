"""records.json y config.json: nunca hacen caer el juego."""
import json

from juego.guardado import TablaRecords, Opciones


def test_records_si_no_existe_lo_crea(tmp_path):
    archivo = tmp_path / "records.json"
    tabla = TablaRecords(str(archivo))
    assert tabla.filas("NORMAL") == [] and tabla.maximo("NORMAL") == 0
    assert json.loads(archivo.read_text()) == {"FACIL": [], "NORMAL": [], "DIFICIL": [], "PESADILLA": []}


def test_records_dañado_empieza_vacio(tmp_path):
    archivo = tmp_path / "records.json"
    archivo.write_text("esto no es json")
    assert TablaRecords(str(archivo)).filas("NORMAL") == []


def test_records_del_formato_viejo_pasan_a_normal(tmp_path):
    # Antes habia una sola tabla (una lista): no se pierden, quedan como los de NORMAL
    archivo = tmp_path / "records.json"
    archivo.write_text(json.dumps([{"nombre": "LUI", "puntos": 120}, {"nombre": "ABC", "puntos": 80}]))
    tabla = TablaRecords(str(archivo))
    assert tabla.maximo("NORMAL") == 120
    assert tabla.filas("FACIL") == [] and tabla.filas("PESADILLA") == []


def test_cada_dificultad_tiene_su_tabla(tmp_path):
    archivo = tmp_path / "records.json"
    tabla = TablaRecords(str(archivo))
    tabla.agregar("AAA", 100, "FACIL")
    tabla.agregar("BBB", 50, "PESADILLA")
    assert tabla.maximo("FACIL") == 100 and tabla.maximo("PESADILLA") == 50 and tabla.maximo("NORMAL") == 0
    otra_vez = TablaRecords(str(archivo))
    assert otra_vez.filas("PESADILLA") == [{"nombre": "BBB", "puntos": 50}]


def test_records_deja_los_5_mejores_y_guarda(tmp_path):
    archivo = tmp_path / "records.json"
    tabla = TablaRecords(str(archivo))
    for puntos in [10, 50, 30, 20, 40, 5]:
        tabla.agregar("AAA", puntos, "NORMAL")
    assert [f["puntos"] for f in tabla.filas("NORMAL")] == [50, 40, 30, 20, 10]
    assert tabla.agregar("ZZZ", 45, "NORMAL") == 1
    assert not tabla.entra(15, "NORMAL") and tabla.entra(25, "NORMAL")
    assert tabla.entra(1, "DIFICIL")                # esa tabla esta vacia
    assert TablaRecords(str(archivo)).maximo("NORMAL") == 50


def test_records_sin_poder_escribir_no_se_cae(tmp_path):
    tabla = TablaRecords(str(tmp_path / "no_existe" / "records.json"))
    assert tabla.agregar("AAA", 10, "NORMAL") == 0


def test_opciones_de_fabrica_y_claves_que_faltan(tmp_path):
    # Un config.json viejo (sin "aviso_jefe") sigue sirviendo
    archivo = tmp_path / "config.json"
    archivo.write_text(json.dumps({"volumen": 4, "resolucion": "COMPLETA"}))
    opciones = Opciones(str(archivo))
    assert opciones.volumen == 4 and opciones.resolucion == "COMPLETA"
    assert opciones.volumen_musica == 10 and opciones.volumen_efectos == 10 and opciones.aviso_jefe
    assert not opciones.silencio and not opciones.audio_mono


def test_la_musica_y_los_efectos_viejos_en_no_pasan_a_volumen_0(tmp_path):
    # Antes eran SI/NO; ahora cada uno tiene su volumen
    archivo = tmp_path / "config.json"
    archivo.write_text(json.dumps({"volumen": 7, "musica": False, "efectos": True}))
    opciones = Opciones(str(archivo))
    assert opciones.volumen == 7 and opciones.volumen_musica == 0 and opciones.volumen_efectos == 10
    opciones.volumen_efectos, opciones.audio_mono = 4, True
    opciones.guardar()
    otra = Opciones(str(archivo))
    assert otra.volumen_musica == 0 and otra.volumen_efectos == 4 and otra.audio_mono
    archivo.write_text(json.dumps({"efectos": False}))
    assert Opciones(str(archivo)).volumen_efectos == 0


def test_opciones_dañadas_usan_las_de_fabrica(tmp_path):
    archivo = tmp_path / "config.json"
    archivo.write_text("[1, 2")
    opciones = Opciones(str(archivo))
    assert opciones.volumen == 10 and opciones.resolucion is None


def test_el_formato_viejo_se_ignora(tmp_path):
    # Antes se podia elegir 4:3 o 16:9; ahora el juego es siempre 16:9
    archivo = tmp_path / "config.json"
    archivo.write_text(json.dumps({"formato": "4:3", "volumen": 3}))
    opciones = Opciones(str(archivo))
    assert opciones.volumen == 3 and not hasattr(opciones, "formato")
    opciones.guardar()
    assert "formato" not in json.loads(archivo.read_text())


def test_opciones_se_guardan(tmp_path):
    archivo = tmp_path / "config.json"
    opciones = Opciones(str(archivo))
    opciones.aviso_jefe = False
    opciones.resolucion = "1280x720"
    opciones.guardar()
    guardado = json.loads(archivo.read_text())
    assert guardado["aviso_jefe"] is False and guardado["resolucion"] == "1280x720"
    otra_vez = Opciones(str(archivo))
    assert otra_vez.aviso_jefe is False and otra_vez.resolucion == "1280x720"

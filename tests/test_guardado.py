"""records.json y config.json: nunca hacen caer el juego."""
import json

from juego.guardado import TablaRecords, Opciones

NOMBRES = ["800x600", "COMPLETA"]


def test_records_si_no_existe_lo_crea(tmp_path):
    archivo = tmp_path / "records.json"
    tabla = TablaRecords(str(archivo))
    assert tabla.filas == [] and tabla.maximo == 0
    assert json.loads(archivo.read_text()) == []


def test_records_dañado_empieza_vacio(tmp_path):
    archivo = tmp_path / "records.json"
    archivo.write_text("esto no es json")
    assert TablaRecords(str(archivo)).filas == []


def test_records_deja_los_5_mejores_y_guarda(tmp_path):
    archivo = tmp_path / "records.json"
    tabla = TablaRecords(str(archivo))
    for puntos in [10, 50, 30, 20, 40, 5]:
        tabla.agregar("AAA", puntos)
    assert [f["puntos"] for f in tabla.filas] == [50, 40, 30, 20, 10]
    assert tabla.agregar("ZZZ", 45) == 1
    assert not tabla.entra(15) and tabla.entra(25)
    assert TablaRecords(str(archivo)).maximo == 50


def test_records_sin_poder_escribir_no_se_cae(tmp_path):
    tabla = TablaRecords(str(tmp_path / "no_existe" / "records.json"))
    assert tabla.agregar("AAA", 10) == 0


def test_opciones_de_fabrica_y_claves_que_faltan(tmp_path):
    archivo = tmp_path / "config.json"
    archivo.write_text(json.dumps({"volumen": 4, "resolucion": "COMPLETA"}))
    opciones = Opciones(str(archivo), NOMBRES)
    assert opciones.volumen == 4 and opciones.resolucion == 1
    assert opciones.musica and opciones.efectos and opciones.aviso_jefe


def test_opciones_dañadas_usan_las_de_fabrica(tmp_path):
    archivo = tmp_path / "config.json"
    archivo.write_text("[1, 2")
    opciones = Opciones(str(archivo), NOMBRES)
    assert opciones.volumen == 10 and opciones.resolucion == 0


def test_opciones_se_guardan(tmp_path):
    archivo = tmp_path / "config.json"
    opciones = Opciones(str(archivo), NOMBRES)
    opciones.aviso_jefe = False
    opciones.guardar()
    assert json.loads(archivo.read_text())["aviso_jefe"] is False
    assert Opciones(str(archivo), NOMBRES).aviso_jefe is False

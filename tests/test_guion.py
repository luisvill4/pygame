"""El guion (GUION.md) se arma con los textos del juego: si cambia un dialogo, hay que rehacerlo."""
from juego.config import ruta
from herramientas.guion import armar


def test_el_guion_esta_al_dia():
    # Si falla: correr  python herramientas/guion.py  (el guion nunca se edita a mano)
    with open(ruta("GUION.md"), encoding="utf-8") as archivo:
        assert archivo.read() == armar()


def test_el_guion_tiene_el_prologo_cada_mision_y_los_dos_finales():
    guion = armar()
    assert "## Prólogo" in guion and "GALAXIA ENANA" in guion
    assert guion.count("## Misión") == 6
    assert "EL ULTIMO" in guion and "SIN FECHA" in guion          # el encuentro y el final verdadero

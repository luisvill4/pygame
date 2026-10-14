"""
Las composiciones (patron Registry): cada funcion que arma una Obra se registra con
@obra("nombre_del_archivo") y herramientas/componer.py la encuentra sola.

    musica.py           los temas (dan la vuelta): el juego, el menu, la gasolinera...
    musica_jefes.py     un tema por jefe
    efectos_*.py        los efectos de sonido, por familia (ver LISTA_DE_SONIDOS.md)
"""
OBRAS = {}      # nombre del archivo (sin extension) -> funcion que devuelve la Obra


def _familia(prefijo, cuantos):
    return ["%s_%d" % (prefijo, numero) for numero in range(1, cuantos + 1)]


# Los efectos ARMONICOS: siguen al acorde de la musica (ver herramientas/estudio/armonia.py).
# Estan escritos en la pentatonica de Do y componer.py los compone una vez por color
# (moneda_1_fa.ogg...). Son los que tienen altura y suenan encima de la musica: premios,
# power-ups e interfaz. Los peligros no: su tension es fija (y de la escala del tema). Los
# de la gasolinera (tienda, caja) estan en Fa, la tonalidad de su tema, y tampoco. El Taller si:
# suena junto con las cartas, que siguen al acorde (fijo en Fa, chocaba con ellas).
# juego/sonido.py tiene la misma lista (un test comprueba que coincidan)
ARMONICOS = set(
    _familia("moneda", 5) + _familia("combo_sube", 3) + _familia("perfecto", 5) + _familia("roce_carga", 6)
    + _familia("hielo_roto", 3) + _familia("enemigo_roto", 3) + _familia("ui_mover", 2) + _familia("carta", 6)
    + _familia("contador", 8) + _familia("dificultad", 4)
    + ["oro_brillo", "combo_max", "interceptado", "nivel", "dash_listo", "nave_dash_extra", "capsula",
       "pw_escudo", "pw_hielo", "pw_vida", "pw_iman", "pw_doble", "pw_turbo", "pw_recarga", "pw_nova",
       "mejora_elegida", "eco", "bonus", "aturdido", "vulnerable", "desafio_nuevo", "desafio_cumplido",
       "oleada_superada", "logro", "nave_nueva", "bala_rota", "aparece", "retirada", "oro_llega",
       "ui_aceptar", "ui_volver", "ui_pestana", "ui_valor_sube", "ui_valor_baja", "ui_llave_si", "ui_llave_no",
       "carta_rara", "hangar_nave", "contador_fin", "taller",
       # los que se repiten todo el tiempo (y su tension la da el ritmo, no las notas)
       "compas", "compas_acento", "combo_cortado", "mina_tic", "pw_acaba", "pw_fin", "dash_vacio",
       "enjambre_picada"] + _familia("rebote", 4))


def obra(nombre):
    def registrar(funcion):
        OBRAS[nombre] = funcion
        return funcion
    return registrar


def cargar_todas():
    # Importar los modulos es lo que registra sus obras
    from herramientas.estudio.obras import (musica, musica_jefes, efectos_interfaz, efectos_juego,  # noqa: F401
                                            efectos_enemigos, efectos_director, efectos_jefes, ambiente)
    return OBRAS

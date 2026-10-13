"""
Configuracion: colores, paletas y todas las reglas que se pueden ajustar.

Aca van SOLO valores (numeros, colores, textos), nada de pygame ni de logica.
Asi se puede cambiar la dificultad sin miedo a romper nada.
"""
import os

# Carpeta raiz del proyecto (donde estan sprites/, efectos/ y fuentes/)
CARPETA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ruta(archivo):
    # Ruta de un archivo del juego, sin importar desde donde se ejecute
    return os.path.join(CARPETA, archivo)


# ================================== #
# ============ PANTALLA ============ #
# ================================== #

# El juego se dibuja en un lienzo de ANCHO x ALTO (16:9). La ventana puede ser mas
# grande: el lienzo se escala. Nunca escribir el ancho a mano: usar ANCHO y CENTRO_X
ANCHO = 1066
ALTO = 600
CENTRO_X = ANCHO // 2
ANCHO_MENU = 800                # los menus se dibujan en una zona central de este ancho
# Todos los sprites estan dibujados con "pixeles de arte" de 2x2 px del lienzo. Todo lo
# demas (particulas, halos, balas, ondas, sprites al pegarlos) se alinea a esta misma
# grilla, y el CRT pone una linea oscura por cada fila de pixeles de arte: asi nada se
# ve "mas fino" que el resto y las lineas calzan con los pixeles
PIXEL_ARTE = 2

# Frecuencia: la LOGICA del juego avanza siempre a 60 pasos por segundo (asi se siente igual
# a cualquier FPS) y se DIBUJA a la frecuencia elegida en Opciones (0 = sin limite).
# Todo lo que dice "por frame" en este archivo es por paso de logica (1/60 s)
PASOS_POR_SEGUNDO = 60
MS_POR_FRAME = 1000 / PASOS_POR_SEGUNDO     # cuanto avanza el reloj del juego en cada paso
FRECUENCIAS = [30, 60, 90, 120, 144, 0]     # opciones de FPS (0 = sin limite)
ATRASO_MAXIMO = 250             # ms: si la ventana se trabo mas que esto, no se intenta alcanzar

# Tamaños de ventana (nombre, ancho, alto)
RESOLUCIONES = [("1066x600", 1066, 600), ("1280x720", 1280, 720), ("1600x900", 1600, 900),
                ("1920x1080", 1920, 1080), ("COMPLETA", 0, 0)]
VOLUMEN_MAX = 10                # pasos de la barra de volumen (tambien es el volumen de fabrica)
FUNDIDO_MUSICA = 700            # ms que tarda un tema en apagarse (y el nuevo en subir) al cambiar

# Archivos que escribe el juego (se crean solos si no existen)
NOMBRE_RECORDS = "records.json"
NOMBRE_CONFIG = "config.json"
NOMBRE_PROGRESO = "progreso.json"   # logros, la nave elegida y cuantas partidas se jugaron

# ================================== #
# ============ COLORES ============= #
# ================================== #

BLANCO = (255, 255, 255)
GRIS = (130, 130, 160)
AMARILLO = (255, 221, 0)
ROJO = (255, 50, 70)
CIAN = (0, 230, 255)
MAGENTA = (255, 0, 170)
VERDE = (60, 255, 120)
HIELO = (140, 190, 255)
NARANJA = (255, 140, 0)
VIOLETA = (190, 120, 255)
FONDO = (6, 6, 18)
ARCOIRIS = [ROJO, AMARILLO, VERDE, CIAN, MAGENTA]

# Paletas de las particulas: van del color final (apagado) al inicial (brillante).
# Cada particula nace con el ultimo color y va bajando por la lista, como en las
# consolas antiguas que cambiaban de color en vez de usar transparencias.
FUEGO = [(120, 0, 30), ROJO, (255, 140, 0), AMARILLO, BLANCO]
ORO = [(150, 90, 0), AMARILLO, (255, 250, 180), BLANCO]
ESCARCHA = [(40, 60, 140), HIELO, BLANCO]
ENERGIA = [(0, 70, 110), CIAN, BLANCO]
CORAZON = [(120, 0, 30), ROJO, (255, 160, 170), BLANCO]
EMBESTIDA = [(90, 0, 60), MAGENTA, (255, 150, 230), BLANCO]
IMANTADO = [(90, 0, 60), MAGENTA, BLANCO]
TREBOL = [(0, 90, 40), VERDE, BLANCO]

# ================================== #
# ==== INTERFAZ Y ACCESIBILIDAD ==== #
# ================================== #

# Colores con un papel fijo: todas las pantallas los usan igual, asi el juego "habla"
# un solo idioma visual. Para cambiar el estilo de toda la interfaz, se cambia aca
TEXTO = BLANCO                  # lo que hay que leer
TEXTO_SUAVE = GRIS              # etiquetas y ayudas
TEXTO_APAGADO = (70, 80, 110)   # lo vacio o lo que no se puede usar
RESALTADO = AMARILLO            # lo elegido
CONTORNO = (8, 6, 22)           # borde de los textos que van encima del juego (se leen sobre cualquier fondo)
LINEA_APAGADA = (40, 60, 80)    # separadores y marcos de fondo
FILA_ELEGIDA = (16, 24, 52)     # franja detras de la fila elegida de un menu (no depende solo del color)
PANEL_FONDO = (10, 12, 32)      # el relleno de los paneles (interfaz.panel)
# Los botones del mando se dibujan con sus colores de siempre (las ayudas de pantalla)
COLORES_BOTON = {"A": (70, 200, 90), "B": (230, 60, 70), "X": (70, 140, 255), "Y": (240, 200, 40)}
TRANSICION_MS = 420             # cuanto dura la transicion entre pantallas (la mitad tapa, la mitad destapa)
ARCOIRIS_MS = 100               # ms que dura cada color del texto arcoiris

# Accesibilidad (Opciones > ACCESIBILIDAD; los efectos la consultan en accesibilidad.py)
# TEMBLOR: cuantos pasos de 2 px puede moverse la pantalla, como mucho
NIVELES_TEMBLOR = {"NO": 0, "SUAVE": 1, "NORMAL": 3}
ORDEN_TEMBLOR = ["NO", "SUAVE", "NORMAL"]
# DESTELLOS REDUCIDOS: sin destellos de pantalla completa y nada parpadea mas de 3 veces
# por segundo (lo que recomiendan las guias para personas con fotosensibilidad)
ORDEN_DESTELLOS = ["NORMALES", "REDUCIDOS"]
PARPADEO_MINIMO = 170           # ms: el parpadeo mas rapido con DESTELLOS REDUCIDOS
ARCOIRIS_REDUCIDO = 400         # ms por color del arcoiris con DESTELLOS REDUCIDOS
# CRT: brillo de las lineas horizontales (255 = sin lineas; mas bajo = mas oscuras)
NIVELES_CRT = {"NO": 255, "SUAVE": 215, "NORMAL": 185}
ORDEN_CRT = ["NO", "SUAVE", "NORMAL"]
# NEON: cuanto brillan las balas, la moneda, las capsulas y las explosiones (0 = nada)
NIVELES_NEON = {"NO": 0, "SUAVE": 0.55, "NORMAL": 1}
ORDEN_NEON = ["NO", "SUAVE", "NORMAL"]
# ESCALADO: NITIDO agranda sin suavizar (rapido; si la escala no es entera, unos pixeles
# salen mas anchos que otros). SUAVE agranda a un multiplo entero y despues achica
# suavizando: todos los pixeles iguales, con el borde apenas suave (mas lento)
ORDEN_ESCALADO = ["NITIDO", "SUAVE"]

# ================================== #
# ======== REGLAS DEL JUEGO ======== #
# ================================== #
# (cambialas para ajustar la dificultad)

COMBO_TIEMPO = 2000             # ms maximos entre monedas para seguir el combo
COMBO_MAXIMO = 5                # el multiplicador llega hasta x5
# Energia: todo lo que haces bien llena una barra y, llena, subis de nivel (ver Partida.ganar_energia)
ENERGIA_MONEDA = 1              # por moneda...
ENERGIA_COMBO = 0.25            # ...mas esto por cada paso del multiplicador del combo (x5: 2 por moneda)
ENERGIA_PERFECTO = 1.5          # por dash perfecto
ENERGIA_ENEMIGO = 0.5           # por enemigo destruido (o congelado roto)
ENERGIA_DESAFIO = 5             # por desafio cumplido
ENERGIA_OLEADA = 3              # por oleada superada
ENERGIA_INICIAL = 10            # lo que pide el nivel 1 para subir...
ENERGIA_POR_NIVEL = 1           # ...y esto mas en cada nivel...
ENERGIA_MAXIMA = 16             # ...hasta este tope
PUNTOS_ENEMIGO_CONGELADO = 5

# Nave
NAVE_VELOCIDAD = 5              # velocidad maxima
NAVE_ACELERACION = 0.15         # que tan rapido llega a la velocidad maxima (0 a 1)
NAVE_FRICCION = 0.88            # al soltar: 1 = patina sin parar, 0 = frena en seco
NAVE_FRENADO = 0.3              # al cambiar de direccion: que tan rapido se corrige la velocidad que
                                # va "para otro lado" (mas que NAVE_ACELERACION: dobla y frena enseguida)
NAVE_VELOCIDAD_GIRO = 15        # maximo de grados que gira en cada frame
INVULNERABLE_GOLPE = 1500       # ms sin recibir daño despues de perder una vida
INVULNERABLE_ESCUDO = 500       # ms sin recibir daño despues de que se rompe el escudo

# Dash
DASH_FUERZA = 14
DASH_DURACION = 180             # ms que dura el impulso (sin recibir daño)
DASH_RECARGA = 1500             # ms hasta poder usarlo otra vez
BUFFER_DASH = 150               # si apretas el dash hasta estos ms antes de que se recargue, sale igual
# Dash perfecto: destruir (o partir) con el dash a un enemigo destruible, o INTERCEPTAR al
# embestidor en plena embestida. Atravesar a los demas enemigos o a las balas no cuenta.
# Premio: puntos, el combo no se corta y el dash se recarga casi enseguida (se pueden encadenar)
DASH_PERFECTO_PUNTOS = 3        # por el multiplicador del combo
DASH_PERFECTO_RECARGA = 200     # ms hasta poder usar el dash otra vez despues de un perfecto
CADENA_PERFECTOS = 1500         # ms: otro perfecto antes de esto alarga la cadena (x2, x3...)
CADENA_MAXIMA = 5               # la cadena multiplica los puntos del perfecto hasta x5
INTERCEPTAR_PUNTOS = 10         # por frenar al embestidor con el dash en plena embestida...
ATURDIDO_INTERCEPTAR = 2000     # ...y los ms que queda aturdido (quieto y sin lastimar)

# Choques que hacen daño: circulos, asi la nave recibe el mismo golpe aunque este girada
RADIO_NAVE = 11
RADIO_ENEMIGO = 15
RADIO_BALA = 4

# Monedas: aparecen a esta distancia de la nave (asi siempre se llega antes de que se corte el combo)
MONEDA_DISTANCIA_MIN = 120
MONEDA_DISTANCIA_MAX = 450

# Power-ups
VELOCIDAD_POWERUP = 1.5         # px por frame que cae la capsula (con 1.5 cruza la pantalla en ~7 s)
PRIMER_POWERUP = 6000           # ms hasta que cae el primero
ESPERA_POWERUP = (8000, 13000)  # ms entre uno y otro (al azar entre estos dos)
TURBO_VELOCIDAD = 7             # velocidad maxima con TURBO (normal: NAVE_VELOCIDAD)
RECARGA_RAPIDA = 750            # ms de recarga del dash con RECARGA (normal: DASH_RECARGA)
DURACION = {                    # milisegundos que dura cada power-up temporal
    "escudo": 15000,
    "hielo": 5000,
    "iman": 7000,
    "doble": 8000,
}
NOVA_RADIO = 180                # NOVA: radio de la explosion al terminar el dash
ECO_RETRASO = 20                # mejora ECO: pasos que espera la copia antes de repetir tu dash
REPETIR_POWERUP = 0.35          # el mismo power-up dos veces seguidas tiene estas chances (de 1)

# Mejoras: cartas que se eligen durante la partida y duran hasta el Game Over (ver mejoras.py).
# Se ofrecen 3 al azar al llegar a MEJORA_PRIMER_NIVEL y al cerrar cada sector.
# Las listas tienen un valor por nivel de la mejora (elegirla dos veces = segundo valor)
MEJORA_PRIMER_NIVEL = 3
MEJORA_RECARGA = 0.2            # RECARGA: el dash se recarga esta parte mas rapido (por nivel)
MEJORA_ONDA_RADIO = [70, 100]   # ONDA: radio de la onda al terminar el dash
MEJORA_COMETA = 1.5             # COMETA: el dash dura esto por su duracion normal
MEJORA_FILO_PUNTOS = 3          # FILO: puntos por un enemigo que normalmente el dash no destruye
MEJORA_ROCE = [6, 4, 3]         # ESCUDO ROCE: dash perfectos para regenerar el escudo (por nivel).
                                # Ese escudo dura hasta que te pegan; mientras lo tenes, no se cuenta
MEJORA_ATRACCION = [110, 170]   # ATRACCION: px desde los que la moneda viene sola
MEJORA_COMBO = 0.3              # COMBO LARGO: el combo tarda esta parte mas en cortarse (por nivel)
MEJORA_SUERTE = 0.25            # SUERTE: esta parte menos de espera entre power-ups (por nivel)
MEJORA_POTENCIA = 0.4           # POTENCIA: esta parte mas de duracion de los power-ups (por nivel)
MEJORA_MOTOR = 0.12             # MOTOR: esta parte mas de velocidad (por nivel)
MEJORA_ECO = [0.25, 0.45]       # ECO: chances de que un dash deje una copia que lo repite
FENIX_INVULNERABLE = 2500       # FENIX: ms sin recibir daño al volver
# Gasolinera: despues de cada jefe se para a cargar combustible y a comprar con los
# CREDITOS que dan las monedas (ver tienda.py y escenas/gasolinera.py). Las cartas del
# nivel 3 siguen siendo gratis (el Taller): la gasolinera es la unica que cobra.
# Los creditos no son puntos: gastarlos no baja el puntaje (los records no cambian)
CREDITOS_POR_MONEDA = 1         # por el multiplicador del combo (con x5, 5 por moneda)
TIENDA_CARTAS = 3               # cartas en el mostrador
PRECIO_CARTA = 40               # una carta comun, si todavia no la tenes...
PRECIO_POR_NIVEL = 25           # ...y esto mas por cada nivel que ya tenes de ella
PRECIO_RARA = 1.5               # las raras (peso menor a 1) cuestan esto por el precio
PRECIO_POR_SECTOR = 0.2         # todo sube esta parte en cada sector (se juntan mas creditos)
# (Medido con un bot: un sector da ~50-70 creditos jugando flojo y ~100-180 jugando bien,
#  porque el combo multiplica los creditos. Con estos precios: 1 carta o 2-3 por parada)
PRECIO_SORTEAR = 15             # cambiar las cartas del mostrador (cada vez que sorteas, esto mas)
PRECIO_ESCUDO = 35              # un escudo que dura hasta el proximo golpe
PRECIO_REPARAR = 60             # recuperar una vida
# Ondas (la mejora ONDA y el power-up NOVA): rompen balas, destruyen a los destruibles y a
# los demas los empujan y los dejan ATURDIDOS (quietos y sin lastimar) un rato
ATURDIDO_ONDA = 1200            # ms
EMPUJE_ONDA = 60                # px

# Enemigos
AVISO_APARICION = 800           # ms que se ve la "X" antes de que aparezca un enemigo
DISTANCIA_APARICION = 300       # los enemigos aparecen a mas de esta distancia de la nave
ENEMIGO_VELOCIDAD_MAX = 4.2     # los que te persiguen nunca van mas rapido que esto (la nave va a 5):
                                # asi siempre se puede escapar. Los ataques con aviso (embestidas, picadas) si

# Presupuesto de amenaza: cada enemigo "cuesta" puntos y cada nivel tiene un presupuesto.
# El juego elige al azar que enemigos poner hasta gastarlo (entre los ya desbloqueados),
# asi cada partida es distinta pero la dificultad sigue controlada (ver progresion.py)
COSTO_ENEMIGO = {"rebotador": 1, "perseguidor": 2, "embestidor": 3, "divisor": 4, "enjambre": 3}
DESBLOQUEO_ENEMIGO = {"perseguidor": 1, "rebotador": 2, "embestidor": 3,   # nivel desde el que aparece
                      "divisor": 4, "enjambre": 7}
REFUERZO_ESPERA = 5000          # ms: si destruiste enemigos, cada tanto llega otro hasta llenar el presupuesto
RECARGA_POR_DESTRUIR = 400      # ms que se adelanta la recarga del dash por cada enemigo que destruye

# Divisor: masa verde que el dash parte en dos (grande -> 2 medianos -> 2 chicos cada uno)
DIVISOR_VELOCIDAD = {"divisor": 0.9, "divisor_mediano": 1.6, "divisor_chico": 2.4}
DIVISOR_PUNTOS = {"divisor": 2, "divisor_mediano": 3, "divisor_chico": 5}
DIVISOR_NACIMIENTO = 450        # ms que parpadean los hijos al nacer (sin hacer daño)

# Enjambre: drones que vuelan en formacion; el dash los destruye de a uno
ENJAMBRE_CANTIDAD = 5
ENJAMBRE_VELOCIDAD = 1.4        # velocidad del grupo
ENJAMBRE_PICADA = 3.8           # velocidad cuando se lanza en picada contra la nave
ENJAMBRE_ESPERA_PICADA = (3500, 5500)   # ms entre picadas (al azar)
ENJAMBRE_PUNTOS = 2             # por dron
ENJAMBRE_BONUS = 10             # por destruir el enjambre entero con el dash
PRESUPUESTO_INICIAL = 2
PRESUPUESTO_POR_NIVEL = 1.8
PRESUPUESTO_MAXIMO = 24
ENEMIGOS_MAX = 10               # nunca mas que esto en pantalla (sin contar las oleadas)

# Oleadas: cada tanto llegan muchos enemigos de golpe por unos segundos y despues se van
OLEADA_DESDE_NIVEL = 2
OLEADA_ESPERA = (35000, 55000)  # ms de juego entre una oleada y la siguiente (al azar)
OLEADA_DURACION = 12000         # ms que dura
OLEADA_PRESUPUESTO = 0.6        # enemigos extra: esta parte del presupuesto del nivel
OLEADA_PUNTOS = 10              # bonus por nivel si la pasas sin perder una vida

# Los que persiguen se separan entre si, para no terminar todos encimados en el mismo punto
SEPARACION_ENEMIGOS = 50        # distancia (px) a la que empiezan a alejarse de otro enemigo
FUERZA_SEPARACION = 0.3         # que tan fuerte se alejan (mas = se separan mas rapido)
# El embestidor solo te sigue (y te embiste) si estas a menos de esta distancia; si no, deambula
RANGO_EMBESTIDOR = 250

# Jefes: se les pega con el dash en el nucleo cuando quedan cansados
JEFE_PULSO = 500                # ms de un "pulso": el tempo de las peleas (ver jefes/base.py)
JEFE_CADA_NIVELES = 5           # aparece al llegar a los niveles 5, 10, 15... (cual: el del sector)
JEFE_VIDA = 3                   # golpes que aguanta el primero (cada 2 jefes vencidos, uno mas)
JEFE_PUNTOS = 50                # bonus al vencerlo (el segundo da el doble, el tercero el triple...)
JEFE_FLOTAR = 2500              # ms que se mueve de lado a lado antes de atacar
JEFE_CANSADO = 2500             # ms que deja el nucleo al descubierto
JEFE_RAFAGAS = 3                # rafagas de balas en cada ataque
CARTEL_JEFE = 2000              # ms que se ve "¡JEFE VENCIDO!" (los enemigos vuelven despues)
CARTEL_SECTOR = 2500            # ms que se ve el cartel del sector nuevo
# Avisos de la franja de arriba: salen de a uno, en una cola (ver avisos.py). Ms que se ve cada uno
AVISO_NIVEL = 1800              # "NIVEL 7" y cuanto falta para el jefe
AVISO_OLEADA = 2200             # "¡OLEADA!" y "¡OLEADA SUPERADA!"
AVISO_ANOMALIA = 3200           # el nombre de la anomalia y su consejo
AVISO_RECORD = 2400             # "¡NUEVO RECORD!"
# Carteles y fichas que tapan algo (la nave, la moneda, un enemigo, una bala...) se vuelven
# casi transparentes, asi se sigue leyendo el mensaje sin perder de vista el juego
CARTEL_ALFA_TAPANDO = 70        # opacidad (0 = invisible, 255 = normal) mientras tapa algo
CARTEL_MARGEN = 24              # px alrededor del cartel que ya cuentan como "debajo"
CARTEL_ESPERA_TAPANDO = 300     # ms que sigue transparente despues (asi no titila en el borde)
CARTEL_ALFA_MOMENTO = 150       # lo mismo para los momentos (jefe vencido, rango, sector): no hay peligro

# La Fortaleza: una marcha militar. Cada "compas" un cañon se carga, dispara a ritmo y
# queda RECALENTADO: ahi se le pega con el dash. Un ataque por vez, siempre con aviso.
# Sin cañones se le cae la coraza: tira cortinas de escombros y CAE sobre vos; al caer
# queda aturdida con el nucleo a la vista. (Las duraciones van en pulsos, ver JEFE_PULSO)
FORTALEZA_VIDA_CANON = 2        # golpes que aguanta cada cañon
FORTALEZA_PUNTOS_CANON = 10     # puntos por romper un cañon
FORTALEZA_PULSOS = [520, 480, 440, 400, 400]  # ms del pulso con 0, 1, 2, 3 y 4 cañones rotos (se acelera)
FORTALEZA_RECALENTADO = 5       # pulsos que queda recalentado
FORTALEZA_MISIL_GUIADO = 2600   # ms que te sigue un misil (despues sigue derecho)
FORTALEZA_LASER_VELOCIDAD = 2.4 # px por paso que barre el laser
FORTALEZA_ATURDIDA = 6          # pulsos que queda aturdida despues de caer
FORTALEZA_FIJAR = 2             # pulsos quieta antes de caer (tiempo para salir de abajo: es ancha)
FORTALEZA_MARGEN_GOLPE = 12     # px de mas alrededor de cada cañon para pegarle con el dash
                                # (solo para pegarle: para el daño que te hace no cuenta)

# La Serpiente: un jefe de movimiento (casi sin balas). Nada a tu alrededor, acecha,
# MUERDE en linea recta y si se golpea contra un borde queda aturdida con la COLA
# brillando: ahi se la cortas con el dash. Cada corte la deja mas corta y mas rapida.
# Desde el segundo corte tambien se enrosca a tu alrededor (escapate antes de que apriete)
SERPIENTE_PULSOS = (460, 380)   # ms del pulso al empezar y al final (se acelera con cada corte)
SERPIENTE_VELOCIDAD = 3.2       # px por paso nadando (sube un 8% por corte)
SERPIENTE_GIRO = 0.06           # cuanto puede doblar por paso (radianes)
SERPIENTE_MORDIDA = 10          # px por paso al morder
SERPIENTE_ESPACIO = 26          # px entre un segmento y el siguiente
SERPIENTE_CUELLO = 4            # segmentos que no se cortan (cortes = vida del jefe)
SERPIENTE_CORTES_EXTRA = 2      # cortes de mas (un corte de cola es un golpe "chico")
SERPIENTE_VENTANA = 5           # pulsos que la cola brilla despues de chocar (la ventana para cortarla)

# La Colmena: una madre que defiende a sus hijas. Abre una compuerta (tiembla y zumba),
# suelta abejas a ritmo y la deja ABIERTA un rato: ahi se rompe con el dash. Sin
# compuertas, EMBISTE rebotando en las paredes (el aviso dibuja el camino con los
# rebotes) y al terminar queda aturdida con el ojo de la reina a la vista
COLMENA_PULSO = 480             # ms del pulso
COLMENA_ABEJAS = 3              # abejas que suelta cada compuerta (una por pulso)
COLMENA_ABEJAS_MAX = 4          # nunca mas abejas que esto a la vez
COLMENA_EXPUESTA = 5            # pulsos que la compuerta queda abierta
COLMENA_EMBESTIDA = 7.5         # px por paso al embestir
COLMENA_REBOTES = 1             # rebotes de la primera embestida (uno mas por cada golpe al ojo)
COLMENA_ATURDIDA = 5            # pulsos que queda aturdida despues de embestir
# La Singularidad: un agujero negro en el centro. Te atrae todo el tiempo, la rodea un
# anillo de asteroides con huecos que gira de a un hueco por pulso (tic, tic...), suelta
# brazos de balas en espiral, INHALA (te tira fuerte) y EXHALA una nova con un hueco.
# Cuando COLAPSA, el nucleo queda a la vista: entra por un hueco del anillo y ¡DASH!
SINGULARIDAD_PULSO = 450        # ms del pulso
SINGULARIDAD_GRAVEDAD = 0.16    # cuanto te atrae por paso (normal)
SINGULARIDAD_INHALAR = 0.42     # cuanto te atrae mientras inhala
SINGULARIDAD_RADIO = 150        # radio del anillo de asteroides
SINGULARIDAD_HUECOS = 3         # huecos del anillo al empezar (de 12 lugares; uno menos cada 2 golpes)
SINGULARIDAD_EXPUESTA = 6       # pulsos con el nucleo a la vista
ABEJA_VELOCIDAD = 2.6           # rondando a tu alrededor
ABEJA_PICADA = 6.5              # al picar
ABEJA_PUNTOS = 2

# Anomalias: una vez por sector el espacio se pone raro un rato (ver anomalias.py).
# Cada sector tiene la suya ("anomalia" en SECTORES), pero no siempre llega esa: asi las
# cuatro se pueden ver desde el primer sector (antes la fiebre del oro recien salia en el nivel 18)
ANOMALIA_PROPIA = 0.5           # chances de que llegue la del sector (si no, una de las otras)
ANOMALIA_NIVEL = 3              # llega en el 3er nivel de cada sector (niveles 3, 8, 13...)
ANOMALIA_ESPERA = 4000          # ms desde que empieza ese nivel
ANOMALIA_DURACION = 20000       # ms que dura
RESPIRO_ANOMALIA = 10000        # ms sin oleadas despues de una anomalia
ASTEROIDES_ESPERA = 1000        # ms entre un asteroide y el siguiente
ASTEROIDES_AVISO = 900          # ms que se ve la columna de aviso antes de que caiga
ASTEROIDES_VELOCIDAD = 5        # px por paso al caer
ASTEROIDES_PUNTOS = 3           # por romperlo con el dash
TORMENTA_AVISO = 1200           # ms que parpadea la franja antes de quemar
TORMENTA_LLAMARADA = 450        # ms que quema
TORMENTA_CALMA = 2000           # ms de calma entre una llamarada y la siguiente
TORMENTA_ANCHO = 90             # ancho de la franja
NIEBLA_RADIO = 170              # lo que se ve alrededor de la nave
ORO_MULTIPLICADOR = 2           # en la fiebre del oro las monedas valen el doble...
ORO_COMBO = 1.5                 # ...y el combo tarda 1.5 veces mas en cortarse

# Desafios: un reto opcional por sector (ver desafios.py). Si lo cumplis: puntos y un power-up
DESAFIO_DESDE_NIVEL = 2         # el primero se propone en el nivel 2; despues, al llegar a cada sector
DESAFIO_ESPERA = 3000           # ms despues de eso (para que no se pise con los otros carteles)
DESAFIO_PUNTOS = 50             # premio por el numero de sector (el sector 3 da 150)
DESAFIO_COMBO = 12              # "SIN CORTAR EL COMBO": monedas seguidas
DESAFIO_CAZADOR = 6             # "CAZADOR": enemigos destruidos con el dash
DESAFIO_INTERCEPTAR = 3         # "INTERCEPTOR": embestidores frenados con el dash

# Rango: al vencer al jefe, una nota de S a C para el sector (ver rango.py)
CARTEL_RANGO = 4500             # ms que se ve el cartel del rango (despues de "¡JEFE VENCIDO!")
RANGO_SELLO = 2100              # ms del cartel en que cae la letra (antes van saliendo las filas)
RANGO_COMBO = 12                # monedas seguidas que dan la estrella del combo (x5)
RANGO_TIEMPO_JEFE = {           # ms para la estrella de "jefe rapido" (20% mas en cada vuelta)
    "ojo": 40000, "fortaleza": 90000, "serpiente": 55000, "colmena": 70000, "singularidad": 70000,
}
RANGO_PUNTOS = {"S": 150, "A": 100, "B": 50, "C": 0}

# Modo desarrollador: F1 en plena partida abre un panel para traer jefes, enemigos y
# power-ups (ver escenas/desarrollador.py). Una partida que lo usa no guarda record ni logros
MODO_DESARROLLADOR = True       # False lo apaga (por ejemplo, para pasarle el juego a otros)

# ================================== #
# ===== DIFICULTAD Y SECTORES ====== #
# ================================== #

# Cada dificultad tiene su propia tabla de records.
#   vidas:          vidas al empezar (y maximas)
#   velocidad:      multiplica la velocidad de enemigos y balas
#   presupuesto:    multiplica el presupuesto de enemigos (mas o menos enemigos)
#   espera_powerup: multiplica la espera entre power-ups (mas = caen menos seguido)
#   apunte_fijo:    ms antes de embestir en que el embestidor deja de seguirte con la mira:
#                   embiste hacia donde estabas un momento antes (0 = te sigue hasta el final)
#   servicios:      lo que vende la gasolinera ademas de las cartas (ver tienda.py)
ORDEN_DIFICULTADES = ["FACIL", "NORMAL", "DIFICIL", "PESADILLA"]
DIFICULTADES = {
    "FACIL": {"color": VERDE, "paleta": TREBOL, "calaveras": 1, "vidas": 5, "velocidad": 0.8,
              "presupuesto": 0.7, "espera_powerup": 0.8, "apunte_fijo": 350,
              "servicios": ["sortear", "escudo", "reparar"],
              "descripcion": ["5 VIDAS", "ENEMIGOS MAS LENTOS", "MAS POWER-UPS"]},
    "NORMAL": {"color": CIAN, "paleta": ENERGIA, "calaveras": 2, "vidas": 3, "velocidad": 1.0,
               "presupuesto": 1.0, "espera_powerup": 1.0, "apunte_fijo": 200,
               "servicios": ["sortear", "escudo"],
               "descripcion": ["3 VIDAS", "EL DESAFIO ORIGINAL", ""]},
    "DIFICIL": {"color": AMARILLO, "paleta": ORO, "calaveras": 3, "vidas": 3, "velocidad": 1.15,
                "presupuesto": 1.3, "espera_powerup": 1.3, "apunte_fijo": 0,
                "servicios": ["sortear"],
                "descripcion": ["3 VIDAS", "ENEMIGOS 15% MAS RAPIDOS", "MAS ENEMIGOS, MENOS POWER-UPS"]},
    "PESADILLA": {"color": ROJO, "paleta": FUEGO, "calaveras": 4, "vidas": 1, "velocidad": 1.3,
                  "presupuesto": 1.6, "espera_powerup": 1.6, "apunte_fijo": 0,
                  "servicios": [],
                  "descripcion": ["1 VIDA", "ENEMIGOS 30% MAS RAPIDOS", "SIN PIEDAD"]},
}

# Sectores (biomas): cada uno termina con SU jefe, y al vencerlo se pasa al siguiente.
# Despues del ultimo se vuelve al primero (los jefes aguantan mas cada vez).
#   tinte:     tiñe nebulosas y planetas (None = colores originales)
#   fondo:     el color del espacio
#   ambiente:  las particulas del fondo (ver fondo.py): asteroides, brasas, esporas, panal o abismo
#   estrellas: cuanto de rojo, verde y azul tienen las estrellas (1 = blancas)
#   favorito:  el enemigo que mas aparece; lema: la frase del cartel al llegar
#   anomalia:  la que suele llegar a mitad del sector (ANOMALIA_PROPIA; None = una al azar)
# Ningun color del fondo pasa de ~110 por canal, para que no se confunda con enemigos
PESO_FAVORITO = 3               # el enemigo favorito del sector sale 3 veces mas seguido
RECAMBIO_SECTOR = 0.34          # al cambiar de sector se va esta parte de los enemigos (vienen otros)
SECTORES = [
    {"nombre": "CINTURON EXTERIOR", "lema": "DONDE EMPIEZA TODO", "color": CIAN, "jefe": "ojo",
     "tinte": None, "fondo": FONDO, "ambiente": "asteroides", "estrellas": (1, 1, 1),
     "favorito": "perseguidor", "anomalia": "asteroides"},
    {"nombre": "NEBULOSA CARMESI", "lema": "EL AIRE ARDE", "color": ROJO, "jefe": "fortaleza",
     "tinte": (110, 35, 50), "fondo": (16, 4, 8), "ambiente": "brasas", "estrellas": (1, 0.7, 0.7),
     "favorito": "embestidor", "anomalia": "tormenta"},
    {"nombre": "CAMPO ESMERALDA", "lema": "ALGO SE MUEVE ENTRE LAS ESPORAS", "color": VERDE, "jefe": "serpiente",
     "tinte": (35, 105, 70), "fondo": (4, 14, 10), "ambiente": "esporas", "estrellas": (0.75, 1, 0.8),
     "favorito": "divisor", "anomalia": "niebla"},
    {"nombre": "MAR DE AMBAR", "lema": "LA COLMENA TE OBSERVA", "color": AMARILLO, "jefe": "colmena",
     "tinte": (110, 80, 30), "fondo": (14, 10, 4), "ambiente": "panal", "estrellas": (1, 0.85, 0.6),
     "favorito": "enjambre", "anomalia": "oro"},
    {"nombre": "ABISMO AZUL", "lema": "NI LA LUZ ESCAPA", "color": HIELO, "jefe": "singularidad",
     "tinte": (35, 65, 110), "fondo": (4, 6, 20), "ambiente": "abismo", "estrellas": (0.7, 0.8, 1),
     "favorito": "rebotador", "anomalia": None},
]
TRANSICION_SECTOR = 60          # pasos (1 s) que tarda el fondo en cambiar de color, en 4 etapas

# Animaciones: milisegundos que dura cada cuadro (menos = mas rapido)
MS_CUADRO_ENEMIGO = 250
MS_CUADRO_MONEDA = 100
MS_CUADRO_ESCUDO = 150
MS_CUADRO_JEFE = 200
MS_CUADRO_REBOTE = 70           # cada cuadro del rebotador aplastandose contra una pared

# Fondo con paralaje: lo lejano se mueve lento y lo cercano rapido
REACCION_PARALAJE = 0.15        # cuanto se corre el fondo cuando se mueve la nave
PROFUNDIDAD = {                 # velocidad de cada capa (las estrellas van de 1 a 3)
    "nebulosa": 0.15,
    "planeta_chico": 0.3,
    "planeta_grande": 0.6,
}

# Naves: colores que se desbloquean con logros (ver logros.py). Se eligen en la pantalla LOGROS.
# (nombre, color con el que se tiñe el sprite (None = el original), logro que la desbloquea (None = siempre))
NAVES = [
    ("ORIGINAL", None, None),
    ("CIAN", CIAN, "primer_jefe"),
    ("MAGENTA", MAGENTA, "al_filo"),
    ("FUEGO", NARANJA, "cazador"),
    ("HIELO", HIELO, "intocable"),
    ("DORADA", AMARILLO, "rango_s"),
    ("VIOLETA", VIOLETA, "arsenal"),
    ("FANTASMA", BLANCO, "viajero"),
    ("SANGRE", ROJO, "sin_piedad"),
]

# Records: letras que se pueden usar en las iniciales
ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
FILAS_RECORDS = 5

# ================================== #
# ============= MANDO ============== #
# ================================== #

# Numeros de los botones del mando de Xbox (mapeo de SDL en Windows) y la accion de cada uno.
# Las acciones estan en entrada.py
BOTON_A = 0
BOTON_B = 1
BOTON_X = 2
BOTON_Y = 3
BOTON_LB = 4                    # los gatillos chicos de arriba (bumpers): cambian de pestaña
BOTON_RB = 5
BOTON_VISTA = 6                 # el de los dos cuadraditos
BOTON_MENU = 7                  # el de las tres rayitas
ZONA_MUERTA = 0.5               # en los menus: cuanto hay que inclinar el stick para que cuente (0 a 1)
ZONA_MUERTA_NAVE = 0.25         # al mover la nave (mas chica, para que responda enseguida)

# ---------- Vibracion (ver haptica.py) ----------
# La opcion VIBRACION multiplica todos los patrones (FUERTE pasa de 1, pero cada motor llega hasta 1)
NIVELES_VIBRACION = {"NO": 0, "SUAVE": 0.5, "NORMAL": 1, "FUERTE": 1.5}
ORDEN_VIBRACION = ["NO", "SUAVE", "NORMAL", "FUERTE"]

# Patrones: nombre -> (prioridad, pasos). Cada paso es (ms, grave, agudo), con fuerzas de 0 a 1.
# Un paso en 0 es un silencio (para separar dos pulsos). Para que se sienta SUAVE: fuerzas bajas,
# mas agudo que grave (el grave es el que se siente brusco) y que suba y baje de a poco.
# Solo vibra lo importante: lo que pasa todo el tiempo (cada moneda, cada dash) no vibra.
# Prioridad: 1 chico, 2 mediano, 3 fuerte, 4 enorme. Uno de menos prioridad no corta al que suena
VIBRACIONES = {
    # --- Premios ---
    "combo_sube":      (1, [(50, 0, 0.15), (60, 0, 0.25), (60, 0, 0.1)]),
    "combo_maximo":    (2, [(60, 0, 0.15), (80, 0.08, 0.3), (80, 0.05, 0.2), (80, 0, 0.08)]),
    "powerup":         (1, [(60, 0, 0.12), (80, 0, 0.22), (60, 0, 0.08)]),
    "subir_nivel":     (2, [(80, 0.04, 0.15), (100, 0.08, 0.22), (80, 0, 0.08)]),
    "mejora":          (2, [(80, 0.04, 0.18), (100, 0, 0.08)]),
    "record":          (2, [(80, 0, 0.15), (100, 0.05, 0.25), (100, 0, 0.08)]),
    "logro":           (2, [(60, 0, 0.18), (60, 0, 0), (120, 0.04, 0.25), (80, 0, 0.08)]),
    "desafio":         (2, [(70, 0, 0.18), (60, 0, 0), (100, 0.04, 0.25), (80, 0, 0.08)]),
    "sello":           (2, [(80, 0.2, 0.12), (100, 0.06, 0.04)]),       # la letra del rango cae

    # --- Enemigos ---
    "destruir":        (1, [(50, 0.06, 0.2), (60, 0, 0.08)]),
    "perfecto":        (1, [(50, 0, 0.25), (70, 0.04, 0.1)]),
    "interceptar":     (2, [(70, 0.18, 0.25), (80, 0.06, 0.08)]),
    "hielo_roto":      (1, [(60, 0, 0.18), (60, 0, 0.06)]),
    "nova":            (2, [(100, 0.25, 0.25), (120, 0.14, 0.12), (120, 0.05, 0.04)]),

    # --- Golpes a la nave (suben un instante antes del pico, asi no es un latigazo) ---
    "escudo_roto":     (3, [(60, 0.08, 0.25), (100, 0.04, 0.1)]),
    "golpe":           (3, [(50, 0.15, 0.2), (120, 0.35, 0.3), (120, 0.15, 0.12), (100, 0.05, 0.04)]),
    "fenix":           (4, [(200, 0.08, 0.12), (200, 0.18, 0.22), (250, 0.3, 0.3), (200, 0.1, 0.08)]),
    "muerte":          (4, [(80, 0.3, 0.25), (200, 0.5, 0.4), (250, 0.3, 0.25), (300, 0.15, 0.1),
                            (300, 0.05, 0.03)]),

    # --- La partida ---
    "oleada":          (2, [(120, 0.15, 0), (100, 0, 0), (120, 0.15, 0)]),        # alarma
    "anomalia":        (1, [(300, 0.08, 0.04), (300, 0.04, 0)]),

    # --- Jefes ---
    "jefe_llega":      (3, [(80, 0.2, 0), (90, 0, 0), (100, 0.3, 0), (420, 0, 0),
                            (80, 0.2, 0), (90, 0, 0), (100, 0.3, 0)]),              # latido
    "jefe_golpe":      (3, [(70, 0.18, 0.3), (120, 0.08, 0.12)]),
    "jefe_parte":      (2, [(60, 0.1, 0.22), (80, 0.04, 0.08)]),
    "parte_rota":      (3, [(100, 0.25, 0.3), (150, 0.1, 0.12), (100, 0.04, 0.04)]),
    "jefe_explota":    (4, [(100, 0.25, 0.25), (200, 0.45, 0.45), (250, 0.3, 0.3), (300, 0.15, 0.12),
                            (300, 0.05, 0.03)]),
    "impacto":         (2, [(100, 0.18, 0.1), (100, 0.06, 0)]),      # el jefe choca una pared
    "impacto_grande":  (3, [(60, 0.15, 0.08), (140, 0.32, 0.15), (160, 0.1, 0.04)]),   # la Fortaleza cae
    "coraza":          (3, [(150, 0.28, 0.28), (250, 0.1, 0.1)]),
    "aviso_jefe":      (1, [(60, 0, 0.15), (60, 0, 0), (60, 0, 0.15)]),           # "¡movete!"
    "zumbido":         (1, [(240, 0, 0.08), (240, 0, 0.12)]),                     # la Colmena tiembla
    "inhalar":         (1, [(150, 0.03, 0), (150, 0.05, 0), (150, 0.08, 0), (150, 0.1, 0.02),
                            (150, 0.13, 0.04), (150, 0.16, 0.06)]),               # crece de a poco
    "exhalar":         (2, [(110, 0.25, 0.22), (130, 0.08, 0.07)]),

    # --- Menus ---
    "prueba":          (2, [(150, 0.2, 0), (100, 0, 0), (150, 0, 0.25)]),         # cada motor por turno
    "pesadilla":       (2, [(80, 0.1, 0.15), (150, 0.2, 0.3), (100, 0.05, 0.08)]),
}

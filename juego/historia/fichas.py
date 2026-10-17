"""
Las fichas del Archivo: el PORQUE de cada cosa del juego, contado por Ines (HISTORIA.md,
seccion 4). Enemigos, jefes, power-ups, anomalias y lo basico (la Marea, el compas...).

No son secretos: se anotan solas la primera vez que las VES en una mision (el ModoHistoria
mira la pantalla de vez en cuando). Pero algunas esconden pistas de los secretos, y otras
apuntan a la verdad de fondo sin decirla ("¿como sabian las medidas de la Alondra?").

Solo datos. Cada ficha: su id ("enemigo:perseguidor"), la seccion del Archivo, el nombre y
los parrafos. 'glifo' (opcional) se dibuja como en los fragmentos. Las imagenes las pone el
Archivo (escenas/historia/archivo.py) segun la categoria del id.
Un enemigo, jefe, power-up o anomalia nuevo NECESITA su ficha: test_historia.py lo exige
(asi todo lo que se agregue al juego tiene su porque).
"""
from juego.historia.glifos import escribir

CRIATURAS, TECNOLOGIA, FENOMENOS = "CRIATURAS", "TECNOLOGIA", "FENOMENOS"
SECCIONES = [CRIATURAS, TECNOLOGIA, FENOMENOS]

# Los que no tienen ficha propia: comparten la de otro (los pedazos del divisor)
MISMA_FICHA = {"enemigo:divisor_mediano": "enemigo:divisor", "enemigo:divisor_chico": "enemigo:divisor"}

# Las que se anotan al empezar la primera mision (lo que Alba ya sabe al despegar)
BASICAS = ["fenomeno:marea", "fenomeno:compas", "fenomeno:monedas", "tecnologia:alondra"]


class Ficha:
    def __init__(self, id_, seccion, nombre, texto, glifo=None):
        self.id = id_
        self.seccion = seccion
        self.nombre = nombre
        self.texto = texto
        self.glifo = glifo

    @property
    def categoria(self):
        # "enemigo:perseguidor" -> ("enemigo", "perseguidor")
        return tuple(self.id.split(":", 1))


FICHAS = [
    # ---------- Criaturas: los enemigos ----------
    Ficha("enemigo:perseguidor", CRIATURAS, "CENTINELA",
          ["LOS PERSEGUIDORES. CUIDAN EL CAMINO.",
           "NO BUSCAN MATAR: ALEJAN A CUALQUIERA QUE SE ACERQUE A LAS MONEDAS.",
           "INES: ¿Y SI NO LAS CUIDAN DE NOSOTROS, SINO PARA NOSOTROS?"]),
    Ficha("enemigo:rebotador", CRIATURAS, "REBOTADOR",
          ["UNA CAPSULA DE MEMORIA DAÑADA.",
           "REBOTA SIN RUMBO REPITIENDO UN MISMO SEGUNDO DEL PASADO, UNA Y OTRA VEZ.",
           "INES GRABO UNO: ADENTRO SE OYE UN PEDAZO DEL COMPAS, TRABADO."]),
    Ficha("enemigo:embestidor", CRIATURAS, "EMBESTIDOR",
          ["UN ARIETE DE CONSTRUCCION. ABRIO LOS TUNELES DEL CINTURON.",
           "FIJA EL RUMBO ANTES DE EMBESTIR PORQUE NUNCA APRENDIO A DOBLAR.",
           "SI LO CRUZAS CON EL DASH, SE QUEDA QUIETO, ESPERANDO UNA ORDEN."]),
    Ficha("enemigo:divisor", CRIATURAS, "DIVISOR",
          ["UNA ESPORA DE TERRAFORMACION.",
           "AL ROMPERSE SE REPARTE, PARA SEMBRAR. ALGUIEN QUERIA QUE ALGO CRECIERA ACA.",
           "EL CAMPO ESMERALDA ES LO QUE PASA CUANDO LAS DEJAN TRABAJAR."]),
    Ficha("enemigo:enjambre", CRIATURAS, "ENJAMBRE",
          ["DRONES OBREROS. VUELAN JUNTOS Y A COMPAS, COMO SI ALGUIEN LES MARCARA EL PASO.",
           "TODOS LLEVAN EL MISMO SELLO QUE LA COLMENA DEL MAR DE AMBAR."]),
    Ficha("enemigo:abeja", CRIATURAS, "ABEJA",
          ["LAS BIBLIOTECARIAS DE LA COLMENA.",
           "SALEN A DEFENDER LOS LIBROS Y VUELVEN CUANDO LA REINA LAS LLAMA.",
           "INES: NUNCA SE ALEJAN DE CASA. NO SON SOLDADOS."]),
    Ficha("enemigo:ladron", CRIATURAS, "LADRON",
          ["EL NOMBRE SE LO PUSO ALBA.",
           "AGARRA LA MONEDA Y SALE DISPARADO HACIA EL BORDE. NUNCA PELEA.",
           "INES: EL RADAR LOS PIERDE EN EL BORDE. ¿A DONDE LLEVAN LAS MONEDAS?"]),
    Ficha("enemigo:escudero", CRIATURAS, "ESCUDERO",
          ["UN GUARDIA DE LOS ARCHIVOS INTERIORES.",
           "SU ESCUDO MIRA SIEMPRE AL QUE SE ACERCA: DE FRENTE, NI EL DASH LO MUEVE.",
           "SOLO DEJA PASAR A QUIEN LO RODEA. A QUIEN SABE BAILAR."]),

    # ---------- Criaturas: los guardianes ----------
    Ficha("jefe:ojo", CRIATURAS, "EL OJO",
          ["PRIMER GUARDIAN DEL COMPAS: UNA LENTE DEL TAMAÑO DE UNA LUNA.",
           "DISPARA EN RAFAGAS Y DESPUES SE CANSA. TODOS LOS GUARDIANES DEJAN UNA VENTANA.",
           "INES: NO VIGILA EL CINTURON. MIRA HACIA OTRO LADO."]),
    Ficha("jefe:fortaleza", CRIATURAS, "EL ACORAZADO",
          ["SEGUNDO GUARDIAN. CUATRO CAÑONES QUE DISPARAN EN COMPAS.",
           "NO ES UN BARCO DE GUERRA: ES UN METRONOMO GIGANTE. MARCA EL TIEMPO PARA QUIEN LO SEPA LEER.",
           "SIN CAÑONES, SE LE CAE LA CORAZA."]),
    Ficha("jefe:serpiente", CRIATURAS, "LA DEVORADORA",
          ["TERCER GUARDIAN. SE COME LAS ESTRELLAS DEL CAMPO ESMERALDA...",
           "...Y LAS SUELTA EN OTRO LADO, COMO SI LAS ORDENARA.",
           "SU NUCLEO ESTA EN LA COLA."]),
    Ficha("jefe:colmena", CRIATURAS, "LA MADRE",
          ["CUARTA GUARDIANA: LA BIBLIOTECARIA MAYOR.",
           "SUS COMPUERTAS GUARDAN LAS CELDAS MAS VIEJAS. SIN ELLAS, LLAMA A SUS HIJAS A CASA Y EMBISTE.",
           "INES: DEFIENDE LIBROS, NO TERRITORIO."]),
    Ficha("jefe:singularidad", CRIATURAS, "EL FIN DE LA LUZ",
          ["EL ULTIMO GUARDIAN NO ES UN GUARDIAN: ES LA PUERTA.",
           "UN AGUJERO NEGRO CON UN ANILLO DE ROCAS QUE GIRA A COMPAS. ADENTRO EL TIEMPO SE DOBLA.",
           "TODO LO QUE CAE AHI... ¿A DONDE VA?"]),

    # ---------- Tecnologia: la Alondra y lo que se encuentra flotando ----------
    Ficha("tecnologia:alondra", TECNOLOGIA, "LA ALONDRA",
          ["LA NAVE DE ALBA. LA ALONDRA ES EL PAJARO QUE CANTA AL AMANECER.",
           "SU DASH ES UN SALTO SOBRE LA MAREA GRAVITATORIA. INES LO INVENTO MIRANDO COMO SE MUEVEN LOS GUARDIANES."]),
    Ficha("powerup:escudo", TECNOLOGIA, "ESCUDO",
          ["UNA BURBUJA DE TIEMPO DETENIDO ALREDEDOR DE LA NAVE.",
           "EL PRIMER GOLPE QUEDA AHI ADENTRO, CONGELADO, Y NUNCA LLEGA.",
           "TECNOLOGIA DE LOS CANTORES. NADIE SABE COMO ANDA. ANDA."]),
    Ficha("powerup:hielo", TECNOLOGIA, "ESTASIS",
          ["PARA EL TIEMPO DE TODO LO QUE ESTA CERCA, MENOS EL DE LA ALONDRA.",
           "LO QUE QUEDA CONGELADO SE ROMPE AL TOCARLO."]),
    Ficha("powerup:vida", TECNOLOGIA, "REPUESTO",
          ["UN REPUESTO PARA LA ALONDRA, EMPAQUETADO A SU MEDIDA.",
           "INES: A LA MEDIDA DE LA ALONDRA. ¿COMO SABIAN LAS MEDIDAS?"]),
    Ficha("powerup:iman", TECNOLOGIA, "IMAN",
          ["LAS MONEDAS VAN SOLAS HACIA LA NAVE.",
           "NO ES MAGNETISMO: ES COMO SI RECONOCIERAN A LA ALONDRA."]),
    Ficha("powerup:doble", TECNOLOGIA, "DOBLE",
          ["TODO VALE EL DOBLE MIENTRAS DURA.",
           "INES CREE QUE AMPLIFICA EL COMPAS: CADA MONEDA SUENA DOS VECES."]),
    Ficha("powerup:turbo", TECNOLOGIA, "TURBO",
          ["UN MOTOR DE REPUESTO QUE ENCAJA JUSTO EN LA ALONDRA. JUSTO.",
           "DURA HASTA EL PRIMER GOLPE."]),
    Ficha("powerup:recarga", TECNOLOGIA, "RECARGA",
          ["UNA CELDA PARA EL MOTOR DE SALTO: EL DASH SE CARGA EL DOBLE DE RAPIDO.",
           "LA FORMA DE LA CELDA COPIA LA DEL MOTOR DE INES. INES NUNCA LA PUBLICO."]),
    Ficha("powerup:nova", TECNOLOGIA, "NOVA",
          ["GUARDA UNA ESTRELLA CHIQUITA. EL PROXIMO DASH LA SUELTA Y TODO ALREDEDOR VUELA."]),

    # ---------- Fenomenos ----------
    Ficha("fenomeno:marea", FENOMENOS, "LA MAREA",
          ["UNA GALAXIA ENANA EN CURSO DE CHOQUE.",
           "NO VA A CHOCAR DE FRENTE: SU GRAVEDAD VA A DESGARRAR LAS ORBITAS DE TODO EL VECINDARIO.",
           "FALTAN SEIS AÑOS. NO SE PUEDE FRENAR. NO HAY A DONDE ESCAPAR."]),
    Ficha("fenomeno:compas", FENOMENOS, "EL COMPAS",
          ["PULSOS QUE SE CUELAN EN TODAS LAS RADIOS, CORTOS Y LARGOS, QUE SE REPITEN. NO ES RUIDO.",
           "MATEO LO OYO HACE TRES AÑOS Y NADIE LE CREYO. HACE TRES MESES LO CAPTO LA ESTACION UMBRAL."],
          glifo=escribir("ALBA")),
    Ficha("fenomeno:monedas", FENOMENOS, "LAS MONEDAS",
          ["METAL CON UN SIMBOLO GRABADO. CADA UNA GUARDA UN PEDAZO DEL COMPAS.",
           "JUNTAS Y RAPIDO, CANTAN: POR ESO EL COMBO SUENA CADA VEZ MAS RICO."]),
    Ficha("anomalia:asteroides", FENOMENOS, "LLUVIA DE ASTEROIDES",
          ["LA MAREA TIRONEA EL CINTURON Y LAS ROCAS SE SUELTAN.",
           "CADA MES PASA MAS SEGUIDO."]),
    Ficha("anomalia:tormenta", FENOMENOS, "TORMENTA SOLAR",
          ["LAS ESTRELLAS SIENTEN LA MAREA Y ESCUPEN FUEGO.",
           "ENTRE LA ESTATICA, A VECES LLEGAN SEÑALES VIEJAS."]),
    Ficha("anomalia:niebla", FENOMENOS, "NIEBLA CERRADA",
          ["ESPORAS TAN DENSAS QUE NI LA RADIO PASA. ADENTRO NO HAY RUIDO.",
           "MATEO DECIA QUE EN EL SILENCIO SE ESCUCHA MEJOR."]),
    Ficha("anomalia:oro", FENOMENOS, "FIEBRE DEL ORO",
          ["LAS MONEDAS APARECEN DE A MONTONES, COMO SI ALGUIEN VACIARA UN COFRE.",
           "INES: SI SE JUNTAN SIN PARAR, CANTAN MAS FUERTE QUE NUNCA."]),
]

POR_ID = {ficha.id: ficha for ficha in FICHAS}


def id_de(categoria, tipo):
    # ("enemigo", "divisor_chico") -> "enemigo:divisor" (la ficha que le toca)
    id_ = categoria + ":" + tipo
    return MISMA_FICHA.get(id_, id_)


def de_la_seccion(seccion):
    return [ficha for ficha in FICHAS if ficha.seccion == seccion]

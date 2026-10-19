"""
Mision 5: EL FIN DE LA LUZ

ABISMO AZUL (el Fin de la Luz). El compas sale del borde de un agujero negro. Al vencer al
ultimo guardian el anillo se abre, Alba baja y encuentra a EL ULTIMO: el que dejo las monedas.
En la estacion, un minuto es un dia de afuera; mas abajo, en el borde mismo, una hora son mil
años: ahi se puede dejar pasar la Marea. Mateo y
su tripulacion estan con el, vivos (para ellos pasaron dos dias). El compas suma una palabra:
VENGAN. Es el final de la historia (final = True).

Secretos: la brujula (con la mirada del Ojo: pegarle a la puerta desde el lado de casa) y
la Bitacora sin fecha (con todo lo demas encontrado: la primera bitacora de El Ultimo, que
tambien fue piloto, y el final verdadero: Alba toma su lugar).
Que cuenta y que esconde: HISTORIA.md. Como se escribe una mision: historia/mision.py.
"""
from juego.historia.mision import Mision, Fragmento, registrar_mision
from juego.historia.glifos import escribir
from juego.rutas import ASEDIO


@registrar_mision
class ElFinDeLaLuz(Mision):
    numero = 5
    titulo = "EL FIN DE LA LUZ"
    sector = 5
    lugar = (2060, 350)
    ambiente = ("gravedad", 2)      # la puerta: el compensador al maximo
    gravedad = 0.5          # al lado del agujero negro: cada visita, medio año mas en la Umbral
    final = True

    tramos = [
        {"nombre": "EL BORDE", "objetivo": ("monedas", 15), "a_la_vez": 2,
         "escuadrones": [("rebotador", 3, "esquinas"), ("divisor", 1, "flanco"), ("rebotador", 2, "pinza")]},
        {"nombre": "LA DESPEDIDA", "objetivo": ("romper", 4, "escudero"), "a_la_vez": 2,
         "escuadrones": [("escudero", 2, "pinza"), ("embestidor", 2, "lluvia"), ("enjambre", 1, "flanco")]},
        {"nombre": "EL COMPAS", "objetivo": ("perfectos", 10), "a_la_vez": 3, "anomalia": "asteroides",
         "escuadrones": [("perseguidor", 3, "cerco"), ("ladron", 1, "flanco"), ("rebotador", 2, "esquinas"),
                         ("divisor", 2, "lluvia")]},
        {"nombre": "ASEDIO FINAL", "objetivo": ASEDIO, "a_la_vez": 3, "asedio": True,
         "escuadrones": [("enjambre", 2, "pinza"), ("escudero", 2, "lluvia"), ("embestidor", 2, "esquinas"),
                         ("perseguidor", 3, "cerco"), ("divisor", 2, "pinza")]},
    ]

    antes = [
        ("cuadro", "umbral_caida", "T6"),
        ("ines", "ALBA... LA MAREA YA LLEGO. LA UMBRAL YA NO EXISTE. TE HABLO DESDE UNA NAVE.", "T6"),
        ("cuadro", "agujero_negro"),
        ("ines", "ES UN AGUJERO NEGRO, ALBA. Y EL COMPAS SALE DEL BORDE, DE MUY CERCA."),
        ("alba", "PEGADO A UN AGUJERO NEGRO EL TIEMPO CASI SE DETIENE. LO QUE HAYA AHI VIVE EN CAMARA LENTA."),
        ("ines", "POR ESO EL COMPAS ES TAN LENTO. ALGUIEN LO TOCA DESDE AHI ABAJO."),
        ("cuadro", "anillo"),
        ("ines", "LAS MONEDAS, LOS LADRONES... TODO VA HACIA AHI. Y UN ANILLO DE ROCAS LO CUIDA."),
        ("alba", "ENTONCES VAMOS HACIA AHI."),
        ("cuadro", "descenso_lejos"),
        ("ines", "ALBA. CADA MINUTO QUE PASES CERCA DEL BORDE SON DIAS AQUI. NO TE QUEDES."),
        ("alba", "NO ME ESPERES DESPIERTA."),
    ]

    radio = {
        "tramo_1": [
            ("ines", "LA GRAVEDAD TE VA A TIRAR. NO PELEES CONTRA ELLA: USALA."),
        ],
        "tramo_2": [
            ("alba", "ESCUDEROS, ARIETES, DRONES... TODOS JUNTOS."),
            ("ines", "ES COMO SI EL CAMINO ENTERO HUBIERA VENIDO A DESPEDIRTE."),
        ],
        "tramo_3": [
            ("cantores", ".- .-.. -... .-"),
            ("ines", "¿ESCUCHASTE? EL COMPAS. NUNCA LO HABIA OIDO TAN CLARO."),
        ],
        "tramo_4": [
            ("ines", "¡ULTIMO EMPUJON, ALBA!"),
        ],
        "jefe": [
            ("alba", "ES... HERMOSO."),
            ("ines", "ALBA. CONCENTRATE."),
            ("ines", "LA LENTE DEL OJO APUNTABA AQUI. DESDE EL CINTURON... DESDE CASA.", "F03+!F09"),
        ],
    }

    despues = [
        ("cuadro", "anillo_abierto"),
        ("ines", "SE ABRIO. ALBA, EL ANILLO SE ABRIO."),
        ("cuadro", "refugio"),
        ("alba", "BAJO. HAY UNA LUZ PEGADA AL BORDE DEL AGUJERO. UNA ESTACION, CON MILES DE MONEDAS ALREDEDOR."),
        ("alba", "INES... HAY ALGUIEN."),
        ("cuadro", "el_ultimo"),
        ("ultimo", "LLEGASTE."),
        ("ultimo", "APRENDI TU IDIOMA ESCUCHANDO SUS RADIOS, CUARENTA DE SUS AÑOS. PERDONA SI LO HABLO MAL."),
        ("alba", "¿ERES TU LOS CANTORES?"),
        ("ultimo", "NO HAY CANTORES. HAY UNO SOLO. SOY EL ULTIMO DE LOS MIOS."),
        ("cuadro", "galaxia_perdida"),
        ("ultimo", "HACE MILLONES DE AÑOS, LA MAREA PASO POR MI GALAXIA. YO LLEGUE TARDE. SOLO ME SALVE YO."),
        ("cuadro", "posta"),
        ("ultimo", "DESDE ENTONCES VIAJO DELANTE DE ELLA, CASI A LA VELOCIDAD DE LA LUZ. PARA MI FUERON OCHENTA AÑOS. FUERA, MILLONES."),
        ("ultimo", "EN CADA GALAXIA DEJO LO MISMO: LAS MONEDAS, LOS GUARDIANES, EL COMPAS. UN CAMINO HASTA AQUI."),
        ("ultimo", "NUNCA NADIE TERMINO EL CAMINO A TIEMPO. TU ERES LA PRIMERA."),
        ("cuadro", "una_hora"),
        ("alba", "¿Y QUE HAY AQUI ABAJO?"),
        ("ultimo", "TIEMPO. AQUI, CADA MINUTO ES UN DIA DE FUERA. MAS ABAJO, EN EL BORDE MISMO, UNA HORA SON MIL AÑOS."),
        ("ultimo", "LA MAREA NO SE PUEDE FRENAR. PERO SE PUEDE DEJAR PASAR. TRAIGAN SUS NAVES Y BAJEN CONMIGO UNAS HORAS."),
        ("ultimo", "CUANDO SUBAN, LA MAREA YA VA A ESTAR LEJOS. Y LAS ESTRELLAS, QUIETAS OTRA VEZ."),
        ("cuadro", "mateo_vivo"),
        ("mateo", "...¿ALBA? SOY MATEO SAAVEDRA, DE LA ERRANTE. LLEGAMOS EN LA CAPSULA, POR UN HUECO DEL ANILLO."),
        ("mateo", "PARA NOSOTROS PASARON DOS DIAS DESDE QUE BAJAMOS. DILE A INES... DILE QUE ME PERDONE."),
        ("alba", "INES. MATEO ESTA AQUI. ESTAN VIVOS, LOS TRES."),
        # La respuesta tarda: arriba el tiempo corre mucho mas rapido
        ("cuadro", "vengan", "!T6"),
        ("ines", "ALBA... TU MENSAJE TARDO TRES DIAS EN LLEGAR. PARA TI FUERON MINUTOS.", "!T6"),
        ("ines", "Y EL COMPAS CAMBIO. AHORA TERMINA CON UNA PALABRA NUEVA: VENGAN.", "!T6"),
        ("ines", "ATENCION, ESTACION UMBRAL. PREPAREN TODAS LAS NAVES. NOS VAMOS.", "!T6"),
        # Tarde: la Marea ya llego a la Umbral
        ("cuadro", "vengan_tarde", "T6"),
        ("ines", "LA MAREA YA ESTA AQUI. LA UMBRAL SE PARTIO. QUEDAMOS POCOS, EN TRES NAVES.", "T6"),
        ("ines", "Y EL COMPAS CAMBIO. TERMINA CON UNA PALABRA NUEVA: VENGAN.", "T6"),
        ("ines", "LLEGAMOS TARDE PARA LOS DEMAS. PERO VAMOS.", "T6"),
        # El final verdadero: con todo encontrado, El Ultimo le cuenta quien fue
        ("cuadro", "primera_bitacora", "F11"),
        ("ultimo", "ANTES DE QUE LLEGUEN, ESCUCHA ESTO. ES MI PRIMERA BITACORA. TE LA TRADUZCO.", "F11"),
        ("voz", "DIA 1. EN MI CIELO APARECIERON MONEDAS. ALGUIEN LAS DEJO PARA NOSOTROS. VOY A SEGUIRLAS.", "F11"),
        ("ultimo", "YO TAMBIEN FUI PILOTO. A MI TAMBIEN ME DEJARON UN CAMINO. NUNCA SUPE QUIEN: SIEMPRE HUBO ALGUIEN DELANTE.", "F11"),
        ("cuadro", "relevo", "F11"),
        ("ultimo", "YA ESTOY VIEJO, ALBA. NO AGUANTO OTRO VIAJE. Y ALGUIEN TIENE QUE IR DELANTE DE LA MAREA, A LA GALAXIA QUE SIGUE.", "F11"),
        ("alba", "...INES. NO VOY A BAJAR CON USTEDES.", "F11"),
        ("ines", "LO SE. LO SUPE EL DIA QUE TE OFRECISTE.", "F11"),
        ("ultimo", "MI NOMBRE, EN TU IDIOMA, QUIERE DECIR AMANECER. LO GRABE ASI EN TODAS LAS MONEDAS: ALBA.", "F11"),
        ("ultimo", "AHORA ES TUYO DE VERDAD.", "F11"),
    ]

    fragmentos = [
        Fragmento("F09", "LA BRUJULA",
                  ["ALBA GOLPEO LA PUERTA DESDE EL LADO DE CASA, HACIA DONDE MIRABA EL OJO.",
                   "LOS INSTRUMENTOS SE VOLVIERON LOCOS: POR CADA SEGUNDO DE LA ALONDRA, EN LA UMBRAL PASABAN HORAS.",
                   "LA PUERTA NO LLEVA A OTRO LUGAR. LLEVA A OTRO:"],
                  glifo=escribir("CUANDO"),
                  reaccion=[("alba", "¡LOS RELOJES! INES, POR CADA SEGUNDO MIO, EL TUYO CORRE HORAS.")]),
        Fragmento("F11", "BITACORA SIN FECHA",
                  ["UNA GRABACION SIN FECHA QUE LLEGO POR EL COMPAS. LA VOZ ES JOVEN, NO ES HUMANA Y HABLA OTRO IDIOMA. ALGUIEN LA TRADUJO EN GLIFOS:",
                   "DIA 1. EN MI CIELO APARECIERON MONEDAS. ALGUIEN LAS DEJO PARA NOSOTROS. VOY A SEGUIRLAS.",
                   "ES LA VOZ DE EL ULTIMO, MILLONES DE AÑOS ANTES, CUANDO TAMBIEN ERA PILOTO."],
                  reaccion=[("voz", "DIA 1. EN MI CIELO APARECIERON MONEDAS. VOY A SEGUIRLAS."),
                            ("ines", "¿QUIEN ES? UNA VOZ JOVEN, EN OTRO IDIOMA. VIENE TRADUCIDA EN GLIFOS... Y NO TIENE FECHA.")],
                  oculto=True),
    ]

    secretos = [
        ("golpe_desde", "F09", {"angulo": 180, "requiere": ["F03"]}),
        ("jefe_vencido", "F11", {"requiere": "todos"}),
    ]

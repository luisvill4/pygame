"""
Los ECOS: las mini historias de los sistemas libres de la galaxia (como las terminales de
Fallout). Se encuentran al despejar por primera vez el sistema que los guarda (galaxia.py) y
van al Archivo, en su propia pestaña.

Solo datos. Son Fragmentos como los de las misiones (mision.py), con id "E01"... Cuentan
lo que la historia principal no: que el compas es mas viejo de lo que creen, que huir no
sirve (el tiempo te alcanza), que otros ya cruzaron la puerta... y, en el sistema mas
lejano y peligroso, lo mas hondo (HISTORIA.md, "Los ecos").
"""
from juego.historia.mision import Fragmento
from juego.historia.glifos import escribir

ECOS = [
    Fragmento("E01", "LA SONDA",
              ["UNA SONDA DE LA UMBRAL, LANZADA HACE CUARENTA AÑOS. NADIE LA ESCUCHABA DESDE HACIA DECADAS.",
               "SU GRABADOR TIENE EL COMPAS. MUY DEBIL, PERO ESTA.",
               "EL COMPAS NO EMPEZO HACE TRES MESES. SIEMPRE ESTUVO."],
              reaccion=[("alba", "UNA SONDA VIEJA DE LA UMBRAL. TIENE GRABADO EL COMPAS... DE HACE CUARENTA AÑOS.")]),
    Fragmento("E02", "LA ESTACION KEPLER",
              ["UNA ESTACION VACIA. SU GENTE SE FUE EN NAVES DE CARGA, PARA HUIR DE LA MAREA LO MAS LEJOS POSIBLE.",
               "CALCULARON MAL: LA MAREA ES MAS ANCHA QUE CUALQUIER VIAJE. NINGUN LUGAR QUEDABA LO BASTANTE LEJOS.",
               "ULTIMA ENTRADA: NO SE PUEDE ESCAPAR HUYENDO."],
              reaccion=[("alba", "UNA ESTACION VACIA. QUISIERON HUIR DE LA MAREA... Y NO HABIA A DONDE.")]),
    Fragmento("E03", "EL RELOJ DE ARENA",
              ["UN PULSAR QUE LATE UNA VEZ POR SEGUNDO. ALREDEDOR, BOYAS DE LOS CANTORES QUE CUENTAN SUS LATIDOS.",
               "LA CUENTA BAJA. TERMINA EL DIA QUE LLEGA LA MAREA. EN LA BOYA MAS GRANDE:"],
              glifo=escribir("PRONTO"),
              reaccion=[("ines", "ES UN RELOJ, ALBA. DEL TAMAÑO DE UNA ESTRELLA. Y CUENTA LO QUE NOS QUEDA.")]),
    Fragmento("E04", "EL PLANETA QUE CANTA",
              ["UN PLANETA CON LA CORTEZA LLENA DE MONEDAS A MEDIO HACER. CUANDO PASA UNA NAVE, VIBRA A COMPAS.",
               "ES UNA FABRICA: ACA SE GRABARON LAS MONEDAS. EN EL SUELO, UN GLIFO DEL TAMAÑO DE UNA CIUDAD:"],
              glifo=escribir("HOGAR"),
              reaccion=[("alba", "TODO EL PLANETA VIBRA... ACA HICIERON LAS MONEDAS.")]),
    Fragmento("E05", "EL VIGIA",
              ["UNA MAQUINA DE LOS CANTORES, SOLA, MIRANDO EL CAMINO DE LAS MONEDAS.",
               "NO ATACA. CUANDO LA ALONDRA PASA, GIRA HACIA ELLA, PRENDE UN GLIFO Y SE APAGA, COMO SI YA HUBIERA TERMINADO SU TRABAJO:"],
              glifo=escribir("LLEGO"),
              reaccion=[("alba", "LA MAQUINA ME MIRO... Y SE APAGO. COMO SI ME ESTUVIERA ESPERANDO.")]),
    Fragmento("E06", "LOS QUE ESCAPARON",
              ["UNA NAVE GENERACIONAL A LA DERIVA. SALIO HACE TRESCIENTOS AÑOS, HUYENDO DE OTRA GUERRA.",
               "SU DIARIO TERMINA CON UNA DECISION: OYERON EL COMPAS Y DIERON LA VUELTA.",
               "LA NAVE ESTA VACIA. LA ESCOTILLA, ABIERTA, MIRA HACIA EL ABISMO."],
              reaccion=[("ines", "TRESCIENTOS AÑOS... Y TAMBIEN FUERON HACIA LA PUERTA. NO SOMOS LOS PRIMEROS.")]),
    Fragmento("E07", "LA CARTA",
              ["UN MENSAJE QUE QUEDO TRES AÑOS DANDO VUELTAS EN LAS CORRIENTES DEL ABISMO, SIN LLEGAR A NADIE.",
               "ES DE INES, PARA MATEO: VOLVE. NO ME IMPORTA EL COMPAS. NO ME IMPORTA LA MAREA. VOLVE.",
               "MATEO NUNCA LO RECIBIO."],
              reaccion=[("alba", "UN MENSAJE DE INES... PARA MATEO. NO SE LO VOY A CONTAR.")]),
    Fragmento("E08", "LA OTRA ALONDRA",
              ["LOS RESTOS DE UNA NAVE IGUAL A LA ALONDRA. EL MISMO MODELO, LA MISMA MATRICULA.",
               "ESTA CUBIERTA DE POLVO DE MILLONES DE AÑOS.",
               "EN LA CABINA, RAYADO A MANO:"],
              glifo=escribir("ALBA"),
              reaccion=[("alba", "...ES LA ALONDRA. MI ALONDRA. ¿COMO PUEDE ESTAR ACA? ¿Y TAN VIEJA?")]),
]

POR_ID = {eco.id: eco for eco in ECOS}

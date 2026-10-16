# La Marea — la biblia del modo historia

> **Beta.** Todo se puede cambiar. Este documento es la referencia para escribir diálogos,
> secretos y misiones sin contradecirse. **Spoilers totales**: acá está la verdad.

El juego tiene dos modos: **ARCADE** (la ruta infinita de siempre, con récords y logros) e
**HISTORIA** (las misiones de este documento, con diálogos, radio, secretos y el Archivo).

---

## 1. Lo que sabe el jugador al empezar

Una galaxia enana, que los astrónomos llaman **la Marea**, viene en curso de choque. No choca de
frente: sus fuerzas de marea van a desgarrar las órbitas de todo el vecindario estelar. Faltan
seis años. No hay a dónde escapar y no hay forma de detenerla.

En las ondas gravitacionales hay un **compás**: pulsos cortos y largos que se repiten. No es
ruido: alguien lo puso ahí. Lleva al Cinturón Exterior, donde flotan unos objetos de metal con un
símbolo grabado. Por la forma les dicen **monedas**.

**Alba**, piloto de la nave **Alondra**, sale a seguir el compás. **Inés Coria** la guía por
radio desde la **Estación Umbral**.

## 2. La verdad (lo que revela el final verdadero)

**Los Cantores somos nosotros.** Es un bucle en el tiempo:

1. La Singularidad del Abismo (*El Fin de la Luz*) no es un arma ni un monstruo: es una **puerta
   en el tiempo**. Cerca de un agujero negro el tiempo se dobla; esta puerta lo dobla hacia atrás.
2. Del otro lado, millones de años antes de la Marea, los que cruzan se vuelven **los Cantores**.
   Saben que la Marea va a venir, así que preparan el camino para que alguien lo encuentre:
   graban las monedas, despiertan a los guardianes, emiten el compás.
3. Ese camino es exactamente el que Alba sigue en el juego. **Las monedas las dejaron ellos**:
   Alba, Mateo, la tripulación de la Errante... y, al final, todos los que cruzan.
4. La Marea no se puede frenar, **pero se puede cruzar**. La puerta es la salida. Por eso el
   compás termina diciendo **VENGAN**.

El compás, en el código de los Cantores, dice **ALBA**. Lo dice desde hace millones de años.

**Regla de oro:** ningún secreto contradice esto, y cada uno, mirado después, apunta hacia acá.

## 3. Personajes

| Quién | Quién es | Cómo habla |
|---|---|---|
| **ALBA** | Piloto de la Alondra. Terca, con humor seco. No cree en señales del destino. No tiene a nadie que la espere: por eso se ofreció. | Frases cortas. Se ríe del peligro. |
| **INÉS CORIA** | Astrofísica de la Estación Umbral. Es la voz de la radio. Vivió siete años con Mateo. | Precisa, cálida, cansada. Dice "compás" y no "señal". |
| **MATEO SAAVEDRA** | Capitán de la Errante. Oyó el compás tres años antes que nadie y salió a seguirlo. | Tranquilo, un poco poeta. Solo queda su voz grabada. |
| **ROCÍO VEGA** | Ingeniera de la Errante. Fue la primera en notar que las monedas "cantan". | Entusiasta, desconfía de las explicaciones fáciles. |
| **TOMÁS ILIC** | Navegante de la Errante. Cuenta todo: los disparos, los días, los pulsos. | Metódico. |
| **LOS CANTORES** | Los que dejaron el camino. Nunca aparecen: solo glifos, ritmos y máquinas. | En glifos. Traducidos, suenan humanos (porque lo son). |
| **LA VOZ SIN FECHA** | Alba, grabada del otro lado de la puerta, millones de años antes. Su retrato es el de Alba en los colores de los Cantores. | Como Alba, pero en paz. |

La nave se llama **Alondra** porque la alondra es el pájaro que canta al amanecer, y *alba*
también quiere decir amanecer: Alba y los Cantores, el amanecer contra *El Fin de la Luz*.

## 4. Cronología

| Cuándo | Qué pasa |
|---|---|
| Hace millones de años | Los que cruzaron la puerta (los Cantores) graban las monedas, despiertan a los guardianes y emiten el compás. Alba graba la Bitácora sin fecha. |
| Hace tres años | Mateo oye el compás, muy débil. Nadie le cree. Sale con la **Errante** (Rocío y Tomás) a seguir las monedas: Cinturón, Nebulosa, Esmeralda, Ámbar. En la niebla aprende a leer los glifos; lee la firma: ALBA. |
| Hace tres años, día 377 | La Marea alcanza a la Errante al borde del Abismo y la parte en tres. Mateo transmite su último mensaje ("...ALBA. DECILE A ALBA...") y entra a la puerta con la tripulación, en la cápsula de escape. Deja la baliza prendida. |
| Hace tres meses | La Estación Umbral capta el compás. Inés lo decodifica en parte. |
| El juego | Alba sigue el compás, misión por misión. |
| Tres días después de la misión 5 | El compás suma una palabra: VENGAN. Si se encontró todo, llega la Bitácora sin fecha e Inés da la orden: "Nos vamos". |

## 5. El porqué de cada cosa del juego

Todo lo que existe en el juego tiene su lugar en la historia. Lo cuentan las **fichas del
Archivo** (`juego/historia/fichas.py`), que se anotan solas la primera vez que se ve cada cosa
en una misión. Algunas esconden pistas (marcadas con ➜).

| Qué | Qué es en la historia |
|---|---|
| **Monedas** | Sellos de memoria de los Cantores: cada una guarda un pedazo del compás. Juntas y rápido "cantan" (la moneda suena más rica con el combo). |
| **El dash** | El salto de la Alondra sobre la marea gravitatoria. Inés lo inventó mirando cómo se mueven los guardianes. |
| **Perseguidores** | Centinelas. No buscan matar: alejan a cualquiera de las monedas. "¿Y si no las cuidan *de* nosotros, sino *para* nosotros?" |
| **Rebotadores** | Cápsulas de memoria dañadas: repiten un mismo segundo del pasado. En los restos de la Errante repiten su último segundo. |
| **Embestidores** | Arietes de construcción. Abrieron los túneles del Cinturón. |
| **Divisores** | Esporas de terraformación: se reparten al romperse, para sembrar. |
| **Enjambre y abejas** | Las obreras y las bibliotecarias de la Colmena, que es una biblioteca. ➜ "No son soldados" (F08). |
| **Ladrones** | Carteros: no roban, **llevan** las monedas al Abismo, de vuelta a la puerta (pista central del bucle). ➜ "¿A dónde llevan las monedas?" (F05). |
| **Escuderos** | Guardias de los archivos. Solo dejan pasar a quien los rodea: a quien sabe bailar. |
| **Power-ups** | Tecnología de los Cantores. ➜ El repuesto viene "a la medida de la Alondra: ¿cómo sabían las medidas?"; el imán, "como si las monedas reconocieran a la Alondra". |
| **Anomalías** | Lo que la Marea ya está rompiendo. ➜ En la niebla "se escucha mejor" (F06); en la fiebre del oro "cantan más fuerte que nunca" (F07). |
| **Los jefes** | **Guardianes del compás.** Pelean a ritmo porque *son* el ritmo. Ponen a prueba a quien sigue el camino: la puerta solo se abre para quien sabe bailar. El Acorazado es un metrónomo; la Colmena, la bibliotecaria mayor. |
| **La Singularidad** | La puerta. *El Fin de la Luz* no es un final: es por donde los Cantores volvieron al principio. |

## 6. Las misiones

Una por sector, en orden, más una oculta. Cada misión tiene **su propia ruta** (4 tramos con
nombres de la historia y la anomalía que necesita su secreto), diálogos antes y después, la
radio en cada tramo y secretos. Las misiones ganadas se rejuegan para buscar lo que falta.

| # | Lugar | Título | Lo que se descubre (la historia principal) |
|---|---|---|---|
| 1 | Cinturón Exterior | LA SEÑAL | Las monedas tienen un símbolo. El Ojo es una lente que mira más allá. El compás suma una nota y señala la Nebulosa, por donde pasó la Errante. |
| 2 | Nebulosa Carmesí | EL ACORAZADO | Inés cuenta quién era Mateo; Alba, por qué se ofreció. Los cañones son metrónomos: Inés traduce la primera palabra, **SEGUÍ**. |
| 3 | Campo Esmeralda | LA DEVORADORA | Alguien más junta monedas: los ladrones, que salen todos hacia el Abismo. En la niebla, la radio no pasa: Alba está sola. |
| 4 | Mar de Ámbar | LA COLMENA | La Colmena es una biblioteca. El mensaje se lee entero: **SEGUÍ LAS MONEDAS**, con una firma. El compás sale del Abismo, de un agujero negro. |
| 5 | Abismo Azul | EL FIN DE LA LUZ | La puerta se abre. Alba entra: "Seguí las monedas". Tres días después, el compás dice **VENGAN**. |
| 6 | Al borde del Abismo (oculta) | LOS RESTOS | Aparece con las tres bitácoras (F02, F04, F07). Sin guardián: los restos de la Errante y el diario de Mateo por la radio. La tripulación no está: falta la cápsula. |

**Los diálogos reaccionan a lo encontrado** (renglones con condición, ver `mision.py`): por
ejemplo, con la clave del compás (F06) y la moneda grabada (F01), Inés lee la firma: "DICE...
ALBA". Sin ellas, no la puede leer. Y la radio solo da una pista si todavía falta lo que señala.

## 7. Las capas del misterio

1. **La historia principal** (diálogos y radio): cualquiera la entiende jugando. Termina con
   VENGAN, que se entiende como esperanza, sin saber quién llama.
2. **El Archivo**: los fragmentos (las mini historias de la Errante, los Cantores y los
   guardianes) y las fichas (el porqué de cada cosa).
3. **Lo cruzado**: pistas que solo tienen sentido juntas. La mirada del Ojo (F03) dice desde
   dónde pegarle a la puerta (F09); las monedas que "cantan" (F02) explican el eco de la
   Errante (F07); la clave del compás (F06) traduce todos los glifos.
4. **Lo muy hondo**: el compás *es* el nombre de Alba en Morse (la ficha EL COMPÁS lo muestra
   en glifos; en la misión 5 los Cantores lo "dicen" por radio; el sonido de encontrar un
   fragmento lo toca). La moneda de la estela (F13) está firmada MATEO: él también se volvió
   Cantor. Quien sepa Morse puede leer todo esto antes de tener la clave.
5. **La verdad**: la Bitácora sin fecha (F11). Pide haber encontrado todo lo demás.

## 8. El código de los glifos

Los Cantores escriben con **ritmos**: cada glifo es una letra hecha de pulsos cortos (◇) y largos
(▬). Es Morse, pero el jugador no lo sabe: lo descubre al encontrar **la clave del compás**
(F06, misión 3). Con la clave, el Archivo traduce todo lo que ya encontró.

| Dónde | Dice |
|---|---|
| F01 La moneda grabada (la firma) | ALBA |
| F04 La Errante 2/3 (en los cañones) | ATRAS |
| F05 El cartero (en la espalda del ladrón) | CASA |
| F08 Las bibliotecarias | OTRA |
| F09 La brújula | CUANDO |
| F12 La baliza (la titila) | SEGUI |
| F13 La otra firma | MATEO |
| La ficha EL COMPÁS y el sonido `fragmento` | ALBA |
| La pantalla final | SEGUI LAS MONEDAS |

En el código, los glifos se escriben con `glifos.escribir("ALBA")` y el ritmo en el tiempo sale
de `glifos.ritmo` (lo usan la baliza, los pulsos de la niebla y el planeta del Abismo, que late
en el mapa).

## 9. Catálogo de secretos

Cada secreto: **dónde**, **cómo se encuentra** (nunca a simple vista), **la pista que lo anuncia**,
**qué cuenta** y **qué pista deja**. Estado: ✅ probado por el usuario, 🟨 en el juego para probar.

| Id | Misión | Nombre | Cómo se encuentra | Pista antes | Qué cuenta | Pista que deja | Estado |
|---|---|---|---|---|---|---|---|
| F01 | 1 | La moneda grabada | Desde el tramo 2, después de 15 monedas aparece una moneda blanca que gira lento. Si no la agarrás en 6 s, se apaga. | Radio T2: "todas tienen un símbolo grabado". Al aparecer, Alba: "¿Y esa moneda blanca?" | Un glifo grande: una firma. | Hay glifos para traducir. | 🟨 |
| F02 | 1 | La Errante 1/3 | En el tramo 3, unos restos cruzan el fondo, apagados como el fondo. Solo el dash los abre. | Radio T3: "hay algo en el fondo, entre las rocas... no, nada". | Rocío: las monedas cantan cuando las juntás rápido. | La Errante existió. Las monedas cantan (el combo). | 🟨 |
| F03 | 1 | La mirada del Ojo | Vencer al Ojo sin recibir un golpe en todo el sector. | Radio jefe: "si salís sin un rasguño, puedo medir a dónde apunta". | La lente apuntaba al Abismo, como una brújula. | Algo importante está en el Abismo (y es la clave de F09). | 🟨 |
| F04 | 2 | La Errante 2/3 | Romper los cuatro cañones del Acorazado **de izquierda a derecha** (se puede: el que no toca, no se le pega). | Radio jefe: "Mateo decía que un reloj se lee como un libro. En orden". | Tomás: los cañones son relojes y cuentan hacia atrás. Glifo ATRAS. | El tiempo va hacia atrás. | 🟨 |
| F12 | 2 | La baliza | En la tormenta solar (tramo 3) cruza una baliza apagada que titila un glifo. Dash. | Radio T3: "entre la estática me llega una baliza. ¿La ves?" | La grabación de Mateo: "Estamos bien. Seguimos. No nos esperen". Titila SEGUI. | Mateo leyó la primera palabra hace tres años. | 🟨 |
| F05 | 3 | El cartero | Dejar que un ladrón se lleve la moneda y **seguirlo de cerca** sin alcanzarlo hasta que salga (seguí las monedas, al pie de la letra). | Radio T2: "quiero saber a dónde llevan las monedas". Ficha del ladrón. | No la robó: la llevó al Abismo, como quien vuelve a casa. Glifo CASA. | Las monedas vuelven al Abismo. | 🟨 |
| F06 | 3 | La clave del compás | En la niebla (tramo 3), quedarse **quieta** (sin tocar nada) hasta oír la palabra entera: 12 pulsos, ~8 s. Cada pulso suena y la nave lo siente. Moverse vuelve a empezar. | Antes: "Mateo decía que en el silencio se escucha mejor el compás". Ficha de la niebla. | Los glifos son ritmos. El Archivo los traduce desde ahora. | La firma dice ALBA. | 🟨 |
| F07 | 4 | La Errante 3/3 | Juntar **20 monedas seguidas** (en la fiebre del oro es posible): cantan tan fuerte que la radio capta un eco de hace tres años. | Radio T3: "si las juntás sin parar, la radio se acopla". Ficha de la fiebre. | La última transmisión de Mateo: "...ALBA. DECILE A ALBA...". | Hace tres años alguien ya nombró a Alba. | 🟨 |
| F08 | 4 | Las bibliotecarias | Vencer a la Colmena **sin romper ninguna abeja**. | Radio jefe: "las abejas son bibliotecarias. No son soldados". Ficha de la abeja. | Un poema: "La vimos llegar una vez. La vamos a ver llegar otra". Glifo OTRA. | Los Cantores ya vivieron esto. | 🟨 |
| F09 | 5 | La brújula | Con F03: pegarle al núcleo de la puerta **desde la izquierda** (el lado de casa, hacia donde miraba el Ojo). | Radio jefe (solo con F03): "la lente del Ojo apuntaba acá. Desde el Cinturón... desde casa". | El reloj de la Alondra cuenta hacia atrás. "No lleva a otro lugar. Lleva a otro cuándo". | La puerta es en el tiempo. | 🟨 |
| F10 | 6 | El último registro | En el tramo 3 de LOS RESTOS cruza un pedazo del casco: la caja negra. Dash. | Al aparecer, Alba: "la caja negra tiene que estar ahí". | Mateo: la nave no aguanta, entran a la puerta. "No es un final". | La tripulación cruzó. | 🟨 |
| F13 | 6 | La otra firma | En el tramo 4 de LOS RESTOS (la estela de la cápsula), después de 6 monedas aparece otra moneda blanca. | Al aparecer, Alba: "¿Otra moneda blanca? ¿Acá?". Radio T4: "algo salió de la Errante hacia la puerta". | Una firma torpe, hecha a mano. Glifo MATEO. | Mateo también se volvió Cantor. | 🟨 |
| F11 | 5 | Bitácora sin fecha | Con **todos** los demás encontrados: vencer a la Singularidad. Es *oculto*: no aparece en el Archivo hasta encontrarlo. | La pantalla final: "La puerta sigue abierta. ¿Volvés a cruzarla?" (si solo falta este). | La voz de Alba desde el otro lado: "Seguí las monedas. Las dejamos nosotros". | La verdad (el final verdadero). | 🟨 |

Los fragmentos de la misión oculta tampoco aparecen en el Archivo hasta que aparece la misión
(la cuenta de arriba sí los suma: hay más de lo que se ve).

## 10. La galaxia y el tiempo

El mapa de la historia es una **galaxia que se recorre libre** (como el mapa estelar de
Starfield): las misiones son sistemas marcados y entre ellas hay 16 **sistemas libres**.

- **La relatividad:** para Alba un viaje dura horas; en la Estación Umbral pasan **años** (viaja
  casi a la velocidad de la luz, y cerca del Abismo la gravedad estira su tiempo todavía más:
  cada visita ahí suma años de **dilatación**). Lo que cuenta es el reloj de la Umbral. La
  Marea llega en el año 6.
- **El costo:** cada viaje gasta años según la distancia; cada salida, aunque no viajes, gasta
  un poco (nada es gratis). El camino directo de la historia cuesta ~3.8 años en viajes, pero
  los módulos obligan a explorar para juntar piezas: una campaña simulada termina entre el año
  4.4 y el 4.9. Explorarlo todo no se puede a tiempo: hay que elegir.
- **La Marea se ve:** un frente rojo avanza desde la izquierda y en el año 6 se traga la Umbral.
  Lo que traga ya no se puede visitar.
- **Inés envejece:** cada año que pasa manda un mensaje ("para vos fueron unas horas; para mí,
  un año"). En el año 6, la Umbral cae y ella sigue a Alba con los que pudieron subir a las naves.
- **La historia reacciona al tiempo** (renglones con `T3`, `!T6`): Inés pide que se apure, y si
  la misión 5 se cumple tarde, el final cambia: "Llegamos tarde para los demás. Pero vamos". La
  pantalla final dice el año y "LLEGASTE TARDE".
- **Con la historia terminada el reloj se detiene:** lo que quedó se puede explorar sin apuro.
- **Cuanto más lejos, más peligro** (de 1 a 5, por la distancia a la Umbral): escuadrones más
  grandes y más rápidos. Desde peligro 3, el último tramo es un asedio.
- **Los módulos abren la galaxia** (pedido del usuario: "que las galaxias estén bloqueadas y se
  desbloqueen a medida que se mejora la nave, y que se vea en la nave"). Muchos sistemas tienen
  un **peligro ambiental** con intensidad 1 o 2, y para entrar hace falta el **módulo** de ese
  peligro con ese nivel. Los peligros están **mezclados** por el mapa (casi siempre el del
  bioma, pero con excepciones en todas las zonas): cada módulo abre lugares en varias zonas y el
  orden lo elige el jugador. Es una red, no una escalera.
  - Un módulo se fabrica en el Hangar (pestaña MÓDULOS) con su **plano** y piezas. Cada plano
    está en uno o dos sistemas libres (se consigue al despejarlos) y además Inés lo diseña al cumplir
    la misión anterior a la que lo pide: **la historia nunca se traba** (lo comprueba un test).
  - **Cada nivel se ve en la Alondra** (pixel art encima del sprite, en la grilla de 2 px). En
    el arcade la nave va siempre limpia.

  | Módulo | Peligro | Nivel 1 | Nivel 2 | Plano en |
  |---|---|---|---|---|
  | Escudo térmico | calor (estrellas) | placas naranjas en el borde de las alas | una fila roja más adentro | Kepler, misión 1 |
  | Filtro de esporas | esporas | cápsulas de metal con luz verde al lado de la cabina | más largas, con dos luces | Vega del Sur, Espora, misión 2 |
  | Casco de panal | panal (la Colmena) | un panal dorado ralo en las alas | una placa dorada en el borde de atrás | Brasa, Espejo, misión 3 |
  | Compensador | gravedad (el Abismo) | un anillo violeta abajo del motor | aletas en las puntas de las alas | Oráculo, Panal Viejo, misión 4 |

  La misión 5 pide el compensador al máximo (la puerta está al lado del agujero negro). El
  Impulsor del hangar también se ve: una tobera más por nivel.
- **Las recompensas:** **piezas** (las monedas de cada partida, y mucho más la primera vez que se
  despeja un sistema, según su peligro) para el **Hangar**: mejoras para siempre de la Alondra
  (las cartas del Taller desde el despegue y el **Impulsor**, que acorta los viajes); los
  **ecos** (las historias de los sistemas libres) y las **puertas menores** (atajos que casi no
  gastan tiempo: Los Gemelos ⇄ Espejo y Cíclope ⇄ Horizonte).

### Los ecos

| Id | Sistema | Nombre | Qué cuenta |
|---|---|---|---|
| E01 | Vega del Sur | La sonda | Una sonda de la Umbral grabó el compás hace cuarenta años: siempre estuvo. |
| E02 | Kepler | La estación Kepler | Quisieron huir de la Marea a la velocidad de la luz: el tiempo los alcanzó. "No se puede escapar huyendo". |
| E03 | Oráculo | El reloj de arena | Un púlsar marcado por los Cantores que cuenta los latidos hasta la Marea. Glifo PRONTO. |
| E04 | Semillero | El planeta que canta | La fábrica de las monedas. Glifo HOGAR. |
| E05 | Vigía | El vigía | Una máquina de los Cantores que espera a la Alondra, la mira y se apaga. Glifo LLEGO. |
| E06 | Miel | Los que escaparon | Una nave generacional de hace 300 años que oyó el compás y dio la vuelta: no son los primeros en cruzar. |
| E07 | Horizonte | La carta | Un mensaje de Inés a Mateo ("volvé") que tardó tres años en llegar y nunca lo recibió. |
| E08 | Umbra (peligro 5) | La otra Alondra | Los restos de **la Alondra**, con millones de años de polvo y ALBA rayado en la cabina. Lo más hondo para quien llega más lejos. |

## 11. Los finales

Después del diálogo de la misión 5 viene la **pantalla final** (`escenas/historia/final.py`):

- **El de siempre:** "LA MAREA — FIN" en rojo, con la música del Game Over. El mensaje del compás
  en glifos (sin traducir), lo encontrado (misiones, fragmentos, fichas) y "Todavía hay cosas que
  no encontraste" (o "La puerta sigue abierta. ¿Volvés a cruzarla?" si solo falta la Bitácora).
- **El verdadero** (con F11): en el diálogo llega la Bitácora sin fecha (la voz de Alba en los
  colores de los Cantores) e Inés da la orden: "Preparen todas las naves. Nos vamos". La pantalla
  dice "**EL PRINCIPIO**" en amarillo, con la música en Do mayor, el mensaje traducido (SEGUI LAS
  MONEDAS) y "LOS CANTORES SOMOS NOSOTROS".

**El mapa también cuenta la historia:** arriba dice "LA MAREA LLEGA EN 6 AÑOS"; después de la
misión 5, "EL COMPAS DICE: VENGAN"; con la verdad, "SEGUI LAS MONEDAS". El planeta del Abismo
late en el ritmo del compás (salvo con DESTELLOS REDUCIDOS).

## 12. Reglas para escribir un secreto

- **Nunca a simple vista.** Se encuentra jugando distinto (quieto, en orden, sin romper algo,
  siguiendo, dejando escapar), no por suerte pura.
- **Todo tiene su porqué.** El secreto usa una mecánica que ya existe y le da sentido (el combo
  "canta", el ladrón "lleva", el jefe "marca el tiempo", las abejas "cuidan libros").
- **Hay una pista antes** (por radio, en una ficha o en otro fragmento) y **cada uno abre otro.**
  Las pistas de radio llevan condición ("!F05"): no se repiten después de encontrarlo.
- **Se puede rejugar.** El Archivo dice cuántos fragmentos hay por misión, no dónde están.
- **Sin texto obvio.** Ningún cartel dice "¡SECRETO!". El hallazgo suena (`fragmento`), se cuenta
  por la radio con una reacción y queda en el Archivo.
- **Que se pueda de verdad:** medirlo con un bot que juegue (con 25 monedas seguidas un bot que
  no esquiva no llegaba nunca; con 20, 2 de cada 6 veces).
- **Texto en el juego:** en mayúsculas y sin vocales mayúsculas con tilde (la fuente las dibuja
  mal), frases cortas. Los tests comprueban que todo entre en su caja.

## 13. Cómo está hecho (para seguir escribiendo)

Todo el modo historia vive en `juego/historia/` y sus pantallas en `juego/escenas/historia/`.
No importa nada del arcade (y el arcade no importa nada de acá): `tests/test_modos.py` lo vigila.
En la historia no hay récords ni logros (miden el avance del arcade).

| Qué | Dónde |
|---|---|
| **Cada misión** (ruta, diálogos, radio, fragmentos y secretos) | `juego/historia/misiones/m1_la_senal.py`... (un archivo por misión) |
| La clase base de las misiones, los renglones con condición y el registro | `juego/historia/mision.py` (`Mision`, `Fragmento`, `filtrar`) |
| Las reglas de una misión y la historia mientras jugás | `juego/historia/modo.py` (`ModoHistoria`) |
| Los tipos de secreto (cómo se encuentra un fragmento) | `juego/historia/secretos.py` |
| Los objetos secretos (moneda grabada, restos, baliza) | `juego/historia/reliquias.py` |
| Las fichas del Archivo (el porqué de cada cosa) | `juego/historia/fichas.py` |
| Quién habla (nombre, color y retrato) | `juego/historia/personajes.py` |
| La escritura de los Cantores: traducir, escribir, el ritmo en el tiempo | `juego/historia/glifos.py` |
| La radio (la cola de mensajes) y su caja | `juego/radio.py` y `carteles.radio()` |
| La galaxia, el hangar, diálogos, Archivo, final y qué pantalla sigue | `juego/escenas/historia/` (`galaxia`, `hangar`, `dialogo`, `archivo`, `final`, `pasajes`) |
| La galaxia: los sistemas, el peligro y el costo de los viajes | `juego/historia/galaxia.py` |
| El reloj de la Umbral: años, mensajes de Inés y el frente de la Marea | `juego/historia/tiempo.py` |
| Un sistema libre: su ruta generada y su peligro | `juego/historia/exploracion.py` (`ModoExploracion`) |
| El hangar y las piezas | `juego/historia/hangar.py` |
| Los módulos: peligros ambientales, planos y cómo se ven en la nave | `juego/historia/modulos.py` (las piezas las dibuja `nave.py`) |
| Los ecos | `juego/historia/ecos.py` |
| Lo que se guarda (misiones, fragmentos, fichas, años, ubicación, piezas, hangar, sistemas, puertas, planos) | `progreso.json`, en `guardado.Progreso` |
| Los sonidos (`fragmento`, `onda_corta`, `onda_larga`) | `herramientas/estudio/obras/efectos_director.py` |

**Para escribir una misión:** copiar un archivo de `historia/misiones/`, cambiar el número, el
título, el sector, el `lugar` en el mapa y los textos, e importarlo en
`historia/misiones/__init__.py`. Aparece sola en el mapa y en el Archivo. Una misión puede traer
su ruta (`tramos`, con `"anomalia"` por tramo), no tener jefe (`jefe = False`: termina con el
último tramo) o ser oculta (`oculta`, `requisitos`, `rama_de`). `tests/test_historia.py` revisa
el estándar: números seguidos, rutas con las reglas del arcade, momentos de radio que existen,
fragmentos sin repetir, cada fragmento con su secreto, condiciones con fragmentos que existen y
que cada texto entre en su caja.

**Para sumar un secreto:** el `Fragmento` (con su `reaccion`) en la misión y una línea en sus
`secretos`. Los tipos que hay:

| Tipo | Opciones | Cómo se encuentra |
|---|---|---|
| `moneda_grabada` | `monedas`, `desde_tramo` | una moneda blanca después de N monedas |
| `restos` / `baliza` | `tramo`, `espera` (`baliza`: `mensaje`) | algo cruza el fondo; se abre con el dash |
| `jefe_sin_golpes` | — | vencer al jefe sin recibir golpes en el sector |
| `jefe_vencido` | (con `requiere`) | vencer al jefe |
| `jefe_sin_romper` | `enemigo` | vencer al jefe sin romper ninguno de ese tipo |
| `partes_en_orden` | — | romper las piezas del jefe de izquierda a derecha |
| `racha` | `monedas` | juntar N monedas seguidas |
| `seguir_al_ladron` | `distancia` | seguir de cerca a un ladrón con la moneda hasta que salga |
| `quieto_en_anomalia` | `anomalia`, `mensaje` | quedarse quieta durante la anomalía hasta oír el mensaje |
| `golpe_desde` | `angulo`, `margen` | pegarle al núcleo del jefe desde un lado |

Cualquier tipo acepta `requiere` (fragmentos antes, o `"todos"`) y `pista` (lo que dice la radio
cuando aparece algo). Si ningún tipo sirve, uno nuevo en `secretos.py`: una clase con
`@registrar_secreto`, su `tipo`, `preparar(opciones)` y los avisos que escuche
(`al_empezar_tramo`, `al_recoger_moneda`, `al_llegar_jefe`, `al_vencer_jefe`, `al_romper`,
`al_romper_parte`, `al_golpear_jefe`, `al_escapar_moneda`, `actualizar`). Si el aviso no existe,
se suma a `modos.Modo` (la Partida o el Director lo dan) y al `ModoHistoria`. Y su test.

**Para sumar un enemigo, jefe, power-up o anomalía al juego:** también su ficha en `fichas.py`
(un test lo exige: todo tiene su porqué).

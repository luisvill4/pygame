# La Marea — la biblia del modo historia

> **Beta.** Todo se puede cambiar. Este documento es la referencia para escribir diálogos,
> secretos y misiones sin contradecirse. **Spoilers totales**: aquí está la verdad.

El juego tiene dos modos: **ARCADE** (la ruta infinita de siempre, con récords y logros) e
**HISTORIA** (las misiones de este documento, con diálogos, radio, secretos y el Archivo).

---

## 1. Lo que sabe el jugador al empezar

Lo cuenta el **prólogo** (`escenas/historia/prologo.py`), la primera vez que se entra a la
HISTORIA: un narrador y un dibujo por cuadro. Pedido del usuario: "ni siquiera sé qué es la
Marea: escribiste la historia pero no hay ningún guion". El guion completo, armado con los
textos del juego, está en **`GUION.md`** (`python herramientas/guion.py` lo rehace).

Una galaxia enana, mil veces más pequeña que la nuestra, viene directo hacia aquí. No va a chocar
contra nada: va a pasar cerca, y su gravedad va a tironear las estrellas y los planetas **como
la Luna tira del mar** hasta desarmar las órbitas. Por eso la llamaron **la Marea**. Faltan seis
años. No se puede frenar y ninguna nave llega lo bastante lejos para escapar.

En todas las radios aparece un **compás**: pulsos cortos y largos que se repiten, lentos, como
en cámara lenta. No es ruido: alguien lo manda. Suena más fuerte cerca de unos objetos de metal
que flotan en el Cinturón Exterior. Por la forma les dicen **monedas**.

Hace tres años, **Mateo Saavedra** salió con su nave, la **Errante**, a buscar de dónde venía el
compás. Nunca volvió.

**La relatividad (decisión del usuario: "es lo que más salsa le da al juego"):** para llegar
lejos hay que viajar casi a la velocidad de la luz, y eso tiene un precio. Para la piloto un
viaje dura horas; en la Estación Umbral pasan meses. Cerca de un agujero negro, todavía más.
Cada viaje acerca la Marea.

**Alba**, piloto de la nave **Alondra**, se ofrece a seguir el compás hasta donde nace. **Inés
Coria** la guía por radio desde la **Estación Umbral**.

## 2. La verdad (lo que se revela al final)

**El que dejó las monedas es uno solo: EL ÚLTIMO.** (Elección del usuario, entre tres ideas.
Reemplazó al bucle "los Cantores somos nosotros", que se parecía demasiado a *Interstellar*.)

1. Hace millones de años, la Marea pasó por **su** galaxia. Él era piloto. Siguió unas monedas
   que alguien había dejado en su cielo, pero **llegó tarde**: solo se salvó él.
2. Desde entonces viaja **adelante de la Marea**, casi a la velocidad de la luz: para él pasaron
   ochenta años; afuera, millones. En cada galaxia que la Marea va a cruzar deja lo mismo: las
   **monedas**, los **guardianes** (sus pruebas: el camino solo lo termina quien aprende el
   ritmo) y el **compás**, un camino hasta su refugio. **Nunca nadie llegó a tiempo.**
3. Su refugio está pegado al borde del agujero negro del Abismo, adentro del anillo que cuida
   *El Fin de la Luz*. Ahí abajo el tiempo casi se detiene: **una hora son mil años de afuera**.
   Por eso el compás suena lento: lo toca desde ahí.
4. La salida no es un lugar, es un **cuándo**: la Marea no se puede frenar, **pero se puede
   dejar pasar**. Las naves bajan unas horas con él y, cuando suben, la Marea ya está lejos y las
   estrellas quietas otra vez. Por eso el compás termina diciendo **VENGAN**.
5. Aprendió nuestro idioma escuchando nuestras radios durante cuarenta años (por eso escribe con
   Morse, el código más simple que encontró). Su nombre, en nuestro idioma, quiere decir
   **amanecer**: lo grabó en todas las monedas como **ALBA**. Que la piloto se llame igual es lo
   que hace que Inés diga "no te lo tomes personal".
6. **Mateo, Rocío y Tomás están vivos**, abajo, con él: la Errante se partió al borde del Abismo
   y bajaron en la cápsula. Para ellos pasaron dos días; para Inés, tres años.

**El final verdadero** (con todo encontrado): El Último le muestra a Alba su primera bitácora,
de cuando era un piloto joven siguiendo monedas. **A él también le dejaron un camino**, nunca
supo quién: siempre hubo alguien adelante. Ya está viejo y no aguanta otro viaje, y alguien tiene
que ir adelante de la Marea, a la galaxia que sigue. Alba se queda con su nombre y su tarea:
**ahora las monedas las deja Alba**. No es un bucle en el tiempo: es una **posta**.

**Regla de oro:** ningún secreto contradice esto, y cada uno, mirado después, apunta hacia aquí.

## 3. Personajes

| Quién | Quién es | Cómo habla |
|---|---|---|
| **ALBA** | Piloto de la Alondra. Terca, con humor seco. No cree en señales del destino. No tiene a nadie que la espere: por eso se ofreció. | Frases cortas. Se ríe del peligro. |
| **INÉS CORIA** | Astrofísica de la Estación Umbral. Es la voz de la radio. Vivió siete años con Mateo. | Precisa, cálida, cansada. Dice "compás" y no "señal". |
| **MATEO SAAVEDRA** | Capitán de la Errante. Oyó el compás tres años antes que nadie y salió a seguirlo. Está vivo, abajo, con El Último. | Tranquilo, un poco poeta. Hasta la misión 5 solo se oye su voz grabada. |
| **ROCÍO VEGA** | Ingeniera de la Errante. Fue la primera en notar que las monedas "cantan". | Entusiasta, desconfía de las explicaciones fáciles. |
| **TOMÁS ILIC** | Navegante de la Errante. Cuenta todo: los disparos, los días, los pulsos. | Metódico. |
| **EL ÚLTIMO** | El que dejó las monedas. El último de su pueblo. Aparece recién al final de la misión 5: viejo, con la capucha violeta y los ojos que brillan. Hasta ahí, Inés cree que son muchos y les dice "los Cantores". | Pausado, con frases cortas y un castellano aprendido de la radio. "Llegaste." |
| **SIN FECHA** | El Último joven, en su primera bitácora (el final verdadero). Su retrato es el mismo, sin arrugas y con colores vivos. | Como un piloto que recién empieza. |

La nave se llama **Alondra** porque la alondra es el pájaro que canta al amanecer, y *alba*
también quiere decir amanecer: la piloto y El Último tienen el mismo nombre, contra *El Fin de
la Luz*.

## 4. Cronología

| Cuándo | Qué pasa |
|---|---|
| Hace millones de años | La Marea arrasa la galaxia de El Último. Él sigue unas monedas que alguien dejó, llega tarde y se salva solo. Empieza a viajar adelante de la Marea. |
| Hace miles de años (de los nuestros) | Llega a nuestra galaxia. Sus máquinas arman el camino: las monedas (el Semillero), los guardianes, la Colmena (una biblioteca), el anillo del Abismo. |
| Hace cuarenta años | Una sonda de la Umbral graba el compás sin que nadie lo note (E01). Él empieza a escuchar nuestras radios. |
| Hace tres años | Mateo oye el compás. Nadie le cree. Sale con la Errante (Rocío y Tomás) a seguir las monedas. En la niebla aprende a leer los glifos. |
| Hace tres años, día 377 | La Marea alcanza a la Errante al borde del Abismo y la parte en tres. Mateo transmite "...es uno solo... se llama Alba..." y baja con la tripulación en la cápsula. Para ellos, desde entonces, pasaron dos días. |
| Hace tres meses | La Estación Umbral capta el compás. Inés lo decodifica en parte. |
| El juego | Alba sigue el compás, misión por misión. Cada viaje gasta meses en la Umbral. |
| Al final de la misión 5 | Alba baja y encuentra a El Último (y a Mateo). Su mensaje tarda tres días en llegar a la Umbral. El compás suma una palabra: VENGAN. Las naves se preparan. |

## 5. El porqué de cada cosa del juego

Todo lo que existe en el juego tiene su lugar en la historia. Lo cuentan las **fichas del
Archivo** (`juego/historia/fichas.py`), que se anotan solas la primera vez que se ve cada cosa
en una misión. Algunas esconden pistas (marcadas con ➜).

| Qué | Qué es en la historia |
|---|---|
| **Monedas** | Sellos de memoria de El Último: cada una guarda un pedazo del compás. Juntas y rápido "cantan" (la moneda suena más rica con el combo). |
| **El dash** | El salto de la Alondra sobre la marea gravitatoria. Inés lo inventó mirando cómo se mueven los guardianes. |
| **Perseguidores** | Centinelas. No buscan matar: alejan a cualquiera de las monedas. "¿Y si no las cuidan *de* nosotros, sino *para* nosotros?" |
| **Rebotadores** | Cápsulas de memoria dañadas: repiten un mismo segundo del pasado. En los restos de la Errante repiten su último segundo. |
| **Embestidores** | Arietes de construcción. Abrieron los túneles del Cinturón. |
| **Divisores** | Esporas de terraformación: se reparten al romperse, para sembrar. |
| **Enjambre y abejas** | Las obreras y las bibliotecarias de la Colmena, que es una biblioteca. ➜ "No son soldados" (F08). |
| **Ladrones** | Carteros: no roban, **llevan** las monedas al Abismo, a la casa de El Último. ➜ "¿A dónde llevan las monedas?" (F05). |
| **Escuderos** | Guardias de los archivos. Solo dejan pasar a quien los rodea: a quien sabe bailar. |
| **Power-ups** | Tecnología de El Último. ➜ El repuesto viene "a la medida de la Alondra: ¿cómo sabían las medidas?"; el imán, "como si las monedas reconocieran a la Alondra". La respuesta: hace cuarenta años que escucha nuestras radios y mira; vio armar la Alondra y probar el motor de Inés. |
| **Anomalías** | Lo que la Marea ya está rompiendo. ➜ En la niebla "se escucha mejor" (F06); en la fiebre del oro "cantan más fuerte que nunca" (F07). |
| **Los jefes** | **Guardianes del compás.** Pelean a ritmo porque *son* el ritmo. Ponen a prueba a quien sigue el camino: la puerta solo se abre para quien sabe bailar. El Acorazado es un metrónomo; la Colmena, la bibliotecaria mayor. |
| **La Singularidad** | El anillo que cuida la puerta: el refugio de El Último, pegado al borde del agujero negro, donde el tiempo casi se detiene. ➜ "¿Quién podría vivir ahí abajo?" |
| **La relatividad** | Una ficha básica (se anota al empezar): más rápido, más despacio pasa tu tiempo; cerca de un agujero negro, peor. |

## 6. Las misiones

Una por sector, en orden, más una oculta. Cada misión tiene **su propia ruta** (4 tramos con
nombres de la historia y la anomalía que necesita su secreto), diálogos antes y después, la
radio en cada tramo y secretos. Las misiones ganadas se rejuegan para buscar lo que falta.

| # | Lugar | Título | Lo que se descubre (la historia principal) |
|---|---|---|---|
| 1 | Cinturón Exterior | LA SEÑAL | Las monedas tienen un símbolo. El Ojo es una lente que mira más allá. El compás suma una nota y señala la Nebulosa, por donde pasó la Errante. |
| 2 | Nebulosa Carmesí | EL ACORAZADO | Inés cuenta quién era Mateo; Alba, por qué se ofreció. Los cañones son metrónomos: Inés traduce la primera palabra, **SIGUE**. |
| 3 | Campo Esmeralda | LA DEVORADORA | Alguien más junta monedas: los ladrones, que salen todos hacia el Abismo. En la niebla, la radio no pasa: Alba está sola. |
| 4 | Mar de Ámbar | LA COLMENA | La Colmena es una biblioteca. El mensaje se lee entero: **SIGUE LAS MONEDAS**, con una firma. El compás sale del Abismo, de un agujero negro. |
| 5 | Abismo Azul | EL FIN DE LA LUZ | El anillo se abre. Alba baja y encuentra a **El Último**, que le cuenta todo, y a Mateo, vivo. Ahí abajo una hora son mil años: se puede dejar pasar la Marea. El compás dice **VENGAN**. |
| 6 | Al borde del Abismo (oculta) | LOS RESTOS | Aparece con las tres bitácoras (F02, F04, F07). Sin guardián: los restos de la Errante y el diario de Mateo por la radio. La tripulación no está: falta la cápsula. Alba: "si bajaron al borde, para ellos pasaron minutos". |

**Los diálogos reaccionan a lo encontrado** (renglones con condición, ver `mision.py`): por
ejemplo, con la clave del compás (F06) y la moneda grabada (F01), Inés lee la firma: "DICE...
ALBA". Sin ellas, no la puede leer. Y la radio solo da una pista si todavía falta lo que señala.

## 7. Las capas del misterio

0. **El prólogo**: qué es la Marea, el compás, la Errante, la relatividad, Alba e Inés.
1. **La historia principal** (diálogos y radio): cualquiera la entiende jugando. Termina con
   el encuentro con El Último y VENGAN: se sabe quién llama y por qué.
2. **El Archivo**: los fragmentos (las mini historias de la Errante, de El Último y de los
   guardianes) y las fichas (el porqué de cada cosa).
3. **Lo cruzado**: pistas que solo tienen sentido juntas. La mirada del Ojo (F03) dice desde
   dónde pegarle a la puerta (F09); las monedas que "cantan" (F02) explican el eco de la
   Errante (F07); la clave del compás (F06) traduce todos los glifos.
4. **Lo muy hondo**: el compás *es* ALBA en Morse (la ficha EL COMPÁS lo muestra en glifos;
   en la misión 5 el compás lo "dice" por radio; el sonido de encontrar un fragmento lo toca):
   es el nombre de El Último. La moneda de la estela (F13) está firmada MATEO y recién grabada:
   Mateo está vivo. El poema de la Colmena (F08) está en singular: es uno solo. Quien sepa Morse
   puede leer todo esto antes de tener la clave.
5. **La verdad**: la Bitácora sin fecha (F11), la primera bitácora de El Último. Pide haber
   encontrado todo lo demás, y abre el final verdadero.

## 8. El código de los glifos

El Último escribe con **ritmos**: cada glifo es una letra hecha de pulsos cortos (◇) y largos
(▬). Es Morse, pero el jugador no lo sabe: lo descubre al encontrar **la clave del compás**
(F06, misión 3). Con la clave, el Archivo traduce todo lo que ya encontró.

| Dónde | Dice |
|---|---|
| F01 La moneda grabada (la firma de El Último) | ALBA |
| F04 La Errante 2/3 (en los cañones) | ATRAS |
| F05 El cartero (en la espalda del ladrón) | CASA |
| F08 Las bibliotecarias | OTRA |
| F09 La brújula | CUANDO |
| F12 La baliza (la parpadea) | SIGUE |
| F13 La otra firma | MATEO |
| La ficha EL COMPÁS, el sonido `fragmento` y E08 | ALBA |
| La pantalla final | SIGUE LAS MONEDAS |

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
| F03 | 1 | La mirada del Ojo | Vencer al Ojo sin recibir un golpe en todo el sector. | Radio jefe: "si sales sin un rasguño, puedo medir a dónde apunta". | La lente apuntaba al Abismo, como una brújula. | Algo importante está en el Abismo (y es la clave de F09). | 🟨 |
| F04 | 2 | La Errante 2/3 | Romper los cuatro cañones del Acorazado **de izquierda a derecha** (se puede: el que no toca, no se le pega). | Radio jefe: "Mateo decía que un reloj se lee como un libro. En orden". | Tomás: los cañones son relojes y cuentan hacia atrás, como una cuenta regresiva. Glifo ATRAS. | Alguien sabe cuánto falta. | 🟨 |
| F12 | 2 | La baliza | En la tormenta solar (tramo 3) cruza una baliza apagada que parpadea con un glifo. Dash. | Radio T3: "entre la estática me llega una baliza. ¿La ves?" | La grabación de Mateo: "Estamos bien. Seguimos. No nos esperen". Parpadea SIGUE. | Mateo leyó la primera palabra hace tres años. | 🟨 |
| F05 | 3 | El cartero | Dejar que un ladrón se lleve la moneda y **seguirlo de cerca** sin alcanzarlo hasta que salga (sigue las monedas, al pie de la letra). | Radio T2: "quiero saber a dónde llevan las monedas". Ficha del ladrón. | No la robó: la llevó al Abismo, como quien vuelve a casa. Glifo CASA. | Las monedas vuelven al Abismo: alguien vive ahí. | 🟨 |
| F06 | 3 | La clave del compás | En la niebla (tramo 3), quedarse **quieta** (sin tocar nada) hasta oír la palabra entera: 12 pulsos, ~8 s. Cada pulso suena y la nave lo siente. Moverse vuelve a empezar. | Antes: "Mateo decía que en el silencio se escucha mejor el compás". Ficha de la niebla. | Los glifos son ritmos. El Archivo los traduce desde ahora. | La firma dice ALBA ("o como el amanecer"). | 🟨 |
| F07 | 4 | La Errante 3/3 | Juntar **20 monedas seguidas** (en la fiebre del oro es posible): cantan tan fuerte que la radio capta un eco de hace tres años. | Radio T3: "si las juntás sin parar, la radio se acopla". Ficha de la fiebre. | La última transmisión de Mateo: "...es uno solo... se llama Alba...". | No son muchos, y se llama como ella. | 🟨 |
| F08 | 4 | Las bibliotecarias | Vencer a la Colmena **sin romper ninguna abeja**. | Radio jefe: "las abejas son bibliotecarias. No son soldados". Ficha de la abeja. | Un poema en singular: "La vi llegar una vez, y se llevó a todos. La voy a ver llegar otra. Esta vez no voy a llegar tarde". Glifo OTRA. | Es uno solo, y ya vivió esto. | 🟨 |
| F09 | 5 | La brújula | Con F03: pegarle al núcleo de la puerta **desde la izquierda** (el lado de casa, hacia donde miraba el Ojo). | Radio jefe (solo con F03): "la lente del Ojo apuntaba aquí. Desde el Cinturón... desde casa". | El reloj de la Alondra casi se detiene. "No lleva a otro lugar. Lleva a otro cuándo". | Ahí abajo el tiempo casi no pasa. | 🟨 |
| F10 | 6 | El último registro | En el tramo 3 de LOS RESTOS cruza un pedazo del casco: la caja negra. Dash. | Al aparecer, Alba: "la caja negra tiene que estar ahí". | Mateo: la nave no aguanta, entran a la puerta. "No es un final". | La tripulación bajó: puede estar viva. | 🟨 |
| F13 | 6 | La otra firma | En el tramo 4 de LOS RESTOS (la estela de la cápsula), después de 6 monedas aparece otra moneda blanca. | Al aparecer, Alba: "¿Otra moneda blanca? ¿Aquí?". Radio T4: "algo salió de la Errante hacia la puerta". | Una firma torpe, hecha a mano, en metal nuevo. Glifo MATEO. | Mateo está vivo. | 🟨 |
| F11 | 5 | Bitácora sin fecha | Con **todos** los demás encontrados: vencer a la Singularidad. Es *oculto*: no aparece en el Archivo hasta encontrarlo. | La pantalla final: "El Último todavía tiene algo para contarte" (si solo falta este). | La primera bitácora de El Último, joven: "En mi cielo aparecieron monedas. Voy a seguirlas". | A él también le dejaron un camino (el final verdadero). | 🟨 |

Los fragmentos de la misión oculta tampoco aparecen en el Archivo hasta que aparece la misión
(la cuenta de arriba sí los suma: hay más de lo que se ve).

## 10. La galaxia y el tiempo

El mapa de la historia es una **galaxia que se recorre libre**: las misiones son sistemas
marcados y entre ellas hay 16 **sistemas libres**.

- **La relatividad** (el usuario la probó sin ella y la quiso de vuelta: "es lo que más salsa
  le da al juego"): para Alba un viaje dura horas; en la Estación Umbral pasan **años** (viaja
  casi a la velocidad de la luz, y cerca del Abismo la gravedad estira su tiempo todavía más:
  cada visita ahí suma años de **dilatación**). Lo que cuenta es el reloj de la Umbral. La
  Marea llega en el año 6.
- **El costo:** cada viaje gasta años según la distancia; cada salida, aunque no viajes, gasta
  un poco (nada es gratis). El camino directo de la historia cuesta ~3.8 años en viajes, pero
  los módulos obligan a explorar para juntar piezas: una campaña simulada termina cerca del año
  4.4 (y en el 5.3 si se juntan pocas piezas). Explorarlo todo no se puede a tiempo: hay que elegir.
- **La Marea se ve:** un frente rojo avanza desde la izquierda y en el año 6 se traga la Umbral.
  Lo que traga ya no se puede visitar.
- **Inés envejece:** cada año que pasa manda un mensaje ("para ti fueron unas horas; para mí,
  un año"). En el año 6, la Umbral cae y ella sigue a Alba con los que pudieron subir a las naves.
- **Un viaje largo pregunta antes:** si gasta un año o más (`VIAJE_LARGO_ANIOS`), o si cruza un
  año en que la historia cambia (`tiempo.HITOS`: el 3, Inés empieza a pedir que te apures; el 6,
  la Umbral cae), la galaxia dice cuántos años pasan y qué cambia, con QUEDARME elegido por
  defecto.
- **La historia reacciona al tiempo** (renglones con `T3`, `!T6`): Inés pide que se apure, y si
  la misión 5 se cumple tarde, el final cambia: "Llegamos tarde para los demás. Pero vamos". La
  pantalla final dice el año y "LLEGASTE TARDE".
- **Con la historia terminada el reloj se detiene:** lo que quedó se puede explorar sin apuro.
- **Cuanto más lejos, más peligro** (de 1 a 5, por la distancia a la Umbral): escuadrones más
  grandes y más rápidos. Desde peligro 3, el último tramo es un asedio.
- **Los módulos abren la galaxia** (pedido del usuario: "que las galaxias estén bloqueadas y se
  desbloqueen a medida que se mejora la nave, y que se vea en la nave"). **Todos** los sistemas
  libres tienen
  un **peligro ambiental** con intensidad 1 o 2, y para entrar hace falta el **módulo** de ese
  peligro con ese nivel. Los peligros están **mezclados** por el mapa (casi siempre el del
  bioma, pero con excepciones en todas las zonas): cada módulo abre lugares en varias zonas y el
  orden lo elige el jugador. Es una red, no una escalera.
  - Un módulo se fabrica en el Hangar (pestaña MÓDULOS) con su **plano** y piezas. Al empezar
    solo la misión 1 está abierta: da el plano del escudo térmico, que abre los primeros
    sistemas. Los otros planos están en uno o dos sistemas libres (se consiguen al despejarlos) y además Inés lo diseña al cumplir
    la misión anterior a la que lo pide: **la historia nunca se traba** (lo comprueba un test).
  - **Cada nivel se ve en la Alondra** (pixel art encima del sprite, en la grilla de 2 px). En
    el arcade la nave va siempre limpia.

  | Módulo | Peligro | Nivel 1 | Nivel 2 | Plano en |
  |---|---|---|---|---|
  | Escudo térmico | calor (estrellas) | placas naranjas en el borde de las alas | una fila roja más adentro | misión 1 |
  | Filtro de esporas | esporas | cápsulas de metal con luz verde al lado de la cabina | más largas, con dos luces | Vega del Sur, misión 2 |
  | Casco de panal | panal (la Colmena) | un panal dorado ralo en las alas | una placa dorada en el borde de atrás | Kepler, Espora, misión 3 |
  | Compensador | gravedad (el Abismo) | un anillo violeta abajo del motor | aletas en las puntas de las alas | Brasa, Oráculo, misión 4 |

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
| E03 | Oráculo | El reloj de arena | Un púlsar marcado por El Último que cuenta los latidos hasta la Marea. Glifo PRONTO. |
| E04 | Semillero | El planeta que canta | La fábrica de las monedas. Glifo HOGAR. |
| E05 | Vigía | El vigía | Una máquina de El Último que espera a la Alondra, la mira y se apaga. Glifo LLEGO. |
| E06 | Miel | Los que escaparon | Una nave generacional de hace 300 años que oyó el compás y dio la vuelta para seguirlo. El diario termina a mitad de camino: nunca llegaron (nadie llegó a tiempo). |
| E07 | Horizonte | La carta | Un mensaje de Inés a Mateo ("vuelve") que tardó tres años en llegar y nunca lo recibió. |
| E08 | Umbra (peligro 5) | La otra Alondra | Los restos de **la nave de El Último**, de cuando era piloto: no es humana, pero se parece a la Alondra como una hermana. Millones de años de polvo y ALBA rayado en la cabina. Lo más hondo para quien llega más lejos: él también fue piloto. |

## 11. Los finales

Después del diálogo de la misión 5 viene la **pantalla final** (`escenas/historia/final.py`):

- **El de siempre:** después del encuentro con El Último, Inés da la orden: "Preparen todas las
  naves. Nos vamos" (tarde: "Llegamos tarde para los demás. Pero vamos"). La pantalla dice "LA
  MAREA — FIN" en rojo, con la música del Game Over: el mensaje del compás en glifos (sin
  traducir), lo encontrado (misiones, fragmentos, fichas) y "Todavía hay cosas que no
  encontraste" (o "El Último todavía tiene algo para contarte" si solo falta la Bitácora).
- **El verdadero** (con F11): El Último le hace oír su primera bitácora (SIN FECHA), le cuenta que
  a él también le dejaron un camino y que ya no aguanta otro viaje. Alba no baja con los demás:
  va a ir adelante de la Marea. "Mi nombre quiere decir amanecer... ahora es tuyo de verdad". La
  pantalla dice "**EL PRINCIPIO**" en amarillo, con la música en Do mayor, el mensaje traducido
  (SIGUE LAS MONEDAS) y "AHORA LAS MONEDAS LAS DEJA ALBA".

**El mapa también cuenta la historia:** arriba dice "LA MAREA LLEGA EN 6 AÑOS"; después de la
misión 5, "EL COMPAS DICE: VENGAN"; con la verdad, "SIGUE LAS MONEDAS". El planeta del Abismo
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
- **Español neutro** (pedido del usuario): tú y nunca vos (TIENES, SIGUE, PARA TI), AQUI y no
  ACA, PEQUEÑO y no CHICO. `test_textos.py` busca las palabras del voseo en todo el juego.

## 13. Cómo está hecho (para seguir escribiendo)

Todo el modo historia vive en `juego/historia/` y sus pantallas en `juego/escenas/historia/`.
No importa nada del arcade (y el arcade no importa nada de aquí): `tests/test_modos.py` lo vigila.
En la historia no hay récords ni logros (miden el avance del arcade).

| Qué | Dónde |
|---|---|
| **El prólogo** (la cinemática del principio: cuadros con su dibujo y el narrador) | `juego/escenas/historia/prologo.py` |
| **El guion** (todo lo que se dice, en orden; se arma solo) | `GUION.md`, con `python herramientas/guion.py` (un test avisa si quedó viejo) |
| **Cada misión** (ruta, diálogos, radio, fragmentos y secretos) | `juego/historia/misiones/m1_la_senal.py`... (un archivo por misión) |
| La clase base de las misiones, los renglones con condición y el registro | `juego/historia/mision.py` (`Mision`, `Fragmento`, `filtrar`) |
| Las reglas de una misión y la historia mientras jugás | `juego/historia/modo.py` (`ModoHistoria`) |
| Los tipos de secreto (cómo se encuentra un fragmento) | `juego/historia/secretos.py` |
| Los objetos secretos (moneda grabada, restos, baliza) | `juego/historia/reliquias.py` |
| Las fichas del Archivo (el porqué de cada cosa) | `juego/historia/fichas.py` |
| Quién habla (nombre, color y retrato) | `juego/historia/personajes.py` |
| La escritura de El Último: traducir, escribir, el ritmo en el tiempo | `juego/historia/glifos.py` |
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

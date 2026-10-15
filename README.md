# Caza Monedas

Juego arcade 2D hecho con Pygame: una nave recoge monedas, esquiva enemigos y pelea contra jefes.

## Cómo jugar

```
pip install -r requirements.txt
python main.py
```

Al abrir, primero sale una advertencia de fotosensibilidad (con cómo reducir los destellos), después "HECHO CON PYGAME" y la pantalla de título: la nave llega del hiperespacio, el logo cae y empieza la música. Cualquier tecla o botón saltea directo al título, y desde ahí **ENTER** (o **A** en el mando) abre el menú.

| Acción | Teclado | Mando de Xbox |
|---|---|---|
| Mover | Flechas | Stick izquierdo (cualquier ángulo) o cruceta |
| Dash | Espacio | X |
| Aceptar | Enter | A |
| Pausa | P o Esc | Menú (≡) |
| Opciones (en pausa) | O | Vista (⧉) |
| Volver | Esc | B |
| Cambiar de pestaña o sección (menús) | Q / E | LB / RB |
| Silenciar / activar el sonido | M | |
| Pantalla completa / ventana | F11 | |
| Modo desarrollador (en la partida) | F1 | |

**Vibración del mando.** Es suave y solo aparece en los momentos importantes: subir el combo, romper enemigos con el dash, power-ups, golpes, subir de nivel, logros y jefes (llega con un latido, cuando le pegás y cuando explota). Lo que pasa todo el tiempo, como agarrar cada moneda o hacer un dash, no vibra. Los dos motores del mando suben y bajan de a poco, y los gatillos no vibran. La intensidad se elige en **Opciones → ACCESIBILIDAD → VIBRACION** (NO, SUAVE, NORMAL, FUERTE).

**Los menús.** Abajo de cada pantalla hay una barra con los botones que sirven ahí, dibujados como en tu control: si tocás el teclado muestra las teclas y si tocás el mando muestra sus botones (A verde, B roja, LB/RB...). En el inicio, ARRIBA/ABAJO elige (JUGAR, LOGROS, OPCIONES o SALIR) y LB/RB o IZQ/DER cambia la página del panel de la derecha. Entre pantalla y pantalla hay una transición de rombos.

Al elegir **JUGAR** se elige la dificultad (FÁCIL, NORMAL, DIFÍCIL o PESADILLA); cada una tiene su propia tabla de récords. En FÁCIL y NORMAL el embestidor deja de seguirte con la mira un momento antes de embestir (la línea roja deja de parpadear): ahí es cuando hay que correrse. En DIFÍCIL y PESADILLA te sigue hasta el último instante.

### La ruta: sectores, tramos y escuadrones
Cada **sector** es una ruta de **4 tramos** y su **jefe**, como las fases de un juego de naves. Abajo a la derecha está el mapa: **SECTOR 2-3** quiere decir sector 2, tramo 3; hay un punto por tramo y la calavera del jefe al final. Lo recorrido se pinta del color del sector y el camino entre tu punto y el siguiente es la **barra de energía**.

Cada tramo tiene su idea y su cartel ("TRAMO 2/4 · BLANCO FÁCIL · ¡ROMPELOS CON EL DASH!"):
- **Tramos 1 y 2:** presentan a los enemigos del sector, de a uno por tramo.
- **Tramo 3, ZONA INESTABLE:** llega la anomalía del sector, con pocos enemigos.
- **Tramo 4, ASEDIO:** escuadrones de todos lados durante 15 segundos. Aunque se llene la barra, el jefe espera a que termine el asedio. Si lo pasás sin perder una vida: puntos y un power-up.

Los enemigos llegan en **escuadrones**: primero una **flecha** en el borde (y un sonido que viene de ese lado), después el grupo entra volando en formación (mientras entra no lastima) y, cuando se le termina el turno, se **retira** (en gris: ya no lastima). Si rompés a todo un escuadrón, ganás un bonus. Un enemigo que te choca también se va. Así la pantalla nunca se llena de enemigos viejos.

Para pasar al tramo siguiente hacen falta dos cosas, como en Metal Slug: la **barra llena** y la **zona despejada** (llegaron todos los escuadrones del tramo y no queda ninguno). Con la barra llena el tramo se apura: los que faltan entran enseguida y los que están se van pronto; si los rompés, despejás más rápido. Al pasar de tramo las estrellas pegan un acelerón.

### Subir de nivel: la barra de energía
Cada tramo es un nivel. Todo lo que hacés bien llena la **barra de energía** (el camino de la ruta) y, cuando se llena y la zona está despejada, pasás al tramo siguiente (lo que sobra pasa al siguiente):

| Qué | Energía |
|---|---|
| Moneda | 1, y +0.25 por cada paso del combo (con x5, 2 por moneda) |
| Dash perfecto | 1.5 |
| Enemigo destruido (o congelado roto) | 0.5 |
| Escuadrón eliminado entero | 1 |
| Asedio superado | 3 |
| Desafío cumplido | 5 |

El nivel 1 pide 10 y cada nivel pide 1 más, hasta 16. Jugar con combo alto y usar el dash te hace avanzar más rápido. Durante la pelea con el jefe (y mientras se ven sus carteles) no se gana energía: la barra se ve gris.

### El dash
El dash es la herramienta principal: te lanza hacia adelante y durante ese instante **nada te hace daño**.

- Algunos enemigos (el divisor, el enjambre, las abejas) y algunos proyectiles (misiles, asteroides) se **destruyen** con el dash, y cada uno adelanta la recarga. Atravesar a los demás enemigos o a las balas solo te salva del golpe: no da nada.
- **Dash perfecto:** romper (o partir) con el dash a un enemigo destruible es un "¡PERFECTO!": unos puntos más, el combo no se corta y **el dash se recarga casi enseguida**. Varios seguidos (antes de 1.5 s) forman una **cadena** que multiplica esos puntos hasta x5.
- **Interceptar:** si le pegás con el dash al **embestidor mientras embiste**, lo frenás en seco: queda aturdido 2 s (no lastima), da 10 puntos y cuenta como dash perfecto ("¡INTERCEPTADO!").
- **El ladrón** (desde el sector 3) no lastima: va hacia la moneda y, si la agarra, se queda quieto medio segundo y huye con ella al borde más cercano. Mientras la lleva, el combo no se corta. Si lo alcanzás con el dash, **recuperás la moneda** (se cobra en el momento, con 10 puntos más) y es un dash perfecto. Si se escapa, se corta el combo y la moneda aparece en otro lado.
- **El escudero** (desde el sector 4) tiene un escudo de frente que gira despacio hacia vos. Un dash de frente **rebota** (no te lastima, pero no le hace nada); rodealo y rompelo **por el costado o la espalda**. Las ondas y el ECO también chocan contra el escudo.
- Contra los jefes, el dash es la única forma de pegarles.

### Mejoras (el Taller y la gasolinera)
En el **nivel 3** el juego se detiene y te ofrece **3 cartas gratis** (el Taller): elegís una y dura toda la partida. Después, las cartas se **compran en la gasolinera** (ver abajo). Se pueden repetir hasta su nivel máximo. Así cada partida termina con una nave distinta:

| Mejora | Qué hace |
|---|---|
| **DOBLE DASH** *(rara)* | Un dash más seguido antes de recargar (se ve como un cuadradito al lado de "DASH"). Una sola vez y desde el sector 3. |
| **ECO** | Cada dash tiene un 25% (45% en nivel 2) de dejar una copia violeta que lo repite un momento después: destruye, aturde y rompe balas. |
| **RECARGA** | El dash se recarga un 20% más rápido (por nivel). |
| **ONDA** | Al terminar cada dash, una onda rompe balas, destruye a los enemigos destruibles y empuja (y aturde) a los demás. |
| **COMETA** | Dash un 50% más largo. |
| **FILO** *(rara)* | El dash destruye a **todos** los enemigos. Desde el sector 2. |
| **ESCUDO ROCE** | Tu escudo se regenera: cada 6 dash perfectos (4 en nivel 2, 3 en nivel 3) ganás un escudo que dura hasta el próximo golpe, y después se vuelve a cargar. La carga se ve abajo a la izquierda. |
| **BOTIN** | Destruir con el dash da el doble de puntos y recarga más. |
| **MOTOR** | La nave va un 12% más rápido. |
| **ATRACCION** | La moneda viene sola si estás cerca. |
| **COMBO LARGO** | El combo tarda un 30% más en cortarse. |
| **CORAZON** | +1 vida máxima (y te cura una). |
| **FENIX** *(rara)* | Si perdés la última vida, volvés con una (una vez). |
| **SUERTE** | Los power-ups caen más seguido. |
| **POTENCIA** | Los power-ups duran un 40% más. |

### Power-ups
Caen desde arriba cada tanto. No caen del todo al azar: el juego elige **el que más sirve en ese momento** (la vida si te queda una, el hielo si hay muchos enemigos, el escudo contra un jefe...) y casi nunca repite el mismo dos veces seguidas.

| Power-up | Qué hace |
|---|---|
| **ESCUDO** | Aguanta un golpe. |
| **HIELO** | Congela a los enemigos (tocarlos da puntos) y rompe las balas. |
| **VIDA** | Recupera una vida. |
| **IMAN** | La moneda vuela hacia vos. |
| **DOBLE** | Puntos dobles. |
| **TURBO** | Más velocidad, hasta perder una vida. |
| **RECARGA** | El dash se recarga el doble de rápido, hasta perder una vida. |
| **NOVA** | Tu próximo dash termina en una gran explosión (rompe balas, destruye y aturde). |

### La gasolinera y los créditos
Cada moneda da **créditos** además de puntos: tantos como el multiplicador del combo (con x5, 5 por moneda; en la fiebre del oro, el doble). Se ven arriba a la izquierda, al lado del puntaje. **No son puntos:** gastarlos no te baja el puntaje ni el récord.

Después de cada jefe (cuando terminan los carteles del rango) parás en la **gasolinera espacial "La Última Gota"**: tu nave carga combustible mientras comprás en el mostrador. IZQ/DER elige, ENTER compra (todo lo que te alcance) y ESC sigue viaje. Lo que no gastes queda para la próxima parada.

- **Cartas:** 3 mejoras al azar. Una carta nueva cuesta 40; cada nivel que ya tengas de ella suma 25; las raras cuestan 50% más; y todo sube un 20% en cada sector.
- **Servicios,** según la dificultad:

  | | SORTEAR (cambia las cartas; cada vez más caro) | ESCUDO (hasta el próximo golpe) | REPARAR (+1 vida) |
  |---|---|---|---|
  | FÁCIL | ✓ | ✓ | ✓ |
  | NORMAL | ✓ | ✓ | |
  | DIFÍCIL | ✓ | | |
  | PESADILLA | | | |

Todo se paga: si llegás sin créditos, no te llevás nada. Jugar con combo alto rinde el doble, porque da más energía **y** más créditos.

### Logros y naves
Hay **16 logros** (vencer a tu primer jefe, 10 dash perfectos, rango S, 5000 puntos...). Se guardan entre partidas en `progreso.json` y cuando desbloqueás uno aparece abajo al centro, con un trofeo (y si regala una nave, te lo dice). Varios logros desbloquean **naves de otro color**: se eligen en **LOGROS** (desde el inicio) con IZQ/DER.

Al perder, el **Game Over** muestra el resumen de la partida: tiempo, sector, monedas, mejor combo, enemigos destruidos, dash perfectos (y la mejor cadena), desafíos, el rango de cada sector y las mejoras que elegiste. ENTER juega otra vez; ESC vuelve al menú. En la **pausa** también se ve cómo va la partida y tus mejoras.

### Carteles
Cada cosa tiene su lugar, así nunca se pisan:
- **Arriba al centro, los avisos:** el tramo nuevo (el asedio, con cinta de peligro), ¡ASEDIO SUPERADO!, cada anomalía con su consejo y ¡NUEVO RECORD!. Salen **de a uno**: el que llega espera su turno, salvo una amenaza (una anomalía o la última vida), que pasa primero.
- **A los costados, las fichas:** enemigo nuevo (izquierda) y desafío (derecha). Si el aviso de arriba es ancho, bajan para no tocarlo.
- **Abajo al centro, los logros.**
- **De lado a lado, los grandes momentos:** ¡JEFE VENCIDO! (con el premio), el rango del sector (las estrellas salen de a una y al final cae la letra como un sello) y, al volver de la gasolinera, el nombre del sector nuevo.

Todos se vuelven casi transparentes cuando tienen algo abajo (la nave, la moneda, un enemigo, una bala), así nunca te tapan el juego. Mientras jugás, las nebulosas y los planetas del fondo se ven más oscuros que en los menús: así lo que importa se lee primero.

### Sectores y jefes
El viaje pasa por 5 **sectores**, cada uno con su ambiente (asteroides, brasas, luciérnagas, un panal gigante, polvo que cae en un agujero negro), su ruta de tramos y **su jefe**, que llega cada 5 niveles. Al vencerlo se pasa al sector siguiente; después del último se vuelve a empezar, con escuadrones más grandes.

Las peleas son un **baile**: cada jefe avisa antes de atacar, ataca al ritmo de su "pulso" y después deja un hueco para pegarle con el dash.

| Sector | Jefe | Cómo se le gana |
|---|---|---|
| Cinturón exterior | **El Ojo** | Esquivá sus abanicos y anillos; cuando queda cansado, dash al núcleo. |
| Nebulosa carmesí | **La Fortaleza** | Sus 4 cañones atacan de a uno (ráfaga, misiles, láser y minas) y quedan recalentados: dash al que brilla. Sin cañones se le cae la coraza y cae sobre vos: salí de la columna roja y pegale cuando queda aturdida en el piso. |
| Campo esmeralda | **La Serpiente** | Te rodea y muerde en línea recta (marca la línea antes). Si se estrella contra un borde, queda mareada y su cascabel brilla: dash a la cola. Después también se enrosca: salí del círculo. |
| Mar de ámbar | **La Colmena** | Abre una compuerta, suelta abejas y la deja abierta: rompela con el dash. Sin compuertas embiste rebotando (el aviso muestra el camino): cuando queda aturdida, dash al ojo. |
| Abismo azul | **La Singularidad** | Te atrae (el dash te libera). El anillo de asteroides gira a ritmo; cuando colapsa, entrá por un hueco y dash al núcleo. |

### Anomalías, desafíos y rango
- **Anomalías:** en el tramo 3 de cada sector (ZONA INESTABLE) el espacio se pone raro hasta que termina el tramo (20 segundos como mucho). Cada sector tiene la suya, que llega la mitad de las veces; la otra mitad llega una de las otras, así las cuatro se pueden ver desde el primer sector. Siempre avisan antes de atacar:

  | Sector | Suele traer | Qué pasa |
  |---|---|---|
  | Cinturón exterior | **Lluvia de asteroides** | Una columna roja punteada marca por dónde cae cada asteroide. El dash los rompe y dan puntos. |
  | Nebulosa carmesí | **Tormenta solar** | Una franja (vertical u horizontal) parpadea y después quema: salí antes. |
  | Campo esmeralda | **Niebla cerrada** | Solo ves cerca de la nave; de los enemigos lejanos ves los ojos, y la moneda brilla a través de la niebla. |
  | Mar de ámbar | **Fiebre del oro** | La buena: las monedas valen el doble (y dan el doble de créditos) y el combo tarda más en cortarse. |
  | Abismo azul | Una al azar | No tiene una propia: siempre la sortea. |

- **Desafíos (opcionales):** al llegar a cada sector (en el primero, en el nivel 2) aparece un reto a la derecha, debajo de las vidas: **SIN DASH**, **INTOCABLE** (sin recibir golpes), **SIN AYUDA** (sin agarrar power-ups), **SIN CORTAR EL COMBO** (12 monedas seguidas), **CAZADOR** (destruir 6 enemigos con el dash) o **INTERCEPTOR** (frenar 3 embestidas con el dash). Los tres primeros se cumplen al llegar al jefe; los otros, apenas los lográs. Premio: puntos y un power-up.
- **Rango:** al vencer al jefe, el sector se califica de **S** a **C** con estrellas: sin golpes (2), combo de 12 (1), desafío cumplido (1) y jefe vencido rápido (1). S = 5 estrellas, A = 4, B = 2 o 3. Cada letra da puntos extra.

**Opciones** tiene tres secciones, a la izquierda: se cambia con **LB/RB** (o **Q/E**). Debajo de cada opción hay una explicación de lo que hace:

- **VIDEO:** RESOLUCION, FPS, CRT (las líneas de pantalla antigua: NO, SUAVE o NORMAL), ESCALADO (NITIDO, o SUAVE para que en pantallas grandes todos los píxeles se vean del mismo tamaño; es un poco más lento) y NEON (el brillo de las balas, la moneda, las cápsulas y las explosiones: NO, SUAVE o NORMAL).
- **SONIDO:** tres barras: VOLUMEN (el de todo), MUSICA y EFECTOS (en 0 no suenan). La tecla **M** calla todo y lo vuelve a prender sin tocar las barras. Y LATIDO: un latido suave cuando te queda una sola vida.

**Música:** cada pantalla tiene su tema y al cambiar se cruzan con un fundido: uno tranquilo en los menús, el de siempre al jugar, uno rápido contra los jefes y uno con swing en la gasolinera. Toda la música y los efectos están hechos con código, en el estudio: `python herramientas/componer.py` los vuelve a generar (las melodías están escritas como una grilla de notas, fáciles de cambiar). Los premios, los power-ups y la interfaz **siguen al acorde** de la música (cada uno está compuesto en 11 versiones, una por color de acorde), y el mezclador cuida que la suma de todo nunca sature. CLAUDE.md (sección "Sonido y música") explica la notación, los instrumentos y cómo agregar un tema o un efecto al juego.
- **ACCESIBILIDAD:** TEMBLOR (cuánto se sacude la pantalla con los golpes: NO, SUAVE o NORMAL; el marcador nunca tiembla), DESTELLOS (REDUCIDOS: sin destellos de pantalla completa y nada parpadea más de 3 veces por segundo, para personas con fotosensibilidad), AVISO JEFE, VIBRACION y AUDIO MONO (todo suena igual por los dos lados, para quien usa un solo auricular u oye de un solo oído; sin esto, los sonidos salen del lado donde pasan las cosas).

El juego es panorámico (16:9): se dibuja en 1066x600 y se agranda a la ventana sin perder los píxeles. En **Opciones → VIDEO → RESOLUCION** se elige el tamaño de la ventana o la pantalla completa (también con **F11**).

En **Opciones → VIDEO → FPS** se elige cuántas veces por segundo se dibuja: 30, 60, 90, 120, 144 o SIN LIMITE. El juego va siempre a la misma velocidad: la lógica avanza 60 veces por segundo y, por encima de 60 FPS, el movimiento se dibuja interpolado (más suave en monitores de alta frecuencia).

**Modo desarrollador.** En plena partida, **F1** abre un panel para probar cosas sin llegar jugando: traer cualquier **jefe** (si ya hay uno, lo cambia), traer un **enemigo** de cualquier tipo, darte un **power-up** al instante, traer una **anomalía**, ponerte **invencible**, **limpiar** la pantalla de enemigos y balas, o abrir la **gasolinera** con 200 créditos de regalo. ARRIBA/ABAJO elige la fila, IZQ/DER cambia el valor y ENTER lo hace y vuelve al juego; F1 o Esc vuelven sin hacer nada. Una partida en la que se usó el panel dice **MODO DEV** abajo y **no guarda récord ni logros**. Para apagarlo (por ejemplo, si le pasás el juego a otros), poné `MODO_DESARROLLADOR = False` en `juego/config.py`.

## Cómo correr los tests

```
python -m pytest
```

Son tests automáticos de las reglas del juego: choques, combo, monedas, enemigos, jefe, power-ups, guardado, controles y el recorrido por las pantallas. Tardan unos segundos y no abren ventana. **Correlos después de cada cambio:** si algo se rompió, te dicen exactamente qué.

## Cómo está organizado el código

```
main.py                 # solo arranca el juego
juego/
  config.py             # TODOS los números que se pueden ajustar (dificultad, velocidades...)
  app.py                # crea todo y corre el bucle principal
  partida.py            # el estado de una partida y sus reglas
  nave.py  moneda.py  proyectiles.py
  progresion.py         # el "director": tramos, escuadrones, asedio, sectores, mejoras
  guiones.py            # la ruta de cada sector: los 4 tramos y sus escuadrones (solo datos)
  escuadrones.py        # las formaciones (por donde entran) y el Escuadron
  anomalias.py  desafios.py  rango.py   # lo que pasa en cada sector
  mejoras.py            # las cartas del Taller y de la gasolinera
  tienda.py             # la gasolinera: que se vende, los precios y que pasa al comprar
  estadisticas.py       # lo que pasa en la partida (para el Game Over y los logros)
  avisos.py             # la cola de avisos: los carteles de arriba salen de a uno
  carteles.py           # como se ven los carteles: avisos, fichas, logro, jefe vencido, rango, sector
  logros.py             # los logros (y que nave desbloquea cada uno)
  eco.py                # la copia de la mejora ECO
  enemigos/             # un archivo por enemigo + base.py
  jefes/                # un archivo por jefe + base.py
  powerups/             # tipos.py (todos los power-ups) + base.py
  escenas/              # una clase por pantalla: inicio, dificultad, logros, listo, juego, taller,
                        # gasolinera, pausa, opciones, explosion, iniciales, fin
  entrada.py            # teclado + mando -> acciones (aceptar, dash, pausa...)
  haptica.py            # la vibracion del mando: patrones (en config.VIBRACIONES) y prioridades
  sonido.py  ventana.py  guardado.py  recursos.py
  dibujo.py  efectos.py  fondo.py  hud.py
  accesibilidad.py      # temblor, destellos y CRT: todos los efectos le preguntan a este modulo
tests/                  # pytest
herramientas/componer.py          # el estudio: compone toda la musica y los efectos (y efectos/fichas.json)
```

### Las ideas de diseño (y por qué)

- **Una responsabilidad por módulo.** Si querés cambiar cómo se ve el marcador, vas a `hud.py`; si querés cambiar el mando, a `entrada.py`. No hay que buscar en un archivo de 2000 líneas.
- **`config.py` solo tiene valores.** Podés ajustar la dificultad sin miedo a romper la lógica.
- **Escenas (patrón *State*).** Cada pantalla es una clase con `actualizar()` y `dibujar()`. La `App` llama a esos dos métodos sobre la escena actual. Para cambiar de pantalla: `self.app.cambiar_escena(OtraEscena(...))`.
- **Registros (patrón *Registry*).** Los enemigos, jefes, power-ups, anomalías, desafíos, mejoras y formaciones se anotan solos con un decorador (`@registrar_enemigo`, `@formacion`…). El resto del juego los crea por nombre, así que **agregar uno nuevo no obliga a tocar el resto del código**.
- **El nivel es un guion, no un sorteo.** Qué enemigos llegan, cuántos y por dónde está escrito a mano en `guiones.py` (solo datos), tramo por tramo. Antes la dificultad crecía sumando enemigos al azar que no se iban nunca y la pantalla se "ensuciaba"; ahora cada tramo tiene su idea y los grupos entran, atacan y se van. Un futuro modo historia es otro guion con la misma forma (`GUIONES["historia"]`).
- **Clases base (patrón *Template Method*).** `Enemigo`, `Jefe` y `PowerUp` resuelven todo lo común: aparecer con aviso, congelarse con el hielo, el sprite de respaldo, el HUD… Cada tipo escribe solo lo que lo hace distinto.
- **`Partida` en vez de variables globales.** Todo el estado de una partida vive en un objeto. Empezar otra partida es crear una nueva, así no queda nada "sucio" de la anterior.
- **Entrada por acciones.** El juego pregunta "¿se apretó DASH?", no "¿se apretó la barra espaciadora?". Así teclado y mando funcionan igual.
- **Paso fijo + interpolación.** La lógica (`actualizar`) corre siempre 60 veces por segundo y el dibujo (`dibujar`) a la frecuencia elegida. Regla de oro: en `actualizar` se cambia el estado, en `dibujar` solo se dibuja.
- **Estable.** El juego no se cae si falta un sprite (usa uno dibujado), si no hay placa de sonido, o si `records.json` / `config.json` / `progreso.json` están dañados o no se pueden escribir.

## Cómo agregar cosas nuevas

### Un enemigo
1. Creá `juego/enemigos/mi_enemigo.py`:
   ```python
   from juego.config import VERDE
   from juego.enemigos.base import Enemigo, registrar_enemigo

   @registrar_enemigo
   class Zigzag(Enemigo):
       tipo = "zigzag"
       color = VERDE

       def mover(self, partida):
           # Cambiá self.vx / self.vy: aca va su comportamiento
           dir_x, dir_y, distancia = self.hacia_la_nave(partida)
           ...
   ```
2. Importalo en `juego/enemigos/__init__.py`.
3. Ponelo en la ruta: en `juego/guiones.py`, sumá un escuadrón a algún tramo, por ejemplo `("zigzag", 2, "pinza")` (tipo, cuántos y por dónde entran). Las formaciones están en `juego/escuadrones.py` (`flanco`, `pinza`, `lluvia`, `esquinas`, `cerco`). La regla de los guiones: un enemigo nuevo por tramo como mucho, y nunca en el asedio. La primera vez que llegue, sale solo su ficha de "NUEVO ENEMIGO".
4. (Opcional) `sprites/zigzag.png`: 2 cuadros de 40x40. Si no está, se dibuja uno de respaldo con su color.

Si necesita algo al aparecer, usá `al_aparecer()`; para dibujarse distinto, `dibujar_cuerpo()`. Mirá `embestidor.py` como ejemplo completo.

Otras opciones (atributos de la clase): `tamano` y `radio` (tamaño y radio de daño), `destruible = True` (el dash lo destruye; ver `divisor.py`), `muere_al_chocar = True`, y `crear()` si un "enemigo" son varios a la vez (ver `enjambre.py`). Con `nombre` y `pista` se presenta solo la primera vez que aparece.

Y métodos que el juego le pregunta (por defecto dicen "no"): `hace_danio()` (el ladrón nunca lastima), `interceptable()` (el embestidor cargando) y `bloquea_dash(x, y)` (el escudo del escudero: un dash que llega desde ahí rebota). Para moverse sin rumbo, `deambular()`.

### Un jefe
1. Creá `juego/jefes/mi_jefe.py` con una clase que herede de `Jefe`, con `@registrar_jefe` y un `tipo`.
2. Escribí `cargar_animaciones()`, `al_terminar_de_entrar()`, `actualizar_fase()` (sus fases y ataques) y `animacion()`.
3. Importalo en `juego/jefes/__init__.py` y ponelo como `"jefe"` de un sector en `SECTORES` (`config.py`).

Entrar (con la presentación de su `nombre` y `apodo`), morir, la vida, el congelado y el destello al recibir un golpe ya los resuelve la clase base. `ojo.py` es el ejemplo simple. Si es más grande que 120x120, dale `ancho`, `alto` y `y_final`.

**El ritmo:** cada jefe tiene un pulso (`ms_pulso`). Usá `cambiar_fase_pulsos("atacar", 3, partida.tiempo)` para que una fase dure 3 pulsos, y en `actualizar_fase()` preguntá `self.nuevo_pulso` (empezó un pulso) y `self.pulso` (cuál). Así los ataques caen a tiempo, como en una canción. Armá cada ataque en tres tiempos: **aviso → ataque → ventana para pegarle**.

**Jefes con partes** (cañones, compuertas, segmentos…): cada pieza es una `Parte` (`jefes/partes.py`) con su caja, su vida y su dibujo, y se guarda en `self.partes`. La base ya resuelve el golpe con el dash, el daño al tocarlas, la flechita de "¡DASH!" y la barra del HUD. Vos decidís cuándo se le puede pegar (`golpeable()`) y qué pasa al golpearla o romperla (`al_golpear_parte()` y `al_romper_parte()`). `fortaleza.py` es el ejemplo completo.

### Un power-up
1. En `juego/powerups/tipos.py`:
   ```python
   @registrar_powerup
   class Lento(PowerUp):
       tipo, letra, color, nombre = "lento", "L", VERDE, "LENTO"
       descripcion = "ENEMIGOS LENTOS"
       paleta = TREBOL
       duracion = 6000          # o HASTA_PERDER_VIDA, o None si es instantáneo
   ```
2. Donde tenga efecto, preguntá `partida.activo("lento")` (por ejemplo, en `Partida.factor_velocidad()`).
3. (Opcional) `peso(partida)`: devolvé más de 1 cuando sea más útil (así cae más seguido en ese momento).

El HUD, la caída y el panel de la pantalla de inicio lo muestran solos.

### Una mejora (carta del Taller)
En `juego/mejoras.py`, una clase que herede de `Mejora`, con `@registrar_mejora`, `tipo`, `nombre` (hasta 12 letras), `descripcion` (líneas de hasta 22), `color`, un `icono` de 7x7 (pixel art con "X") y `maximo`. Si cambia algo una sola vez, escribí `al_elegir()` (como `Corazon`); si no, preguntá `partida.mejora("mi_tipo")` donde tenga efecto (devuelve cuántas veces la elegiste). Con `peso` < 1 sale menos (y la carta dice RARA). Aparece sola en el Taller y en la gasolinera (con su precio calculado).

### Un servicio de la gasolinera
En `juego/tienda.py`, una clase que herede de `Articulo` con `tipo`, `nombre`, `descripcion`, `color` e `icono`, y sus métodos `precio(tienda)`, `al_comprar(tienda)` y, si no siempre tiene sentido, `disponible(partida)`. Anotala en `SERVICIOS` y sumá su `tipo` a `"servicios"` en las dificultades de `config.py` que la vendan.

### Un tramo o una formación
Los tramos de cada sector están en `juego/guiones.py`: cada uno tiene `nombre`, `pista` (los dos entran en el cartel: 16 y 32 letras como mucho), `a_la_vez` (cuántos escuadrones a la vez) y la lista de `escuadrones` `(tipo, cuántos, formación)`. Las reglas para escribirlos están arriba del archivo y `tests/test_progresion.py` las comprueba.

Una formación nueva es una función en `juego/escuadrones.py` con `@formacion("nombre")`: recibe cuántos son y dónde está la nave, y devuelve un par `(desde, hasta)` por enemigo (desde afuera de la pantalla hasta su lugar). Ninguno termina de entrar cerca de la nave: `lugares()` lo corre solo.

### Un logro
En `juego/logros.py`, sumá un `Logro(id, nombre, descripcion, condicion)` a `LOGROS`. La condición recibe la partida y devuelve True cuando se cumplió (usá `partida.estadisticas`). Para que dé una nave, agregala a `NAVES` en `config.py` con el id del logro.

### Una anomalía
En `juego/anomalias.py`, una clase que herede de `Anomalia`, con `@registrar_anomalia`, un `tipo`, `nombre`, `pista` y `color`. Usá los ganchos que necesites: `actualizar()` (lo que hace en cada paso), `dibujar()` (avisos, efectos), `terminar()`, `multiplicador_monedas()` o `factor_combo()`. Si ataca, que **avise antes** (como las columnas de los asteroides). Para que un sector la tenga, ponela como `"anomalia"` en `SECTORES`.

### Un desafío
En `juego/desafios.py`, una clase que herede de `Desafio`, con `@registrar_desafio`, `tipo`, `nombre`, `pista` y `color`. Elegí los avisos que le importan (`al_usar_dash`, `al_recibir_golpe`, `al_agarrar_powerup`, `al_recoger_moneda`, `al_destruir_enemigo`, `al_interceptar`) y llamá a `self.fallar()` (los de aguantar) o a `self.avanzar(progreso)` con una `meta` (los de lograr). Si no se puede en cualquier momento, escribí `disponible()`.

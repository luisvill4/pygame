# Caza Monedas

Juego arcade 2D hecho con Pygame: una nave recoge monedas, esquiva enemigos y pelea contra jefes.

## Cómo jugar

```
pip install -r requirements.txt
python main.py
```

| Acción | Teclado | Mando de Xbox |
|---|---|---|
| Mover | Flechas | Stick izquierdo (cualquier ángulo) o cruceta |
| Dash | Espacio | X |
| Aceptar | Enter | A |
| Pausa | P o Esc | Menú (≡) |
| Opciones (en pausa) | O | Vista (⧉) |
| Volver | Esc | B |
| Silenciar / activar el sonido | M | |
| Pantalla completa / ventana | F11 | |

Al elegir **JUGAR** se elige la dificultad (FÁCIL, NORMAL, DIFÍCIL o PESADILLA); cada una tiene su propia tabla de récords. En FÁCIL y NORMAL el embestidor deja de seguirte con la mira un momento antes de embestir (la línea roja deja de parpadear): ahí es cuando hay que correrse. En DIFÍCIL y PESADILLA te sigue hasta el último instante.

### Subir de nivel: la barra de energía
Abajo a la derecha, debajo de "NIVEL", hay una **barra de energía**. Todo lo que hacés bien la llena y, cuando se llena, subís de nivel (lo que sobra pasa al siguiente):

| Qué | Energía |
|---|---|
| Moneda | 1, y +0.25 por cada paso del combo (con x5, 2 por moneda) |
| Dash perfecto | 1.5 |
| Enemigo destruido (o congelado roto) | 0.5 |
| Oleada superada | 3 |
| Desafío cumplido | 5 |

El nivel 1 pide 10 y cada nivel pide 1 más, hasta 16. Jugar con combo alto y usar el dash te hace avanzar más rápido. Durante la pelea con el jefe (y mientras se ven sus carteles) no se gana energía: la barra se ve gris.

### El dash
El dash es la herramienta principal: te lanza hacia adelante y durante ese instante **nada te hace daño**.

- Algunos enemigos (el divisor, el enjambre, las abejas) y algunos proyectiles (misiles, asteroides) se **destruyen** con el dash, y cada uno adelanta la recarga. Atravesar a los demás enemigos o a las balas solo te salva del golpe: no da nada.
- **Dash perfecto:** romper (o partir) con el dash a un enemigo destruible es un "¡PERFECTO!": unos puntos más, el combo no se corta y **el dash se recarga casi enseguida**. Varios seguidos (antes de 1.5 s) forman una **cadena** que multiplica esos puntos hasta x5.
- **Interceptar:** si le pegás con el dash al **embestidor mientras embiste**, lo frenás en seco: queda aturdido 2 s (no lastima), da 10 puntos y cuenta como dash perfecto ("¡INTERCEPTADO!").
- Contra los jefes, el dash es la única forma de pegarles.

### Mejoras (el Taller)
En el **nivel 3** y **al cerrar cada sector** el juego se detiene y te ofrece **3 cartas**: elegís una y dura toda la partida. Se pueden repetir hasta su nivel máximo. Así cada partida termina con una nave distinta:

| Mejora | Qué hace |
|---|---|
| **DOBLE DASH** *(rara)* | Un dash más seguido antes de recargar (se ve como un cuadradito al lado de "DASH"). Una sola vez y desde el sector 3. |
| **ECO** | Cada dash tiene un 25% (45% en nivel 2) de dejar una copia violeta que lo repite un momento después: destruye, aturde y rompe balas. |
| **RECARGA** | El dash se recarga un 20% más rápido (por nivel). |
| **ONDA** | Al terminar cada dash, una onda rompe balas, destruye a los enemigos destruibles y empuja (y aturde) a los demás. |
| **COMETA** | Dash un 50% más largo. |
| **FILO** *(rara)* | El dash destruye a **todos** los enemigos. Desde el sector 2. |
| **ESCUDO ROCE** | Cada 4 dash perfectos (3 en nivel 2) ganás un escudo. |
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

### Logros y naves
Hay **16 logros** (vencer a tu primer jefe, 10 dash perfectos, rango S, 5000 puntos...). Se guardan entre partidas en `progreso.json` y cuando desbloqueás uno aparece una ficha "¡LOGRO!". Varios logros desbloquean **naves de otro color**: se eligen en **LOGROS** (desde el inicio) con IZQ/DER.

Al perder, el **Game Over** muestra el resumen de la partida: tiempo, sector, monedas, mejor combo, enemigos destruidos, dash perfectos (y la mejor cadena), desafíos, el rango de cada sector y las mejoras que elegiste. ENTER juega otra vez; ESC vuelve al menú. En la **pausa** también se ve cómo va la partida y tus mejoras.

### Carteles
Los carteles ("NIVEL 3", "¡JEFE VENCIDO!", el rango...) y las fichas (enemigo nuevo, desafío) se vuelven casi transparentes cuando tienen algo abajo (la nave, la moneda, un enemigo, una bala), así nunca te tapan el juego. Cada tanto llega una **oleada**: muchos enemigos durante unos segundos; si la pasás sin perder una vida, ganás puntos y un power-up. Los enemigos de cada nivel se eligen al azar según un "presupuesto", así que cada partida es distinta.

### Sectores y jefes
El viaje pasa por 5 **sectores**, cada uno con su ambiente (asteroides, brasas, luciérnagas, un panal gigante, polvo que cae en un agujero negro), sus enemigos favoritos y **su jefe**, que llega cada 5 niveles. Al vencerlo se pasa al sector siguiente; después del último se vuelve a empezar, más difícil.

Las peleas son un **baile**: cada jefe avisa antes de atacar, ataca al ritmo de su "pulso" y después deja un hueco para pegarle con el dash.

| Sector | Jefe | Cómo se le gana |
|---|---|---|
| Cinturón exterior | **El Ojo** | Esquivá sus abanicos y anillos; cuando queda cansado, dash al núcleo. |
| Nebulosa carmesí | **La Fortaleza** | Sus 4 cañones atacan de a uno (ráfaga, misiles, láser y minas) y quedan recalentados: dash al que brilla. Sin cañones se le cae la coraza y cae sobre vos: salí de la columna roja y pegale cuando queda aturdida en el piso. |
| Campo esmeralda | **La Serpiente** | Te rodea y muerde en línea recta (marca la línea antes). Si se estrella contra un borde, queda mareada y su cascabel brilla: dash a la cola. Después también se enrosca: salí del círculo. |
| Mar de ámbar | **La Colmena** | Abre una compuerta, suelta abejas y la deja abierta: rompela con el dash. Sin compuertas embiste rebotando (el aviso muestra el camino): cuando queda aturdida, dash al ojo. |
| Abismo azul | **La Singularidad** | Te atrae (el dash te libera). El anillo de asteroides gira a ritmo; cuando colapsa, entrá por un hueco y dash al núcleo. |

### Anomalías, desafíos y rango
- **Anomalías:** a mitad de cada sector (en su 3er nivel) el espacio se pone raro durante 20 segundos. Siempre avisan antes de atacar:

  | Sector | Anomalía | Qué pasa |
  |---|---|---|
  | Cinturón exterior | **Lluvia de asteroides** | Una columna roja punteada marca por dónde cae cada asteroide. El dash los rompe y dan puntos. |
  | Nebulosa carmesí | **Tormenta solar** | Una franja (vertical u horizontal) parpadea y después quema: salí antes. |
  | Campo esmeralda | **Niebla cerrada** | Solo ves cerca de la nave; de los enemigos lejanos ves los ojos, y la moneda brilla a través de la niebla. |
  | Mar de ámbar | **Fiebre del oro** | La buena: las monedas valen el doble y el combo tarda más en cortarse. |
  | Abismo azul | Una al azar | Desde la segunda vuelta, todos los sectores la sortean. |

- **Desafíos (opcionales):** al llegar a cada sector (en el primero, en el nivel 2) aparece un reto a la derecha, debajo de las vidas: **SIN DASH**, **INTOCABLE** (sin recibir golpes), **SIN AYUDA** (sin agarrar power-ups), **SIN CORTAR EL COMBO** (12 monedas seguidas), **CAZADOR** (destruir 6 enemigos con el dash) o **INTERCEPTOR** (frenar 3 embestidas con el dash). Los tres primeros se cumplen al llegar al jefe; los otros, apenas los lográs. Premio: puntos y un power-up.
- **Rango:** al vencer al jefe, el sector se califica de **S** a **C** con estrellas: sin golpes (2), combo de 12 (1), desafío cumplido (1) y jefe vencido rápido (1). S = 5 estrellas, A = 4, B = 2 o 3. Cada letra da puntos extra.

En **Opciones → FORMATO** se elige entre 4:3 (800x600) y 16:9 (1066x600, un campo de juego más ancho). Se cambia desde el menú de inicio, no en medio de una partida.

En **Opciones → FPS** se elige cuántas veces por segundo se dibuja: 30, 60, 90, 120, 144 o SIN LIMITE. El juego va siempre a la misma velocidad: la lógica avanza 60 veces por segundo y, por encima de 60 FPS, el movimiento se dibuja interpolado (más suave en monitores de alta frecuencia).

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
  progresion.py         # el "director": enemigos de cada nivel, sectores, oleadas, mejoras
  anomalias.py  desafios.py  rango.py   # lo que pasa en cada sector
  mejoras.py            # las cartas del Taller
  estadisticas.py       # lo que pasa en la partida (para el Game Over y los logros)
  logros.py             # los logros (y que nave desbloquea cada uno)
  eco.py                # la copia de la mejora ECO
  enemigos/             # un archivo por enemigo + base.py
  jefes/                # un archivo por jefe + base.py
  powerups/             # tipos.py (todos los power-ups) + base.py
  escenas/              # una clase por pantalla: inicio, dificultad, logros, listo, juego, taller, pausa,
                        # opciones, explosion, iniciales, fin
  entrada.py            # teclado + mando -> acciones (aceptar, dash, pausa...)
  sonido.py  ventana.py  guardado.py  recursos.py
  dibujo.py  efectos.py  fondo.py  hud.py
tests/                  # pytest
```

### Las ideas de diseño (y por qué)

- **Una responsabilidad por módulo.** Si querés cambiar cómo se ve el marcador, vas a `hud.py`; si querés cambiar el mando, a `entrada.py`. No hay que buscar en un archivo de 2000 líneas.
- **`config.py` solo tiene valores.** Podés ajustar la dificultad sin miedo a romper la lógica.
- **Escenas (patrón *State*).** Cada pantalla es una clase con `actualizar()` y `dibujar()`. La `App` llama a esos dos métodos sobre la escena actual. Para cambiar de pantalla: `self.app.cambiar_escena(OtraEscena(...))`.
- **Registros (patrón *Registry*).** Los enemigos, jefes, power-ups, anomalías, desafíos y mejoras se anotan solos con un decorador (`@registrar_enemigo`…). El resto del juego los crea por nombre, así que **agregar uno nuevo no obliga a tocar el resto del código**.
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
3. Dale un costo en `COSTO_ENEMIGO` y un nivel de aparición en `DESBLOQUEO_ENEMIGO` (`config.py`). El director lo va a sumar solo, según el presupuesto de cada nivel; podés hacerlo el `favorito` de algún sector en `SECTORES`.
4. (Opcional) `sprites/zigzag.png`: 2 cuadros de 40x40. Si no está, se dibuja uno de respaldo con su color.

Si necesita algo al aparecer, usá `al_aparecer()`; para dibujarse distinto, `dibujar_cuerpo()`. Mirá `embestidor.py` como ejemplo completo.

Otras opciones (atributos de la clase): `tamano` y `radio` (tamaño y radio de daño), `destruible = True` (el dash lo destruye; ver `divisor.py`), `muere_al_chocar = True`, y `crear()` si un "enemigo" son varios a la vez (ver `enjambre.py`). Con `nombre` y `pista` se presenta solo la primera vez que aparece.

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
En `juego/mejoras.py`, una clase que herede de `Mejora`, con `@registrar_mejora`, `tipo`, `nombre` (hasta 12 letras), `descripcion` (líneas de hasta 22), `color`, un `icono` de 7x7 (pixel art con "X") y `maximo`. Si cambia algo una sola vez, escribí `al_elegir()` (como `Corazon`); si no, preguntá `partida.mejora("mi_tipo")` donde tenga efecto (devuelve cuántas veces la elegiste). Con `peso` < 1 sale menos (y la carta dice RARA).

### Un logro
En `juego/logros.py`, sumá un `Logro(id, nombre, descripcion, condicion)` a `LOGROS`. La condición recibe la partida y devuelve True cuando se cumplió (usá `partida.estadisticas`). Para que dé una nave, agregala a `NAVES` en `config.py` con el id del logro.

### Una anomalía
En `juego/anomalias.py`, una clase que herede de `Anomalia`, con `@registrar_anomalia`, un `tipo`, `nombre`, `pista` y `color`. Usá los ganchos que necesites: `actualizar()` (lo que hace en cada paso), `dibujar()` (avisos, efectos), `terminar()`, `multiplicador_monedas()` o `factor_combo()`. Si ataca, que **avise antes** (como las columnas de los asteroides). Para que un sector la tenga, ponela como `"anomalia"` en `SECTORES`.

### Un desafío
En `juego/desafios.py`, una clase que herede de `Desafio`, con `@registrar_desafio`, `tipo`, `nombre`, `pista` y `color`. Elegí los avisos que le importan (`al_usar_dash`, `al_recibir_golpe`, `al_agarrar_powerup`, `al_recoger_moneda`, `al_destruir_enemigo`, `al_interceptar`) y llamá a `self.fallar()` (los de aguantar) o a `self.avanzar(progreso)` con una `meta` (los de lograr). Si no se puede en cualquier momento, escribí `disponible()`.

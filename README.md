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

Al elegir **JUGAR** se elige la dificultad (FÁCIL, NORMAL, DIFÍCIL o PESADILLA); cada una tiene su propia tabla de récords. En FÁCIL y NORMAL el embestidor deja de seguirte con la mira un momento antes de embestir (la línea roja deja de parpadear): ahí es cuando hay que correrse. En DIFÍCIL y PESADILLA te sigue hasta el último instante.

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

- **Desafíos (opcionales):** al llegar a cada sector (en el primero, en el nivel 2) aparece un reto a la derecha, debajo de las vidas: **SIN DASH**, **INTOCABLE** (sin recibir golpes), **SIN AYUDA** (sin agarrar power-ups), **SIN CORTAR EL COMBO** (12 monedas seguidas) o **CAZADOR** (destruir 6 enemigos con el dash). Los tres primeros se cumplen al llegar al jefe; los otros dos, apenas los lográs. Premio: puntos y un power-up.
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
  progresion.py         # el "director": enemigos de cada nivel, sectores, oleadas
  anomalias.py  desafios.py  rango.py   # lo que pasa en cada sector
  enemigos/             # un archivo por enemigo + base.py
  jefes/                # un archivo por jefe + base.py
  powerups/             # tipos.py (todos los power-ups) + base.py
  escenas/              # una clase por pantalla: inicio, listo, juego, pausa, opciones, explosion, iniciales, fin
  entrada.py            # teclado + mando -> acciones (aceptar, dash, pausa...)
  sonido.py  ventana.py  guardado.py  recursos.py
  dibujo.py  efectos.py  fondo.py  hud.py
tests/                  # pytest
```

### Las ideas de diseño (y por qué)

- **Una responsabilidad por módulo.** Si querés cambiar cómo se ve el marcador, vas a `hud.py`; si querés cambiar el mando, a `entrada.py`. No hay que buscar en un archivo de 2000 líneas.
- **`config.py` solo tiene valores.** Podés ajustar la dificultad sin miedo a romper la lógica.
- **Escenas (patrón *State*).** Cada pantalla es una clase con `actualizar()` y `dibujar()`. La `App` llama a esos dos métodos sobre la escena actual. Para cambiar de pantalla: `self.app.cambiar_escena(OtraEscena(...))`.
- **Registros (patrón *Registry*).** Los enemigos, jefes, power-ups, anomalías y desafíos se anotan solos con un decorador (`@registrar_enemigo`…). El resto del juego los crea por nombre, así que **agregar uno nuevo no obliga a tocar el resto del código**.
- **Clases base (patrón *Template Method*).** `Enemigo`, `Jefe` y `PowerUp` resuelven todo lo común: aparecer con aviso, congelarse con el hielo, el sprite de respaldo, el HUD… Cada tipo escribe solo lo que lo hace distinto.
- **`Partida` en vez de variables globales.** Todo el estado de una partida vive en un objeto. Empezar otra partida es crear una nueva, así no queda nada "sucio" de la anterior.
- **Entrada por acciones.** El juego pregunta "¿se apretó DASH?", no "¿se apretó la barra espaciadora?". Así teclado y mando funcionan igual.
- **Paso fijo + interpolación.** La lógica (`actualizar`) corre siempre 60 veces por segundo y el dibujo (`dibujar`) a la frecuencia elegida. Regla de oro: en `actualizar` se cambia el estado, en `dibujar` solo se dibuja.
- **Estable.** El juego no se cae si falta un sprite (usa uno dibujado), si no hay placa de sonido, o si `records.json` / `config.json` están dañados o no se pueden escribir.

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

El HUD, la caída al azar y el panel de la pantalla de inicio lo muestran solos.

### Una anomalía
En `juego/anomalias.py`, una clase que herede de `Anomalia`, con `@registrar_anomalia`, un `tipo`, `nombre`, `pista` y `color`. Usá los ganchos que necesites: `actualizar()` (lo que hace en cada paso), `dibujar()` (avisos, efectos), `terminar()`, `multiplicador_monedas()` o `factor_combo()`. Si ataca, que **avise antes** (como las columnas de los asteroides). Para que un sector la tenga, ponela como `"anomalia"` en `SECTORES`.

### Un desafío
En `juego/desafios.py`, una clase que herede de `Desafio`, con `@registrar_desafio`, `tipo`, `nombre`, `pista` y `color`. Elegí los avisos que le importan (`al_usar_dash`, `al_recibir_golpe`, `al_agarrar_powerup`, `al_recoger_moneda`, `al_destruir_enemigo`) y llamá a `self.fallar()` (los de aguantar) o a `self.avanzar(progreso)` con una `meta` (los de lograr). Si no se puede en cualquier momento, escribí `disponible()`.

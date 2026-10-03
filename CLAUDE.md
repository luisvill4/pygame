# Caza Monedas (Pygame)

Juego arcade 2D hecho con Pygame. El jugador controla una nave que recoge monedas, esquiva enemigos y pelea contra jefes. El código está en el paquete `juego/`; `main.py` solo lo arranca. README.md tiene la guía para el usuario y explica cómo agregar enemigos, jefes y power-ups.

## Cómo ejecutar y probar
```
python main.py
python -m pytest        # ~90 tests, unos 7 s, sin ventana
```
- Requisitos: Python 3.12, pygame 2.6.1 y pytest (están en `requirements.txt`). Se necesita pygame ≥ 2.1.4 por `pygame.transform.grayscale`.
- **Git:** `main` tiene la versión de un solo archivo de antes del refactor (commit `9805b13`). El refactor modular se hizo en la rama `refactor-modular`. `.gitignore` deja afuera `records.json`, `config.json` y `__pycache__`.
- **Correr `python -m pytest` después de cada cambio.** Si se agrega una regla de juego, sumarle su test.

## Estructura
```
main.py                 # App().ejecutar()
juego/
  config.py             # SOLO valores: colores, paletas, "Reglas del juego", DURACION, mando
  lienzo.py             # formato actual (4:3 / 16:9) y ancho del lienzo: lienzo.ancho
  app.py                # App: servicios, escenas y bucle de paso fijo (paso(), cuadro(ms), ejecutar())
  interpolacion.py      # Interpolador: dibujar en posiciones intermedias entre pasos de logica
  reloj.py              # LimitadorFPS: limite de FPS preciso (sleep + espera activa final)
  partida.py            # Partida: todo el estado de una partida y sus reglas
  nave.py  moneda.py  proyectiles.py (Bala)
  enemigos/  base.py (Enemigo + registro) · perseguidor.py · rebotador.py · embestidor.py
  jefes/     base.py (Jefe + registro) · ojo.py (JefeOjo)
  powerups/  base.py (PowerUp, Capsula, registro) · tipos.py (los 7 power-ups, en orden)
  escenas/   base.py · inicio · opciones · listo · juego · pausa · explosion · iniciales · fin
  entrada.py  sonido.py  ventana.py  guardado.py  recursos.py
  dibujo.py   efectos.py  fondo.py   hud.py
tests/                  # conftest.py (fixtures app/partida), ayudas.py, test_*.py
sprites/ efectos/ fuentes/   # recursos (ver "Sprites"); efectos/ son los sonidos
records.json            # top 5 {"nombre", "puntos"}; se crea vacío si no existe
config.json             # {"formato", "resolucion", "fps", "volumen" (0-10), "musica", "efectos", "aviso_jefe"}
```

**Frecuencia: paso fijo (fixed timestep) + interpolación.**
- **La lógica avanza siempre en pasos de 1/60 s** (`PASOS_POR_SEGUNDO`, `MS_POR_FRAME`). Todo lo que en `config.py` dice "por frame" es por paso.
- **Se dibuja a `opciones.fps`** (`FRECUENCIAS` = 30, 60, 90, 120, 144 y 0 = SIN LIMITE). El juego va a la misma velocidad a cualquier FPS, y hay un test que lo comprueba.
- `App.ejecutar()`: `LimitadorFPS.esperar(fps)` → `cuadro(ms)`. Este suma `ms` a `acumulado` (como mucho `ATRASO_MAXIMO`), corre los pasos que tocan, calcula `fraccion = acumulado / MS_POR_FRAME` y dibuja. `paso()` hace exactamente un paso y un cuadro (lo usan los tests).
- **Reglas para no romperlo:**
  - En `actualizar()` va **todo** lo que cambia el estado, incluido `mover_fondo()` y el descuento del temblor y el destello (que va en `Efectos.actualizar`).
  - `dibujar()` solo dibuja, porque puede correr varias veces o ninguna por paso.
  - La entrada se acumula (`procesar`) hasta que un paso la usa (`consumir`); así no se pierden teclas.
  - Lo que se mueve tiene `x`/`y` y está en `Partida.objetos_que_se_mueven()` (o en el `Fondo`). Así se dibuja interpolado con `Interpolador`, que no interpola saltos de más de 80 px (reapariciones).
Las rutas pasan por `config.ruta()`, relativas a la carpeta raíz.

**Formato (4:3 / 16:9):** el juego se dibuja a 60 FPS en un lienzo de `ALTO = 600` y un ancho que depende del formato (`FORMATOS`: 800 o 1066).
- **Nunca escribir 800 a mano.** En el juego se usa `lienzo.ancho` y `lienzo.centro_x()`, que se leen en vivo con `from juego import lienzo`; no importar el valor.
  - Lo de la izquierda se ancla a x=20, lo de la derecha a `lienzo.ancho - 20` y lo central a `centro_x()`.
- **Los menús** (Inicio, Opciones, Pausa, Iniciales, Fin) dibujan el fondo y el CRT en todo el lienzo, y su contenido en `dibujo.zona_central(pantalla)`: una subsuperficie de 800x600 (`ANCHO_MENU`) centrada, así sus coordenadas no cambian entre formatos.
  - `texto_3d`, `oscurecer` y `efecto_crt` usan el tamaño de la superficie que reciben.
- **Cambiar el formato:** `App.aplicar_formato()` llama a `lienzo.cambiar()`, crea `app.pantalla` y un `Fondo` nuevos (estrellas y objetos escalados al ancho) y abre la ventana con una resolución de ese formato (`RESOLUCIONES[formato]`). Si la resolución guardada no existe en el formato, usa la primera; "COMPLETA" existe en los dos.
  - El formato solo se cambia desde Inicio; desde la Pausa (`Opciones(..., en_partida=True)`) la fila aparece en gris.

## El usuario y el estilo del código
- **Todo en español**: la conversación, los nombres de variables, funciones y clases, y los comentarios. El usuario escribe en español informal.
- **El usuario está aprendiendo.** Pidió explícitamente una arquitectura modular y escalable, y eligió el nivel "modular con clases": clases base, registros y escenas, **sin** type hints ni dataclasses ni bus de eventos. Mantener ese nivel. El código tiene que poder leerlo alguien que aprende: nombres claros, métodos cortos y comentarios que explican el "por qué" y los patrones (State, Registry, Template Method).
- Cualquier número que el usuario pueda querer tocar va en `config.py`, en la sección "Reglas del juego" (o en `DURACION`).
- Dependencias sin ciclos: `config` ← `recursos`/`dibujo` ← entidades ← `partida` ← escenas ← `app`. Las entidades reciben `partida` como parámetro (no la importan).

## Estilo visual: arcade retro (el usuario lo aprecia mucho, no romperlo)
- Fuente Press Start 2P, siempre con `antialias=False`, en tamaños múltiplos de 8: `dibujo.CHICA/MEDIA/GRANDE/TITULO` = 16/24/40/56.
  - `dibujo.texto(pantalla, mensaje, tamaño, color, x, y, sombra, alinear)` recibe el tamaño como número; `recursos.fuente(tamaño)` guarda las fuentes en caché.
- Colores neón definidos como constantes en `config.py` (`AMARILLO`, `CIAN`, `MAGENTA`, `ROJO`…). Números con 6 dígitos (`dibujo.numero_arcade`).
- Partículas (`efectos.Efectos`): cuadrados alineados a una cuadrícula de 2 px. No se desvanecen con transparencia: cambian de color por etapas según una **paleta**, una lista que va de oscuro a brillante (`FUEGO`, `ORO`, `ESCARCHA`…).
- Efectos disponibles:
  - en `dibujo`: líneas CRT (`efecto_crt`), parpadeos duros (`parpadeo`), texto con relieve (`texto_3d`), marcos de doble línea (`marco`), arcoíris (`color_arcoiris`) y `oscurecer`;
  - en `Efectos`: temblor en pasos de 2 px y destello de color (`sacudir`, `dibujar_temblor_y_destello`; se descuentan en `actualizar`).
- Variantes de sprites sin archivos nuevos: `recursos.tenir()` (escala de grises + multiplicar color) y `recursos.blanquear()` (`BLEND_RGB_MAX`).

## Sprites
El usuario dibuja los sprites; Claude los integra. Todos están en `sprites/`.

**Reglas para sprites nuevos:**
- PNG con fondo transparente, pixel art sin antialiasing y tamaño exacto.
- Colores neón del juego: `#FFDD00`, `#FF3246`, `#00E6FF`, `#FF00AA`, `#3CFF78`, `#8CBEFF`, `#FFFFFF`, más tonos oscuros de esos mismos.
- Las animaciones son una "hoja" horizontal: cuadros del mismo tamaño, uno al lado del otro y sin separación.
- Lo que gira con la nave se dibuja mirando hacia arriba.

**Cómo se cargan** (`recursos.py`, siempre con caché):
- `sprite(archivo)` devuelve `None` si no existe y quien lo pidió usa su dibujo de respaldo; `sprite_obligatorio()` es solo para `nave.png`.
- `hoja(archivo, ancho_cuadro)` devuelve la lista de cuadros (o `None`).
- `cuadro_animado(cuadros, ms_por_cuadro, desfase)` elige el cuadro según el reloj real.
- Las velocidades de las animaciones están en `config.py`: `MS_CUADRO_ENEMIGO`, `MS_CUADRO_MONEDA`, `MS_CUADRO_ESCUDO` y `MS_CUADRO_JEFE`.

### Sprites que ya existen
| Archivo | Tamaño | Cuadros | Dónde se usa | Respaldo si falta |
|---|---|---|---|---|
| `nave.png` | 50x50 | 1 | `nave.imagen("nave")` (mira hacia arriba); también `"icono"`/`"icono_vacio"` (vidas del HUD, 25x25) y `"fantasma"` (dash) | obligatorio |
| `perseguidor.png`, `rebotador.png`, `embestidor.png` | 80x40 | 2 de 40x40 | `Enemigo.cuadros()` (por `tipo + ".png"`); el perseguidor también es el ícono "ESQUIVA" en Inicio | `enemigo_respaldo(color)`: cuadrado con dos ojos |
| `embestidor_carga.png` | 40x40 | 1 | `Embestidor.dibujar_cuerpo()` en la fase "apuntar" | parpadeo con el primer cuadro en blanco |
| `moneda_giro.png` | 120x20 | 6 de 20x20 | `moneda.imagen_moneda()` (en el juego y en Inicio) | elipse amarilla que se angosta |
| `powerups.png` | 150x30 | 5 de 30x30 | `PowerUp.dibujar_capsula()` según `cuadro_sprite` (escudo 0, hielo 1, vida 2, imán 3, doble 4). Turbo y recarga no tienen | cuadro con la letra |
| `escudo.png` | 152x76 | 2 de 76x76 | burbuja en `Nave.dibujar()`. Tiene píxeles semitransparentes (el brillo); está bien así | círculo cian |
| `nebulosa.png`, `planeta_chico.png`, `planeta_grande.png` | 256x192 / 32x32 / 96x96 | 1 | `Fondo` (paralaje) | no se dibujan |
| `jefe.png` | 720x120 | 6 de 120x120, de a pares: flotar, atacar, cansado | `JefeOjo.cargar_animaciones()`; `Jefe.animaciones()` arma las variantes congelada y blanca. Con 2 cuadros se usan para todo | `jefe_respaldo(color_nucleo)` |

La llama del motor son partículas (`Efectos.estela()`), y el usuario prefiere que siga así: no proponer un sprite de propulsor. Los enemigos congelados se generan con `tenir(..., HIELO)`. No hay sprites pendientes y el usuario solo quiso dibujar el jefe: no proponer sprites nuevos.

- **Trampa:** en Press Start 2P la "É" mayúscula se dibuja como "é" pequeña. Por eso se escribe "RECORD" sin tilde. "¡" y los números funcionan bien.
- **Trampa:** en este Windows `SysFont("Arial")` carga **Arial Narrow**.

## Arquitectura

### App y escenas (patrón State)
- `App` crea una sola vez los servicios: `ventana`, `opciones`, `sonidos`, `records`, `entrada`, `fondo`, `efectos`, más `pantalla` (el lienzo de 800x600).
- Un paso de lógica es `escena.actualizar(entrada)` + `entrada.consumir()`. Un cuadro es `escena.dibujar(pantalla)` + `ventana.mostrar(pantalla)`. `cuadro(ms)` corre los pasos que tocan y un cuadro; `ejecutar()` lo repite con `LimitadorFPS` (ver "Frecuencia").
- `App.ahora()` es el reloj real; los tests lo reemplazan. `App(carpeta_datos=..., usar_mandos=...)` también se usa en los tests.
- Cada escena hereda de `escenas/base.Escena`:
  - `actualizar` cambia el estado o pasa a otra escena con `self.app.cambiar_escena(...)`; `dibujar` solo dibuja.
  - `al_cerrar()` se llama si se cierra la ventana; Iniciales guarda el récord ahí.
  - `tiempo_en_escena()` cuenta con el reloj real y sirve para READY (1.6 s), la explosión (1.5 s) y el Game Over (ENTER se ignora 0.8 s).
  - `dibujar_partida(pantalla, partida, con_nave, paralaje)` dibuja el fondo y la partida.
- Flujo: `Inicio → Listo → Juego ⇄ Pausa ⇄ Opciones`, y `Juego → Explosion → Iniciales (si entra al top 5) → Fin → Listo`. `App.nueva_partida()` reinicia los efectos, crea una `Partida`, suena "seleccion", arranca la música y pasa a `Listo`.
- Hay escenas que guardan otras escenas: `Opciones(volver_a=escena)` y `Pausa(escena_juego, captura)`, así al volver se retoma la misma instancia.
- **Hit-stop:** mientras `partida.congelar_frames > 0`, Juego y Explosion no actualizan ni dibujan (`saltar_dibujo`). `Juego.actualizar` revisa primero `partida.termino`, después el hit-stop y después la pausa.

### Partida (`partida.py`)
- Contiene todo el estado de una partida: `nave`, `vidas`, `puntaje`, `combo`, `nivel`, `moneda`, `capsula`, `activos` (tipo → ms en que termina; `math.inf` para los que duran hasta perder una vida), `enemigos`, `enemigos_guardados`, `jefe` (`None` si no hay pelea), `balas`, `tiempo`, `congelar_frames`, `pausa_pendiente` y `termino`.
- Los servicios le llegan por parámetro (`efectos`, `sonidos`, `entrada` para vibrar, `records` y `opciones`, que se leen en vivo).
- **Dos relojes, no mezclarlos:**
  - `partida.tiempo` avanza `MS_POR_FRAME` solo en `actualizar()` y lo usan todos los temporizadores de juego.
  - `pygame.time.get_ticks()` es el reloj real: solo para parpadeos y animaciones.
- Reglas (siempre pasar por ellas):
  - `danar_jugador(x, y)`: si hay escudo, lo rompe y da 0.5 s de invulnerabilidad. Si no, quita una vida, corta el combo y saca los power-ups que duran hasta perder una vida (con textos "-TURBO"…). Con 0 vidas, marca `termino`.
  - `sumar_puntos(base)`: aplica DOBLE y detecta cuándo se supera el récord.
  - `subir_nivel()`, `iniciar_jefe()` y `jefe_vencido()`.
- Consultas: `activo(tipo)`, `restante(tipo)`, `activar(tipo, duracion)`, `desactivar(tipo)`, `vel_max()` (turbo), `recarga_dash()` (recarga), `factor_velocidad()` y `multiplicador_combo() = min(1 + combo // 3, COMBO_MAXIMO)`.
- Orden de `actualizar(dx, dy, pidio_dash)`: tiempo → nave → corte del combo → imán → moneda → power-ups → devolver enemigos guardados → enemigos (mover y choques) → jefe (balas, fases y choques) → estela → brillo de la moneda → efectos.

### Entrada (`entrada.py`)
- Teclado y mando se convierten en **acciones**: `ACEPTAR`, `VOLVER`, `PAUSA`, `OPCIONES`, `DASH`, `ARRIBA`, `ABAJO`, `IZQUIERDA` y `DERECHA`.
  - Las acciones de un toque quedan en `entrada.acciones` (en orden) y se consultan con `pulso(accion)`.
  - El movimiento sale de `direccion()`: primero las flechas; si no hay, el mando (cruceta en 8 direcciones, o stick en **cualquier ángulo** con zona muerta circular `ZONA_MUERTA_NAVE`).
- `TECLAS`: ESC dispara `VOLVER` y `PAUSA`. `BOTONES`: A = aceptar, X = dash, B = volver (solo eso, así B no pausa el juego), Menú = pausa y Vista = opciones.
- El stick cuenta como un toque solo cuando recién se inclina más allá de `ZONA_MUERTA` (`stick_antes`).
- Banderas del frame: `cerrar`, `foco_perdido` y `mando_desconectado` (solo si el mando estaba en `mandos`). Listo y Juego las convierten en `partida.pausa_pendiente`: es la pausa automática.
- `hay_mando()` y `ayuda(texto_teclado, texto_mando)` eligen los textos de ayuda. `vibrar(suave, fuerte, ms)` se usa al romperse el escudo, al perder una vida, al morir, al golpear al jefe y cuando el jefe explota.
- El mando del usuario (Xbox Series X en Windows) da este mapeo de SDL: A=b0, B=b1, X=b2, Vista=b6, Menú=b7, cruceta=hat 0, stick=ejes 0/1.

### Entidades
- **Nave** (`nave.py`): física con inercia (`NAVE_*`), diagonal normalizada y giro suavizado (0 = arriba, 90 = izquierda, `atan2(-dx, -dy)`). Además:
  - Inclinación al girar; flota 2 px cuando está casi quieta.
  - **Dash con buffer:** `dash_pedido_en` + `BUFFER_DASH`, y un destello cian una sola vez cuando se recarga (`dash_avisado`).
  - Choques: `caja_recoger()` (50x50, para recoger cosas), `toca_circulo()` y `toca_rect()` (daño con `RADIO_NAVE = 11`), `atraviesa(t)` (dash o invulnerable) y `empujon()`.
- **Moneda** (`moneda.py`): `lugar_para_moneda(partida)` busca un lugar con `hud.posicion_libre()` a entre `MONEDA_DISTANCIA_MIN` y `MONEDA_DISTANCIA_MAX` de la nave, a más de 60 px de cada enemigo y lejos del jefe (hasta 200 intentos).
- **Zonas del HUD** (`hud.zonas_hud()`, una función porque dependen del ancho): la franja de arriba (y < 100), la de abajo (y ≥ 530) y la columna de power-ups activos. Si el HUD cambia, hay que actualizarlas.
- **Enemigos** (`enemigos/`), registro `TIPOS_ENEMIGO` con `@registrar_enemigo` y `crear_enemigo(tipo, partida)`:
  - La base resuelve:
    - la aparición lejos de la nave (`DISTANCIA_APARICION`), con una "X" de aviso durante `AVISO_APARICION` en la que no hace daño;
    - el congelado (sprite azul y "+5"; tocarlo con la caja grande da puntos);
    - los bordes (`rebota_en_bordes`), la animación con `desfase` y `separarse()`.
  - Las subclases escriben `mover()`, y si hace falta `al_aparecer()`, `paso()` y `dibujar_cuerpo()`.
  - `perseguidor`: inercia y se separa de los demás.
  - `rebotador`: diagonal y rebota; se acelera con `factor_velocidad()`.
  - `embestidor`: `acercarse → apuntar (0.6 s, línea roja) → cargar (0.5 s)`. Solo te sigue y embiste dentro de `RANGO_EMBESTIDOR`; si no, deambula con `rumbo`.
  - **Separación:** los que persiguen se alejan entre sí a menos de `SEPARACION_ENEMIGOS`, con fuerza `FUERZA_SEPARACION`. Sin esto, se fusionaban a los ~10 s.
  - Progresión: `ENEMIGOS_INICIALES`, `ENEMIGOS_POR_NIVEL` y, después de cada jefe, uno de `ENEMIGOS_POR_JEFE` hasta `ENEMIGOS_MAX`.
- **Jefes** (`jefes/`), registro `TIPOS_JEFE`; el que sale lo decide `ORDEN_JEFES[jefes_vencidos % len]`:
  - La base resuelve las fases `entrar` (baja hasta y=70 con "¡CUIDADO!") y `morir` (2 s, después llama a `partida.jefe_vencido()`). También: la vida (`JEFE_VIDA + jefes_vencidos`), el congelado (no aplica en entrar ni en morir; corre `fase_hasta`), `recibir_golpe()`, `explotar()`, las variantes de sprite, "¡DASH!" cuando `puede_recibir_golpe()` y las cajas `caja_cuerpo()` y `caja_nucleo()`.
  - `JefeOjo` (`ojo.py`): `flotar` (`JEFE_FLOTAR`) → `atacar` (carga 0.7 s y `JEFE_RAFAGAS` ráfagas, turnando abanico y anillo) → `cansado` (`JEFE_CANSADO`) → `flotar`.
    - `direcciones_ataque()` la usan tanto el disparo como el **aviso** (`dibujar_aviso_ataque`, apagable con `opciones.aviso_jefe`).
  - Daño al jefe: dash contra `caja_nucleo()` mientras puede recibir golpe (`Partida._choques_jefe`). La nave rebota y queda 0.8 s invulnerable.
  - Daño a la nave: las balas (círculo) y el cuerpo (`toca_rect`).
  - Durante la pelea las monedas no suben de nivel. Al vencerlo: bonus `JEFE_PUNTOS * jefes_vencidos` y el cartel "¡JEFE VENCIDO!" (`CARTEL_JEFE`). Los enemigos guardados vuelven recién cuando se va el cartel.
- **Power-ups** (`powerups/`), registro `TIPOS_POWERUP`; el orden de `tipos.py` es el del HUD y del panel de inicio:
  - `duracion`: ms (escudo, hielo, imán, doble; valores en `DURACION`), `HASTA_PERDER_VIDA` (turbo, recarga) o `None` (vida, instantáneo).
  - `disponible(partida)`: vida solo si falta alguna; los permanentes, solo si no están activos.
  - `al_recoger()`: el hielo además rompe las balas y hace explotar escarcha.
  - `Capsula`: aparece cada `ESPERA_POWERUP` (la primera a los `PRIMER_POWERUP`), **cae** desde y=-15 en una x al azar a `VELOCIDAD_POWERUP` y se va al pasar y > 615.
  - Los efectos se consultan con `partida.activo(tipo)`: escudo en `danar_jugador`, hielo congela, imán atrae la moneda, doble en `sumar_puntos`, turbo en `vel_max` y recarga en `recarga_dash`.

### Servicios
- **Opciones** (`escenas/opciones.py` + `guardado.Opciones(archivo)`):
  - `FILAS` = RESOLUCION, FORMATO, FPS, VOLUMEN, MUSICA, EFECTOS, AVISO JEFE y VOLVER, cada 36 px (`210 + i * 36`) dentro del marco de 180 a 490. Con una fila más ya no entran: habría que hacer páginas o achicar el título.
  - `opciones.resolucion` es un nombre ("800x600", `None` = la primera) y `opciones.formato` es "4:3" o "16:9".
  - IZQ/DER cambian el valor con `_cambiar()`, que lo aplica al instante y lo guarda. ENTER cambia los `INTERRUPTORES`.
  - Para agregar una opción: sumarla a `FILAS`, dibujarla en `_dibujar_valor`, manejarla en `_cambiar` y guardarla en `guardado.Opciones`.
- **Guardado:** `TablaRecords` (`filas`, `maximo`, `entra()`, `agregar()` → posición) y `Opciones`.
  - Si el archivo no existe, se crea; si está dañado, se usan los valores de fábrica.
  - Si no se puede escribir, el juego sigue (`_escribir_json` ignora `OSError`).
- **Sonido:** `Sonidos.reproducir(nombre)`, `empezar_musica()`/`parar_musica()`, `pausar_todo()`/`reanudar_todo()` y `aplicar_volumen(opciones)`.
  - Si no hay audio o falta un archivo, ese sonido no suena.
  - Desactivar la música o los efectos los deja en volumen 0, así la música retoma donde iba. Para agregar un sonido: sumarlo a `ARCHIVOS`.
- **Ventana:** el lienzo es `app.pantalla` y `Ventana.mostrar()` lo escala sin suavizar, centrado y con barras negras.
  - `resoluciones` (propiedad) son las de `RESOLUCIONES[lienzo.formato]` que caben en el monitor; "COMPLETA" siempre está. `aplicar(nombre)` abre la ventana por nombre.
  - **Trampa:** al salir de FULLSCREEN, el primer `set_mode` deja el tamaño anterior; `aplicar()` lo repite.
- **Fondo** (`Fondo.mover(empuje_x, empuje_y)` en la lógica, mediante `Escena.mover_fondo(partida=None)`, y `Fondo.dibujar(pantalla, fraccion)` interpolado, mediante `Escena.dibujar_fondo`): objetos (`PROFUNDIDAD`) y estrellas (90 cada 800 px de ancho). Caen a `0.6 * profundidad` y, solo en Juego, se corren con el paralaje (`-v * REACCION_PARALAJE`). Paleta: ningún canal por encima de ~110.

## Tests (`tests/`)
- `conftest.py`:
  - pone los drivers dummy;
  - fixture `app` (datos en `tmp_path`, `usar_mandos=False`, reloj falso `app.reloj_falso` y teclas mantenidas en el conjunto `app.teclas`);
  - fixture `partida` (recién creada, sin enemigos, sin power-ups y con la moneda lejos).
- `ayudas.py`: `avanzar(app, frames)` (frames completos de la App, sin esperar), `tecla(K)`, `boton(n)` y `jugar(partida, frames, dx, dy, dash)` (solo la lógica).
- Se verificó que los tests detectan bugs inyectados a propósito (combo, hitbox y rango del embestidor).
- Para inspeccionar algo visual, sacar una captura de `app.pantalla` con `pygame.image.save` desde un script en el scratchpad que use `App(carpeta_datos=<scratchpad>)`. Filtrar la salida con `grep -a`, porque "¡" hace que grep la trate como binaria.

## Ideas pendientes (propuestas, aún sin hacer)
- Estadísticas al final de la partida (monedas, enemigos destruidos, tiempo); por ahora solo se muestra el mejor combo.
- Logros, tecla M para silenciar, música más intensa según el nivel, transiciones retro entre pantallas y F11 para pantalla completa.
- Del análisis de gameplay (no elegidas todavía):
  - tope de velocidad de los enemigos por debajo de la nave (el perseguidor la supera desde el nivel 11);
  - frenar más rápido al cambiar de dirección;
  - roce (graze) con puntos;
  - HUD que se oscurece si hay algo debajo.

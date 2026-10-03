# Caza Monedas (Pygame)

Juego arcade 2D hecho con Pygame. El jugador controla una nave que recoge monedas, esquiva enemigos y pelea contra jefes. El código está en el paquete `juego/`; `main.py` solo lo arranca. README.md tiene la guía para el usuario y explica cómo agregar enemigos, jefes y power-ups.

## Cómo ejecutar y probar
```
python main.py
python -m pytest        # ~210 tests, unos 18 s, sin ventana
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
  progresion.py         # Director: presupuesto de enemigos, sectores, oleadas, anomalias, desafios y rango
  anomalias.py          # Anomalia + registro: asteroides, tormenta, niebla, oro
  desafios.py           # Desafio + registro: sin_dash, intocable, sin_ayuda, combo, cazador
  rango.py              # Bitacora del sector y calcular_rango() (S/A/B/C)
  nave.py  moneda.py  proyectiles.py (Bala, Obus, Misil, Mina, Escombro, Onda, Veneno, Meteoro)
  enemigos/  base.py (Enemigo + registro) · perseguidor · rebotador · embestidor · divisor · enjambre · abeja
  jefes/     base.py (Jefe + registro + pulso) · partes.py (Parte) · ojo · fortaleza · serpiente · colmena · singularidad
  powerups/  base.py (PowerUp, Capsula, registro) · tipos.py (los 7 power-ups, en orden)
  escenas/   base.py · inicio · dificultad · opciones · listo · juego · pausa · explosion · iniciales · fin
  entrada.py  sonido.py  ventana.py  guardado.py  recursos.py
  dibujo.py   efectos.py  fondo.py   hud.py
tests/                  # conftest.py (fixtures app/partida), ayudas.py, test_*.py
sprites/ efectos/ fuentes/   # recursos (ver "Sprites"); efectos/ son los sonidos
records.json            # top 5 POR DIFICULTAD: {"FACIL": [{"nombre", "puntos"}...], "NORMAL": [...], ...}
                        # (un archivo viejo con una sola lista pasa a ser la tabla de NORMAL)
config.json             # {"formato", "resolucion", "fps", "volumen" (0-10), "musica", "efectos", "aviso_jefe", "dificultad"}
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
- Fuente Press Start 2P, siempre con `antialias=False`, en tamaños múltiplos de 8: `dibujo.MINI/CHICA/MEDIA/GRANDE/TITULO` = 8/16/24/40/56 (MINI solo para textos de apoyo, como la ficha de enemigo nuevo).
  - `dibujo.texto(pantalla, mensaje, tamaño, color, x, y, sombra, alinear)` recibe el tamaño como número; `recursos.fuente(tamaño)` guarda las fuentes en caché.
- Colores neón definidos como constantes en `config.py` (`AMARILLO`, `CIAN`, `MAGENTA`, `ROJO`…). Números con 6 dígitos (`dibujo.numero_arcade`).
- Partículas (`efectos.Efectos`): cuadrados alineados a una cuadrícula de 2 px. Pueden tener `gravedad`; `pedazos()` la usa para trozos que saltan y caen. No se desvanecen con transparencia: cambian de color por etapas según una **paleta**, una lista que va de oscuro a brillante (`FUEGO`, `ORO`, `ESCARCHA`…).
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

### Sprites opcionales que todavía no existen (todos tienen dibujo de respaldo)
El usuario pidió la lista para dibujarlos. Variantes (congelado, golpe, recalentado, brillo) se generan solas con `tenir`/`blanquear`: no hace falta dibujarlas.

| Archivo | Tamaño | Cuadros | Dónde se usa |
|---|---|---|---|
| `divisor.png` / `divisor_mediano.png` / `divisor_chico.png` | 96x48 / 64x32 / 40x20 | 2 cada uno | `Enemigo.cuadros()` |
| `enjambre.png` | 40x20 | 2 de 20x20 | `Dron` |
| `abeja.png` | 40x20 | 2 de 20x20 (alas arriba, abajo) | `Abeja` |
| `fortaleza.png` | 1536x128 | 6 de 256x128, de a pares: coraza, furia, cansado | `Fortaleza.cargar_animaciones()`; las 4 lamparitas del compás se dibujan encima (x+106..154, y+88) |
| `fortaleza_canon.png` | 64x32 | 2 de 32x32: sano, dañado (caño hacia abajo) | `cuadros_canon()`; la luz de color va encima en (14, 4) |
| `serpiente_cabeza.png` | 96x48 | 2 de 48x48: boca cerrada, abierta (mirando hacia arriba, SIN ojos) | `cuadros("cabeza", ...)`; ojos y lengua se dibujan aparte |
| `serpiente_cuerpo.png` | 64x32 | 2 de 32x32 (dos dibujos de escamas, se alternan) | segmentos (no giran) |
| `serpiente_cola.png` | 32x32 | 1 (el cascabel, punta hacia arriba) | gira y se sacude cuando brilla |
| `colmena.png` | 960x160 | 6 de 160x160, de a pares: calma, furia, aturdida | `Colmena.cargar_animaciones()` (el ojo de la reina va dibujado en el sprite) |
| `colmena_compuerta.png` | 64x32 | 2 de 32x32: cerrada, abierta | `cuadros_compuerta()` |
| `singularidad.png` | 768x128 | 6 de 128x128, de a pares: girar, inhalar, expuesta | se escala al nacer y al colapsar |
| `singularidad_asteroide.png` | 64x32 | 2 de 32x32 (dos rocas) | el anillo |

La llama del motor son partículas (`Efectos.estela()`), y el usuario prefiere que siga así: no proponer un sprite de propulsor. Los enemigos congelados se generan con `tenir(..., HIELO)`. Fuera de esta lista, no proponer sprites nuevos.

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
- Flujo: `Inicio → Dificultad → Listo → Juego ⇄ Pausa ⇄ Opciones`, y `Juego → Explosion → Iniciales (si entra al top 5 de esa dificultad) → Fin → Listo` (Fin repite con la misma dificultad).
- `App.nueva_partida(dificultad=None)`: sin dificultad, usa `opciones.dificultad`. Reinicia los efectos, vuelve el fondo a los colores del primer sector, crea una `Partida`, suena "seleccion", arranca la música y pasa a `Listo`.
- **Dificultad** (`escenas/dificultad.py`): IZQ/DER cambian con animación. El nombre entra deslizándose (`PASOS_ANIMACION`) y destella, las calaveras (`CALAVERA`, pixel art de 7x7) aparecen de a una, saltan chispas con la `paleta` de la dificultad y PESADILLA hace temblar la pantalla. ENTER guarda `opciones.dificultad` y empieza; ESC vuelve al inicio.
- **Pausa** (`escenas/pausa.py`): menú `FILAS_PAUSA` = CONTINUAR, OPCIONES y VOLVER AL MENU (ARRIBA/ABAJO + ENTER).
  - Siguen los atajos P/ESC/Menú (seguir) y O/Vista (opciones).
  - VOLVER AL MENU pregunta "¿VOLVER AL MENU?" (`confirmando`, NO por defecto; IZQ/DER cambia y ESC/B es NO) y avisa que se pierden la partida y su puntaje.
  - Si se confirma, `_volver_al_menu()` reanuda el mixer, para la música, reinicia los efectos y el fondo y pasa a un `Inicio` nuevo, sin guardar récord.
  - La ayuda de abajo cambia según si está la pregunta.
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
- Orden de `actualizar(dx, dy, pidio_dash)`: tiempo → nave (y aviso de dash) → corte del combo (`tiempo_combo()`) → imán → moneda → power-ups → director (oleadas, anomalías, desafíos, rango) → devolver enemigos guardados → enemigos (mover y choques) → jefe (balas, fases y choques) o balas sueltas → estela → brillo de la moneda → efectos.

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
  - `_acelerar()` separa la velocidad en **avance** (hacia donde se aprieta) y **deriva** (de costado). Arrancar usa `NAVE_ACELERACION`; lo que va hacia atrás o de costado se corrige con `NAVE_FRENADO` (más fuerte): dobla y frena enseguida sin perder la inercia. Acelerando desde quieta da lo mismo que antes (lo usa `test_frecuencia`).
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
  - **Tope de velocidad:** `Enemigo.rapidez(partida, base)` = `min(base * factor_velocidad(), ENEMIGO_VELOCIDAD_MAX)` (4.2; la nave va a 5): ningún enemigo que te persigue es más rápido que la nave. Lo usan perseguidor, divisor, embestidor (al acercarse) y el `paso()` del rebotador. Los ataques con aviso (embestida, picadas) no tienen tope.
  - `perseguidor`: inercia y se separa de los demás.
  - `rebotador`: diagonal y rebota; se acelera con `factor_velocidad()`.
  - **Enemigos destruibles con el dash** (`destruible = True`): `Partida._actualizar_enemigos` los destruye si la nave está en dash y su `caja_recoger()` toca `enemigo.caja()`.
    - `destruir_con_dash()` da `puntos_dash`, chispas y 2 frames de hit-stop, y adelanta la recarga del dash `RECARGA_POR_DESTRUIR` ms.
    - Después pasa por `destruir_enemigo()`, que llama a `al_destruirse(partida, con_dash)` y a `quitar_enemigo()`.
    - **Todo enemigo que sale del juego pasa por `Partida.quitar_enemigo()`**, que llama al hook `al_quitar()`; el dron lo usa para dejar su bandada.
    - Congelados y destruibles se rompen enteros (sin partirse).
    - Los de siempre (perseguidor, rebotador, embestidor) siguen siendo atravesados por el dash.
  - `esbirro = True` (las abejas): es de un jefe; `Partida.jefe_vencido()` los saca a todos. `hace_danio()` (por defecto True) deja que un enemigo no lastime por un rato (abeja volviendo a casa).
  - `abeja` (20x20, sin costo ni desbloqueo: solo la crea la Colmena): `salir_de()` una compuerta → rondar a 130 px → aviso (blanco y "!", 400 ms) → picar (`ABEJA_PICADA`). `enojarse()` la hace picar ya; `volver_a_casa()` la lleva a la Colmena sin hacer daño (`llego`).
  - Atributos de clase de `Enemigo`:
    - `tamano` y `radio`: el tamaño varía por tipo, y el daño usa `enemigo.radio`.
    - `destruible`, `puntos_dash` y `muere_al_chocar` (si te pega, se destruye en vez de reaparecer).
    - `nombre` y `pista`: el cartel "NUEVO ENEMIGO" en `hud.py`.
    - `crear()`: el enjambre crea varios enemigos a la vez; se usa vía `crear_enemigos(tipo, partida)`, que devuelve una lista.
    - Cada instancia tiene su `costo`: los hijos del divisor cuestan 0 y cada dron cuesta una parte del enjambre.
    - `nacer_en(partida, x, y, espera)`: aparecer en un punto, parpadeando (`naciendo`) en vez de con la X.
  - `divisor` (48x48) → 2 `divisor_mediano` (32x32) → 2 `divisor_chico` (20x20), cada uno con su clase.
    - Los hijos nacen al costado del dash con `DIVISOR_NACIMIENTO` ms sin hacer daño.
    - Su velocidad está en `DIVISOR_VELOCIDAD` y sus puntos en `DIVISOR_PUNTOS`.
    - El respaldo es `slime()`, dibujado a la mitad del tamaño y escalado x2.
  - `enjambre` (`Dron`, 20x20): son `ENJAMBRE_CANTIDAD` drones que comparten una `Bandada`.
    - La bandada es el centro del grupo: sigue a la nave y gira, y la formación se abre y se cierra. Sus fases son volar → aviso (destello blanco, `AVISO_PICADA`) → picada (`ENJAMBRE_PICADA`).
    - Cada dron va hacia `bandada.lugar(dron)` como un resorte.
    - Si un dron te choca, explota (`muere_al_chocar`). Destruirlos a todos con el dash da `ENJAMBRE_BONUS` (`todos_con_dash`).
    - Al volver del jefe, la bandada se reubica una sola vez (`ubicar`).
  - `embestidor`: `acercarse → apuntar (0.6 s, línea roja) → cargar (0.5 s)`. Solo te sigue y embiste dentro de `RANGO_EMBESTIDOR`; si no, deambula con `rumbo`.
  - **Separación:** los que persiguen se alejan entre sí a menos de `SEPARACION_ENEMIGOS`, con fuerza `FUERZA_SEPARACION`. Sin esto, se fusionaban a los ~10 s.
  - Progresión: la decide `Partida.director` (`progresion.Director`).
    - **Presupuesto:** cada tipo cuesta `COSTO_ENEMIGO` y se desbloquea en `DESBLOQUEO_ENEMIGO`. Cada nivel tiene `presupuesto()` (`PRESUPUESTO_INICIAL + (nivel-1) * PRESUPUESTO_POR_NIVEL`, con tope `PRESUPUESTO_MAXIMO`, por `reglas["presupuesto"]`).
      - `completar_presupuesto()` agrega enemigos al azar con `random.choices`; el favorito del sector pesa `PESO_FAVORITO`. Como mucho hay `ENEMIGOS_MAX` fijos.
      - El tipo recién desbloqueado se presenta primero.
      - Se llama al empezar, al subir de nivel y al volver del jefe. La cantidad se cuenta con `cantidad_actual()` (un enjambre cuenta como uno).
      - **Refuerzos:** cada `REFUERZO_ESPERA`, si sobra presupuesto (porque destruiste enemigos), llega uno nuevo.
      - Cuando se desbloquea un tipo después del nivel 1, el HUD muestra una **ficha chica** debajo del puntaje (`hud._ficha`: entra desde su lado, `DURACION_FICHA`, se ensancha si el nombre no entra): dibujo, "NUEVO ENEMIGO", nombre y pista en MINI. Antes era un cartel al centro y el usuario se quejó de que tapaba la pantalla. La ficha del desafío es la misma, del lado derecho.
    - **Sectores = biomas, uno por jefe** (`SECTORES`, en orden fijo): Cinturón → Ojo, Carmesí → Fortaleza, Esmeralda → Serpiente, Ámbar → Colmena, Abismo → Singularidad, y vuelve al primero. `iniciar_jefe()` usa `director.jefe_del_sector()`.
      - Cada sector: `nombre`, `lema` (debajo del nombre en el cartel), `color`, `jefe`, `tinte`, `fondo`, `ambiente`, `estrellas` (factor RGB) y `favorito`.
      - Se cambia en `jefe_vencido()` → `director.al_vencer_al_jefe()`; el cartel del sector sale cuando termina el cierre (`tiempo_cartel_sector` en el futuro; el HUD lo muestra si `0 <= t < 2500`).
      - Al cambiar se va `RECAMBIO_SECTOR` de los **grupos** de enemigos (un enjambre es un grupo); si estaban guardados por la pelea, no vuelven.
      - El fondo cambia con `Fondo.ir_a_sector(sector)` en 4 etapas durante `TRANSICION_SECTOR` pasos (lo llama `Escena.mover_fondo(partida)`). Los tintes no pasan de ~110 por canal.
    - **Anomalías** (`anomalias.py`, registro `TIPOS_ANOMALIA`, `director.anomalia`): en el nivel `ANOMALIA_NIVEL` de cada sector (3, 8, 13…), `ANOMALIA_ESPERA` después, llega la del sector (`sector["anomalia"]`; `None` o desde la 2ª vuelta, al azar) por `ANOMALIA_DURACION`.
      - Ganchos de `Anomalia`: `actualizar`, `terminar`, `dibujar` (lo llama `Partida._dibujar_todo` encima de todo y debajo del HUD), `multiplicador_monedas` y `factor_combo` (los consulta la Partida por medio del director).
      - `asteroides`: columnas punteadas (`avisos`) y `Meteoro`s que caen justo ahí `ASTEROIDES_AVISO` después (destruibles). `tormenta`: calma → aviso (bordes punteados) → llamarada (quema con `toca_rect`; el golpe empuja hacia afuera de la franja). `niebla`: superficie a 1/4 escalada x4 (bordes pixelados) con un agujero alrededor de la nave, del color del sector; encima, ojos de los enemigos lejanos y destellos de moneda y cápsula. `oro`: monedas x`ORO_MULTIPLICADOR`, combo x`ORO_COMBO`, polvo dorado.
      - No se pisa con las oleadas (ninguna empieza durante una ni hasta `RESPIRO_ANOMALIA` después); el jefe la corta. Medido con un bot (golpes/min, mismo nivel): sin nada ~4, oleada ~5.6, tormenta ~6.2, asteroides ~7 (pero solo ~0.7/min son de los asteroides: el resto, enemigos mientras esquiva), niebla y oro ≈ normal.
      - **Proyectiles sin jefe:** si no hay jefe pero hay balas (asteroides), `Partida._actualizar_balas_sueltas()` las mueve, el dash rompe las destruibles y `_tocar_balas()` revisa el daño (la misma que usa `_choques_jefe`).
    - **Desafíos** (`desafios.py`, registro `TIPOS_DESAFIO`, `director.desafio`): uno por sector, `DESAFIO_ESPERA` después de llegar (en el primero, del nivel `DESAFIO_DESDE_NIVEL`), al azar entre los `disponible()` y distinto del anterior.
      - De **aguantar** (`meta = None`: sin_dash, intocable, sin_ayuda) se fallan con su aviso y se cumplen al llegar el jefe; de **lograr** (combo `DESAFIO_COMBO`, cazador `DESAFIO_CAZADOR`, solo desde el divisor) se cumplen con `avanzar()` y se fallan si llega el jefe.
      - **Avisos:** la Partida llama a `director.al_recibir_golpe()` (en `danar_jugador`, también si para el escudo), `al_usar_dash()` (si cambió `nave.dash_hasta`), `al_agarrar_powerup()`, `al_recoger_moneda(combo)` y `al_destruir_enemigo()` (en `destruir_con_dash`). El director anota la bitácora y le pasa el aviso al desafío; `revisar_desafio()` premia (`DESAFIO_PUNTOS * numero_sector`, anillo, power-up enseguida) o lo marca fallado.
      - HUD: ficha a la derecha (`_ficha_desafio`: al proponerse, al cumplirse y al fallarse) y el nombre con el progreso debajo de las vidas (y 72/86, MINI).
    - **Rango y cierre del sector** (`rango.py`): `Bitacora` (golpes, mejor_combo, desafio_cumplido, inicio_jefe, tiempo_jefe). En `al_vencer_al_jefe()` se calcula `calcular_rango()` (estrellas: golpes 2/1/0, combo ≥ `RANGO_COMBO`, desafío, jefe antes de `RANGO_TIEMPO_JEFE` +20% por vuelta; S = 5, A = 4, B ≥ 2, C) y empieza el **cierre**: `CARTEL_JEFE` ("¡JEFE VENCIDO!") + `CARTEL_RANGO` (el cartel con las filas de a una; la letra cae a los `RANGO_SELLO`, y ahí `pagar_rango()` suma `RANGO_PUNTOS`). Mientras `director.cerrando_sector()`, los enemigos guardados no vuelven, las monedas no suben de nivel y no hay oleadas ni anomalías; al terminar sale el cartel del sector nuevo.
    - **Oleadas:** cada `OLEADA_ESPERA` (desde `OLEADA_DESDE_NIVEL`, sin jefe) llegan enemigos extra con `de_oleada=True` por `OLEADA_DURACION`, y después se van.
      - Si no perdiste vidas: `OLEADA_PUNTOS * nivel` y un power-up enseguida.
      - El jefe corta la oleada (`al_empezar_jefe`).
      - HUD: cartel "¡OLEADA!" y una barra abajo al centro.
  - **Dificultad:** `Partida(…, dificultad)` guarda `reglas = DIFICULTADES[dificultad]`, `vidas_max` y `vidas`.
    - `factor_velocidad()` multiplica por `reglas["velocidad"]` (también las balas del Ojo), y `espera_powerup()` por `reglas["espera_powerup"]`.
    - El HUD dibuja `vidas_max` íconos.
- **Jefes** (`jefes/`), registro `TIPOS_JEFE`; el que sale es el `"jefe"` del sector actual.
  - **Filosofía (pedido explícito del usuario):** las peleas son un **baile con ritmo, estilo Cuphead/Dark Souls**, no una lluvia de balas. Un ataque por vez, cada uno con **anticipación (aviso) → ataque a ritmo → ventana para pegarle**. Pocas balas (el bot mide ~0-10 en pantalla de promedio). Cada jefe con personalidad (nombre, apodo, gestos, textos) y su propio estilo de combate. Si se agrega uno, seguir esto.
  - **Pulso:** `ms_pulso` (por defecto `JEFE_PULSO`). `cambiar_fase(fase, ms, t)` y `cambiar_fase_pulsos(fase, n, t)` guardan `fase_desde`/`fase_hasta`; en cada paso la base calcula `self.pulso` (pulsos desde que empezó la fase, el 0 empieza el paso siguiente) y `self.nuevo_pulso`. `fin_de_fase(t)`. **Trampa:** el paso en que termina una fase también es el comienzo de un pulso: revisar `fin_de_fase` ANTES de `nuevo_pulso` (si no, sale un disparo de más; lo detectó un test).
  - La base resuelve `entrar` (`actualizar_entrada()`, por defecto baja hasta `y_final`) con la **presentación**: "¡CUIDADO!", `nombre` letra por letra y `apodo` (`color`, `y_presentacion`). Y `morir` (2 s de explosiones en `punto_de_explosion()`, después `partida.jefe_vencido()`).
  - También: la vida (`JEFE_VIDA + jefes_vencidos // 2`), el congelado (solo en `fases_congelables`; corre `fase_desde`/`fase_hasta` y llama a `al_congelarse()`), `recibir_golpe()` → `empezar_a_morir()`, `explotar()`, `al_vencerlo()`, las variantes de sprite (`imagen_actual()`), "¡DASH!" en `punto_cartel_dash()`, las cajas `caja_cuerpo()`/`caja_nucleo()`/`cajas_danio()`, `zonas_sin_monedas()` y `objetos_que_se_mueven()` (para interpolar piezas sueltas).
  - Dibujo: `dibujar()` = `dibujar_cuerpo()` (sprite en `posicion_dibujo()` + partes) + `dibujar_extra()` + avisos. Los jefes que no son un sprite fijo (Serpiente, Singularidad) reescriben `dibujar_cuerpo()`.
  - Tamaño por clase: `ancho`, `alto` (120 por defecto) e `y_final`. `temblando()` dice cuándo se dibuja temblando (por defecto, al morir).
  - **Partes** (`partes.py`, `Parte(dx, dy, ancho, alto, vida)`): piezas con posición relativa al jefe, guardadas en `jefe.partes`.
    - `Partida._choques_jefe`: en dash, primero `jefe.parte_golpeable(caja)` → `jefe.golpear_parte()` (efectos, hit-stop y `al_golpear_parte`/`al_romper_parte`); después el núcleo. Las dos rebotan la nave con `_rebotar_en()`.
    - El daño al tocar usa `jefe.cajas_danio()` (cuerpo + partes vivas; la Fortaleza suma los láseres prendidos). `lugar_para_moneda` también las esquiva.
    - `vida_barra()` da (vida, máximo) para el HUD; los jefes con partes suman las de ellas.
    - La base dibuja las partes (con el mismo flotar y temblor del cuerpo) y, debajo de cada parte golpeable, una flechita cian con un solo "¡DASH!" entre todas (con un cartel por parte se pisaban).
    - Las partes con posición propia (segmentos, asteroides) no son `Parte`: son objetos con `x`/`y` que el jefe devuelve en `objetos_que_se_mueven()`.
    - Congelado, una parte golpeable se puede seguir golpeando: el hielo alarga la ventana, igual que con el núcleo del Ojo.
  - `JefeOjo` ("EL OJO", Cinturón): `flotar` (`JEFE_FLOTAR`) → `atacar` (carga 0.7 s y `JEFE_RAFAGAS` ráfagas, turnando abanico y anillo de 12 balas) → `cansado` (`JEFE_CANSADO`) → `flotar`.
    - `direcciones_ataque()` la usan tanto el disparo como el **aviso** (`dibujar_aviso_ataque`, apagable con `opciones.aviso_jefe`).
  - `Fortaleza` ("ACORAZADO IMPERIAL", Carmesí, 256x128, `y_final = 56`): una marcha militar; 4 lamparitas del casco marcan el pulso.
    - Con coraza, cada compás: `reubicarse` (2) → `cargar` (2) → `disparar` (`PULSOS_ATAQUE`) → `recalentado` (`FORTALEZA_RECALENTADO`; los cañones del compás quedan `caliente` = golpeables). Si los golpean a todos, el compás termina antes.
    - 4 `Canon` (32x32, luz de su color): ráfaga (3 `Obus`, uno por pulso), misiles (2 `Misil`, el dash los destruye y da puntos), láser (barre hacia la nave a `FORTALEZA_LASER_VELOCIDAD`; hay que cruzarlo con el dash) y minas (2 `Mina` a las X de `objetivos`, estallan en "+" y "x" a 3 pulsos).
    - `FORTALEZA_PULSOS[cañones rotos]`: el pulso se acelera. Con 2 cañones el compás trae a los dos; con 1, ataca dos veces.
    - Sin cañones: `descubrirse` (4) → `caer_coraza()` → `cortinas` (6: aviso, cae, aviso, cae, 2 de respiro; `Escombro` con un hueco de 180 px) → `apuntar` (2, se pone encima) → `fijar` (1, quieta y temblando: tiempo para salir de abajo) → `caer` (`Onda` a los costados al tocar el piso) → `aturdida` (`FORTALEZA_ATURDIDA`, núcleo golpeable) → `subir` (3).
    - Cajas del casco en dos (`cajas_danio`): abajo es más angosto, así no pega con una esquina que no se ve.
  - `Serpiente` ("DEVORADORA DE ESTRELLAS", Esmeralda): jefe de movimiento, casi sin balas. Cabeza 48x48 + `Segmento`s (centro x/y) que siguen como cuerda (`arrastrar_cuerpo`, `SERPIENTE_ESPACIO`).
    - `nadar` (6, orbita la nave) → `acechar` (2; en el pulso 1 la `mordida` queda fija) → `morder` (`SERPIENTE_MORDIDA`) → si choca un borde `aturdida` (`SERPIENTE_VENTANA`) / si no `mareada`.
    - La vida son los cortes (`vida_max + SERPIENTE_CORTES_EXTRA`); el "núcleo" es la cola (`caja_nucleo`). Cada corte la acorta, la acelera (`factor()`) y acelera el pulso (`SERPIENTE_PULSOS`).
    - Desde el 2º corte alterna con `enroscarse` (6; círculo de aviso, cierra de 220 a 30 px alrededor de donde estabas). Desde la mitad escupe `Veneno` en los pulsos 2 y 4 de `nadar`.
    - Ojos que siguen a la nave, lengua cada 1.6 s, boca abierta al acechar/morder, ojos en cruz mareada.
  - `Colmena` ("MADRE DEL ENJAMBRE", Ámbar, 160x160): 4 `Compuerta`s (vida 1).
    - `flotar` (4) → `abrir` (2, tiembla y "BZZZ") → `soltar` (`COLMENA_ABEJAS`, una por pulso, tope `COLMENA_ABEJAS_MAX`) → `expuesta` (`COLMENA_EXPUESTA`, compuerta abierta = golpeable). Con ≤2 compuertas abre todas.
    - Romper una compuerta enoja a las abejas. Sin compuertas: llama a las abejas a casa ("¡A CASA, HIJAS!"; en la embestida no hay abejas: una sola amenaza), `enfurecerse` (3) → `temblar` (3; en el pulso 2 queda fija) → `embestir` (rebota `COLMENA_REBOTES` + golpes recibidos) → `aturdida` (ojo golpeable) → `volver` (3).
    - El aviso (`camino()`) dibuja centro y bordes del pasillo con los rebotes usando `paso_embestida()`, la misma cuenta que el movimiento (hay un test que lo compara).
  - `Singularidad` ("EL FIN DE LA LUZ", Abismo, 128x128 en el centro, `y_presentacion = 500`): gravedad (`atraer`, el dash no la siente) y un anillo de `Asteroide`s (20 `LUGARES`, entre dos vecinos no pasa la nave) con `huecos()`.
    - `girar` (6; `tic()`: el anillo avanza un lugar por pulso; brazos de 2-3 balas por pulso) → `inhalar` (3; atrae `SINGULARIDAD_INHALAR`; marca los bordes del hueco de la nova) → `exhalar` (nova de 15 balas con un hueco de 90° y empujón) → `colapsar` (2) → `expuesta` (`SINGULARIDAD_EXPUESTA`; anillo quieto y flechitas en los huecos) → `estallido` si le pegaste (te empuja afuera, el anillo se abre y cambia de sentido).
    - Cada 2 golpes, un hueco menos (`armar_anillo`) y un brazo más; desde el 3º, el anillo avanza de a 2. Se come la moneda (`comer_moneda`); `zonas_sin_monedas` incluye todo el disco del anillo. Mientras nace (`entrar`) no lastima.
  - **Proyectiles** (`proyectiles.py`): todos en `partida.balas`, con `mover(partida)` (False = borrar), `dibujar(pantalla, encendido)`, `radio`, `destruible` y `puntos` (los destruibles los rompe el dash en `Partida._destruir_proyectiles`). `Obus` (grande), `Misil` (te sigue `guiado` ms), `Mina` (frena y estalla en cruz "+"/"x"), `Escombro`, `Onda` (a ras del piso) y `Veneno`.
  - Daño al jefe: dash contra `caja_nucleo()` mientras puede recibir golpe, o contra una parte golpeable (`Partida._choques_jefe`). La nave rebota y queda 0.8 s invulnerable.
  - **Balance medido con un bot** (script del scratchpad que esquiva balas/cuerpos, lee los avisos y pega en las ventanas; cada jefe con su `jefes_vencidos` real): Ojo ~24 s, Fortaleza ~60 s, Serpiente ~33 s, Colmena ~45 s, Singularidad ~43 s; balas en pantalla de promedio: 7.6 / 3.7 / 0.6 / 0 / 9.5. Cuando el bot recibía muchos golpes en una fase, casi siempre era un aviso que no daba tiempo (se agregaron `fijar`, un pulso más en `temblar` y las flechitas de los huecos).
  - Daño a la nave: las balas (círculo de `bala.radio`) y `cajas_danio()` (`toca_rect`).
  - Durante la pelea las monedas no suben de nivel. Al vencerlo: bonus `JEFE_PUNTOS * jefes_vencidos`, el cartel "¡JEFE VENCIDO!" (`CARTEL_JEFE`) y el del rango (`CARTEL_RANGO`). Los enemigos guardados vuelven recién cuando termina el cierre del sector.
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
- **Guardado:** `TablaRecords`, con una tabla por dificultad: `filas(dif)`, `maximo(dif)`, `entra(puntos, dif)` y `agregar(nombre, puntos, dif)` → posición. `Opciones` guarda además `dificultad` (la última elegida).
  - Si el archivo no existe, se crea; si está dañado, se usan los valores de fábrica.
  - Si no se puede escribir, el juego sigue (`_escribir_json` ignora `OSError`).
- **Sonido:** `Sonidos.reproducir(nombre)`, `empezar_musica()`/`parar_musica()`, `pausar_todo()`/`reanudar_todo()` y `aplicar_volumen(opciones)`.
  - Si no hay audio o falta un archivo, ese sonido no suena.
  - Desactivar la música o los efectos los deja en volumen 0, así la música retoma donde iba. Para agregar un sonido: sumarlo a `ARCHIVOS`.
- **Ventana:** el lienzo es `app.pantalla` y `Ventana.mostrar()` lo escala sin suavizar, centrado y con barras negras.
  - `resoluciones` (propiedad) son las de `RESOLUCIONES[lienzo.formato]` que caben en el monitor; "COMPLETA" siempre está. `aplicar(nombre)` abre la ventana por nombre.
  - **Trampa:** al salir de FULLSCREEN, el primer `set_mode` deja el tamaño anterior; `aplicar()` lo repite.
- **Fondo** (`Fondo.mover(empuje_x, empuje_y)` en la lógica, mediante `Escena.mover_fondo(partida=None)`, y `Fondo.dibujar(pantalla, fraccion)` interpolado, mediante `Escena.dibujar_fondo`): objetos (`PROFUNDIDAD`) y estrellas (90 cada 800 px de ancho, teñidas con `sector["estrellas"]`). Caen a `0.6 * profundidad` y, solo en Juego, se corren con el paralaje (`-v * REACCION_PARALAJE`). Paleta: ningún canal por encima de ~110.
  - **Ambiente del bioma** (`sector["ambiente"]`, `Mota`s con tope `MAXIMO_MOTAS`): asteroides + estrellas fugaces, brasas que suben + relámpagos (`relampago`), luciérnagas + esporas, panal de fondo (`panal()`, baldosa que se desplaza) + polen, polvo que gira hacia el centro + ondas de gravedad. Al cambiar de sector, las motas viejas se van apagando de a poco.

## Tests (`tests/`)
- `conftest.py`:
  - pone los drivers dummy;
  - fixture `app` (datos en `tmp_path`, `usar_mandos=False`, reloj falso `app.reloj_falso` y teclas mantenidas en el conjunto `app.teclas`);
  - fixture `partida` (recién creada, sin enemigos, sin power-ups, sin oleadas, **sin anomalías ni desafíos** (`director.con_anomalias`/`con_desafios = False`; sus tests los prenden) y con la moneda lejos).
  - Para esperar a que vuelvan los enemigos después de un jefe: `CARTEL_JEFE + CARTEL_RANGO`.
- `ayudas.py`: `avanzar(app, frames)` (frames completos de la App, sin esperar), `tecla(K)`, `boton(n)` y `jugar(partida, frames, dx, dy, dash)` (solo la lógica).
- Se verificó que los tests detectan bugs inyectados a propósito (combo, hitbox y rango del embestidor).
- Para inspeccionar algo visual, sacar una captura de `app.pantalla` con `pygame.image.save` desde un script en el scratchpad que use `App(carpeta_datos=<scratchpad>)`. Filtrar la salida con `grep -a`, porque "¡" hace que grep la trate como binaria.

## Ideas pendientes (propuestas, aún sin hacer)
- Propuestas no elegidas: Torreta + Mina, Ladrón + Escudero, Fantasma + Barrera + Élites, taller de cartas, Los Gemelos, fase 2 del Ojo.
- Estadísticas al final de la partida (monedas, enemigos destruidos, tiempo); por ahora solo se muestra el mejor combo.
- Logros, tecla M para silenciar, música más intensa según el nivel, transiciones retro entre pantallas y F11 para pantalla completa.
- Del análisis de gameplay (no elegidas todavía; el tope de velocidad y el frenado ya se hicieron):
  - roce (graze) con puntos;
  - HUD que se oscurece si hay algo debajo.
- Mostrar los rangos de cada sector en la pantalla de Fin.

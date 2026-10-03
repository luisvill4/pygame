# Caza Monedas (Pygame)

Juego arcade 2D hecho con Pygame. El jugador controla una nave que recoge monedas y esquiva enemigos. Todo el código está en `main.py`.

## Cómo ejecutar
```
python main.py
```
- Requisitos: Python 3.12 y pygame 2.6.1. Se necesita pygame ≥ 2.1.4 por `pygame.transform.grayscale`.
- No hay `requirements.txt`, ni tests en el repo, ni git.

## Estructura
```
main.py                 # todo el juego (~2200 líneas)
sprites/                # imágenes del juego (lista completa en la sección "Sprites")
efectos/                # musica.mp3, moneda.wav, moneda_brillante.wav, golpe.wav,
                        # game_over.wav, seleccion.wav, nuevo_record.wav
fuentes/                # PressStart2P-Regular.ttf + OFL.txt (licencia, descargada de Google Fonts)
records.json            # top 5 {"nombre", "puntos"}; se crea vacío ([]) al arrancar si no existe
config.json             # {"resolucion", "volumen" (0-10), "musica", "efectos", "aviso_jefe"}; se crea al arrancar si no existe
```
El juego se dibuja siempre en 800x600 a 60 FPS (la ventana puede ser más grande, ver "Ventana"). Todas las rutas pasan por `ruta()` (relativas a la carpeta de `main.py`).

## El usuario y el estilo del código
- **Todo en español**: la conversación, los nombres de variables y funciones, y los comentarios. El usuario escribe en español informal.
- **Código de nivel principiante, a propósito:** variables globales a nivel de módulo, funciones simples con `global` cuando hace falta y comentarios cortos que explican el "por qué". La única clase es `Enemigo`. Mantener ese estilo y no introducir patrones avanzados sin que lo pida.
- Las constantes de ajuste están arriba, en la sección "Reglas del juego", y en el diccionario `DURACION`. Poner ahí cualquier número nuevo que el usuario pueda querer tocar.
- El archivo está dividido en secciones con banners `# ===== NOMBRE =====`: CONFIGURACION, RECURSOS, ESTADO, RECORDS, OPCIONES, MANDO, DIBUJO, PARTICULAS, ENEMIGOS, JEFE, JUEGO y BUCLE PRINCIPAL.

## Estilo visual: arcade retro (el usuario lo aprecia mucho, no romperlo)
- Fuente Press Start 2P siempre renderizada con `antialias=False`, en tamaños múltiplos de 8 (16/24/40/56).
- Colores neón definidos como constantes (`AMARILLO`, `CIAN`, `MAGENTA`, `ROJO`…). Números con 6 dígitos (`numero_arcade`).
- Partículas: cuadrados alineados a una cuadrícula de 2 px. No se desvanecen con transparencia: cambian de color por etapas según una **paleta**, una lista que va de oscuro a brillante (`FUEGO`, `ORO`, `ESCARCHA`…).
- Efectos disponibles: líneas CRT (`efecto_crt`), temblor en pasos de 2 px, destello de color, parpadeos duros (`parpadeo`), texto con relieve (`texto_3d`), marcos de doble línea (`marco`) y arcoíris (`color_arcoiris`).
- Variantes de sprites sin archivos nuevos: `tenir()` (escala de grises + multiplicar color) y `BLEND_RGB_MAX` para el destello blanco.

## Sprites
El usuario dibuja los sprites; Claude los integra. Todos están en `sprites/`.

**Reglas para sprites nuevos:**
- PNG con fondo transparente, pixel art sin antialiasing y tamaño exacto.
- Colores neón del juego: `#FFDD00`, `#FF3246`, `#00E6FF`, `#FF00AA`, `#3CFF78`, `#8CBEFF`, `#FFFFFF`, más tonos oscuros de esos mismos.
- Las animaciones son una "hoja" horizontal: cuadros del mismo tamaño, uno al lado del otro y sin separación.
- Lo que gira con la nave se dibuja mirando hacia arriba.

**Cómo se cargan** (sección RECURSOS):
- `cargar_sprite(archivo)` devuelve `None` si el archivo no existe; en ese caso se usa el dibujo de respaldo, así que nunca hay que tener todos los sprites para que el juego funcione.
- `cortar_hoja(hoja, ancho_cuadro)` separa los cuadros.
- `cuadro_animado(cuadros, ms_por_cuadro, desfase)` elige el cuadro con el reloj real.
- Las velocidades están en CONFIGURACION: `MS_CUADRO_ENEMIGO`, `MS_CUADRO_MONEDA` y `MS_CUADRO_ESCUDO`.

### Sprites que ya existen
| Archivo | Tamaño | Cuadros | Dónde se usa | Respaldo si falta |
|---|---|---|---|---|
| `nave.png` | 50x50 | 1 | `jugador_img` (mira hacia arriba); también `nave_icono` (vidas del HUD, 25x25) y `nave_fantasma_img` (dash) | obligatorio |
| `perseguidor.png` | 80x40 | 2 de 40x40 | `ENEMIGO_CUADROS["perseguidor"]`; también el ícono "ESQUIVA" en Inicio | `enemigo_respaldo(ROJO)`: cuadrado con dos ojos |
| `rebotador.png` | 80x40 | 2 de 40x40 | `ENEMIGO_CUADROS["rebotador"]` | `enemigo_respaldo(AMARILLO)` |
| `embestidor.png` | 80x40 | 2 de 40x40 | `ENEMIGO_CUADROS["embestidor"]` | `enemigo_respaldo(MAGENTA)` |
| `embestidor_carga.png` | 40x40 | 1 | `embestidor_carga_img`: embestidor en la fase "apuntar", fijo (la línea roja ya parpadea) | parpadeo con el primer cuadro en blanco (`embestidor_blanco_img`) |
| `moneda_giro.png` | 120x20 | 6 de 20x20 | `MONEDA_CUADROS`, con `imagen_moneda()` (en el juego y en Inicio) | elipse amarilla que se angosta |
| `powerups.png` | 150x30 | 5 de 30x30 | `CAPSULAS`, con `dibujar_capsula()`. Orden: escudo, hielo, vida, imán, doble (el mismo de `POWERUPS`) | cuadro con la letra |
| `escudo.png` | 152x76 | 2 de 76x76 | `ESCUDO_CUADROS`: burbuja centrada en la nave, en `dibujar_nave()`. Tiene píxeles semitransparentes (el brillo); está bien así | círculo cian |
| `nebulosa.png` | 256x192 | 1 | fondo con paralaje, 2 copias (la segunda volteada) | no se dibuja |
| `planeta_chico.png` | 32x32 | 1 | fondo con paralaje, 2 copias | no se dibuja |
| `planeta_grande.png` | 96x96 | 1 | fondo con paralaje, 1 copia | no se dibuja |
| `jefe.png` | 720x120 | 6 de 120x120, de a pares: flotar (1-2), atacar (3-4), cansado (5-6, núcleo a la vista) | `JEFE_ANIMACION[animacion]`, con sus variantes `JEFE_CONGELADO` y `JEFE_BLANCO`. Si la hoja trae 2 cuadros, se usan para todo | `jefe_respaldo(color_nucleo)` |

La llama del motor son partículas (`estela_nave()`), y el usuario prefiere que siga así: no proponer un sprite de propulsor.

Los enemigos congelados (`ENEMIGO_CONGELADO[tipo]`) se generan con `tenir(primer cuadro, HIELO)`, así que no necesitan sprite. Cada enemigo tiene `desfase`, para que no se animen todos a la vez.

No hay sprites pendientes. El usuario solo quiso dibujar el jefe: no proponer sprites nuevos.

- **Trampa:** en Press Start 2P la "É" mayúscula se dibuja como "é" pequeña. Por eso se escribe "RECORD" sin tilde. "¡" y los números funcionan bien.
- **Trampa:** en este Windows `SysFont("Arial")` carga **Arial Narrow**.

## Arquitectura
- **Máquina de estados** en la variable `estado`: `Inicio → Listo → Jugando ⇄ Pausa → Explosion → Iniciales (solo si entra al top 5) → Fin → Listo`. Cada estado es un bloque `if estado == ...:` dentro del bucle principal que termina con `mostrar(); tick(60); continue`. "Jugando" es el código que queda al final del bucle.
  - `Opciones` se abre desde Inicio (menú JUGAR / OPCIONES con IZQ/DER, `opcion_inicio`) o desde Pausa (tecla O). Al salir (ESC o VOLVER) vuelve a `volver_a`. Las filas están en la lista `filas`: RESOLUCION, VOLUMEN, MUSICA, EFECTOS, AVISO JEFE y VOLVER (`opcion_menu` es la elegida). Van cada 45 px (`fila_y = 230 + i * 45`); con una fila más ya no entran en el marco (de 190 a 480).
    - IZQ/DER llaman a `cambiar_opcion(fila, ±1)`, que aplica el cambio al instante y guarda `config.json`. ENTER también prende y apaga MUSICA, EFECTOS y AVISO JEFE.
    - Para agregar una opción: sumarla a `filas`, dibujar su valor en el `if` del bloque Opciones, manejarla en `cambiar_opcion()` y guardarla en `cargar_config()`/`guardar_config()`.
- **Sonido:** los efectos están en la lista `efectos_sonido`, sin `musica_fondo`. `aplicar_volumen()` usa `set_volume(volumen / VOLUMEN_MAX)`. Desactivar la música o los efectos los pone en volumen 0, pero siguen sonando en silencio, así la música retoma donde iba. Todo efecto nuevo tiene que sumarse a `efectos_sonido`.
- **Opciones guardadas:** `cargar_config()` llena `resolucion_actual`, `volumen`, `musica_activa`, `efectos_activos` y `aviso_jefe`. Si falta una clave, usa el valor de fábrica; si el archivo está dañado, usa todos los de fábrica.
  - `dibujar_opcion()` dibuja una opción de menú: la elegida va en amarillo con una flecha que parpadea.
- **Ventana:** `pantalla` es un lienzo de 800x600 (`Surface`), no la ventana. La ventana real es `ventana`, y `mostrar()` escala el lienzo sin suavizar, centrado y con barras negras si hace falta, y después hace `flip()`.
  - Siempre hay que dibujar en `pantalla` y llamar a `mostrar()`, nunca a `pygame.display.flip()` directo.
  - `resoluciones` es `RESOLUCIONES` filtrada según la altura del monitor (con 80 px de margen); "COMPLETA" siempre está.
  - La resolución se cambia desde Opciones con `aplicar_resolucion()`.
  - **Trampa:** al salir de FULLSCREEN, el primer `set_mode((ancho, alto))` deja la ventana en su tamaño anterior. Por eso `aplicar_resolucion()` lo repite si el tamaño no coincide.
- **Dos relojes, no mezclarlos:**
  - `tiempo_juego` avanza `1000/60` por fotograma, solo en Jugando. Lo usan todos los temporizadores de juego (`*_hasta`, `proximo_powerup`, combo, dash, `aparece_en` de enemigos, `tiempo_moneda`/`tiempo_golpe`). Así la pausa, READY y el hit-stop no los gastan.
  - `pygame.time.get_ticks()` es el reloj real. Solo se usa para parpadeos y animaciones visuales, y para `tiempo_menu`, que mide la duración de pantallas como READY, la explosión y el conteo del Game Over.
- **Teclado:** las acciones de un solo toque (ENTER, ESPACIO, P/ESC, letras de las iniciales) se leen de la lista `teclas_pulsadas`, que se llena con los `KEYDOWN` del fotograma. El movimiento usa `pygame.key.get_pressed()`.
- **Mando de Xbox** (sección MANDO): `evento_mando()` traduce los botones, la cruceta y el stick izquierdo a teclas falsas dentro de `teclas_pulsadas`, así menús, pausa e iniciales funcionan sin cambios. Los botones se traducen con `BOTONES_MANDO` (CONFIGURACION): A = ENTER, X = ESPACIO (dash), B = ESC (ignorado en Jugando para no pausar sin querer), Menú = P y Vista = O.
  - El stick cuenta como tecla solo cuando recién se inclina más allá de `ZONA_MUERTA` (`stick_antes`).
  - En Jugando, si no hay flechas apretadas, el movimiento sale de `direccion_mando()`. La cruceta va en 8 direcciones; el stick, en **cualquier ángulo** y siempre a velocidad máxima: los valores del eje se normalizan, igual que con las flechas. La zona muerta del stick es circular (`ZONA_MUERTA_NAVE = 0.25`, más chica que la de los menús).
  - `mandos` se llena con `JOYDEVICEADDED`, que pygame manda también por los mandos ya conectados, y se vacía con `JOYDEVICEREMOVED`.
  - `ayuda(teclado, mando)` elige el texto de ayuda según `hay_mando()`.
  - `vibrar(suave, fuerte, ms)` se llama en `danar_jugador()` (escudo, vida y muerte), en `golpear_jefe()` y en `jefe_explota()`.
  - El mando del usuario (Xbox Series X en Windows) da este mapeo de SDL: A=b0, B=b1, X=b2, Vista=b6, Menú=b7, cruceta=hat 0, stick izquierdo=ejes 0/1.
  - Para probar sin el mando: postear `JOYBUTTONDOWN`/`JOYHATMOTION`/`JOYAXISMOTION` con `instance_id` y meter un objeto falso en `g["mandos"]` con `get_numhats`, `get_hat`, `get_numaxes`, `get_axis` y `rumble`. Antes hay que vaciar `g["mandos"]`, para que el mando real no vibre.
- **Pausa automática:** con `WINDOWFOCUSLOST` (bucle de eventos) o al desconectarse un mando que estaba en `mandos` (`evento_mando()`), estando en Listo o Jugando, se marca `pausa_automatica = True`. Jugando la usa como si se hubiera apretado P. Si pasa durante READY, pausa en el primer fotograma de juego.
- **Hit-stop:** mientras `congelar_frames > 0`, el bucle solo hace flip, sin actualizar ni redibujar.
- **Dibujo del juego:** `dibujar_escena(con_nave)` dibuja todo y se reutiliza en Listo, Jugando y Explosion. La pausa muestra una captura (`captura_pausa`) oscurecida.
- **Fondo con paralaje** (`dibujar_fondo()`, se usa en todas las pantallas): primero `objetos_fondo` (nebulosas, planetas chicos y el grande, de lejos a cerca), después las estrellas.
  - Cada capa cae a `0.6 * profundidad` px por fotograma. Solo en Jugando se corre además `-vx/-vy * REACCION_PARALAJE * profundidad`.
  - La profundidad está en `PROFUNDIDAD` (0.15 / 0.3 / 0.6); las estrellas usan su velocidad (1 a 3).
  - Lo que sale por un costado entra por el otro; lo que sale por arriba o por abajo vuelve por el lado opuesto en una x al azar.
  - Para agregar otro objeto: `agregar_objeto_fondo(archivo, x, y, voltear)` y su profundidad en `PROFUNDIDAD`.
  - Paleta del fondo: ningún canal por encima de ~110, nada de colores neón ni grises claros, para que no se confunda con enemigos, monedas o power-ups.
- **Nave:** física con inercia (`aceleracion`, `friccion`, velocidad máxima 5, diagonal normalizada) y giro suavizado hacia el ángulo de las teclas (0 = arriba, 90 = izquierda; `atan2(-dx, -dy)`).
  - `inclinacion` angosta el sprite al girar.
  - Flota a pasos de 2 px cuando está casi quieta.
  - Al ser golpeada recibe un empujón (`empujon`) y queda invulnerable 1.5 s (parpadea).
  - **Dash con buffer:** apretar el dash guarda `dash_pedido_en`, y el dash sale si `ahora - dash_pedido_en <= BUFFER_DASH` y ya se recargó. Cuando se recarga, la nave hace un destello cian chico, una sola vez por recarga (`dash_avisado`).
- **Zonas del HUD:** `ZONAS_HUD` (sección JUEGO) tiene los rectángulos que ocupa el HUD: la franja de arriba (y < 100), la de abajo (y ≥ 530) y la columna de power-ups activos (abajo a la izquierda). `posicion_libre(ancho, alto)` elige una posición al azar fuera de esas zonas. Si el HUD cambia de lugar o crece, hay que actualizar `ZONAS_HUD`.
- **Moneda nueva:** `lugar_moneda()` usa `posicion_libre()` y además pide estar a entre `MONEDA_DISTANCIA_MIN` y `MONEDA_DISTANCIA_MAX` (120–450 px) de la nave, a más de 60 px de cada enemigo y lejos del cuerpo del jefe. Prueba hasta 200 lugares. Con 450 px como máximo, siempre se llega antes de que se corte el combo (`COMBO_TIEMPO`).
- **Choques:**
  - Para recoger cosas (monedas, power-ups, enemigos congelados y el núcleo del jefe con el dash) se usa la caja grande de 50×50 (`caja_jugador`) contra `Enemigo.caja()` (32×32), entre otras.
  - El **daño usa círculos**, que no cambian con el giro de la nave: `nave_toca_circulo(cx, cy, radio)` con `RADIO_NAVE = 11` contra `RADIO_ENEMIGO = 15` y `RADIO_BALA = 4`, y `nave_toca_rect(rect)` para el cuerpo del jefe (punto más cercano del rectángulo).
- **Enemigos:** la lista `enemigos` contiene objetos `Enemigo` de tres tipos:
  - `perseguidor`: persigue con inercia.
  - `rebotador`: va en línea recta y rebota en los bordes.
  - `embestidor`: pasa por las fases `acercarse → apuntar` (0.6 s, línea roja punteada y sprite de carga) `→ cargar` (0.5 s en línea recta).
    - En `acercarse` solo te sigue si estás a menos de `RANGO_EMBESTIDOR` (250 px). Si no, deambula a 0.5 px por fotograma según `self.rumbo`, que cambia al azar (1% por fotograma) y apunta al centro cuando toca un borde.
    - Solo pasa a `apuntar` si estás dentro del rango; si `fase_hasta` ya pasó, embiste apenas entrás. Una vez que apunta, la embestida sigue aunque te alejes.
  - Cada tipo tiene su sprite animado (ver "Sprites").
  - **Separación:** el perseguidor y el embestidor en `acercarse` llaman a `Enemigo.separarse()`. Esa función los empuja lejos de cualquier enemigo activo a menos de `SEPARACION_ENEMIGOS` (50 px), con más fuerza cuanto más cerca (`FUERZA_SEPARACION`). Sin esto, los perseguidores terminaban fusionados en el mismo punto a los ~10 s, porque todos siguen a la nave de la misma forma. El rebotador no la usa: va en línea recta.
  - Al aparecer o reaparecer, cada uno muestra una "X" durante `AVISO_APARICION` y en ese tiempo no hace daño.
  - Se agrega uno según `ENEMIGOS_POR_NIVEL`; el nivel sube cada `MONEDAS_POR_NIVEL` monedas. Son 5 hasta el primer jefe.
  - Después de cada jefe vencido, cuando vuelven los enemigos guardados, se suma uno de `ENEMIGOS_POR_JEFE` (embestidor, perseguidor, rebotador, rotando) hasta `ENEMIGOS_MAX = 8`.
- **Jefe** (sección JEFE; variables globales `jefe_*`, sin clase): aparece en `subir_nivel()` cuando `nivel % JEFE_CADA_NIVELES == 0`.
  - `iniciar_jefe()` hace explotar a los enemigos y los pasa a `enemigos_guardados`. Vuelven con `reaparecer()` desde el bucle de Jugando, recién cuando termina el cartel "¡JEFE VENCIDO!" (`CARTEL_JEFE` ms después de `jefe_explota()`). Así el cartel no tapa la "X" de aviso.
  - Fases (`jefe_fase`): `entrar` (baja hasta y=70 con el cartel "¡CUIDADO!") → `flotar` (`JEFE_FLOTAR` ms de lado a lado) → `atacar` → `cansado` (`JEFE_CANSADO` ms) → `flotar`… y `morir` (2 s) al llegar a 0 de vida. Se cambia de fase con `cambiar_fase_jefe(fase, duracion)`.
  - `atacar` se carga 0.7 s y tira `JEFE_RAFAGAS` ráfagas desde el ojo (`disparar_jefe()`), turnándose entre `abanico` (hacia la nave) y `anillo` (con un giro distinto por ráfaga). Los ángulos y la rapidez salen de `direcciones_ataque()`, que usan tanto el disparo como el aviso.
  - **Aviso del ataque** (`dibujar_aviso_ataque()`, desde `dibujar_jefe()`): durante la carga (`jefe_rafagas == JEFE_RAFAGAS`), si `aviso_jefe` está activo y el jefe no está congelado, el abanico muestra líneas punteadas rojas hacia la nave y el anillo rayitas magenta cortas en la dirección de cada bala. Parpadea con `parpadeo(100)`. Se desactiva en Opciones → AVISO JEFE.
  - Las balas están en `balas` (`[x, y, vx, vy]`) y se dibujan con `dibujar_balas()`.
  - Daño al jefe: solo con el dash contra `caja_nucleo_jefe()` mientras está `cansado` (`golpear_jefe()`, que hace rebotar la nave y le da 0.8 s de invulnerabilidad). Durante `cansado` aparece "¡DASH!" debajo del jefe.
  - Daño al jugador: las balas (círculos) y `caja_cuerpo_jefe()` (con `nave_toca_rect`), que se revisan en `revisar_choques_jefe(caja_jugador)`. El dash y la invulnerabilidad los atraviesan.
  - Hielo: al recogerlo rompe todas las balas. Con `jefe_congelado()` (no aplica en `entrar` ni en `morir`), el jefe no se mueve, no ataca, no hace daño y su fase no avanza.
  - Vida: `JEFE_VIDA + jefes_vencidos`. Bonus: `JEFE_PUNTOS * jefes_vencidos`. Las balas son más y más rápidas con cada jefe vencido.
  - Durante la pelea las monedas dan puntos pero no cuentan para subir de nivel. La barra del jefe va abajo al centro (`dibujar_barra_jefe()`) y, al vencerlo, aparece el cartel "¡JEFE VENCIDO!" (`tiempo_cartel_jefe`, dura `CARTEL_JEFE`).
- **Daño al jugador:** siempre pasar por `danar_jugador(golpe_x, golpe_y)` (enemigos, jefe y balas). Si hay escudo, lo rompe y da 0.5 s de invulnerabilidad; si no, quita una vida y, con 0 vidas, pasa a `Explosion`.
- **Puntos:** siempre pasar por `sumar_puntos(base)`, que aplica "doble" y detecta cuándo se supera el récord. El combo usa `multiplicador_combo() = min(1 + combo // 3, 5)`.
- **Power-ups:** el diccionario `POWERUPS` guarda por tipo (letra, color, nombre, descripción); la duración está en `DURACION`. Hay uno en pantalla a la vez (`powerup_tipo`), aparece cada 8–13 s y **cae** desde arriba de la pantalla (`py = -15`, con `px` al azar entre 30 y 770) a `VELOCIDAD_POWERUP` px por fotograma. Si no lo recogés, desaparece al pasar `py > 615` (con 1.5 tarda ~7 s). Tipos:
  - escudo: aguanta un golpe;
  - hielo: congela a todos los enemigos, y tocarlos da +5;
  - vida: solo aparece si falta alguna;
  - imán;
  - doble;
  - turbo (`turbo_activo`, velocidad máxima `TURBO_VELOCIDAD`) y recarga (`recarga_activa`, el dash se recarga en `RECARGA_RAPIDA` vía `recarga_dash()`): no están en `DURACION`, **duran hasta perder una vida** (se apagan en `danar_jugador()`; si el escudo aguanta el golpe, siguen). Solo aparecen si no están activos. No tienen cuadro en `powerups.png`, así que usan el cuadro con letra (T y R).
- **Récords:** `cargar_records()` lee `records.json`. Si no existe, lo crea con `[]`; si está dañado, empieza con la tabla vacía (se sobrescribe al guardar). `agregar_record()` ordena la tabla, deja 5 filas y guarda. Si se cierra la ventana en la pantalla de iniciales, el récord se guarda igual.

## Cómo probar sin ventana (patrón usado en sesiones anteriores)
1. **No probar en la carpeta real.** El juego escribe `records.json` y `config.json`, así que hay que copiar `main.py sprites efectos fuentes` a una carpeta del scratchpad y correr ahí.
2. El script de prueba:
   - pone `SDL_VIDEODRIVER=dummy`;
   - reemplaza `pygame.display.flip` por una función "hook" que se ejecuta una vez por fotograma;
   - reemplaza `pygame.key.get_pressed` para simular teclas mantenidas;
   - envía teclas de un toque con `pygame.event.post(Event(KEYDOWN, key=...))`;
   - ejecuta el juego con `exec(compile(open("main.py").read(), ...), g)`, con `"__file__"` definido dentro de `g`.
3. Desde el hook se leen y modifican las variables globales del juego a través de `g` (por ejemplo, llamar a `g["reiniciar_partida"]()` o mover enemigos), y se guardan capturas con `pygame.image.save(pygame.display.get_surface(), ...)` para revisarlas.
4. Filtrar la salida con `grep -a`: los textos con "¡" hacen que grep la trate como binaria.
5. Las pruebas corren en tiempo real (60 FPS). Considerarlo al elegir los números de fotograma.
6. Con el driver dummy, el escritorio mide 1024x768, así que `resoluciones` queda solo en 800x600 y COMPLETA. Para probar las otras, hay que asignar `g["resoluciones"] = list(g["RESOLUCIONES"])` desde el hook. `pygame.display.get_surface()` es la ventana ya escalada; `g["pantalla"]` es el lienzo de 800x600.

## Ideas pendientes (propuestas, aún sin hacer)
- Estadísticas al final de la partida (monedas, enemigos destruidos, tiempo); por ahora solo se muestra el mejor combo.
- Logros simples, tecla M como atajo para silenciar (el silencio ya existe en Opciones), música más intensa según el nivel.
- Dividir en archivos (`config.py`, `efectos.py`, `pantallas.py`), clases para el jugador y las partículas, delta time.
- Transiciones retro entre pantallas. Tecla F11 como atajo a la pantalla completa (esta ya existe en Opciones).
- Del análisis de gameplay (propuestas que el usuario no eligió todavía):
  - limitar la velocidad de los enemigos por debajo de la de la nave (el perseguidor la supera desde el nivel 11);
  - frenar más rápido al cambiar de dirección;
  - roce (graze) con puntos;
  - HUD que se oscurece si hay algo debajo.
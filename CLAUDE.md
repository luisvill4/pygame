# Caza Monedas (Pygame)

Juego arcade 2D hecho con Pygame: una nave recoge monedas, esquiva enemigos y pelea contra jefes. Tiene dos modos: **ARCADE** (la ruta sin fin, con récords) e **HISTORIA** (*La Marea*, en beta). El código está en el paquete `juego/`; `main.py` solo lo arranca. `README.md` es la guía para el usuario (y explica cómo agregar enemigos, jefes y power-ups). **`HISTORIA.md` es la biblia del modo historia** (la verdad de fondo, personajes, misiones, catálogo de secretos y cómo escribirlos): leerla antes de tocar cualquier texto o secreto. El sonido tiene sus propios documentos: `MAPA_DE_AUDIO.md` (qué suena en cada evento) y `LISTA_DE_SONIDOS.md` (la partitura de cada sonido, la base musical y el registro de avances).

## Cómo ejecutar y probar
```
python main.py
python -m pytest        # ~500 tests, 70-150 s, sin ventana
```
- Python 3.12, pygame 2.6.1 (≥ 2.1.4 por `pygame.transform.grayscale`) y pytest. El estudio de sonido necesita además numpy, numba y soundfile. Todo está en `requirements.txt`.
- **Git:** `main` tiene la versión de un solo archivo de antes del refactor; se trabaja en la rama `refactor-modular`. `.gitignore` deja afuera `records.json`, `config.json`, `progreso.json` y `__pycache__`.
- **Correr `python -m pytest` después de cada cambio.** Una regla de juego nueva lleva su test.

## El usuario y el estilo del código
- **Todo en español**: la conversación, los nombres de variables, funciones y clases, y los comentarios. El usuario escribe en español informal.
- **El usuario está aprendiendo.** Eligió una arquitectura "modular con clases": clases base, registros y escenas, **sin** type hints, dataclasses ni bus de eventos. Mantener ese nivel. Nombres claros, métodos cortos y comentarios que explican el "por qué" y los patrones (State, Registry, Template Method).
- Cualquier número que el usuario pueda querer tocar va en `config.py` ("Reglas del juego" o `DURACION`).
- Dependencias sin ciclos: `config` ← `recursos`/`dibujo` ← entidades ← `partida` ← escenas ← `app`. Las entidades reciben `partida` como parámetro (no la importan).
- **El arcade y la historia están separados** (pedido del usuario): `juego/arcade/` y `escenas/arcade/` no importan nada de la historia, y al revés; la lógica de los modos no importa pantallas. `tests/test_modos.py` lo comprueba. Lo compartido (partida, Director, rutas, enemigos, jefes, HUD...) no pregunta "¿es la historia?": le pregunta al **modo** (`partida.modo`).
- Quiere que todo "parezca un triple A" sin perder la esencia retro: ante un cambio visual, mostrar capturas.

## Estructura
```
main.py                 # App().ejecutar()
juego/
  config.py             # SOLO valores: colores, paletas, "Reglas del juego", DURACION, mando
  app.py                # App: servicios, escenas y bucle de paso fijo (paso(), cuadro(ms), ejecutar())
  interpolacion.py      # Interpolador: dibujar en posiciones intermedias entre pasos de logica
  reloj.py              # LimitadorFPS
  partida.py            # Partida: todo el estado de una partida y sus reglas
  modos.py              # Modo: la base de los modos de juego (Strategy): lo que la partida le pregunta
  progresion.py         # Director: tramos, escuadrones, asedio, sectores, anomalias, desafios, rango
  rutas.py              # SOLO datos: la ruta de cada sector (4 tramos con su objetivo y sus escuadrones)
  objetivos.py          # lo que pide cada tramo para pasar (registro: monedas, romper, interceptar, perfectos, asedio)
  escuadrones.py        # las formaciones (@formacion: flanco, pinza, lluvia, esquinas, cerco) y Escuadron
  radio.py              # la cola de mensajes de radio (la usa la historia; existe en toda partida)
  anomalias.py  desafios.py  mejoras.py  rango.py  estadisticas.py  logros.py  eco.py
  arcade/               # EL MODO ARCADE: modo.py (ModoArcade) · tienda.py (la gasolinera)
  historia/             # EL MODO HISTORIA ("La Marea", ver HISTORIA.md):
    modo.py             #   ModoHistoria: las reglas de una mision, la radio y los secretos mientras jugas
    mision.py           #   Mision (base) + Fragmento + registro (@registrar_mision, misiones_en_orden)
    misiones/           #   UNA MISION POR ARCHIVO: m1_la_senal.py ... m5_el_fin_de_la_luz.py
    secretos.py         #   tipos de secreto (registro): moneda_grabada, restos, baliza, racha, golpe_desde...
    fichas.py           #   SOLO datos: el porque de cada enemigo, jefe, power-up y anomalia (el Archivo)
    galaxia.py          #   el mapa: los sistemas (la Umbral, las misiones y los libres), el peligro y el costo de viajar
    tiempo.py           #   el reloj de la Umbral (la relatividad): años, mensajes de Ines, el frente de la Marea
    exploracion.py      #   ModoExploracion: una partida en un sistema libre (ruta generada por su peligro)
    hangar.py  ecos.py  #   las mejoras para siempre (con piezas) · SOLO datos: las historias de los sistemas libres
    modulos.py          #   los modulos que abren la galaxia (peligros ambientales, planos) y sus piezas en la nave
    reliquias.py  personajes.py  glifos.py   # objetos secretos · quien habla y sus retratos · la escritura y su ritmo
  nave.py  moneda.py  proyectiles.py
  enemigos/  base.py (Enemigo + registro) · perseguidor · rebotador · embestidor · divisor · enjambre · abeja
             · ladron · escudero
  jefes/     base.py (Jefe + registro + pulso) · partes.py · ojo · fortaleza · serpiente · colmena · singularidad
  powerups/  base.py (PowerUp, Capsula, registro) · tipos.py (en el orden del HUD)
  escenas/   base.py · presentacion · inicio · logros · opciones · listo · juego · taller · pausa
             · desarrollador · explosion · pasajes.py (que pantalla sigue segun el modo)
             arcade/   dificultad · gasolinera · iniciales · fin · pasajes
             historia/ galaxia · hangar · dialogo · archivo · final · pasajes
  entrada.py  haptica.py  sonido.py  ventana.py  guardado.py  recursos.py
  dibujo.py  efectos.py  fondo.py  hud.py
  accesibilidad.py      # temblor, destellos y CRT: los efectos le preguntan aca
  interfaz.py           # el kit de interfaz (panel, titulo, menu, ayudas, pestanas, carta...)
  transicion.py         # el barrido de rombos entre pantallas
  avisos.py  carteles.py  impactos.py   # la cola de avisos, el dibujo de los carteles y de los impactos
herramientas/
  componer.py           # compone musica y efectos con el estudio
  estudio/              # el estudio de sonido (ver "El estudio")
tests/                  # conftest.py (fixtures app/partida), ayudas.py, test_*.py
sprites/  fuentes/
efectos/                # todo el sonido, en OGG, por familia (la del modulo del estudio donde se compone):
  fichas.json           #   cuanto suena cada archivo (lo escribe el estudio, lo lee el mezclador)
  musica/  ambiente/  interfaz/  juego/  enemigos/  director/  jefes/
    moneda_1/           #   un efecto ARMONICO va en su carpeta, un archivo por color (moneda_1_fa.ogg...)
records.json            # top 5 por dificultad: {"FACIL": [{"nombre", "puntos"}...], ...}
config.json             # las opciones (guardado.Opciones)
progreso.json           # {"logros": [ids], "nave": "CIAN", "partidas": n, "misiones": [1, 2], "fragmentos": ["F01"], "fichas": [...],
                        #  "anios", "ubicacion", "piezas", "hangar": {"impulsor": 1, "filtro": 2}, "sistemas", "puertas", "mensajes", "planos"}
```
Las rutas pasan por `config.ruta()`, relativas a la carpeta raíz.

## Reglas que no se pueden romper

### Paso fijo + interpolación
- **La lógica avanza siempre en pasos de 1/60 s** (`MS_POR_FRAME`). Todo lo que en `config.py` dice "por frame" es por paso. Se dibuja a `opciones.fps` (30 a 144 o sin límite) y el juego va a la misma velocidad a cualquier FPS (hay un test).
- `App.cuadro(ms)` acumula tiempo, corre los pasos que tocan y dibuja con `fraccion`. `App.paso()` hace un paso y un cuadro (lo usan los tests).
- En `actualizar()` va **todo** lo que cambia el estado: también `mover_fondo()`, el temblor (`Efectos.actualizar`) y el marcador que cuenta (`puntaje_visible`). `dibujar()` solo dibuja: puede correr varias veces o ninguna por paso.
- La entrada se acumula (`procesar`) hasta que un paso la usa (`consumir`).
- Lo que se mueve tiene `x`/`y` y está en `Partida.objetos_que_se_mueven()` (o en el `Fondo`): así se dibuja interpolado. El `Interpolador` no interpola saltos de más de 80 px.
- **Dos relojes, no mezclarlos:** `partida.tiempo` (avanza solo en `actualizar()`) para todo temporizador de juego; el reloj real (`pygame.time.get_ticks()`, `App.ahora()`) solo para parpadeos y animaciones que se repiten.
- Lo que se anima en un menú avanza en `actualizar` (ej. `interfaz.Cursor.avanzar()`), así anda igual a cualquier FPS.

### Pantalla: 16:9 y la grilla de 2 px
- Lienzo de `ANCHO` x `ALTO` = 1066x600. **Nunca escribir el ancho a mano:** `ANCHO` y `CENTRO_X`. Lo de la izquierda se ancla a x=20, lo de la derecha a `ANCHO - 20`. El usuario eliminó el modo 4:3.
- Los menús usan todo el ancho. Solo el panel de desarrollador usa `dibujo.zona_central` (800x600).
- **Grilla de píxeles de arte (`PIXEL_ARTE` = 2):** los sprites están dibujados con píxeles de 2x2 y **todo lo demás se alinea a esa grilla** (pedido del usuario: el neón y el halo no calzaban). Todo sprite se pega con `dibujo.pegar(...)`; las posiciones con `dibujo.en_grilla(...)`; partículas, halos, ondas, barras y texto en tamaños pares. `test_todo_calza_en_la_grilla_de_pixeles_de_arte` lo comprueba. Solo quedan afuera los íconos de vidas y el texto MINI (píxeles de 1).
- **El CRT lo pone `Ventana.mostrar()` después de escalar**, una línea al pie de cada fila de píxeles de arte. Las escenas NO dibujan el CRT.
- **Capas de la partida** (`Escena.dibujar_partida`): fondo → mundo (interpolado) → temblor y destello → impactos (`partida.dibujar_impactos`) → HUD. **El temblor y el destello nunca mueven el HUD.**
- **Trampa:** al salir de FULLSCREEN, el primer `set_mode` deja el tamaño anterior; `Ventana.aplicar()` lo repite.

### Accesibilidad
- **Un efecto nuevo que tiembla, destella o parpadea pasa por `accesibilidad.py`** (`temblor_maximo()`, `destellos_reducidos()`) o por `dibujo.parpadeo()`/`color_arcoiris()`, que ya lo hacen. Con DESTELLOS REDUCIDOS: sin destellos de pantalla completa y nada parpadea más de 3 veces por segundo.
- MINI (fuente de 8) solo para textos de apoyo, nunca para información que haya que leer jugando.

### Carteles que no tapan el juego
- Pedido del usuario: los carteles le tapaban monedas y enemigos. **Todo cartel o ficha del HUD se dibuja con `hud._cartel(...)`**: dibuja en una capa transparente y, si lo dibujado toca algo de `cosas_que_importan(partida)`, lo pega con menos opacidad (`CARTEL_ALFA_TAPANDO`) por un rato.
- **Trampa:** para volver opaca la capa se usa `set_alpha(255)`. `set_alpha(None)` le saca la transparencia por píxel y el cartel sale sobre un recuadro negro.

## Estilo visual: arcade retro (el usuario lo aprecia mucho, no romperlo)
- **Fuente** Press Start 2P, siempre con `antialias=False`, en tamaños múltiplos de 8: `dibujo.MINI/CHICA/MEDIA/GRANDE/TITULO` = 8/16/24/40/56. `dibujo.texto(..., contorno)`: **todo lo que va encima del juego lleva contorno** (`CONTORNO`). Los textos se guardan armados en caché (`dibujo._textos`).
- **Trampas de la fuente:** la "É" mayúscula sale como "é" chica (por eso "RECORD" va sin tilde; "¡", "¿", "Ñ" andan bien). En este Windows `SysFont("Arial")` carga Arial Narrow.
- **Colores:** los neón son constantes de `config.py` (`AMARILLO`, `CIAN`, `MAGENTA`, `ROJO`…). La interfaz usa los de papel fijo: `TEXTO`, `TEXTO_SUAVE`, `TEXTO_APAGADO`, `RESALTADO`, `CONTORNO`, `LINEA_APAGADA`, `FILA_ELEGIDA`. Números de 6 dígitos con `dibujo.numero_arcade`.
- **Kit de interfaz (`interfaz.py`): toda pantalla nueva se arma con esto.** `panel` (con escuadras y franja de título), `titulo`, `renglon`, `separador`, `menu` (con la nave del jugador como cursor que se desliza: `Cursor`), `ayudas` y `boton` (la barra de abajo con los botones **del último control que se tocó**: `entrada.usando_mando()`), `pestanas` (con LB/RB o Q/E en las puntas), `carta` (la carta de mejora del Taller y la Gasolinera) y `pixelado` (el fondo de Pausa, Taller y Desarrollador, sobre `Escena.captura_del_mundo`, que no incluye el HUD).
- **Componentes de `dibujo`** (usarlos en vez de dibujar a mano): `pestanas`, `barra` (bloques de 4 px; `borde=None` = finita), `barra_segmentos`, `partir_lineas`, `flecha`, `parpadeo`, `texto_3d`, `marco`, `color_arcoiris`, `oscurecer`, `pixel_art` (dibujos de "X" y ".") y `halo`.
- **Partículas** (`efectos.Efectos`): cuadrados en la grilla de 2 px que no se desvanecen con transparencia: cambian de color por etapas según una **paleta** de oscuro a brillante (`FUEGO`, `ORO`, `ESCARCHA`…). También: `onda_de_choque`, `fogonazo`, `texto_flotante` (nunca se pisan) y el temblor/destello (`sacudir`).
- **Neón** (opción NEON): un resplandor **solo en lo que es energía** (proyectiles con `brillo`, la moneda, las cápsulas, las chispas), nunca en toda la pantalla: un bloom general lavaba el pixel art de los jefes.
- **Carteles del juego** (`carteles.py`), cada tamaño en su lugar:
  - **Avisos** arriba al centro (TRAMO 2/4, ¡ASEDIO SUPERADO!, anomalías, récord): salen **de a uno** con `partida.avisar(Aviso(...), urgente)` → `ColaDeAvisos`. Los urgentes se cuelan adelante.
  - **Fichas** a los costados: nuevo enemigo (izquierda) y desafío (derecha). Bajan si el aviso de arriba las tocaría.
  - **Logro** abajo al centro, uno detrás de otro.
  - **Momentos** en franjas de lado a lado: jefe vencido y sector nuevo. Y el panel del **rango**.
- **Fondo atrás del juego:** jugando (`dibujar_partida`, `captura_del_mundo`) el fondo se dibuja `apagado` (nebulosas y planetas a `BRILLO_FONDO_JUGANDO`): un planeta naranja a pleno brillo parecía un peligro. En los menús, a pleno.
- **Transiciones:** `App.cambiar_escena(escena, transicion=True)` dibuja el barrido de rombos encima (es solo dibujo). Sin transición lo que tiene que ser instantáneo: pausar y seguir, READY → juego, la explosión y el panel F1.
- Variantes de sprites sin archivos nuevos: `recursos.tenir()` (gris + color: congelado, golpe) y `recursos.blanquear()`.

## Sprites
El usuario dibuja los sprites; Claude los integra. Todos en `sprites/`.

**Reglas para sprites nuevos:** PNG con fondo transparente, pixel art sin antialiasing, tamaño exacto y píxeles de 2x2. Colores del juego: `#FFDD00`, `#FF3246`, `#00E6FF`, `#FF00AA`, `#3CFF78`, `#8CBEFF`, `#FFFFFF` y tonos oscuros de esos. Las animaciones son una hoja horizontal de cuadros iguales sin separación. Lo que gira con la nave se dibuja mirando hacia arriba.

**Cómo se cargan** (`recursos.py`, con caché): `sprite(archivo)` devuelve `None` si no existe y quien lo pidió usa su dibujo de respaldo (`sprite_obligatorio()` solo para `nave.png`); `hoja(archivo, ancho_cuadro)`; `hoja_por_filas(archivo, lado, nombres_filas)` → `{nombre: [cuadros]}`; `cuadro_animado(cuadros, ms, desfase)` con el reloj real. Las animaciones que cambian la lógica (el choque del rebotador) usan `partida.tiempo`. Las velocidades están en `config.py` (`MS_CUADRO_*`).

### Sprites que ya existen
| Archivo | Tamaño | Cuadros | Dónde se usa | Respaldo si falta |
|---|---|---|---|---|
| `nave.png` | 50x50 | 1 | `nave.imagen("nave")` (mira hacia arriba); también los íconos de vidas (25x25) y el fantasma del dash | obligatorio |
| `perseguidor.png`, `embestidor.png` | 80x40 | 2 de 40x40 | `Enemigo.cuadros()` (por `tipo + ".png"`) | `enemigo_respaldo(color)` |
| `rebotador.png` | 320x160 | 4 filas (una por pared: abajo, arriba, izquierda, derecha) de 8 cuadros de 40x40: 0 vuela, 1-7 el choque | `Rebotador.cuadros_por_pared()`. Al chocar: secuencia `CHOQUE` = [1, 2, 2, 3, 4, 5, 6, 7] a `MS_CUADRO_REBOTE`; los primeros `PEGADO` lugares se queda quieto | `enemigo_respaldo(color)` |
| `embestidor_carga.png` | 40x40 | 1 | fase "apuntar" | parpadeo en blanco |
| `moneda_giro.png` | 120x20 | 6 de 20x20 | `moneda.imagen_moneda()` | elipse amarilla |
| `powerups.png` | 150x30 | 5 de 30x30 | cápsulas según `cuadro_sprite` (escudo 0, hielo 1, vida 2, imán 3, doble 4) | cuadro con la letra |
| `escudo.png` | 152x76 | 2 de 76x76 | la burbuja de la nave (tiene píxeles semitransparentes a propósito) | círculo cian |
| `nebulosa.png`, `planeta_chico.png`, `planeta_grande.png` | 256x192 / 32x32 / 96x96 | 1 | `Fondo` (paralaje) | no se dibujan |
| `jefe.png` | 720x120 | 6 de 120x120, de a pares: flotar, atacar, cansado | `JefeOjo` | `jefe_respaldo()` |
| `fortaleza.png` | 2304x192 | 6 de 384x192, de a pares: coraza, furia, cansado | casco de y 9 a 150; núcleo de 72x72 centrado en (192, 84) (= `caja_nucleo`); las 4 lamparitas en (x 159..225, y 132) | `fortaleza_respaldo()` |
| `fortaleza_canon.png` | 96x48 | 2 de 48x48: sano, dañado | encima del casco (los 6 px de arriba son el soporte); luz en el hueco (21, 6) de 6x6; cuelgan en x 24, 114, 222, 312, y 144 | `canon_respaldo()` |
| `divisor.png` / `divisor_mediano.png` / `divisor_chico.png` | 96x48 / 64x32 / 40x20 | 2: normal, aplastado | por `tipo + ".png"` | `slime()` |
| `enjambre.png`, `abeja.png` | 40x20 | 2 de 20x20 (alas; no giran) | `Dron`, `Abeja` | `dron_respaldo()`, `abeja_respaldo()` |
| `serpiente_cabeza.png` | 96x48 | 2 de 48x48: boca cerrada, abierta (sin ojos) | gira; los ojos (6x6) van en (15, 18) y (33, 18) | `cabeza_respaldo()` |
| `serpiente_cuerpo.png` | 64x32 | 2 de 32x32: rombo y banda (se alternan, no es animación) | segmentos (no giran) | `segmento_respaldo()` |
| `serpiente_cola.png` | 32x32 | 1 (cascabel, punta hacia arriba) | gira | `cola_respaldo()` |
| `colmena.png` | 960x160 | 6 de 160x160, de a pares: calma, furia, aturdida | las esquinas de afuera son transparentes: `COMPUERTAS` está corrida hacia adentro (x 16 y 112) | `colmena_respaldo()` |
| `singularidad.png` | 768x128 | 6 de 128x128, de a pares: girar, inhalar, expuesta | se escala al nacer y al colapsar | `singularidad_respaldo()` |
| `singularidad_asteroide.png` | 64x32 | 2 de 32x32 (dos rocas, no es animación) | el anillo (`lugar % 2`) | `asteroide_respaldo()` |

### Sprites opcionales que todavía no existen (tienen dibujo de respaldo)
| Archivo | Tamaño | Cuadros | Dónde se usa |
|---|---|---|---|
| `rebotador_vuelo.png` | 80x40 | 2 de 40x40 mientras vuela: el 1 = la columna 0 de `rebotador.png`; el 2 cambia poco (púas que laten, brillo o pestañeo: el usuario sacó el aleteo porque cambiaba la silueta) | `Rebotador.cuadros()` |
| `colmena_compuerta.png` | 64x32 | 2 de 32x32: cerrada, abierta | encima de la Colmena en (16, 30), (112, 30), (16, 98) y (112, 98) |
| `ladron.png` | 80x40 | 2 de 40x40 (violeta `#BE78FF`; un antifaz ayuda a leerlo) | `Enemigo.cuadros()`; la moneda robada va encima de su cabeza, así que arriba conviene dejar aire |
| `escudero.png` | 80x40 | 2 de 40x40 (naranja `#FF8C00`), **solo el cuerpo y sin girar**: el escudo lo dibuja el código alrededor (radio 26 a 32 px del centro) | `Enemigo.cuadros()` |

Las variantes (congelado, golpe, brillo) se generan solas: no hace falta dibujarlas. **La llama del motor son partículas y el usuario prefiere que siga así: no proponer un sprite de propulsor.** Fuera de esta lista, no proponer sprites nuevos.

## Arquitectura

### App y escenas (patrón State)
- `App` crea una vez los servicios: `ventana`, `opciones`, `sonidos`, `records`, `progreso`, `entrada`, `fondo`, `efectos` y `pantalla` (el lienzo). Atajos globales (`App._atajos()`): M silencia, F11 pantalla completa.
- `App(carpeta_datos=..., usar_mandos=..., presentacion=...)`: los tests usan `presentacion=False` y reemplazan `App.ahora()` (el reloj real).
- Cada escena hereda de `escenas/base.Escena`: `actualizar` cambia el estado o pasa a otra escena con `self.app.cambiar_escena(...)`; `dibujar` solo dibuja; `al_cerrar()` si se cierra la ventana; `tiempo_en_escena()` con el reloj real; `musica` y `ambiente` (ver "Sonido"). Escenas que guardan otra para volver a la misma instancia: `Opciones(volver_a=...)`, `Pausa(escena_juego, captura)`.
- **Flujo:** `Presentacion → Inicio → (ARCADE: Dificultad | HISTORIA: Mapa | Logros | Opciones)`, `Galaxia ⇄ Archivo`, `Galaxia ⇄ Hangar`, `Galaxia → (viaje) → [Dialogo: mensaje de Inés si pasó un año] → Dialogo (antes) → Listo → Juego → Dialogo (después) → Galaxia` (después de la misión final: `→ Final → Galaxia`); un sistema libre: `Galaxia → Listo → Juego → Dialogo (sistema despejado) → Galaxia` y `Juego → Explosion → Dialogo (Inés te saca) → Mapa`, `Dificultad → Listo → Juego ⇄ Pausa ⇄ Opciones`, `Juego ⇄ Taller`, `Juego ⇄ Gasolinera`, `Juego ⇄ Desarrollador` (F1), `Juego → Explosion → Iniciales (si entra al top 5) → Fin → Listo` (ENTER) o `→ Inicio` (ESC).
- Lo que no se deduce fácil del código de cada escena:
  - **Presentación:** el usuario eligió **sin tarjeta de estudio** y **con advertencia de fotosensibilidad**. Se saltea con cualquier tecla (`entrada.algo_apretado`). Mientras dura, prepara los giros de la nave.
  - **Inicio:** `test_inicio.py` comprueba que todo entre (power-ups, pestañas, descripciones del menú de ≤ 25 letras).
  - **Taller:** cartas gratis, solo en el nivel `MEJORA_PRIMER_NIVEL`. Lo abre Juego cuando `director.ofertas` no está vacía. El tiempo de la partida no corre.
  - **Gasolinera** (`arcade/tienda.py`, solo en el arcade): la parada después de cada jefe. **Todo se paga** con créditos (elección del usuario: sin carta de regalo). Qué servicios vende depende de la dificultad (`reglas["servicios"]`). Precios en config (`PRECIO_*`, con inflación por sector). Las descripciones de las cartas se leen unidas: si una línea termina una frase, lleva punto.
  - **Pausa:** VOLVER AL MENU pregunta (NO por defecto) y no guarda récord.
  - **Inicio:** el menú es ARCADE, HISTORIA, LOGROS, OPCIONES, SALIR (ARCADE primero: los tests que arrancan una partida aprietan ENTER en la primera opción).
  - **Dialogo:** recibe los renglones y `al_terminar` (quien la abre decide qué sigue: así no depende de ninguna escena). Música `SILENCIO` y el ambiente del sector (`app.fondo.sector`).
  - **Galaxia** (reemplazó al mapa estelar; pedido del usuario: "mundo libre, que las galaxias se puedan seleccionar como en Starfield, más lejos más difícil, y la relatividad del tiempo afectando la historia"): un mapa de 2400x640 con cámara que sigue al elegido (`VISTA`, `set_clip`). Las flechas eligen el sistema más cercano hacia ese lado (`_vecino`); ACEPTAR viaja: el vuelo dura `VIAJE_PASOS` con el reloj corriendo y al llegar pasan los años (`tiempo.pasar`), Inés manda sus mensajes y se despega (misión: `ModoHistoria(n)`; sistema libre: `ModoExploracion(id)`). No se puede ir a casa, a una misión bloqueada, a lo que la Marea se tragó o se va a tragar antes de que llegues, ni a un sistema con un peligro ambiental sin su módulo ("NECESITA ESCUDO TERMICO 1."). El ícono del módulo va al lado de cada sistema (brillante si falta) y el peligro al lado del bioma en el panel. Pone el equipo de la nave (`nave.cambiar_equipo`) y prepara sus giros en cada paso. P abre el Hangar, O el Archivo. Importa `Inicio` adentro del método (Inicio importa Galaxia). Los pasajes (al cumplir y al morir) están en `escenas/historia/pasajes.py`.
  - **Hangar:** dos pestañas. INSTALACIONES: las 6 en cartas (2 filas de 3; las cartas necesitan 200 de alto o los niveles pisan la descripción). MÓDULOS: los 4 módulos (2x2) y la Alondra en grande con la pieza del nivel siguiente titilando (`nave.armar(capas)`); abajo, qué abre o dónde está el plano. Las piezas: monedas × `PIEZAS_POR_CREDITO` y, la primera vez que se despeja un sistema, `PIEZAS_POR_PELIGRO` × peligro (medido con un bot: antes las monedas daban 240-450 piezas por partida y lo lejano no valía más).
  - **Archivo:** cuatro pestañas (REGISTROS = fragmentos; CRIATURAS, TECNOLOGÍA y FENÓMENOS = fichas) y la lista se desplaza. El reparto del texto lo hace `acomodar()` (la usa también el test de que todo entra). Los jefes dan su dibujo con `Jefe.retrato()`.
  - **Final:** dos finales según la Bitácora sin fecha (F11): "FIN" con la música `fin` o "EL PRINCIPIO" con `iniciales`.
  - **Modo desarrollador** (F1, solo si `config.MODO_DESARROLLADOR`): poner jefes, enemigos, power-ups y anomalías, invencible, gasolinera de prueba. Al usar algo, `partida.modo_desarrollador = True`: sin logros ni récord, y "MODO DEV" en el HUD. Las listas salen de los registros: un tipo nuevo aparece solo.
- **Hit-stop:** mientras `partida.congelar_frames > 0`, Juego y Explosion no actualizan ni dibujan (salvo el cuadro de impacto del golpe final). Después del golpe final, `partida.camara_lenta`. **Trampa:** la App borra las acciones en cada paso, así que durante el hit-stop Juego guarda el dash y la pausa (`dash_pendiente`, `pausa_pendiente`): si no, se perdían al encadenar perfectos.

### Partida (`partida.py`)
- Todo el estado de una partida. Los servicios le llegan por parámetro (`efectos`, `sonidos`, `entrada`, `records`, `opciones`, `progreso`: si es `None`, no se revisan logros).
- **Reglas: siempre pasar por ellas.** `sumar_puntos(base)` (DOBLE y récord), `ganar_creditos`/`gastar_creditos`, `danar_jugador(x, y)`, `recoger_powerup(...)`, `subir_nivel()`, `iniciar_jefe()`, `jefe_vencido()`, `quitar_enemigo()` y `activar(tipo, duracion)` (nunca acorta).
- **Subir de nivel = cumplir el OBJETIVO del tramo y despejar la zona** (decisión del usuario: el objetivo reemplazó a la barra de energía, que ya no existe; con la barra, al llenarse, los enemigos se iban apenas llegaban). Lo decide el Director (`_revisar_objetivo`, en cada paso) y llama a `subir_nivel()`. La Partida solo avisa: `director.al_recoger_moneda`, `al_romper(enemigo)` (dash, onda o congelado; no el dron que te choca), `al_perfecto`, `al_interceptar`. Nada cuenta con el jefe ni en el cierre del sector. Después del jefe, al terminar el cierre, el Director pasa solo al primer nivel del sector nuevo (`subir_nivel(anunciar=False)`).
- **Dash perfecto** (pedido del usuario: atravesar cualquier cosa era fácil para farmear): solo cuenta si el dash **rompe un enemigo `destruible`** o **intercepta** uno (`interceptable()`: el embestidor cargando). Una vez por dash. Otro perfecto antes de `CADENA_PERFECTOS` sube la cadena.
- **Créditos** (la plata de la gasolinera) no son puntos: gastarlos no baja el puntaje.
- **Modos de juego (patrón Strategy, `modos.py`):** `Partida(..., modo=...)` y `App.nueva_partida(modo=...)` reciben un `ModoArcade()` (por defecto) o un `ModoHistoria(numero)`. El modo responde las reglas que cambian (`primer_sector`, `ruta`, `abre_el_taller`, `propone_desafio`, `sigue_despues_del_jefe`, `hay_jefe`, `encabezado`, `guarda_records`, `cuenta_logros`), recibe los avisos (`al_empezar_tramo`, `al_llegar_jefe`, `al_vencer_jefe`, `al_recoger_moneda`, `al_romper`, `al_romper_parte`, `al_golpear_jefe` —antes del rebote—, `al_escapar_moneda`) y actualiza y dibuja lo suyo. Sin jefe (`hay_jefe()` False), al despejar el último tramo el Director cierra con "ZONA DESPEJADA" y la partida se cumple; el HUD muestra una bandera en vez de la calavera. Un tramo puede elegir su anomalía (`"anomalia"` en la ruta). `modo.empezar(partida)` va antes del Director (pone el nivel del primer sector). Si el modo no sigue después del jefe, al terminar el cierre `partida.cumplida = True`. **Qué pantalla sigue** al morir o al cumplir lo deciden los **pasajes** del modo (`escenas/pasajes.py` → `escenas/<modo>/pasajes.py`: `al_morir`, `al_cumplir`). Un modo nuevo (desafío diario, tutorial): una clase que herede de `Modo` y sus pasajes.
- **Modo historia:** una partida es una misión: empieza en su sector, sigue su ruta (`Mision.tramos`), el Taller abre en el tramo `MEJORA_TRAMO_HISTORIA`, el desafío en el tramo 2, termina al vencer al jefe (o al despejar la ruta si no tiene) y **no guarda récord ni logros** (miden el avance del arcade: empezar en el sector 5 daba "EXPLORADOR"). `partida.radio` (la cola) existe siempre; en el arcade nadie habla. La historia completa (6 misiones, 13 fragmentos, 2 finales) está en `HISTORIA.md`.
- **Renglones con condición:** `(quien, texto, "F01+!F06")`. Diálogos, radio y reacciones se filtran con lo encontrado (`mision.filtrar`): la historia reacciona a los secretos, y una pista de radio no se repite después de encontrar lo que señala.
- **La galaxia y el tiempo** (decisiones del usuario: un solo mapa, carrera contra el reloj, recompensas de mejoras, historia y atajos): `progreso.anios` es el reloj de la Umbral; la Marea llega en `MAREA_ANIOS`. Viajar cuesta `costo_viaje` (distancia × `VIAJE_ANIOS_POR_PX` con el descuento del IMPULSOR, o `PUERTA_ANIOS` por una puerta conocida, más `ESTADIA_ANIOS` y la `gravedad` del sistema). El camino directo de la historia cuesta ~3.8 años; explorarlo todo no entra (un test vigila el margen). Con la misión final cumplida el reloj se detiene. Los renglones aceptan condiciones de tiempo (`"T6"`, `"!T6"`), y el Final y la misión 5 tienen su versión tarde. El peligro de un sistema (1 a 5) sale de la distancia a la Umbral; `ModoExploracion` agranda escuadrones y velocidad por peligro, no abre el Taller ni propone desafíos, y su ruta sale de `ruta_del_sistema` (siempre la misma: el azar usa el id).
- **Los módulos** (`historia/modulos.py`; pedido del usuario: la galaxia bloqueada al principio, que se abra mejorando la nave y que se vea en la nave): los sistemas y las misiones tienen `ambiente = ("calor", 1)` y `plano`. Para entrar, el módulo de ese peligro con ese nivel (`modulos.falta`). Se fabrica con el plano y piezas (`MODULOS_PRECIOS`, medidos con una campaña simulada: `test_la_campaña_con_modulos_llega_a_tiempo`). Los planos llegan en los pasajes (`dar_plano` al cumplir una misión o despejar un sistema; cada misión da el de la siguiente). Las piezas son capas de pixel art en la grilla de 25x25 del sprite (`(pixeles, color, solo_sobre_el_casco)`) que `nave.py` pinta encima; cada equipo guarda sus imágenes y sus giros. **El modo decide qué lleva la nave** (`Modo.equipo()`: el arcade nada, la historia lo comprado) e Inicio la deja limpia.
- **Fichas del Archivo** (`historia/fichas.py`): el porqué de cada enemigo, jefe, power-up y anomalía; el `ModoHistoria` anota (cada `MIRAR_CADA` pasos) lo que está en pantalla. **Un enemigo, jefe, power-up o anomalía nuevo necesita su ficha** (lo exige un test).
- **Misiones estandarizadas (Registry + datos):** una clase por archivo en `historia/misiones/`, con `@registrar_mision` y casi todo datos: `numero`, `titulo`, `sector`, `lugar` (en el mapa), `tramos`, `jefe`, `oculta`/`requisitos`/`rama_de`, `final`, `antes`, `despues`, `radio` (momentos `tramo_1..4` y `jefe`), `fragmentos` (`Fragmento(id, nombre, texto, glifo, reaccion, oculto)`) y `secretos`. Los glifos se escriben con `glifos.escribir("ALBA")`. El mapa, el Archivo y los tests las leen del registro: una misión nueva aparece sola. `test_historia.py` comprueba el estándar (números seguidos, momentos de radio que existen, fragmentos sin repetir, cada secreto da un fragmento de su misión, textos que entran).
- **Los secretos** (decisiones del usuario: todo se resuelve dentro del juego, nunca a simple vista, todo tiene su porqué; la verdad de fondo es un bucle: "los Cantores somos nosotros"): las misiones los declaran como datos, `("moneda_grabada", "F01", {"monedas": 15})`, y cada **tipo** es una clase en `historia/secretos.py` (Registry + Template Method, como los objetivos) que escucha los avisos y suelta reliquias; cualquiera acepta `requiere` y `pista`. El `ModoHistoria` crea uno nuevo por partida. Lo encontrado se guarda **al instante** en `progreso.fragmentos` (aunque después pierdas), suena `fragmento` (A-L-B-A en Morse) y se cuenta por la radio (`Fragmento.reaccion`), sin cartel de "¡SECRETO!". Cada secreto que pide jugar distinto se midió con un bot (`bot_secretos.py` en el scratchpad; se reescribe si falta): F07 bajó de 25 a 20 monedas seguidas. **Trampa:** "quieta" es sin tocar ninguna dirección (`nave.acelerando`): empujar contra un borde también deja la velocidad en cero.
- **Textos de la historia:** en mayúsculas y sin vocales mayúsculas con tilde (Ñ ¡ ¿ sí). `test_historia.py` comprueba que cada texto entre en su caja (diálogo ≤ 4 renglones, radio ≤ 3, nombres del Archivo en su lista).
- **Mejoras:** `mejora(tipo)` dice cuántas veces se eligió; cada regla que depende de una mejora la consulta ahí (`vel_max`, `recarga_dash`, `tiempo_combo`, `puede_destruir`...). `sumar_mejora` es la regla; `elegir_mejora` es la del Taller. ESCUDO ROCE se recarga con perfectos sin escudo puesto y dura hasta el golpe (antes duraba 8 s y el usuario sentía que funcionaba una vez). DOBLE DASH es rara y desde el sector 3 (con dos dash era muy fácil).
- **Orden de `actualizar`:** tiempo → nave → ecos → corte del combo → imán → moneda → power-ups → director → enemigos → jefe (o balas sueltas) → efectos → logros (cada 30 pasos).

### Entrada (`entrada.py`)
- Teclado y mando se convierten en **acciones** (`ACEPTAR`, `VOLVER`, `PAUSA`, `OPCIONES`, `DASH`, direcciones, `PESTANA_ANTERIOR`/`SIGUIENTE` = LB/RB o Q/E). Las de un toque se consultan con `pulso(accion)`; el movimiento con `direccion()` (stick en cualquier ángulo).
- B solo vuelve (no pausa el juego). Perder el foco o desconectar el mando pausan solos (`pausa_pendiente`).
- `entrada.con_mando`: el último control que se tocó (para mostrar teclas o botones).
- El mando del usuario es un Xbox Series X en Windows: A=b0, B=b1, X=b2, Y=b3, LB=b4, RB=b5, Vista=b6, Menú=b7, cruceta=hat 0, stick=ejes 0/1.
- **Vibración** (`haptica.py`, `entrada.vibrar(nombre, fuerza)`, patrones en `config.VIBRACIONES`). **Pedido del usuario: suave y poca** (la primera versión le pareció brusca): sin gatillos, nada pasa de 0.5 (lo comprueba un test), y **no vibra lo que pasa todo el tiempo** (monedas, dash, menús).

### Entidades
- **Nave:** inercia con avance y deriva (dobla y frena enseguida), dash con buffer, dashes extra (DOBLE DASH), `cambiar_color()` para las naves del hangar.
  - **Giro tipo RotSprite** (`nave.girada`): con `rotate` directo el pixel art se rompía. Cada ángulo cuesta 2-5 ms la primera vez: **Inicio y la Presentación llaman a `nave.preparar_giros(2)` en cada paso**, así llegan calculados a la partida.
  - Choques: `caja_recoger()` (50x50) para recoger; `RADIO_NAVE` = 11 para el daño.
- **Moneda:** `lugar_para_moneda` busca lugar con `hud.posicion_libre()`, lejos de enemigos y del jefe.
- **HUD:** `hud.zonas_hud()` son las zonas donde no caen cosas. **Si el HUD cambia de lugar, actualizarlas.** Abajo a la derecha, la **ruta** (`_ruta`): el renglón "2-3  DIVISORES 2/3" (sector-tramo y `objetivo.etiqueta()`, en verde "¡CUMPLIDO!") y abajo un punto por tramo y la calavera del jefe; el camino entre el punto actual y el siguiente se llena con `objetivo.fraccion()` y destella con `director.tiempo_avance`. Abajo al centro, la barra del jefe, del asedio o de la anomalía.
- **Enemigos** (`enemigos/`, registro `TIPOS_ENEMIGO` con `@registrar_enemigo`):
  - La base resuelve la **entrada** (`entrar(partida, desde, hasta, demora)`: flecha en el borde durante la demora, después vuela `ENTRADA_ESCUADRON` ms sin lastimar), la **retirada** (`retirarse()`: vuela al borde más cercano en gris, no lastima ni se puede romper, `activo()` es False; afuera sale con `quitar_enemigo`), el congelado, los bordes, la animación y la separación. Las subclases escriben `mover()` (y si hace falta `al_aparecer()`, `al_entrar()`, `al_retirarse()`, `paso()`, `dibujar_cuerpo()`). `reaparecer()` (la "X" en un lugar al azar) queda solo para lo que no llega en escuadrón.
  - **Nada aparece de la nada ni se queda para siempre** (pedido del usuario: "la pantalla se ensucia"): un enemigo que te choca, o que se rompe con el hielo sin ser destruible, **se retira** (no reaparece). **Trampa:** lo que se suma a un escuadrón después de la orden de retirada (los hijos del divisor) también se tiene que ir: el Director repite `retirarse()` en cada paso, y `retirarse()` corta el `naciendo` (si no, el divisor recién nacido se acomodaba adentro de la pantalla y trababa el tramo).
  - Atributos de clase: `tamano`, `radio`, `destruible`, `puntos_dash`, `muere_al_chocar`, `bonus_propio` (su grupo ya tiene bonus: sin el del escuadrón), `nombre`/`pista` (la ficha de "nuevo enemigo"), `esbirro` (de un jefe), y `crear()` para los que nacen en grupo (el enjambre: una "unidad" de varios drones que entra junta y dibuja una sola flecha).
  - Avisos que la Partida le pregunta (por defecto "no"): `hace_danio()`, `interceptable()` y `bloquea_dash(x, y)` (con `al_bloquear` y `punto_de_bloqueo`). Las ondas y el ECO preguntan con `partida.puede_destruir(enemigo, desde)`: **una defensa nueva también tiene que frenarlas** (si no, ONDA rompía al escudero de frente).
  - **Ladrón** (sector 3, decisiones del usuario): no lastima; roba la moneda y huye al borde más cercano. Las reglas de la moneda robada están en la Partida (`robar_moneda`, `recuperar_moneda`, `moneda_escapada`, `soltar_moneda`); `moneda.robada_por` dice quién la tiene. Mientras la lleva, **el reloj del combo espera** (`ultima_moneda` avanza con el tiempo) y ni el imán ni la nave la pueden agarrar. Todo lo que saca a un ladrón del juego sin el dash (se retira, llega el jefe) la suelta sin castigo; si se escapa con ella, cuenta como que se escapó de su escuadrón.
  - **Escudero** (sector 4): el dash de frente rebota (`_rebotar_en_escudo`, como contra un jefe, sin daño); por el costado o la espalda lo rompe (perfecto). El escudo **se dibuja con código** en la grilla de 2 px (`celdas_del_escudo`): así gira sin romper el pixel art.
  - **Tope de velocidad:** `Enemigo.rapidez()` nunca deja que uno que te persigue sea más rápido que la nave. Los ataques con aviso (embestida, picadas) no tienen tope.
  - **Todo enemigo que sale del juego pasa por `Partida.quitar_enemigo()`.**
  - **Aturdido:** quieto y sin lastimar (ondas, ECO, intercepción). El rebotador reescribe `empujar()` (si no, quedaba quieto para siempre).
  - El embestidor fija la mira un rato antes de embestir según la dificultad (`reglas["apunte_fijo"]`, pedido del usuario): la línea deja de parpadear y es la señal para correrse.
- **Director** (`progresion.py`). El rediseño "que se sienta progresión, no una pantalla sucia" (pedido del usuario, inspirado en Metal Slug y los juegos de naves):
  - **Ruta:** cada sector = 4 **tramos** + jefe, un tramo por nivel (`numero_tramo` = `(nivel - 1) % 5 + 1`; 0 = jefe o cierre). La ruta (`rutas.py`; el modo la elige con `modo.ruta(numero_sector)`) dice por tramo `nombre`, `objetivo` (`("romper", 3, "divisor")`), `a_la_vez` y la lista de `escuadrones` `(tipo, cuantos, formacion)`. Reglas de una ruta (las comprueban `test_progresion.py` y `test_objetivos.py`): un enemigo nuevo por tramo como mucho y nunca en el asedio; el objetivo se tiene que poder cumplir con lo que trae el tramo; tramo 3 = ZONA INESTABLE (la anomalía); tramo 4 = ASEDIO (objetivo `("asedio",)`). Una misión de la historia puede traer su propia ruta con la misma forma (`Mision.tramos`).
  - **Escuadrones** (`escuadrones.py`): `lanzar_escuadron()` toma el siguiente de la cola del tramo (vuelve a empezar si se acaba), lo escala con `_cantidad()` (dificultad `reglas["escuadrones"]` y `vuelta()`) y cada miembro hace `entrar()` desde su formación. `lugares()` nunca deja a uno a menos de `LEJOS_DE_LA_NAVE` de la nave. Turno `TURNO_ESCUADRON` y se retira; roto entero (2 o más) → bonus (`_premiar_escuadron`). Suena `escuadron_llega` con paneo del lado por donde entran.
  - **Objetivos** (`objetivos.py`, Registry + Template Method como los desafíos; `crear_objetivo(datos, factor)`, la meta crece `VUELTA_OBJETIVO` por vuelta). Cumplido: festejo (`OBJETIVO_PUNTOS` × sector; el asedio tiene el suyo), no llegan más escuadrones y `despedir_escuadrones()`: se van, pero **el que ya entró se queda al menos `PERMANENCIA_MINIMA`** (pedido del usuario: "apenas llegan se van"; medido con un bot: antes 62-75 % de los que se retiraban se iban antes de 5 s, ahora 8-16 %, casi todos por chocar). Con la zona despejada (no queda ningún escuadrón) sube el nivel. **Válvula:** si en `PACIENCIA_OBJETIVO` no se cumple, "EL PASO SE ABRE" sin premio (un bot que no intercepta quedaba trabado para siempre en CARGA). `cumplir_objetivo()` lo da por cumplido (tests).
  - **Trampa:** no volver a acortar turnos al acercarse el final del tramo o del asedio: eso era lo que hacía que los enemigos se fueran apenas llegaban. Un escuadrón del asedio tiene su `ASEDIO_TURNO` entero.
  - **Asedio** (tramo 4): empieza `ASEDIO_INICIO` después, dura `ASEDIO_DURACION`, con escuadrones de `ASEDIO_TURNO` que rotan; al terminar se despiden (con la permanencia mínima) y recién con la zona despejada llega el jefe. Sin perder vidas: premio.
  - Al cambiar de tramo: los del anterior se retiran, la anomalía del tramo 3 termina, sale el cartel `TRAMO n/4` (si se ve la franja del sector nuevo, el cartel y el primer escuadrón esperan a que termine: `anuncio_en`) y Juego le pide al fondo un `acelerar()` (las estrellas pegan un tirón: se siente que avanzás).
  - Además: **sectores = biomas, uno por jefe** (`SECTORES`, en orden fijo), anomalías, desafíos (`disponible()` mira `tipos_del_sector()`), el **rango** y el **cierre del sector** (mientras dura no llega nadie ni cuenta nada para el objetivo) y las ofertas de mejoras. Al llegar el jefe, los enemigos explotan y se van (ya no se guardan). `rotulo()` = "2-3" o "2-JEFE" (HUD, Pausa, Game Over). `con_escuadrones`/`con_anomalias`/`con_desafios`/`con_mejoras = False` los apagan (los usa el fixture de los tests).
- **Dificultad:** `Partida(..., dificultad)` guarda `reglas = DIFICULTADES[dificultad]` (velocidad, cuántos trae cada escuadrón, espera de power-ups, apunte fijo, servicios de la gasolinera, vidas).
- **Jefes** (`jefes/`, registro `TIPOS_JEFE`; sale el `"jefe"` del sector):
  - **Filosofía (pedido explícito del usuario):** las peleas son un **baile con ritmo, estilo Cuphead/Dark Souls**, no una lluvia de balas. Un ataque por vez, cada uno con **aviso → ataque a ritmo → ventana para pegarle**. Pocas balas. Cada jefe con personalidad (nombre, apodo, gestos) y su propio estilo. Si se agrega uno, seguir esto. Si un ataque pega demasiado, casi siempre es un aviso que no da tiempo: alargar el aviso.
  - **Pulso:** `cambiar_fase(fase, ms, t)` / `cambiar_fase_pulsos(fase, n, t)`, y en cada paso `self.pulso` y `self.nuevo_pulso`. **Trampa:** revisar `fin_de_fase` ANTES de `nuevo_pulso` (el paso en que termina una fase también empieza un pulso: si no, sale un disparo de más).
  - La base resuelve la entrada, la cinemática de llegada (¡ALERTA! y la presentación con nombre y apodo), la vida, el congelado (solo en `fases_congelables`), la muerte, las **partes** (`Parte`: piezas golpeables con el dash; `margen_golpe` agranda solo la caja del golpe), las cajas de daño y `zonas_sin_monedas()`.
  - Los cinco: **El Ojo** (ráfagas con aviso de dirección), **Acorazado Imperial** (marcha militar, 4 cañones que se calientan; tamaño con `ESCALA`), **Devoradora de Estrellas** (jefe de movimiento, la cola es el núcleo), **Madre del Enjambre** (compuertas que sueltan abejas y después embiste con rebotes; el aviso del camino usa la misma cuenta que el movimiento) y **El Fin de la Luz** (gravedad y un anillo de asteroides con huecos).
  - **Proyectiles** (`proyectiles.py`): todos en `partida.balas`, con `mover`, `dibujar`, `radio`, `destruible`, `puntos`, `brillo` y `estela`.
- **Power-ups** (`powerups/`, registro `TIPOS_POWERUP`; el orden de `tipos.py` es el del HUD y del panel de inicio): eligen con peso según la situación (`PowerUp.peso`), `duracion` en ms, `HASTA_PERDER_VIDA` o `None` (instantáneo), y `disponible()`. La cápsula cae desde arriba.

### Servicios
- **Opciones:** cada fila es un `Ajuste` (Template Method) de la lista `AJUSTES` (`Lista`, `Interruptor`, `Volumen`). **Para agregar una opción:** sumarla a `guardado.Opciones` (fábrica, cargar, guardar) y una línea en `AJUSTES`. Nada más. LB/RB (Q/E) cambian de sección. `test_opciones.py` comprueba que todo entre.
- **Guardado:** si el archivo no existe, se crea; si está dañado, valores de fábrica; si no se puede escribir, el juego sigue.
- **Fondo:** estrellas y objetos con paralaje, salto al hiperespacio, ambiente propio de cada bioma (motas). Los tintes no pasan de ~110 por canal.
- **Logros** (`logros.py`): `Logro(id, nombre ≤16, descripcion ≤36, condicion)`. Algunos regalan una nave (`NAVES` en config). La pantalla tiene lugar para 16: con más hay que paginar.

## Sonido y música
Todo el audio pasa por `juego/sonido.py` (el servicio `app.sonidos`). **Todo sale del estudio** (`herramientas/estudio/`): un sonido nuevo se compone ahí, nunca se trae hecho. El juego no usa el estudio: solo los archivos de `efectos/`.

**Los documentos:** `MAPA_DE_AUDIO.md` tiene cada evento del juego con su código, dónde pasa y qué suena; `LISTA_DE_SONIDOS.md` tiene la partitura de cada sonido, la base musical (sección 0) y el Registro. **Antes de agregar un sonido, buscarlo ahí; al terminarlo, marcar su estado, anotar en el Registro y actualizar la columna "Hoy" del mapa.**

**La base musical (no romperla):**
- Tonalidades: juego, menú, tensión y fin en La menor; iniciales Do mayor; jefes Re menor (cada jefe tiene su tema); gasolinera Fa mayor.
- **Los premios y la interfaz se escriben en la pentatónica de Do** (C D E G A) y **siguen al acorde** que suena (ver "Armonía en vivo").
- **La tensión sale de la propia escala del tema** (en La menor el tritono Si–Fa; en Re menor Si♭, Mi–Si♭, La–Si♭). Notas de afuera solo en los raros y a propósito (la ¡ALERTA!, PESADILLA, `desafio_fallado`, la presentación del jefe). Los avisos de peligro terminan en tensión; `vulnerable` y los premios resuelven.
- Registros: la interfaz arriba, el peligro en el medio, los impactos con ruido grave.

### El mezclador (`sonido.py`)
- **Catálogo (patrón Registry):** `CATALOGO` = nombre → `Efecto(archivos, categoria, prioridad, voces, enfriamiento, volumen, paneo)`. Ayudas: `_uno`, `_variantes` (se turnan al azar sin repetir) y `_escala` (se piden por número: `moneda_1..5`). Criterios: la interfaz en INTERFAZ y al centro; avisos y ataques en PELIGRO; los grandes momentos en MOMENTO (bajan la música); lo que suena todo el tiempo en DETALLE y con enfriamiento.
- `MUSICAS` y `AMBIENTES`: nombre → archivo. `SILENCIO` es un nombre de música que no existe: deja todo callado con fundido.
- **Los archivos se buscan por nombre** en cualquier subcarpeta de `efectos/` (`ruta_del_sonido`): el catálogo no sabe de carpetas, y dos archivos no pueden llamarse igual.
- **Volumen:** general × el de su categoría (opciones) × `MEZCLA[categoria]` (config). `MEZCLA` deja margen: con todo al máximo el juego saturaba.
- **El limitador:** SDL suma los canales y recorta lo que se pasa. El mezclador sabe cuánto suena cada efecto por su **ficha** (`efectos/fichas.json`) y, si la suma pasaría de `TECHO_MEZCLA`, baja primero los DETALLE y ACCION y, si no alcanza, todo. Un archivo sin ficha engaña al limitador: por eso hay un test.
- **Armonía en vivo** (como Rez o Tetris Effect): los efectos de `ARMONICOS` (la misma lista en `sonido.py` y en `herramientas/estudio/obras/__init__.py`, un test lo comprueba) tienen un archivo por **color** (la pentatónica de cada acorde). La ficha de cada tema dice el color de cada compás; `color_actual()` calcula en qué compás va la música (descontando las pausas) y toca el archivo de ese color. Sin música, el de Do.
- **`reproducir(nombre, x=None)`:** enfriamiento → voces (corta la copia más vieja) → canal libre o le roba el suyo al menos importante → variante → paneo (si hay `x`) → los MOMENTO bajan la música (ducking). `reproducir_luego(nombre, ms)` programa uno.
- **Canales:** 0-1 música, 2-3 ambiente, 4-5 loops, 6-23 efectos. Música y ambiente con un `Tocadiscos` (dos canales para cruzar temas; un tema que vuelve empieza de cero).
- **Loops** (`tocar_loop`/`parar_loop`): **quien lo prende lo tiene que parar**, y al morir o salir de la partida, `parar_loops()`.
- **Pausa:** `pausar_todo()`/`reanudar_todo()` congelan todos los canales. Un efecto pedido después de pausar sí suena.
- **Trampas:**
  - No usar `pygame.mixer.music`: es una sola pista y `mixer.pause()` no la pausa.
  - `canal.set_volume(izq, der)` va **después** de `play()`: play lo vuelve a 1.
  - El audio se abre con `pygame.mixer.pre_init(44100, -16, 2, 512)` antes de `pygame.init()` (estéreo y poca latencia).
  - `_cache` (archivo → Sound) se comparte entre Apps: sin él los tests tardaban ~100 s más.

**Música y ambiente por escena (patrón State):** cada escena tiene `musica` y `ambiente` (atributo o propiedad); antes de cada paso la App pide ese tema. `None` = no lo cambio.

| Escena | `musica` |
|---|---|
| Inicio, Dificultad, Logros, Mapa | `"menu"` |
| Final (historia) | `"fin"` en el final de siempre, `"iniciales"` en el verdadero |
| Dialogo (historia) | `SILENCIO` (con el ambiente del sector de la misión) |
| Listo | `SILENCIO` en el READY? y la del sector desde el GO! |
| Juego | con jefe: `SILENCIO` en la ¡ALERTA!, `"jefe_<tipo>"` (o `"jefe"`) después y `SILENCIO` desde el golpe final. `SILENCIO` en el cierre del sector. `"tension"` en el nivel antes del jefe. Si no, la del sector (`"juego"`, `"juego_2"`...) |
| Gasolinera | `"gasolinera"` |
| Iniciales / Fin | `"iniciales"` / `"fin"` |
| Pausa, Opciones, Taller, Desarrollador, Explosion, Archivo | `None` |

El ambiente: el del sector en Juego y Listo (`SILENCIO` en la pelea, el cierre y al morir), `SILENCIO` en los menús, la Gasolinera y el Game Over, y `None` en Pausa, Opciones, Taller y Desarrollador. Si cambia qué suena en una escena, sumar un caso a `tests/test_musica.py` y actualizar esta tabla.

**Dónde suena cada cosa:** buscar `reproducir(` en el código (o el mapa). Los jefes declaran sus sonidos por fase (`SONIDOS_FASE`, `FASES_VENTANA` → `vulnerable`, `SONIDO_ENTRADA`) y la base los toca al cambiar de fase.

### Para agregar un efecto o un tema al juego
1. Buscarlo en `LISTA_DE_SONIDOS.md` y componerlo en el estudio (ver abajo).
2. Efecto: una línea en `CATALOGO` con su categoría, prioridad, voces y enfriamiento. Si es armónico, sumarlo a `ARMONICOS` en los dos lugares.
3. `sonidos.reproducir("nombre", x)` donde pase la cosa, **en la lógica, nunca en `dibujar`** (la x si viene de un lugar de la pantalla).
4. Tema: sumarlo a `MUSICAS` (o `AMBIENTES`) y ponerlo en la `musica` de la escena.
5. Marcarlo en `LISTA_DE_SONIDOS.md` y en `MAPA_DE_AUDIO.md`.

### El estudio (`herramientas/estudio/` + `herramientas/componer.py`)
**Pedido del usuario:** "que inspire calidad, profesionalismo; que no suene chillón, que tenga cuerpo". Estética **synthwave retro-futurista** (va con el neón y el CRT), no chiptune.
```
python herramientas/componer.py                         # todo (~20 min)
python herramientas/componer.py musica_juego moneda     # esos (y los que empiezan con "moneda")
python herramientas/componer.py ui_ --escuchar          # los compone y los hace sonar
python herramientas/componer.py --efectos               # todos los efectos, sin los temas (~10 min)
python herramientas/componer.py --lista
python herramientas/componer.py --fichas                # rehace efectos/fichas.json sin componer
```
- Por cada archivo imprime duración, volumen (LUFS), pico, **brillo** (centroide: arriba de ~2500 Hz en música o ~4000 Hz en efectos suena chillón) y estéreo. Todo es determinista (la semilla sale del nombre).
- **Dónde guarda:** en OGG, en la carpeta de la familia: la del módulo donde se compone (`CARPETA_DEL_MODULO` y `ruta_relativa()` en `obras/__init__.py`). Un armónico se compone una vez por color, en su propia carpeta. `test_cada_sonido_esta_en_la_carpeta_de_su_familia` lo comprueba.
- **Módulos:** `base.py` (notas, acordes, curvas), `sintesis.py` (`onda` sin aliasing, `adsr`, `filtrar`, `Sinte` sustractivo, `FM`, `ruido`; todo en estéreo), `bateria.py`, `procesos.py` (reverb, delay, EQ, compresor, limitador, bombeo y las medidas: `loudness`, `centroide`...), `armonia.py`, `instrumentos.py` (los presets), `obra.py` y `obras/`.
- **`armonia.py`:** 11 `COLORES` = (fundamental, forma: mayor, dominante o suspendida). `armonizar(nota, color)` lleva cada nota de la pentatónica de Do al mismo **grado** del color; una nota de afuera tira `FueraDeLaPentatonica`. Un acorde de la música sin color → `KeyError`: sumarlo a `COLORES` y a `juego/sonido.py`. El sus se cuenta desde su séptima (Mi sus4 → pentatónica mayor de Re), así se conservan los intervalos.
- **`obra.py`:**
  - `Obra(nombre, bpm, acordes, ...)`: un tema que da la vuelta sin costura (lo que se pasa del final entra por el principio, también la reverb y el delay). `objetivo` en LUFS (-14).
  - `Efecto(nombre, segundos, dinamica)`: suena una vez. `DINAMICAS` (LUFS del bloque más fuerte, contra la música a -14): pp -24, p -19, mf -15, f -12, ff -9. Más seco que un tema (cola corta) y **sin compresión ni cinta en el master**.
  - `Pista`: el instrumento y su tira de consola (volumen en dB, paneo, eq, envíos de reverb y delay, bombeo). Notación: `grilla` (tracker de semicorcheas), `acordes` (con conducción de voces), `bajo`, `arpegio`, `secuencia("G5:40 C6:90")` (ms), `barrido`, `ruido`, `golpe`.
  - El master de un tema: EQ, compresión suave, **cinta calibrada** (entra siempre con el pico en `NIVEL_CINTA`), volumen al objetivo y limitador a -1 dB.
- **`obras/`** (patrón Registry, `@obra("nombre")`, `cargar_todas()`): `musica.py`, `musica_jefes.py`, `ambiente.py` (loops de 24 s), `capas.py` (las capas de un efecto: `tono`, `deslizar`, `cuerpo`, `aire`, `explosion`, `golpe`, `clic`, `abrir_acorde`) y un módulo de efectos por familia (`efectos_interfaz`, `_juego`, `_enemigos`, `_director`, `_jefes`). `registrar_familia(prefijo, valores, fabrica)` registra variantes y escalas. `laser` es una `Obra` de 1 s (un loop; un `Efecto` se recorta y haría clic).

**Sonidos limpios: lista de verificación antes de componer** (los errores que ya se cometieron; el usuario los oyó como "saturado". Detalle y mediciones en `LISTA_DE_SONIDOS.md`, sección 0.12):
- [ ] ¿El master o una saturación depende del nivel con que llegan las pistas? Tiene que trabajar a un nivel fijo (`test_el_master_no_ensucia_un_acorde_fuerte`). Esta era la causa de fondo.
- [ ] ¿Algún acorde con dos notas a un tono o un semitono en el medio o el grave? → abrir las voces (quintas, cuartas, octavas).
- [ ] ¿Un pad o un bajo una octava abajo de un acorde cerrado? → solo la fundamental (o fundamental y quinta).
- [ ] ¿Es armónico? Los acordes con Do, Re y Sol (no cambian en ningún color); el Mi y el La solo en la melodía (sobre un acorde con séptima, La + Mi se vuelve tritono).
- [ ] ¿Suena junto a un efecto armónico (en el mismo momento o pisándolo)? → también armónico (el Taller fijo en Fa chocaba con las cartas).
- [ ] ¿Escala rápida en un instrumento con cola (cristal, campana, piano)? → arpegio con saltos: cada nota sigue sonando debajo de la siguiente.
- [ ] ¿Sierras (`PLUCK`, `LEAD_CALIDO`, `LASER`) tocando acordes en un efecto? → piano eléctrico o cristal. En la música sí pueden.
- [ ] ¿Un instrumento nuevo? Relaciones FM enteras (las inarmónicas desafinaban contra la música).
- [ ] ¿La dinámica es la justa? ff solo para los grandes momentos.
- [ ] Aire y siseos: filtros de banda en el medio-agudo, no pasa altos (llegaban a 11-13 kHz). `capas.aire` ya tiene techo a 7.5 kHz.
- `test_los_efectos_armonicos_no_apilan_notas_que_raspan` revisa los armónicos en los 11 colores. La moneda suma una capa por multiplicador del combo (para oír el combo sin mirar el HUD): `test_la_moneda_suma_capas_con_el_combo`.

**Para un sonido nuevo:** su partitura de `LISTA_DE_SONIDOS.md` (la sección 0.5 traduce los timbres) → la función con `@obra` en el módulo de su familia, en capas (tono, cuerpo, aire) → la lista de verificación → `componer.py nombre --escuchar` y mirar los números → `pytest tests/test_estudio.py`. Si es un módulo nuevo, sumarlo a `cargar_todas()` y a `CARPETA_DEL_MODULO`.

**Mezclar con números, pero que el usuario escuche al final:** además del brillo, mirar la energía por franjas (sub, graves, medios, presencia, aire), la **aspereza** (Plomp-Levelt; una nota de cristal ~0.003; en ruido no sirve) y la prueba nula (con y sin una etapa). Los scripts de medición viven en el scratchpad y se reescriben si faltan.

**Trampas del estudio:**
- libvorbis se queda sin pila en Windows (se cae sin mensaje) si recibe un tema entero: `guardar` escribe de a bloques.
- La FFT es circular: en un efecto, el ecualizador rellena 1 s de silencio a cada lado.
- El volumen relativo entre efectos sale de la dinámica de cada uno; `MEZCLA` ajusta por categoría en el juego.
- Un tema tarda ~80 s en componerse.

## Tests (`tests/`)
- `conftest.py`: drivers dummy; fixture `app` (datos en `tmp_path`, sin mandos, reloj falso `app.reloj_falso`, teclas mantenidas en `app.teclas`); fixture `partida` (sin enemigos ni escuadrones, sin power-ups, anomalías, desafíos ni mejoras, y con la moneda lejos). Para probar escuadrones: `director.con_escuadrones = True` (ver `con_escuadrones()` en `test_progresion.py`).
- `ayudas.py`: `avanzar(app, frames)`, `tecla(K)`, `boton(n)`, `jugar(partida, frames, dx, dy, dash)` (solo la lógica) e `ir_al_ajuste(app, nombre)` (en Opciones; nunca con un número fijo de flechas).
- En los tests de sonido, el fixture `pedidos` anota cada `reproducir`/`reproducir_luego`.
- Para probar que un test sirve, inyectar el error y ver que falle. **Trampa:** si el cambio deja el archivo del mismo tamaño y se restaura en el mismo segundo, Python usa el `.pyc` de la versión rota: después de restaurar, borrar los `__pycache__`.
- Para ver algo visual: un script en el scratchpad con `App(carpeta_datos=<scratchpad>)` que guarde `app.pantalla` con `pygame.image.save`. Filtrar la salida con `grep -a` ("¡" hace que grep la trate como binaria).
- Los bots de medición (créditos por sector, golpes por minuto, cuánto dura cada tramo, partida entera) viven en el scratchpad y se reescriben si faltan. Para comparar con la versión anterior: `git worktree add <scratchpad>/viejo HEAD`, correr el mismo bot ahí y después `git worktree remove`.

## Pendiente (para el "triple A")
- Lo que quedó fuera de la grilla de 2 px: los íconos de vidas y el texto MINI.
- Modo demostración o tutorial.
- Accesibilidad: cambiar los controles, modo para daltonismo, HUD más grande, modo asistido.
- Planetas variados hechos por código y música que se intensifica con el nivel.
- Contenido propuesto y no elegido: Torreta + Mina, Fantasma + Barrera + Élites, Los Gemelos, fase 2 del Ojo.
- Los módulos: falta que el usuario los pruebe (el orden en que abren el mapa, los precios, cómo se ven en la nave y si quiere un sonido propio al fabricar o al conseguir un plano; hoy `mejora_elegida`). El presupuesto de tiempo con los módulos sale de una campaña simulada, no de partidas reales.
- La galaxia libre: falta que el usuario la recorra (el presupuesto de tiempo, el peligro de cada zona, los precios del hangar) y diga si quiere un sonido propio para el viaje (hoy `nave_dash_1`) y más sistemas o ecos.
- Modo historia (beta, completo): 6 misiones, 13 secretos, el Archivo con fichas y dos finales. Falta que el usuario lo juegue y opine (la historia, los diálogos, la dificultad de cada secreto) y escuche `fragmento` y las ondas de la niebla. Ideas que siguen: un clic de radio propio (hoy `teclear`), un epílogo jugable (cruzar la puerta) y más misiones ocultas.
- Ladrón y Escudero: falta que el usuario los pruebe jugando (F1 → ENEMIGO) y escuche sus 4 sonidos, y que dibuje sus sprites si quiere. Desafío diario (semilla fija). Más logros (con paginado).
- La ruta de tramos, escuadrones y objetivos: falta que el usuario la juegue (ritmo y dificultad de cada objetivo, el asedio, las flechas y el sonido `escuadron_llega`). El festejo del objetivo usa `bonus`: se podría componer un sonido propio. El mapa entre sectores ya es la galaxia del modo historia.
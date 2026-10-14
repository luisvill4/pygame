# Caza Monedas (Pygame)

Juego arcade 2D hecho con Pygame. El jugador controla una nave que recoge monedas, esquiva enemigos y pelea contra jefes. El código está en el paquete `juego/`; `main.py` solo lo arranca. README.md tiene la guía para el usuario y explica cómo agregar enemigos, jefes y power-ups. `MAPA_DE_AUDIO.md` es el plan de sonido (ver "Sonido y música").

## Cómo ejecutar y probar
```
python main.py
python -m pytest        # ~450 tests, unos 45-100 s, sin ventana
```
- Requisitos: Python 3.12, pygame 2.6.1 y pytest (están en `requirements.txt`). Se necesita pygame ≥ 2.1.4 por `pygame.transform.grayscale`.
- **Git:** `main` tiene la versión de un solo archivo de antes del refactor (commit `9805b13`). El refactor modular se hizo en la rama `refactor-modular`. `.gitignore` deja afuera `records.json`, `config.json`, `progreso.json` y `__pycache__`.
- **Correr `python -m pytest` después de cada cambio.** Si se agrega una regla de juego, sumarle su test.

## Estructura
```
main.py                 # App().ejecutar()
juego/
  config.py             # SOLO valores: colores, paletas, "Reglas del juego", DURACION, mando
  app.py                # App: servicios, escenas y bucle de paso fijo (paso(), cuadro(ms), ejecutar())
  interpolacion.py      # Interpolador: dibujar en posiciones intermedias entre pasos de logica
  reloj.py              # LimitadorFPS: limite de FPS preciso (sleep + espera activa final)
  partida.py            # Partida: todo el estado de una partida y sus reglas
  progresion.py         # Director: presupuesto de enemigos, sectores, oleadas, anomalias, desafios y rango
  anomalias.py          # Anomalia + registro: asteroides, tormenta, niebla, oro
  desafios.py           # Desafio + registro: sin_dash, intocable, sin_ayuda, combo, cazador
  rango.py              # Bitacora del sector y calcular_rango() (S/A/B/C)
  mejoras.py            # Mejora + registro: las cartas del Taller y la gasolinera (15), sortear_mejoras()
  tienda.py             # Tienda de la gasolinera: Articulo, Carta, servicios (Sortear, EscudoDeViaje, Reparar), precios
  estadisticas.py       # Estadisticas de UNA partida (Game Over y logros)
  logros.py             # LOGROS (16, con su condicion) y revisar_logros()
  eco.py                # Eco: la copia de la mejora ECO que repite un dash
  nave.py  moneda.py  proyectiles.py (Bala, Obus, Misil, Mina, Escombro, Onda, Veneno, Meteoro)
  enemigos/  base.py (Enemigo + registro) · perseguidor · rebotador · embestidor · divisor · enjambre · abeja
  jefes/     base.py (Jefe + registro + pulso) · partes.py (Parte) · ojo · fortaleza · serpiente · colmena · singularidad
  powerups/  base.py (PowerUp, Capsula, registro) · tipos.py (los 7 power-ups, en orden)
  escenas/   base.py · presentacion · inicio · dificultad · logros · opciones · listo · juego · taller · gasolinera · pausa · desarrollador · explosion · iniciales · fin
  entrada.py  haptica.py  sonido.py  ventana.py (escala y pone el CRT)  guardado.py  recursos.py
  dibujo.py   efectos.py  fondo.py   hud.py
  accesibilidad.py      # lo que el jugador puede suavizar (temblor, destellos, CRT): los efectos preguntan aca
  interfaz.py           # el kit de interfaz: panel, titulo, menu (con Cursor), ayudas/boton, pestanas, carta...
  transicion.py         # Transicion: el barrido de rombos entre pantallas
  avisos.py             # Aviso + ColaDeAvisos: los carteles de arriba salen de a uno (solo logica)
  carteles.py           # el dibujo de los carteles: pancarta, fichas, logro, momentos (franjas) y rango
  impactos.py           # el dibujo de los momentos de impacto: cuadro de impacto del golpe final, vineta de herida y de ultima vida
herramientas/
  componer.py           # compone musica y efectos con el estudio (python herramientas/componer.py [nombres] [--escuchar])
  estudio/              # el estudio: base, sintesis, bateria, procesos, instrumentos, obra, obras/ (ver "El estudio")
tests/                  # conftest.py (fixtures app/partida), ayudas.py, test_*.py
sprites/ efectos/ fuentes/   # recursos (ver "Sprites"); efectos/ son los sonidos y la musica:
efectos/                # todo OGG, por familia (la del modulo del estudio donde se compone):
  fichas.json           #   cuanto suena cada archivo (lo escribe el estudio; lo lee el mezclador)
  musica/ ambiente/     #   los temas y los loops de cada sector
  interfaz/ juego/ enemigos/ director/ jefes/   # los efectos (efectos_interfaz.py -> interfaz/...)
    moneda_1/           #   un efecto ARMONICO va en su carpeta con un archivo por color (moneda_1_fa.ogg...)
records.json            # top 5 POR DIFICULTAD: {"FACIL": [{"nombre", "puntos"}...], "NORMAL": [...], ...}
                        # (un archivo viejo con una sola lista pasa a ser la tabla de NORMAL)
config.json             # {"resolucion", "fps", "volumen", "volumen_musica", "volumen_efectos" (0-10), "silencio",
                        #  "audio_mono", "latido", "aviso_jefe", "vibracion",
                        #  "crt", "neon", "escalado", "temblor", "destellos", "dificultad"}
progreso.json           # {"logros": [ids], "nave": "CIAN", "partidas": n}  (guardado.Progreso)
```

**Frecuencia: paso fijo (fixed timestep) + interpolación.**
- **La lógica avanza siempre en pasos de 1/60 s** (`PASOS_POR_SEGUNDO`, `MS_POR_FRAME`). Todo lo que en `config.py` dice "por frame" es por paso.
- **Se dibuja a `opciones.fps`** (`FRECUENCIAS` = 30, 60, 90, 120, 144 y 0 = SIN LIMITE). El juego va a la misma velocidad a cualquier FPS, y hay un test que lo comprueba.
- `App.ejecutar()`: `LimitadorFPS.esperar(fps)` → `cuadro(ms)`. Este suma `ms` a `acumulado` (como mucho `ATRASO_MAXIMO`), corre los pasos que tocan, calcula `fraccion = acumulado / MS_POR_FRAME` y dibuja. `paso()` hace exactamente un paso y un cuadro (lo usan los tests).
- **Reglas para no romperlo:**
  - En `actualizar()` va **todo** lo que cambia el estado, incluido `mover_fondo()`, el descuento del temblor y el destello y el sorteo de cuánto se corre la imagen (`Efectos.desplazamiento`, en `Efectos.actualizar`: así tiembla igual a cualquier FPS), y el marcador que cuenta (`puntaje_visible`).
  - `dibujar()` solo dibuja, porque puede correr varias veces o ninguna por paso.
  - La entrada se acumula (`procesar`) hasta que un paso la usa (`consumir`); así no se pierden teclas.
  - Lo que se mueve tiene `x`/`y` y está en `Partida.objetos_que_se_mueven()` (o en el `Fondo`). Así se dibuja interpolado con `Interpolador`, que no interpola saltos de más de 80 px (reapariciones).
Las rutas pasan por `config.ruta()`, relativas a la carpeta raíz.

**Pantalla (solo 16:9):** el juego se dibuja en un lienzo de `ANCHO` x `ALTO` = 1066x600 (`config.py`). El modo 4:3 se eliminó a pedido del usuario (antes `lienzo.py` cambiaba el ancho entre 800 y 1066).
- **Nunca escribir el ancho a mano.** Se usan `ANCHO` y `CENTRO_X` de `config.py`.
  - Lo de la izquierda se ancla a x=20, lo de la derecha a `ANCHO - 20` y lo central a `CENTRO_X`.
- **Los menús usan todo el ancho** (Inicio, Opciones, Pausa, Taller, Gasolinera, Dificultad, Logros, Iniciales y Fin, con `ANCHO`/`CENTRO_X`). Solo el panel de desarrollador sigue en `dibujo.zona_central(pantalla)` (una subsuperficie de 800x600, `ANCHO_MENU`, centrada). La estación de la Gasolinera se dibuja en su propia imagen de 800 de ancho (sus coordenadas de siempre) y se pega centrada.
  - `texto_3d` y `oscurecer` usan el tamaño de la superficie que reciben.
- **La grilla de píxeles de arte (`PIXEL_ARTE` = 2):** todos los sprites están dibujados con píxeles de 2x2 del lienzo (medido: sus tramos de color miden 2, 4, 6...). **Todo lo demás se alinea a esa grilla** (pedido del usuario: el neón "tenía más píxeles que los sprites" y no calzaba con el CRT; el halo estaba corrido 1 px):
  - `dibujo.en_grilla(valor)` y `dibujo.pegar(pantalla, imagen, x, y, centrado)`: **todo sprite se pega con `pegar`** (enemigos, jefe vía `posicion_dibujo`, nave, moneda, cápsulas, eco, fondo).
  - Halos (el bloque del centro sobre el píxel de arte de (x, y)), partículas (tamaños pares), estelas, ondas de choque (un anillo de bloques, no `draw.circle` que tiene escalones de 1 px), la `Bala` (cruz de 5x3 y 3x5 píxeles de arte), estrellas (2 px; las lejanas más oscuras), barras del HUD (bloques de 4 con 2 de aire, adentro del marco a 4 px) y el texto (`texto()` lleva la esquina a la grilla). `zona_central` y la estación de la Gasolinera usan un margen par.
  - `test_efectos_visuales.py::test_todo_calza_en_la_grilla_de_pixeles_de_arte` dibuja en lugares impares y comprueba que todo cambio de color caiga en coordenadas pares. Quedan fuera solo los íconos de vidas (la nave a la mitad: píxeles de 1) y el texto MINI (fuente de 8: píxeles de 1).
- **CRT:** lo pone `Ventana.mostrar()` DESPUÉS de escalar (antes cada escena llamaba a `efecto_crt` en el lienzo; la captura de la Pausa además las duplicaba). Una capa blanca con filas grises que se multiplica (`BLEND_RGB_MULT`, ~0.3 ms en 1080p) con **UNA línea al pie de cada fila de píxeles de arte**: cada píxel de los sprites lleva su línea, como en una pantalla de verdad. Con escala no entera (1.8x) una fila ocupa 3 o 4 filas de la ventana: `pies_de_las_filas()` le pregunta al mismo escalador dónde termina cada una (una tira con cada fila de otro color). Grosor `round(escala * PIXEL_ARTE * 0.3)` (mínimo 1). Las escenas NO dibujan el CRT. `test_opciones.py` lo comprueba pintando cada fila de arte de otro tono.
- **ESCALADO SUAVE** (opción de VIDEO; `accesibilidad.escalado_suave()`): `Ventana._escalar_parejo` agranda sin suavizar al múltiplo entero de arriba (`self._grande`) y achica con `smoothscale` ("sharp bilinear"): con escala no entera (1.8x en 1080p), todos los píxeles llevan la misma luz. ~6 ms en 1080p (NITIDO ~1 ms). `test_efectos_visuales.py` lo comprueba midiendo la luz de rayas de 1 px.
- **La ventana escala directo sobre sí misma** (`transform.scale(lienzo, tamaño, subsuperficie)`: ~1 ms en vez de ~3.5 ms en 1080p; si el formato de píxel no coincide, `ValueError` y se copia como antes). Las barras negras se pintan una vez por ventana (`_zona_del_juego`).
- `App.abrir_ventana()` abre la ventana con `opciones.resolucion`; si no existe en `RESOLUCIONES` (un `config.json` viejo de 4:3) o no entra en el monitor, usa la primera. Un `"formato"` viejo en `config.json` se ignora.

## El usuario y el estilo del código
- **Todo en español**: la conversación, los nombres de variables, funciones y clases, y los comentarios. El usuario escribe en español informal.
- **El usuario está aprendiendo.** Pidió explícitamente una arquitectura modular y escalable, y eligió el nivel "modular con clases": clases base, registros y escenas, **sin** type hints ni dataclasses ni bus de eventos. Mantener ese nivel. El código tiene que poder leerlo alguien que aprende: nombres claros, métodos cortos y comentarios que explican el "por qué" y los patrones (State, Registry, Template Method).
- Cualquier número que el usuario pueda querer tocar va en `config.py`, en la sección "Reglas del juego" (o en `DURACION`).
- Dependencias sin ciclos: `config` ← `recursos`/`dibujo` ← entidades ← `partida` ← escenas ← `app`. Las entidades reciben `partida` como parámetro (no la importan).

## Estilo visual: arcade retro (el usuario lo aprecia mucho, no romperlo)
- Fuente Press Start 2P, siempre con `antialias=False`, en tamaños múltiplos de 8: `dibujo.MINI/CHICA/MEDIA/GRANDE/TITULO` = 8/16/24/40/56 (MINI solo para textos de apoyo, nunca para información que haya que leer jugando: por accesibilidad, el desafío del HUD pasó de MINI a CHICA).
  - `dibujo.texto(pantalla, mensaje, tamaño, color, x, y, sombra, alinear, contorno)` recibe el tamaño como número. Con `contorno` (un color oscuro, `CONTORNO`) lleva un borde de un "píxel de la fuente" (`tamaño // 8`): **todo lo que va encima del juego lo lleva** (el HUD usa su propio `texto()` que lo agrega solo; textos flotantes, el "+5" de los congelados). `texto_3d(..., contorno)` rodea toda la pila del relieve.
  - Cada texto se arma una vez (letras + sombra + contorno) y se guarda en `dibujo._textos` (se vacía al pasar `MAXIMO_TEXTOS`): dibujarlo es un solo blit. `recursos.fuente(tamaño)` guarda las fuentes.
- **Colores con un papel fijo** (sección "Interfaz y accesibilidad" de config): `TEXTO`, `TEXTO_SUAVE`, `TEXTO_APAGADO`, `RESALTADO`, `CONTORNO`, `LINEA_APAGADA`, `FILA_ELEGIDA`. Lo nuevo de la interfaz usa estos, no colores sueltos.
- **Kit de interfaz** (`interfaz.py`, pedido del usuario: "que parezca un triple A"; toda pantalla nueva se arma con esto):
  - `panel(pantalla, rect, color, titulo=None, alfa)`: fondo `PANEL_FONDO`, borde fino del color apagado, escuadras brillantes en las esquinas y, con título, una franja con el nombre y rayitas inclinadas. Devuelve el rect de adentro.
  - `titulo(pantalla, mensaje, x, y, color, relieve, alinear, tamano)`: título con relieve y una raya de color debajo. `renglon(pantalla, partes, tamaño, centro_x, y)`: un renglón centrado de varios colores. `separador(...)`.
  - `menu(pantalla, opciones, cursor, x, y, ancho, alto_fila, tamano, color, apagadas, iconos)`: lista vertical; la elegida tiene franja y **la nave del jugador como cursor**, que se desliza (`Cursor`: `ir_a`, `saltar_a`, `avanzar()` en `actualizar`, así anda igual a cualquier FPS).
  - `ayudas(pantalla, entrada, [(accion, texto)...], extra)`: la barra de abajo (40 px) con los botones **del último control que se tocó** (`entrada.usando_mando()`): `GLIFOS` = accion → (teclas, botones). `boton(pantalla, glifo, x, y)` dibuja A/B/X/Y redondos con sus colores (`COLORES_BOTON`), LB/RB, MENU, VISTA, la cruceta (`CRUZ_V`/`CRUZ_H`) o una tecla (con flechas dibujadas). Si `extra` no entra sin pisar los botones, no se dibuja.
  - `pestanas(pantalla, rect, entrada, nombres, actual, color, color_fondo)`: las pestañas de `dibujo` con el botón para cambiar en cada punta (LB/RB o Q/E).
  - `carta(pantalla, rect, color, icono, nombre, lineas, elegida, apagada, rara, nivel)`: la carta de mejora (arte con rayas e ícono grande, nombre, descripción, cinta RARA, cuadraditos de nivel; la elegida con borde que late). Devuelve el rect de abajo (precio o etiqueta). La usan el Taller y la Gasolinera.
  - `pixelado(imagen, factor, oscuridad)`: el fondo de Pausa, Taller y Desarrollador. Se usa con `Escena.captura_del_mundo(partida)` (fondo + mundo, sin HUD: el HUD pixelado parecía basura).
- **Componentes de `dibujo`** (usarlos en vez de dibujar a mano, así todo se ve igual): `pestanas(pantalla, rect, nombres, actual, color, color_fondo, enfocada)` (el espacio sobrante se reparte igual; con el foco la actual se invierte, sin parpadeo), `barra(pantalla, rect, fraccion, color, borde=GRIS)` (bloques de 4 px; `borde=None` = finita sobre un riel oscuro), `barra_segmentos(pantalla, rect, llenos, total, color, destacado)` (uno por golpe; el `destacado` sale blanco), `partir_lineas(mensaje, tamaño, ancho)` y `flecha(...)`.
- Colores neón definidos como constantes en `config.py` (`AMARILLO`, `CIAN`, `MAGENTA`, `ROJO`…). Números con 6 dígitos (`dibujo.numero_arcade`).
- Partículas (`efectos.Efectos`): cuadrados alineados a una cuadrícula de 2 px. Pueden tener `gravedad`; `pedazos()` la usa para trozos que saltan y caen. No se desvanecen con transparencia: cambian de color por etapas según una **paleta**, una lista que va de oscuro a brillante (`FUEGO`, `ORO`, `ESCARCHA`…).
- **Carteles que no tapan el juego** (pedido del usuario: los carteles le tapaban monedas y enemigos): todo cartel o ficha del HUD se dibuja con `hud._cartel(pantalla, partida, nombre, funcion, *datos)`. La función dibuja en una capa transparente del tamaño de la pantalla; `_zona_dibujada()` busca qué ocupó (con la capa achicada 8 veces por `smoothscale`: `get_bounding_rect()` tardaba 2 ms) y, si esa zona + `CARTEL_MARGEN` toca algo de `cosas_que_importan(partida)` (nave, moneda, cápsula, enemigos, balas, jefe), se pega con opacidad `CARTEL_ALFA_TAPANDO` y sigue así `CARTEL_ESPERA_TAPANDO` ms (reloj real) para no titilar. Cuesta ~0.5 ms por cartel visible. **Trampa:** para volverla opaca se usa `set_alpha(255)`; `set_alpha(None)` le saca la transparencia por píxel y el cartel sale sobre un recuadro negro. Un cartel nuevo tiene que pasar por `_cartel()`. Los momentos (jefe vencido, rango, sector) pasan `alfa_tapando=CARTEL_ALFA_MOMENTO` (150): ahí no hay peligro y con 70 el gran momento quedaba apagado cada vez que la moneda pasaba por debajo.
- **Carteles del juego** (`carteles.py`, pedido del usuario: "que parezca un triple A"; antes eran texto suelto con el marco doble viejo, se apilaban "¡OLEADA!" y "NIVEL 2" y casi siempre salían apagados en el centro). Tres tamaños, cada uno en su lugar:
  - **Avisos** (`pancarta`, arriba al centro, `Y_PANCARTA` 112): NIVEL n (con cuánto falta para el jefe: "JEFE EN 3 NIVELES" / "PROXIMO NIVEL: ¡JEFE!"; en el nivel del jefe no sale), ¡OLEADA! (con cinta de peligro), ¡OLEADA SUPERADA!, cada anomalía con su consejo y ¡NUEVO RECORD! (arcoíris: `color=None`). **Salen de a uno** por `partida.avisar(Aviso(etiqueta, titulo, subtitulo, color, duracion, alerta), urgente)` → `ColaDeAvisos` (`avisos.py`, patrón Cola): el que llega espera; los **urgentes** (oleada, anomalía) se cuelan adelante y el que se veía se va en `SALIDA_RAPIDA`. `iniciar_jefe()` vacía la cola. Duraciones `AVISO_*` en config. Ancho entre `ANCHO_PANCARTA` (352, entra entre las dos fichas con su raya) y 640; el título va GRANDE si entra y si no MEDIA. Se abre (raya desde el centro → caja que baja → contenido), el título cae y nace blanco y el subtítulo se escribe solo (18 ms por letra).
  - **Fichas** (`ficha_nuevo_enemigo` a la izquierda, `ficha_desafio` a la derecha, `Y_FICHAS` 112, `DURACION_FICHA`): entran desde su lado, raya de color del lado de donde vienen, hueco con el dibujo, pestañita con la categoría. Si el aviso de arriba las tocaría (con su raya de afuera, `SALIDA_RAYA`), **bajan** de a poco mientras se abre (`caja_pancarta()`).
  - **Logro** (`logro`, abajo al centro, `Y_LOGRO` 464): primero la insignia con el trofeo, se abre hacia los costados y se escribe; si regala una nave (`nave_del_logro`, de `NAVES`), una pestañita "NAVE NUEVA: X" en su color. Uno detrás de otro (`fichas_logro`).
  - **Momentos** (franjas de lado a lado en y 300, como la llegada del jefe): `jefe_vencido` (el nombre del jefe en su color; "¡JEFE VENCIDO!" entra desde la izquierda y "BONUS +n" desde la derecha: la presentación al revés; usa `partida.ultimo_jefe`/`bonus_jefe`) y `sector_nuevo` (`CARTEL_SECTOR`; el nombre se escribe de a una letra con un cursor y después el lema; sale al volver de la Gasolinera, con el hiperespacio).
  - **Rango** (`rango`, `RANGO`): un `interfaz.panel` "SECTOR n COMPLETO" que se abre desde el centro; filas de a una (cada estrella nace blanca), el total de ESTRELLAS y la medalla con "?" hasta `RANGO_SELLO`: ahí cae la letra al doble (80 ms), destella (no con DESTELLOS REDUCIDOS) y sale un anillo cuadrado. `COLOR_RANGO` vive acá (lo usa el Game Over).
  - Piezas comunes: `texto` (con contorno; el HUD lo usa), `fondo` (semitransparente en la capa o en la pantalla), `raya` (sigue por afuera en dos escalones), `etiqueta` (pestañita), `rayitas`, `cinta` (de peligro, en escalones de 2 px) y `franja` (la usan también READY y la llegada del jefe), `apertura`/`suave`/`deslizar` para abrir, cerrar y deslizar. Todo en la grilla de 2 px (lo comprueba `test_carteles.py`).
- Efectos disponibles:
  - en `dibujo`: parpadeos duros (`parpadeo`), texto con relieve (`texto_3d`), marcos de doble línea (`marco`), arcoíris (`color_arcoiris`, un color cada `ARCOIRIS_MS`), `oscurecer` y `pixel_art(pantalla, filas, x, y, color, tamano_pixel)` (dibujos de "X" y ".": iconos de mejoras, trofeo, tilde, candado);
  - en `Efectos`: temblor en pasos de 2 px que se calma los últimos `CALMA_TEMBLOR` pasos y destello de color (`sacudir`, `dibujar_temblor_y_destello`, que usa `pantalla.scroll`).
- **Transiciones** (`transicion.py`): `App.cambiar_escena(escena, transicion=True)` guarda la imagen vieja y `_dibujar` pinta encima un barrido de rombos `FONDO` en diagonal (`TRANSICION_MS`, reloj real): la primera mitad tapan la vieja, la segunda destapan la nueva. Es solo dibujo (la escena nueva ya corre). **Sin transición** (`transicion=False`) lo que tiene que ser instantáneo: pausar y seguir, READY → juego, la explosión y el panel F1.
- **Capas de dibujo de la partida** (`Escena.dibujar_partida`): fondo → mundo (`partida.dibujar`, interpolado) → temblor y destello → HUD (`partida.dibujar_hud`). El temblor y el destello mueven y tiñen el mundo, **nunca el HUD**. `Partida.dibujar` ya no dibuja el HUD.
- **Neón** (opción NEON de VIDEO, `accesibilidad.fuerza_neon()`; pedido "que parezca un triple A"): un resplandor **solo en lo que es energía**, no en toda la pantalla (un bloom general lavaba el pixel art gris de los jefes). `dibujo.halo(pantalla, x, y, radio, color, fuerza)`: tres anillos pixelados (de a 2 px) que se SUMAN (`BLEND_RGB_ADD`), guardados en `_halos` por (radio, color, nivel de 4). `dibujo.resplandor_rect(...)` para el láser de la Fortaleza. Lo usan: cada proyectil (`brillo`, clase; None = no brilla, ej. `Escombro`), la moneda (late, y cada `DESTELLO_CADA` destella una `ESTRELLITA`), las cápsulas y las chispas grandes (`Efectos.dibujar`, hasta `MAXIMO_RESPLANDORES`). Medido: no cambia el tiempo de dibujo (~3 ms con 280 partículas).
- **Proyectiles por capas** (`dibujar_balas`): resplandores → estelas (`estela`, clase: dos cuadraditos detrás según la velocidad; sin estela la `Mina` y la `Onda`) → proyectiles.
- **Ondas de choque** (`Efectos.onda_de_choque(x, y, radio, color, pasos)`, `OndaDeChoque`): un anillo que crece frenando, blanco → su color → oscuro, de 4 y después 2 px. En: enemigo roto con el dash, dash perfecto (más grande con la cadena), power-up, escudo roto, vida perdida, NOVA/ONDA (marca el radio), golpe al jefe (en `jefe.color`), parte golpeada y la explosión final (dos). `Efectos.fogonazo(x, y, color)`: el destello donde nace cada bala de un jefe (`Partida._actualizar_jefe` mira las balas nuevas, hasta 6 por paso).
- **Textos flotantes** (`Efectos.texto_flotante`): nacen blancos `BLANCO_TEXTO` pasos, suben frenando (`SUBIDA_TEXTO`, `FRENO_TEXTO`), se apagan en dos etapas de color (sin titilar) y llevan contorno. Nunca se pisan: al nacer se apilan arriba del que está (o abajo si no entran) y al moverse cada uno frena debajo del que tiene encima. Siempre adentro de `ZONA_TEXTOS` (fuera del HUD y de los bordes).
- **Accesibilidad** (`accesibilidad.py`; la App le pasa sus opciones): `temblor_maximo()` (`NIVELES_TEMBLOR`: NO/SUAVE/NORMAL), `destellos_reducidos()` (sin destello de pantalla completa, `parpadeo()` nunca más rápido que `PARPADEO_MINIMO` = menos de 3 por segundo, arcoíris a `ARCOIRIS_REDUCIDO`, el relámpago del Carmesí no titila) y `brillo_crt()`. **Un efecto nuevo que tiembla, destella o parpadea tiene que pasar por acá** (o por `parpadeo()`/`color_arcoiris()`, que ya lo hacen).
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
- `hoja_por_filas(archivo, lado, nombres_filas)`: una animación por fila (por ejemplo, una por dirección) → `{nombre: [cuadros]}` (o `None`). Toda animación es "lista de cuadros + ms por cuadro": las que se repiten usan `cuadro_animado` (reloj real); las que pasan una vez y cambian la lógica (el choque del rebotador) usan `partida.tiempo`.
- `cuadro_animado(cuadros, ms_por_cuadro, desfase)` elige el cuadro según el reloj real.
- Las velocidades de las animaciones están en `config.py`: `MS_CUADRO_ENEMIGO`, `MS_CUADRO_MONEDA`, `MS_CUADRO_ESCUDO`, `MS_CUADRO_JEFE` y `MS_CUADRO_REBOTE`.

### Sprites que ya existen
| Archivo | Tamaño | Cuadros | Dónde se usa | Respaldo si falta |
|---|---|---|---|---|
| `nave.png` | 50x50 | 1 | `nave.imagen("nave")` (mira hacia arriba); también `"icono"`/`"icono_vacio"` (vidas del HUD, 25x25) y `"fantasma"` (dash) | obligatorio |
| `perseguidor.png`, `embestidor.png` | 80x40 | 2 de 40x40 | `Enemigo.cuadros()` (por `tipo + ".png"`); el perseguidor también es el ícono "ESQUIVA" en Inicio | `enemigo_respaldo(color)`: cuadrado con dos ojos |
| `rebotador.png` | 320x160 | 4 filas de 8 cuadros de 40x40, una fila por pared (abajo, arriba, izquierda, derecha): 0 vuela (igual en las 4 filas), 1-7 el choque contra esa pared | `recursos.hoja_por_filas()` → `Rebotador.cuadros_por_pared()`. Al rebotar: estado "choque", secuencia `CHOQUE` = [1, 2, 2, 3, 4, 5, 6, 7] a `MS_CUADRO_REBOTE` (70) cada uno = 560 ms, con `partida.tiempo` (es lógica); los primeros `PEGADO` (4 lugares = columnas 1-3, 280 ms) se queda quieto (`paso()` = 0). Otra pared en medio reinicia el choque. Volando: `cuadros()` (ver `rebotador_vuelo.png`; sin él, la columna 0 quieta) | `enemigo_respaldo(color)` en todas las paredes |
| `embestidor_carga.png` | 40x40 | 1 | `Embestidor.dibujar_cuerpo()` en la fase "apuntar" | parpadeo con el primer cuadro en blanco |
| `moneda_giro.png` | 120x20 | 6 de 20x20 | `moneda.imagen_moneda()` (en el juego y en Inicio) | elipse amarilla que se angosta |
| `powerups.png` | 150x30 | 5 de 30x30 | `PowerUp.dibujar_capsula()` según `cuadro_sprite` (escudo 0, hielo 1, vida 2, imán 3, doble 4). Turbo y recarga no tienen | cuadro con la letra |
| `escudo.png` | 152x76 | 2 de 76x76 | burbuja en `Nave.dibujar()`. Tiene píxeles semitransparentes (el brillo); está bien así | círculo cian |
| `nebulosa.png`, `planeta_chico.png`, `planeta_grande.png` | 256x192 / 32x32 / 96x96 | 1 | `Fondo` (paralaje) | no se dibujan |
| `jefe.png` | 720x120 | 6 de 120x120, de a pares: flotar, atacar, cansado | `JefeOjo.cargar_animaciones()`; `Jefe.animaciones()` arma las variantes congelada y blanca. Con 2 cuadros se usan para todo | `jefe_respaldo(color_nucleo)` |
| `fortaleza.png` | 2304x192 | 6 de 384x192, de a pares: coraza, furia (núcleo rojo), cansado (núcleo amarillo, casco roto) | `Fortaleza.cargar_animaciones()`. Casco de y 9 a 150, núcleo centrado en (192, 84) de 72x72 (coincide con `caja_nucleo`); las 4 lamparitas del compás se dibujan encima, en el panel oscuro de abajo (x 159..225, y 132) | `fortaleza_respaldo(...)` |
| `fortaleza_canon.png` | 96x48 | 2 de 48x48: sano, dañado (caño hacia abajo) | `cuadros_canon()`; se dibuja ENCIMA del casco (sus 6 px de arriba son el soporte). La luz de color va en el hueco oscuro (21, 6), de 6x6. Cuelgan en x 24, 114, 222 y 312, y 144. El cañón roto (muñón) lo dibuja el código | `canon_respaldo(danado)` |
| `divisor.png` / `divisor_mediano.png` / `divisor_chico.png` | 96x48 / 64x32 / 40x20 | 2 cada uno: normal, aplastado (apoyados abajo) | `Enemigo.cuadros()` por `tipo + ".png"` (el grande es `divisor`; el usuario lo había llamado `divisor_grande.png`: se renombró) | `slime()` |
| `enjambre.png` | 40x20 | 2 de 20x20: alas abiertas, cerradas (no gira) | `Dron` | `dron_respaldo()` |
| `abeja.png` | 40x20 | 2 de 20x20: alas arriba, abajo (no gira) | `Abeja` | `abeja_respaldo()` |
| `serpiente_cabeza.png` | 96x48 | 2 de 48x48: boca cerrada, abierta (mirando hacia arriba, SIN ojos) | `cuadros("cabeza", ...)`, gira. Ojos y lengua se dibujan aparte: los ojos (6x6) caen en las cuencas oscuras de (15, 18) y (33, 18) | `cabeza_respaldo()` |
| `serpiente_cuerpo.png` | 64x32 | 2 de 32x32: rombo y banda (dos dibujos que se alternan a lo largo del cuerpo, no es animación) | segmentos (no giran) | `segmento_respaldo()` |
| `serpiente_cola.png` | 32x32 | 1 (el cascabel, punta hacia arriba) | gira y se sacude cuando brilla (`tenir` amarillo) | `cola_respaldo()` |
| `colmena.png` | 960x160 | 6 de 160x160, de a pares: calma, furia, aturdida | `Colmena.cargar_animaciones()` (el ojo de la reina va en el sprite). Hexágono con puntas a los costados: las esquinas de afuera son transparentes, por eso `COMPUERTAS` está corrida hacia adentro (x 16 y 112) | `colmena_respaldo()` |
| `singularidad.png` | 768x128 | 6 de 128x128, de a pares: girar, inhalar, expuesta | `Singularidad.dibujar_cuerpo()`; se escala al nacer y al colapsar | `singularidad_respaldo()` |
| `singularidad_asteroide.png` | 64x32 | 2 de 32x32 (dos rocas distintas, no es animación; no giran) | el anillo (`lugar % 2`) | `asteroide_respaldo()` |

### Sprites opcionales que todavía no existen (tienen dibujo de respaldo)
Variantes (congelado, golpe, recalentado, brillo) se generan solas con `tenir`/`blanquear`: no hace falta dibujarlas.

| Archivo | Tamaño | Cuadros | Dónde se usa |
|---|---|---|---|
| `rebotador_vuelo.png` | 80x40 | 2 de 40x40 mientras vuela (el 1 = la columna 0 de `rebotador.png`; el 2 cambia poco: púas que laten, brillo o pestañeo. El usuario sacó el aleteo viejo porque cambiaba la silueta y se movía de más) | `Rebotador.cuadros()` → `dibujar_animado` a `MS_CUADRO_ENEMIGO` (también HUD, congelado y parpadeo al nacer) |
| `colmena_compuerta.png` | 64x32 | 2 de 32x32: cerrada, abierta | `cuadros_compuerta()`; van encima de la Colmena en (16, 30), (112, 30), (16, 98) y (112, 98). La compuerta rota (agujero que gotea) la dibuja el código |

La llama del motor son partículas (`Efectos.estela()`), y el usuario prefiere que siga así: no proponer un sprite de propulsor. Los enemigos congelados se generan con `tenir(..., HIELO)`. Fuera de esta lista, no proponer sprites nuevos.

- **Trampa:** en Press Start 2P la "É" mayúscula se dibuja como "é" pequeña. Por eso se escribe "RECORD" sin tilde. "¡", "¿", "Ñ" y los números funcionan bien.
- **Trampa:** en este Windows `SysFont("Arial")` carga **Arial Narrow**.

## Arquitectura

### App y escenas (patrón State)
- `App` crea una sola vez los servicios: `ventana`, `opciones`, `sonidos`, `records`, `progreso`, `entrada`, `fondo`, `efectos`, más `pantalla` (el lienzo de 1066x600). Al arrancar aplica el color de la nave elegida (`nave.cambiar_color`).
- **Atajos globales** (`App._atajos()`, antes de cada paso de la escena): M (`SILENCIO`) da vuelta `opciones.silencio` (calla todo sin tocar los volúmenes); F11 (`PANTALLA_COMPLETA`) pasa a "COMPLETA" y vuelve a la ventana de antes (`ventana_antes`). Los dos guardan las opciones y muestran un aviso chico (`App.avisar()`, dibujado encima de todo por `_dibujar_aviso`).
- Un paso de lógica es `escena.actualizar(entrada)` + `entrada.consumir()`. Un cuadro es `escena.dibujar(pantalla)` + `ventana.mostrar(pantalla)`. `cuadro(ms)` corre los pasos que tocan y un cuadro; `ejecutar()` lo repite con `LimitadorFPS` (ver "Frecuencia").
- `App.ahora()` es el reloj real; los tests lo reemplazan. `App(carpeta_datos=..., usar_mandos=...)` también se usa en los tests.
- Cada escena hereda de `escenas/base.Escena`:
  - `actualizar` cambia el estado o pasa a otra escena con `self.app.cambiar_escena(...)`; `dibujar` solo dibuja.
  - `al_cerrar()` se llama si se cierra la ventana; Iniciales guarda el récord ahí.
  - `tiempo_en_escena()` cuenta con el reloj real y sirve para READY (1.6 s), la explosión (1.5 s) y el Game Over (ENTER se ignora 0.8 s).
  - `dibujar_partida(pantalla, partida, con_nave)` dibuja la partida por capas (ver "Capas de dibujo").
- **Presentación** (`escenas/presentacion.py`, pedido del usuario: "una pequeña pantalla que haga aparecer el menú, que parezca un juego profesional"; eligió **sin tarjeta de estudio** y **con advertencia de fotosensibilidad**). Es lo primero al abrir: `App(presentacion=True)` arranca en ella (los tests usan `presentacion=False` y van directo al Inicio; volver al menú desde una partida también va directo). Tres fases:
  1. `advertencia`: la de fotosensibilidad sobre negro, con la señal `TRIANGULO`. Avisa que los destellos se reducen en Opciones o, si ya están reducidos, lo dice en verde. Dura `MS_ADVERTENCIA`.
  2. `pygame`: "HECHO CON PYGAME"; las letras se escriben de a una (`MS_POR_LETRA`, cada una con `teclear` y naciendo blanca) y crece una línea. Dura `MS_PYGAME`.
  3. `titulo`:
     - salto al hiperespacio (con su sonido) y la nave que sube con su estela (`NAVE_SUBE`);
     - el logo CAZA MONEDAS cae acelerando, las dos palabras juntas (`LOGO_CAE`), y golpea con temblor, chispas, onda de choque y el sonido `logo`;
     - entra la música del menú (`musica` es `SILENCIO` hasta ahí), el lema, "PRESIONA" + el botón de aceptar del control que se usa (`_presiona`, con `interfaz.boton`) titilando, y `VERSION` (config) abajo.
  - Cada pantalla aparece y se va en 4 escalones de negro (`_fundido`).
  - **Saltear:** con `entrada.algo_apretado` (cualquier tecla o botón, no solo acciones; se ignora los primeros `MS_SIN_SALTEAR`):
    - en la advertencia o en la tarjeta, va directo al título;
    - en el título, si el logo no cayó, lo hace caer ya;
    - 400 ms después del golpe, al Inicio (`ui_aceptar` + transición de rombos). Apretar de nuevo enseguida no se pasa de largo.
  - Mientras dura, prepara los giros de la nave (`nave.preparar_giros(2)`).
  - Tests: `tests/test_presentacion.py`, que detecta 5 errores inyectados.
- Flujo: `Presentacion → Inicio`, `Inicio → (Dificultad | Logros | Opciones)`, `Dificultad → Listo → Juego ⇄ Pausa ⇄ Opciones`, `Juego ⇄ Taller`, `Juego ⇄ Gasolinera`, `Juego ⇄ Desarrollador` (F1), y `Juego → Explosion → Iniciales (si entra al top 5 de esa dificultad) → Fin → Listo` (ENTER repite con la misma dificultad) o `Fin → Inicio` (ESC).
- **Inicio** (todo el ancho; rediseñado a pedido del usuario):
  - Franja de arriba: trofeo + LOGROS n/16 (izquierda), RECORD y DIFICULTAD (derecha).
  - Izquierda: el logo (con un brillo que lo cruza cada `BRILLO_CADA`: una franja blanca multiplicada sobre las letras), el lema y el **menú vertical** `MENU` = JUGAR, LOGROS, OPCIONES, SALIR (ARRIBA/ABAJO, da la vuelta; SALIR cierra) con la nave-cursor y la descripción de cada opción (`DESCRIPCION_MENU`, ≤ 25 letras: un renglón).
  - Derecha: la nave grande volando (`NAVE_GRANDE`) y el `PANEL` con 3 `PESTANAS` (GUIA, POWER-UPS, RECORDS) que cambian solas cada `PAGINA_MS` o con LB/RB, Q/E o IZQ/DER (`cambiar_pagina`, que reinicia el tiempo). Páginas: 4 filas de cómo se juega, los 8 power-ups uno por renglón (`ALTO_POWERUP`, descripción en `COLUMNA_DESCRIPCION`) y récords (top 5 y el mejor de cada dificultad).
  - **Todo tiene que entrar**: `test_inicio.py` comprueba los power-ups, las pestañas entre los botones y las descripciones del menú.
- **Taller** (`escenas/taller.py`): las cartas GRATIS, solo en el nivel `MEJORA_PRIMER_NIVEL` (para conocer las mejoras). Lo abre Juego cuando `partida.director.ofertas` no está vacía (con `captura_del_mundo`, pixelada de fondo). 3 cartas de `interfaz.carta` (240x316) que caen de a una (`PASOS_ENTRE_CARTAS`), IZQ/DER + ENTER → `partida.elegir_mejora(tipo)` y vuelve al mismo Juego. Ignora las teclas `PASOS_SIN_ELEGIR` pasos. Las de `peso < 1` dicen RARA. El tiempo de la partida no corre.
- **Gasolinera** (`escenas/gasolinera.py` + `tienda.py`, pedido del usuario: darle protagonismo a las cartas y que las monedas sirvan para algo más que puntos): la parada después de CADA jefe (reemplazó al Taller del cierre del sector). La abre Juego cuando `director.gasolinera` es True (al terminar el cierre: `gasolinera_tras_cierre`); al salir (ESC/B) lo pone en False y vuelve al mismo Juego. El tiempo de la partida no corre.
  - **Todo se paga** con `partida.creditos` (elección del usuario: sin carta de regalo). Lo que no se gasta queda para la próxima.
  - `Tienda(partida)`: `cartas` (`TIENDA_CARTAS` sorteadas con `sortear_mejoras`, envueltas en `Carta`) + `servicios` según `reglas["servicios"]` (pedido del usuario: FACIL sortear/escudo/reparar, NORMAL sortear/escudo, DIFICIL sortear, PESADILLA nada). `articulos()`, `a_la_venta()`, `alcanza()`, `comprar()` (paga con `gastar_creditos`, marca `vendido` salvo `se_repite` y llama a `al_comprar`). Cada cosa una vez por parada; SORTEAR se repite y cada vez cuesta `PRECIO_SORTEAR` más.
  - Precios (`PRECIO_*` en config, de a 5 con `redondear`): carta = `PRECIO_CARTA` + `PRECIO_POR_NIVEL` × nivel que ya tenés (× `PRECIO_RARA` si `peso < 1`), y todo × `inflacion()` = 1 + `PRECIO_POR_SECTOR` por sector después del primero. Medido con un bot (`medir_creditos.py`): un sector da ~50-70 créditos jugando flojo y ~100-180 jugando bien (energía y créditos dependen los dos del combo) → 1 carta o 2-3 por parada.
  - La carta comprada usa `partida.sumar_mejora(tipo)` (la regla sin los efectos del Taller). `EscudoDeViaje` = escudo `HASTA_PERDER_VIDA` (no se vende con uno así puesto); `Reparar` +1 vida (solo si falta).
  - Dibujo (todo con código, sin sprites nuevos salvo la nave al doble), a todo el ancho: encabezado (créditos que cuentan hacia abajo al gastar, `creditos_visibles`; título; PROXIMO SECTOR), la plataforma de lado a lado y la estación (en `self.estacion`, 800 de ancho, pegada `SUBIDA_ESTACION` más arriba: edificio con el vendedor robot `VENDEDOR`, cartel de neón "GAS" que titila, surtidor con los litros, manguera, la nave y el medidor `TANQUE`), el mostrador (cartas de `interfaz.carta` de `ANCHO_CARTA` 140 que caen de a una; la elegida sube siguiendo un `Cursor`; precio con la moneda, amarillo si alcanza, rojo si no; sello VENDIDA; "NO HACE FALTA"; los servicios dicen SERVICIO) y el panel `DETALLE` (la descripción unida en ≤ 2 renglones de `ANCHO_DESCRIPCION`, el precio y "TE QUEDAN n" / "TE FALTAN n"). Al comprar sale "-precio" de la carta. Si no alcanza, la carta tiembla (`PASOS_TEMBLOR`). Tiene sus propios `Efectos`. Entran hasta 6 artículos (un test lo comprueba). **Las descripciones se leen unidas**: si una línea termina una frase, lleva punto.
- **Logros** (`escenas/logros.py`): panel `HANGAR` (IZQ/DER cambia entre `progreso.naves_disponibles()`, se aplica y se guarda) y panel `LISTA` en dos columnas (tilde o candado, y un cuadradito del color de la nave que da).
- **Fin**: tres paneles: `RESULTADO` (puntaje que cuenta, dificultad, sector y nivel, y cada rango en su medalla de color), `ESTADISTICAS` (salen de a una cada `MS_POR_FILA`) y `RECORDS` (tabla, iconos de mejoras y logros nuevos). ENTER otra vez, ESC al menú (importa Inicio adentro del método para no hacer un ciclo).
- **Listo**: una franja de lado a lado que se abre (`carteles.franja`), con el sector y la dificultad (`interfaz.renglon`) y READY? / GO!.
- **Explosion**: cámara lenta los primeros `CAMARA_LENTA` ms (los efectos se actualizan un paso sí y uno no), una viñeta roja en escalones que se cierra y "NAVE DESTRUIDA".
- **Iniciales**: panel con el puntaje, el puesto que vas a ocupar y tres casillas grandes.
- `App.nueva_partida(dificultad=None)`: sin dificultad, usa `opciones.dificultad`. Reinicia los efectos, vuelve el fondo a los colores del primer sector, crea una `Partida`, suena "seleccion" y pasa a `Listo` (que pide la música del juego: ver "Sonido y música").
- **Dificultad** (`escenas/dificultad.py`): las cuatro arriba (`FILA_DIFICULTADES`, con `dibujo.pestanas`), la `TARJETA` de la elegida en un panel y flechas grandes a los costados. IZQ/DER cambian con animación. El nombre entra deslizándose (`PASOS_ANIMACION`) y destella, las calaveras (`CALAVERA`, pixel art de 7x7) aparecen de a una, saltan chispas con la `paleta` de la dificultad y PESADILLA hace temblar la pantalla. ENTER guarda `opciones.dificultad` y empieza; ESC vuelve al inicio.
- **Modo desarrollador** (`escenas/desarrollador.py`, pedido del usuario para probar jefes, enemigos y power-ups): F1 (acción `DESARROLLADOR`) en Juego, solo si `config.MODO_DESARROLLADOR`. Como la Pausa: guarda `escena_juego` y la captura, pausa sonido y vibración, y la partida no corre.
  - `FILAS` = JEFE, ENEMIGO, POWER-UP (IZQ/DER elige de `ELEGIBLES`, que sale de los registros: un tipo nuevo aparece solo; sin esbirros), ANOMALIA (`director.empezar_anomalia(tipo)`; con un jefe no se puede; los nombres largos usan el tipo), INVENCIBLE, LIMPIAR, GASOLINERA (+`CREDITOS_DE_PRUEBA` y abre la tienda) y VOLVER (`FILA_Y` 188 y `ALTO_FILA` 33 para que entren las 8). ENTER vuelve al juego y después llama a `hacer(fila)` (así el sonido no queda en pausa); F1/ESC vuelven sin hacer nada. `_elegido` (del módulo) recuerda la última elección.
  - JEFE: si ya hay uno, lo saca sin premio (y a sus esbirros) y llama a `partida.iniciar_jefe(tipo)`. ENEMIGO: `director.agregar(tipo)`. POWER-UP: `partida.recoger_powerup()` (la misma que usa la cápsula), solo si `disponible()`. Cada acción avisa con `app.avisar()`.
  - Al usar algo: `partida.modo_desarrollador = True` → sin logros (`revisar_logros`), sin récord (Explosion va directo a Fin) y "MODO DEV" en el HUD (MINI, abajo al centro, y 592, debajo de la barra del jefe: arriba tapaba al jefe). `partida.invencible`: `danar_jugador()` no hace nada.
- **Pausa** (`escenas/pausa.py`): de fondo `captura_del_mundo` pixelada; a la izquierda el menú `FILAS_PAUSA` = CONTINUAR, OPCIONES y VOLVER AL MENU (`interfaz.menu`, ARRIBA/ABAJO + ENTER); a la derecha la ficha de la partida (sector y lema, 6 números en grilla, el desafío y las mejoras con sus niveles). La confirmación es una ventana con botones NO/SI.
  - Siguen los atajos P/ESC/Menú (seguir) y O/Vista (opciones).
  - VOLVER AL MENU pregunta "¿VOLVER AL MENU?" (`confirmando`, NO por defecto; IZQ/DER cambia y ESC/B es NO) y avisa que se pierden la partida y su puntaje.
  - Si se confirma, `_volver_al_menu()` reanuda el mixer, para la música, reinicia los efectos y el fondo y pasa a un `Inicio` nuevo, sin guardar récord.
  - La ayuda de abajo cambia según si está la pregunta.
- Hay escenas que guardan otras escenas: `Opciones(volver_a=escena)` y `Pausa(escena_juego, captura)`, así al volver se retoma la misma instancia.
- **Hit-stop:** mientras `partida.congelar_frames > 0`, Juego y Explosion no actualizan ni dibujan (`saltar_dibujo`). Excepción: con `partida.impacto` (el golpe final al jefe) Juego sí dibuja, para mostrar el cuadro de impacto. Después del golpe final, `partida.camara_lenta` pasos a media velocidad (Juego salta un paso sí y uno no, guardando lo apretado con `_guardar_lo_apretado`). `Juego.actualizar` revisa primero `partida.termino`, después el hit-stop y después la pausa. **Trampa:** la App borra las acciones en cada paso, así que durante el hit-stop Juego guarda el dash (`dash_pendiente`) y la pausa (`pausa_pendiente`): si no, se perdían justo al encadenar perfectos.

### Partida (`partida.py`)
- Contiene todo el estado de una partida: `nave`, `vidas`, `puntaje`, `combo`, `nivel`, `moneda`, `capsula`, `activos` (tipo → ms en que termina; `math.inf` para los que duran hasta perder una vida), `enemigos`, `enemigos_guardados`, `jefe` (`None` si no hay pelea), `balas`, `ecos`, `mejoras` (tipo → veces elegida), `estadisticas`, `tiempo`, `congelar_frames`, `pausa_pendiente` y `termino`.
- Los servicios le llegan por parámetro (`efectos`, `sonidos`, `entrada` para vibrar, `records` y `opciones`, que se leen en vivo, y `progreso`: si es `None`, no se revisan logros).
- **Dash perfecto:** solo cuenta (pedido del usuario: atravesar cualquier cosa era muy fácil para farmear puntos) cuando el dash **rompe a un enemigo `destruible`** (en `_actualizar_enemigos`; con FILO se rompen todos, pero solo los destruibles de por sí dan perfecto) o **intercepta** a uno (`enemigo.interceptable()`: el embestidor en "cargar"). Atravesar a los demás o a las balas no da nada. `_dash_perfecto(x, y, cartel, puntos_extra)` premia **una vez por dash** (`perfecto_en_este_dash`): `DASH_PERFECTO_PUNTOS` × combo × cadena (+ extra), el combo no se corta (`ultima_moneda`), `dash_listo` baja a `DASH_PERFECTO_RECARGA`, energía y 3 frames de hit-stop. **Cadena:** otro perfecto antes de `CADENA_PERFECTOS` sube `cadena` (multiplica hasta `CADENA_MAXIMA`).
- **Interceptar** (`_interceptar(enemigo)`): `enemigo.al_interceptar(partida)` (el embestidor vuelve a "acercarse"), velocidad 0, `aturdido_hasta` = + `ATURDIDO_INTERCEPTAR`, estadística `interceptados`, aviso `director.al_interceptar()` (desafío INTERCEPTOR) y un perfecto con el cartel "¡INTERCEPTADO!" y `INTERCEPTAR_PUNTOS` de más (si ya hubo perfecto en ese dash, solo los puntos).
- **Inicio y fin del dash:** `actualizar()` detecta el cambio de `nave.dash_hasta` (`_al_empezar_dash`: estadística, desafío, borra `camino_dash`) y el fin (`en_dash_antes` → `_al_terminar_dash`: NOVA, si no ONDA, y con la mejora ECO crea un `Eco` con chance `MEJORA_ECO[nivel - 1]`). Mientras dura, anota `camino_dash`.
- `onda_expansiva(x, y, radio)`: rompe balas (las destruibles dan puntos), destruye lo que `puede_destruir()` (con `destruir_con_dash`) y a los demás `enemigo.empujar(..., EMPUJE_ONDA, ATURDIDO_ONDA)`. No toca al jefe. La usan ONDA y NOVA.
- **Créditos** (la plata de la gasolinera): `ganar_creditos(cantidad)` es la única entrada (suma `estadisticas.creditos` y `tiempo_creditos` para el destello del HUD) y `gastar_creditos(cantidad)` → True si alcanzó. Los da cada moneda: `CREDITOS_POR_MONEDA` × multiplicador del combo × `multiplicador_monedas()` (fiebre del oro; DOBLE no). No son puntos: gastarlos no baja el puntaje. El HUD los muestra al lado del puntaje (`hud.icono_credito`, que también usa la gasolinera).
- **Mejoras:** `mejora(tipo)` (cuántas veces), `sumar_mejora(tipo)` (la regla: suma, `al_elegir`, estadística), `elegir_mejora(tipo)` (Taller: `sumar_mejora` + vacía `director.ofertas` + efectos en la nave), `mejoras_elegidas()` [(tipo, veces)]. Las reglas que consultan mejoras: `vel_max` (MOTOR), `recarga_dash` (RECARGA), `tiempo_combo` (COMBO LARGO), `espera_powerup` (SUERTE), `duracion_powerup` (POTENCIA, la usa `PowerUp.al_recoger`), `puede_destruir` (FILO), `destruir_con_dash` (BOTIN), `_regenerar_escudo` (ESCUDO ROCE: `MEJORA_ROCE` = [6, 4, 3] perfectos según el nivel, solo se cuentan sin escudo puesto, y el escudo dura hasta el golpe (`HASTA_PERDER_VIDA`); se repite toda la partida. Antes duraba 8 s y los perfectos con escudo se perdían: el usuario sentía que funcionaba una vez. El HUD muestra la carga con `_carga_escudo`, arriba de los activos), `danar_jugador` (FENIX: vuelve con 1 vida y la mejora baja a 0), la atracción de la moneda (ATRACCION), `_al_terminar_dash` (ECO). DOBLE DASH es rara (`peso` 0.35), una sola vez y desde el sector 3 (pedido: con dos dash seguidos era muy fácil).
- **Logros:** cada 30 pasos `revisar_logros()`; cada logro nuevo va a `logros_nuevos` y a `fichas_logro` ([logro, desde], una detrás de otra; los dibuja `carteles.logro`). Al terminar (`_al_terminar`): última revisión y `progreso.partidas += 1`.
- **Dos relojes, no mezclarlos:**
  - `partida.tiempo` avanza `MS_POR_FRAME` solo en `actualizar()` y lo usan todos los temporizadores de juego.
  - `pygame.time.get_ticks()` es el reloj real: solo para parpadeos y animaciones.
- Reglas (siempre pasar por ellas):
  - **Subir de nivel = barra de energía** (pedido del usuario, reemplazó a "cada 10 monedas"): `ganar_energia(cantidad)` es la única entrada (como `sumar_puntos`). La llaman la moneda (`ENERGIA_MONEDA` + `ENERGIA_COMBO` × (multiplicador − 1)), `_dash_perfecto` (`ENERGIA_PERFECTO`), `destruir_con_dash` y el congelado roto (`ENERGIA_ENEMIGO`), y el director al superar una oleada (`ENERGIA_OLEADA`) o cumplir un desafío (`ENERGIA_DESAFIO`). No suma si `not puede_ganar_energia()` (jefe o cierre del sector). Llena (`energia_necesaria()` = `ENERGIA_INICIAL` + (nivel−1) × `ENERGIA_POR_NIVEL`, tope `ENERGIA_MAXIMA`): `subir_nivel()` y lo que sobra pasa, pero menos de lo que pide el nivel nuevo (nunca se saltean dos); si llegó el jefe, queda en 0. `tiempo_energia` hace destellar la barra. Con el bot, tope 16 deja los sectores 1-4 al mismo ritmo que antes (20 los alargaba un 13%).
  - `danar_jugador(x, y)`: si hay escudo, lo rompe y da 0.5 s de invulnerabilidad. Si no, quita una vida, corta el combo y saca los power-ups que duran hasta perder una vida (con textos "-TURBO"…). Con 0 vidas, marca `termino`.
  - `sumar_puntos(base)`: aplica DOBLE y detecta cuándo se supera el récord.
  - `recoger_powerup(powerup, x, y)`: agarrar un power-up (cápsula o modo desarrollador).
  - `subir_nivel()`, `iniciar_jefe()` y `jefe_vencido()`.
- Consultas: `activo(tipo)`, `restante(tipo)`, `activar(tipo, duracion)` (nunca acorta: la cápsula del escudo no achica el de ESCUDO ROCE, y con ese puesto la cápsula no cae), `desactivar(tipo)`, `vel_max()` (turbo), `recarga_dash()` (recarga), `factor_velocidad()` y `multiplicador_combo() = min(1 + combo // 3, COMBO_MAXIMO)`.
- Orden de `actualizar(dx, dy, pidio_dash)`: tiempo → nave (empieza/termina el dash, camino del ECO) → ecos → corte del combo (`tiempo_combo()`) → imán o ATRACCION → moneda (energía) → power-ups → director (oleadas, anomalías, desafíos, rango, ofertas de mejoras) → devolver enemigos guardados → enemigos (mover y choques) → jefe (balas, fases y choques) o balas sueltas → estela → brillo de la moneda → efectos → logros (cada 30 pasos).

### Entrada (`entrada.py`)
- Teclado y mando se convierten en **acciones**: `ACEPTAR`, `VOLVER`, `PAUSA`, `OPCIONES`, `DASH`, `ARRIBA`, `ABAJO`, `IZQUIERDA`, `DERECHA`, y `PESTANA_ANTERIOR`/`PESTANA_SIGUIENTE` (LB/RB = `BOTON_LB` 4 y `BOTON_RB` 5, o Q/E: cambian de pestaña o sección en cualquier menú que las tenga).
- **Último control usado:** `entrada.con_mando` cambia con cada tecla (False) o botón/cruceta/stick (True); `usando_mando()` = eso y que siga conectado. `ayuda()` y `interfaz.ayudas()` lo usan para mostrar las teclas o los botones.
  - Las acciones de un toque quedan en `entrada.acciones` (en orden) y se consultan con `pulso(accion)`.
  - El movimiento sale de `direccion()`: primero las flechas; si no hay, el mando (cruceta en 8 direcciones, o stick en **cualquier ángulo** con zona muerta circular `ZONA_MUERTA_NAVE`).
- `TECLAS`: ESC dispara `VOLVER` y `PAUSA`; F1 dispara `DESARROLLADOR`. `BOTONES`: A = aceptar, X = dash, B = volver (solo eso, así B no pausa el juego), Menú = pausa y Vista = opciones.
- El stick cuenta como un toque solo cuando recién se inclina más allá de `ZONA_MUERTA` (`stick_antes`).
- Banderas del frame: `cerrar`, `foco_perdido` y `mando_desconectado` (solo si el mando estaba en `mandos`). Listo y Juego las convierten en `partida.pausa_pendiente`: es la pausa automática.
- `hay_mando()` y `ayuda(texto_teclado, texto_mando)` eligen los textos de ayuda.
- **Vibración** (`haptica.py`, `entrada.haptica`): `entrada.vibrar(nombre, fuerza=1)` toca un patrón de `config.VIBRACIONES`: nombre → (prioridad 1-4, pasos `(ms, grave, agudo)`). Uno de menos prioridad no corta al que suena. `fuerza` lo escala (cadena de perfectos, rango S/A).
  - **Pedido del usuario: suave y poca.** La primera versión (con los gatillos, golpes al máximo y vibración en cada moneda y cada dash) le pareció demasiado y brusca. Por eso: **sin gatillos** (Impulse Triggers), nada pasa de 0.5 (lo comprueba un test), más agudo que grave, cada patrón sube y baja en varios pasos, y **no vibra lo que pasa todo el tiempo** (cada moneda, dash, dash recargado, ONDA, combo cortado, mira del embestidor, agonía del jefe, menús).
  - Avanza con el reloj real: `App._paso_de_logica` llama a `haptica.actualizar()` (sigue en el hit-stop). Cada paso se manda `SOLAPAR_MS` más largo para que no haya huecos. `parar()` al pausar y al cerrar.
  - Intensidad: `opciones.vibracion` (`ORDEN_VIBRACION`, `NIVELES_VIBRACION`: NO 0, SUAVE 0.5, NORMAL 1, FUERTE 1.5). La App le pasa `opciones` y su reloj (`lambda: self.ahora()`).
  - Dónde vibra: el combo sube / x5, destruir, perfecto, interceptar, hielo roto, NOVA, escudo, golpe, FÉNIX, muerte, power-up, nivel, mejora, récord, logro, oleada, anomalía, desafío, sello del rango, jefe (llega con un latido, golpe, parte, parte rota, explota), impactos de jefes, coraza, avisos (`fijar` de la Fortaleza, `temblar` de la Colmena, `inhalar`/`exhalar` de la Singularidad), PESADILLA y la prueba al cambiar la opción.
  - Tests: `test_haptica.py` con un `MandoFalso` en `entrada.mandos`.
- El mando del usuario (Xbox Series X en Windows) da este mapeo de SDL: A=b0, B=b1, X=b2, Y=b3, LB=b4, RB=b5, Vista=b6, Menú=b7, cruceta=hat 0, stick=ejes 0/1.

### Entidades
- **Nave** (`nave.py`): física con inercia (`NAVE_*`), diagonal normalizada y giro suavizado (0 = arriba, 90 = izquierda, `atan2(-dx, -dy)`). Además:
  - `_acelerar()` separa la velocidad en **avance** (hacia donde se aprieta) y **deriva** (de costado). Arrancar usa `NAVE_ACELERACION`; lo que va hacia atrás o de costado se corrige con `NAVE_FRENADO` (más fuerte): dobla y frena enseguida sin perder la inercia. Acelerando desde quieta da lo mismo que antes (lo usa `test_frecuencia`).
  - Inclinación al girar; flota 2 px cuando está casi quieta.
  - **Dash con buffer:** `dash_pedido_en` + `BUFFER_DASH`, y un destello cian una sola vez cuando se recarga (`dash_avisado`).
  - **Dashes extra** (DOBLE DASH): `dash_extra_max` y `dash_extra`. `dash_disponible(t)`: recargado o con extras (nunca en medio de un dash). Usar uno extra no reinicia la recarga; al recargarse vuelven todos. `duracion_dash` (COMETA lo alarga). El HUD dibuja un cuadradito por extra a la izquierda de "DASH".
  - `nave.cambiar_color(color)`: otra nave (tiñe el sprite con `tenir` y borra el caché de imágenes y de giros).
  - **Giro tipo RotSprite** (`nave.girada(nombre, angulo, inclinacion)`): Scale2x tres veces (x8), `rotate`, y achica tomando el píxel del centro de cada bloque de 8x8 (con un margen de 4 px). Con `rotate` directo el pixel art se rompía. Se guarda por (nombre, paso de 5°, escalón de inclinación de `ESCALONES_INCLINACION`). Cada uno cuesta 2-5 ms la primera vez: **Inicio llama a `nave.preparar_giros(2)` en cada paso**, así llegan todos calculados a la partida. Los fantasmas del dash usan una copia (`girada(...).copy()` antes de `set_alpha`).
  - Choques: `caja_recoger()` (50x50, para recoger cosas), `toca_circulo()` y `toca_rect()` (daño con `RADIO_NAVE = 11`), `atraviesa(t)` (dash o invulnerable) y `empujon()`.
- **Moneda** (`moneda.py`): `lugar_para_moneda(partida)` busca un lugar con `hud.posicion_libre()` a entre `MONEDA_DISTANCIA_MIN` y `MONEDA_DISTANCIA_MAX` de la nave, a más de 60 px de cada enemigo y lejos del jefe (hasta 200 intentos).
- **Zonas del HUD** (`hud.zonas_hud()`, una función porque dependen del ancho): la franja de arriba (y < 100), la de abajo (y ≥ 524) y la columna de power-ups activos. Si el HUD cambia, hay que actualizarlas.
- **Columna de abajo a la derecha del HUD:** "DASH" (y 536, recarga con `dibujo.barra` finita en 547, cuadraditos de DOBLE DASH en 530), "NIVEL n" (y 563) y `_barra_energia` (`dibujo.barra` de 128x12 en y 576; blanca al ganar, naranja parpadeando casi llena, vacía con el jefe).
- **Resto del HUD:**
  - Puntaje: muestra `partida.puntaje_visible`, que cuenta hacia el real en ~6 pasos (`Partida._contar_marcador`, en la lógica).
  - Combo (y 72 + barra finita en 84): color por multiplicador (`COLOR_MULTIPLICADOR`; x5 en arcoíris) y blanco 150 ms al subir (`partida.tiempo_multiplicador`).
  - Desafío: un renglón CHICA debajo de las vidas (y 76): nombre y progreso o CUMPLIDO/FALLADO.
  - Power-ups activos (abajo a la izquierda, de abajo hacia arriba cada `ALTO_ACTIVO`): cápsula (`PowerUp.imagen_capsula()`, también la usa `dibujar_capsula`), nombre y barra finita del tiempo que queda (sin barra los que duran hasta perder una vida). La cápsula parpadea el último 1.5 s. La carga de ESCUDO ROCE usa la cápsula del escudo en gris.
  - `BARRA_CENTRAL` (abajo al centro, 320x16 en y 564) con el nombre arriba a la izquierda: el jefe (`jefe.nombre` en `jefe.color`, `barra_segmentos`, y el segmento recién perdido blanco 400 ms desde `jefe.ultimo_golpe`, que anotan `recibir_golpe` y `golpear_parte`), la oleada o la anomalía (su `nombre`).
- **Enemigos** (`enemigos/`), registro `TIPOS_ENEMIGO` con `@registrar_enemigo` y `crear_enemigo(tipo, partida)`:
  - La base resuelve:
    - la aparición lejos de la nave (`DISTANCIA_APARICION`), con una "X" de aviso durante `AVISO_APARICION` en la que no hace daño;
    - el congelado (sprite azul y "+5"; tocarlo con la caja grande da puntos);
    - los bordes (`rebota_en_bordes`), la animación con `desfase` y `separarse()`.
  - Las subclases escriben `mover()`, y si hace falta `al_aparecer()`, `paso()` y `dibujar_cuerpo()`.
  - **Tope de velocidad:** `Enemigo.rapidez(partida, base)` = `min(base * factor_velocidad(), ENEMIGO_VELOCIDAD_MAX)` (4.2; la nave va a 5): ningún enemigo que te persigue es más rápido que la nave. Lo usan perseguidor, divisor, embestidor (al acercarse) y el `paso()` del rebotador. Los ataques con aviso (embestida, picadas) no tienen tope.
  - `perseguidor`: inercia y se separa de los demás.
  - `rebotador`: diagonal y rebota; se acelera con `factor_velocidad()`. Estados "volando" y "choque" (se aplasta contra la pared que tocó, ver la tabla de sprites).
  - **Aturdido** (`aturdido_hasta`, `aturdido(t)`, `empujar(partida, x, y, distancia, ms)`): quieto y sin lastimar (ni da dash perfecto); dibuja tres estrellitas amarillas que giran. Lo causan las ondas, el ECO y la intercepción; `reaparecer()` lo borra. `empujar()` deja la velocidad en 0: sirve a los que la recalculan en `mover()`, pero el rebotador reescribe `empujar()` para salir lejos de la onda con su rapidez (si no, quedaba quieto para siempre).
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
  - `embestidor`: `acercarse → apuntar (0.6 s, línea roja) → cargar (0.5 s)`. Solo te sigue y embiste dentro de `RANGO_EMBESTIDOR`; si no, deambula con `rumbo`. En "cargar" es `interceptable()`: un dash lo frena y lo aturde (ver Interceptar).
    - **Mira fija** (pedido del usuario): en `apuntar` guarda `mira` (dirección y distancia) y la sigue actualizando hasta `reglas["apunte_fijo"]` ms antes de embestir (FACIL 350, NORMAL 200, DIFICIL y PESADILLA 0 = hasta el final). Desde ahí `mira_fija = True`: embiste hacia donde estabas y la línea deja de parpadear y se alarga (es la señal para correrse).
  - **Separación:** los que persiguen se alejan entre sí a menos de `SEPARACION_ENEMIGOS`, con fuerza `FUERZA_SEPARACION`. Sin esto, se fusionaban a los ~10 s.
  - Progresión: la decide `Partida.director` (`progresion.Director`).
    - **Presupuesto:** cada tipo cuesta `COSTO_ENEMIGO` y se desbloquea en `DESBLOQUEO_ENEMIGO`. Cada nivel tiene `presupuesto()` (`PRESUPUESTO_INICIAL + (nivel-1) * PRESUPUESTO_POR_NIVEL`, con tope `PRESUPUESTO_MAXIMO`, por `reglas["presupuesto"]`).
      - `completar_presupuesto()` agrega enemigos al azar con `random.choices`; el favorito del sector pesa `PESO_FAVORITO`. Como mucho hay `ENEMIGOS_MAX` fijos.
      - El tipo recién desbloqueado se presenta primero.
      - Se llama al empezar, al subir de nivel y al volver del jefe. La cantidad se cuenta con `cantidad_actual()` (un enjambre cuenta como uno).
      - **Refuerzos:** cada `REFUERZO_ESPERA`, si sobra presupuesto (porque destruiste enemigos), llega uno nuevo.
      - Cuando se desbloquea un tipo después del nivel 1, el HUD muestra una **ficha chica** a la izquierda (`carteles.ficha_nuevo_enemigo`, ver "Carteles del juego"): dibujo, "NUEVO ENEMIGO", nombre y pista en MINI. Antes era un cartel al centro y el usuario se quejó de que tapaba la pantalla. La ficha del desafío es la misma, del lado derecho.
    - **Sectores = biomas, uno por jefe** (`SECTORES`, en orden fijo): Cinturón → Ojo, Carmesí → Fortaleza, Esmeralda → Serpiente, Ámbar → Colmena, Abismo → Singularidad, y vuelve al primero. `iniciar_jefe()` usa `director.jefe_del_sector()`.
      - Cada sector: `nombre`, `lema` (debajo del nombre en el cartel), `color`, `jefe`, `tinte`, `fondo`, `ambiente`, `estrellas` (factor RGB) y `favorito`.
      - Se cambia en `jefe_vencido()` → `director.al_vencer_al_jefe()`; el cartel del sector sale cuando termina el cierre (`tiempo_cartel_sector` en el futuro; el HUD lo muestra si `0 <= t < CARTEL_SECTOR`).
      - Al cambiar se va `RECAMBIO_SECTOR` de los **grupos** de enemigos (un enjambre es un grupo); si estaban guardados por la pelea, no vuelven.
      - El fondo cambia con `Fondo.ir_a_sector(sector)` en 4 etapas durante `TRANSICION_SECTOR` pasos (lo llama `Escena.mover_fondo(partida)`). Los tintes no pasan de ~110 por canal.
    - **Anomalías** (`anomalias.py`, registro `TIPOS_ANOMALIA`, `director.anomalia`): en el nivel `ANOMALIA_NIVEL` de cada sector (3, 8, 13…), `ANOMALIA_ESPERA` después, llega una por `ANOMALIA_DURACION`: `elegir_anomalia()` da la del sector (`sector["anomalia"]`) con chance `ANOMALIA_PROPIA` (0.5) y si no una de las otras (`None` = siempre al azar). Pedido del usuario: antes era siempre la del sector y la fiebre del oro recién salía en el nivel 18 (nunca la veía).
      - Ganchos de `Anomalia`: `actualizar`, `terminar`, `dibujar` (lo llama `Partida._dibujar_todo` encima de todo y debajo del HUD), `multiplicador_monedas` y `factor_combo` (los consulta la Partida por medio del director).
      - `asteroides`: columnas punteadas (`avisos`) y `Meteoro`s que caen justo ahí `ASTEROIDES_AVISO` después (destruibles). `tormenta`: calma → aviso (bordes punteados) → llamarada (quema con `toca_rect`; el golpe empuja hacia afuera de la franja). `niebla`: superficie a la mitad escalada x2 (escalones de 2 px) con un agujero alrededor de la nave que se desvanece en `BANDAS_NIEBLA` bandas de `ANCHO_BANDA_NIEBLA`, del color del sector; encima, ojos de los enemigos lejanos y destellos de moneda y cápsula. `oro`: monedas x`ORO_MULTIPLICADOR`, combo x`ORO_COMBO`, polvo dorado.
      - No se pisa con las oleadas (ninguna empieza durante una ni hasta `RESPIRO_ANOMALIA` después); el jefe la corta. Medido con un bot (golpes/min, mismo nivel): sin nada ~4, oleada ~5.6, tormenta ~6.2, asteroides ~7 (pero solo ~0.7/min son de los asteroides: el resto, enemigos mientras esquiva), niebla y oro ≈ normal.
      - **Proyectiles sin jefe:** si no hay jefe pero hay balas (asteroides), `Partida._actualizar_balas_sueltas()` las mueve, el dash rompe las destruibles y `_tocar_balas()` revisa el daño (la misma que usa `_choques_jefe`).
    - **Desafíos** (`desafios.py`, registro `TIPOS_DESAFIO`, `director.desafio`): uno por sector, `DESAFIO_ESPERA` después de llegar (en el primero, del nivel `DESAFIO_DESDE_NIVEL`), al azar entre los `disponible()` y distinto del anterior.
      - De **aguantar** (`meta = None`: sin_dash, intocable, sin_ayuda) se fallan con su aviso y se cumplen al llegar el jefe; de **lograr** (combo `DESAFIO_COMBO`, cazador `DESAFIO_CAZADOR`, solo desde el divisor, e interceptor `DESAFIO_INTERCEPTAR`, solo desde el embestidor) se cumplen con `avanzar()` y se fallan si llega el jefe.
      - **Avisos:** la Partida llama a `director.al_recibir_golpe()` (en `danar_jugador`, también si para el escudo), `al_usar_dash()` (si cambió `nave.dash_hasta`), `al_agarrar_powerup()`, `al_recoger_moneda(combo)`, `al_destruir_enemigo()` (en `destruir_con_dash`) y `al_interceptar()`. El director anota la bitácora y le pasa el aviso al desafío; `revisar_desafio()` premia (`DESAFIO_PUNTOS * numero_sector`, anillo, power-up enseguida) o lo marca fallado.
      - HUD: ficha a la derecha (`carteles.ficha_desafio`: al proponerse, al cumplirse y al fallarse) y el nombre con el progreso debajo de las vidas (y 72/86, MINI).
    - **Rango y cierre del sector** (`rango.py`): `Bitacora` (golpes, mejor_combo, desafio_cumplido, inicio_jefe, tiempo_jefe). En `al_vencer_al_jefe()` se calcula `calcular_rango()` (estrellas: golpes 2/1/0, combo ≥ `RANGO_COMBO`, desafío, jefe antes de `RANGO_TIEMPO_JEFE` +20% por vuelta; S = 5, A = 4, B ≥ 2, C) y empieza el **cierre**: `CARTEL_JEFE` ("¡JEFE VENCIDO!") + `CARTEL_RANGO` (el cartel con las filas de a una; la letra cae a los `RANGO_SELLO`, y ahí `pagar_rango()` suma `RANGO_PUNTOS`). Mientras `director.cerrando_sector()`, los enemigos guardados no vuelven, no se gana energía y no hay oleadas ni anomalías; al terminar sale el cartel del sector nuevo.
    - **Mejoras** (`mejoras.py`, registro `TIPOS_MEJORA` de instancias, `director.ofertas`): `ofrecer_mejoras()` deja `sortear_mejoras(partida)` (3 distintas, `random.choices` con `peso`, solo las `disponible()`: no al máximo y desde `desde_sector`) en el nivel `MEJORA_PRIMER_NIVEL` (gratis, el Taller). Cuando termina el cierre del sector se pide la gasolinera (`gasolinera_tras_cierre` → `gasolinera = True`). `con_mejoras = False` apaga las dos (fixture). Cada `Mejora`: `tipo`, `nombre` (≤12), `descripcion` (líneas ≤22, MINI), `color`, `icono` 7x7, `maximo`, `peso`, `desde_sector`, `al_elegir()`. Los valores están en config (`MEJORA_*`, `FENIX_INVULNERABLE`). Medido con el bot: no cambian los golpes/min del juego normal (el bot elige al azar).
    - **Oleadas:** cada `OLEADA_ESPERA` (desde `OLEADA_DESDE_NIVEL`, sin jefe) llegan enemigos extra con `de_oleada=True` por `OLEADA_DURACION`, y después se van.
      - Si no perdiste vidas: `OLEADA_PUNTOS * nivel` y un power-up enseguida.
      - El jefe corta la oleada (`al_empezar_jefe`).
      - HUD: cartel "¡OLEADA!" y una barra abajo al centro.
  - **Dificultad:** `Partida(…, dificultad)` guarda `reglas = DIFICULTADES[dificultad]`, `vidas_max` y `vidas`.
    - `factor_velocidad()` multiplica por `reglas["velocidad"]` (también las balas del Ojo), y `espera_powerup()` por `reglas["espera_powerup"]`. `reglas["apunte_fijo"]` lo usa el embestidor. `reglas["servicios"]` dice qué vende la gasolinera además de las cartas.
    - El HUD dibuja `vidas_max` íconos.
- **Jefes** (`jefes/`), registro `TIPOS_JEFE`; el que sale es el `"jefe"` del sector actual.
  - **Filosofía (pedido explícito del usuario):** las peleas son un **baile con ritmo, estilo Cuphead/Dark Souls**, no una lluvia de balas. Un ataque por vez, cada uno con **anticipación (aviso) → ataque a ritmo → ventana para pegarle**. Pocas balas (el bot mide ~0-10 en pantalla de promedio). Cada jefe con personalidad (nombre, apodo, gestos, textos) y su propio estilo de combate. Si se agrega uno, seguir esto.
  - **Pulso:** `ms_pulso` (por defecto `JEFE_PULSO`). `cambiar_fase(fase, ms, t)` y `cambiar_fase_pulsos(fase, n, t)` guardan `fase_desde`/`fase_hasta`; en cada paso la base calcula `self.pulso` (pulsos desde que empezó la fase, el 0 empieza el paso siguiente) y `self.nuevo_pulso`. `fin_de_fase(t)`. **Trampa:** el paso en que termina una fase también es el comienzo de un pulso: revisar `fin_de_fase` ANTES de `nuevo_pulso` (si no, sale un disparo de más; lo detectó un test).
  - La base resuelve `entrar` (`actualizar_entrada()`, por defecto baja hasta `y_final`; al salir de "entrar", `cambiar_fase` anota `fin_entrada`) y `morir` (2 s de explosiones en `punto_de_explosion()`, después `partida.jefe_vencido()`).
  - **Cinemática de llegada** (`hud._presentacion_jefe`, encima de todo; mientras dura, el resto del HUD se esconde): franjas de cine (`ALTO_CINE`, entran en `MS_FRANJAS`) con cinta de peligro roja que se desplaza, luces de sirena a los costados (fijas con DESTELLOS REDUCIDOS), "¡ALERTA! / SE ACERCA UN JEFE" (`MS_ALERTA`) y después una franja en `y_presentacion` con "JEFE DEL SECTOR n", el `nombre` (entra desde la izquierda) y el `apodo` (desde la derecha) en su `color`. Al terminar la entrada todo se retira y la barra de vida se llena de a un segmento (`MS_POR_SEGMENTO`).
  - También: la vida (`JEFE_VIDA + jefes_vencidos // 2`), el congelado (solo en `fases_congelables`; corre `fase_desde`/`fase_hasta` y llama a `al_congelarse()`), `recibir_golpe()` → `empezar_a_morir()`, `explotar()`, `al_vencerlo()`, las variantes de sprite (`imagen_actual()`), "¡DASH!" en `punto_cartel_dash()`, las cajas `caja_cuerpo()`/`caja_nucleo()`/`cajas_danio()`, `zonas_sin_monedas()` y `objetos_que_se_mueven()` (para interpolar piezas sueltas).
  - Dibujo: `dibujar()` = `dibujar_cuerpo()` (sprite en `posicion_dibujo()` + partes) + `dibujar_extra()` + avisos. Los jefes que no son un sprite fijo (Serpiente, Singularidad) reescriben `dibujar_cuerpo()`.
  - Tamaño por clase: `ancho`, `alto` (120 por defecto) e `y_final`. `temblando()` dice cuándo se dibuja temblando (por defecto, al morir).
  - **Partes** (`partes.py`, `Parte(dx, dy, ancho, alto, vida)`): piezas con posición relativa al jefe, guardadas en `jefe.partes`. `margen_golpe` (clase, 0 por defecto) agranda `caja_golpe()`, la que usa `parte_golpeable()` para el dash; el daño sigue usando `caja()`.
    - `Partida._choques_jefe`: en dash, primero `jefe.parte_golpeable(caja)` → `jefe.golpear_parte()` (efectos, hit-stop y `al_golpear_parte`/`al_romper_parte`); después el núcleo. Las dos rebotan la nave con `_rebotar_en()`.
    - El daño al tocar usa `jefe.cajas_danio()` (cuerpo + partes vivas; la Fortaleza suma los láseres prendidos). `lugar_para_moneda` también las esquiva.
    - `vida_barra()` da (vida, máximo) para el HUD; los jefes con partes suman las de ellas.
    - La base dibuja las partes (con el mismo flotar y temblor del cuerpo) y, debajo de cada parte golpeable, una flechita cian con un solo "¡DASH!" entre todas (con un cartel por parte se pisaban).
    - Las partes con posición propia (segmentos, asteroides) no son `Parte`: son objetos con `x`/`y` que el jefe devuelve en `objetos_que_se_mueven()`.
    - Congelado, una parte golpeable se puede seguir golpeando: el hielo alarga la ventana, igual que con el núcleo del Ojo.
  - `JefeOjo` ("EL OJO", Cinturón): `flotar` (`JEFE_FLOTAR`) → `atacar` (carga 0.7 s y `JEFE_RAFAGAS` ráfagas, turnando abanico y anillo de 12 balas) → `cansado` (`JEFE_CANSADO`) → `flotar`.
    - `direcciones_ataque()` la usan tanto el disparo como el **aviso** (`dibujar_aviso_ataque`, apagable con `opciones.aviso_jefe`).
  - `Fortaleza` ("ACORAZADO IMPERIAL", Carmesí, 384x192, `y_final = 56`): una marcha militar; 4 lamparitas del casco marcan el pulso.
    - **Tamaño (rework pedido por el usuario: más grande y con más hitbox):** todo se mide en "pixeles del dibujo" (128x64) con `px(n) = n * ESCALA` (`ESCALA = 3`); para cambiar el tamaño alcanza con `ESCALA`. `ABAJO_CASCO` = px(50). Cañones de 48x48 con `margen_golpe = FORTALEZA_MARGEN_GOLPE` (12 px de más para pegarles con el dash; `Parte.caja_golpe()`, solo para el golpe, no para el daño). Por ser más ancha, `fijar` dura `FORTALEZA_FIJAR` = 2 pulsos: con 1, el casco llegaba a la altura de la nave antes de que saliera de abajo (`test_se_puede_escapar_de_la_caida_sin_dash` lo detecta).
    - Con coraza, cada compás: `reubicarse` (2) → `cargar` (2) → `disparar` (`PULSOS_ATAQUE`) → `recalentado` (`FORTALEZA_RECALENTADO`; los cañones del compás quedan `caliente` = golpeables). Si los golpean a todos, el compás termina antes.
    - 4 `Canon` (48x48, luz de su color): ráfaga (3 `Obus`, uno por pulso), misiles (2 `Misil`, el dash los destruye y da puntos), láser (barre hacia la nave a `FORTALEZA_LASER_VELOCIDAD`; hay que cruzarlo con el dash) y minas (2 `Mina` a las X de `objetivos`, estallan en "+" y "x" a 3 pulsos).
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
  - Durante la pelea no se gana energía (no se sube de nivel). Al vencerlo: bonus `JEFE_PUNTOS * jefes_vencidos`, el cartel "¡JEFE VENCIDO!" (`CARTEL_JEFE`) y el del rango (`CARTEL_RANGO`). Los enemigos guardados vuelven recién cuando termina el cierre del sector.
- **Power-ups** (`powerups/`), registro `TIPOS_POWERUP`; el orden de `tipos.py` es el del HUD y del panel de inicio (8: escudo, hielo, vida, imán, doble, turbo, recarga, nova; ECO pasó a ser una mejora):
  - **Inteligentes:** `Partida.elegir_powerup()` usa `random.choices` con `PowerUp.peso(partida)` (por defecto 1: vida 4 con una vida, escudo y recarga más contra un jefe, hielo y nova según enemigos y balas, imán y doble según el combo) y multiplica por `REPETIR_POWERUP` al que cayó recién (`ultimo_powerup`).
  - `nova` (HASTA_PERDER_VIDA): el próximo dash termina en `onda_expansiva(NOVA_RADIO)` y se gasta.
  - La mejora ECO crea un `Eco(camino, angulo)` (`eco.py`): espera `ECO_RETRASO` pasos y recorre el camino del dash: destruye lo destruible, aturde (una vez por enemigo) y rompe balas; deja partículas violetas.
  - `duracion`: ms (escudo, hielo, imán, doble; valores en `DURACION`), `HASTA_PERDER_VIDA` (turbo, recarga) o `None` (vida, instantáneo).
  - `disponible(partida)`: vida solo si falta alguna; los permanentes, solo si no están activos.
  - `al_recoger()`: el hielo además rompe las balas y hace explotar escarcha.
  - `Capsula`: aparece cada `ESPERA_POWERUP` (la primera a los `PRIMER_POWERUP`), **cae** desde y=-15 en una x al azar a `VELOCIDAD_POWERUP` y se va al pasar y > 615.
  - Los efectos se consultan con `partida.activo(tipo)`: escudo en `danar_jugador`, hielo congela, imán atrae la moneda, doble en `sumar_puntos`, turbo en `vel_max` y recarga en `recarga_dash`.

### Servicios
- **Opciones** (`escenas/opciones.py` + `guardado.Opciones(archivo)`), en `PESTANAS` = VIDEO (RESOLUCION, FPS, CRT, ESCALADO, NEON; con 5 filas `ALTO_FILA` es 40), SONIDO (VOLUMEN, MUSICA, EFECTOS: tres barras `Volumen`) y ACCESIBILIDAD (TEMBLOR, DESTELLOS, AVISO JEFE, VIBRACION, AUDIO MONO):
  - Cada fila es un `Ajuste` (Template Method) en la lista `AJUSTES`: `Lista(nombre, pestaña, atributo, valores, descripcion, vuelta, nombres, al_cambiar)` (`valores` puede ser una función(app); `vuelta=True` da la vuelta, sin vuelta se queda en la punta), `Interruptor` (SI/NO; ENTER también) y `Volumen` (barra). `al_cambiar(app)` aplica el cambio (resolución, vibración de prueba). Los valores "apagados" (NO, 0) se ven en gris.
  - **Para agregar una opción:** sumarla a `guardado.Opciones` (fábrica, cargar, guardar) y una línea en `AJUSTES`. Nada más.
  - Todo el ancho: a la izquierda `PANEL_SECCIONES` (las secciones con `ICONOS` y la nave-cursor, y los botones para cambiar), a la derecha `PANEL` con el nombre de la sección. **LB/RB (Q/E) cambian de sección** (`PESTANA_ANTERIOR`/`PESTANA_SIGUIENTE`); ARRIBA/ABAJO recorren los ajustes y VOLVER (dan la vuelta); IZQ/DER cambian el valor.
  - Cómo se ve cada valor: `Lista` con flechas a `SEPARACION_FLECHA` y, si es una escala (sin vuelta), un indicador de segmentos debajo; `Interruptor` como una llave; `Volumen` en cuadritos que crecen. La franja de la fila elegida se desliza (`cursor_fila`). Abajo, la descripción (`partir_lineas`, hasta 2 renglones). `test_opciones.py` comprueba que todo entre (filas, descripciones y el valor más ancho de cada ajuste).
  - Los tests llegan a un ajuste con `ayudas.ir_al_ajuste(app, nombre)` (teclas reales: E y ABAJO), nunca con un número fijo de flechas.
  - VIBRACION va de NO a FUERTE (no da la vuelta) y al cambiarla vibra el patrón "prueba" (un motor y después el otro).
  - `opciones.resolucion` es un nombre ("1280x720", `None` = la primera).
- **Guardado:** `TablaRecords`, con una tabla por dificultad: `filas(dif)`, `maximo(dif)`, `entra(puntos, dif)` y `agregar(nombre, puntos, dif)` → posición. `Opciones` guarda además `dificultad` (la última elegida).
  - Si el archivo no existe, se crea; si está dañado, se usan los valores de fábrica.
  - Si no se puede escribir, el juego sigue (`_escribir_json` ignora `OSError`).
- **Sonido y música:** ver la sección "Sonido y música" (más abajo).
- **Ventana:** el lienzo es `app.pantalla` y `Ventana.mostrar()` lo escala sin suavizar, centrado y con barras negras.
  - `resoluciones` (propiedad) son las de `RESOLUCIONES` (todas 16:9) que caben en el monitor; "COMPLETA" siempre está. `aplicar(nombre)` abre la ventana por nombre.
  - **Trampa:** al salir de FULLSCREEN, el primer `set_mode` deja el tamaño anterior; `aplicar()` lo repite.
- **Fondo** (`Fondo.mover(empuje_x, empuje_y)` en la lógica, mediante `Escena.mover_fondo(partida=None)`, y `Fondo.dibujar(pantalla, fraccion)` interpolado, mediante `Escena.dibujar_fondo`): objetos (`PROFUNDIDAD`) y estrellas (90 cada 800 px de ancho, teñidas con `sector["estrellas"]`). Caen a `0.6 * profundidad` y, solo en Juego, se corren con el paralaje (`-v * REACCION_PARALAJE`). Paleta: ningún canal por encima de ~110.
  - Las estrellas titilan de a una (`TITILAR_MS`, `TITILAR_CADA`). **Salto al hiperespacio** (`saltar_al_hiperespacio()`, al empezar una partida y al salir de la Gasolinera): `HIPERESPACIO_PASOS`, la velocidad extra sube y baja como un seno (`velocidad_salto()`, hasta `HIPERESPACIO_VELOCIDAD`) y las estrellas se dibujan como rayas.
  - **Ambiente del bioma** (`sector["ambiente"]`, `Mota`s con tope `MAXIMO_MOTAS`): asteroides + estrellas fugaces, brasas que suben + relámpagos (`relampago`), luciérnagas + esporas, panal de fondo (`panal()`, baldosa que se desplaza) + polen, polvo que gira hacia el centro + ondas de gravedad. Al cambiar de sector, las motas viejas se van apagando de a poco.

- **Logros** (`logros.py`): `Logro(id, nombre ≤16, descripcion ≤36, condicion)`; `revisar_logros(partida, progreso)` devuelve los nuevos y los desbloquea (`Progreso.desbloquear` guarda). `NAVES` en config: (nombre, color o None, id del logro o None); `Progreso.naves_disponibles()` y `color_nave()`. Las estadísticas (`estadisticas.py`) las suma la Partida: monedas, creditos (ganados), enemigos, dashes, perfectos, mejor_cadena, powerups, desafios, sectores_limpios, rangos, mejoras.

## Sonido y música
Todo el audio pasa por `juego/sonido.py` (el servicio `app.sonidos`).
- **Todo el sonido sale del estudio** (`herramientas/estudio/`, ver "El estudio"):
  - los efectos (los armónicos, en 11 colores: ver "Armonía en vivo");
  - los 5 ambientes de los sectores;
  - todos los temas: `musica_juego` (con sus 4 variantes por sector, `musica_juego_2..5`), `musica_tension`, `musica_iniciales`, `musica_fin`, `musica_menu`, `musica_gasolinera` y los de los jefes.
- **Los temas chiptune se rehicieron en el estudio** (2026-10-14, pedido del usuario: "que todos los efectos sean armónicos, lo mismo con la música, que parezca profesional"; eligió rehacerlos en vez de solo nivelarlos). Eran mono, ~2 dB más fuertes y de otra estética. Conservan su melodía, sus acordes y su carácter: `musica_menu` y `musica_gasolinera` en `obras/musica.py`, los 5 de jefe en `obras/musica_jefes.py`.
- **Cada jefe tiene su tema**, todos en Re menor (los efectos de los jefes están en Re menor): `musica_jefe` (el Ojo), `_fortaleza` (marcha), `_serpiente` (swing y adornos frigios), `_colmena` (las alas zumban en el grave) y `_singularidad` (medio tiempo). En `Juego.musica`, `"jefe_" + jefe.tipo` si está en `MUSICAS`, si no `"jefe"`.
- **El compositor viejo de chiptune se borró** (2026-10-14, con su test): ya no hacía ningún sonido del juego. Queda en el historial de git (commit `73a57fb`, `herramientas/componer_musica.py`).
- **La carpeta `efectos/`** (2026-10-14, pedido del usuario: "organizar los efectos de sonido y revisar que no haya archivos huérfanos"): todo en **OGG** (los efectos estaban en WAV: 52 → 33 MB) y ordenado por familia, la del módulo del estudio donde se compone (`CARPETA_DEL_MODULO` y `ruta_relativa()` en `obras/__init__.py`). Un armónico va en su propia carpeta con sus 11 colores. **El juego busca cada archivo por su nombre** en cualquier subcarpeta (`sonido.ruta_del_sonido`, que recorre `efectos/` una vez): el catálogo no sabe de carpetas y los nombres no se pueden repetir. `test_cada_sonido_esta_en_la_carpeta_de_su_familia` lo comprueba (OGG, sin nombres repetidos, cada uno en su carpeta). La auditoría no encontró huérfanos: cada archivo está en el catálogo, cada sonido del catálogo se pide en el código, cada obra va al juego y cada ficha tiene su archivo.
- **Los 6 efectos viejos y `musica.mp3` se borraron:** el usuario los eliminó y cada uso pasó a su sonido nuevo.
- Mezclador hecho (fase A del mapa); P1, P2 y P3 compuestos y conectados: `LISTA_DE_SONIDOS.md` está completa.

**Plan de sonido: `MAPA_DE_AUDIO.md`** (pedido del usuario: "una sensación de calidad sin precedentes, sin saturar"). Es el mapa de todo lo que puede sonar en el juego: cada evento con un código (`N01`, `FO07`...), dónde pasa en el código, qué suena hoy, el sonido propuesto y su prioridad (P1/P2/P3/NO). También tiene las reglas de mezcla (prioridad, voces, enfriamiento, paneo, ducking), el catálogo de sonidos, la música por momento, los silencios a propósito y el orden para hacerlo. **Antes de agregar un sonido, buscarlo ahí y seguir sus reglas; al hacerlo, actualizar la columna "Hoy".**

**Lista de trabajo: `LISTA_DE_SONIDOS.md`** (pedido del usuario: componer "como un músico profesional"). Tiene cada sonido del catálogo con su estado (⬜ pendiente, 🟨 compuesto, ✅ en el juego), los eventos que lo usan, la prioridad y la **partitura** (notas, armonía, timbre, duración y volumen), más un **Registro** de avances al final. Su sección 0 es la base musical, que no hay que romper:
- La tonalidad de cada tema: juego, menú, tensión y fin La menor; iniciales Do mayor; jefes Re menor; gasolinera Fa mayor.
- **Los premios y la interfaz se escriben en la pentatónica de Do** (C D E G A) y **siguen al acorde** que suena (ver "Armonía en vivo"): el estudio los re-armoniza a la pentatónica de cada acorde.
- **La tensión sale de la propia escala del tema** (2026-10-14): en La menor el tritono Si–Fa y la sexta menor Fa; en Re menor la sexta menor Si♭, el tritono Mi–Si♭ y la segunda menor La–Si♭. Antes los peligros usaban notas de afuera (Mi♭, La♭, Fa#) y, repetidos cada pocos segundos, sonaban desafinados. Solo quedan de afuera los raros y a propósito: la ¡ALERTA! (suena en silencio), PESADILLA, el "trombón triste" de `desafio_fallado` y la presentación del jefe (La mayor: el V de Re).
- Los avisos de peligro terminan en tensión; `vulnerable` y los premios resuelven.
- Los registros: la interfaz arriba (octavas 6-7), el peligro en el medio y los impactos con ruido grave.
- El recorrido armónico de los momentos: jefe en Re menor → `jefe_vencido` en Re MAYOR → rango en Do (V de Fa) → gasolinera en Fa.
- Las herramientas para efectos (`secuencia`, `barrido`, `ruido`, curvas, trémolo/vibrato, dinámicas) están en el estudio (ver "El estudio").

**Todo el sonido se hizo de cero** (decisión del usuario: "todos los efectos ya existentes hay que rehacerlos, desde cero con nueva temática").
- Cada archivo de `efectos/` sale de una obra del estudio, salvo los tres temas que se quedan.
- `test_sonidos_del_juego.py::test_todo_el_sonido_sale_del_estudio` lo comprueba, y `test_el_catalogo_y_los_archivos_coinciden` comprueba que no falte ni sobre ningún archivo.
- Un sonido nuevo se compone en el estudio, nunca se trae hecho.

Al terminar un sonido: cambiar su estado, anotar el avance en el Registro y actualizar la columna "Hoy" del mapa.

### El mezclador (`sonido.py`, fase A del mapa: hecho)
- **Catálogo de efectos (patrón Registry):** `CATALOGO` = nombre → `Efecto(archivos, categoria, prioridad, voces, enfriamiento, volumen, paneo)`, **214 nombres** (los armónicos, con un archivo por color). Se arma con `_armar(...)` y tres ayudas:
  - `_uno(nombre, ...)`: un archivo;
  - `{nombre: Efecto(_variantes(nombre, n), ...)}`: **variantes** que se turnan al azar (`nave_dash`, `ui_mover`, `enemigo_roto`, `hielo_roto`, `onda`, `agonia`, `teclear`);
  - `_escala(nombre, n, ...)`: **escalas** que se piden por número (`moneda_1..5`, `perfecto_1..5`, `combo_sube_1..3`, `estrella_1..5`, `sector_nuevo_1..5`, `barra_jefe_1..12`, `rebote_1..4`, `divisor_parte_1..3`, `ui_tecla_1..5`, `dificultad_1..4`, `carta_1..6`, `roce_carga_1..6`).
  - Criterios: la interfaz va en INTERFAZ, siempre al centro. Los avisos y los ataques son PELIGRO. Los grandes momentos son MOMENTO y bajan la música: `record`, `logro`, `fenix`, `nave_muerte`, `golpe_final`, `jefe_explota`, `jefe_vencido`, `sello_*`, `sector_nuevo_*`, `oleada_superada`, `desafio_cumplido`, `destruida`, `game_over`. Lo que suena todo el tiempo es DETALLE y lleva enfriamiento (`aparece` 120, `rebote` 200, `agonia` 150, `teclear` 45...).
  - `laser` es un `.ogg` que da la vuelta (loop).
  - `MUSICAS` (todos del estudio): "juego" (el Cinturón), "juego_2" a "juego_5" (el color de cada sector), "tension", "iniciales", "fin", "menu", "gasolinera", "jefe" y uno por jefe.
  - `AMBIENTES`: el `"ambiente"` de `config.SECTORES` → `amb_<sector>.ogg` (asteroides, brasas, esporas, panal, abismo).
  - **`SILENCIO`** ("silencio") es un nombre de música que no existe: una escena que lo pide deja todo callado, con fundido.
- **Categorías** `MUSICA`, `EFECTOS`, `INTERFAZ`, `AMBIENTE`. Su volumen es `nivel(categoria)` = general × el suyo (`volumen_musica` para MUSICA, `volumen_efectos` para las otras tres) × `MEZCLA[categoria]` (config), y 0 con `opciones.silencio`.
- **La mezcla deja margen (headroom)** (2026-10-14, pedido: "se siente mucho solapamiento y saturación"). `MEZCLA` = música 0.5, efectos 0.7, interfaz 0.6, ambiente 0.3: los temas (−14 LUFS) quedan en −20 dentro del juego y los efectos un poco por encima. Medido con un bot y una mezcla fuera de línea igual a la de SDL (suma y recorte): con todo en 1.0, **53 de 362 segundos sonaban recortados** (pico +3.5 dB); ahora 0, con el pico en −2.5 dB.
- **El limitador** (`Sonidos.limitar()`, lo llaman `reproducir` y `actualizar`): SDL suma los canales y recorta lo que se pasa. El mezclador sabe cuánto suena cada efecto en cada momento por su **ficha** (`efectos/fichas.json`, que escribe el estudio: el pico de cada bloque de 50 ms de un efecto, el nivel típico de un tema) y lleva la cuenta en cada canal (`Sonando`: nombre, `sonido`, prioridad, inicio, ganancia, paneo, envolvente; `carga(ahora)`). Si la suma con la música, el ambiente y los loops (`carga_del_fondo`) pasaría de `TECHO_MEZCLA` (0.89 = −1 dB), `_cuanto_bajar` baja primero los DETALLE y ACCION (hasta `PISO_DETALLES`) y, si no alcanza, todo. Bajar es inmediato; volver, en `RECUPERACION_MEZCLA` ms. El canal recibe `paneo × lo que bajó su grupo`. Con la mezcla con margen trabaja ~3% del tiempo: es una red de seguridad.
- **Armonía en vivo** (los efectos siguen al acorde, como en Rez o Tetris Effect): `ARMONICOS` (la misma lista que en `herramientas/estudio/obras`, un test lo comprueba) son los efectos con altura que suenan sobre la música: monedas, combo, perfectos, power-ups, premios e interfaz. Un `Efecto` cuyas variantes están en `ARMONICOS` tiene `armonico = True` y `por_color` = {color: [archivo de cada variante]} (`archivo_de_color("moneda_1.wav", "fa")` = `"moneda_1_fa.ogg"`). `COLORES` son 11 (la pentatónica de cada acorde, ver "El estudio"). `color_actual()`: la ficha de cada tema trae el color de cada compás y cuánto dura uno; el `Tocadiscos` anota `inicio` al empezar un tema (y `reanudar_todo` lo corre lo que duró la pausa); mirando `ADELANTO_ACORDE` ms adelante, da el color del compás. Sin música, o con su volumen en 0, `COLOR_SIN_MUSICA` ("do"). `_elegir_variante` toca el archivo de ese color. `aplicar_volumen(opciones)` lo pone en cada `Sound` (× `efecto.volumen`) y guarda las opciones; lo llaman la App al arrancar, Opciones y el atajo M. Apagado = volumen 0: sigue sonando callado, así la música retoma donde iba.
- **`reproducir(nombre, x=None)`** devuelve el canal, o `None` si no sonó. En orden:
  1. **Enfriamiento:** si sonó hace menos de `enfriamiento` ms (reloj real: `self.reloj`, que la App pone en `self.ahora`), no suena.
  2. **Voces:** si ya suenan `voces` copias, corta la más vieja de ellas y usa su canal.
  3. Si no, el primer canal de efectos libre.
  4. Si están todos ocupados, **le roba el canal al menos importante** (prioridad `DETALLE` 1 < `ACCION` 2 < `PELIGRO` 3 < `MOMENTO` 4; entre iguales, al más viejo), solo si no es más importante que el nuevo.
  5. **Variantes:** con varios archivos, elige al azar sin repetir la anterior (`_elegir_variante`).
  6. **Paneo:** después de `play()` (que vuelve el canal a 1), `canal.set_volume(*paneo(x, mono))`. `paneo()`: al centro los dos lados enteros; hacia un costado el otro baja hasta `PANEO_MINIMO` (0.35), nunca a 0. Sin x, con `paneo=False` o con `opciones.audio_mono` (AUDIO MONO), al centro.
  7. **Ducking:** un efecto `MOMENTO` llama a `atenuar_musica(su duración)`. La música baja a `ATENUAR_MUSICA` (0.4) y vuelve en `ATENUAR_VUELTA` ms (600); `actualizar()` (la App la llama en cada paso) la sube de a poco.
  - `sonando(nombre)` dice cuántas copias suenan (los tests lo usan).
- **`reproducir_luego(nombre, ms, x)`** programa un efecto (reloj real; lo dispara `actualizar()`). Ejemplos: la fanfarria 500 ms después de la explosión del jefe, el sello después de la caja, el logro cuando sale su ficha, el trueno 450 ms después del relámpago, la presentación del jefe a los `MS_ALERTA`. `cancelar_pendientes()` al morir y al volver al menú.
- **Canales** (`CANALES_AUDIO` = 24, `set_reserved(6)`): 0-1 música, 2-3 ambiente, 4-5 loops, 6-23 efectos (`canales_efectos`, con lo que suena en `en_canal`).
- **`Tocadiscos(canales, temas, fundido)`**: dos canales para cruzar temas; lo usan `self.musica` y `self.ambiente`.
  - `tocar(nombre)`: si ya suena, nada. Si no, el viejo baja con `fadeout` y el nuevo empieza **desde el principio** en el canal libre, con `fade_ms`.
  - `parar(fundido)`: con 0, corta en seco.
  - `actual` es el nombre pedido **aunque no haya audio** (los tests lo miran).
  - Sonidos ofrece `tocar_musica`, `parar_musica(fundido=FUNDIDO_MUSICA)`, `actual` (propiedad: la música), `tocar_ambiente` y `parar_ambiente` (`FUNDIDO_AMBIENTE` 1500).
- **Loops** (`tocar_loop(nombre)`, `parar_loop(nombre, fundido=0)`, `parar_loops()`): un efecto del catálogo que se repite en los canales 4-5 (el láser de la Fortaleza, una sirena). Si ya suena, no se duplica; con los dos ocupados, no entra. **Quien lo prende lo tiene que parar** (y al morir o al salir de la partida, `parar_loops()`).
- **Ducking sin pisar el fundido:** la música baja con el volumen del `Sound` del tema que suena (`_poner_volumen_musica`), no con el del canal, que es el que usa el fundido.
- **Música por escena (patrón State):** cada escena tiene el atributo de clase `musica` (`Escena.musica = None` en `escenas/base.py`). `App._paso_de_logica` hace, antes de cada `escena.actualizar`, `if self.escena.musica is not None: self.sonidos.tocar_musica(self.escena.musica)`. `None` significa "no la cambio": sigue la que venía (o el silencio).

  | Escena | `musica` |
  |---|---|
  | Inicio, Dificultad, Logros | `"menu"` |
  | Listo | **propiedad**: `SILENCIO` en el READY? y `musica_del_sector(partida)` desde el GO! (1 s): la música entra en el GO |
  | Juego | **propiedad**: `None` si `partida.termino`. Con jefe: `SILENCIO` durante la ¡ALERTA! (`hud.MS_ALERTA` desde `jefe.creado_en`: suena la sirena), `"jefe"` desde su nombre, y `SILENCIO` cuando `jefe.muriendo()` (el golpe final la corta: `empezar_a_morir` hace `parar_musica(150)`). `SILENCIO` en el cierre del sector (`director.cerrando_sector()`: la fanfarria y el sello suenan solos). `"tension"` en el nivel antes del jefe (`nivel % JEFE_CADA_NIVELES == JEFE_CADA_NIVELES - 1`). Si no, `musica_del_sector(partida)`: `"juego"` en el sector 1 y `"juego_N"` en los otros |
  | Gasolinera | `"gasolinera"` (al salir vuelve al mismo Juego, que pide la suya) |
  | Iniciales | `"iniciales"` |
  | Fin | `"fin"` |
  | Pausa, Opciones, Taller, Desarrollador, Explosion | `None` |

- **Ambiente por escena (como la música):** `Escena.ambiente` (`None` = no lo cambio) → `sonidos.tocar_ambiente` en cada paso.
  - Juego: propiedad, el `"ambiente"` del sector, y `SILENCIO` en la pelea, en el cierre y al morir.
  - Listo: el del sector.
  - Inicio, Dificultad, Logros, Explosion, Iniciales, Fin y Gasolinera: `SILENCIO`.
  - Pausa, Opciones, Taller y Desarrollador: `None` (la pausa ya congela todo).
  - Al cambiar de sector, el tocadiscos del ambiente cruza en `FUNDIDO_AMBIENTE` (1.5 s).
- Al perder la última vida (`Partida.danar_jugador`), `parar_musica(fundido=0)` corta la música en seco, se paran los loops, se cancelan los pendientes y suena `nave_muerte`. En la Explosion suena `destruida` (con el cartel, a los 450 ms) y al final `game_over`. Después, Iniciales y Fin tienen su música. `Pausa._volver_al_menu()` llama a `parar_musica()` y el Inicio nuevo pide "menu".
- **Pausa:** `pausar_todo()`/`reanudar_todo()` = `pygame.mixer.pause()/unpause()`: congela TODOS los canales (música, ambiente y loops) y retoma donde iban. Un efecto pedido **después** de pausar sí suena (play saca la pausa de ese canal): la pausa puede tener su sonido. Lo usan Juego (al abrir Pausa y Desarrollador) y Pausa.
- **El audio se abre en la App** con `pygame.mixer.pre_init(44100, -16, 2, 512)` antes de `pygame.init()`: estéreo (para el paneo) y un buffer chico (~12 ms de retraso; el de fábrica se nota).
- **Opciones de sonido** (`guardado.Opciones`):
  - `volumen` (el general), `volumen_musica` y `volumen_efectos` (0-10, tres barras `Volumen` en SONIDO);
  - `silencio` (la tecla M; tocar cualquier barra lo saca, y con él las barras se ven grises);
  - `latido` (SONIDO, SI/NO: un latido suave cada 1.6 s con una sola vida, `Partida._latir`);
  - `audio_mono` (ACCESIBILIDAD).
  - Un `config.json` viejo con `"musica": false` o `"efectos": false` (eran SI/NO) pasa a ese volumen en 0.
- `_cache` del módulo (archivo → Sound): abrir los 4 temas tarda ~0.3 s y los tests crean una App por test (sin caché eran ~100 s más). El caché comparte los objetos `Sound` entre Apps: su volumen es uno solo.
- **Tests:**
  - `tests/test_sonido.py`: catálogo, paneo, enfriamiento, voces, prioridades, variantes, ducking, loops, ambiente, volúmenes, mono, pausa y Opciones, y el limitador (nada pasa del techo, primero bajan los detalles, vuelve de a poco, cada efecto tiene su envolvente). Se verificó que detecta 15 errores inyectados, contando los del compositor y del guardado, y 2 más del limitador.
  - `tests/test_armonia.py`: los colores de cada acorde (y que no choquen con él), la re-armonización (la escalera de la moneda sigue subiendo), que el estudio y el juego tengan la misma lista, el color de cada compás de cada tema, que la moneda suene en el color del acorde, la pausa, sin música en Do y los colores que se abren tarde con su volumen. Detecta 5 errores inyectados.
  - **Medir la mezcla jugando** (scratchpad, se reescriben si faltan): `grabar_partida.py` (un bot juega N minutos, invencible y con ayuda para pegarle a los jefes, y anota cada efecto que sonó con su archivo, canal, paneo y acorde, más la música y el limitador en cada paso), `mezclar_sesion.py` (lo mezcla como SDL: suma y recorte; da segundos recortados, pico, niveles y voces a la vez) y `choques.py` (cuánto de cada efecto cae a un semitono del acorde que sonaba, y cuánto habría chocado fijo en Do). Ojo: el ruido da ~45 % de "choque" al azar.
  - `tests/test_musica.py`: la música de cada escena, incluidos el silencio de la ALERTA, el golpe final, el cierre del sector, el READY y la música de Iniciales y Fin.
  - `tests/test_sonidos_del_juego.py`:
    - todo sale del estudio (los colores, de su obra); el catálogo y los archivos coinciden; cada archivo tiene su ficha;
    - la moneda sube de tono con el combo; el dash suena; los golpes suenan distinto (y la última vida avisa); la cadena de perfectos;
    - el jefe con alerta y sus fases; la oleada, los menús, la pausa y la gasolinera.
    - Usa el fixture `pedidos`, que anota cada `reproducir`/`reproducir_luego`; los programados aparecen dos veces, al programarse y al sonar.
    - Se verificó que detecta 10 errores inyectados en el cableado.
- **Trampas:**
  - No usar `pygame.mixer.music`: es una sola pista (no hay fundido cruzado) y `mixer.pause()` no la pausa.
  - `canal.set_volume(izq, der)` va **después** de `play()`: play lo vuelve a 1.
  - Volver a un tema (Gasolinera → Juego) lo empieza de cero. Si alguna vez se quiere retomar donde iba, hay que guardar el canal en vez de pararlo.

### Dónde suena cada cosa (el cableado)
- **Partida:**
  - Nave: `_al_empezar_dash` (`nave_dash` / `nave_dash_extra`), `dash_listo` (cuando `nave.dash_avisado` pasa a True).
  - Golpes (`danar_jugador`): `escudo_roto`, `nave_golpe`, `ultima_vida` programada, `fenix`, `nave_muerte`.
  - Monedas y combo: `moneda_<multiplicador>` (+ `oro_brillo` en la fiebre), `combo_sube_N` / `combo_max` (en `_vibrar_moneda`), `combo_cortado` (al cortarse con x2 o más).
  - Puntos: `perfecto_<cadena>`, `interceptado` + `aturdido`, `enemigo.sonido_roto` al destruir (`"enemigo_roto"`; los divisores, `divisor_parte_1..3`), `bala_rota`, `hielo_roto`, `record`, `nivel` (no en el nivel del jefe), `logro` + `nave_nueva`.
  - Power-ups y mejoras: `capsula` (al caer), `pw_<tipo>` al recoger, `_avisar_powerups` (`pw_acaba` a 1.5/1/0.5 s y `pw_fin`), `nova`, `onda`, `eco`, `roce_carga_N`, `mejora_elegida`.
  - Jefe: `iniciar_jefe` (`alerta`, `franjas`, presentación programada, `SONIDO_ENTRADA`), `_llenar_barra_del_jefe` (`barra_jefe_N` por segmento) y `jefe_vencido` (para los loops y programa la fanfarria).
- **Director:** `oleada`, `oleada_superada`, `retirada`, `<tipo>_llega` y `anomalia_fin`, `desafio_nuevo` / `_cumplido` / `_fallado`, `ficha_enemigo`, `sello_<letra>` y `_sonidos_del_rango` (`estrella_N` en el momento exacto en que sale cada estrella, con los tiempos de `carteles.rango`; `teclear` en una fila sin estrellas).
- **Jefes:** cada clase completa `SONIDOS_FASE` (fase → efecto al entrar en ella), `FASES_VENTANA` (fases en que se le puede pegar: suena `vulnerable`) y `SONIDO_ENTRADA`. `Jefe.actualizar` compara la fase antes y después de `_actualizar` (la lógica de siempre) y `sonar(partida, nombre, x)` panea desde el jefe. Además, en el código de cada uno:
  - Ojo: los disparos y su voz.
  - Fortaleza: la marcha del compás en cada pulso, las cargas, los cuatro ataques, el láser (`tocar_loop` / `parar_loop` con fundido) y las cortinas.
  - Serpiente: veneno, choque y corte.
  - Colmena: las abejas, "¡A CASA, HIJAS!" y los choques.
  - Singularidad: el tic del anillo, los brazos, exhalar y la moneda tragada.
  - En la base: `golpe_final` / `jefe_golpe`, `jefe_parte` / `parte_rota`, `agonia` y `jefe_explota`.
- **Enemigos y proyectiles:**
  - `aparece` (en `Enemigo.actualizar`, al terminar la X) y `rebote_<pared>`.
  - Embestidor: `embestidor_apunta`, `mira_fija`, `embestida`. Enjambre (`Bandada`): `enjambre_aviso`, `enjambre_picada`, `bonus`. `abeja_aviso`.
  - `mina_tic` (a 500, 300, 160 y 60 ms de estallar) y `mina_estalla`.
  - Anomalías: `meteoro_aviso` y `tormenta_aviso` / `llamarada`.
- **Escenas:**
  - Inicio: SALIR toca `ui_apagar` y cierra 450 ms después.
  - Dificultad: `dificultad_N` y `pesadilla`.
  - Listo: `listo_ready` y `listo_go`.
  - Juego: `pausa` después de `pausar_todo()`.
  - Pausa: `ui_mover`, `ui_alerta`, `seguir`.
  - Opciones: `ui_mover`, `ui_pestana`, y `ui_llave_si/no` o `ui_valor_sube/baja`, que sirven de muestra del volumen nuevo.
  - Logros: `hangar_nave`.
  - Taller: `taller` y `carta_N` al caer cada carta (+ `carta_rara`).
  - Gasolinera: `tienda`, `carta_N` al caer, `caja` + lo comprado (y `sello`), `ui_error` + `vendedor_no`, y al salir `hiperespacio` + `sector_nuevo_N`.
  - Explosion: `destruida`, `game_over`.
  - Iniciales: `ui_tecla_N` por letra, `record_guardado`.
  - Fin: `ui_volver`.
  - `App.nueva_partida`: `ui_empezar` + `hiperespacio`.
  - App: `logo` al arrancar (programado), `ui_transicion` en cada `cambiar_escena` con transición, `mando_fuera` / `mando_dentro` (con `entrada.mando_conectado`; no los que ya estaban al abrir, los primeros 2 s).
  - Gasolinera: `surtidor` al llegar y `neon` cuando el cartel GAS vuelve a prender (`_sonar_neon`, con el mismo reloj que su dibujo).
  - Fin: `_sonidos` (`contador_1..8` mientras cuenta, `contador_fin`, `teclear` por fila de estadísticas) y `fuego_artificial` con los fuegos del récord.
  - Partida: `dash_vacio` (pidió el dash y falta más que `BUFFER_DASH`) y `_latir`.
  - `Escena.mover_fondo`: `trueno` después de cada relámpago del Carmesí.

### Para agregar un efecto o un tema al juego
1. Buscarlo en `LISTA_DE_SONIDOS.md` (su partitura) y componerlo en el estudio (ver abajo). Nunca traer un archivo hecho.
2. Efecto: una línea en `CATALOGO` con su categoría, prioridad, voces y enfriamiento (los del mapa). Variantes: una lista de archivos. Una escala (`moneda_1` ... `moneda_5`) son entradas separadas.
3. Llamar a `sonidos.reproducir("nombre", x)` donde pase la cosa (en la lógica, nunca en `dibujar`; la x si viene de un lugar de la pantalla). Un loop: `tocar_loop` / `parar_loop`.
4. Tema: sumarlo a `MUSICAS` (o `AMBIENTES`) y ponerlo en el `musica` de la escena (o en la propiedad de Juego, si depende de la partida). Si cambia qué suena en una escena, sumar un caso a `tests/test_musica.py` (se mira `app.sonidos.actual`) y actualizar la tabla de arriba.
5. Marcarlo en `LISTA_DE_SONIDOS.md` (estado y Registro) y en la columna "Hoy" de `MAPA_DE_AUDIO.md`.

### El estudio (`herramientas/estudio/` + `herramientas/componer.py`)
**Pedido del usuario:** "algo diferente, que inspire calidad, profesionalismo en el desarrollo de la música; que no suene chillón, que tenga cuerpo". Se dejó el chiptune por **synthwave retro-futurista** (va con el neón y el CRT).

**La evidencia medida:** los efectos viejos tenían su brillo (centroide) entre 4100 y 6900 Hz y la música vieja era mono, a -11 LUFS y con el brillo en ~5200 Hz. `musica_juego` quedó a -14 LUFS, con 2200 Hz de brillo, estéreo 0.81 y pico -3.3 dB (dinámica: los golpes respiran; era -8 con la cinta sin calibrar, que los aplastaba).

El juego NO usa el estudio: solo los archivos que escribe en `efectos/`. Necesita `numpy`, `numba` (los filtros; sin numba anda pero lento) y `soundfile` (OGG), en `requirements.txt` aparte de lo del juego.
```
python herramientas/componer.py                         # todo
python herramientas/componer.py musica_juego moneda     # esos (y los que empiezan con "moneda")
python herramientas/componer.py ui_ --escuchar          # los compone y los hace sonar
python herramientas/componer.py --lista
python herramientas/componer.py --fichas                # rehace efectos/fichas.json sin componer (~2 s)
```
- **Fichas** (`efectos/fichas.json`): cada archivo que se compone anota cuánto suena (`envolvente` de un efecto: el pico de cada 50 ms; `nivel` de un tema: el percentil 95 de esos picos) y un tema también `acordes`, `colores` (uno por compás) y `compas_ms`. Las usa el mezclador del juego (limitador y armonía). `--fichas` las rehace leyendo los archivos (conserva los acordes y calcula los colores).
- **Efectos armónicos** (`ARMONICOS` en `obras/__init__.py`): se componen una vez por color con `armonia.en_color` y se guardan en su propia carpeta, uno por color (`juego/moneda_1/moneda_1_fa.ogg`: son ~1070; cargar uno tarda ~1.5 ms).
Por cada uno imprime la duración, el volumen (LUFS: el integrado en un tema, el bloque de 400 ms más fuerte en un efecto), el pico, el **brillo** (centroide; arriba de ~2500 Hz en música o ~4000 Hz en efectos empieza a sonar chillón) y el **estéreo** (correlación: 1 = mono). Todo en OGG Vorbis (`compression_level` 0.4, ~1 MB por 49 s de tema; un WAV pesa 6 veces más y no se oye la diferencia), en la carpeta de su familia (`guardar()`). Todo es determinista: la semilla sale del nombre de la obra.

**Módulos:**
- `base.py`: `FS`, `njit` (el de numba, o uno que no hace nada sin numba), `midi`/`hertz`/`a_hertz`, `leer_acorde` (`TIPOS_ACORDE` con sus4, add9, m9, 6/9, dim...; barra "C/E"), `db`, `curva(puntos, cuantas, exponencial)` (automatización vectorizada) y `muestras(segundos)`.
- `sintesis.py`:
  - `onda(forma, frecuencias)`: sierra/cuadrada con **PolyBLEP** (sin aliasing), triángulo y seno; `frecuencias` es un arreglo, así un glissando es solo una curva.
  - `adsr(...)`: exponencial, con 5 constantes de cola y que termina en 0.
  - `filtrar(senal, corte, resonancia, modo, polos)`: **SVF TPT** (Zavalishin) en numba; el corte puede cambiar en cada muestra; `polos=4` = 24 dB/oct.
  - `Sinte`: sustractivo. Varias voces desafinadas y paneadas (unísono), sub, ruido, filtro con su ADSR (más fuerza = más brillo), seguimiento de teclado, vibrato que entra tarde, deriva analógica (dos senos lentos de unos centésimos) y saturación.
  - `FM`: moduladores `(relación, índice, caída del índice)`: piano eléctrico, campanas, metales, marimba.
  - `ruido(...)`: filtro con curva, forma, chasquidos y trémolo.
  - Todo devuelve **estéreo (2, muestras)**.
- `bateria.py`: `bombo` (seno que cae ×3 en 35 ms + clic), `caja` (parche de dos senos + bordona de ruido), `palmas` (tres palmadas + cola), `hat` (seis cuadradas "808" + ruido, pasa altos 7 kHz), `tom`, `platillo` y `platillo_al_reves`. `GOLPES` mapea las letras de la grilla: K S C h H T t X R.
- `procesos.py`:
  - `reverb`: convolución por FFT con una respuesta generada (ruido L/R que se apaga y se oscurece), cacheada.
  - `delay`: ping-pong en numba, que se oscurece en cada vuelta.
  - `chorus`, `saturar` (tanh), `ensanchar` (medio/costado).
  - `ecualizar(senal, bandas, vuelta)`: FFT, fase cero; bandas `corte_graves`, `corte_agudos`, `graves`, `agudos`, `campana`.
  - `comprimir` (rodilla suave, numba), `limitar` (mira 3 ms adelante, techo exacto), `bombeo` (la ganancia del sidechain).
  - Para medir: `loudness` (LUFS ~BS.1770: ponderación K, bloques de 400 ms, compuertas), `loudness_maximo`, `centroide`, `correlacion`, `a_db_pico`.
- `armonia.py`: los efectos que siguen al acorde.
  - `COLORES`: 11 (do, reb, re7, mi, mi7, misus, fa, sol, la, sib, do7) = (fundamental, forma); `FORMAS`: "mayor" [0 2 4 7 9], "dominante" [0 2 4 7 10] (acordes con séptima), "suspendida" [-2 0 2 5 7] (sus4: Mi sus4 = Re Mi Fa# La Si, la pentatónica MAYOR de Re. Contada desde Mi, la tercera Mi-Sol de un efecto se volvía un tono).
  - `color_de_acorde(nombre)`: mayor → su pentatónica mayor; menor → la de su relativo mayor (Am → do); con séptima → dominante; sus4 → suspendida; con barra manda el acorde. Si un acorde no tiene color, `KeyError`: sumarlo a `COLORES` y a `juego/sonido.py`.
  - `armonizar(nota, color)`: cada nota de la pentatónica de Do pasa al mismo **grado** del color, en la misma octava, corrida como mucho media octava (la escalera de la moneda sigue siendo una escalera). Una nota de afuera tira `FueraDeLaPentatonica`: un efecto armónico solo se escribe con Do Re Mi Sol La.
  - `with en_color(color):` compone en ese color.
- `instrumentos.py`: los presets.
  - **`CAMPANA` y `METAL` tienen relaciones FM enteras** (2026-10-14). Antes eran inarmónicos a propósito: `CAMPANA` (3.5) sumaba a −5 dB una tercera mayor arriba de cada nota (sobre un La, un Do# que chocaba con la música en La menor) y `METAL` (1.41, 3.73) sonaba más fuerte en un La3 desafinado un cuarto de tono que en su nota. Ahora `CAMPANA` usa 3 y 7, y `METAL` 1.002 y 3.997: los parciales caen sobre los armónicos pero "baten" (el brillo inquieto del metal) sin desafinar. **Un instrumento nuevo: relaciones enteras** (medirlo con un análisis de parciales).
  - Pads: `PAD_CALIDO`, `PAD_OSCURO`, `PAD_SUAVE`.
  - Bajos: `BAJO_ANALOGICO`, `BAJO_SUB`, `BAJO_RUGIDO`.
  - Melódicos: `PLUCK`, `LEAD_CALIDO`, `LEAD_HUECO`.
  - FM: `EPIANO`, `CAMPANA`, `CRISTAL`, `MARIMBA`, `METAL`.
  - La idea de todos: nada sin filtro, el brillo en el ataque, el cuerpo en voces y sub.
- `obra.py`:
  - **`Obra(nombre, bpm, acordes, ..., sala, eco, objetivo=-14 LUFS)`**: un tema que da la vuelta. Lo que se pasa del final entra por el principio, y la reverb (circular), el delay y el compresor pasan dos veces: **loop sin costura**.
  - **`Efecto(nombre, segundos, dinamica)`**: suena una vez. `DINAMICAS` en LUFS del bloque más fuerte, calibradas contra la música a -14: pp -24, p -19, mf -15, f -12, ff -9. Sin compresión ni cinta en el master (`cinta=0`): suena limpio. Se recorta lo que queda 50 dB debajo del pico y nunca pasa de `segundos + cola`, con un fundido: un efecto ocupa un canal mientras suena.
  - **Un efecto es más seco que un tema** (2026-10-14): `cola` por defecto 0.3 × la sala (era 0.6) y `retorno_sala` 0.3 (en un tema, 0.5). Con las colas largas, una moneda duraba 1.1 s y tres seguidas eran un solo ruido que no terminaba.
  - `Obra.color`: el color en que se compone (lo toma de `armonia.color_actual`); `Pista.nota` y `Pista.barrido` llevan cada nota a ese color con `armonia.armonizar` (las alturas en Hz, como los `cuerpo`, quedan igual).
  - **`Pista`**: el instrumento y su tira de consola: `volumen` (dB), `paneo`, `eq`, `saturacion`, `chorus`, `ancho`, envíos `reverb`/`delay` y `bombeo` (sidechain con los bombos).
  - Notas: `grilla(texto, desde)` (tracker de semicorcheas: nota, "." sigue, "-" silencio, "C5+E5" acorde, "!" acento, "?" fantasma), `acordes(patron)` con **conducción de voces** (`voces_del_acorde`: la posición más cercana a la anterior, voz por voz), `bajo(patron)` (R 3 5 6 7 8 B), `arpegio(orden)`, `secuencia("G5:40 C6:90")` (ms), `barrido(puntos)`, `ruido(...)` y `golpe(letra)`. `Bateria.grilla` usa letras y anota los bombos para el bombeo.
  - Un poco de "humano" (±3 ms y ±4 % de fuerza; nunca en efectos).
  - El master: EQ (graves y presencia suaves, +1.5 dB de aire arriba de 11 kHz), compresión de "pegamento" 2:1, saturación de cinta (`cinta`, 0.08), volumen al objetivo y limitador a -1 dB.
  - **La cinta trabaja siempre al mismo nivel** (2026-10-14): antes recibía la mezcla tal como salía de las pistas, y un acorde (varias notas sumadas) llegaba tan fuerte que la curva lo aplastaba y mezclaba sus notas entre ellas (intermodulación de −8 a −15 dB en ~70 efectos: lo "saturado" de las monedas, los menús y los premios; en la música, −18 a −20). Ahora la mezcla entra con el pico en `NIVEL_CINTA` (−6 dB). `test_el_master_no_ensucia_un_acorde_fuerte` comprueba que el master no depende del nivel de las pistas.
- `obras/` (patrón Registry, `@obra("nombre_del_archivo")`; `cargar_todas()` importa los módulos):
  - `musica.py`:
    - `neon_en_ruta(nombre, color)`: "Neón en ruta" con un color de `COLORES` (bpm, swing, sala, pad, bajo, arpegio, lead, contracanto, medio tiempo, hats), registrado como `musica_juego` (color 1) y `musica_juego_2..5`;
    - `musica_tension`, `musica_iniciales`, `musica_fin`, `musica_menu` ("Hangar") y `musica_gasolinera` ("Parada técnica": vibráfono, piano eléctrico a contratiempo, bajo caminante R 3 5 6).
  - `musica_jefes.py`: un tema por jefe, en Re menor (con `bateria()`, una ayuda que arma las 5 piezas con sus cortes): `musica_jefe` ("Mirada fija", el Ojo, con el riff de semicorcheas), `_fortaleza` ("Marcha imperial": redoblante, oom-pah, golpes de metal y el lead doblado por `METAL`), `_serpiente` ("Danza de escamas": swing, flauta hueca con adornos frigios, campanas), `_colmena` ("Enjambre de cristal": las alas son un `ZUMBIDO` en semicorcheas) y `_singularidad` ("Horizonte de sucesos": medio tiempo, sala de 4 s).
  - `ambiente.py`: `amb_*`. Son `Obra` de 24 s que dan la vuelta, a -26 LUFS. Las curvas terminan donde empiezan y los trémolos tienen períodos que entran justo en 24 s: el loop no tiene costura.
  - `capas.py`: las capas con que se arma cada efecto.
    - `tono` (secuencia en ms), `deslizar` (barrido) y `cuerpo` (grave corto que baja);
    - `aire` (ruido, siempre con techo a 7.5 kHz: lo de arriba es lo chillón);
    - `explosion`, `golpe` (batería) y `clic`.
  - Los efectos, por familia:
    - `efectos_interfaz.py`: la interfaz, la dificultad, el Taller, la gasolinera y el hangar;
    - `efectos_juego.py`: la nave, las monedas, el combo, los power-ups y las mejoras;
    - `efectos_enemigos.py`: los enemigos y los proyectiles;
    - `efectos_director.py`: oleadas, anomalías, desafíos, carteles, rango, READY/GO, Game Over y trueno;
    - `efectos_jefes.py`: los comunes y los 5 jefes, en Re menor.
  - **Familias** (variantes y escalas): `registrar_familia(prefijo, valores, fabrica)` registra `prefijo_1`, `prefijo_2`... `abrir_acorde(...)` arma un acorde que se abre nota por nota.
  - `laser` es una `Obra` de 1 s que da la vuelta, no un `Efecto` (un efecto se recorta y se apaga: el loop haría clic).
  - `componer.py --efectos` compone todos los efectos sin los temas (~10 min: los armónicos van en 11 colores). Todos los temas (`componer.py musica`): ~10 min.
  - **Brillo:** la meta es menos de ~3900 Hz por efecto, y el promedio quedó en 2031 Hz. Los siseos (serpiente, vapor, cascabel) usan filtros de banda en el medio-agudo, no pasa altos: con pasa altos llegaban a 11-13 kHz.

**Sonidos limpios** (2026-10-14, pedido: "otros muy saturados que rompen la experiencia"; `LISTA_DE_SONIDOS.md` sección 0.12). Seis patrones que saturaban, con su regla:
1. El master no puede depender del nivel de las pistas (ver la cinta, arriba).
2. En el medio y el grave, nada a menos de una tercera: voces abiertas (quintas, cuartas, octavas), nunca un pad una octava abajo de un acorde cerrado.
3. Lo que suena junto a un efecto armónico también es armónico (el Taller estaba en Fa y las cartas encima seguían al acorde). Por eso `taller` y `dificultad_1..4` son ARMÓNICOS.
4. Las sierras (`PLUCK`, `LEAD_CALIDO`) para melodías y bajos, no para acordes de efectos: piano eléctrico y cristal.
5. En los armónicos, **los acordes con Do, Re y Sol** (no cambian en ningún color) y el Mi o el La en la melodía: sobre un acorde con séptima el La pasa a ser la séptima y La+Mi se vuelve tritono.
6. En un instrumento con cola (cristal, campana), arpegios con saltos, no escalas rápidas: cada nota sigue sonando debajo de la siguiente y se apilan segundas.
- `test_los_efectos_armonicos_no_apilan_notas_que_raspan` (en `test_estudio.py`) anota las notas de cada armónico en los 11 colores, sin sintetizarlas, y falla si dos que suenan juntas están a 1, 2 o 6 semitonos.
- Para medir: la **aspereza** (Plomp-Levelt, parciales a menos de una banda crítica; una nota de cristal ~0.003, en ruido no sirve) y la prueba nula (con y sin una etapa). Los scripts del scratchpad: `sonda.py` (distorsión del master), `aspereza.py`, `colores.py` (viejo contra nuevo en 4 colores), `barrido.py` (todos) y `choques_notas.py`.
- **La moneda y el combo:** cada multiplicador sube la nota principal y suma una capa (x2 segunda voz, x3 brillo de la octava, x4 una nota más en la subida, x5 un destello): `test_la_moneda_suma_capas_con_el_combo`.

**Para un sonido nuevo:**
1. Tomar su partitura de `LISTA_DE_SONIDOS.md` y traducir el timbre (sección 0.5 de la lista).
2. Escribir la función en el módulo de su familia, con `@obra`, armado en capas: tono, cuerpo y aire.
3. **Revisar la lista de "Sonidos limpios" antes de componer** (abajo), sobre todo si lleva acordes, notas rápidas o suena junto con otro efecto.
4. `python herramientas/componer.py nombre --escuchar` y mirar los números. Si lleva acordes, medir también la aspereza en varios colores (`colores.py` del scratchpad; si no está, reescribirlo: ver "Sonidos limpios").
5. Si es un módulo nuevo, sumarlo a `cargar_todas()`.
6. `python -m pytest tests/test_estudio.py`: el test de notas que raspan revisa todos los armónicos en los 11 colores.

**Lista de verificación de "Sonidos limpios"** (los errores que ya se cometieron; el usuario los oyó como "saturado"):
- [ ] ¿Algún acorde con dos notas a un tono o un semitono en el medio o el grave? → abrir las voces.
- [ ] ¿Un pad o un bajo una octava abajo de un acorde cerrado? → solo la fundamental (o fundamental y quinta).
- [ ] ¿Es armónico? Los acordes, con Do, Re y Sol; el Mi y el La, solo en la melodía.
- [ ] ¿Suena junto a un efecto armónico (en el mismo momento o pisándolo)? → también armónico.
- [ ] ¿Escala rápida en un instrumento con cola (cristal, campana, piano)? → arpegio con saltos.
- [ ] ¿Sierras (`PLUCK`, `LEAD_CALIDO`, `LASER`) tocando acordes? → piano eléctrico o cristal.
- [ ] ¿Un instrumento nuevo? Relaciones FM enteras y una sola nota con aspereza ~0.003.
- [ ] ¿Se tocó el master o se agregó una saturación? Tiene que trabajar a un nivel fijo, no al que llegan las pistas (`test_el_master_no_ensucia_un_acorde_fuerte`).
- [ ] ¿La dinámica es la justa? ff solo para los grandes momentos; un aviso o un GO, f.
- [ ] En la música vale lo mismo, salvo que las sierras sí pueden tocar acordes (pads y leads) porque pasan por su filtro y la cinta calibrada.

**Mezclar con números, no a ciegas:**
- Además del brillo, mirar el reparto de energía por franjas (sub <60 Hz, graves, medios, presencia 2-6 kHz, aire >6 kHz).
- La primera mezcla de `musica_juego` tenía 32 % de sub y 0 % de aire: se oía "tapada". Se corrigió con menos sub en el bajo y el bombo, hats más fuertes desde la fuente, el pad y los plucks más abiertos y aire en el master.
- **Al final, que el usuario escuche:** los números no reemplazan al oído.

**Tests:** `tests/test_estudio.py`: notas y acordes, curvas, sin aliasing, ADSR, filtro, ningún instrumento chillón, ruido, limitador, ecualizador sin basura al final, reverb que da la vuelta, bombeo, LUFS de un seno conocido, notación, conducción de voces, tema que da la vuelta a su volumen, efecto recortado, y que todos los efectos registrados se compongan (los temas no: tardan ~80 s cada uno). Se verificó que detectan 11 errores inyectados.

**Trampas:**
- **libvorbis se queda sin pila en Windows** (se cae sin mensaje, exit 127) si recibe un tema entero de una vez: `guardar` escribe de a bloques de 32768.
- La FFT es circular: en un efecto, el ecualizador rellena 1 s de silencio a cada lado (si no, su "adelanto" aparecía al final y el recorte no cortaba nada).
- `canal.set_volume` del juego y el volumen de los archivos son aparte: el volumen relativo entre efectos sale de la dinámica de cada uno, y la `MEZCLA` de `config.py` ajusta por categoría.
- Un tema tarda ~80 s en componerse (casi todo es sintetizar las notas de los pads de 6 voces).

## Tests (`tests/`)
- `conftest.py`:
  - pone los drivers dummy;
  - fixture `app` (datos en `tmp_path`, `usar_mandos=False`, reloj falso `app.reloj_falso` y teclas mantenidas en el conjunto `app.teclas`);
  - fixture `partida` (recién creada, sin enemigos, sin power-ups, sin oleadas, **sin anomalías, desafíos ni mejoras** (`director.con_anomalias`/`con_desafios`/`con_mejoras = False`; sus tests los prenden) y con la moneda lejos).
  - Para esperar a que vuelvan los enemigos después de un jefe: `CARTEL_JEFE + CARTEL_RANGO`.
- `ayudas.py`: `avanzar(app, frames)` (frames completos de la App, sin esperar), `tecla(K)`, `boton(n)`, `jugar(partida, frames, dx, dy, dash)` (solo la lógica) e `ir_al_ajuste(app, nombre)` (en Opciones).
- `test_inicio.py`: menú vertical, páginas con LB/RB/Q/E/IZQ/DER, SALIR y que todo entre. `test_hud.py`: además, el marcador que cuenta y la barra del jefe (aparece al terminar de entrar, se llena de a uno y destella).
- `test_opciones.py`: secciones con LB/RB y Q/E, que todo entre en el panel, cada opción de accesibilidad (temblor, destellos, CRT parejo en 1080p), que el HUD no tiemble y que los textos flotantes no se pisen.
- `test_efectos_visuales.py`: halos y la opción NEON, estelas (el metal no brilla), ondas de choque, fogonazos del jefe, giros de la nave y su preparación de a poco, hiperespacio y el escalado suave.
- **Trampa al inyectar errores a propósito** (para probar los tests): si el cambio deja el archivo con el mismo tamaño (intercambiar dos líneas) y se restaura en el mismo segundo, Python sigue usando el `.pyc` de la versión rota (valida su caché por tamaño y segundo). Después de restaurar, borrar los `__pycache__` (o tocar la fecha del archivo).
- Se verificó que los tests detectan bugs inyectados a propósito (combo, hitbox, rango del embestidor, dash perfecto, dashes extra, aturdido, fénix, Taller, peso de la vida, guardado de logros, combo en el perfecto, la oferta del nivel 3, la barra de energía, el perfecto solo con destruibles, la intercepción, la chance del ECO, DOBLE DASH desde el sector 3, y en la gasolinera: comprar una vez, créditos con el combo, reparar solo si falta y salir apaga `gasolinera`).
- Bots del scratchpad (se borran entre sesiones: si no están, se reescriben): `medir_creditos.py` (créditos por sector; los jefes se vencen al instante), `bot_sector.py` (partida entera eligiendo mejoras al azar), `medir_anomalias.py` (golpes/min; con `CAZA_RAIZ` apunta a otra carpeta, por ejemplo un `git worktree` de un commit viejo, para comparar), `app_completa.py` (la App entera a 144 FPS apretando teclas: pasa por Taller, jefes y Game Over).
- Para inspeccionar algo visual, sacar una captura de `app.pantalla` con `pygame.image.save` desde un script en el scratchpad que use `App(carpeta_datos=<scratchpad>)`. Filtrar la salida con `grep -a`, porque "¡" hace que grep la trate como binaria.

## Retoque visual (pedido del usuario: "altísimamente profesional, sin perder la esencia")
Por fases, mostrando capturas antes/después:
- **Hecho — Fase 1 (cimientos):** accesibilidad (temblor, destellos, CRT), Opciones con pestañas, CRT en la ventana, capas mundo/HUD, texto con contorno y en caché, textos flotantes, "+5" de congelados solo cerca de la nave (`DISTANCIA_PUNTOS_HIELO`).
- **Hecho — Fase 2 (HUD):** power-ups con cápsula y barra, combo por colores, desafío legible, barra central con el nombre del jefe y segmentos, marcador que cuenta, barras comunes.
- **Hecho — Fase 3 (rediseño visible, después de que el usuario pidió "algo que parezca un triple A"):** el kit `interfaz.py`, LB/RB y Q/E en todos los menús con pestañas, ayudas con los botones del control que se usa, transiciones de rombos, cinemática de ALERTA para cada jefe, y rehechas a todo el ancho: Inicio, Opciones, Pausa, Taller, Gasolinera, Dificultad, Logros, Iniciales, Game Over, READY/GO y la muerte de la nave.
- **Hecho — Fase 4 (impacto y mundo):** neón opcional (halos), ondas de choque, estelas y fogonazos de las balas, destello de la moneda, giro RotSprite de la nave, estrellas que titilan, salto al hiperespacio, niebla con borde en bandas y la opción ESCALADO SUAVE.
- **Hecho — Fase 5 (carteles del juego):** cola de avisos, pancarta de arriba, fichas que esquivan el aviso, logro abajo, momentos en franjas y el panel del rango (ver "Carteles del juego").
- **Hecho — Sonido:** el mezclador, el estudio, 252 efectos, ambientes, temas nuevos y uno por jefe (ver "Sonido y música"; `LISTA_DE_SONIDOS.md` completa).
- **Hecho — Sonidos limpios** (2026-10-14): los 6 patrones que saturaban (ver "Sonidos limpios" en El estudio) y todo recompuesto. **El usuario lo escuchó y lo aprobó** ("ahora sí se escucha bien").
- **Hecho — Mezcla y armonía** (2026-10-14): margen y limitador (0 recortes), efectos secos, `CAMPANA`/`METAL` armónicos, peligros con la tensión de la escala, efectos que siguen al acorde (11 colores) y los temas chiptune rehechos en el estudio. **Falta que el usuario lo escuche** jugando (los números no reemplazan al oído).
- **Hecho — Impacto de los momentos clave** (`impactos.py`, valores en config: `IMPACTO_*`, `CAMARA_LENTA_JEFE`, `HERIDA_MS`, `LATIDO_MS`, `VINETA_*`):
  - **Golpe final al jefe** (`Partida.golpe_final`, lo llama `Jefe.recibir_golpe` con vida 0): el cuadro de impacto, como en los juegos de pelea.
    - Hit-stop de `IMPACTO_PASOS` (24): los primeros `IMPACTO_DESTELLO` pasos, un destello blanco (no con DESTELLOS REDUCIDOS).
    - Después, el mundo oscuro (`NEGRO_VELO`) con el jefe y la nave redibujados encima (los protagonistas, iluminados), y rayos de bloques en el color del jefe que se recogen (`nuevo_impacto` los sortea una vez).
    - Después, `CAMARA_LENTA_JEFE` pasos de cámara lenta.
  - **Herida:** una viñeta roja que se apaga en `HERIDA_MS`; en el HUD, la vida perdida destella blanca (`_icono_blanco`) en vez de parpadear toda la fila.
  - **Última vida:**
    - el aviso urgente "¡ULTIMA VIDA!" (`AVISO_ULTIMA_VIDA`) con cinta de peligro;
    - la viñeta late con el corazón (`fuerza_de_la_vineta`, sincronizada con el sonido `latido`, ambos con `LATIDO_MS`);
    - la vida que queda se pinta de rojo en el golpe del latido (`impactos.latiendo`, `_icono_rojo`);
    - con DESTELLOS REDUCIDOS la viñeta queda quieta y la vida no late.
  - **Capas:** `Escena.dibujar_partida` dibuja `partida.dibujar_impactos` después del temblor y **antes del HUD** (el marcador siempre se lee).
  - `impactos.vineta(tamaño, color)` la usa también la Explosion.
  - Tests: `tests/test_impactos.py`, que detecta 7 errores inyectados.
- **Hecho — Presentación con logo:** advertencia, "HECHO CON PYGAME" y pantalla de título (ver "Presentación").
- **Lo que queda para el triple A** (lista que se le dio al usuario, en su orden): lo que quedó fuera de la grilla (íconos de vidas, MINI), modo demostración/tutorial, accesibilidad (remapear controles, daltonismo, HUD más grande, modo asistido) y variantes de planetas por código.

## Ideas pendientes (propuestas, aún sin hacer)
- Propuestas no elegidas: Torreta + Mina, Ladrón + Escudero, Fantasma + Barrera + Élites, Los Gemelos, fase 2 del Ojo.
- Música más intensa según el nivel y transiciones retro entre pantallas.
- HUD fijo (puntos, vidas) que se oscurece si hay algo debajo (los carteles y fichas ya lo hacen).
- Desafío diario (semilla fija), más logros (la pantalla LOGROS tiene lugar para 16: con más hay que paginar).

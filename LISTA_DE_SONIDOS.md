# Lista de sonidos — Caza Monedas

Esta es la lista de trabajo del sonido: cada sonido del catálogo de `MAPA_DE_AUDIO.md` con su **partitura** (notas, armonía, timbre y duración), lista para componerla con **el estudio** (`herramientas/componer.py`, ver CLAUDE.md, "El estudio"). La vamos completando de a poco: cuando un sonido se compone y se conecta al juego, se marca acá.

**Estados**
- ⬜ pendiente
- 🟨 compuesto: el archivo existe en `efectos/`, pero el juego todavía no lo usa
- ✅ listo: suena en el juego y tiene su test

Los códigos de la columna **Para** (`N01`, `FO07`...) son los eventos del mapa. Al terminar una fila, actualizar también la columna "Hoy" del mapa y anotar el avance en el **Registro** del final.

**Todo se hace de cero** (decisión del usuario): ningún efecto que vino hecho queda en el juego. Los 6 archivos viejos se reemplazan por sonidos nuevos compuestos con el estudio, siguiendo la base musical de la sección 0 (ver la sección 0.10). **La música también se rehace entera** (también `musica.mp3`). Al final, **cada archivo de `efectos/` sale de una obra del estudio** (`herramientas/estudio/obras/`): todo el sonido del juego se puede volver a generar y cambiar desde el código.

**La estética (pedido del usuario: "algo diferente, que inspire calidad, profesionalismo; que no suene chillón, que tenga cuerpo"):** se dejó el chiptune (la onda cuadrada es justamente lo chillón: medido, los efectos viejos tenían su brillo entre 4100 y 6900 Hz y la música vieja era mono) por un **synthwave retro-futurista**, que va con el neón y el CRT:
- sintes analógicos virtuales (sin aliasing, voces desafinadas en estéreo y filtros que respiran), pianos eléctricos y campanas FM, y batería con cuerpo;
- reverb de sala, delay ping-pong, chorus, bombeo (sidechain) y master con LUFS.

**Las metas medibles** (las muestra `componer.py`):
- brillo (centroide) de la música entre 1500 y 2500 Hz y de los efectos por debajo de ~3900 Hz;
- música a -14 LUFS, con el pico debajo de -1 dB;
- estéreo (correlación) entre 0.5 y 0.9.

---

## 0. La base musical (leer antes de componer)

### 0.1 En qué tonalidad está cada tema
Medido con un cromagrama de cada archivo (la energía de cada nota y la del bajo):

| Tema | Tonalidad | Cómo se midió |
|---|---|---|
| `musica_juego` (y sus colores), `musica_tension`, `musica_fin` | **La menor** | por composición: `Am F C G...` |
| `musica_menu` | **La menor** | por composición: `Am F C G` (tiene las mismas notas que Do mayor) |
| `musica_iniciales` | **Do mayor** | por composición: `C Am F G` |
| `musica_jefe` y los de cada jefe | **Re menor** | por composición: el bajo en Re y La |
| `musica_gasolinera` | **Fa mayor** | por composición: `Fmaj7 Dm7 Gm7 C7` |

Desde el 2026-10-14 **todos los temas salen del estudio** (los chiptune se rehicieron) y cada uno anota en su ficha (`efectos/fichas.json`) sus acordes y el color de cada compás: los efectos armónicos siguen al acorde (sección 0.11).

### 0.2 La paleta común: la pentatónica de Do
**Do Re Mi Sol La** (C D E G A) están en todas las escalas de los temas: Do mayor, La menor, Mi menor, Sol mayor, Re menor (Re Mi Fa Sol La Sib Do) y Fa mayor (Fa Sol La Sib Do Re Mi). Por eso:
- **Todo lo bueno y toda la interfaz se escriben con esas cinco notas**, en cualquier octava. Desde el 2026-10-14 además **siguen al acorde** (sección 0.11): la pentatónica de Do afina con la tonalidad, pero no con todos los acordes (sobre el Mi mayor del tema del juego, cada Sol chocaba con el Sol# del acorde).
- La tensión de los peligros sale **de la escala del tema**, no de afuera (sección 0.3).

### 0.3 La gramática (qué significa cada movimiento)
| Significa | Recurso musical | Ejemplo |
|---|---|---|
| Ganaste, sí, adelante | intervalos que **suben**: cuarta justa, quinta, octava; arpegios mayores | `ui_aceptar` Sol5→Do6 |
| Volver, no pasa nada | el mismo intervalo **bajando** | `ui_volver` Do6→Sol5 |
| Perdiste algo | segunda o tercera **menor que baja**, notas que se "desinflan" (bajan de tono) | `combo_cortado` Sol4→Mi4→Re4 |
| **Peligro / aviso** | **el tritono y la segunda menor DE LA ESCALA** (en La menor: Si–Fa, Mi–Fa, y la sexta menor Fa; en Re menor: Mi–Si♭, La–Si♭ y la sexta menor Si♭); una subida que **no resuelve** | `embestidor_apunta` Si3→Fa4 |
| La ventana para pegarle al jefe | **resolución sin tercera** (quintas y novenas: `sus2`): brilla y suena bien sobre mayor y menor | `vulnerable` La5 Re6 Mi6 La6 |
| Error de interfaz | pulso grave doble con **tritono** | `ui_error` Si2+Fa3 |
| Impacto | **ruido** + una nota grave que cae (sin melodía: no choca con nada) | `nave_golpe` |

**La regla de oro:** todo aviso de peligro termina en una tensión (tritono o semitono). La resolución llega cuando el jugador hace lo correcto (`vulnerable`, `perfecto`, `jefe_vencido`). Así el sonido cuenta la historia del baile: tensión → acción → alivio.

**La tensión, adentro de la escala** (2026-10-14): antes los peligros usaban notas de afuera (Mi♭ y Fa# sobre La menor, La♭ y Mi♭ sobre Re menor). Un aviso que suena una vez puede salirse; pero el ataque del Ojo, la carga de los cañones o el embestidor suenan cada pocos segundos, y repetidos se oían **desafinados** contra la música, no tensos. Por eso usan el tritono y las segundas menores que la escala ya tiene: el mismo intervalo, la misma tensión, sin salirse del tema. Quedan de afuera solo los raros y a propósito: la ¡ALERTA! (suena sola, en silencio), PESADILLA, el "trombón triste" de `desafio_fallado` y la presentación del jefe (La mayor, el V de Re: armonía funcional).

### 0.4 Registros (para que nada tape a nada)
Como en una mezcla profesional, cada familia vive en su franja de frecuencias:

| Franja | Octavas | Qué va |
|---|---|---|
| Brillo | 6-7 | interfaz, tics, chispas, hielo, `dash_listo` |
| Melodía | 5-6 | monedas, premios, jingles |
| Medio | 3-4 | avisos de peligro, voces de los jefes |
| Grave | 1-3 | impactos, explosiones, drones, jefes |
| Ruido | — | dash, golpes, viento, vapor: textura sin altura |

La música ocupa sobre todo las octavas 2-5. Por eso los efectos agudos (6-7) se oyen sin subir el volumen, y los impactos graves llevan mucho ruido para no ensuciar el bajo.

### 0.5 Timbre = categoría
Las partituras de abajo se escribieron para el compositor viejo (chiptune). **Al componerlas en el estudio, cada timbre viejo se traduce así** (los presets están en `herramientas/estudio/instrumentos.py`), y cada efecto se arma en **capas**: el tono (lo que canta), el cuerpo (un grave corto que le da peso) y el aire (ruido filtrado):

| Timbre viejo | En el estudio | Usos |
|---|---|---|
| `PULSO_FINO` (12.5 %) | `MARIMBA` o `PLUCK` (+ un clic de ruido) | interfaz, tics, zumbidos de insectos, la voz del Ojo |
| `PULSO_MEDIO` (25 %) | `EPIANO`, `PLUCK`, `LEAD_CALIDO` | jingles, melodías de premio |
| `PULSO_REDONDO` (50 %) | `LEAD_HUECO`, `PAD_OSCURO`, `METAL` | alarmas, sirenas, láseres, metales de la Fortaleza |
| `CAMPANA` | `CRISTAL` (corta) o `CAMPANA` (larga) | brillos, hielo, oro, cápsula, estrellas del rango, monedas |
| `BAJO` (triángulo) | `BAJO_SUB` o `BAJO_ANALOGICO` (con `barrido`) | resortes, golpes con altura, drones, el cuerpo de los impactos |
| `TECLADO` | `EPIANO` o `PAD_SUAVE` | acordes |
| ruido | `pista.ruido(...)` con su filtro y su forma | dash, explosiones, vapor, viento, cascabel, escombros |

**Las octavas de las partituras bajan cuando hace falta:** lo de la octava 6-7 con pulso (`ui_mover` E6) va una octava abajo con madera o cristal (E5), que tiene más armónicos propios. La nota sigue en la paleta, así que todo sigue afinando.

### 0.6 Escalas que crecen
- **Moneda**: una subida de cristal y la principal, con el piano una octava abajo. La principal sube por la pentatónica con el multiplicador y **cada multiplicador suma una capa**: el oído "lee" el combo sin mirar el HUD. La segunda voz es la última nota de la subida, que se queda sonando (nunca dos notas vecinas a la vez).

  | Sonido | Subida → principal | Capas |
  |---|---|---|
  | `moneda_1` | Sol5 → Do6 | cristal + piano |
  | `moneda_2` | La5 → Re6 | + segunda voz (La5) |
  | `moneda_3` | Do6 → Mi6 | + segunda voz (Do6) + brillo de la octava |
  | `moneda_4` | Sol5 Re6 → Sol6 | + una nota más en la subida (segunda voz Re6) |
  | `moneda_5` | La5 Re6 → La6 | + un destello de chispas |

- **Cadena de perfectos**: cada perfecto agrega una nota de un acorde de **Do abierto**. Antes era Do 6/9 (Mi Sol La Do Re): Sol y La juntos en el medio raspaban.

  | Sonido | Notas |
  |---|---|
  | `perfecto_1` | Sol5 |
  | `perfecto_2` | Do5 Sol5 |
  | `perfecto_3` | Do5 Sol5 Mi6 |
  | `perfecto_4` | Do5 Sol5 Do6 Mi6 |
  | `perfecto_5` | Sol4 Do5 Sol5 Do6 Mi6 |

  Todos llevan además el "slash" de ruido.
- **Barra del jefe al llenarse**: la escala de Re menor subiendo (Re5 Mi5 Fa5 Sol5 La5 Sib5 Do6 Re6...). El último segmento queda en La, sin resolver: la pelea empieza en tensión.
- **Estrellas del rango**: Do6 Re6 Mi6 Sol6 La6 (una por estrella).

### 0.7 El recorrido armónico de los grandes momentos
Los momentos están encadenados como una progresión:
- **Llegada del jefe:** la presentación toca **La** (el V de Re) en el nombre y en el apodo, y la música del jefe entra en **Re menor** (i). Es una cadencia: el tema llega como una resolución.
- **Victoria:** la pelea está en **Re menor**. `jefe_vencido` es una fanfarria en **Re mayor**: la "tercera de picardía", el truco barroco de terminar en mayor una obra menor.
- **Rango:** se canta en **Do mayor**, que es el **V de Fa**.
- **Gasolinera:** entra en **Fa mayor**. Sello y gasolinera forman una cadencia perfecta (V → I): llegar a la tienda suena a "llegué a casa".
- **READY? / GO!:** READY toca Do→Sol (termina en el V: es una pregunta). GO! es un acorde de **Do**, y la música del juego (Do mayor) entra en ese tiempo.

### 0.8 Las herramientas del compositor para efectos (✅ hechas)
Además de notas con pulso y triángulo y 4 golpes de batería, el compositor tiene (detalle en CLAUDE.md, "El compositor"):
1. **`barrido([(0, "A3"), (0.6, "Eb4")], instrumento, volumen)`**: una nota que cambia de altura siguiendo una curva (láseres, sirenas, cargas, caídas, resortes, power-down).
2. **`ruido(segundos, volumen, filtro=[(0, 800), (0.06, 6000)], pasa_altos, forma, chasquidos)`**: ruido con un filtro que se mueve (dash, explosiones, viento, vapor, succión) o que crepita (brasas, cascabel).
3. **`tremolo=(desde_hz, hasta_hz, profundidad)` y `vibrato=(desde_hz, hasta_hz, semitonos)`**: el volumen o la afinación oscilando, cada vez más rápido si se pide (zumbidos, alarmas, cargas que se aceleran). Valen en `secuencia` y `barrido`; `tremolo` también en `ruido`.

Con eso se hace toda la lista sin samples. También: `secuencia("G5:40 C6:90 C5+E5+G5:300")` (las partituras de esta lista se copian tal cual), `dinamica` (pp…ff: el pico del archivo), `medir()` y `--escuchar`.

**ffmpeg:** en esta computadora no hay. Los efectos se guardan en WAV, así que no hace falta. Solo los temas de música (y pasar `musica.mp3` a OGG) lo necesitan: instalarlo antes de esas filas (`winget install ffmpeg`).

### 0.9 Cómo leer la partitura
- Las notas van con el nombre del compositor (`C5` = Do5, `F#3` = Fa#3; `A4` = 440 Hz). Las flechas `→` son notas seguidas y `+` son notas juntas.
- Duraciones en ms. "Arpegio de 32avos" = notas de ~30 ms.
- **Volumen**:
  - **ff**: muy fuerte, los momentos;
  - **f**: fuerte;
  - **mf**: medio, la mayoría;
  - **p**: suave;
  - **pp**: casi imperceptible: tics, ambiente.

### 0.11 La mezcla y la armonía en vivo (2026-10-14)
Pedido del usuario: "los sonidos no se sienten tan armónicos, y cuando juego se siente mucho solapamiento y saturación de audio". Se midió con un bot que juega y una mezcla fuera de línea igual a la de SDL (suma los canales y recorta):

| Problema medido | Arreglo |
|---|---|
| **53 de 362 segundos recortados** (pico +3.5 dB): música y efectos al máximo, sin margen | `MEZCLA` con margen (música 0.5, efectos 0.7) y un **limitador** en el mezclador que sabe cuánto suena cada efecto (las fichas) y baja primero los detalles. Ahora: 0 recortes |
| Colas largas: una moneda duraba 1.1 s, `perfecto_1` 1.75 s; hasta 8 efectos a la vez | efectos más secos: cola 0.3 × la sala (era 0.6) y menos reverb (`retorno_sala` 0.3) |
| `CAMPANA` (FM 3.5) sumaba una tercera mayor a −5 dB sobre cada nota; `METAL` (1.41, 3.73) sonaba un cuarto de tono corrido | relaciones enteras: todos los parciales son armónicos de la nota |
| Peligros con notas de afuera, repetidos cada pocos segundos | la tensión de la propia escala (sección 0.3) |
| La pentatónica de Do choca con algunos acordes (Mi mayor, Si♭) | los premios y la interfaz **siguen al acorde** (abajo) |
| Temas chiptune mono, ~2 dB más fuertes y de otra estética | rehechos en el estudio (sección 11) |

**Armonía en vivo** (`herramientas/estudio/armonia.py`; como en Rez o Tetris Effect):
- Cada acorde tiene un **color**: la pentatónica que mejor le queda. Mayor: la de su fundamental. Menor: la de su relativo mayor (La menor → Do). Con séptima: la "dominante" (Do Re Mi Sol Si♭). Suspendido: sin tercera, la pentatónica mayor de su séptima (Mi sus4 → Re Mi Fa# La Si: así un efecto suena igual que en Do, un tono más arriba). Los temas usan 11: do, reb, re7, mi, mi7, misus, fa, sol, la, sib, do7.
- Los efectos **armónicos** (premios, power-ups, interfaz: `ARMONICOS`) se escriben en la pentatónica de Do, como siempre. El estudio los compone una vez por color cambiando cada nota por la del **mismo grado** del color: la escalera de la moneda sigue subiendo grado a grado, pero sobre las notas del acorde.
- El juego sabe en qué compás va el tema (cuándo empezó, sin las pausas) y toca el archivo de ese color, mirando 120 ms adelante (si el acorde cambia justo, el efecto ya suena en el nuevo). Sin música, el de Do.
- Los peligros, los golpes y la gasolinera (en Fa, la tonalidad de su tema) no siguen al acorde.

### 0.12 Sonidos limpios: los patrones que saturaban (2026-10-14)
Pedido del usuario: "muchos bien, pero otros muy saturados que rompen la experiencia" (aceptar y volver, la dificultad, el GO, la moneda, los power-ups, la cápsula, las cartas del Taller, la ventana del jefe). El dash, que "está espectacular", sirvió de referencia. Se midió cada efecto con una prueba nula (con y sin cada etapa), su **aspereza** (Plomp-Levelt: parciales a menos de una banda crítica) y un detector de notas que suenan juntas.

| # | Patrón | Arreglo | Regla para lo que venga |
|---|---|---|---|
| 1 | **La cinta del master recibía la mezcla sin nivelar.** Un acorde (varias notas sumadas) llegaba al triple que una nota sola y la curva lo aplastaba: intermodulación de −8 a −15 dB en ~70 efectos (el dash: −29). Era la causa de fondo | la cinta trabaja siempre con el pico en `NIVEL_CINTA` (−6 dB) y un `Efecto` no lleva cinta (`cinta=0`). La música también la tenía (−18 a −20 dB): recompuesta | el master no puede depender del nivel de las pistas (lo comprueba un test) |
| 2 | **Acordes cerrados** con segundas en el medio o el grave (Sol+La del 6/9, Re+Mi, La Re Mi del `vulnerable`, el disminuido de PESADILLA con un pad abajo) | voces abiertas: quintas, cuartas y octavas | en el medio y el grave, nada a menos de una tercera |
| 3 | **Un sonido fijo junto a uno que sigue al acorde.** `taller` estaba en Fa y las cartas que caen encima seguían al acorde: sobre Mi mayor, Fa contra Fa#. Las dificultades, en Do sobre el Mi mayor del menú | `taller` y las dificultades son ARMÓNICOS | lo que suena junto a un armónico, también armónico |
| 4 | **Sierras saturadas en acordes** (`LEAD_CALIDO` en el GO, `PLUCK` debajo de la moneda) | piano eléctrico y cristal; el GO de ff a f | las sierras, para melodías y bajos, no para acordes de efectos |
| 5 | **El grado cambia el intervalo.** Sobre un acorde con séptima el La pasa a ser la séptima: La+Mi se vuelve tritono y La+Do un tono. Sobre Mi sus4, contado desde Mi, Mi+Sol se volvía un tono | los acordes de los armónicos con Do, Re y Sol (no cambian en ningún color), el Mi o el La en la melodía; el sus se cuenta desde Re (sección 0.11) | lo comprueba un test, en los 11 colores |
| 6 | **Escalas rápidas en instrumentos que suenan largo** (Sol La Do Re Mi en 30 ms: el cristal sigue sonando y se apilan segundas): `combo_sube`, `combo_max`, `bonus`, `pw_hielo`, `oro_llega` | arpegios con saltos | en un instrumento con cola, arpegios, no escalas |

**Antes de componer un sonido nuevo, revisar la lista de verificación de "Sonidos limpios" en `CLAUDE.md`.**

Resultado (aspereza, el peor de 4 colores, antes → ahora): `vulnerable` 0.077 → 0.016, `taller` 0.071 → 0.017, `capsula` 0.048 → 0.005, `listo_go` 0.052 → 0.013, `dificultad_4` 0.104 → 0.029, `moneda_5` 0.032 → 0.013, `ui_aceptar` 0.019 → 0.008. Una nota sola de cristal o de piano da ~0.003; el ruido del dash, ~0.1 (en el ruido esta medida no sirve).

### 0.10 Los 6 efectos viejos: se reemplazan todos
Hoy cada efecto viejo cubre muchos eventos distintos (por eso suenan a "lo mismo para todo"). Cada uso pasa a su sonido nuevo. **Cuando el último uso de un efecto viejo se reemplaza, se borra su archivo de `efectos/` y su línea del `CATALOGO`.**

| Efecto viejo (archivo) | Usos | Cada uso pasa a… | Estado |
|---|---|---|---|
| `seleccion` (`seleccion.wav`) | 24 | mover → `ui_mover` · aceptar → `ui_aceptar` · volver → `ui_volver` · pestañas → `ui_pestana` · cambiar un ajuste → `ui_valor` / `ui_llave_si` / `ui_llave_no` · confirmación → `ui_alerta` · cambiar dificultad → `dificultad` · empezar partida → `ui_empezar` · iniciales → `ui_aceptar` · salir de la gasolinera → `ui_volver` + `hiperespacio` · hangar → `hangar_nave` · **dash perfecto → `perfecto_N`** · subir de nivel → `nivel` · desafío nuevo → `desafio_nuevo` · rango B/C → `sello_B` / `sello_C` | ✅ reemplazado y borrado |
| `golpe` (`golpe.wav`) | 18 | te pegan → `escudo_roto` / `nave_golpe` · destruir enemigo → `enemigo_roto` · interceptar → `interceptado` · NOVA → `nova` · romper proyectil → `bala_rota` · mina → `mina_estalla` · llamarada → `llamarada` · golpes al jefe → `jefe_golpe` / `jefe_parte` / `parte_rota` · explosión del jefe → `jefe_explota` · láser → `laser` · coraza → `coraza` · cortinas → `escombros` · estrellarse → `estrellarse` · choques de Serpiente y Colmena → `serpiente_choca` / `colmena_choca` · exhalar → `exhalar` · **no alcanzan los créditos → `ui_error`** | ✅ reemplazado y borrado |
| `nuevo_record` (`nuevo_record.wav`) | 8 | récord → `record` · logro → `logro` · **oleada → `oleada`** · anomalía → `asteroides_llega` / `tormenta_llega` / `niebla_llega` / `oro_llega` · FÉNIX → `fenix` · rango S/A → `sello_S` / `sello_A` · Taller → `taller` · gasolinera → `tienda` | ✅ reemplazado y borrado |
| `powerup` (`moneda_brillante.wav`) | 7 | power-up → `pw_escudo` … `pw_nova` · mejora → `mejora_elegida` · ESCUDO ROCE → `pw_escudo` · oleada superada → `oleada_superada` · desafío cumplido → `desafio_cumplido` · jefe vencido → `jefe_vencido` · compra → `caja` + `mejora_elegida` | ✅ reemplazado y borrado |
| `moneda` (`moneda.wav`) | 3 | moneda → `moneda_1` … `moneda_5` · congelado roto → `hielo_roto` · compra → `caja` | ✅ reemplazado y borrado |
| `game_over` (`game_over.wav`) | 1 | se recompone con el mismo nombre (sección 6) | ✅ reemplazado y borrado |

Al borrar el último, sumar a `tests/test_sonido.py` un test que compruebe que **cada archivo del `CATALOGO` está en `COMPOSICIONES`** (así nunca vuelve a entrar un sonido que no salga del código).

---

## 1. Interfaz (`INTERFAZ`)
| Estado | Sonido | Para | Prio | Partitura | Timbre y forma |
|---|---|---|---|---|---|
| ✅ | `ui_mover` (2 variantes: `ui_mover_1`, `ui_mover_2`) | I01, PA03, OP01, GA03 | P1 | **a:** E6 · **b:** G6, 30 ms cada una (se turnan) | `PULSO_FINO`, ataque 0, cae en 25 ms · p |
| ✅ | `ui_aceptar` | I02, IR02 | P1 | G4 (55 ms) → C5 (220 ms): cuarta que sube, el "sí"; la madera una octava arriba, suave | `EPIANO` + `MARIMBA` · mf |
| ✅ | `ui_volver` | I03 | P1 | C5 (55 ms) → G4 (220 ms): la misma cuarta, bajando | `EPIANO` + `MARIMBA` · mf |
| ✅ | `ui_error` | I04, GA05 | P1 | F#3 + C4 juntas (tritono), dos golpes de 60 ms con 30 ms de aire | `PULSO_REDONDO` sin vibrato, filtrado · mf |
| ✅ | `ui_pestana` | I05, OP02 | P2 | ruido "fsst" de 60 ms (el filtro sube) + D6 de 40 ms al final | ruido + `PULSO_FINO` · p |
| ✅ | `ui_valor` | OP03 | P2 | subir: C5 → E5 · bajar: E5 → C5 (25 ms + 50 ms; una tercera: Re-Mi raspaba) | `MARIMBA` · p |
| ✅ | `ui_llave_si` / `ui_llave_no` | OP04, I07 | P2 | sí: clic + C6 → G6 · no: clic + G5 → C5 | clic de ruido de 8 ms + `PULSO_MEDIO` · mf |
| ✅ | `ui_alerta` | I08 | P2 | B4 + F5 (tritono), 150 ms con vibrato; después A4 sola | `PULSO_REDONDO` · mf |
| ✅ | `ui_transicion` | I06 | P3 | ruido de 420 ms: el filtro sube hasta la mitad y baja (como los rombos) | ruido · pp |
| ✅ | `ui_empezar` | DI04, FI04 | P1 | arpegio C5 E5 G5 C6 (40 ms cada una) → acorde Cadd9 (C5 E5 G5 D6) de 300 ms + bombo en el acorde: "insert coin" | `PULSO_MEDIO` + bombo · f |
| ✅ | `ui_apagar` | IN04 | P2 | G5 E5 C5 (50 ms cada una) → C4 de 200 ms que se desinfla + clic de CRT (ruido de 15 ms) | `PULSO_MEDIO` + barrido hacia abajo · mf |
| ✅ | `ui_tecla` | IR01 | P1 | una nota de 30 ms según la letra: A=C5 y sube por la pentatónica (C D E G A), dando la vuelta cada 5 letras | `PULSO_FINO` · p |
| ✅ | `pausa` | PA01, S01 | P1 | E6 → A5 (60 ms + 120 ms), con eco | `CAMPANA` · mf |
| ✅ | `seguir` | PA02 | P1 | A5 → E6 (60 ms + 120 ms) | `CAMPANA` · mf |

## 2. La nave
| Estado | Sonido | Para | Prio | Partitura | Timbre y forma |
|---|---|---|---|---|---|
| ✅ | `nave_dash` (3 variantes: `nave_dash_1` ... `_3`) | N01 | P1 | **sin altura** (así nunca desafina). 180 ms (`DASH_DURACION`): el filtro del ruido sube de 800 a 6000 Hz en 60 ms y baja en 120 ms. Variantes: el pico en 5000, 6000 y 7000 Hz | ruido · mf (nunca más fuerte que la moneda) |
| ✅ | `nave_dash_extra` | N02 | P2 | el mismo con el pico en 9000 Hz + un "tin" E7 de 40 ms al final | ruido + `CAMPANA` · mf |
| ✅ | `dash_listo` | N03 | P2 | E7 de 50 ms, cae enseguida (una gota de luz) | `CAMPANA` sin eco · pp |
| ✅ | `dash_vacio` | N04 | P3 | clic de 10 ms + C3 de 30 ms apagado | ruido + `BAJO` · pp |
| ✅ | `escudo_roto` | N05 | P1 | ruido agudo de 120 ms (vidrio) + los pedazos: arpegio que cae E7 C7 A6 E6 (25 ms cada uno) | ruido + `CAMPANA` · f |
| ✅ | `nave_golpe` | N06 | P1 | ruido de 200 ms (el filtro baja de 4000 a 300 Hz) + barrido del `BAJO` de 220 a 55 Hz. Suena entero durante el hit-stop | ruido + triángulo · f |
| ✅ | `ultima_vida` | N07 | P1 | alarma de tritono B5 / F5 alternando cada 90 ms, 4 notas, dos veces con 120 ms de aire | `PULSO_REDONDO` · f |
| ✅ | `latido` (opcional) | N07 | P3 | dos golpes graves (C2 80 ms, C2 60 ms, 120 ms entre ellos), cada 1.5 s | bombo suave · pp |
| ✅ | `fenix` | N08 | P1 | llamarada: ruido que sube 300 ms. Después **de La menor a Do mayor** (de la muerte a la vida): arpegio A4 C5 E5 (40 ms cada una) → acorde C5 E5 G5 C6 de 500 ms con vibrato | ruido + `PULSO_MEDIO` · f |
| ✅ | `nave_muerte` (+ `_lenta`) | EX01, N09 | P1 | explosión: ruido de 1.2 s (el filtro baja de 8000 a 100 Hz) + `BAJO` de 110 a 30 Hz. La versión lenta dura el doble (para `CAMARA_LENTA`) | ruido + triángulo · ff |
| ✅ | `hiperespacio` | F01, LI01, GA13 | P1 | 1.5 s como `velocidad_salto()` (sube y baja como un seno): el filtro del ruido sube y baja + barrido de pulso de C3 a C6 y vuelta, con eco | ruido + `PULSO_REDONDO` · f |

## 3. Monedas, combo y puntos
| Estado | Sonido | Para | Prio | Partitura | Timbre y forma |
|---|---|---|---|---|---|
| ✅ | `moneda_1` ... `moneda_5` | P01, P02 | P1 | adorno de 35 ms → principal de 140 ms (ver la tabla de la sección 0.6) | `PULSO_MEDIO` (ciclo 25 %), sin vibrato · mf |
| ✅ | `moneda_oro` | P03 | P2 | `moneda_N` + campanita una octava arriba de la principal, 30 ms después | + `CAMPANA` · mf |
| ✅ | `combo_sube` | P04 | P1 | 3 notas de 40 ms con saltos que terminan en la principal de la moneda nueva: a x2 D5 G5 D6, a x3 C5 G5 E6, a x4 G5 D6 G6 | `CRISTAL` + `EPIANO` · mf |
| ✅ | `combo_max` | P05 | P1 | arpegio C5 G5 C6 E6 G6 (30 ms cada una) → acorde abierto C6 + G6 + C7 de 450 ms, sobre C4 G4 E5 | `CRISTAL` + `EPIANO` + bombo · f |
| ✅ | `combo_cortado` | P06 | P2 | G5 → Eb5 (80 ms + 160 ms) desinflándose (la segunda baja 50 cents) | `PULSO_FINO` · p |
| ✅ | `perfecto_1` ... `perfecto_5` | P07 | P1 | "slash": ruido de 60 ms con el filtro bajando de 9000 a 2000 Hz + las notas de la cadena (sección 0.6), a 25 ms entre una y otra, que suenan 150 ms | ruido + `CAMPANA` · f |
| ✅ | `interceptado` | P08 | P1 | "clang": A4 + E5 + C#6 (golpe de metal con armónicos no afinados) de 150 ms, caída rápida + ruido de 30 ms | `PULSO_REDONDO` + ruido · f |
| ✅ | `record` | P09 | P1 | jingle arcade a 180 bpm en Do: `C5 E5 G5 C6 . G5 C6 E6 . . . -` (semicorcheas), con el bajo en C3 y G3 y un platillo abierto en el último E6 | `PULSO_MEDIO` + `BAJO` + batería · ff |
| ✅ | `nivel` | P10 | P1 | arpegio C5 E5 G5 C6 (35 ms cada una) + C6 sostenida 150 ms con vibrato | `PULSO_MEDIO` · mf |
| ✅ | `bala_rota` | P12, D08 | P1 | "pop" de ruido de 50 ms + D6 de 30 ms | ruido + `PULSO_FINO` · mf |
| ✅ | `contador` | FI01, GA06 | P2 | un tic de 15 ms que se repite: la altura sube de C5 a C7 mientras cuenta y termina en un "ding" C7 + G7 de 200 ms | `PULSO_FINO` + `CAMPANA` · p |

## 4. Power-ups y mejoras
Cada power-up tiene un motivo propio (forma y timbre distintos), siempre en la paleta común.

| Estado | Sonido | Para | Prio | Partitura | Timbre y forma |
|---|---|---|---|---|---|
| ✅ | `capsula` | W01 | P2 | G6 → D6 (cuarta que cae: "llegó algo"; Sol-Re es cuarta en todos los colores), 60 ms + 220 ms con eco, y el piano una octava abajo | `CRISTAL` + `EPIANO` · p |
| ✅ | `pw_escudo` | W04, M05, GA10 | P1 | barrido de C4 a C5 (150 ms) → quinta abierta C5 + G5 + C6 de 300 ms con vibrato lento (una armadura) | `PULSO_REDONDO` · f |
| ✅ | `pw_hielo` | W05 | P1 | cascada que cae por quintas y cuartas: G6 D6 G5 D5 G4 (35 ms cada una, con eco) + crujido de ruido. Con la escala entera se apilaban segundas | `CRISTAL` + ruido · f |
| ✅ | `pw_vida` | W06, GA09 | P1 | "1UP": G4 C5 E5 G5 E5 C6 (termina en la octava; en La chocaba con el Mi sobre un acorde con séptima) | `EPIANO` + `CRISTAL` una octava arriba · f |
| ✅ | `pw_iman` | W07 | P2 | D5 con vibrato enorme (±1 semitono, 12 Hz) de 300 ms, que se desliza hasta A5 | `PULSO_FINO` · mf |
| ✅ | `pw_doble` | W08 | P2 | C6 (80 ms) → C7 (200 ms): la octava, "el doble" | `CAMPANA` · f |
| ✅ | `pw_turbo` | W09 | P2 | motor que acelera: arpegio C4 E4 G4 repetido, cada vuelta más rápida (60 → 20 ms por nota) mientras todo sube a C5; 400 ms | `PULSO_REDONDO` · f |
| ✅ | `pw_recarga` | W10 | P2 | carga eléctrica: arpegio de 32avos C5 E5 G5 C6 E6 G6 C7 + chispa de ruido | `PULSO_FINO` · f |
| ✅ | `pw_nova` | W11 | P2 | drone C3 + G3 (quinta grave, en todos los colores) de 550 ms con trémolo que se acelera (4 → 14 Hz) + sub C2 | `PAD_OSCURO` + `BAJO_SUB` · mf |
| ✅ | `nova` | W12 | P1 | ruido de 600 ms (el filtro baja de 7000 a 150 Hz) + barrido del `BAJO` de 165 a 40 Hz + campanita A6 al final (el anillo) | ruido + triángulo · f |
| ✅ | `pw_acaba` | W13 | P2 | E6 de 25 ms (sale 3 veces: a 1.5, 1 y 0.5 s; cada una un poco más fuerte) | `PULSO_FINO` · pp → p |
| ✅ | `pw_fin` | W14 | P2 | power-down: G5 E5 C5 (40 ms cada una), la última se desinfla un semitono | `PULSO_MEDIO` · p |
| ✅ | `hielo_roto` (3 variantes) | W15 | P1 | crujido de ruido agudo de 80 ms + una nota de cristal: E7 / G7 / A7 | ruido + `CAMPANA` · mf |
| ✅ | `mejora_elegida` | M01, TA04, GA04 | P1 | el acorde que se abre: C5, después + G5, + D6, + E6, + A6 (25 ms entre una y otra), sostenido 400 ms con eco. Es un Do 6/9: suena bien sobre todos los temas, también en la gasolinera (Fa) | `PULSO_MEDIO` + `CAMPANA` · f |
| ✅ | `onda` (2 variantes) | M02 | P2 | "fuuum": `BAJO` de 110 a 55 Hz en 200 ms + ruido grave · variante 2: de 98 a 49 Hz | triángulo + ruido · p |
| ✅ | `eco` | M03 | P2 | `nave_dash` con el filtro más bajo (pico 3500 Hz) + eco de 3 repeticiones | ruido · p |
| ✅ | `roce_carga` | M04 | P3 | un tic según la carga, en la pentatónica: C6, D6, E6... (40 ms) | `CAMPANA` · pp |

## 5. Enemigos y proyectiles
Los avisos de peligro **duran exactamente lo mismo que el aviso visual** y terminan en una tensión.

| Estado | Sonido | Para | Prio | Partitura | Timbre y forma |
|---|---|---|---|---|---|
| ✅ | `aparece` | E01, D20 | P2 | se materializa: barrido corto que sube (C5 → C6, 80 ms) + D6 de 20 ms | `PULSO_FINO` · pp |
| ✅ | `enemigo_roto` (3 variantes × 3 tamaños) | E03, M06 | P1 | crunch de ruido de 90 ms + una nota que cae una octava en 60 ms. Altura según el tamaño: grande C4, mediano G4, chico C5. Variantes: el filtro del ruido | ruido + `BAJO` · mf |
| ✅ | `aturdido` | E05 | P3 | "pío-pío": A7 → E7 → A7 → E7, 30 ms cada una, con vibrato rápido | `PULSO_FINO` · pp |
| ✅ | `rebote` (4, uno por pared) | E08 | P2 | "boing" de resorte: el `BAJO` baja una quinta y vuelve, con vibrato que se apaga, 150 ms. Abajo C4, arriba G4, izquierda E4, derecha A4 | triángulo · p |
| ✅ | `embestidor_apunta` | E09 | P1 | 600 ms: sube cromáticamente de A3 a Eb4 (tritono: no resuelve) con trémolo que se acelera (6 → 16 Hz) | `PULSO_FINO` · mf |
| ✅ | `mira_fija` | E10 | P1 | clic de 10 ms + Bb5 de 80 ms seco: la séptima menor, un pinchazo que queda en el aire | ruido + `PULSO_REDONDO` · f |
| ✅ | `embestida` | E11 | P1 | whoosh: el filtro del ruido baja en 400 ms + Eb4 → A3 que cae (el tritono vuelve abajo) | ruido + `PULSO_FINO` · mf |
| ✅ | `divisor_parte` (grande, mediano, chico) | E12 | P2 | "splat" gelatinoso: el `BAJO` cae una sexta en 80 ms con vibrato rápido + ruido húmedo (filtro bajo). Alturas: C4 / G4 / C5 | triángulo + ruido · mf |
| ✅ | `enjambre_aviso` | E13 | P1 | 450 ms: zumbido que sube de F#4 a C5 (tritono) con trémolo de 30 Hz (las alas) | `PULSO_FINO` · mf |
| ✅ | `enjambre_picada` | E14 | P2 | barrido que cae de C6 a C4 en 350 ms + zumbido | `PULSO_FINO` · p |
| ✅ | `bonus` | E15 | P2 | arpegio G5 A5 C6 D6 E6 G6 (30 ms cada una) + G6 sostenida 150 ms | `PULSO_MEDIO` · mf |
| ✅ | `abeja_sale` | E16, CO03 | P2 | bzz: A4 de 100 ms con trémolo de 35 Hz | `PULSO_FINO` · pp |
| ✅ | `abeja_aviso` | E17 | P1 | 400 ms: el bzz sube de A4 a Eb5 (tritono) y se acelera | `PULSO_FINO` · mf |
| ✅ | `retirada` | E19, D03, J03 | P3 | "poof": ruido de 250 ms con el filtro bajando + E5 → C5 muy suave | ruido + `PULSO_FINO` · pp |
| ✅ | `mina_tic` | B01 | P1 | Bb5 de 40 ms (fuera de la paleta: peligro). Sale 4 veces en los últimos 500 ms: a 0, 200, 340 y 440 ms | `PULSO_REDONDO` · mf |
| ✅ | `mina_estalla` | B02 | P1 | ruido seco de 250 ms + `BAJO` de 130 a 45 Hz | ruido + triángulo · f |

## 6. Oleadas, anomalías, desafíos y carteles
| Estado | Sonido | Para | Prio | Partitura | Timbre y forma |
|---|---|---|---|---|---|
| ✅ | `oleada` | D01 | P1 | alarma: A4 / Eb5 (tritono) alternando cada 120 ms, 3 veces + bombo en cada A4 | `PULSO_REDONDO` + batería · f |
| ✅ | `oleada_superada` | D02 | P1 | fanfarria en Do a 160 bpm: `G4 C5 . E5 G5 . C6 . . .` + acorde C5 E5 G5 C6 al final | `PULSO_MEDIO` + `BAJO` · f |
| ✅ | `asteroides_llega` | D05 | P1 | retumbo: ruido grave de 1 s + drone C2 con Ab2 (sexta menor: amenaza) | ruido + triángulo · f |
| ✅ | `meteoro_aviso` | D06 | P1 | 900 ms: silbido que cae de G6 a G5 (sin tensión: es una caída, no un ataque) | `PULSO_FINO`, sin vibrato · p, con paneo |
| ✅ | `tormenta_llega` | D09 | P1 | chisporroteo (ráfagas de ruido) + arpegio disminuido rápido B4 D5 F5 Ab5 (32avos, dos vueltas): electricidad | ruido + `PULSO_FINO` · f |
| ✅ | `tormenta_aviso` | D10 | P1 | 1.2 s: crepitar cada vez más denso + nota que sube de E4 a Bb4 (tritono) | ruido + `PULSO_FINO` · mf |
| ✅ | `llamarada` | D11 | P1 | rugido: ruido ancho de 450 ms (filtro de 3000 Hz abierto) + `BAJO` en C2 | ruido + triángulo · f |
| ✅ | `niebla_llega` | D12 | P1 | viento hueco: ruido con el filtro que sube y baja lento (1.5 s) + A3 E4 B4 (una quinta y una novena: fantasmal) que aparecen y se van | ruido + `PULSO_REDONDO` · mf |
| ✅ | `oro_llega` | D14 | P1 | lluvia de oro: C7 A6 G6 E6 D6 C6 cayendo con swing (40 ms) + arpegio que sube C6 E6 G6 C7 | `CAMPANA` · f |
| ✅ | `anomalia_fin` | D15 | P2 | se disipa: el filtro del ruido baja en 600 ms + quinta abierta C5 + G5 que se apaga | ruido + `PULSO_REDONDO` · p |
| ✅ | `desafio_nuevo` | D16 | P2 | G5 → D6 (quinta que sube y queda abierta: "¿podrás?"), 60 ms + 200 ms | `PULSO_MEDIO` · mf |
| ✅ | `desafio_cumplido` | D18 | P1 | G5 C6 E6 (40 ms cada una) → acorde C6 + E6 + G6 + A6 de 350 ms | `PULSO_MEDIO` + `CAMPANA` · f |
| ✅ | `desafio_fallado` | D19 | P1 | "trombón triste": E5 Eb5 D5 (100 ms cada una) → Db5 de 300 ms que se desinfla, con vibrato | `PULSO_REDONDO` · mf |
| ✅ | `ficha_enemigo` | C03 | P2 | deslizamiento (ruido de 120 ms con el filtro subiendo) + B4 → F5 (tritono que sube): "ojo con este" | ruido + `PULSO_FINO` · mf |
| ✅ | `logro` | C05 | P1 | trofeo a 150 bpm: `E5 G5 C6 . E6 . G6 . . .` + C7 brillando 400 ms con eco (distinto de `record`: campana y sin bajo) | `CAMPANA` + `PULSO_MEDIO` · f |
| ✅ | `nave_nueva` | C05 | P3 | G6 → C7 → E7 (50 ms cada una) | `CAMPANA` · mf |
| ✅ | `teclear` (3 variantes) | C02, C10, DI02, FI02 | P3 | tic de ruido de 8 ms + una nota de la pentatónica al azar en la octava 6, de 10 ms | ruido + `PULSO_FINO` · pp |
| ✅ | `estrella` (5) | C08 | P2 | C6 / D6 / E6 / G6 / A6 (una por estrella ganada), 200 ms con eco | `CAMPANA` · mf |
| ✅ | `sello_S` | C09 | P1 | **Do mayor (V de Fa).** Golpe (bombo + platillo abierto) + fanfarria a 160 bpm `G4 C5 E5 G5 C6 . . .`, arpegio de 32avos C E G subiendo dos octavas y acorde final C5 E5 G5 C6 E6 de 700 ms con vibrato | `PULSO_MEDIO` + `BAJO` + batería · ff |
| ✅ | `sello_A` | C09 | P1 | golpe + E5 G5 C6 (40 ms cada una) → acorde C5 E5 G5 C6 de 400 ms | `PULSO_MEDIO` + bombo · f |
| ✅ | `sello_B` | C09 | P1 | golpe + Csus4 (C5 F5 G5) que resuelve a C (F5 → E5): neutro, "está bien" | `PULSO_MEDIO` + bombo · mf |
| ✅ | `sello_C` | C09 | P1 | golpe seco + quinta sin tercera C3 + G3 de 150 ms, sin brillo | `BAJO` + bombo · mf |
| ✅ | `sector_nuevo` (5, uno por sector) | C10 | P2 | un acorde de Do mayor para cada bioma, arpegiado (40 ms) y sostenido 600 ms. Cinturón **Cadd9** (luminoso), Carmesí **Am** (oscuro), Esmeralda **Fmaj7** (mágico), Ámbar **Gsus4 → G** (expectante), Abismo **Em** (el más oscuro) | `PULSO_MEDIO` + `CAMPANA` · f |
| ✅ | `barra_jefe` | C11 | P2 | tic de 30 ms por segmento: la escala de Re menor subiendo desde D5. El último segmento suena en La (sin resolver) | `PULSO_FINO` · p |
| ✅ | `listo_ready` | LI02 | P1 | C5 (150 ms) → G5 (300 ms): termina en el V, es una pregunta | `PULSO_MEDIO` · f |
| ✅ | `listo_go` | LI03 | P1 | bombo + La abierto sin tercera (A3 E4 A4 E5, rasgueado) + La5 que brilla + sub A2 + un soplo que cae (en vez del platillo) | `EPIANO` + `LEAD_HUECO` + `CRISTAL` · f (era ff, con sierras saturadas) |
| ✅ | `destruida` | EX02 | P2 | acorde de La menor grave A2 C3 E3 sostenido 1 s, que cae un cuarto de tono mientras se apaga | `PULSO_REDONDO` + `BAJO` · mf |
| ✅ | `game_over` (reemplaza a `game_over.wav`) | EX03 | P1 | **desde cero.** La menor, lento (90 bpm): `A4:300 E4:300 C4:300` → acorde A2 + E3 + A3 de 900 ms que cae un cuarto de tono, + bombo en la primera nota | `PULSO_MEDIO` + `BAJO` + bombo · f |
| ✅ | `record_guardado` | IR03 | P2 | C5 E5 G5 C6 (40 ms cada una) + acorde de 300 ms | `PULSO_MEDIO` · f |

## 7. Jefes: comunes
**Tonalidad de las peleas: Re menor** (la de `musica_jefe`). La tensión usa el **tritono de Re (La bemol)** y la **segunda menor frigia (Mi bemol)**.

| Estado | Sonido | Para | Prio | Partitura | Timbre y forma |
|---|---|---|---|---|---|
| ✅ | `alerta` (loop) | J01 | P1 | sirena de tritono D5 / Ab5 alternando cada 175 ms (4 por segundo), mientras duran las luces (1.4 s) | `PULSO_REDONDO` · f |
| ✅ | `franjas` | J01, C07 | P1 | clunk: ruido metálico de 80 ms + D2 de 150 ms | ruido + `BAJO` · f |
| ✅ | `presentacion` | J02 | P1 | **la cadencia de llegada.** Nombre: golpe + acorde de La (A3 C#4 E4, el V) de 300 ms. Apodo: golpe + A2 + A3 más fuerte. La música del jefe entra en Re: V → i | `PULSO_REDONDO` + `BAJO` + bombo · ff |
| ✅ | `vulnerable` | J04 (y OJ05, FO09, SE05, SE06, CO04, SI07) | P1 | **la resolución, sin tercera:** G4 D5 G5 D6 (quintas y cuartas, 30 ms) que sostiene 350 ms con eco, sobre C4 G4 D5 abiertas | `CRISTAL` + `EPIANO` · f |
| ✅ | `jefe_golpe` | J05 | P1 | impacto: ruido de 300 ms (el filtro baja de 6000 a 200 Hz) + `BAJO` de D3 a D1 + la voz del jefe encima | ruido + triángulo · ff |
| ✅ | `jefe_parte` | J06 | P1 | como `jefe_golpe`, más corto (180 ms) y en La (A2 → A1) | ruido + triángulo · f |
| ✅ | `parte_rota` | J07, FO10, CO05 | P1 | crash de ruido de 400 ms + arpegio de Re menor que cae A4 F4 D4 A3 (40 ms cada una) | ruido + `PULSO_REDONDO` · f |
| ✅ | `golpe_final` | J08 | P1 | el impacto más grande: ruido de 500 ms + `BAJO` de D2 a D0 + 250 ms de silencio al final (la música ya se cortó) | ruido + triángulo · ff |
| ✅ | `agonia` (3 variantes) | J09, FO11 | P1 | explosiones chicas: ruido de 150 ms + D2 / A1 / F2 (Re menor que se derrumba) | ruido + triángulo · mf |
| ✅ | `jefe_explota` | J10 | P1 | ruido de 2 s (el filtro baja de 9000 a 60 Hz) + `BAJO` de D2 a D0, con dos réplicas a 400 y 900 ms | ruido + triángulo · ff |
| ✅ | `jefe_vencido` | J10, C06 | P1 | **tercera de picardía: Re MAYOR.** Fanfarria a 150 bpm: `A4 D5 F#5 A5 . . D6 . . . . .` con bajo D3 A2 D3, bombo y platillo abierto en el D6, acorde final D5 F#5 A5 D6 de 800 ms | `PULSO_MEDIO` + `BAJO` + batería · ff |

## 8. Jefes: cada uno
**EL OJO** (Cinturón)
| Estado | Sonido | Para | Prio | Partitura | Timbre y forma |
|---|---|---|---|---|---|
| ✅ | `ojo_flota` (loop) | OJ01 | P3 | drone D2 con trémolo lento (1 Hz) | `BAJO` · pp |
| ✅ | `ojo_carga` | OJ02 | P1 | 700 ms: sube cromáticamente de D4 a Ab4 (tritono) con trémolo que se acelera (5 → 20 Hz) y termina en el primer disparo | `PULSO_FINO` · f |
| ✅ | `ojo_abanico` | OJ03 | P1 | zap: barrido que cae de A6 a A4 en 120 ms + ruido de 20 ms | `PULSO_REDONDO` · mf |
| ✅ | `ojo_anillo` | OJ04 | P1 | zap más grave, de D6 a D4 en 160 ms, con eco | `PULSO_REDONDO` · mf |
| ✅ | `ojo_cansado` | OJ05 | P2 | vapor (ruido de 300 ms con el filtro bajando) + F4 → D4 que se desinfla (está agotado) | ruido + `PULSO_FINO` · mf |
| ✅ | `ojo_cierra` | OJ06 | P3 | clac: ruido de 15 ms + A3 de 40 ms | ruido + `BAJO` · p |
| ✅ | `ojo_voz` (por vida) | OJ07 | P2 | grito electrónico: barrido de A5 a D5 en 200 ms con vibrato. Más grave cuanta menos vida le queda (baja un tono por golpe) | `PULSO_FINO` · f |

**ACORAZADO IMPERIAL** (Carmesí): una marcha militar en el pulso.

| Estado | Sonido | Para | Prio | Partitura | Timbre y forma |
|---|---|---|---|---|---|
| ✅ | `compas` (2: acento y normal) | FO01 | P2 | tic metálico por pulso: el primero en D3 (acento, más fuerte), los otros en A3. Ruido de 10 ms + la nota de 40 ms | ruido + `PULSO_REDONDO` · p |
| ✅ | `motor_pesado` | FO02 | P3 | ruido grave con un pulso de 8 Hz (orugas), 1 s | ruido · pp |
| ✅ | `carga_canon` (4: ráfaga, misiles, láser, minas) | FO03 | P2 | chispas de ruido + una nota según el ataque: ráfaga D4, misiles F4, láser A4, minas C4, que sube un semitono en el pulso de carga | ruido + `PULSO_FINO` · p |
| ✅ | `obus` | FO04 | P1 | cañonazo: ruido de 200 ms + `BAJO` de D2 a D1 | ruido + triángulo · f |
| ✅ | `misil` | FO05 | P1 | lanzamiento (ruido de 250 ms que se va) + bip A5 de 20 ms cada 200 ms mientras te sigue | ruido + `PULSO_FINO` · mf |
| ✅ | `laser_carga` | FO06 | P1 | barrido de A3 a A5 en un pulso (520 ms) con trémolo que se acelera | `PULSO_REDONDO` · f |
| ✅ | `laser` (loop) | FO07 | P1 | zumbido: D3 + D4 (octava) con vibrato rápido (8 Hz) + un poco de ruido. Suena mientras `laser_prendido` y se corta en seco | `PULSO_REDONDO` · f |
| ✅ | `mina_lanza` | FO08 | P2 | thunk: D3 de 60 ms + ruido de 20 ms | `BAJO` + ruido · mf |
| ✅ | `recalentado` | FO09 | P2 | vapor (ruido de 1 s con el filtro bajando) + tics de metal que se enfría (A6 de 10 ms, al azar, cada vez más espaciados) | ruido + `PULSO_FINO` · p |
| ✅ | `coraza` | FO12 | P1 | crash enorme de 800 ms + arpegio de Re menor que cae D5 A4 F4 D4 A3 D3 | ruido + `PULSO_REDONDO` + `BAJO` · ff |
| ✅ | `cortina_aviso` | FO13 | P1 | retumbo de techo: ruido grave + D2 con trémolo de 10 Hz, un pulso | ruido + triángulo · mf |
| ✅ | `escombros` | FO14 | P1 | rocas: 4-5 golpes de ruido grave al azar en 300 ms | ruido · f |
| ✅ | `servo` | FO15 | P3 | barrido corto que sube y baja (D4 ↔ E4) | `PULSO_FINO` · pp |
| ✅ | `fijar` | FO16 | P1 | clic de traba + **Eb4** sostenida (la segunda menor de Re: la tensión máxima) con trémolo que se acelera, durante `FORTALEZA_FIJAR` | `PULSO_REDONDO` · f |
| ✅ | `caida` | FO17 | P1 | silbido que cae de Ab5 a D4 (del tritono a la tónica: llega el golpe) | `PULSO_FINO` · f |
| ✅ | `estrellarse` | FO18 | P1 | impacto gigante: ruido de 600 ms + `BAJO` de D2 a D0 | ruido + triángulo · ff |
| ✅ | `onda_suelo` | FO18 | P1 | ruido grave que rueda (el filtro oscila a 6 Hz), 800 ms | ruido · mf |
| ✅ | `hidraulica` | FO19 | P3 | ruido de 1.5 s + barrido de D3 a A3 | ruido + `PULSO_FINO` · pp |

**DEVORADORA DE ESTRELLAS** (Esmeralda)
| Estado | Sonido | Para | Prio | Partitura | Timbre y forma |
|---|---|---|---|---|---|
| ✅ | `siseo` | SE01 | P2 | ruido muy agudo (filtro 6000-9000 Hz) de 1 s que entra y sale | ruido · mf |
| ✅ | `cascabel` | SE03, SE10 | P1 | cascabel de serpiente: ráfagas de ruido de 15 ms en semicorcheas del pulso (8 por pulso), 2 pulsos | ruido · f |
| ✅ | `mordida` | SE04 | P1 | siseo de 200 ms + golpe seco (ruido de 30 ms) + D4 → Ab3 (tritono hacia abajo) | ruido + `PULSO_FINO` · f |
| ✅ | `serpiente_choca` | SE05 | P1 | golpe sordo: ruido grave de 200 ms + `BAJO` en A1 | ruido + triángulo · f |
| ✅ | `mareo` | SE06 | P2 | D5 E5 D5 C5 con vibrato enorme y que se desafina (borracha), 500 ms | `PULSO_FINO` · mf |
| ✅ | `enroscar` | SE07 | P1 | 6 pulsos: siseo que sube de D4 a Ab4 mientras el círculo se cierra; aprieta al final | ruido + `PULSO_FINO` · f |
| ✅ | `escupir` | SE08 | P2 | "ptú": ruido húmedo de 40 ms + barrido corto de G4 a C5 | ruido + `PULSO_FINO` · mf |
| ✅ | `corte` | SE09 | P1 | slice (ruido que cae) + grito agudo: barrido de D6 a A5 con vibrato | ruido + `PULSO_FINO` · f |

**MADRE DEL ENJAMBRE** (Ámbar)
| Estado | Sonido | Para | Prio | Partitura | Timbre y forma |
|---|---|---|---|---|---|
| ✅ | `panal` (loop) | CO01 | P3 | zumbido grave A2 con trémolo de 25 Hz | `PULSO_FINO` · pp |
| ✅ | `compuerta_abre` | CO02 | P1 | chirrido (barrido de D4 a A4 con vibrato desparejo) + zumbido A3 que crece durante 2 pulsos | `PULSO_FINO` · mf |
| ✅ | `llamado` | CO06 | P2 | glissando que llama: A4 → D5 → A4 → D5 (como un "¡vengan!") | `PULSO_REDONDO` · f |
| ✅ | `furia` | CO07 | P2 | 3 pulsos: zumbido grave que sube de D3 a Ab3 y se ensancha | `PULSO_REDONDO` · f |
| ✅ | `temblar` | CO08 | P1 | 3 pulsos: traqueteo de ruido cada vez más denso + traba (clic + Eb4) en el pulso 2, cuando la dirección queda fija | ruido + `PULSO_REDONDO` · f |
| ✅ | `embestida_colmena` | CO09 | P1 | whoosh grave (el filtro baja) + zumbido D3 | ruido + `PULSO_FINO` · f |
| ✅ | `colmena_choca` | CO10 | P1 | golpe sordo: ruido de 200 ms + `BAJO` en D2 + "splat" de miel (filtro bajo) | ruido + triángulo · f |

**EL FIN DE LA LUZ** (Abismo)
| Estado | Sonido | Para | Prio | Partitura | Timbre y forma |
|---|---|---|---|---|---|
| ✅ | `nacer` | SI01 | P1 | implosión al revés: el ruido sube de 100 a 4000 Hz y el `BAJO` de D1 a D4, lo que dura la entrada | ruido + triángulo · f |
| ✅ | `anillo_tic` | SI02 | P2 | piedra: ruido de 30 ms + D2 (en los pulsos impares A1) | ruido + `BAJO` · p |
| ✅ | `brazos` | SI03 | P2 | zap suave: barrido de D5 a A4 en 80 ms | `PULSO_FINO` · p |
| ✅ | `inhalar` | SI04 | P1 | 3 pulsos: succión (el ruido sube y crece) + `BAJO` de D2 a Ab2 (tritono) | ruido + triángulo · f |
| ✅ | `exhalar` | SI05 | P1 | estallido: ruido de 400 ms + viento + acorde D3 A3 de 200 ms | ruido + `PULSO_REDONDO` · f |
| ✅ | `colapso` | SI06 | P2 | implosión: barrido de D5 a D2 en 2 pulsos, el ruido se cierra | ruido + `PULSO_REDONDO` · mf |
| ✅ | `inestable` (loop) | SI07 | P2 | zumbido D4 + Eb4 (segunda menor) con trémolo, mientras está expuesta | `PULSO_FINO` · p |
| ✅ | `estallido` | SI08 | P2 | ruido de 300 ms + barrido del `BAJO` que sube de D2 a D3 (empuja hacia afuera) | ruido + triángulo · f |
| ✅ | `moneda_tragada` | SI09 | P3 | la moneda deslizándose de C6 a C4 en 400 ms (un detalle con humor) | `PULSO_MEDIO` · p |

## 9. Escenas: sonidos propios
| Estado | Sonido | Para | Prio | Partitura | Timbre y forma |
|---|---|---|---|---|---|
| ✅ | `logo` | IN02 | P2 | el logo se abre: C4 → G4 → C5 → acorde Cadd9 (C5 D5 E5 G5) que crece en 800 ms, + brillo C7 junto con el brillo de las letras | `PULSO_MEDIO` + `CAMPANA` · f |
| ✅ | `dificultad` (4) | DI01 | P2 | golpe cuando el nombre llega. FACIL: C5 + E5 · NORMAL: A4 + C5 · DIFICIL: D4 + F4 · PESADILLA: ver abajo | `PULSO_REDONDO` + bombo · mf |
| ✅ | `pesadilla` | DI03 | P2 | rugido: ruido grave de 600 ms + C2 + F#2 (tritono grave) + trueno | ruido + triángulo · f |
| ✅ | `carta_cae` | TA02, GA02, GA08 | P2 | roce de papel (ruido de 50 ms, 900 → 2200 Hz) + la nota de la carta: 1ª C5, 2ª D5, 3ª E5, 4ª G5... Sigue al acorde, igual que `taller` | ruido + `EPIANO` + `CRISTAL` arriba · p |
| ✅ | `carta_rara` | TA03 | P3 | brillo: G5 + C6 de 250 ms con eco (una cuarta en todos los colores) | `CRISTAL` · p |
| ✅ | `taller` | TA01 | P2 | un telón que se abre (aire que sube) y la quinta C4 + G4 que flota; a los 350 ms G5. Sin melodía: la ponen las cartas (C5 D5 E5) y la cierra el Sol. ARMÓNICO, como las cartas | ruido + `PAD_SUAVE` + `CRISTAL` · mf |
| ✅ | `tienda` | GA01 | P2 | "ding-dong" de tienda **en Fa** (el tema de la gasolinera): A5 → F5, 200 ms cada una con eco | `CAMPANA` · mf |
| ✅ | `caja` | GA04 | P1 | "ka-ching": trinquete (5 clics de ruido en 60 ms) + campana F6 + A6 + C7 (Fa mayor) de 300 ms | ruido + `CAMPANA` · f |
| ✅ | `vendedor_no` | GA05 | P2 | el robot niega: E5 → C5 → E5 → C5 (30 ms cada una), desafinado | `PULSO_FINO` · p |
| ✅ | `sello` | GA07 | P2 | golpe de goma: ruido sordo de 60 ms + F3 | ruido + `BAJO` · mf |
| ✅ | `barajar` | GA08 | P2 | 6 "flips" de ruido en 200 ms | ruido · mf |
| ✅ | `surtidor` (loop) | GA11 | P3 | bomba: F3 → C4 en corcheas con trémolo (glu-glu), termina en clunk (ruido + F2) | `BAJO` + ruido · pp |
| ✅ | `neon` | GA12 | P3 | zumbido de 120 Hz con armónicos, 100 ms, cada vez que el cartel prende | `PULSO_REDONDO` filtrado · pp |
| ✅ | `hangar_nave` | LO01 | P2 | el motor arranca: barrido de C3 a C5 en 300 ms + quinta C5 + G5 | `PULSO_REDONDO` · mf |
| ✅ | `mando_dentro` / `mando_fuera` | S02 | P3 | dentro: C6 → G6 · fuera: G6 → C6 | `PULSO_FINO` · p |

## 10. Ambiente (`AMBIENTE`, loops de 20-30 s que dan la vuelta sin cortes)
Todos usan drones en **Do o Sol**, para sonar bien debajo de la música del juego (Do mayor).

| Estado | Sonido | Para | Prio | Partitura | Timbre y forma |
|---|---|---|---|---|---|
| ✅ | `amb_cinturon` | F03 | P3 | viento espacial (el filtro del ruido se mueve muy lento) + drone C2 + G2 | ruido + triángulo · pp |
| ✅ | `amb_carmesi` | F03 | P3 | crepitar de brasas (clics de ruido al azar) + drone A1 | ruido · pp |
| ✅ | `amb_esmeralda` | F03 | P3 | grillos chiptune: E7 de 10 ms en pares, al azar + drone C3 | `PULSO_FINO` · pp |
| ✅ | `amb_ambar` | F03 | P3 | zumbido lejano del panal: G2 con trémolo de 20 Hz, entra y sale | `PULSO_FINO` · pp |
| ✅ | `amb_abismo` | F03 | P3 | drone C1 + G1 que "respira" (el volumen sube y baja cada 4 s) | triángulo · pp |
| ✅ | `trueno` (2 variantes) | F08 | P2 | ruido muy grave de 1.5 s con dos picos (el retumbo) | ruido · p |

## 11. Música
| Estado | Tema | Para | Prio | Plan |
|---|---|---|---|---|
| ✅ | `musica_juego` | MU03 | P1 | **"Neón en ruta"**: synthwave en **La menor, 118 bpm, 24 compases (~49 s)**. A (1-8) `Am F C G Am F C G` respiro: bajo 3-3-2, arpegio pluck con delay de corchea con puntillo, pad que bombea. B (9-16) `F G Em Am F G Esus4 E` entra la melodía (`LEAD_CALIDO`). C (17-24) `Dm Am F C Dm Am F G` clímax: bajo en octavas, palmas, hats en semicorcheas y una campana de contracanto. Redobles de toms y platillo al revés entre secciones; el Sol final vuelve a La: loop sin costura. Reemplazó a `musica.mp3` |
| ✅ | `musica_menu` | MU01 | — | **"Hangar"** (rehecho en el estudio el 2026-10-14; era chiptune): La menor, 112 bpm, 16 compases, `Am F C G` ×2 y `F G Em Am F G E E`. La melodía de siempre en `LEAD_HUECO`, arpegio pluck, pad suave, bajo analógico y batería liviana |
| ✅ | `musica_jefe` | MU06 | — | **"Mirada fija"** (el Ojo; rehecho en el estudio): Re menor, 150 bpm, 24 compases. A presenta la melodía (`LEAD_CALIDO`), B la sube con hats en semicorcheas, C el riff de semicorcheas (pluck) y el bombo empuja. Bajo rugido en octavas y pad oscuro |
| ✅ | `musica_gasolinera` | MU09 | — | **"Parada técnica"** (rehecho en el estudio): Fa mayor, 96 bpm con swing, `Fmaj7 Dm7 Gm7 C7...`. Vibráfono (`CAMPANA`, ahora armónica) con la melodía de siempre, piano eléctrico a contratiempo, bajo caminante (R 3 5 6) y batería con escobillas |
| ✅ | `musica_iniciales` | MU14 | P2 | **"Tu nombre en neón"**: Do mayor, 120 bpm, 8 compases (16 s), `C Am F G C Am Dm G`. Melodía de piano eléctrico (`EPIANO`), arpegio pluck con delay, bajo en octavas, pad suave y batería liviana |
| ✅ | `musica_fin` | MU15 | P2 | **"Señal perdida"**: La menor, 80 bpm, 8 compases (24 s), `Am F C G Am F E E`, sin batería. Campana con eco largo, pad suave con chorus, piano eléctrico a contratiempo y un sub. A -16 LUFS: melancolía tranquila |
| ✅ | `musica_tension` | MU04 | P3 | **La menor sobre un pedal de Mi** (el V: algo se acerca y no resuelve), 126 bpm, 8 compases (~15 s): `Am/E F/E Dm/E E | Am/E F/E Dm/E E7`. Bajo `BAJO_RUGIDO` martillando el Mi, pad oscuro, arpegio nervioso, un lead hueco que sube por semitonos y toms que crecen. Suena el nivel antes del jefe |
| ✅ | Temas por jefe (`musica_jefe_fortaleza`, `_serpiente`, `_colmena`, `_singularidad`) | MU06 | P3 | Rehechos en el estudio el 2026-10-14 (`obras/musica_jefes.py`; eran chiptune), con las mismas melodías y acordes, todos en Re menor. **Fortaleza** "Marcha imperial": 132 bpm, redoblante de desfile con redobles, bajo oom-pah (R y 5), golpes de acordes y la melodía de metales (`LEAD_CALIDO` saturado, doblado por `METAL` una octava abajo). **Serpiente** "Danza de escamas": 120 bpm con swing 0.3, flauta hueca (`LEAD_HUECO`) con adornos frigios (Mib de paso) y campanas que ondulan. **Colmena** "Enjambre de cristal": 160 bpm, las alas son un `ZUMBIDO` en semicorcheas, bajo rugido en octavas. **Singularidad** "Horizonte de sucesos": 100 bpm a medio tiempo, notas largas, campanas con eco y una sala de 4 s |
| ✅ | Variantes de `musica_juego` por sector (`musica_juego_2` ... `_5`) | MU03 | P3 | la misma canción con otro color (`COLORES` en `obras/musica.py`): **Carmesí** 122 bpm, pad oscuro y bajo rugido; **Esmeralda** 112 bpm, piano eléctrico en corcheas, flauta hueca y campanas, sala grande; **Ámbar** 110 bpm con swing, marimba y piano eléctrico; **Abismo** a medio tiempo, sala de 4 s y campanas lejanas |

---

## Registro
| Fecha | Qué se hizo |
|---|---|
| 2026-10-14 | **Sonidos limpios** (pedido: "otros muy saturados que rompen la experiencia"; sección 0.12). Seis patrones: la cinta del master sin nivelar (la causa de fondo, en ~70 efectos y la música), acordes cerrados, el Taller fijo en Fa contra las cartas armónicas, sierras en acordes, intervalos que cambian con el color (el sus ahora se cuenta desde Re) y escalas rápidas en cristal. Rehechos: moneda (suma una capa por multiplicador), dificultad y `taller` (ahora armónicos), cartas, GO, cápsula, `vulnerable`, perfectos, `combo_sube`/`combo_max`, `bonus`, `pw_hielo`, `pw_nova`, `pw_vida`, `oro_llega`, `mejora_elegida`, `desafio_cumplido`, `ui_valor`, `aturdido`. Todo recompuesto (efectos, ambientes y temas). 3 tests nuevos (el master no depende del nivel, notas que raspan en los 11 colores, capas de la moneda), que detectan 4 errores inyectados. **El usuario lo escuchó: "ahora sí se escucha bien".** |
| 2026-10-14 | **Mezcla y armonía** (pedido: "no se sienten armónicos; mucho solapamiento y saturación"; sección 0.11). Mezcla con margen y un limitador con las fichas (`efectos/fichas.json`); efectos más secos; `CAMPANA` y `METAL` armónicos; los peligros con la tensión de la escala; **los efectos armónicos siguen al acorde** (11 colores, `armonia.py`); y los 7 temas chiptune **rehechos en el estudio** (el usuario eligió rehacerlos). El compositor viejo guarda en `herramientas/chiptune/`. |
| 2026-10-13 | **Un tema para cada jefe** (pedido del usuario), en el estilo chiptune de `musica_jefe` con el compositor viejo: `musica_jefe_fortaleza`, `_serpiente`, `_colmena`, `_singularidad` (Re menor, ±1 dB del original). El compositor viejo ahora guarda OGG con soundfile si no hay ffmpeg. **La lista está completa.** |
| 2026-10-13 | **Las P3.** El ambiente de cada sector (5 loops de 24 s, `obras/ambiente.py`, con su tocadiscos y fundido), `musica_tension` (el nivel antes del jefe), las variantes de "Neón en ruta" por sector (`musica_juego_2..5`), `logo`, `ui_transicion`, `mando_dentro/fuera`, el contador del Game Over (`contador_1..8` + `contador_fin`, y `teclear` por fila), `fuego_artificial`, `surtidor` y `neon` en la gasolinera, `dash_vacio`, `latido` (con la opción LATIDO en SONIDO) y los detalles de los jefes (`ojo_flota`, `motor_pesado`, `servo`, `hidraulica`, `panal`, `inestable`). Queda decidir si se hacen temas por jefe. |
| 2026-10-13 | **Todo el sonido nuevo, compuesto y conectado.** El usuario borró los 6 efectos viejos y `musica.mp3`, y devolvió `musica_menu`, `musica_jefe` y `musica_gasolinera` (se quedan). Compuestos en el estudio: `musica_iniciales`, `musica_fin` y **226 efectos** (`herramientas/estudio/obras/efectos_*.py`, con las capas de `capas.py`: tono, cuerpo, aire y explosión). Brillo medio de los efectos: 2031 Hz (los viejos: 4100-6900). Todos en el `CATALOGO` de `sonido.py` (214 nombres, con variantes y escalas) y conectados a cada evento del mapa. Nuevo en el mezclador: `reproducir_luego` y `SILENCIO`. Quedan las P3 (ambiente de cada sector, surtidor, neón, logo, contador del Game Over, `ojo_flota`, `motor_pesado`, `servo`, `hidraulica`, `panal`, `inestable`, `ui_transicion`, `dash_vacio`, `latido`, mandos) y los temas extra (tensión, por jefe, por sector). |
| 2026-10-13 | **Nueva estética y el estudio** (pedido: "algo diferente, profesional, que no sea chillón, con cuerpo"): synthwave en vez de chiptune. Se armó `herramientas/estudio/` (síntesis sin aliasing, FM, batería, reverb, delay, chorus, EQ, compresor, bombeo, limitador, LUFS) y `herramientas/componer.py`. Compuestos: **`musica_juego`** (ya suena en el juego, en lugar de `musica.mp3`) y un primer paquete de efectos para escuchar (🟨): `ui_mover_1/2`, `ui_aceptar`, `ui_volver`, `moneda_1`…`5`, `nave_dash_1`…`3`, `nave_golpe`, `perfecto_1`…`5`. Toda la música se rehace. |
| 2026-10-13 | Decisión del usuario: **los 6 efectos viejos se rehacen todos desde cero.** Sección 0.10: a qué sonido nuevo pasa cada uso; `game_over` pasa a ⬜ (se recompone). |
| 2026-10-13 | **Fase A hecha:** el mezclador (`sonido.py`: catálogo con categoría, prioridad, voces, enfriamiento y variantes; paneo, ducking, loops y ambiente; 24 canales), VOLUMEN / MUSICA / EFECTOS por separado, silencio con M y AUDIO MONO; en el compositor `secuencia`, `barrido`, `ruido`, curvas, trémolo, vibrato, dinámicas, `medir` y `--escuchar`. 26 tests nuevos. Ningún sonido nuevo todavía. |
| 2026-10-13 | Se armó la lista a partir de `MAPA_DE_AUDIO.md`, con la base musical medida (Do mayor / La menor / Re menor / Fa mayor → paleta común: pentatónica de Do) y la partitura de cada sonido. Todos pendientes. |

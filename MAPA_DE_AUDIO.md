# Mapa de audio — Caza Monedas

Este documento es el plan de sonido del juego. Lista **todo lo que pasa en el juego** (cada escena, acción, enemigo, fase de jefe, cartel y menú), con lo que suena hoy y lo que se propone que suene. La idea es llegar a un sonido de nivel "triple A" **sin saturar**: cada sonido tiene un significado, una prioridad y un límite.

Se armó recorriendo todo el código (octubre 2026). **Estado:** las fases A, B y C están hechas: el mezclador está terminado y todo P1 y P2 está compuesto en el estudio y conectado. Quedan las P3. La columna **Hoy** de las tablas es el diagnóstico original; lo que ya suena está marcado ✅ en `LISTA_DE_SONIDOS.md`. **La partitura de cada sonido y el avance están en `LISTA_DE_SONIDOS.md`.** La columna **Hoy** es lo que suena en el juego actual. Lo demás todavía **no está hecho**.

**Cómo leerlo**
- Cada fila tiene un **código** (por ejemplo `N01`, `FO07`) para nombrarla al implementarla.
- **Dónde**: el archivo y la función donde pasa la cosa. Ahí va el `sonidos.reproducir(...)`, siempre en la lógica y nunca en `dibujar`.
- **Hoy**: el efecto que suena ahora (`golpe`, `seleccion`...), o "—" si no suena nada.
- **Propuesta**: el nombre del sonido nuevo (ver el catálogo en la sección 3) y cómo tiene que sonar.
- **Prioridad**:
  - **P1** es imprescindible: es lo que más se nota y lo que más cambia la sensación de calidad.
  - **P2** es calidad: le da identidad a cada cosa.
  - **P3** es pulido fino.
  - **NO** es un silencio a propósito (ver la sección 6).

---

## 1. Diagnóstico: cómo suena hoy

### Lo que hay
| Archivo | Nombre en `EFECTOS` | Dura | Usos en el código | Qué significa hoy |
|---|---|---|---|---|
| `seleccion.wav` | `seleccion` | 0.05 s | **24** | mover el cursor, aceptar, volver, cambiar de pestaña, cambiar un ajuste, subir de nivel, **dash perfecto**, desafío nuevo, rango B/C, empezar partida |
| `golpe.wav` | `golpe` | 0.18 s | **18** | **te pegaron**, **le pegaste al jefe**, destruiste un enemigo, interceptaste, NOVA, láser, cortina, mina, llamarada solar, choques de jefes, **no te alcanzan los créditos** |
| `nuevo_record.wav` | `nuevo_record` | 0.49 s | 8 | récord superado, **logro**, **¡OLEADA!**, **anomalía**, FÉNIX, rango S/A, abrir el Taller, llegar a la gasolinera |
| `moneda_brillante.wav` | `powerup` | 0.22 s | 7 | power-up, mejora, ESCUDO ROCE, oleada superada, desafío cumplido, compra, explosión del jefe |
| `moneda.wav` | `moneda` | 0.23 s | 3 | moneda, enemigo congelado roto, compra |
| `game_over.wav` | `game_over` | 0.8 s | 1 | al terminar la escena de la explosión |

Música: `musica_menu`, `musica` (juego, MP3), `musica_jefe` y `musica_gasolinera` (ver "Sonido y música" en CLAUDE.md).

**Los 6 efectos se rehacen todos desde cero** (decisión del usuario): ninguno queda. Qué sonido nuevo reemplaza cada uso está en `LISTA_DE_SONIDOS.md`, sección 0.10.

### Problemas encontrados
1. **Un sonido significa cosas opuestas.** `golpe` suena igual cuando te pegan y cuando le pegás al jefe. `nuevo_record` suena igual en un logro (algo bueno) y en "¡OLEADA!" (peligro). `seleccion` suena igual al mover el cursor y en un dash perfecto. El oído no puede aprender qué pasó.
2. **La acción más usada no suena: el dash.** Se usa cada 1.5 s y es el centro del juego (perfectos, intercepciones, golpes al jefe).
3. **Ningún aviso de peligro suena.** El embestidor apuntando, la carga del Ojo, el `fijar` de la Fortaleza, el `temblar` de la Colmena, el `inhalar` de la Singularidad, la mina por estallar, el aviso de la tormenta y las columnas de los asteroides solo se ven (y algunos vibran). Las peleas son "un baile con ritmo" y al baile le falta la mitad del ritmo: el que se oye.
4. **Momentos grandes mudos.** La cinemática de ¡ALERTA! del jefe, READY?/GO!, pausar, el golpe final al jefe, el cartel del rango (salvo el sello), el sector nuevo, el desafío fallado, el combo cortado, el power-up que se acaba y el fin de una anomalía.
5. **Pantallas sin música.** Iniciales y Game Over están en silencio total.
6. **Menús que no suenan igual.** Moverse suena en Inicio, pero **no en Pausa, Opciones ni Desarrollador**. Cambiar de letra en Iniciales no suena.
7. **Técnicos:**
   - Solo hay 6 canales para efectos (pygame trae 8 y la música reserva 2).
   - No hay límite de voces por sonido ni paneo estéreo (todo suena al centro).
   - La música no baja en los momentos importantes (no hay ducking).
   - Un solo volumen para todo, con dos interruptores.

---

## 2. Reglas para sonar "triple A" sin saturar

Estas reglas valen para cada sonido nuevo. Las que dicen cómo hacerlo en pygame son la base técnica de la fase A (sección 7).

1. **Un sonido, un significado.** Lo bueno sube (notas que suben, acordes mayores, brillo). Lo malo baja (notas que caen, ruido, graves). El peligro avisa (dos tonos que alternan, algo que crece). Nunca se reusa un sonido para dos cosas que significan distinto.
2. **Cuatro niveles de prioridad.** Si suenan muchas cosas juntas, se cortan primero las de abajo:
   - 4: **momentos** (jefe vencido, muerte, rango, récord, logro);
   - 3: **peligro** (avisos de ataque, golpes que te dan);
   - 2: **acciones y premios** (dash, moneda, perfecto, power-up);
   - 1: **detalle y ambiente** (rebotes, tics, motas).
3. **Límite de voces y enfriamiento por sonido.**
   - Cada sonido tiene `voces` (cuántos a la vez como máximo; `Sound.get_num_channels()` dice cuántos suenan) y `enfriamiento` (ms mínimos entre dos).
   - Ejemplos: `aparece` 120 ms, `rebote` 200 ms, `ui_mover` 40 ms, `agonia` 150 ms.
   - **Nunca un sonido por bala:** uno por ráfaga o por pulso.
4. **Variantes y escalas.**
   - Lo que suena mucho (dash, enemigo roto, onda) tiene 2 o 3 variantes que se turnan sin repetir la anterior.
   - Lo que se encadena **sube de tono**: la moneda con el multiplicador (x1 a x5), el perfecto con la cadena (x1 a x5), la barra del jefe al llenarse, las estrellas del rango y las calaveras de la dificultad.
   - pygame no cambia el tono al reproducir: las escalas se componen de antemano (`moneda_1` ... `moneda_5`).
5. **Paneo estéreo según la x.**
   - Después de `play()`, `canal.set_volume(izquierda, derecha)` según dónde pasó la cosa (0 a `ANCHO`), suave: nunca menos de 0.35 de un lado.
   - Así se oye de qué lado cayó la cápsula, rebotó el rebotador o viene el meteoro.
   - La interfaz y los momentos van al centro.
   - Opción de accesibilidad **AUDIO MONO** (para quien oye de un solo oído): apaga el paneo.
6. **Ducking.** En los momentos (prioridad 4) la música baja a ~40 % y vuelve en ~600 ms, con `canal.set_volume` del tocadiscos. Así la fanfarria se oye clara sin subir el volumen general.
7. **El silencio también es un sonido.**
   - La muerte ya corta la música en seco (muy bien).
   - Lo mismo para la ¡ALERTA! del jefe, el golpe final y el instante antes de la explosión del jefe.
   - Ver la sección 6 para lo que **no** tiene que sonar.
8. **Todo aviso visual de peligro tiene su sonido, con el mismo tiempo.**
   - Si el aviso dura 600 ms, el sonido dura 600 ms y termina justo cuando llega el ataque.
   - Esto además es **accesibilidad**: se puede jugar mirando menos.
9. **En los jefes, los sonidos caen en el pulso.** Los avisos y disparos usan `jefe.nuevo_pulso`, así se oye el ritmo del baile (`JEFE_PULSO`, `FORTALEZA_PULSOS`, `SERPIENTE_PULSOS`).
10. **Mismo estilo que la música: synthwave con cuerpo** (antes decía chiptune: el usuario pidió algo distinto, profesional y que no sea chillón; ver la estética en `LISTA_DE_SONIDOS.md`).
    - Sintes analógicos virtuales, FM y batería sintetizada, todo hecho con el estudio (`herramientas/componer.py`): nada de samples.
    - Cada efecto en capas: el tono (afinado en la paleta), el cuerpo (un grave corto) y el aire (ruido filtrado).
    - Nada de grabaciones realistas: rompen la esencia retro igual que un sprite con antialiasing.
11. **Mezcla por categorías.**
    - Cada sonido pertenece a una: `MUSICA`, `EFECTOS`, `INTERFAZ` o `AMBIENTE`. Su volumen relativo va en `config.py` (`MEZCLA`).
    - En Opciones (SONIDO): **VOLUMEN MUSICA** y **VOLUMEN EFECTOS** por separado (hoy hay un solo volumen).
12. **Más canales, algunos reservados.**
    - `pygame.mixer.set_num_channels(24)`.
    - 2 canales para la música (ya están), 1 para el ambiente y 2 para los loops (el láser de la Fortaleza y la sirena de la ¡ALERTA!). El resto para efectos.
13. **La pausa.** `mixer.pause()` congela lo que suena; un sonido que se pide **después** igual suena (verificarlo con un test). Así PAUSA puede tener su sonido.
14. **Margen y limitador** (2026-10-14: "mucho solapamiento y saturación").
    - pygame suma los canales y **recorta** lo que pasa del máximo: eso es la saturación. Medido con un bot y una mezcla fuera de línea: con todo al máximo, 53 de 362 segundos sonaban recortados.
    - **Margen (headroom):** `MEZCLA` deja la música en −20 LUFS dentro del juego (0.5) y los efectos un poco arriba (0.7). La suma casi nunca llega al techo.
    - **Limitador:** el mezclador sabe cuánto suena cada efecto en cada momento (`efectos/fichas.json`) y, si la suma pasaría de −1 dB, baja primero los detalles y las acciones y, si no alcanza, todo. Medido: 0 recortes en 15 minutos de partida.
    - **Efectos secos y cortos:** lo que pasa seguido no puede tener una cola larga (una moneda duraba 1.1 s y tres seguidas eran un solo ruido). Cola 0.3 × la sala y poca reverb.
15. **Afinados con la música, acorde por acorde** (2026-10-14: "que todos los efectos sean armónicos").
    - Los premios, los power-ups y la interfaz **siguen al acorde**: se componen en 11 colores (la pentatónica de cada acorde) y el juego toca el del compás que suena (`LISTA_DE_SONIDOS.md`, sección 0.11). También los que se repiten todo el tiempo aunque no sean premios (rebotes, el compás de la Fortaleza, el tic de la mina).
    - Los peligros llevan la tensión **de la escala del tema** (tritono y segunda menor de la escala), no notas de afuera: repetidas cada pocos segundos, sonaban desafinadas.
    - **Instrumentos armónicos:** en FM, solo relaciones enteras (o casi: 1.002 para que el metal "bata"). Una campana inarmónica suma notas que no están en la partitura.

---

## 3. Catálogo de sonidos propuesto

Los nombres van en `EFECTOS` (`sonido.py`) y en `COMPOSICIONES` (compositor). Todos son `vuelta=False` (efecto), salvo los loops. Duraciones aproximadas.

### Interfaz (`INTERFAZ`)
| Nombre | Cómo suena | Usado en |
|---|---|---|
| `ui_mover` (2 variantes que alternan) | tic de pulso fino, ~30 ms | I01 |
| `ui_aceptar` | dos notas que suben, ~120 ms | I02 |
| `ui_volver` | las mismas dos notas, bajando | I03 |
| `ui_error` | zumbido grave doble, ~150 ms | I04, GA05 |
| `ui_pestana` | "fsst" de ruido + una nota, ~80 ms | I05 |
| `ui_valor` | tic con dos alturas (subir/bajar) | OP03 |
| `ui_llave_si` / `ui_llave_no` | clic + nota aguda / grave | OP04 |
| `ui_alerta` | dos notas tensas (tritono) | I08 |
| `ui_transicion` | barrido de ruido que sube y baja, 420 ms | I06 |
| `ui_empezar` | acorde grande tipo "insert coin", ~400 ms | DI04, FI06 |
| `ui_apagar` | nota que cae + clic de pantalla CRT apagándose | IN05 |
| `ui_tecla` | tic con la altura según la letra | IR01 |
| `pausa` / `seguir` | dos notas que caen / que suben | PA01, PA02 |

### Nave (`EFECTOS`)
| Nombre | Cómo suena | Usado en |
|---|---|---|
| `nave_dash` (3 variantes) | barrido de ruido que sube y baja en 180 ms (`DASH_DURACION`) | N01 |
| `nave_dash_extra` | el mismo, más agudo | N02 |
| `dash_listo` | "tin" corto y muy suave | N03 |
| `dash_vacio` | clic seco apagado | N04 |
| `escudo_roto` | vidrio de energía que se quiebra + nota que cae | N06 |
| `nave_golpe` | impacto grave con distorsión corta | N07 |
| `ultima_vida` | alarma de dos tonos, dos veces | N08 |
| `fenix` | llamarada que sube + acorde mayor | N09 |
| `nave_muerte` (+ versión estirada para la cámara lenta) | explosión grande de ruido con cola grave, ~1.2 s | EX01 |
| `hiperespacio` | barrido que sube y baja en 1.5 s, como `velocidad_salto()` | F01 |

### Monedas y puntos
| Nombre | Cómo suena | Usado en |
|---|---|---|
| `moneda_1` ... `moneda_5` | la moneda, un escalón más arriba por multiplicador (escala pentatónica) | P01, P02 |
| `moneda_oro` | moneda + campanita | P03 |
| `combo_sube` | arpegio rápido de 3 notas que termina en el tono nuevo | P05 |
| `combo_max` | arpegio + acorde brillante | P06 |
| `combo_cortado` | dos notas que caen | P07 |
| `perfecto_1` ... `perfecto_5` | "slash" brillante + una nota que sube con la cadena | P08 |
| `interceptado` | "clang" metálico | P09 |
| `record` | jingle arcade, ~1 s | P10 |
| `nivel` | arpegio que sube, ~500 ms | P11 |
| `bala_rota` | pop metálico | P14 |
| `contador` | tics rápidos que suben, terminan en `ding` | FI01, GA06 |

### Power-ups y mejoras
| Nombre | Cómo suena | Usado en |
|---|---|---|
| `capsula` | campanita corta que baja (con paneo) | W01 |
| `pw_escudo` | zumbido de energía que sube y se cierra | W04, M05, GA10 |
| `pw_hielo` | cristal que se congela | W05 |
| `pw_vida` | jingle "1UP" de 4 notas | W06, GA09 |
| `pw_iman` | wobble (vibrato fuerte) | W07 |
| `pw_doble` | dos "ding", el segundo una octava arriba | W08 |
| `pw_turbo` | motor que acelera | W09 |
| `pw_recarga` | carga eléctrica rápida | W10 |
| `pw_nova` | zumbido grave que queda "cargado" | W11 |
| `nova` | explosión con onda | W12 |
| `pw_acaba` | tic suave (sale 3 veces) | W13 |
| `pw_fin` | power-down corto | W14 |
| `hielo_roto` | cristal que se quiebra + nota | W15 |
| `mejora_elegida` | acorde que se abre + brillo | M01, TA04, GA04 |
| `onda` (2 variantes) | "fuuum" grave y corto | M02 |
| `eco` | `nave_dash` más bajo y con eco | M03 |
| `roce_carga` | tic de energía; el tono sube con la carga | M04 |

### Enemigos y proyectiles
| Nombre | Cómo suena | Usado en |
|---|---|---|
| `aparece` | blip de teletransporte | E01 |
| `escuadron_llega` | soplido que crece + dos pings de radar Si-Fa (con paneo) | E01b, D20 |
| `enemigo_roto` (3 variantes) | crunch + chispa | E03 |
| `aturdido` | "pío-pío" | E05 |
| `rebote` | "boing" elástico | E08 |
| `embestidor_apunta` | zumbido que sube, 600 ms | E09 |
| `mira_fija` | clic metálico de traba | E10 |
| `embestida` | whoosh | E11 |
| `divisor_parte` (grande, mediano, chico) | "splat" gelatinoso, cada uno más agudo | E12 |
| `enjambre_aviso` | zumbido que sube, 450 ms | E13 |
| `enjambre_picada` | barrido que baja | E14 |
| `bonus` | arpegio | E15 |
| `abeja_sale` | bzz corto | E16, CO03 |
| `abeja_aviso` | bzz agudo que sube, 400 ms | E17 |
| `retirada` | "poof" grupal (uno solo) | E19, D03, J03 |
| `mina_tic` | bip (se pide cada vez más seguido) | B01 |
| `mina_estalla` | estallido seco | B02 |
| `ladron_roba` | manotazo + risita, 500 ms | E20 |
| `moneda_recuperada` | arpegio de cristal que sube | E21 |
| `ladron_escapa` | silbido que se aleja | E22 |
| `escudo_bloquea` | "tonk" de metal | E23 |

### Director, carteles y jingles
| Nombre | Cómo suena | Usado en |
|---|---|---|
| `oleada` | alarma de dos tonos ×3 + bombo (hoy: empieza el ASEDIO) | D01 |
| `oleada_superada` | fanfarria corta (hoy: ¡ASEDIO SUPERADO!) | D02 |
| `asteroides_llega`, `tormenta_llega`, `niebla_llega`, `oro_llega` | stinger de cada anomalía: retumbo / chisporroteo / viento hueco / campanitas | D05, D09, D12, D14 |
| `meteoro_aviso` | silbido que baja, 900 ms (con paneo) | D06 |
| `tormenta_aviso` | crepitar que crece, 1.2 s | D10 |
| `llamarada` | rugido de ruido ancho | D11 |
| `anomalia_fin` | barrido que se disipa | D15 |
| `desafio_nuevo` | dos notas de "objetivo" | D16 |
| `desafio_cumplido` | fanfarria corta | D18 |
| `desafio_fallado` | dos notas que caen + ruido | D19 |
| `ficha_enemigo` | deslizamiento + nota de alerta | C03 |
| `logro` | jingle de trofeo (distinto de `record`) | C05 |
| `nave_nueva` | segundo jingle corto, en el color de la nave | C05 |
| `teclear` | tic muy bajo | C02, C10 |
| `estrella` | "ding" que sube con cada estrella | C08 |
| `sello_S`, `sello_A`, `sello_B`, `sello_C` | golpe + acorde: S fanfarria con arpegios, A brillante, B neutro, C seco | C09 |
| `sector_nuevo` | stinger de llegada | C10 |
| `barra_jefe` | tic que sube, uno por segmento | C11 |
| `listo_ready` / `listo_go` | dos notas que preguntan / acorde brillante + bombo | LI02, LI03 |
| `game_over` (ya existe) | jingle de fin | EX03 |
| `destruida` | acorde menor grave sostenido | EX02 |
| `record_guardado` | jingle corto | IR04 |

### Jefes
Comunes:

| Nombre | Cómo suena |
|---|---|
| `alerta` (loop) | sirena de dos tonos |
| `franjas` | clunk metálico |
| `presentacion` | dos golpes: uno para el nombre, otro para el apodo |
| `vulnerable` | brillo cristalino que sube: siempre igual, el jugador aprende que "ahora se puede" |
| `jefe_golpe` | impacto grande |
| `jefe_parte` | impacto medio |
| `parte_rota` | crash |
| `golpe_final` | impacto grande + corte |
| `agonia` | explosiones chicas |
| `jefe_explota` | explosión gigante |
| `jefe_vencido` | fanfarria |

Cada jefe tiene además sus sonidos propios (sección 4.10).

### Ambiente (`AMBIENTE`, loops en el canal reservado)
| Nombre | Sector | Cómo suena |
|---|---|---|
| `amb_cinturon` | Cinturón | viento espacial grave |
| `amb_carmesi` | Carmesí | crepitar de brasas |
| `amb_esmeralda` | Esmeralda | grillos lejanos, chiptune |
| `amb_ambar` | Ámbar | zumbido lejano de panal |
| `amb_abismo` | Abismo | drone grave que "respira" |

Más `trueno`, el trueno lejano del relámpago.

---

## 4. Mapa de eventos

### 4.1 Interfaz (todas las pantallas)
| Código | Situación | Dónde | Hoy | Propuesta | Prio | Anti-saturación |
|---|---|---|---|---|---|---|
| I01 | Mover el cursor | menús de todas las escenas | `seleccion` en Inicio, Logros, Taller, Gasolinera y Dificultad; **— en Pausa, Opciones y Desarrollador** | `ui_mover`, igual en todas | P1 | enfriamiento 40 ms |
| I02 | Aceptar / entrar | idem | `seleccion` | `ui_aceptar` | P1 | |
| I03 | Volver (ESC/B) | Dificultad, Logros, Opciones, Fin, Gasolinera | `seleccion` | `ui_volver` | P1 | |
| I04 | No se puede (vendida, no alcanza, poder no disponible, anomalía con jefe) | Gasolinera `_comprar`, Desarrollador | `golpe` en la Gasolinera, — en el resto | `ui_error` | P1 | |
| I05 | Cambiar pestaña o sección (LB/RB, Q/E) | Inicio `cambiar_pagina`, Opciones `_cambiar_pestana` | `seleccion` | `ui_pestana` | P2 | |
| I06 | Transición de rombos | `App.cambiar_escena` | — | `ui_transicion`, muy bajo | P3 | casi siempre coincide con I02/I03: probarlo y sacarlo si suma ruido |
| I07 | Atajo M (silencio) | `App._atajos` | — | `ui_llave_si` antes de silenciar / `ui_llave_no` después de volver a prender | P3 | |
| I08 | Aparece una ventana de confirmación | Pausa `_elegir` | `seleccion` | `ui_alerta` | P2 | |

### 4.2 Escenas
**Inicio**
| Código | Situación | Hoy | Propuesta | Prio |
|---|---|---|---|---|
| IN01 | Música | `musica_menu` | la misma | — |
| IN02 | Primera vez que se ve el Inicio (arranque) | — | stinger del logo (acorde que se abre) junto con el brillo del logo; queda pendiente la "presentación con logo" | P2 |
| IN03 | ARRIBA/ABAJO, ACEPTAR | `seleccion` | I01, I02 | P1 |
| IN04 | SALIR | `seleccion` | `ui_apagar`, cerrando ~300 ms después para que se oiga | P2 |
| IN05 | La página del panel cambia sola cada 7 s | — | silencio | NO |
| IN06 | Brillo del logo cada 4.5 s, nave volando | — | silencio | NO |

**Dificultad**
| Código | Situación | Hoy | Propuesta | Prio |
|---|---|---|---|---|
| DI01 | Cambiar de dificultad (el nombre entra deslizándose) | `seleccion` | `ui_pestana` + un golpe cuando el nombre llega, más grave cuanto más difícil | P2 |
| DI02 | Las calaveras aparecen de a una | — | `teclear`, subiendo de tono en cada calavera | P3 |
| DI03 | PESADILLA (tiembla y vibra) | `seleccion` | rugido grave + trueno de ruido (~600 ms) | P2 |
| DI04 | ENTER: empieza la partida | `seleccion` (`App.nueva_partida`) | `ui_empezar` | P1 |
| DI05 | ESC | `seleccion` | I03 | P1 |

**Listo (READY? / GO!)**
| Código | Situación | Hoy | Propuesta | Prio |
|---|---|---|---|---|
| LI01 | Salto al hiperespacio al empezar | — | F01 | P1 |
| LI02 | READY? (0 a 1 s) | — | `listo_ready` | P1 |
| LI03 | GO! (a 1 s) | — | `listo_go` | P1 |
| LI04 | La música del juego | arranca al comenzar READY | READY en silencio; la música entra en el GO (el GO es el primer tiempo) | P2 |

**Pausa**
| Código | Situación | Hoy | Propuesta | Prio |
|---|---|---|---|---|
| PA01 | Pausar (P/ESC/Menú, o automática por foco perdido o mando desconectado) | — (`mixer.pause`) | `pausa`, sonando después de `pausar_todo()` | P1 |
| PA02 | Seguir | — | `seguir`, antes de `reanudar_todo()` | P1 |
| PA03 | Mover, NO/SI en la confirmación | — | I01 | P1 |
| PA04 | OPCIONES, VOLVER AL MENU | `seleccion` | I02, I08 | P1 |
| PA05 | SI: se abandona la partida | `seleccion` + `parar_musica()` | `ui_volver` (el fundido de la música ya está) | P1 |
| PA06 | La música durante la pausa | congelada | queda así. Alternativa a decidir: seguir al 30 %, como muchos juegos modernos | — |

**Opciones**
| Código | Situación | Hoy | Propuesta | Prio |
|---|---|---|---|---|
| OP01 | Mover entre ajustes | **—** | I01 | P1 |
| OP02 | Cambiar de sección | `seleccion` | I05 | P2 |
| OP03 | Cambiar un valor (lista, volumen) | `seleccion`, ya con el volumen nuevo (sirve de muestra) | `ui_valor`. En VOLUMEN MUSICA, la muestra es la música misma | P2 |
| OP04 | Interruptor SI/NO | `seleccion` | `ui_llave_si` / `ui_llave_no` | P2 |

**Logros**
| Código | Situación | Hoy | Propuesta | Prio |
|---|---|---|---|---|
| LO01 | Cambiar de nave en el hangar | `seleccion` | `hangar_nave`: motor que arranca (barrido que sube) | P2 |
| LO02 | Volver | `seleccion` | I03 | P1 |

**Taller** (las cartas gratis del nivel 3)
| Código | Situación | Hoy | Propuesta | Prio |
|---|---|---|---|---|
| TA01 | Se abre | `nuevo_record` | stinger misterioso (arpegio) + la música del juego al 40 % (ducking) | P2 |
| TA02 | Las cartas caen de a una | — | `carta_cae`: "flip" de ruido, subiendo un tono por carta | P2 |
| TA03 | Carta RARA a la vista | — | brillo agudo cuando cae | P3 |
| TA04 | Elegir carta | `powerup` | `mejora_elegida` | P1 |

**Gasolinera**
| Código | Situación | Hoy | Propuesta | Prio |
|---|---|---|---|---|
| GA01 | Llegar | `nuevo_record` + `musica_gasolinera` | "ding-dong" de tienda + la música | P2 |
| GA02 | Las cartas caen | — | `carta_cae` | P2 |
| GA03 | Mover | `seleccion` | I01 | P1 |
| GA04 | Comprar | `moneda` + `powerup` | `caja` ("ka-ching" de caja registradora) + `mejora_elegida` | P1 |
| GA05 | No alcanza o ya está vendida (la carta tiembla) | **`golpe`** (suena a que te pegaron) | `ui_error` + bips de "no" del vendedor robot | P1 |
| GA06 | Los créditos cuentan hacia abajo | — | `contador`, como mucho ~10 tics | P3 |
| GA07 | Sello VENDIDA | — | `sello`: golpe de goma seco | P2 |
| GA08 | SORTEAR (caen cartas nuevas) | (los de comprar) | `barajar` + `carta_cae` | P2 |
| GA09 | REPARAR (+1 vida) | (comprar) | + `pw_vida` | P2 |
| GA10 | ESCUDO DE VIAJE | (comprar) | + `pw_escudo` | P2 |
| GA11 | El tanque se llena (2.5 s) y el surtidor cuenta los litros | — | `surtidor`: loop bajito de bomba que termina en "clunk" | P3 |
| GA12 | El cartel GAS titila | — | `neon`: zumbido eléctrico muy bajo, solo cuando prende | P3 |
| GA13 | Salir (ESC/B) | `seleccion` | `ui_volver` → `hiperespacio` | P1 |

**Desarrollador (F1)**: usa la interfaz común (I01-I04). Lo que hace (traer un jefe, dar un power-up) suena con sus propios sonidos. — P3.

**Explosión (muerte)**
| Código | Situación | Hoy | Propuesta | Prio |
|---|---|---|---|---|
| EX01 | El golpe que te mata | `golpe` + la música se corta en seco | `nave_muerte`; la versión estirada durante la cámara lenta (`CAMARA_LENTA` 600 ms). El corte de música queda | P1 |
| EX02 | Viñeta roja y "NAVE DESTRUIDA" (a 450 ms) | — | `destruida` | P2 |
| EX03 | Fin de la escena (1.5 s) | `game_over` | el mismo (o recompuesto con el compositor, para que tenga el estilo de los temas) | P1 |

**Iniciales**
| Código | Situación | Hoy | Propuesta | Prio |
|---|---|---|---|---|
| IR01 | Cambiar la letra (ARRIBA/ABAJO) | **—** | `ui_tecla` | P1 |
| IR02 | Confirmar letra / volver a la anterior | `seleccion` / — | I02 / I03 | P1 |
| IR03 | Tercera letra: récord guardado | `seleccion` | `record_guardado` | P2 |
| IR04 | Música | silencio | `musica_iniciales`: tema corto de "ingresá tu nombre", clásico de los arcades | P2 |

**Fin (Game Over)**
| Código | Situación | Hoy | Propuesta | Prio |
|---|---|---|---|---|
| FI01 | El puntaje cuenta (1.5 s) | — | `contador` que termina en "ding" | P2 |
| FI02 | Las estadísticas salen de a una (cada 120 ms) | — | `teclear` | P3 |
| FI03 | Fuegos artificiales con récord nuevo | — | pops chicos, con enfriamiento de 300 ms | P3 |
| FI04 | ENTER (otra vez) / ESC | `seleccion` | `ui_empezar` / I03 | P1 |
| FI05 | Música | silencio | `musica_fin`: tema corto y melancólico, en loop | P2 |

### 4.3 La nave
| Código | Situación | Dónde | Hoy | Propuesta | Prio | Anti-saturación |
|---|---|---|---|---|---|---|
| N01 | **Dash** | `Partida._al_empezar_dash` | **—** | `nave_dash` | P1 | la acción más frecuente: volumen medio-bajo, 3 variantes, nunca más fuerte que la moneda |
| N02 | Dash extra (DOBLE DASH) | `Nave._dash` (`dash_extra -= 1`) | — | `nave_dash_extra` | P2 | |
| N03 | El dash se recargó (destello cian) | `Nave._dash` (`dash_avisado`) | — | `dash_listo` | P2 | muy bajo |
| N04 | Pediste dash sin recarga (el buffer vence) | `Nave._dash` | — | `dash_vacio` | P3 | solo cuando vence el buffer |
| N05 | Te pegan con escudo: el escudo se rompe | `Partida.danar_jugador` | `golpe` | `escudo_roto` | P1 | |
| N06 | Te pegan: perdés una vida | idem | `golpe` | `nave_golpe`, al empezar el hit-stop (suena mientras todo está quieto) | P1 | prioridad 3 |
| N07 | Quedás con una vida | idem (`vidas == 1`) | — | `ultima_vida`, una sola vez. Es el "aviso de última vida" pendiente; opcional, un latido suave cada ~1.5 s (con su opción) | P1 | |
| N08 | FÉNIX: volvés con una vida | idem | `nuevo_record` | `fenix` | P1 | |
| N09 | Muerte | idem | `golpe` + corte de música | EX01 | P1 | prioridad 4 |
| N10 | Rebote al pegarle al jefe | `Partida._rebotar_en` | (lo del jefe) | lo cubre J05/J06 | NO | |
| N11 | Motor, estela, inclinación | `Nave` | — | silencio | NO | |

### 4.4 Monedas, combo y puntos
| Código | Situación | Dónde | Hoy | Propuesta | Prio | Anti-saturación |
|---|---|---|---|---|---|---|
| P01 | Moneda sin combo | `Partida._revisar_moneda` | `moneda` | `moneda_1` | P1 | |
| P02 | Moneda con multiplicador x2 a x5 | idem | `moneda` | `moneda_N` (N = multiplicador) | P1 | el tono sube con el combo: el oído "lee" el multiplicador |
| P03 | Moneda en FIEBRE DEL ORO | idem | `moneda` | `moneda_oro` | P2 | |
| P04 | Sube el multiplicador (x2, x3, x4) | `_vibrar_moneda` | — (vibra) | `combo_sube`, un instante después de la moneda | P1 | |
| P05 | Llega a x5 | idem | — (vibra) | `combo_max` | P1 | |
| P06 | Se corta el combo | `Partida.actualizar` (`combo = 0`) y `danar_jugador` | — | `combo_cortado`, solo si el multiplicador era x2 o más; en `danar_jugador` no (ya suena el golpe) | P2 | |
| P07 | Dash perfecto (cadena x1 a x5) | `Partida._dash_perfecto` | `seleccion` | `perfecto_N` (N = cadena) | P1 | uno por dash (ya está así en la regla) |
| P08 | Interceptar al embestidor | `Partida._interceptar` | `golpe` | `interceptado` (+ el perfecto) | P1 | |
| P09 | Superás el récord | `Partida.sumar_puntos` | `nuevo_record` | `record` + ducking | P1 | prioridad 4 |
| P10 | Subís de nivel (tramo nuevo: objetivo cumplido y zona despejada) | `Partida.subir_nivel` | `seleccion` | `nivel` | P1 | si llega el jefe, `alerta` lo tapa (no suena); el primer tramo de un sector nuevo no suena (ya suena `sector_nuevo`) |
| P11 | La barra de energía casi llena (parpadea naranja) | HUD | — | silencio | NO | |
| P12 | Romper un proyectil destruible con el dash (misil, meteoro) | `Partida._destruir_proyectiles` | `golpe` | `bala_rota` | P1 | |
| P13 | Textos flotantes, marcador que cuenta, créditos | | — | silencio (ya suena la causa) | NO | |

### 4.5 Power-ups
| Código | Situación | Dónde | Hoy | Propuesta | Prio |
|---|---|---|---|---|---|
| W01 | Cae una cápsula | `Partida._actualizar_powerups` | — | `capsula`, con paneo según su x | P2 |
| W02 | La cápsula se va por abajo | idem | — | silencio | NO |
| W03 | Recoger | `Partida.recoger_powerup` | `powerup` | el sonido de cada uno (W04-W11), que reemplaza al genérico | P1 |
| W04 | ESCUDO | `powerups/tipos.py` | `powerup` | `pw_escudo` | P1 |
| W05 | HIELO (además rompe las balas) | idem | `powerup` | `pw_hielo` | P1 |
| W06 | VIDA | idem | `powerup` | `pw_vida` | P1 |
| W07 | IMÁN | idem | `powerup` | `pw_iman` | P2 |
| W08 | DOBLE | idem | `powerup` | `pw_doble` | P2 |
| W09 | TURBO | idem | `powerup` | `pw_turbo` | P2 |
| W10 | RECARGA | idem | `powerup` | `pw_recarga` | P2 |
| W11 | NOVA (queda armada) | idem | `powerup` | `pw_nova` | P2 |
| W12 | NOVA estalla al terminar el dash | `Partida._al_terminar_dash` | `golpe` | `nova` | P1 |
| W13 | A un power-up con tiempo le queda 1.5 s (la cápsula del HUD parpadea) | `Partida` (con `restante()`) | — | `pw_acaba`, 3 veces (a 1.5, 1 y 0.5 s); solo uno a la vez | P2 |
| W14 | Termina un power-up con tiempo | idem | — | `pw_fin` | P2 |
| W15 | Romper un enemigo congelado (+5) | `Partida._actualizar_enemigos` | `moneda` | `hielo_roto` | P1 |

### 4.6 Mejoras
| Código | Situación | Dónde | Hoy | Propuesta | Prio | Anti-saturación |
|---|---|---|---|---|---|---|
| M01 | Elegir una carta (Taller) | `Partida.elegir_mejora` | `powerup` | `mejora_elegida` | P1 | |
| M02 | ONDA: una onda al final de cada dash | `Partida._al_terminar_dash` | — | `onda` | P2 | cada dash: bajo, con variantes |
| M03 | ECO: la copia repite el dash (20 pasos después) | `Eco.actualizar` (cuando empieza a recorrer) | — | `eco` | P2 | |
| M04 | ESCUDO ROCE: un perfecto suma carga | `Partida._regenerar_escudo` | — | `roce_carga` | P3 | |
| M05 | ESCUDO ROCE: el escudo se completa | idem | `powerup` | `pw_escudo` | P1 | |
| M06 | FILO rompe a uno que no es destruible | `destruir_con_dash` | `golpe` | `enemigo_roto` | P1 | |
| M07 | Las pasivas (MOTOR, RECARGA, COMETA, BOTÍN, ATRACCIÓN, COMBO LARGO, CORAZÓN, SUERTE, POTENCIA) | | — | silencio: se oyen en sus efectos | NO | |

### 4.7 Enemigos
| Código | Situación | Dónde | Hoy | Propuesta | Prio | Anti-saturación |
|---|---|---|---|---|---|---|
| E01 | Aparece un enemigo suelto (al final de la "X", 800 ms) | `Enemigo.reaparecer` → cuando `activo()` pasa a True | — | `aparece` | P2 | enfriamiento 120 ms. Los que llegan en escuadrón no lo usan (E01b) |
| E01b | Un escuadrón se asoma por un borde (la flecha de aviso) | `Director.lanzar_escuadron` | — | `escuadron_llega`, uno por escuadrón, con paneo del lado por donde entra | P2 | enfriamiento 250 ms |
| E02 | Hijos del divisor que nacen parpadeando | `nacer_en` | — | lo cubre E12 | NO | |
| E03 | Destruido con el dash | `Partida.destruir_con_dash` | `golpe` | `enemigo_roto`, más grave cuanto más grande | P1 | máx 3 voces |
| E04 | Congelado roto | | `moneda` | W15 | P1 | |
| E05 | Aturdido (estrellitas) | `Partida._interceptar`, ondas | — | `aturdido`, solo en la intercepción | P3 | |
| E06 | Te choca y explota (dron, abeja) | `_actualizar_enemigos` | (golpe del daño) | lo cubre N06 | NO | |
| E07 | Perseguidor | | — | silencio: es "el que te sigue callado" | NO | |
| E08 | Rebotador: choca contra la pared (se aplasta) | `Rebotador.actualizar` (`estado = "choque"`) | — | `rebote`, con paneo | P2 | 1 cada 200 ms entre todos; bajo |
| E09 | **Embestidor apunta** (600 ms, línea roja) | `Embestidor.mover` (`fase = "apuntar"`) | **—** | `embestidor_apunta`, que dura lo mismo que el aviso | P1 | prioridad 3 |
| E10 | **Embestidor: la mira se fija** (`mira_fija`, `apunte_fijo` antes de embestir) | idem | — | `mira_fija`: "¡ahora correte!" | P1 | en DIFICIL y PESADILLA (`apunte_fijo` = 0) suena con la embestida |
| E11 | Embestidor carga (500 ms) | idem (`fase = "cargar"`) | — | `embestida` | P1 | |
| E12 | El divisor se parte | `DivisorBase.al_destruirse` | `golpe` (destruir) | `divisor_parte` (según el tamaño) en vez de `enemigo_roto` | P2 | |
| E13 | **Enjambre: aviso de picada** (450 ms, destellan) | `Bandada.actualizar` (`fase = "aviso"`) | — | `enjambre_aviso`, uno por bandada | P1 | |
| E14 | Enjambre: picada | idem (`"picada"`) | — | `enjambre_picada` | P2 | |
| E15 | Enjambre entero destruido con el dash | `Dron.al_destruirse` (`todos_con_dash`) | — | `bonus` | P2 | |
| E16 | Una abeja sale de la compuerta | `Colmena.soltar_abeja` | — | `abeja_sale` | P2 | máx 2 voces |
| E17 | **Abeja: aviso** (400 ms, "!") | `Abeja.mover` (`estado = "aviso"`) | — | `abeja_aviso` | P1 | máx 2 voces |
| E18 | La abeja vuelve a casa | `volver_a_casa` | — | silencio | NO | |
| E19 | Enemigos que se van (se retiran volando: fin de su turno, cambio de tramo) | `Enemigo.retirarse` | — | silencio: se ven irse en gris | — | el asedio perdido sí suena (D03) |
| E20 | **Ladrón: agarra la moneda** (se queda quieto 500 ms con ella: el aviso de que va a huir) | `Partida.robar_moneda` | `ladron_roba` | `ladron_roba`, que dura lo mismo que el aviso | P1 | 1 voz |
| E21 | Ladrón alcanzado con el dash: moneda recuperada | `Partida.recuperar_moneda` | `moneda_recuperada` (+ la moneda, `enemigo_roto` y el perfecto) | `moneda_recuperada` | P1 | |
| E22 | El ladrón se escapa con la moneda (se corta el combo) | `Partida.moneda_escapada` | `ladron_escapa` | `ladron_escapa`, con paneo hacia el borde (en vez de `combo_cortado`) | P1 | |
| E23 | El dash rebota en el escudo del escudero | `Partida._rebotar_en_escudo` | `escudo_bloquea` | `escudo_bloquea` | P1 | enfriamiento 80 ms |
| E24 | Escudero roto por la espalda | `Partida.destruir_con_dash` | `enemigo_roto` + el perfecto | lo cubre E03 | NO | |

**Proyectiles sueltos** (de cualquier jefe):

| Código | Situación | Dónde | Hoy | Propuesta | Prio | Anti-saturación |
|---|---|---|---|---|---|---|
| B01 | Mina: el último medio segundo parpadea | `Mina.mover` (`espera < 500`) | — | `mina_tic`, cada vez más seguido (3-4 bips) | P1 | |
| B02 | La mina estalla en cruz | `Mina.estallar` | `golpe` | `mina_estalla` | P1 | |
| B03 | Las balas que rompen la onda, el hielo o la muerte del jefe | `onda_expansiva`, `romper_balas` | — | silencio: suena la causa | NO | |

### 4.8 Director: oleadas, anomalías y desafíos
| Código | Situación | Dónde | Hoy | Propuesta | Prio |
|---|---|---|---|---|---|
| D01 | **Empieza el ASEDIO** (tramo 4) | `Director.empezar_asedio` | **`nuevo_record`** (suena a premio) | `oleada` | P1 |
| D02 | Asedio superado | `terminar_asedio(superado=True)` | `powerup` | `oleada_superada` + ducking | P1 |
| D03 | El asedio termina y perdiste una vida | `terminar_asedio(False)` | — | `retirada` | P3 |
| D04 | Llega una anomalía | `Director.empezar_anomalia` | `nuevo_record` | el stinger de cada una (D05, D09, D12, D14) | P1 |
| D05 | Asteroides: llegan | | | `asteroides_llega` | P1 |
| D06 | Asteroides: columna de aviso (900 ms) | `LluviaDeAsteroides.actualizar` | — | `meteoro_aviso`, con paneo según la columna | P1 |
| D07 | El meteoro pasa | | — | silencio (el aviso alcanza) | NO |
| D08 | Romper un meteoro con el dash | | `golpe` | P12 | P1 |
| D09 | Tormenta: llega | | | `tormenta_llega` | P1 |
| D10 | Tormenta: aviso (la franja parpadea 1.2 s) | `TormentaSolar.actualizar` (`"aviso"`) | — | `tormenta_aviso` | P1 |
| D11 | Tormenta: llamarada (450 ms) | idem (`"llamarada"`) | **`golpe`** (suena a que te pegaron) | `llamarada` | P1 |
| D12 | Niebla: llega | | | `niebla_llega` | P1 |
| D13 | Niebla: mientras dura | `Niebla` | — | la música al 70 % (ducking leve) + viento muy bajo | P3 |
| D14 | Fiebre del oro: llega | | | `oro_llega` | P1 |
| D15 | Termina la anomalía | `Director.terminar_anomalia` (si no la cortó el jefe) | — | `anomalia_fin` | P2 |
| D16 | Desafío nuevo (la ficha de la derecha) | `Director.proponer_desafio` | `seleccion` | `desafio_nuevo` | P2 |
| D17 | El desafío avanza (CAZADOR 3/10...) | `avanzar()` | — | silencio (ya suena la acción) | NO |
| D18 | Desafío cumplido | `Director.revisar_desafio` | `powerup` | `desafio_cumplido` + ducking | P1 |
| D19 | **Desafío fallado** | idem (`estado == "fallado"`) | **—** | `desafio_fallado` | P1 |
| D20 | Llega el escuadrón siguiente del tramo | `Director._escuadrones` | — | E01b | P2 |
| D21 | ¡OBJETIVO CUMPLIDO! (el del tramo) | `Director._festejar_objetivo` | — | `bonus` (provisorio: podría tener uno propio) | P2 |
| D22 | El paso se abre (el objetivo no se cumplió en 90 s) | `Director._abrir_el_paso` | — | `anomalia_fin` | P3 |

### 4.9 Carteles y HUD
| Código | Situación | Dónde | Hoy | Propuesta | Prio | Anti-saturación |
|---|---|---|---|---|---|---|
| C01 | Una pancarta se abre (TRAMO, ASEDIO, anomalía, RÉCORD) | `carteles.pancarta` | — | silencio: el aviso ya trae el sonido de lo que pasó (P10, D01...) | NO | |
| C02 | El subtítulo se escribe solo (18 ms por letra) | `carteles.pancarta` | — | `teclear`, uno cada 3 letras | P3 | muy bajo; se calcula en la lógica con `partida.tiempo` |
| C03 | Ficha NUEVO ENEMIGO (entra por la izquierda) | `Director._presentar` (la primera vez que llega un tipo) | — | `ficha_enemigo` | P2 | |
| C04 | Fichas del desafío (derecha) | | | D16, D18, D19 | — | |
| C05 | Logro (abajo, la insignia y se abre) | `Partida.revisar_logros` | `nuevo_record` | `logro` + ducking; si regala una nave, `nave_nueva` | P1 | uno por ficha, en fila (como `fichas_logro`) |
| C06 | ¡JEFE VENCIDO! (franjas) | `Partida.jefe_vencido` | (la explosión) | J10 | P1 | |
| C07 | Rango: el panel se abre | `carteles.rango` (en la lógica: `tiempo_cartel_rango`) | — | `franjas` suave | P3 | |
| C08 | Rango: las filas salen de a una (cada estrella nace blanca) | idem | — | `estrella`, subiendo un tono por estrella ganada; las filas sin estrella, `teclear` | P2 | |
| C09 | Rango: cae la letra (`RANGO_SELLO` 2.1 s) | `Director.pagar_rango` | `nuevo_record` (S/A) / `seleccion` (B/C) | `sello_S/A/B/C` + ducking | P1 | prioridad 4 |
| C10 | Sector nuevo (el nombre letra por letra + el lema) | `tiempo_cartel_sector` | — | `sector_nuevo` + `teclear` | P2 | |
| C11 | La barra del jefe se llena de a un segmento (45 ms cada uno) | `hud._barra_jefe` (llevarlo a la lógica) | — | `barra_jefe`, subiendo de tono (como en los juegos de pelea) | P2 | |
| C12 | Combo, energía, marcador, carteles que se apagan por tapar | HUD | — | silencio | NO | |

### 4.10 Jefes
**Comunes a todos** (`jefes/base.py`, `Partida`):

| Código | Situación | Dónde | Hoy | Propuesta | Prio |
|---|---|---|---|---|---|
| J01 | **¡ALERTA! / SE ACERCA UN JEFE** (franjas de cine, sirenas, 1.4 s) | `Partida.iniciar_jefe` | — (vibra; la música pasa a `jefe` con fundido) | la música del juego se corta con un fundido corto; `franjas` cuando entran las franjas y `alerta` (sirena) mientras duran las luces | P1 |
| J02 | La presentación: el nombre entra desde la izquierda y el apodo desde la derecha | `hud._tarjeta_del_jefe` (el tiempo sale de `partida.tiempo`) | — | `presentacion` (un golpe para cada uno); **la música del jefe arranca en el nombre** | P1 |
| J03 | Los enemigos explotan al llegar el jefe | `iniciar_jefe` | — | `retirada` | P3 |
| J04 | **Se abre la ventana para pegarle** ("¡DASH!": cansado, recalentado, aturdida, expuesta, mareada) | el `cambiar_fase` de cada jefe | — | `vulnerable`, siempre el mismo | P1 |
| J05 | Golpe al núcleo | `Jefe.recibir_golpe` | `golpe` | `jefe_golpe` + la voz del jefe | P1 |
| J06 | Golpe a una parte | `Jefe.golpear_parte` | `golpe` | `jefe_parte` | P1 |
| J07 | Parte rota | idem | `golpe` | `parte_rota` | P1 |
| J08 | **El golpe que lo mata** | `recibir_golpe` (`vida <= 0`) | `golpe` | `golpe_final` + la música se corta en seco | P1 |
| J09 | Agonía (2 s de explosiones por el cuerpo) | `Jefe.actualizar` (`"morir"`) | — | `agonia`, en el mismo azar de las explosiones; máx 1 cada 150 ms | P1 |
| J10 | La explosión final | `Jefe.explotar` | `golpe` + `powerup` | `jefe_explota`, ~300 ms de silencio y después `jefe_vencido` (con el cartel) | P1 |
| J11 | Congelado (HIELO) | | — | lo cubre W05 | NO |
| J12 | Cada bala de una ráfaga | `_actualizar_jefe` (fogonazos) | — | **nunca una por bala**: un sonido por ráfaga o pulso (abajo) | NO |

**EL OJO** (Cinturón)

| Código | Situación | Hoy | Propuesta | Prio |
|---|---|---|---|---|
| OJ01 | Flotar (va de lado a lado) | — | zumbido grave muy bajo | P3 |
| OJ02 | **Carga** (0.7 s, chispas que se juntan en el ojo) | — | `ojo_carga`: carga que sube y termina justo en el primer disparo | P1 |
| OJ03 | Ráfaga en abanico (cada 450 ms) | — | `ojo_abanico`: láser corto, uno por ráfaga | P1 |
| OJ04 | Ráfaga en anillo | — | `ojo_anillo`: más grave y con eco | P1 |
| OJ05 | Cansado (se abren las placas) | — | vapor + J04 | P2 |
| OJ06 | Vuelve a flotar (cierra) | — | clac mecánico | P3 |
| OJ07 | La voz al recibir un golpe | — | grito electrónico corto, más grave con menos vida | P2 |

**ACORAZADO IMPERIAL** (Carmesí). Es una marcha militar: sus sonidos van en el pulso.

| Código | Situación | Hoy | Propuesta | Prio |
|---|---|---|---|---|
| FO01 | Las 4 lamparitas del compás | — | `compas`: tic metálico por pulso, con acento en el primero | P2 |
| FO02 | Reubicarse | — | motor pesado | P3 |
| FO03 | Cargar (chispas en la boca del cañón) | — | `carga_canon`, distinto para cada ataque | P2 |
| FO04 | Ráfaga: 3 obuses, uno por pulso | — | `obus`: cañonazo grave | P1 |
| FO05 | Misiles (2) | — | `misil`: lanzamiento + bip mientras te sigue (`guiado`) | P1 |
| FO06 | **Láser: carga** | — | `laser_carga` | P1 |
| FO07 | **Láser prendido** (barre hacia vos) | `golpe` (al prender) | `laser`: loop en un canal propio mientras `laser_prendido`, que se corta al apagarse | P1 |
| FO08 | Minas lanzadas (2) | — | `mina_lanza` (thunk); después B01 y B02 | P2 |
| FO09 | Recalentado (los cañones echan fuego) | — | siseo de vapor + tics de metal que se enfría; J04 | P2 |
| FO10 | Cañón roto | `golpe` | J07 + metal que cae | P2 |
| FO11 | Descubrirse (4 pulsos de explosiones) | — | `agonia` + una alarma interna | P2 |
| FO12 | **¡SIN CORAZA!** | `golpe` | `coraza`: gran crash metálico | P1 |
| FO13 | Cortinas: el aviso | — | `cortina_aviso`: retumbo de techo | P1 |
| FO14 | Cortinas: caen los escombros | `golpe` | `escombros` | P1 |
| FO15 | Apuntar (se pone encima) | — | servo | P3 |
| FO16 | **Fijar** (quieta y temblando: ¡salí de abajo!) | — (vibra `aviso_jefe`) | `fijar`: traba + tensión | P1 |
| FO17 | Caer | — | `caida`: silbido que baja | P1 |
| FO18 | Estrellarse + ondas a ras del piso | `golpe` | `estrellarse`: impacto gigante + `onda_suelo` | P1 |
| FO19 | Subir | — | hidráulica | P3 |

**DEVORADORA DE ESTRELLAS** (Esmeralda)

| Código | Situación | Hoy | Propuesta | Prio |
|---|---|---|---|---|
| SE01 | Entrada nadando en zigzag | — | `siseo` largo | P2 |
| SE02 | Nadar (te rodea) | — | silencio | NO |
| SE03 | **Acechar** (2 pulsos; en el último la mordida queda fija) | — | `cascabel`: cascabel de serpiente al ritmo del pulso | P1 |
| SE04 | Morder ("¡SSSS!") | — | `mordida`: siseo + embestida | P1 |
| SE05 | Choca con un borde → aturdida | `golpe` | `serpiente_choca` + J04 | P1 |
| SE06 | Mareada (no chocó) | — | notas que se tambalean (vibrato) + J04 | P2 |
| SE07 | **Enroscarse** (círculo de aviso que se cierra) | — | `enroscar`: siseo que sube mientras se cierra | P1 |
| SE08 | Escupe veneno (pulsos 2 y 4, desde la mitad de la vida) | — | `escupir` | P2 |
| SE09 | Le cortás el cascabel ("¡SSSIII!") | `golpe` | `corte` + grito agudo (su voz) | P1 |

**MADRE DEL ENJAMBRE** (Ámbar)

| Código | Situación | Hoy | Propuesta | Prio |
|---|---|---|---|---|
| CO01 | Flotar | — | zumbido de panal, bajo (su identidad) | P3 |
| CO02 | **Abrir compuerta** ("BZZZ", 2 pulsos) | — | `compuerta_abre`: chirrido + zumbido | P1 |
| CO03 | Soltar abeja (una por pulso) | — | E16 | P2 |
| CO04 | Expuesta | — | J04 | P1 |
| CO05 | Compuerta rota ("¡BZZZT!") | `golpe` | J07 + cera que se rompe | P2 |
| CO06 | "¡A CASA, HIJAS!" | — | `llamado`: zumbido que llama (glissando) | P2 |
| CO07 | Enfurecerse (3 pulsos) | — | `furia`: zumbido grave que crece | P2 |
| CO08 | **Temblar** (aviso de 3 pulsos; en el 2 queda fija) | — (vibra `zumbido`) | `temblar`: traqueteo que crece + traba en el pulso 2 | P1 |
| CO09 | Embestir ("¡BZZZZZ!") | — | `embestida_colmena` | P1 |
| CO10 | Choca con la pared (cada rebote) | `golpe` | `colmena_choca`: golpe sordo + miel | P1 |
| CO11 | Volver | — | silencio | NO |

**EL FIN DE LA LUZ** (Abismo)

| Código | Situación | Hoy | Propuesta | Prio |
|---|---|---|---|---|
| SI01 | Nace de un punto (crece, el polvo cae al centro) | — | `nacer`: implosión al revés, que sube | P1 |
| SI02 | Girar: el anillo avanza un lugar por pulso | — | `anillo_tic`: clic grave de piedra, en el pulso | P2 |
| SI03 | Brazos (2-3 balas por pulso) | — | `brazos`: disparo suave, uno por pulso | P2 |
| SI04 | **Inhalar** (3 pulsos, tira fuerte) | — (vibra) | `inhalar`: succión que crece | P1 |
| SI05 | Exhalar (nova con un hueco + empujón) | `golpe` | `exhalar`: estallido + viento | P1 |
| SI06 | Colapsar ("¡COLAPSO!") | — | `colapso`: implosión | P2 |
| SI07 | Expuesta | — | J04 + zumbido inestable | P1 |
| SI08 | Estallido (al pegarle: te empuja y el anillo se abre) | (lo del golpe) | `estallido` | P2 |
| SI09 | Se come la moneda | — | `moneda_tragada`: la moneda bajando de tono (un detalle con humor) | P3 |

### 4.11 Fondo y ambiente
| Código | Situación | Dónde | Hoy | Propuesta | Prio |
|---|---|---|---|---|---|
| F01 | **Salto al hiperespacio** (al empezar y al salir de la gasolinera, 1.5 s) | `Fondo.saltar_al_hiperespacio` | — | `hiperespacio` | P1 |
| F02 | Cambio de sector (los colores cambian en 4 etapas) | `Fondo.ir_a_sector` | — | el ambiente nuevo entra con un fundido cruzado (canal de ambiente) | P3 |
| F03-F07 | El ambiente de cada sector (rocas, brasas, luciérnagas, panal, polvo) | `Fondo._mover_ambiente` | — | `amb_*` en loop, muy bajo; baja más en las peleas | P3 |
| F08 | Relámpago (Carmesí) | `Fondo` (`relampago = 8`) | — | `trueno` lejano, 300-800 ms después del destello | P2 |
| F09 | Estrella fugaz, motas | | — | silencio | NO |

### 4.12 Sistema
| Código | Situación | Hoy | Propuesta | Prio |
|---|---|---|---|---|
| S01 | Pausa automática (foco perdido, mando desconectado) | — | PA01 | P1 |
| S02 | Se conecta o desconecta un mando | — | dos notas que suben / bajan | P3 |
| S03 | F11, cerrar la ventana | — | silencio | NO |

---

## 5. Música: qué suena en cada momento

| Código | Momento | Hoy | Propuesta | Prio |
|---|---|---|---|---|
| MU01 | Inicio, Dificultad, Logros (y Opciones desde Inicio) | `menu` ("Hangar", rehecho en el estudio) | igual | — |
| MU02 | READY? / GO! | `juego` desde READY | silencio en READY; `juego` entra en el GO | P2 |
| MU03 | Jugando | `musica.mp3` | pasarla a OGG (hoy tiene un hueco al dar la vuelta). Más adelante: una variante por sector (la misma base con otro color e instrumentos) | P2 / P3 |
| MU04 | El nivel antes del jefe ("PROXIMO NIVEL: ¡JEFE!") | `juego` | un tema de tensión o un remate | P3 |
| MU05 | ¡ALERTA! | `jefe`, con fundido desde que llega | silencio + sirena; `jefe` arranca con el nombre (J02) | P1 |
| MU06 | La pelea | un tema por jefe, todos del estudio en Re menor (el Ojo `musica_jefe`, la Fortaleza marcha, la Serpiente con swing, la Colmena zumba, la Singularidad lenta y grave) | igual | — |
| MU07 | El jefe muere | `jefe` hasta que explota | se corta en el golpe final (J08); la explosión; después la fanfarria | P1 |
| MU08 | El cierre del sector (¡JEFE VENCIDO! + rango, 6.5 s) | `juego` | el ambiente solo, o un colchón suave, para que la fanfarria y el sello se oigan solos; después la gasolinera | P2 |
| MU09 | Gasolinera | `gasolinera` ("Parada técnica", rehecho en el estudio) | igual (al volver, el tema del juego empieza de cero: está bien, es un sector nuevo) | — |
| MU10 | Taller | `juego` sigue | `juego` al 40 % (ducking) | P2 |
| MU11 | Pausa, Opciones desde Pausa, Desarrollador | congelada | igual (o al 30 %, ver PA06) | — |
| MU12 | Anomalía | `juego` | igual; en la niebla, al 70 % | P3 |
| MU13 | Muerte y explosión | se corta en seco; `game_over` al final | igual (está muy bien) | — |
| MU14 | Iniciales | silencio | `musica_iniciales` | P2 |
| MU15 | Fin | silencio | `musica_fin` | P2 |
| MU16 | Última vida | — | opcional: el latido de N07 encima de la música | P3 |

**Jingles** (efectos con música, `vuelta=False`): `listo_ready`, `listo_go`, `nivel`, `record`, `logro`, `oleada_superada`, `desafio_cumplido`, `jefe_vencido`, `sello_S/A/B/C`, `sector_nuevo`, `game_over`, `record_guardado`. Tienen que estar en la tonalidad del tema que suena debajo (La menor para el juego y el menú) para no chocar. Los que suenan encima de la música (`nivel`, `logro`, `oleada_superada`, `desafio_cumplido`) además siguen al acorde (regla 15).

---

## 6. Silencios a propósito (lo que NO tiene que sonar)

Un juego que suena a todo cansa en 5 minutos. Esto se deja callado a propósito:
- **Cada bala de un jefe.** Suena la ráfaga o el pulso, una vez.
- **El motor de la nave**, la estela y la inclinación. El dash ya es "la voz" de la nave.
- El imán y la ATRACCIÓN cuadro por cuadro, la moneda que brilla, las partículas, las chispas y los fogonazos.
- Cada letra de los carteles: como mucho un tic cada 3 letras.
- Las páginas del Inicio que cambian solas, el brillo del logo y la nave grande.
- El perseguidor (su silencio es su personalidad), las abejas que vuelven a casa y la serpiente nadando.
- El HUD: el marcador que cuenta, el combo, la barra de energía y los carteles que se apagan por tapar.
- Lo que ya suena por su causa: los textos flotantes, el avance de un desafío, las balas que rompe una onda.
- Las estrellas fugaces y las motas del ambiente.

Además, **no vibra** lo que pasa todo el tiempo (ver `haptica.py`), y la misma idea vale para el sonido: lo frecuente, bajo y corto.

---

## 7. Orden sugerido para hacerlo

**Fase A: el sistema, sin sonidos nuevos todavía** ✅ hecha (2026-10-13; ver "El mezclador" en CLAUDE.md)
- Implementar las reglas 2 a 6, 11, 12 y 13 de la sección 2 en `sonido.py`:
  - `reproducir(nombre, x=None)` con paneo;
  - categorías, prioridad, `voces` y `enfriamiento` (tablas en `config.py`);
  - variantes (`nombre_1`, `nombre_2`... elegidas sin repetir);
  - `atenuar_musica(nivel, ms)` (ducking);
  - `set_num_channels(24)` y el canal de ambiente y de loops (`tocar_loop(nombre)` / `parar_loop(nombre)`).
- Sumar VOLUMEN MUSICA / VOLUMEN EFECTOS y AUDIO MONO en Opciones.
- Tests con un `SonidosFalsos` que anote lo que se pidió, como el `MandoFalso` de la vibración.
- En el compositor, sumar lo que hace falta para efectos que no son notas:
  - **barrido** (una nota que sube o baja de frecuencia);
  - **ruido con envolvente y filtro** (explosiones, vapor, viento);
  - **arpegio rápido** (jingles).

**Fase B: las P1 (~70 sonidos, muchos son variantes o escalas del mismo)**
- La interfaz común, el dash, las monedas en escala, el perfecto en escala, los golpes que te dan (escudo, vida, última vida, muerte), los power-ups y el hielo.
- Los avisos de peligro: embestidor, enjambre, abejas, minas, asteroides, tormenta, y los avisos de los 5 jefes.
- La ¡ALERTA! y la presentación del jefe, `vulnerable`, el golpe final, la explosión y la fanfarria, el rango.
- La oleada, las anomalías, los desafíos, el récord, los logros, READY/GO, la pausa, el hiperespacio y la gasolinera (comprar / no alcanza).

**Fase C: las P2**
- La identidad de cada enemigo y cada jefe (voces, compás de la Fortaleza, cascabel...).
- Las cartas que caen, el contador del Fin, la barra del jefe, las estrellas del rango, el sector nuevo.
- La música de Iniciales y Fin, el ducking del Taller y del cierre, la música que entra en el GO, `musica.mp3` → OGG.

**Fase D: las P3**
- El ambiente de cada sector, el trueno, el surtidor y el neón, los tics de los textos, los temas por jefe y por sector.

**Cada sonido nuevo:**
1. Componerlo (`COMPOSICIONES`).
2. Sumarlo a `EFECTOS` con su categoría, voces y enfriamiento.
3. Llamarlo donde dice la columna "Dónde", en la lógica.
4. Agregar un test que compruebe que ese evento lo pide.
5. Marcar la fila acá como hecha (la columna **Hoy** pasa a decir el nombre del sonido).

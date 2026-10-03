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
- **Registros (patrón *Registry*).** Los enemigos, jefes y power-ups se anotan solos con un decorador (`@registrar_enemigo`…). El resto del juego los crea por nombre, así que **agregar uno nuevo no obliga a tocar el resto del código**.
- **Clases base (patrón *Template Method*).** `Enemigo`, `Jefe` y `PowerUp` resuelven todo lo común: aparecer con aviso, congelarse con el hielo, el sprite de respaldo, el HUD… Cada tipo escribe solo lo que lo hace distinto.
- **`Partida` en vez de variables globales.** Todo el estado de una partida vive en un objeto. Empezar otra partida es crear una nueva, así no queda nada "sucio" de la anterior.
- **Entrada por acciones.** El juego pregunta "¿se apretó DASH?", no "¿se apretó la barra espaciadora?". Así teclado y mando funcionan igual.
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
3. Usalo en `ENEMIGOS_POR_NIVEL` o `ENEMIGOS_POR_JEFE` (`config.py`).
4. (Opcional) `sprites/zigzag.png`: 2 cuadros de 40x40. Si no está, se dibuja uno de respaldo con su color.

Si necesita algo al aparecer, usá `al_aparecer()`; para dibujarse distinto, `dibujar_cuerpo()`. Mirá `embestidor.py` como ejemplo completo.

### Un jefe
1. Creá `juego/jefes/mi_jefe.py` con una clase que herede de `Jefe`, con `@registrar_jefe` y un `tipo`.
2. Escribí `cargar_animaciones()`, `al_terminar_de_entrar()`, `actualizar_fase()` (sus fases y ataques) y `animacion()`.
3. Importalo en `juego/jefes/__init__.py` y agregalo a `ORDEN_JEFES` en `config.py` (por ejemplo, `["ojo", "mi_jefe"]` para que se turnen).

Entrar, morir, la vida, el congelado y el destello al recibir un golpe ya los resuelve la clase base. `ojo.py` es el ejemplo.

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

"""
Los instrumentos ya armados ("presets"), la paleta de todo el sonido del juego.

Idea general (para que tenga cuerpo y no sea chillon):
- Nada de ondas "desnudas": todo pasa por un filtro que redondea los agudos.
- Los sonidos con cuerpo tienen varias voces desafinadas y abiertas en estereo.
- Los graves llevan un sub-oscilador (un seno una octava abajo): peso sin barro.
- El brillo vive en el ataque (la envolvente del filtro) y despues se apaga: suena
  "caro" y no cansa al oido.
"""
from herramientas.estudio.sintesis import Sinte, FM

# ---------- Colchones (acordes largos) ----------

# El pad del synthwave: muchas sierras desafinadas, filtro cerrado que respira
PAD_CALIDO = Sinte(osciladores=(("sierra", 1.0, 0), ("sierra", 0.45, 12)), voces=6, desafinacion=16, ancho=1.0,
                   ruido=0.02, corte=1100, resonancia=0.12, env_filtro=1.3, seguimiento=0.3, polos=4,
                   amp=(0.45, 1.2, 0.85, 1.1), filtro_adsr=(0.9, 1.6, 0.35, 1.2), saturacion=0.15, volumen=0.8)

# Mas grave y tenso (para los jefes)
PAD_OSCURO = Sinte(osciladores=(("sierra", 1.0, 0), ("cuadrada", 0.5, -12)), voces=6, desafinacion=22, ancho=0.9,
                   corte=450, resonancia=0.25, env_filtro=1.0, seguimiento=0.2, polos=4,
                   amp=(0.3, 1.0, 0.9, 0.9), filtro_adsr=(0.6, 1.2, 0.3, 1.0), saturacion=0.3, volumen=0.8)

# Calido y quieto (para la gasolinera y los menus): triangulos y un poco de sierra
PAD_SUAVE = Sinte(osciladores=(("triangulo", 1.0, 0), ("sierra", 0.25, 0)), voces=4, desafinacion=10, ancho=0.8,
                  corte=1200, resonancia=0.05, env_filtro=0.6, polos=2,
                  amp=(0.6, 1.5, 0.9, 1.4), filtro_adsr=(1.0, 2.0, 0.5, 1.5), volumen=0.9)

# ---------- Bajos ----------

# El bajo analogico: sierra + cuadrada con sub, el filtro "muerde" en cada nota. Mono (el bajo
# va siempre al centro: es lo que sostiene todo)
BAJO_ANALOGICO = Sinte(osciladores=(("sierra", 1.0, 0), ("cuadrada", 0.5, 0)), voces=2, desafinacion=5, ancho=0.0,
                       sub=0.35, corte=240, resonancia=0.3, env_filtro=2.8, seguimiento=0.35, polos=4,
                       amp=(0.003, 0.35, 0.85, 0.05), filtro_adsr=(0.002, 0.11, 0.08, 0.08),
                       saturacion=0.35, deriva=1.0)

# Un sub casi puro (redondo, para debajo de todo)
BAJO_SUB = Sinte(osciladores=(("seno", 1.0, 0), ("triangulo", 0.25, 0)), corte=600, polos=2,
                 amp=(0.006, 0.6, 0.9, 0.08), saturacion=0.2, deriva=0.5)

# Distorsionado y con mas mordida (jefes)
BAJO_RUGIDO = Sinte(osciladores=(("sierra", 1.0, 0), ("sierra", 0.8, -12)), voces=3, desafinacion=9, ancho=0.15,
                    sub=0.5, corte=260, resonancia=0.4, env_filtro=2.8, seguimiento=0.3, polos=4,
                    amp=(0.003, 0.3, 0.8, 0.06), filtro_adsr=(0.002, 0.14, 0.15, 0.1), saturacion=0.7)

# ---------- Melodicos ----------

# Pluck: el ataque brilla y se apaga enseguida (arpegios)
PLUCK = Sinte(osciladores=(("sierra", 1.0, 0), ("cuadrada", 0.5, 12)), voces=3, desafinacion=8, ancho=0.6,
              corte=700, resonancia=0.28, env_filtro=3.3, seguimiento=0.6, polos=2,
              amp=(0.002, 0.22, 0.0, 0.18), filtro_adsr=(0.001, 0.085, 0.0, 0.1), saturacion=0.1)

# El lead: calido, con vibrato que entra tarde (canta, no grita)
LEAD_CALIDO = Sinte(osciladores=(("sierra", 1.0, 0), ("cuadrada", 0.35, -12)), voces=3, desafinacion=7, ancho=0.3,
                    corte=1600, resonancia=0.2, env_filtro=1.4, seguimiento=0.5, polos=4,
                    amp=(0.012, 0.5, 0.85, 0.22), filtro_adsr=(0.01, 0.35, 0.45, 0.3),
                    vibrato=(5.2, 0.16, 0.3), saturacion=0.25)

# Un lead hueco (cuadradas anchas, filtrado): mas suave, para menus
LEAD_HUECO = Sinte(osciladores=(("cuadrada", 1.0, 0), ("triangulo", 0.6, 12)), voces=2, desafinacion=5, ancho=0.3,
                   ancho_pulso=0.42, corte=900, resonancia=0.1, env_filtro=1.0, seguimiento=0.5, polos=4,
                   amp=(0.02, 0.6, 0.8, 0.3), filtro_adsr=(0.02, 0.4, 0.4, 0.3), vibrato=(5.0, 0.12, 0.35))

# ---------- FM ----------

# Piano electrico (tipo Rhodes/DX7): calido, con la "campanita" del ataque
EPIANO = FM(moduladores=((1.0, 1.5, 0.8), (14.0, 0.45, 0.02)), amp=(0.002, 1.8, 0.0, 0.45), voces=2,
            desafinacion=4, ancho=0.4, corte=5500)

# Campana de cristal (larga). Relaciones ENTERAS: todos sus parciales son armonicos de la
# nota. Antes era 3.5 (una campana "de verdad", inarmonica): cada nota sumaba un parcial a
# -5 dB en 2.5 veces su frecuencia, una tercera mayor arriba: sobre un La sonaba un Do# que
# chocaba con la musica en La menor. El brillo de campana sale del 7 y de la caida rapida
CAMPANA = FM(moduladores=((3.0, 1.6, 0.9), (7.0, 0.35, 0.25)), amp=(0.001, 1.6, 0.0, 1.2), voces=2, desafinacion=3,
             ancho=0.5, corte=7000)

# Campanita corta y brillante (premios, monedas)
CRISTAL = FM(moduladores=((5.0, 1.1, 0.12), (2.0, 0.6, 0.3)), amp=(0.001, 0.5, 0.0, 0.35), corte=5500)

# Marimba de madera (golpes con altura, interfaz)
MARIMBA = FM(moduladores=((4.0, 2.2, 0.05),), amp=(0.001, 0.32, 0.0, 0.15), corte=6000)

# Metal (golpes metalicos, el "clang" de la Fortaleza). Antes usaba relaciones 1.41 y 3.73
# (inarmonicas): un "Do5" sonaba mas fuerte en un La3 desafinado un cuarto de tono. Ahora
# son casi enteras (1.002 y 3.997): los parciales caen sobre los armonicos de la nota pero
# corridos un 0.2 %, asi "baten" entre ellos (el brillo inquieto del metal) sin desafinar
METAL = FM(moduladores=((1.002, 3.0, 0.25), (3.997, 1.5, 0.1)), amp=(0.001, 0.6, 0.0, 0.5), corte=6000)


# ---------- Para efectos ----------

# Zumbido de insecto (abejas, enjambre): pulso angosto filtrado, sostenido
ZUMBIDO = Sinte(osciladores=(("cuadrada", 1.0, 0), ("sierra", 0.4, 0.07)), ancho_pulso=0.2, corte=1400,
                resonancia=0.2, polos=2, amp=(0.01, 0.2, 0.9, 0.05), deriva=6.0)

# Sirena y alarmas: redonda, sostenida, con cuerpo (no un pitido)
SIRENA = Sinte(osciladores=(("sierra", 1.0, 0), ("cuadrada", 0.6, -12)), voces=2, desafinacion=8, ancho=0.4,
               corte=1300, resonancia=0.25, env_filtro=0.6, polos=4, amp=(0.01, 0.3, 0.9, 0.08),
               filtro_adsr=(0.01, 0.2, 0.6, 0.1), saturacion=0.3)

# Laser y cargas: sierra con resonancia (el "pew" con cuerpo)
LASER = Sinte(osciladores=(("sierra", 1.0, 0), ("sierra", 0.7, 0.1)), voces=2, desafinacion=12, ancho=0.5,
              corte=1800, resonancia=0.55, env_filtro=1.2, polos=2, amp=(0.002, 0.3, 0.8, 0.06),
              filtro_adsr=(0.001, 0.12, 0.3, 0.1), saturacion=0.2)

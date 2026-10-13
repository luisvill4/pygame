"""
Caza Monedas: juego arcade 2D hecho con Pygame.

Mapa del paquete (cada modulo tiene una sola responsabilidad):

    config.py       numeros, colores y reglas que se pueden ajustar (sin logica)
    recursos.py     carga de imagenes y fuentes, con cache
    sonido.py       efectos de sonido y musica (funciona aunque no haya placa de audio)
    entrada.py      teclado + mando de Xbox -> "acciones" (aceptar, dash, pausa...)
    ventana.py      ventana real y escalado del lienzo de 1066x600
    guardado.py     records.json y config.json
    dibujo.py       ayudas de dibujo: texto, marcos, efecto CRT...
    efectos.py      particulas, textos flotantes, temblor y destello
    fondo.py        estrellas, nebulosas y planetas con paralaje
    hud.py          marcador (puntos, vidas, dash, power-ups activos) y la llegada del jefe
    avisos.py       la cola de avisos de arriba (salen de a uno)
    carteles.py     como se ven los carteles: avisos, fichas, logro, momentos y rango

    nave.py         la nave del jugador
    moneda.py       la moneda
    proyectiles.py  balas del jefe
    enemigos/       un archivo por tipo de enemigo + la clase base
    jefes/          un archivo por jefe + la clase base
    powerups/       los power-ups + la clase base
    partida.py      todo el estado de UNA partida y sus reglas

    escenas/        una clase por pantalla (inicio, juego, pausa...)
    app.py          crea todo y corre el bucle principal
"""

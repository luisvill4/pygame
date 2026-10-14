"""
El estudio: un sintetizador y una consola de mezcla hechos con numpy, para componer toda
la musica y los efectos del juego con calidad de estudio (y sin samples).

    base.py          notas, acordes, curvas, decibeles
    sintesis.py      osciladores sin aliasing, envolventes, filtro analogico, Sinte, FM y Ruido
    bateria.py       bombo, caja, palmas, hi-hats, toms y platillos
    procesos.py      reverb, delay, chorus, saturacion, ecualizador, compresor, limitador, loudness
    instrumentos.py  los "presets": los sonidos ya armados (pads, bajos, leads, campanas...)
    obra.py          Obra: pistas, buses de efectos, mezcla, master y guardado
    obras/           las composiciones (cada una se registra con @obra)

El juego NO usa nada de esto: solo los archivos que esto escribe en efectos/.
Se usa con herramientas/componer.py (ver ahi).
"""

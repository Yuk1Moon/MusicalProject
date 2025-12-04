## Sonificación de Datos

Este proyecto explora cómo distintos tipos de datos pueden convertirse en música.  
A partir de una captura de tráfico de red (PCAP) y de los dígitos de números irracionales en archivos CSV, se generan varias pistas MIDI que luego se mezclan en un DAW (BandLab) para crear una pieza musical estilo lo-fi.

Canción: https://www.bandlab.com/track/76e02683-75ce-f011-8196-000d3a96100f?revId=74e02683-75ce-f011-8196-000d3a96100f

---

## Objetivo
Mostrar cómo datos que normalmente se usan de forma numérica (paquetes de red, dígitos de constantes matemáticas) pueden modelarse y representarse como música mediante:
- Lectura y procesamiento de archivos PCAP y CSV.
- Diseño de algoritmos.
- Mapeo de datos numéricos a parámetros musicales (altura, duración, intensidad).
- Uso de MIDI como puente entre código y producción musical.

---

## Estructura del proyecto
Scripts principales:

- `traffic2midi.py`  
  Genera un acompañamiento armónico en Do mayor a partir de un archivo PCAP:
  - Calcula un nivel de actividad por compás usando el tamaño de los paquetes.
  - Asigna acordes diatónicos (C, Am, F, G, Em, Dm) con transiciones suaves.
  - Crea dos tracks MIDI: pad de acordes y arpegios.

- `melodia_pi.py`  
  Genera una melodía en Do mayor a partir de los dígitos de π en un CSV:
  - Cada dígito decide el grado de la escala, la duración y la intensidad.
  - Usa una tabla de transiciones entre grados para mantener coherencia melódica.
  - Dura hasta 45 compases en 4/4.

- `bajo_e.py`  
  Genera una línea de bajo en Do mayor a partir de los dígitos de e:
  - El dígito controla el movimiento entre grados de la escala en registro grave.
  - Duraciones más largas para un bajo estable.
  - Cierra en la tónica.

- `drums_medium_plus.py`  
  Genera una pista de batería en 4/4 con 45 compases:
  - Kick en 1 y variaciones suaves en el resto del compás.
  - Snare en 2 y 4, con ghost notes ocasionales.
  - Hi-hat a corcheas o negras con pequeños adornos.
  - Usa el canal 10 GM para batería.

---

## Temas de uso
- Procesamiento de datos 
- Redes y tráfico 
  - Interpretación del tamaño de los paquetes como una medida de nivel de tráfico.
- Algoritmos generativos
  - Tablas de transición para acordes y grados de la escala.  
  - Reglas para evitar repeticiones excesivas (AAA, ABAB).  

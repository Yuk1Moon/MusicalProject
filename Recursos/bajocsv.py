#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Genera una línea de bajo en Do mayor a partir de dígitos de un archivo CSV.
# Usa cada dígito para decidir el grado de la escala, la duración y la intensidad de la nota.
# Produce hasta 45 compases en 4/4 en un solo track MIDI.

import csv
import os
import sys
from midiutil import MIDIFile

# Configuración de rutas
CSV_INPUT_PATH = "entrada_digitos_e.csv"
OUTPUT_DIR = "MIDI's"

# Configuración musical
BASE_TEMPO = 96
BEATS_PER_BAR = 4
TARGET_BARS = 45
MAX_BEATS = BEATS_PER_BAR * TARGET_BARS

# Escala de Do en registro grave
ESCALA_DO = [36, 38, 40, 41, 43, 45, 47]


# Duración de cada nota según el dígito
def duracion_para_digito(d):
    if d >= 7:
        return 2.0   # blanca
    else:
        return 1.0   # negra


# Velocidad (intensidad) según el dígito
def velocidad_para_digito(d):
    v = 50 + d * 3
    return max(45, min(85, v))


# Movimiento de grado en la escala según el dígito
def siguiente_grado(last_degree, d):
    move = (d % 5) - 2
    degree = last_degree + move
    degree = max(0, min(len(ESCALA_DO) - 1, degree))
    return degree


# Lee dígitos desde un archivo CSV
def leer_digitos_desde_csv(csv_path):
    secuencia_digitos = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        lector = csv.reader(f)
        for fila in lector:
            for celda in fila:
                for ch in str(celda).strip():
                    if ch.isdigit():
                        secuencia_digitos.append(ch)
    return secuencia_digitos


# Crea el archivo MIDI con la línea de bajo
def crear_midi_desde_digitos(digitos, midi_path, nombre_pista):
    midi = MIDIFile(numTracks=1)
    track = 0
    canal = 0
    tiempo_actual = 0.0

    midi.addTrackName(track, tiempo_actual, nombre_pista)
    midi.addTempo(track, tiempo_actual, BASE_TEMPO)

    last_degree = 0

    for ch in digitos:
        if tiempo_actual >= MAX_BEATS:
            break

        d = int(ch)
        degree = siguiente_grado(last_degree, d)
        pitch = ESCALA_DO[degree]
        dur = duracion_para_digito(d)
        vel = velocidad_para_digito(d)

        # Ajuste si la nota alcanza el final de los 45 compases
        if tiempo_actual + dur >= MAX_BEATS:
            dur = MAX_BEATS - tiempo_actual
            pitch = ESCALA_DO[0]  # cierra en la tónica
            if dur <= 0:
                break

        midi.addNote(
            track,
            canal,
            pitch,
            tiempo_actual,
            dur,
            vel
        )

        tiempo_actual += dur
        last_degree = degree

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(midi_path, "wb") as salida:
        midi.writeFile(salida)


def main():
    global CSV_INPUT_PATH

    if len(sys.argv) > 1:
        CSV_INPUT_PATH = sys.argv[1]

    name = os.path.splitext(os.path.basename(CSV_INPUT_PATH))[0]
    midi_output_path = os.path.join(OUTPUT_DIR, f"{name}_bajo.mid")

    print("Leyendo dígitos desde:", CSV_INPUT_PATH)
    digitos = leer_digitos_desde_csv(CSV_INPUT_PATH)
    print(f"Se leyeron {len(digitos)} dígitos.")

    if not digitos:
        print("No se encontraron dígitos en el CSV. No se generará el MIDI.")
        return

    print("Creando archivo MIDI en:", midi_output_path)
    crear_midi_desde_digitos(digitos, midi_output_path, name)
    print("Listo. Archivo MIDI generado.")


if __name__ == "__main__":
    main()

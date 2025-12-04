#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Genera una melodía en Do mayor a partir de dígitos de un archivo CSV.
# Usa reglas de transición entre grados de la escala para mantener coherencia melódica.
# Produce hasta 45 compases en 4/4 en un solo track MIDI.

import csv
import os
import sys
import random
from midiutil import MIDIFile

# Rutas
CSV_INPUT_PATH = "entrada_digitos_pi.csv"
OUTPUT_DIR = "MIDI's"

# Parámetros musicales
BASE_TEMPO = 96
BEATS_PER_BAR = 4
TARGET_BARS = 45
MAX_BEATS = BEATS_PER_BAR * TARGET_BARS

# Escala de Do en registro medio
ESCALA_DO = [60, 62, 64, 65, 67, 69, 71]
SCALE_DEGREES = list(range(len(ESCALA_DO)))

# Transiciones suaves entre grados de la escala
DEGREE_TRANSITIONS = {
    0: [2, 4, 1, 3],
    1: [3, 4, 0, 2],
    2: [4, 0, 3, 5],
    3: [0, 4, 2, 5],
    4: [0, 2, 5, 3, 6],
    5: [3, 4, 2, 6],
    6: [4, 5, 2],
}


# Normaliza el dígito a un valor entre 0 y 1
def actividad_desde_digito(d):
    return d / 9.0 if d <= 9 else 1.0


# Duración de la nota según el dígito
def duracion_para_digito(d):
    if d <= 4:
        return 0.5   # corchea
    else:
        return 1.0   # negra


# Velocidad (intensidad) según el dígito
def velocidad_para_digito(d):
    v = 60 + d * 5
    return max(50, min(110, v))


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


# Genera una secuencia de grados de la escala a partir de los dígitos
def generar_secuencia_grados(digitos):
    grados = []

    for i, ch in enumerate(digitos):
        d = int(ch)
        a = actividad_desde_digito(d)

        if i == 0:
            current = 0
        else:
            prev = grados[-1]

            idx = int(a * len(SCALE_DEGREES))
            idx = min(len(SCALE_DEGREES) - 1, idx)

            allowed = DEGREE_TRANSITIONS.get(prev, SCALE_DEGREES)

            candidates_sorted = sorted(
                allowed,
                key=lambda deg: abs(deg - idx)
            )

            candidate = candidates_sorted[0]

            # A veces usamos el segundo candidato para variar
            if len(candidates_sorted) > 1 and random.random() < 0.35:
                candidate = candidates_sorted[1]

            # Evitar tres notas seguidas en el mismo grado
            if len(grados) >= 2 and candidate == grados[-1] == grados[-2]:
                for alt in candidates_sorted:
                    if alt != candidate:
                        candidate = alt
                        break

            # Evitar patrón ABAB prolongado
            if len(grados) >= 3 and grados[-3] == grados[-1] and candidate == grados[-2]:
                for alt in candidates_sorted:
                    if alt not in (grados[-1], grados[-2]):
                        candidate = alt
                        break

            current = candidate

        grados.append(current)

    return grados


# Crea el archivo MIDI con la melodía
def crear_midi_desde_digitos(digitos, midi_path, nombre_pista):
    midi = MIDIFile(numTracks=1)
    track = 0
    canal = 0
    tiempo_actual = 0.0

    midi.addTrackName(track, tiempo_actual, nombre_pista)
    midi.addTempo(track, tiempo_actual, BASE_TEMPO)

    grados = generar_secuencia_grados(digitos)

    for ch, grado in zip(digitos, grados):
        if tiempo_actual >= MAX_BEATS:
            break

        d = int(ch)

        # Dígito 0 se usa como silencio
        if d == 0:
            dur_sil = duracion_para_digito(d)
            if tiempo_actual + dur_sil > MAX_BEATS:
                dur_sil = MAX_BEATS - tiempo_actual
            tiempo_actual += dur_sil
            continue

        pitch = ESCALA_DO[grado]
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

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(midi_path, "wb") as salida:
        midi.writeFile(salida)


def main():
    global CSV_INPUT_PATH

    if len(sys.argv) > 1:
        CSV_INPUT_PATH = sys.argv[1]

    name = os.path.splitext(os.path.basename(CSV_INPUT_PATH))[0]
    midi_output_path = os.path.join(OUTPUT_DIR, f"{name}_melodia.mid")

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

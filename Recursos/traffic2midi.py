#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Genera un acompañamiento en Do mayor a partir de un archivo PCAP/PCAPNG.
# Usa la cantidad de bytes por bloque de paquetes como nivel de actividad
# para elegir acordes y patrones rítmicos.
# Produce 45 compases en 4/4 con:
# - Track 0: Soft Pad
# - Track 1: Arpegios de piano

from midiutil import MIDIFile
from scapy.all import rdpcap
import os
import random

# Configuración de archivos y parámetros generales
PCAP_INPUT_PATH = r"traffic1.pcapng"
MIDI_OUTPUT_PATH = r".\MIDI's\acompanamiento.mid"

TEMPO_BPM = 96
BEATS_PER_BAR = 4
TARGET_BARS = 45
TOTAL_BEATS = BEATS_PER_BAR * TARGET_BARS

# Instrumentos (GM Program numbers)
PAD_PROGRAM = 89         # Soft Pad
ARPEGGIO_PROGRAM = 0     # Piano

# Acordes en Do
CHORDS = {
    "C":  [48, 52, 55, 60],
    "Am": [57, 60, 64, 69],
    "F":  [53, 57, 60, 65],
    "G":  [55, 59, 62, 67],
    "Dm": [50, 53, 57, 62],
    "Em": [52, 55, 59, 64],
}

# Orden de acordes en Do
CHORD_ORDER = ["C", "Am", "F", "G", "Em", "Dm"]

# Transiciones suaves entre acordes
CHORD_TRANSITIONS = {
    "C":  ["Am", "F", "G", "Em"],
    "Am": ["F", "Dm", "C", "Em"],
    "F":  ["C", "Dm", "G"],
    "G":  ["C", "Em", "Am"],
    "Em": ["C", "G", "Am"],
    "Dm": ["G", "F", "Em"],
}

# Patrones rítmicos en 4/4 (las duraciones suman 4 beats)
RHYTHM_PATTERNS = [
    [1, 1, 1, 1],
    [2, 1, 1],
    [1, 0.5, 0.5, 1, 1],
    [0.5, 0.5, 1, 0.5, 0.5, 1],
    [1.5, 0.5, 2],
]


# Lee longitudes de los paquetes del archivo PCAP/PCAPNG
def read_packet_lengths(pcap_path):
    packets = rdpcap(pcap_path)
    lengths = [len(p) for p in packets]
    return lengths


# Calcula un nivel de actividad por compás a partir de las longitudes
def compute_bar_activities(lengths, n_bars=TARGET_BARS):
    if not lengths:
        return [0.0] * n_bars

    bar_size = max(1, len(lengths) // n_bars)

    bar_sums = []
    for i in range(n_bars):
        start = i * bar_size
        end = min(len(lengths), (i + 1) * bar_size)
        chunk = lengths[start:end] or [0]
        bar_sums.append(sum(chunk))

    max_sum = max(bar_sums) or 1
    activities = [s / max_sum for s in bar_sums]
    return activities


# Genera una secuencia de acordes a partir de la actividad
def choose_chord_sequence(activities):
    chords = []

    for i, a in enumerate(activities):
        if i == 0:
            current = "C"  # siempre empieza en I
        else:
            prev = chords[-1]

            idx = int(a * len(CHORD_ORDER))
            idx = min(len(CHORD_ORDER) - 1, idx)

            allowed = CHORD_TRANSITIONS.get(prev, CHORD_ORDER)

            candidates_sorted = sorted(
                allowed,
                key=lambda name: abs(CHORD_ORDER.index(name) - idx)
            )

            candidate = candidates_sorted[0]

            # A veces usamos el segundo más cercano para variar
            if len(candidates_sorted) > 1 and random.random() < 0.35:
                candidate = candidates_sorted[1]

            # Evitar 3 compases seguidos con el mismo acorde
            if len(chords) >= 2 and candidate == chords[-1] == chords[-2]:
                for alt in candidates_sorted:
                    if alt != candidate:
                        candidate = alt
                        break

            # Evitar patrón ABAB prolongado
            if len(chords) >= 3 and chords[-3] == chords[-1] and candidate == chords[-2]:
                for alt in candidates_sorted:
                    if alt not in (chords[-1], chords[-2]):
                        candidate = alt
                        break

            current = candidate

        chords.append(current)

    # Forzar C en compases internos y al final
    if chords:
        for i in range(8, len(chords) - 1, 8):
            chords[i] = "C"
        chords[-1] = "C"

    return chords


# Elige un patrón rítmico según el nivel de actividad
def choose_rhythm_pattern(activity):
    idx = int(activity * len(RHYTHM_PATTERNS))
    idx = min(len(RHYTHM_PATTERNS) - 1, idx)
    return RHYTHM_PATTERNS[idx]


# Crea el archivo MIDI con pad y arpegios a partir del PCAP
def create_midi_from_pcap(pcap_path, midi_path):
    lengths = read_packet_lengths(pcap_path)
    activities = compute_bar_activities(lengths, n_bars=TARGET_BARS)
    chord_sequence = choose_chord_sequence(activities)

    midi = MIDIFile(numTracks=2)

    midi.addTempo(0, 0, TEMPO_BPM)
    midi.addTempo(1, 0, TEMPO_BPM)

    midi.addProgramChange(0, 0, 0, PAD_PROGRAM)
    midi.addProgramChange(1, 1, 0, ARPEGGIO_PROGRAM)

    # Track 0: pad de acordes
    current_time = 0.0
    for chord_name in chord_sequence:
        notes = CHORDS[chord_name]
        pad_notes = notes[:3]
        for pitch in pad_notes:
            midi.addNote(
                track=0,
                channel=0,
                pitch=pitch,
                time=current_time,
                duration=BEATS_PER_BAR,
                volume=70
            )
        current_time += BEATS_PER_BAR

    # Track 1: arpegios de piano
    current_time = 0.0
    for chord_name, activity in zip(chord_sequence, activities):
        notes = CHORDS[chord_name]
        pattern = choose_rhythm_pattern(activity)

        t = 0.0
        for i, dur in enumerate(pattern):
            pitch = notes[i % len(notes)]

            if activity > 0.75 and i % 2 == 0:
                pitch += 12

            midi.addNote(
                track=1,
                channel=1,
                pitch=pitch,
                time=current_time + t,
                duration=dur,
                volume=80
            )
            t += dur

        current_time += BEATS_PER_BAR

    with open(midi_path, "wb") as f:
        midi.writeFile(f)


if __name__ == "__main__":
    if not os.path.exists(PCAP_INPUT_PATH):
        print(f"No se encontró el archivo: {PCAP_INPUT_PATH}")
    else:
        create_midi_from_pcap(PCAP_INPUT_PATH, MIDI_OUTPUT_PATH)
        print(f"Archivo MIDI generado en: {MIDI_OUTPUT_PATH}")

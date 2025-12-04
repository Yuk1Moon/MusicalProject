#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Genera una pista de batería en 4/4 con 45 compases.
# Usa un groove tranquilo con variaciones en kick, snare y hi-hats.
# Produce un archivo MIDI con un solo track de batería (canal 10 GM).

import os
from midiutil import MIDIFile

# Configuración musical
TEMPO_BPM = 120
BEATS_PER_BAR = 4
TARGET_BARS = 45
OUTPUT_DIR = "MIDI's"
MIDI_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "drums.mid")

# Track y canal de batería (GM: canal 10 -> 9 en 0-based)
DRUM_TRACK = 0
DRUM_CHANNEL = 9

# Notas GM de batería
KICK = 36
SNARE = 38
CH_HAT = 42
OP_HAT = 46
CRASH = 49


# Golpes de bombo
def add_kick(midi, time, dur=0.25, vel=95):
    midi.addNote(DRUM_TRACK, DRUM_CHANNEL, KICK, time, dur, vel)


def add_kick_ghost(midi, time, dur=0.2, vel=70):
    midi.addNote(DRUM_TRACK, DRUM_CHANNEL, KICK, time, dur, vel)


# Golpes de tarola
def add_snare(midi, time, dur=0.25, vel=90):
    midi.addNote(DRUM_TRACK, DRUM_CHANNEL, SNARE, time, dur, vel)


def add_snare_ghost(midi, time, dur=0.18, vel=65):
    midi.addNote(DRUM_TRACK, DRUM_CHANNEL, SNARE, time, dur, vel)


# Hi-hats
def add_hat_closed(midi, time, dur=0.16, vel=72):
    midi.addNote(DRUM_TRACK, DRUM_CHANNEL, CH_HAT, time, dur, vel)


def add_hat_closed_soft(midi, time, dur=0.14, vel=60):
    midi.addNote(DRUM_TRACK, DRUM_CHANNEL, CH_HAT, time, dur, vel)


def add_hat_open(midi, time, dur=0.32, vel=80):
    midi.addNote(DRUM_TRACK, DRUM_CHANNEL, OP_HAT, time, dur, vel)


# Crash
def add_crash(midi, time, dur=0.9, vel=92):
    midi.addNote(DRUM_TRACK, DRUM_CHANNEL, CRASH, time, dur, vel)


# Agrega un compás de groove según el índice de compás
def add_groove_bar(midi, bar_index):
    base_time = bar_index * BEATS_PER_BAR
    bar_type_a = (bar_index % 4 in (0, 2))

    # Kick principal
    add_kick(midi, base_time + 0.0, vel=96)

    if bar_type_a:
        add_kick(midi, base_time + 2.0, vel=92)
        add_kick_ghost(midi, base_time + 1.5, vel=68)
    else:
        if bar_index % 3 != 1:
            add_kick(midi, base_time + 2.0, vel=90)

    # Snares en 2 y 4
    add_snare(midi, base_time + 1.0, vel=88)
    add_snare(midi, base_time + 3.0, vel=90)

    # Ghost notes de snare
    if bar_type_a:
        add_snare_ghost(midi, base_time + 0.75, vel=62)
    else:
        add_snare_ghost(midi, base_time + 2.75, vel=62)

    # Hi-hats
    if bar_type_a:
        # Hi-hat a corcheas
        for step in range(8):
            t = base_time + step * 0.5
            if step % 2 == 0:
                add_hat_closed(midi, t, vel=72)
            else:
                add_hat_closed_soft(midi, t, vel=62)
    else:
        # Hi-hat a negras
        for beat in range(4):
            t = base_time + beat
            vel = 70 if beat in (0, 2) else 66
            add_hat_closed(midi, t, vel=vel)
        if bar_index % 6 in (1, 5):
            add_hat_closed_soft(midi, base_time + 1.5, vel=60)

    # Crash de entrada
    if bar_index == 0:
        add_crash(midi, base_time + 0.0, dur=1.0, vel=90)

    # Open hat suave cada 16 compases
    if bar_index % 16 == 15:
        add_hat_open(midi, base_time + 3.5, dur=0.32, vel=78)

    # Pequeño cierre en el último compás
    if bar_index == TARGET_BARS - 1:
        add_hat_closed(midi, base_time + 3.0, vel=75)
        add_hat_closed(midi, base_time + 3.5, vel=75)
        add_snare(midi, base_time + 3.0, vel=94)


# Crea el archivo MIDI con la pista de batería
def create_drum_midi(path):
    midi = MIDIFile(
        numTracks=1,
        deinterleave=False,
        removeDuplicates=False
    )
    midi.addTempo(DRUM_TRACK, 0, TEMPO_BPM)

    for bar in range(TARGET_BARS):
        add_groove_bar(midi, bar)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(path, "wb") as f:
        midi.writeFile(f)


if __name__ == "__main__":
    create_drum_midi(MIDI_OUTPUT_PATH)
    print(f"Drums generados en: {MIDI_OUTPUT_PATH}")

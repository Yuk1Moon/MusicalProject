#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Genera un archivo CSV con dígitos de un número irracional (pi, e, phi, etc.).
# Permite elegir la constante, el número de decimales y el nombre del archivo de salida.

import csv
import os
from mpmath import mp

# Carpeta donde se guardarán los CSV
OUTPUT_DIR = "CSV"


# Regresa el número irracional correspondiente a la opción elegida
def elegir_irracional(opcion: str):
    if opcion == "1":
        return mp.pi, "pi"
    elif opcion == "2":
        return mp.e, "e"
    elif opcion == "3":
        return (1 + mp.sqrt(5)) / 2, "phi"
    elif opcion == "4":
        return mp.sqrt(2), "sqrt2"
    elif opcion == "5":
        return mp.sqrt(3), "sqrt3"
    elif opcion == "6":
        return mp.log(2), "ln2"
    else:
        return None, None


# Pide datos al usuario y genera el CSV con los dígitos
def irracional_a_csv():
    print("=== Generador de CSV de dígitos de un número irracional ===\n")
    print("Elige el número irracional:")
    print("  1) π (pi)")
    print("  2) e")
    print("  3) φ (phi, número áureo)")
    print("  4) √2")
    print("  5) √3")
    print("  6) ln(2)")
    
    opcion = input("\nOpción (1-6): ").strip()
    valor, nombre_constante = elegir_irracional(opcion)

    if valor is None:
        print("Opción no válida")
        return

    try:
        n_decimales = int(input("¿Cuántos dígitos decimales quieres?: ").strip())
        if n_decimales <= 0:
            print("El número de dígitos debe ser positivo.")
            return
    except ValueError:
        print("No entendí el número de dígitos")
        return

    mp.dps = n_decimales + 5
    valor = +valor

    s = str(valor)

    if "." in s:
        parte_entera, parte_decimal = s.split(".")
    else:
        parte_entera, parte_decimal = s, ""

    parte_decimal = parte_decimal[:n_decimales]
    todos_los_digitos = parte_entera + parte_decimal

    print(f"\nValor aproximado: {s}")
    print(f"Parte entera: {parte_entera}")
    print(f"Primeros {n_decimales} decimales: {parte_decimal}")
    print(f"Total de dígitos que se guardarán en CSV: {len(todos_los_digitos)}")

    nombre_archivo = input(
        f"Nombre del archivo CSV de salida (por defecto: digitos_{nombre_constante}.csv): "
    ).strip()
    if not nombre_archivo:
        nombre_archivo = f"digitos_{nombre_constante}.csv"
    if not nombre_archivo.endswith(".csv"):
        nombre_archivo += ".csv"

    # Asegurar carpeta y construir ruta completa
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ruta_salida = os.path.join(OUTPUT_DIR, nombre_archivo)

    with open(ruta_salida, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for d in todos_los_digitos:
            writer.writerow([d])

    print(f"\nListo. Se guardaron {len(todos_los_digitos)} dígitos en '{ruta_salida}'.")


if __name__ == "__main__":
    irracional_a_csv()

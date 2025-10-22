#! /usr/bin/env python3

"""
gen-2.py
Usar: ./gen-2.py fichero-entrada fichero-salida
Genera un .dat compatible con el .mod del enunciado, ejecuta glpsol y muestra la solución.
"""

import sys
import os
import subprocess
import re
from math import comb

def parse_input_file(input_file: str):
    with open(input_file, 'r') as f:
        lineas = [l.strip() for l in f if l.strip() != ""]

    if len(lineas) < 3:
        raise ValueError("Formato de entrada inválido: se esperan al menos 3 líneas con n, m, u")

    n = int(lineas[0])      # Nº FRANJAS
    m = int(lineas[1])      # Nº BUSES
    u = int(lineas[2])      # Nº TALLERES

    # comprobar que hay suficientes líneas para c (m filas) y o (n filas)
    expected_lines = 3 + m + n
    if len(lineas) < expected_lines:
        raise ValueError(f"Faltan líneas en el fichero de entrada. Se esperaban {expected_lines} líneas no vacías")

    # matriz c de tamaño m x m
    c = []
    idx = 3
    for _ in range(m):
        fila = list(map(int, lineas[idx].split()))
        if len(fila) != m:
            raise ValueError(f"Cada fila de la matriz c debe tener {m} elementos (fila {idx-2})")
        c.append(fila)
        idx += 1

    # matriz o de tamaño n x u (n franjas, u talleres)
    o = []
    for _ in range(n):
        fila = list(map(int, lineas[idx].split()))
        if len(fila) != u:
            raise ValueError(f"Cada fila de la matriz o debe tener {u} elementos (fila {idx-2-m})")
        o.append(fila)
        idx += 1

    return n, m, u, c, o

def generar_dat(output_file, datos):
    n, m, u, c, o = datos

    # nombres de sets: buses a1..am, franjas s1..sn, talleres t1..tu
    buses = [f"a{i+1}" for i in range(m)]
    franjas = [f"s{i+1}" for i in range(n)]
    talleres = [f"t{i+1}" for i in range(u)]

    with open(output_file, "w") as f:
        f.write("data;\n\n")

        f.write("set BUSES := " + " ".join(buses) + ";\n")
        f.write("set FRANJAS := " + " ".join(franjas) + ";\n")
        f.write("set TALLERES := " + " ".join(talleres) + ";\n\n")

        # matriz de pasajeros c[i,l] (indexada por BUSES x BUSES)
        f.write("param c : " + " ".join(buses) + " :=\n")
        for i in range(m):
            fila = " ".join(str(c[i][j]) for j in range(m))
            f.write(f"{buses[i]} {fila}\n")
        f.write(";\n\n")

        # matriz de disponibilidad o[j,k] (FRANJAS x TALLERES). Cada fila es una franja sX y columnas talleres tY
        f.write("param o : " + " ".join(talleres) + " :=\n")
        for j in range(n):
            fila = " ".join(str(o[j][k]) for k in range(u))
            f.write(f"{franjas[j]} {fila}\n")
        f.write(";\n\n")

        f.write("end;\n")

def ejecutar_glpk(mod_file, dat_file, output_txt="glpk_output.txt"):
    # llamada a glpsol (se espera que glpsol esté en PATH)
    cmd = ["glpsol", "--model", mod_file, "--data", dat_file, "--output", output_txt]
    try:
        completed = subprocess.run(cmd, text=True, capture_output=True)
    except FileNotFoundError:
        raise FileNotFoundError("glpsol no encontrado. Instala GLPK y asegúrate de que 'glpsol' esté en el PATH.")
    # devolvemos stdout/stderr y el fichero de salida si fue creado
    stdout = completed.stdout
    stderr = completed.stderr
    if not os.path.exists(output_txt):
        # si glpsol falló de forma que no creó el fichero, devolvemos stdout/stderr para diagnóstico
        raise RuntimeError(f"glpsol no produjo el fichero de salida '{output_txt}'. stdout+stderr:\n{stdout}\n{stderr}")
    with open(output_txt, "r") as f:
        contenido = f.read()
    return contenido

def extraer_objetivo(glpk_text: str):
    # Buscar línea con "Objective:  Z = <valor>" (varias versiones posibles)
    m = re.search(r"Objective[:\s]+(?:Z\s*=\s*)?([+-]?\d+(\.\d+)?([eE][+-]?\d+)?)", glpk_text)
    if m:
        try:
            return float(m.group(1))
        except:
            return None
    # alternativa: buscar "Objective:  Z =  123.000 (MINimum)"
    m2 = re.search(r"Objective:\s*\w*\s*=\s*([+-]?\d+(\.\d+)?([eE][+-]?\d+)?)", glpk_text)
    if m2:
        return float(m2.group(1))
    # si no se encuentra, intentar buscar "Objective:  value" en español u otros formatos
    return None

def extraer_variables_solucion(glpk_text: str):
    """
    Extrae valores de variables x[...] e y[...] del texto de salida de glpsol.
    Devuelve diccionarios: x_vals[(bus,franja,taller)] = valor, y_vals[(bus_i,bus_l,franja)] = valor
    """
    x_vals = {}
    y_vals = {}

    # patrón que capture variables en formas como:
    # x[a1,s1,t1] 1
    # y[a1,a2,s1] * 1
    var_pattern = re.compile(r'^\s*([xy])\[([^\]]+)\]\s+([+-]?\d+(\.\d+)?([eE][+-]?\d+)?)', re.MULTILINE)
    for m in var_pattern.finditer(glpk_text):
        var = m.group(1)
        inside = m.group(2)
        val = float(m.group(3))
        parts = [p.strip() for p in inside.split(',')]
        if var == 'x' and len(parts) == 3:
            x_vals[(parts[0], parts[1], parts[2])] = val
        elif var == 'y' and len(parts) == 3:
            # y is indexed by two buses and a franja
            y_vals[(parts[0], parts[1], parts[2])] = val
    # also try alternative output style line like: x[a1,s1,t1] * 1.000000e+00
    alt_pattern = re.compile(r'^\s*([xy])\[([^\]]+)\]\s+\*\s*([+-]?\d+(\.\d+)?([eE][+-]?\d+)?)', re.MULTILINE)
    for m in alt_pattern.finditer(glpk_text):
        var = m.group(1)
        inside = m.group(2)
        val = float(m.group(3))
        parts = [p.strip() for p in inside.split(',')]
        if var == 'x' and len(parts) == 3:
            x_vals[(parts[0], parts[1], parts[2])] = val
        elif var == 'y' and len(parts) == 3:
            y_vals[(parts[0], parts[1], parts[2])] = val

    return x_vals, y_vals

def imprimir_solucion_legible(x_vals):
    """
    Dado x_vals con claves (bus,franja,taller)->valor, imprimimos líneas legibles por cada bus asignado (valor ~=1).
    """
    asignaciones = {}
    for (bus, franja, taller), val in x_vals.items():
        # considerar asignado si valor suficientemente cercano a 1
        if abs(val - 1.0) < 1e-6:
            asignaciones.setdefault(bus, []).append((franja, taller))
    # Para cada bus, debe tener exactamente una asignación (según restricción), pero imprimimos todas por si acaso
    lines = []
    for bus in sorted(asignaciones.keys()):
        for franja, taller in asignaciones[bus]:
            lines.append(f"Bus {bus} -> franja {franja}, taller {taller}")
    return lines

def contar_variables_restricciones(n, m, u):
    # Variables:
    # x: m * n * u
    # y: m * m * n   (porque en el .mod definiste var y {BUSES, BUSES, FRANJAS})
    num_x = m * n * u
    num_y = m * m * n
    total_vars = num_x + num_y

    # Restricciones:
    # AsignacionBuses: m
    # FranjasDisponibles: m * n * u
    # Capacidad: n * u
    # YBusIFranjaJ: C(m,2) * n
    # YBusLFranjaJ: C(m,2) * n
    # MismaFranja: C(m,2) * n
    pairs = comb(m, 2) if m >= 2 else 0
    total_constraints = (
        m +
        (m * n * u) +
        (n * u) +
        3 * (pairs * n)
    )
    return total_vars, total_constraints

def main():
    if len(sys.argv) != 3:
        print("Error: número de argumentos incorrecto\nUso: ./gen-2.py fichero-entrada fichero-salida")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dat = sys.argv[2]

    if not os.path.exists(input_file):
        print("Error: el archivo de entrada no existe:", input_file)
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    mod_file = os.path.join(script_dir, "parte-2-2.mod")  # Cambia si tu .mod tiene otro nombre
    if not os.path.exists(mod_file):
        print(f"Error: no se encuentra el fichero .mod en la carpeta del script: {mod_file}")
        sys.exit(1)

    try:
        datos = parse_input_file(input_file)
    except Exception as e:
        print("Error al parsear el fichero de entrada:", e)
        sys.exit(1)

    try:
        generar_dat(output_dat, datos)
    except Exception as e:
        print("Error al generar el fichero .dat:", e)
        sys.exit(1)

    # ejecutar glpk
    try:
        glpk_out = ejecutar_glpk(mod_file, output_dat, output_txt="glpk_output.txt")
    except Exception as e:
        print("Error ejecutando glpsol:", e)
        sys.exit(1)

    # obtener datos
    objetivo = extraer_objetivo(glpk_out)
    x_vals, y_vals = extraer_variables_solucion(glpk_out)

    n, m, u, _, _ = datos
    total_vars, total_constraints = contar_variables_restricciones(n, m, u)

    # Primera línea: valor óptimo, num variables y num restricciones
    if objetivo is None:
        print("No se encontró un valor objetivo en la salida de GLPK. Salida completa:\n")
        print(glpk_out)
        sys.exit(1)

    # Imprimir como indica el enunciado
    print(f"Valor óptimo: {objetivo}")
    print(f"Número de variables de decisión: {total_vars}")
    print(f"Número de restricciones: {total_constraints}")

    # Imprimir asignaciones legibles
    lines = imprimir_solucion_legible(x_vals)
    if not lines:
        # si no hay x con valor 1, mostrarmos advertencia y salida completa para depuración
        print("\nNo se encontraron asignaciones x[i,j,k] = 1 en la solución (o la salida tuvo otro formato).")
        # opcionalmente mostrar la salida completa de glpsol para depuración
        print("\n--- salida completa de GLPK ---\n")
        print(glpk_out)
        sys.exit(0)

    print("\nAsignaciones (autobús -> franja, taller):")
    for L in lines:
        print(L)

if __name__ == "__main__":
    main()
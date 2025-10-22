"""
gen-2.py
Uso: py gen-2.py fichero-entrada fichero-salida
Genera un .dat compatible con el .mod del enunciado, ejecuta GLPK y muestra la solución.
"""

import sys
import os
import subprocess
import re
from math import comb

# --- Funciones para leer el fichero de entrada ---
def leer_entrada(fichero):
    """Lee el fichero de entrada y devuelve n,m,u, c y o"""
    with open(fichero, 'r') as f:
        lineas = [l.strip() for l in f if l.strip()]
    if len(lineas) < 3:
        raise ValueError("Fichero demasiado corto")
    n = int(lineas[0])
    m = int(lineas[1])
    u = int(lineas[2])
    if len(lineas) < 3 + m + n:
        raise ValueError("Faltan líneas en el fichero")
    # matriz c
    c = [list(map(int, lineas[3+i].split())) for i in range(m)]
    # matriz o
    o = [list(map(int, lineas[3+m+i].split())) for i in range(n)]
    return n,m,u,c,o

# --- Generar fichero .dat para AMPL/GLPK ---
def generar_dat(fichero_dat, n,m,u,c,o):
    buses = [f"a{i+1}" for i in range(m)]
    franjas = [f"s{i+1}" for i in range(n)]
    talleres = [f"t{i+1}" for i in range(u)]
    with open(fichero_dat, "w") as f:
        f.write("data;\n\n")
        f.write("set BUSES := " + " ".join(buses) + ";\n")
        f.write("set FRANJAS := " + " ".join(franjas) + ";\n")
        f.write("set TALLERES := " + " ".join(talleres) + ";\n\n")
        # c[i,l]
        f.write("param c : " + " ".join(buses) + " :=\n")
        for i in range(m):
            f.write(buses[i] + " " + " ".join(str(c[i][j]) for j in range(m)) + "\n")
        f.write(";\n\n")
        # o[j,k]
        f.write("param o : " + " ".join(talleres) + " :=\n")
        for j in range(n):
            f.write(franjas[j] + " " + " ".join(str(o[j][k]) for k in range(u)) + "\n")
        f.write(";\n\nend;\n")

# --- Ejecutar GLPK ---
def ejecutar_glpk(mod_file, dat_file):
    """Ejecuta glpsol y devuelve el contenido de la salida"""
    try:
        subprocess.run(["glpsol", "--model", mod_file, "--data", dat_file, "--output", "glpk_out.txt"], check=True)
    except FileNotFoundError:
        print("Error: glpsol no encontrado. Instala GLPK y ponlo en el PATH.")
        sys.exit(1)
    with open("glpk_out.txt", "r") as f:
        return f.read()

# --- Extraer objetivo ---
def extraer_objetivo(texto):
    m = re.search(r"Objective.*=\s*([0-9\.Ee+-]+)", texto)
    return float(m.group(1)) if m else None

# --- Extraer variables x[i,j,k] ---
def extraer_x(texto):
    x_vals = {}
    patron = re.compile(r'x\[(.*?)\]\s+\*?\s*([01])')
    for match in patron.finditer(texto):
        partes = match.group(1).split(",")
        x_vals[(partes[0], partes[1], partes[2])] = int(match.group(2))
    return x_vals

# --- Imprimir asignaciones ---
def imprimir_asignaciones(x_vals):
    asignaciones = {}
    for (bus, franja, taller), val in x_vals.items():
        if val == 1:
            asignaciones[bus] = (franja, taller)
    print("\nAsignaciones (autobús -> franja, taller):")
    for bus in sorted(asignaciones.keys()):
        franja,taller = asignaciones[bus]
        print(f"Bus {bus} -> franja {franja}, taller {taller}")

# --- Contar variables y restricciones ---
def contar_vars_restricciones(n,m,u):
    num_x = m*n*u
    num_y = m*m*n
    total_vars = num_x + num_y
    pairs = comb(m,2) if m>=2 else 0
    total_constraints = m + m*n*u + n*u + 3*pairs*n
    return total_vars, total_constraints

# --- Función principal ---
def main():
    if len(sys.argv)!=3:
        print("Uso: py gen-2.py fichero-entrada fichero-salida")
        sys.exit(1)
    input_file = sys.argv[1]
    output_dat = sys.argv[2]
    if not os.path.exists(input_file):
        print("Error: fichero de entrada no existe:", input_file)
        sys.exit(1)
    mod_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parte-2-2.mod")
    if not os.path.exists(mod_file):
        print("Error: fichero .mod no encontrado:", mod_file)
        sys.exit(1)
    try:
        n,m,u,c,o = leer_entrada(input_file)
        generar_dat(output_dat, n,m,u,c,o)
        salida = ejecutar_glpk(mod_file, output_dat)
        objetivo = extraer_objetivo(salida)
        x_vals = extraer_x(salida)
        total_vars, total_constraints = contar_vars_restricciones(n,m,u)
        print(f"Valor óptimo: {objetivo}")
        print(f"Número de variables de decisión: {total_vars}")
        print(f"Número de restricciones: {total_constraints}")
        imprimir_asignaciones(x_vals)
    except Exception as e:
        print("Error:", e)
        sys.exit(1)

if __name__=="__main__":
    main()
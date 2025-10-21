#!/usr/bin/env python3
import sys
import os
import subprocess

def parse_input_file(input_file: str):
    with open(input_file, 'r') as f:
        lineas = [l.strip() for l in f.readlines()]

    n = int(lineas[0])      # Nº FRANJAS
    m = int(lineas[1])      # Nº BUSES
    u = int(lineas[2])      # Nº TALLERES

    # matriz c de tamaño m x m
    c = []
    idx = 3
    for _ in range(m):
        fila = list(map(int, lineas[idx].split()))
        c.append(fila)
        idx += 1

    # matriz o de tamaño n x u
    o = []
    for _ in range(n):
        fila = list(map(int, lineas[idx].split()))
        o.append(fila)
        idx += 1

    return n, m, u, c, o

def generar_dat(output_file, datos):
    n, m, u, c, o = datos

    with open(output_file, "w") as f:
        f.write("data;\n\n")

        f.write("set BUSES := " + " ".join([f"a{i+1}" for i in range(m)]) + ";\n")
        f.write("set FRANJAS := " + " ".join([f"s{i+1}" for i in range(n)]) + ";\n")
        f.write("set TALLERES := " + " ".join([f"t{i+1}" for i in range(u)]) + ";\n\n")

        # matriz de pasajeros c[i,l]
        f.write("param c : " + " ".join([f"a{i+1}" for i in range(m)]) + " :=\n")
        for i in range(m):
            fila = " ".join(str(c[i][j]) for j in range(m))
            f.write(f"a{i+1} {fila}\n")
        f.write(";\n\n")

        # matriz de disponibilidad o[j,k]
        f.write("param o : " + " ".join([f"t{i+1}" for i in range(u)]) + " :=\n")
        for j in range(n):
            fila = " ".join(str(o[j][k]) for k in range(u))
            f.write(f"s{j+1} {fila}\n")
        f.write(";\n\n")

        f.write("end;\n")

def ejecutar_glpk(mod_file, dat_file):
    subprocess.run(
        ["glpsol", "--model", mod_file, "--data", dat_file, "--output", "output.txt"],
        text=True
    )
    with open("output.txt", "r") as f:
        return f.read()

def main():
    if len(sys.argv) != 3:
        print("Error: número de argumentos incorrecto")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dat = sys.argv[2]

    if not os.path.exists(input_file):
        print("Error: el archivo de entrada no existe")
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    mod_file = os.path.join(script_dir, "modelo1.mod")  # <-- cambia al nombre de tu archivo mod

    datos = parse_input_file(input_file)
    generar_dat(output_dat, datos)

    salida = ejecutar_glpk(mod_file, output_dat)
    print(salida)

if __name__ == "__main__":
    main()
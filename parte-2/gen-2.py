#!env python3

"""
gen-2.py
Uso: py gen-2.py fichero-entrada fichero-salida
Genera un .dat compatible con el .mod del enunciado, ejecuta GLPK y muestra la solución.
"""

import sys
import os
import subprocess
import re

def parse_input_file(input_file: str) -> tuple:
    """Función que recibe el fichero de entrada y lo procesa. 
    Devuelve una tupla con los datos: (n, m, u, c, o)
    
    Formato del fichero de entrada:
    <n> <m> <u>
    <c11 c12 ... c1m>
    ...
    <cm1 cm2 ... cmm>
    <o11 o12 ... o1u>
    ...
    <on1 on2 ... onu>
    """
    with open(input_file, "r") as file:
        archivo_en_lineas = file.readlines()

    # Quitamos saltos de línea y líneas vacías
    archivo_en_lineas = [linea.strip() for linea in archivo_en_lineas if linea.strip() != ""]

    # --- Cabecera ---
    linea_cabecera = archivo_en_lineas[0]

    n = int(linea_cabecera.split()[0])  # número de franjas
    m = int(linea_cabecera.split()[1])  # número de autobuses
    u = int(linea_cabecera.split()[2])  # número de talleres

    # --- Matriz c ---
    # Las siguientes m líneas corresponden a la matriz de pasajeros c[i][j]
    c = []
    for i in range(1, 1 + m):
        fila = list(map(float, archivo_en_lineas[i].split()))
        if len(fila) != m:
            raise ValueError(f"Línea {i+1} de la matriz c tiene {len(fila)} elementos en lugar de {m}.")
        c.append(fila)

    # --- Matriz o ---
    # A continuación, las siguientes n líneas son la matriz de disponibilidad o[i][j]
    o = []
    for i in range(1 + m, 1 + m + n):
        fila = list(map(int, archivo_en_lineas[i].split()))
        if len(fila) != u:
            raise ValueError(f"Línea {i+1} de la matriz o tiene {len(fila)} elementos en lugar de {u}.")
        o.append(fila)

    return (n, m, u, c, o)

def generar_dat(output_file_name: str, tupla_elems: tuple):
    """Función que escribe en el .dat todos los datos necesarios para GLPK.
    No devuelve nada. 
    Recibe la tupla (n, m, u, c, o) devuelta por parse_input_file().
    """

    n = tupla_elems[0]
    m = tupla_elems[1]
    u = tupla_elems[2]
    c = tupla_elems[3]
    o = tupla_elems[4]

    # Abrimos el fichero .dat para escribirlo
    with open(output_file_name, "w") as file:

        # --- Cabecera ---
        file.write("data;\n\n")

        # --- Conjuntos ---
        file.write("set BUSES := ")
        for i in range(1, m):
            file.write("a" + str(i) + " ")
        file.write("a" + str(m) + ";\n")

        file.write("set FRANJAS := ")
        for i in range(1, n):
            file.write("s" + str(i) + " ")
        file.write("s" + str(n) + ";\n")

        file.write("set TALLERES := ")
        for i in range(1, u):
            file.write("t" + str(i) + " ")
        file.write("t" + str(u) + ";\n\n")

        # --- Parámetro c ---
        # Matriz cuadrada de tamaño m x m (pasajeros compartidos)
        file.write("param c : ")
        for i in range(1, m + 1):
            file.write("a" + str(i) + " ")
        file.write(":=\n")

        for i in range(1, m + 1):
            file.write("a" + str(i) + " ")
            for j in range(1, m + 1):
                file.write(str(c[i-1][j-1]) + " ")
            file.write("\n")

        file.write(";\n\n")

        # --- Parámetro o ---
        # Matriz n x u de disponibilidad de franjas por taller
        file.write("param o : ")
        for j in range(1, u + 1):
            file.write("t" + str(j) + " ")
        file.write(":=\n")

        for i in range(1, n + 1):
            file.write("s" + str(i) + " ")
            for j in range(1, u + 1):
                file.write(str(o[i-1][j-1]) + " ")
            file.write("\n")

        file.write(";\n\n")

        # --- Fin del fichero ---
        file.write("end;\n")


def ejecutar_glpk(mod_file, dat_file):
    """Ejecuta GLPK con el modelo y el fichero de datos indicados. 
    Devuelve el texto completo de la salida del solver."""

    # Creamos (o vaciamos) un archivo temporal donde GLPK escribirá su salida
    if not os.path.exists("output.txt"):
        with open("output.txt", "w") as f:
            f.write("")

    # Ejecutamos GLPK mediante subprocess
    result = subprocess.run(
        ["glpsol", "--model", mod_file, "--data", dat_file, "--output", "output.txt"],
        text=True,
        capture_output=True
    )
    # PARA AMBOS ARCHIVOS PENSAMOS QUE HABIA QUE GENERAR UN FICHERO DE SALIDA, FINALMENTE NO,
    # SIMPLEMENTE BORRAMOS EL ARCHIVO AL FINAL

    # Leemos la salida del fichero generado
    with open("output.txt", "r") as file:
        output_text = file.read()

    # Verificamos si GLPK encontró una solución óptima
    # TODO: manejo de soluciones no factibles
    if "OPTIMAL SOLUTION FOUND" not in result.stdout:
        return("GLPK no encontró una solución factible para el problema.")

    # Devolvemos el texto completo (lo parsearemos después)
    return output_text


def parse_glpk_output(output_text: str):
    """Extrae la información relevante de la salida de GLPK y la muestra por pantalla.
    Muestra el valor óptimo, número de variables y restricciones, y las asignaciones
    de cada autobús a su franja y taller correspondiente.
    """

    # SI NO HAY SOLUCIÓN ÓPTIMA:
    if output_text == "GLPK no encontró una solución factible para el problema.":
        print(output_text)
        return


    # --- Leemos las líneas y limpiamos ---
    lineas_texto = output_text.split('\n')

    # Buscamos las líneas clave de cabecera (igual que en gen-1)
    linea_restricciones = lineas_texto[1]
    linea_variables = lineas_texto[2]
    linea_z = lineas_texto[5]

    # --- Extraemos con regex ---
    num_restr = re.search(r'\d+', linea_restricciones)
    texto_restr = "Número de restricciones: " + num_restr.group()

    num_variables = re.search(r'\d+', linea_variables)
    texto_variables = "Número de variables: " + num_variables.group()

    z = re.search(r'\d+(?:\.\d+)?', linea_z)
    texto_z = "z = " + z.group()

    # --- Buscamos la tabla de variables (tras los guiones '------') ---
    contador = 0
    index = 0
    while index < len(lineas_texto) and contador < 2:
        if lineas_texto[index][:6] == "------":
            contador += 1
        index += 1

    # --- Listas auxiliares ---
    asignaciones = []  # [(aX, sY, tZ)]
    all_buses = []

    # Recorremos líneas hasta fin de bloque
    while index < len(lineas_texto) and lineas_texto[index] != "":
        # Solo procesamos variables x[a,s,t]
        patron = re.search(r'(x\[[^\]]+\])\s+\*\s+([01])', lineas_texto[index])
        if patron:
            # Extraemos el contenido x[a,s,t]
            tripleta = re.match(r'x\[(a\d+),(s\d+),(t\d+)\]', patron.group(1))
            if tripleta:
                bus = tripleta.group(1)
                franja = tripleta.group(2)
                taller = tripleta.group(3)
                valor = patron.group(2)

                if bus not in all_buses:
                    all_buses.append(bus)
                if valor == "1":
                    asignaciones.append((bus, franja, taller))
        index += 1

    # --- Impresión formateada ---
    print("\n" + texto_z + ", " + texto_variables + ", " + texto_restr + "\n")

    # Mostramos las asignaciones
    for bus, franja, taller in asignaciones:
        print("Autobús", bus, "asignado a franja", franja, "en taller", taller)

    print("\n")  # Línea en blanco final para legibilidad


def main():
    """Función principal: controla todo el flujo del programa.
    Lee los argumentos, procesa el fichero de entrada, genera el .dat,
    ejecuta GLPK con el modelo y muestra el resultado formateado.
    """

    # --- Comprobaciones iniciales ---
    if len(sys.argv) != 3:
        print("Error: número de argumentos incorrecto")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Obtenemos la carpeta donde está el script (para encontrar el .mod)
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construimos la ruta completa al modelo de la parte 2.2.2
    mod_file = os.path.join(script_dir, "parte-2-2.mod")

    if not os.path.exists(input_file):
        print("Error: el archivo de entrada no existe")
        sys.exit(1)

    if not os.path.exists(mod_file):
        print("Error: el archivo de modelo parte-2-2.mod no se encuentra")
        sys.exit(1)

    # --- Ejecución principal ---
    tupla_datos = parse_input_file(input_file=input_file)
    generar_dat(output_file_name=output_file, tupla_elems=tupla_datos)
    output_text = ejecutar_glpk(mod_file=mod_file, dat_file=output_file)
    parse_glpk_output(output_text)

    # --- Limpieza final ---
    if os.path.exists("output.txt"):
        os.remove("output.txt")


if __name__ == "__main__":
    main()
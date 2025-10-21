#!/usr/bin/env python3
import sys
import os
import subprocess


def parse_input_file(input_file:str) -> tuple:
    """Función que recibe el fichero de entrada y lo procesa. Devuelve una tupla = (n, m, kd, kp , d, p)"""

    with open(input_file, "r") as file:
        archivo_en_lineas = file.readlines()

    # Obtenemos cada línea y quitamos los \n
    linea_n_m = archivo_en_lineas[0].strip() # Línea 1: n y m
    linea_kd_kp = archivo_en_lineas[1].strip() # Línea 2: kd y kp
    linea_d = archivo_en_lineas[2].strip() # Línea d
    linea_p = archivo_en_lineas[3].strip() # Línea p

    # Quitamos los espacios y seleccionamos los elementos
    n = linea_n_m.split()[0]
    m = linea_n_m.split()[1]

    kd = linea_kd_kp.split()[0]
    kp = linea_kd_kp.split()[1]

    d = []
    p = []

    # Rellenamos d y p con los valores
    for i in range(0, m):
        d[i] = linea_d.split()[i]
        p[i] = linea_p.split()[i]

    return (n, m, kd, kp, d, p)

def generar_dat(output_file_name:str, tupla_elems:tuple):
    n = tupla_elems[0]
    m = tupla_elems[1]
    kd = tupla_elems[2]
    kp = tupla_elems[3]
    d = tupla_elems[4]
    p = tupla_elems[5]

    # Una vez seleccionados los elementos, escribimos en el .dat
    with open(output_file_name, "w") as file:
        # Cabecera
        file.write("data;\n")

        # Conjuntos
        file.write("set BUSES := ")
        for i in range(1, m):
            file.write("a" + i + " ")

        # El último sin espacio: 
        file.write("a" + m + ";\n")

        file.write("set FRANJAS := ")
        for i in range(1, n):
            file.write("s" + i + " ")

        # El último sin espacio: 
        file.write("s" + n + ";\n\n")

        # Ahora los parámetros
        file.write("param kd := " + kd + ";\n")
        file.write("param kp := " + kp + ";\n\n")

        # Por último, los valores
        file.write("param d :=\n")

        for i in range(1, m):
            file.write("a" + i + " " + d[i-1])

        # El último sin espacio:
        file.write("a" + (i+1) + " " + d[i+1] + ";\n\n")

        file.write("param p :=\n")

        for i in range(1, n):
            file.write("s" + i + " " + p[i-1])
        # El último sin espacio:

        file.write("s" + (i+1) + " " + p[i+1] + ";\n\n")

        # Línea end
        file.write("end;\n")

def ejecutar_glpk(mod_file, dat_file):
    """Ejecuta GLPK y devuelve la salida"""
    result = subprocess.run(["glpsol", "--model", mod_file, "--data", dat_file, "--output", "output.txt"], capture_output=True, text = True, check = True)
    return result.stdout

def parse_glpk_output(salida):
    """Extrae la información que queremos de la salida de GLPK"""
    pass

def print_solucion():
    """Imprimimos la solución"""
    pass



def main():
    if len(sys.argv) != 3:
        print("Error: número de argumentos incorrecto")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print("Error: El archivo de entrada no existe")
        sys.exit(1)



if __name__ == "__main__":
    main()
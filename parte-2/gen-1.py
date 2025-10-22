#!env python3
import sys
import os
import subprocess
import re


def parse_input_file(input_file:str) -> tuple:
    """Función que recibe el fichero de entrada y lo procesa. 
    Devuelve una tupla con los datos: (n, m, kd, kp , d, p)"""

    with open(input_file, "r") as file:
        archivo_en_lineas = file.readlines()

    # Obtenemos cada línea y quitamos los \n
    linea_n_m = archivo_en_lineas[0].strip() # Línea 1: n y m
    linea_kd_kp = archivo_en_lineas[1].strip() # Línea 2: kd y kp
    linea_d = archivo_en_lineas[2].strip() # Línea d
    linea_p = archivo_en_lineas[3].strip() # Línea p

    # Quitamos los espacios y seleccionamos los elementos
    n = int(linea_n_m.split()[0])
    m = int(linea_n_m.split()[1])

    kd = float(linea_kd_kp.split()[0])
    kp = float(linea_kd_kp.split()[1])

    d = []
    p = []

    # Rellenamos d y p con los valores
    for i in range(0, m):
        d.append(float(linea_d.split()[i]))
        p.append(float(linea_p.split()[i]))

    return (n, m, kd, kp, d, p)

def generar_dat(output_file_name:str, tupla_elems:tuple):
    """ Función que escribe en el dat todos los datos. No devuelve nada"""
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
            file.write("a" + str(i) + " ")

        # El último sin espacio: 
        file.write("a" + str(m) + ";\n")

        file.write("set FRANJAS := ")
        for i in range(1, n):
            file.write("s" + str(i) + " ")

        # El último sin espacio: 
        file.write("s" + str(n) + ";\n\n")

        # Ahora los parámetros
        file.write("param kd := " + str(kd) + ";\n")
        file.write("param kp := " + str(kp) + ";\n\n")

        # Parámetros d
        file.write("param d :=\n")

        for i in range(1, m):
            file.write("a" + str(i) + " " + str(d[i-1]) + "\n")

        # El último
        file.write("a" + str(i+1) + " " + str(d[i]) + ";\n\n")

        # Parámetros p
        file.write("param p :=\n")

        for i in range(1, m):
            file.write("a" + str(i) + " " + str(p[i-1]) + "\n")

        # El último
        file.write("a" + str(i+1) + " " + str(p[i]) + ";\n\n")

        # Línea end
        file.write("end;\n")

def ejecutar_glpk(mod_file, dat_file):
    """Ejecuta GLPK y devuelve la salida en un fichero output.txt"""

    if not os.path.exists("output.txt"):
        with open("output.txt", "w") as f:
            f.write("")

    result = subprocess.run(["glpsol", "--model", mod_file, "--data", dat_file, "--output", "output.txt"], text = True, capture_output=True)

    # TODO: HAY QUE CONTEMPLAR LAS SALIDAS INFACTIBLES

    with open("output.txt", "r") as file:
        output_text = file.read()

    return output_text

def parse_glpk_output(output_text:str):
    """Extrae la información que queremos del archivo de
      salida de GLPK: output.txt"""
    
    # Seleccionamos las líneas
    lineas_texto = output_text.split('\n')

    linea_restricciones = lineas_texto[1]
    linea_variables = lineas_texto[2]
    linea_z = lineas_texto[5]

    # Cogemos el texto que nos interesa de cada línea
    num_restr = re.search(r'\d+', linea_restricciones)
    texto_restr = "Número de restricciones: " + num_restr.group()

    num_variables = re.search(r'\d+', linea_variables)
    texto_variables = "Número de variables: " + num_variables.group()


    z = re.search(r'\d+', linea_z)
    texto_z = "z = "+ z.group()

    # Ahora debemos seleccionar las líneas de las asignaciones, que no
    # tienen posición fija



    # bucle aqui para coger lo de cada asignacion
    linea_prueba = lineas_texto[34]
    print(linea_prueba)

    # esto no funciona, ver por qué
    patron_asignaciones = re.search(r'(x\[[^\]]+\])\s+\*\s+([01])', linea_prueba)

    print(patron_asignaciones.group(2))


    print(texto_z + ", " + texto_variables + ", " + texto_restr)

    return 


def print_solucion():
    """Imprimimos la solución"""
    pass



def main():

    # Comprobaciones

    if len(sys.argv) != 3:
        print("Error: número de argumentos incorrecto")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Obtiene la carpeta donde está el script, independientemente del directorio
    # en el que estemos
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construye la ruta completa al .mod
    mod_file = os.path.join(script_dir, "parte-2-1.mod")
    
    if not os.path.exists(input_file):
        print("Error: El archivo de entrada no existe")
        sys.exit(1)

    tupla_datos = parse_input_file(input_file = input_file)
    generar_dat(output_file_name = output_file, tupla_elems=tupla_datos)
    output_text = ejecutar_glpk(mod_file=mod_file, dat_file=output_file)
    parse_glpk_output(output_text)



if __name__ == "__main__":

    main()
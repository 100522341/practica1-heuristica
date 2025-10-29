#!/usr/bin/env python3
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

    # PARA AMBOS ARCHIVOS PENSAMOS QUE HABIA QUE GENERAR UN FICHERO DE SALIDA, FINALMENTE NO,
    # SIMPLEMENTE BORRAMOS EL ARCHIVO AL FINAL
    with open("output.txt", "r") as file:
        output_text = file.read()
    
    # Verificamos si GLPK encontró solución óptima
    if "OPTIMAL SOLUTION FOUND" not in result.stdout:
        return("GLPK no encontró una solución factible para el problema.")
    # Aunque NO es necesario, el problema será siempre factible ya que no hay un mínimo de 
    # franjas ni de autobuses que deban ser asignados / recibir autobuses asignados

    # Devolvemos el texto completo (lo parsearemos después)
    return output_text
    

def parse_glpk_output(output_text:str):
    """Extrae la información que queremos del archivo de
      salida de GLPK: output.txt y la imprime formateada"""
    
    # Seleccionamos las líneas que siempre estarán en el mismo sitio
    lineas_texto = output_text.split('\n')

    linea_restricciones = lineas_texto[1]
    linea_variables = lineas_texto[2]
    linea_z = lineas_texto[5]

    # Cogemos el texto que nos interesa de cada línea
    num_restr = re.search(r'\d+', linea_restricciones)
    texto_restr = "Número de restricciones: " + num_restr.group()

    num_variables = re.search(r'\d+', linea_variables)
    texto_variables = "Número de variables: " + num_variables.group()


    z = re.search(r'\d+(?:\.\d+)?', linea_z)
    texto_z = "z = "+ z.group()

    # Ahora debemos seleccionar las líneas de las asignaciones, que no
    # tienen posición fija

    # Empezamos por ir a la primera línea de las asignaciones
    contador = 0
    index = 0
    while index < len(lineas_texto) and contador < 2:
        if lineas_texto[index][:6] == "------":
            contador += 1
        index += 1    

    # Vamos asignación por asignación
    all_buses = []
    buses_asignados = []
    franja_bus = [] # franja_bus[i] es la franja asociada al bus buses_asignados[i]
    buses_no_asignados = []
    
    while lineas_texto[index] != "":
        if re.match(r'\s*\d+\s+y\[[^\]]+\]', lineas_texto[index]): # Si encontramos la linea y[]
            break
        linea_a_procesar = lineas_texto[index]
        
        # sacar x[ai,sj] y numero actividad 0/1
        patron_asignaciones = re.search(r'(x\[[^\]]+\])\s+\*\s+([01])', linea_a_procesar)

        # sacar ai (group1) sj (group2)
        bus_franja = re.match(r'x\[(a\d+),(s\d+)\]', patron_asignaciones.group(1)) 

        # Añadimos todos los buses a una lista para luego imprimir por separado
        if bus_franja.group(1) not in all_buses:
            all_buses.append(bus_franja.group(1))

        if patron_asignaciones.group(2) == "1": # Si ese autobús está asignado: añadimos a lista asignados
            buses_asignados.append(bus_franja.group(1))
            franja_bus.append(bus_franja.group(2))

        index += 1

    
    print("\n"+ texto_z + ", " + texto_variables + ", " + texto_restr + "\n")
    
    # Rellenamos la lista de no asignados
    for bus in all_buses:
        if bus not in buses_asignados:
            buses_no_asignados.append(bus)

    # Finalmente, imprimimos las asignaciones 
    j = 0
    while j < len(buses_asignados):
        print("Autobús", buses_asignados[j], "asignado a franja", franja_bus[j])
        j += 1

    i = 0
    while i < len(buses_no_asignados):
        print("Autobús", buses_no_asignados[i], "no asignado a ninguna franja")
        i += 1
    print("\n") # Más legibilidad

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

    # Eliminamos el output.txt porque no hace falta
    # Lo hacemos cutre porque el profesor dijo que el script daba igual
    if os.path.exists("output.txt"):
        os.remove("output.txt")



if __name__ == "__main__":

    main()
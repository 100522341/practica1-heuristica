
/* Conjuntos */
set BUSES;  
set FRANJAS;  
set TALLERES;  

/* Parametros escalares */
param c {BUSES, BUSES} >= 0;    # Número de pasajeros compartidos entre autobuses i y l
param o {FRANJAS, TALLERES} binary;    # Disponibilidad de la franja j en el taller k


/* Definicion de variables de decision */
var x {BUSES, FRANJAS, TALLERES} binary;     # 1 si el autobús i se asigna a la franja j y taller k
var y {BUSES, BUSES} binary;        # 1 si autobuses i y l comparten la misma franja 

/* Variable auxiliar */
var z {BUSES, BUSES, FRANJAS, TALLERES} binary;  # 1 si i y l están asignados a la misma franja 


/* Funcion objetivo */
minimize Z:
    sum {i in BUSES, l in BUSES: i < l} c[i,l] * y[i,l];


/* Restricciones */
/* Constraint1: cada autobus se asigna a una franja y un taller */
s.t. AsignacionBuses {i in BUSES}:
    sum {j in FRANJAS, k in TALLERES} x[i,j,k] = 1;

/* Constraint2: solo se asignan franjas disponibles */
s.t. FranjasDisponibles {i in BUSES, j in FRANJAS, k in TALLERES}:
    x[i,j,k] <= o[j,k];

/* Constraint3: cada franja de cada taller se asigna a un autobus */
s.t. Capacidad {j in FRANJAS, k in TALLERES}:
    sum {i in BUSES} x[i,j,k] <= 1;

/* Garantizamos que z[i,l,j,k]=1 cuando x[i,j,k]=1 y x[l,j,k]=1 */
s.t. Acotado1 {i in BUSES, l in BUSES: i < l, j in FRANJAS, k in TALLERES}:
    z[i,l,j,k] <= x[i,j,k];
s.t. Acotado2 {i in BUSES, l in BUSES: i < l, j in FRANJAS, k in TALLERES}:
    z[i,l,j,k] <= x[l,j,k];
s.t. Acotado3 {i in BUSES, l in BUSES: i < l, j in FRANJAS, k in TALLERES}:
    z[i,l,j,k] >= x[i,j,k] + x[l,j,k] - 1;

/* El valor de y[i,l] sera 1 si existe alguna franja en la que ambos autobuses coincidan */
s.t. Rel_OR1 {i in BUSES, l in BUSES: i < l}:
    y[i,l] >= z[i,l,j,k]  for all j,k;
s.t. Rel_OR2 {i in BUSES, l in BUSES: i < l}:
    y[i,l] <= sum {j in FRANJAS, k in TALLERES} z[i,l,j,k];

/* Conjuntos */
set BUSES;
set FRANJAS;

/* Parametros escalares */
param kd;
param kp;

/* Parametros unidimensionales */
param d{BUSES};
param p{BUSES};

/* Definicion de variables de decision */
var x{BUSES, FRANJAS} binary; /* 1 si el autobús i se asigna a franja j */
var y{BUSES} binary; /* 1 si autobús i NO es asignado a ninguna franja */

/* Funcion objetivo */

minimize OverallCost:
	sum{i in BUSES, j in FRANJAS} kd * d[i] * x[i,j]
	+
	sum{i in BUSES} kp * p[i] * y[i];

/* Constraint1: cada autobús máx asignado a una franja: */
s.t. CapacidadFranja {j in FRANJAS}:
	sum{i in BUSES} x[i,j] <= 1; 

/* Constraint2: cada franja tiene asignado como máx un autobús: */
s.t. AsignacionAutobus {i in BUSES}:
	sum{j in FRANJAS} x[i,j] + y[i]<= 1;

/* Constraint3: restringimos la variable auxiliar y */
s.t. AuxY {i in BUSES}:
	y[i] = 1 - sum{j in FRANJAS} x[i, j];


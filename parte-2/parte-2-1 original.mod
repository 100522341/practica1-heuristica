
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
var x{BUSES, FRANJAS} binary;

/* Funcion objetivo */

minimize OverallCost:
	sum{i in BUSES, j in FRANJAS} kd * d[i] * x[i,j]
	+
	sum{i in BUSES} kp * p[i] * (1 - sum{j in FRANJAS} x[i,j]);

/* Constraint1: cada autobús máx asignado a una franja: */
s.t. CapacidadFranja {j in FRANJAS}:
	sum{i in BUSES} x[i,j] <= 1; 

/* Constraint2: cada franja tiene asignado como máx un autobús: */
s.t. AsignacionAutobus {i in BUSES}:
	sum{j in FRANJAS} x[i,j] <= 1;



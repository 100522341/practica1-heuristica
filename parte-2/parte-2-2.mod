/* Conjuntos */
set BUSES;  
set FRANJAS;  
set TALLERES;  


/* Parámetros */
param c {BUSES, BUSES} >= 0;    /* Número de pasajeros compartidos entre autobuses i y l */
param o {FRANJAS, TALLERES} binary;    /* Disponibilidad de la franja j en el taller k */


/* Variables de decisión */
var x {BUSES, FRANJAS, TALLERES} binary;      /* 1 si el autobús i se asigna a la franja j y taller k */
var y {BUSES, BUSES, FRANJAS} binary;         /* 1 si los autobuses i y l coinciden en la misma franja j */


/* Función objetivo */
minimize Z:
    sum {i in BUSES, l in BUSES: i < l} c[i,l] * sum {j in FRANJAS} y[i,l,j];


/* Restricciones */

/* Constraint1: cada autobús se asigna a exactamente una franja y taller */
s.t. AsignacionBuses {i in BUSES}:
    sum {j in FRANJAS, k in TALLERES} x[i,j,k] = 1;

/* Constraint2: solo se asignan franjas disponibles */
s.t. FranjasDisponibles {i in BUSES, j in FRANJAS, k in TALLERES}:
    x[i,j,k] <= o[j,k];

/* Constraint3: cada franja de cada taller se asigna a lo sumo a un autobús */
s.t. Capacidad {j in FRANJAS, k in TALLERES}:
    sum {i in BUSES} x[i,j,k] <= 1;

/* Constraint4: y[i,l,j] solo puede ser 1 si el bus i está en la franja j */
s.t. YBusIFranjaJ {i in BUSES, l in BUSES, j in FRANJAS: i < l}:
    y[i,l,j] <= sum {k in TALLERES} x[i,j,k];

/* Constraint5: y[i,l,j] solo puede ser 1 si el bus l está en la franja j */
s.t. YBusLFranjaJ {i in BUSES, l in BUSES, j in FRANJAS: i < l}:
    y[i,l,j] <= sum {k in TALLERES} x[l,j,k];

/* Constraint6: y[i,l,j] se activa si ambos buses están en la franja j */
s.t. MismaFranja {i in BUSES, l in BUSES, j in FRANJAS: i < l}:
    y[i,l,j] >= sum {k in TALLERES} (x[i,j,k] + x[l,j,k]) - 1;

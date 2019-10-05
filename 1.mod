set votantes;
set centros;

param lat_vot{i in votantes};
param long_vot{i in votantes};
param lat_cen{i in centros};
param long_cen{j in centros};
param capacidad{j in centros};


/***** Se importan los " " datos del csv de votantes *****/

table tin IN "CSV" "./data/votantes_reducido.csv" : 
votantes <- [id], lat_vot ~ lat, long_vot ~ long;

/***** Se importan los datos del csv de centros *****/
table tin IN "CSV" "./data/centros_reducido.csv" :
centros <- [id], lat_cen ~ lat, long_cen ~ long, capacidad ~ max_votantes;

printf "\n\n\nCantidad de votantes: %d\n", card(votantes);
printf "Cantidad de centros: %d\n", card(centros);


/* En un momento pensé usar Manhattan, pero nada me garantiza */
/* que la direccion de cada calle sea paralela */
/* a la dirección en la que crece la latitud o la longitud */
/* Distancia Euclideana */
param dist{i in votantes, j in centros} := sqrt(abs(lat_vot[i] - lat_cen[j]) ** 2 + abs(long_vot[i] - long_cen[j]) ** 2 );

/***** Variables *****/

/* 1 si el votante i fue asignado al centro j, 0 sino */
var y{i in votantes, j in centros}, binary >= 0;

/* 1 si el centro j se abre para la elección, 0 sino */
var abre{j in centros}, binary >= 0;

/* Distancia que recorre el votante i */
var x{i in votantes} >= 0;

/* Distancia maxima que recorre un votante */
var max_x >= 0;

/* var mesas{j in centros}, integer >= 0; */

/***** Objetivo *****/
minimize z: sum{i in votantes} x[i] / card(votantes) + max_x;



/***** Restricciones *****/
s.t. DistanciaMaxima{i in votantes}: max_x >= x[i];

s.t. DebeVotar{i in votantes}: sum{j in centros} y[i,j] = 1;

/* Junto la restricción de la capacidad y la que dice que si */
/* el centro está cerrado, no se le asignen votantes */
s.t. CapacidadMax{j in centros}: sum{i in votantes} y[i,j] <= capacidad[j] * abre[j];

/* s.t. Min150PorMesa{j in centros}: sum{i in votantes} y[i,j] >= mesas[j] * 150; */

/* s.t. Max300PorMesa{j in centros}: sum{i in votantes} y[i,j] <= 300 * mesas[j]; */

s.t. DistMinSiSeAsigna{i in votantes, j in centros}: x[i] >= dist[i,j] * y[i,j];
s.t. DistMaxSiSeAsigna{i in votantes, j in centros}: x[i] <= dist[i,j] + 1000 * (1 - y[i,j]);


end;



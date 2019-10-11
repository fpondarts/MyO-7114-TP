set votantes;
set centros;

param lat_vot{i in votantes};
param long_vot{i in votantes};
param lat_cen{i in centros};
param long_cen{j in centros};
param capacidad{j in centros};


/***** Se importan los " " datos del csv de votantes *****/
table tin IN "CSV" "./data/votantes.csv" : 
votantes <- [id], lat_vot ~ latitud, long_vot ~ longitud;

/***** Se importan los datos del csv de centros *****/
table tin IN "CSV" "./data/centros.csv" :
centros <- [id], lat_cen ~ lat, long_cen ~ long, capacidad ~ max_votantes;


printf "\n\n\nCantidad de votantes: %d\n", card(votantes);
printf "Cantidad de centros: %d\n", card(centros);

/* En un momento pensé usar Manhattan, pero nada me garantiza */
/* que la direccion de cada calle sea paralela */
/* a la dirección en la que crece la latitud o la longitud */
/* Distancia Euclideana */
param dist{i in votantes, j in centros} := sqrt(abs(lat_vot[i] - lat_cen[j]) ** 2 + abs(long_vot[i] - long_cen[j]) ** 2); 


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
#La bivalente abre[j] deberia encenderse cuando se cumpla la cantidad minima de mesas? 
s.t. CapacidadMax{j in centros}: sum{i in votantes} y[i,j] <= capacidad[j] * abre[j];

#¿El valor de mesas[j] es la cantidad de mesas que tiene el centro j?
# o es la cantidad minima de mesas que deben abrirse para habilitar el centro j?
#La cantidad minima de mesas para habilitar un centro es global, o es individual para cada establecimiento?
#s.t. Min150PorMesa{j in centros}: sum{i in votantes} y[i,j] >= 10 * 150;
#s.t. Max300PorMesa{j in centros}: sum{i in votantes} y[i,j] <= 300 * mesas[j];

#tomamos minimo de votantes 20 y cantidad de mesas minima igual a 1
s.t. Min120PorMesa{j in centros}: sum{i in votantes} y[i,j] >= 120 * 1 * abre[j] ;
#tomamos maximo de votantes 70 y cantidad de mesas minima igual a 1
#s.t. MaxPersonasPorMesa{j in centros}: 20 * 1 + (50 * abre[j]) >= sum{i in votantes} y[i,j];
s.t. MaxPersonasPorMesa{j in centros}:  capacidad[j] * abre[j] >= sum{i in votantes} y[i,j];


#s.t. DistMinSiSeAsigna{i in votantes, j in centros}: x[i] >= dist[i,j] * y[i,j];
#s.t. DistMaxSiSeAsigna{i in votantes, j in centros}: x[i] <= dist[i,j] + 1000 * (1 - y[i,j]);
/*Calculo de distancia recorrida por el votante i*/
s.t. DistRecorridaPorVotanteI{i in votantes} : sum{j in centros} dist[i,j] * y[i,j] <= x[i];

end;



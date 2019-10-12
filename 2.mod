set votantes;
set centros;

param lat_vot{i in votantes};
param long_vot{i in votantes};
param lat_cen{i in centros};
param long_cen{j in centros};
param capacidad{j in centros};


/***** Se importan los " " datos del csv de votantes *****/
table tin IN "CSV" "./data/votantes.csv" : 
votantes <- [id], lat_vot ~ lat, long_vot ~ long;


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

param RADIO := 6371000;

param PI := 3.141592; 

param latrad_vot{i in votantes} := lat_vot[i] * PI / 180;
param latrad_cen{j in centros} := lat_cen[j] * PI / 180;
param lonrad_vot{i in votantes} := long_vot[i] * PI / 180;
param lonrad_cen{j in centros} := long_cen[j] * PI / 180;

param d_lat{i in votantes, j in centros} := (latrad_cen[j] - latrad_vot[i]);
param d_long{i in votantes, j in centros} := (lonrad_cen[j] - lonrad_vot[i]);

param aux_a{i in votantes, j in centros} := ( sin( d_lat[i,j] / 2 ) ** 2 ) + cos( latrad_vot[i] ) * cos( latrad_cen[j] ) * ( sin( d_long[i,j] / 2 ) ** 2 ) ; 

param aux_c{i in votantes, j in centros} := 2 * atan( sqrt( aux_a[i,j] )/ sqrt( 1 - aux_a[i,j] ) ) ;

param haversine{i in votantes, j in centros} := RADIO * aux_c[i,j];

#table tout {i in votantes, j in centros} OUT "CSV" "./haversine.csv" :
#i,j,haversine[i,j];

/***** Variables *****/
/* 1 si el votante i fue asignado al centro j, 0 sino */
var y{i in votantes, j in centros}, binary >= 0;

/* 1 si el centro j se abre para la elección, 0 sino */
var abre{j in centros}, binary >= 0;

/* Distancia que recorre el votante i */
var x{i in votantes} >= 0;

/* Distancia maxima que recorre un votante */
var max_x >= 0;


/***** Objetivo *****/
minimize z: sum{i in votantes} x[i] / card(votantes) + max_x;

/***** Restricciones *****/
s.t. DistanciaMaxima{i in votantes}: max_x >= x[i];

s.t. DebeVotar{i in votantes}: sum{j in centros} y[i,j] = 1;

/* Junto la restricción de la capacidad y la que dice que si */
/* el centro está cerrado, no se le asignen votantes */
#La bivalente abre[j] deberia encenderse cuando se cumpla la cantidad minima de mesas? 
s.t. CapacidadMax{j in centros}: sum{i in votantes} y[i,j] <= capacidad[j] * abre[j];

#tomamos minimo de votantes 120 y cantidad de mesas minima igual a 1
s.t. Min120PorMesa{j in centros}: sum{i in votantes} y[i,j] >= 120 * 1 * abre[j] ;

/*Calculo de distancia recorrida por el votante i*/
s.t. DistRecorridaPorVotanteI{i in votantes} : sum{j in centros} haversine[i,j] * y[i,j] = x[i];


end;



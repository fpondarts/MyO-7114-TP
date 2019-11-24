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


/* Un paso de 0.0011 grados en latitud/longitud */
/* Esto se calculo utilizando google maps y trazando una línea */
/* con distancia de 100m, dejando fija una coordenada y variando la otra */
/* se corresponde con un paso de 100 metros aproximadamente */

param PASO := 0.0011;

/* Lat y Long maximas y minimas para obtener las dimensiones del circuito */
param max_lat := max{i in votantes} lat_vot[i];
param max_long := max{i in votantes} long_vot[i];
param min_lat := min{i in votantes} lat_vot[i];
param min_long := min{i in votantes} long_vot[i];


/* Se obtienen las dimensiones del circuito */
param ALTO := max_lat - min_lat ;
param ANCHO := max_long - min_long ;


/* Se modela al circuito como una matriz de FILAS y COLUMNAS */
/* Cada elemento de la matriz se corresponde con un recinto de */
/* 100 metros x 100 metros */
param COLUMNAS := round( ANCHO / PASO ) + 1;
param FILAS := round( ALTO / PASO ) + 1;

/* Se mapea cada votante a un elemento (fila,columna) de la matriz */
/* En otras palabras, se calcula a que manzana pertenece cada votante */
param fila{i in votantes} := round( (lat_vot[i] - min_lat) / PASO ) + 1; 
param columna{i in votantes} := round( ( long_vot[i] - min_long ) / PASO ) + 1;

/* Se genera un csv donde cada registro es */
/* id_votante, fila, columna */
table tout{i in votantes} OUT "CSV" "./matriz.csv":
i,fila[i],columna[i];


/* Se calcula la cantidad de votantes que tiene cada manzana */
param VotantesManzana{f in 1..FILAS, c in 1..COLUMNAS} := sum{i in votantes: fila[i] == f && columna[i] == c} 1;
printf "Suma de votantes es: %i\n", sum{f in 1..FILAS, c in 1..COLUMNAS} VotantesManzana[f,c];


table tout{f in 1..FILAS, c in 1..COLUMNAS: VotantesManzana[f,c] > 0} OUT "CSV" "./votantes_manzana.csv":
f,c,VotantesManzana[f,c];

param PI := 3.141592; 
param RADIO := 6371000;

param LatRad_manzana{ f in 1..FILAS } := (min_lat + (f - 1 + 0.5) * PASO) * PI / 180;
param LonRad_manzana{ c in 1..COLUMNAS } := (min_long + (c - 1 + 0.5 ) * PASO) * PI / 180;

param LatRad_cen{j in centros} := lat_cen[j] * PI / 180;
param LonRad_cen{j in centros} := long_cen[j] * PI / 180;

param d_lat{f in 1..FILAS, j in centros} := (LatRad_cen[j] - LatRad_manzana[f]);
param d_long{c in 1..COLUMNAS, j in centros} := (LonRad_cen[j] - LonRad_manzana[c]);

param aux_a{f in 1..FILAS, c in 1..COLUMNAS, j in centros} := ( sin( d_lat[f,j] / 2 ) ** 2 ) + cos( LatRad_manzana[f] ) * cos( LatRad_cen[j] ) * ( sin( d_long[c,j] / 2 ) ** 2 ) ; 

param aux_c{f in 1..FILAS, c in 1..COLUMNAS, j in centros} := 2 * atan( sqrt( aux_a[f,c,j] )/ sqrt( 1 - aux_a[f,c,j] ) ) ;

param haversine{f in 1..FILAS, c in 1..COLUMNAS, j in centros} := RADIO * aux_c[f,c,j];

param M := 10000000;
param m := 0.0000001;


/***** Variables *****/

/* 1 si el centro j se abre para la elección, 0 sino */
var abre{j in centros}, binary >= 0;

var y{f in 1..FILAS, c in 1..COLUMNAS, j in centros: VotantesManzana[f,c] > 0}, binary >= 0;

/* votantes de la manzana[i,j] asignados al centro j */
var x{f in 1..FILAS, c in 1..COLUMNAS, j in centros: VotantesManzana[f,c] > 0}, integer >= 0;

table tout{f in 1..FILAS, c in 1..COLUMNAS, j in centros: VotantesManzana[f,c] > 0} OUT "CSV" "./asignaciones.csv":
f,c,j,x[f,c,j];

/* Distancia maxima que recorre un votante */
var max_x >= 0;

minimize z: sum{f in 1..FILAS, c in 1..COLUMNAS, j in centros: VotantesManzana[f,c] > 0} haversine[f,c,j] * x[f,c,j] / card(votantes) + max_x;

s.t. TotalManzana{f in 1..FILAS, c in 1..COLUMNAS :VotantesManzana[f,c] > 0}: sum{j in centros} x[f,c,j] = VotantesManzana[f,c];

s.t. CapacidadCentro{j in centros}: sum{f in 1..FILAS, c in 1..COLUMNAS: VotantesManzana[f,c] > 0} x[f,c,j] <= capacidad[j] * abre[j];

s.t. Minimo30ParaAbrir{j in centros}: sum{f in 1..FILAS, c in 1..COLUMNAS: VotantesManzana[f,c] > 0} x[f,c,j] >= 30 * abre[j];

s.t. EnvioAlguno{f in 1..FILAS, c in 1..COLUMNAS, j in centros: VotantesManzana[f,c] > 0}: x[f,c,j] <= M * y[f,c,j];

s.t. EnvioAlgunoBis{f in 1..FILAS, c in 1..COLUMNAS, j in centros: VotantesManzana[f,c] > 0}: x[f,c,j] >= 1 * y[f,c,j];

s.t. DistMax{f in 1..FILAS, c in 1..COLUMNAS, j in centros: VotantesManzana[f,c] > 0}: max_x >= haversine[f,c,j] * y[f,c,j];


end;

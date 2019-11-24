#!/bin/sh

MATRIZ="matriz.csv"

if [ ! -f "$MATRIZ" ] ; then 
    echo "No se ha encontrado el archivo matriz.csv o el archivo manzanas.sol"
    exit
fi 

mkdir ./ids_por_manzana

if [ ! -d "./ids_por_manzana" ] ; then 
    echo "No se ha podido crear el directorio ids_por_manzana"
    exit
fi

while read -r linea
do

    id="$(echo $linea | sed "s/\([0-9]*\),\([0-9]*\),\([0-9]*\)/\1/")"
    if [ "$id" == "id" ];then
        continue
    fi
    fila="$(echo $linea | sed "s/\([0-9]*\),\([0-9]*\),\([0-9]*\)/\2/")"
    columna="$(echo $linea | sed "s/\([0-9]*,\)\([0-9]*,\)\([0-9]*\)/\3/")"

    echo "$id" >> "./ids_por_manzana/manzana_$fila-$columna"

done < "$MATRIZ"     

#!/bin/bash

if [ $# -eq 0 ]
then
    echo "No pasaste ningun archivo"
    echo "digita './analiza.sh NOMBRE.log'"
    echo "en caso de ser varios archivos"
    echo "digita './analiza.sh NOMBRE.log NOMBRE.log NOMBRE.log'"
    exit 1
fi

for archivo in "$@"
do
    if [ ! -e "$archivo" ]
    then
        echo "Error: $archivo no existe"

    elif [ ! -f "$archivo" ]
    then
        echo "Error: $archivo no es un archivo valido"

    else
        echo "Archivo: $archivo"
        echo "Lineas: $(wc -l < "$archivo")"
        echo "Palabras: $(wc -w < "$archivo")"
        echo "Caracteres: $(wc -c < "$archivo")"
        echo "Cantidad lineas 'ERROR': $(grep 'ERROR' "$archivo" | wc -l)"
        echo "Cantidad lineas 'WARN': $(grep 'WARN' "$archivo" | wc -l)"
    fi
done

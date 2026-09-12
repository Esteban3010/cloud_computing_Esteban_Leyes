#!/bin/bash

ruta=$1

echo "Hostname: $(hostname)"
echo "Usuario: $(whoami)"
echo "Fecha: $(date)"

echo "Filesystem de: $ruta"
df -h "$ruta"

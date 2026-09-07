#!/bin/bash

echo "===== MONITOR DEL CONTENEDOR ====="
echo "Hostname: $(hostname)"
echo "Usuario: $(whoami)"
echo "Fecha: $(date)"
echo "Directorio: $(pwd)"

echo "===== DISCO ====="
df -h

echo "===== PROCESOS ====="
ps aux | wc -l

particion=$(df / | awk 'NR==2 {print $5}' | cut -d'%' -f1)

if [ $particion -gt 67]
then
        echo "Advertencia: el disco supera el 67% de uso"
else
        echo "Aviso: el uso del disco ta bien"
fi

echo "===== FIN DEL REPORTE ====="

#!/bin/bash
#SBATCH --job-name=mitrabajo
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=16384
#SBATCH --time=72:00:00
#SBATCH --tmp=9G
#SBATCH --partition=normal
#SBATCH --qos=normal
#SBATCH --mail-type=ALL
#SBATCH --mail-user=santiolmedo99@gmail.com

source /etc/profile.d/modules.sh

cd ~/hpc/Montevideo-bus-stops-delay/
for EJECUCION in 1 2 3 4 5
do
	echo "Ejecucion $EJECUCION"
	echo "1 proceso con 16gb de RAM" 
	python3 procesar_viajes.py
done

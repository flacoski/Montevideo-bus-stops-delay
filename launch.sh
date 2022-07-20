#!/bin/bash
#SBATCH --job-name=mitrabajo
#SBATCH --ntasks=1
#SBATCH --mem=16384
#SBATCH --time=6:00:00
#SBATCH --tmp=9G
#SBATCH --partition=normal
#SBATCH --qos=normal
#SBATCH --mail-type=ALL
#SBATCH --mail-user=santiolmedo99@gmail.com

source /etc/profile.d/modules.sh

cd ~/hpc/Montevideo-bus-stops-delay/
python3 procesar_viajes.py

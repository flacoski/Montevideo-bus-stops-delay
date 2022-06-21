import multiprocessing as mp
import string
import subprocess
import math
import os
import pdb


numero_de_hilos=16
ruta_archivo_viajes="datos/viajes/viajes_stm_052022.csv"
ruta_archivo_horarios="datos/horariosOmnibus.csv"
ruta_archivo_paradas="datos/ubicacionParadas/paradas.csv"

listaParadas = {}

archivo_paradas=open(ruta_archivo_paradas)
filas_paradas=archivo_paradas.readlines()
filas_paradas=filas_paradas[1:]
for fila in filas_paradas:
    filaAux=fila.split(",")
    if filaAux[4] == "AV GRAL RIVERA":
        listaParadas[int(filaAux[0].strip())] = (0)

archivo_paradas.close()

archivo_viajes=open(ruta_archivo_viajes)
filas_viajes=archivo_viajes.readlines()
filas_viajes=filas_viajes[1:]
for fila in filas_viajes:
    filaAux=fila.split(",")
    #pdb.set_trace()
    if int(filaAux[11].strip()) in listaParadas.keys():
        listaParadas[int(filaAux[11].strip())] += 1

sort_listaParadas = sorted(listaParadas.items(), key=lambda x: x[1], reverse=True)
listaParadasmasvendidas = sort_listaParadas[0:10]

dictParadas = {}


print(listaParadasmasvendidas)
archivo_viajes.close()
import multiprocessing as mp
from operator import mod
import string
import subprocess
import math
import os
import pdb
import time
from datetime import datetime

comienzo = time.time()
numero_de_hilos=16
ruta_archivo_viajes="datos/viajes/viajes_stm_052022.csv"
ruta_archivo_horarios="datos/horariosOmnibus.csv"
ruta_archivo_paradas="datos/ubicacionParadas/paradas.csv"
ruta_archivo_avenidas="lista_avenidas"

def tipo_dia(fecha):
    ret = fecha.weekday()
    if ret == 5:
        return 2
    elif ret == 6:
        return 3
    else:
        return 1

def comparar_horarios(fecha_string,horario):
    formato = "%Y-%m-%dT%H:%M:%S.%f%z"
    fecha_completa = datetime.strptime(fecha_string,formato)
    if tipo_dia(fecha_completa.date()) != horario[0]: #caso borde entre tipos de dia
        return None
    return comparar_horas(fecha_completa.time(),horario[2])

def comparar_horas(fecha_hora_string, hora_completa_teorica):
    formato = "%H:%M:%S"
    minutos_teoricos = int(hora_completa_teorica % 100)
    hora_teorica = int((hora_completa_teorica - minutos_teoricos) / 100) if (hora_completa_teorica - minutos_teoricos) != 0 else 0
    hora_completa = datetime.strptime(str(hora_teorica) + ":" + str(minutos_teoricos) + ":00",formato).time()
    desviacion = hora_a_segundos(hora_completa) - hora_a_segundos(fecha_hora_string)
    if abs(desviacion) > 900:
        return None
    else:
        return desviacion
    
def hora_a_segundos(hora_datetime):
    return(hora_datetime.hour * 60 + hora_datetime.minute) * 60 + hora_datetime.second

lista_avenidas = ["AV GRAL RIVERA"]

# archivo_avenidas=open(ruta_archivo_avenidas)
# filas_avenidas=archivo_avenidas.readlines()
# filas_avenidas=filas_avenidas[1:]
# for fila in filas_avenidas:
#     lista_avenidas.append(fila.rstrip('\n'))
# archivo_avenidas.close()

lista_paradas_contador = {} #key = codigo_parada, values = [contador,calle 1, calle 2]

#Recorremos las paradas y nos quedamos con las que pertenecen a las calles elegidas
archivo_paradas=open(ruta_archivo_paradas)
filas_paradas=archivo_paradas.readlines()
filas_paradas=filas_paradas[1:]
for fila in filas_paradas:
    fila_aux=fila.split(",")
    if fila_aux[4] in lista_avenidas:
        lista_paradas_contador[int(fila_aux[0])] = [0,fila_aux[4],fila_aux[5]]
archivo_paradas.close()

del filas_paradas

#Recorremos los viajes y le sumamos uno al contador de cada parada
archivo_viajes=open(ruta_archivo_viajes)
filas_viajes=archivo_viajes.readlines()
filas_viajes=filas_viajes[1:]
for fila in filas_viajes:
    fila_aux=fila.split(",")
    if int(fila_aux[11]) in lista_paradas_contador.keys():
        lista_paradas_contador[int(fila_aux[11])][0] += 1
archivo_viajes.close()

del filas_viajes

lista_paradas_avenida = {} #key = calle1, values = [contador, calle 2, codigo_parada, desviacion, cantidad_viajes]

#Hacer un diccionario donde la key sea la avenida
for parada in lista_paradas_contador.items():
    if parada[1][1] in lista_paradas_avenida:
        lista_paradas_avenida[parada[1][1]].append([parada[1][0],parada[1][2],parada[0],0,0])
    else:
        lista_paradas_avenida[parada[1][1]] = [[parada[1][0],parada[1][2],parada[0],0,0]]

del lista_paradas_contador

#Ordenar las paradas por cantidad de boletos vendidos(descendente) y quedarnos con las 10 primeras paradas por cada avenida
for avenida in lista_paradas_avenida.items():
    paradas_en_orden = sorted(avenida[1], key=lambda x: x[0], reverse=True)
    paradas_en_orden = paradas_en_orden[0:10]
    lista_paradas_avenida[avenida[0]] = paradas_en_orden

lista_horarios_parada  = {}#key = codigo_parada, values = [tipo_dia,codigo_omnibus,hora_teorica,calle 1]

#Recorrer los horarios teóricos y quedarnos solo con aquellos que pertenezcan a las paradas relevantes
archivo_horarios=open(ruta_archivo_horarios)
filas_horarios=archivo_horarios.readlines()
filas_horarios=filas_horarios[1:]
for fila in filas_horarios:
    fila_aux=fila.split(";")
    for avenida in lista_paradas_avenida.items():
        for parada in avenida[1]:
            if int(fila_aux[3]) == parada[2]:
                if int(fila_aux[3]) in lista_horarios_parada:
                    lista_horarios_parada[int(fila_aux[3])].append([int(fila_aux[0]),int(fila_aux[1]),int(fila_aux[5]),avenida[0]])
                else:
                    lista_horarios_parada[int(fila_aux[3])] = [[int(fila_aux[0]),int(fila_aux[1]),int(fila_aux[5]),avenida[0]]]
                break
archivo_horarios.close()

del filas_horarios

archivo_viajes=open(ruta_archivo_viajes)
filas_viajes=archivo_viajes.readlines()
filas_viajes=filas_viajes[1:]
for fila in filas_viajes:
    fila_aux=fila.split(",")
    if int(fila_aux[11]) in lista_horarios_parada.keys():
        for horario in lista_horarios_parada[int(fila_aux[11])]:
            if int(fila_aux[16]) == horario[1]:
                desviacion = comparar_horarios(fila_aux[2],horario)
                if desviacion != None:
                    for parada in lista_paradas_avenida[lista_horarios_parada[int(fila_aux[11])][0][3]]:
                        if parada[2] == int(fila_aux[11]):
                            parada[3] += desviacion #aca estamos contando todos los boletos que se emiten en una parada
                            parada[4] += 1
archivo_viajes.close() 


final = time.time()
print(lista_paradas_avenida)
print(final-comienzo)


    











import multiprocessing as mp
from operator import mod
import time
from datetime import datetime

comienzo = time.time()
numero_de_hilos=16
ruta_archivo_viajes="datos/viajes/viajes_stm_052022.csv"
ruta_archivo_horarios_teoricos="datos/horariosOmnibus.csv"
ruta_archivo_paradas="datos/ubicacionParadas/paradas.csv"
ruta_archivo_avenidas="lista_avenidas"


#dado un dia de la semana retorna el tipo de dia:
#    lunes a viernes: 1
#    sabado: 2
#    domingo: 3
def tipo_dia(fecha):
    weekday = fecha.weekday()
    if weekday == 5:
        return 2
    elif weekday == 6:
        return 3
    else:
        return 1

#retorna la desviacion de segundos entre el horario real y el teorico si aplica.
#no aplica si no es el mismo tipo de dia o si hay mas de 900 segundos de diferencia
def comparar_horarios(fecha_string,horario):
    formato_fecha = "%Y-%m-%dT%H:%M:%S.%f%z"
    fecha_completa = datetime.strptime(fecha_string,formato_fecha)
    if tipo_dia(fecha_completa.date()) != horario[0]: #caso borde entre tipos de dia
        return None
    return comparar_horas(fecha_completa.time(),horario[2])


def comparar_horas(fecha_hora_real_string, hora_completa_teorica):
    formato_hora = "%H:%M:%S"
    minutos_teoricos = int(hora_completa_teorica % 100)
    hora_teorica = int((hora_completa_teorica - minutos_teoricos) / 100) if (hora_completa_teorica - minutos_teoricos) != 0 else 0
    hora_completa_real = datetime.strptime(str(hora_teorica) + ":" + str(minutos_teoricos) + ":00",formato_hora).time()
    desviacion = hora_a_segundos(hora_completa_real) - hora_a_segundos(fecha_hora_real_string)
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
paradas=archivo_paradas.readlines()
paradas=paradas[1:]
for _parada in paradas:
    parada=_parada.split(",")
    if parada[4] in lista_avenidas:
        lista_paradas_contador[int(parada[0])] = [0,parada[4],parada[5]]
archivo_paradas.close()

del paradas

#Recorremos los viajes y le sumamos uno al contador de cada parada
archivo_viajes=open(ruta_archivo_viajes)
viajes=archivo_viajes.readlines()
viajes=viajes[1:]
for _viaje in viajes:
    viaje=_viaje.split(",")
    if int(viaje[11]) in lista_paradas_contador.keys():
        lista_paradas_contador[int(viaje[11])][0] += 1
archivo_viajes.close()

del viajes

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
    lista_paradas_avenida[avenida[0]] = paradas_en_orden[0:10]

lista_horarios_teoricos_parada  = {}#key = codigo_parada, values = [tipo_dia,codigo_omnibus,hora_teorica,calle 1]

#Recorrer los horarios teóricos y quedarnos solo con aquellos que pertenezcan a las paradas relevantes
archivo_horarios_teoricos=open(ruta_archivo_horarios_teoricos)
horarios_teoricos=archivo_horarios_teoricos.readlines()
horarios_teoricos=horarios_teoricos[1:]
for _horario_teorico in horarios_teoricos:
    horario_teorico=_horario_teorico.split(";")
    for avenida in lista_paradas_avenida.items():
        for parada in avenida[1]:
            if int(horario_teorico[3]) == parada[2]:
                if int(horario_teorico[3]) in lista_horarios_teoricos_parada:
                    lista_horarios_teoricos_parada[int(horario_teorico[3])].append([int(horario_teorico[0]),int(horario_teorico[1]),int(horario_teorico[5]),avenida[0]])
                else:
                    lista_horarios_teoricos_parada[int(horario_teorico[3])] = [[int(horario_teorico[0]),int(horario_teorico[1]),int(horario_teorico[5]),avenida[0]]]
                break
archivo_horarios_teoricos.close()

del horarios_teoricos

archivo_viajes=open(ruta_archivo_viajes)
viajes=archivo_viajes.readlines()
viajes=viajes[1:]
for _viaje in viajes:
    viaje=_viaje.split(",")
    if int(viaje[11]) in lista_horarios_teoricos_parada.keys():
        for horario_teorico in lista_horarios_teoricos_parada[int(viaje[11])]:
            if int(viaje[16]) == horario_teorico[1]: #solo comparamos si son la misma variante
                desviacion = comparar_horarios(viaje[2],horario_teorico)
                if desviacion != None:
                    for parada in lista_paradas_avenida[lista_horarios_teoricos_parada[int(viaje[11])][0][3]]:
                        if parada[2] == int(viaje[11]):
                            parada[3] += desviacion #aca estamos contando todos los boletos que se emiten en una parada
                            parada[4] += 1
archivo_viajes.close() 


final = time.time()
print(lista_paradas_avenida)
print(final-comienzo)


    











import multiprocessing as mp
import time
import pdb
from datetime import datetime

comienzo = time.time()
numero_de_hilos = 16
ruta_archivo_viajes = "datos/viajes/viajes_stm_052022.csv"
ruta_archivo_horarios_teoricos = "datos/horariosOmnibus.csv"
ruta_archivo_paradas = "datos/ubicacionParadas/paradas.csv"
ruta_archivo_avenidas = "lista_avenidas"


# dado un dia de la semana retorna el tipo de dia:
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

# retorna la desviacion de segundos entre el horario real y el teorico si aplica.
# no aplica si no es el mismo tipo de dia o si hay mas de 900 segundos de diferencia


def comparar_horarios(horario_real, horario_teorico):
    tipo_dia_teorico = horario_teorico[0]
    hora_teorica = horario_teorico[1]
    formato_fecha = "%Y-%m-%dT%H:%M:%S.%f%z"
    fecha_completa = datetime.strptime(horario_real, formato_fecha)
    # caso borde entre tipos de dia
    if tipo_dia(fecha_completa.date()) != tipo_dia_teorico:
        return None
    return comparar_horas(fecha_completa.time(), hora_teorica)


def comparar_horas(fecha_hora_real_string, hora_completa_teorica):
    formato_hora = "%H:%M:%S"
    minutos_teoricos = int(hora_completa_teorica % 100)
    hora_teorica = int((hora_completa_teorica - minutos_teoricos) / 100)
    datatime_teorico = datetime.strptime(
        str(hora_teorica) + ":" + str(minutos_teoricos) + ":00", formato_hora).time()
    desviacion = hora_a_segundos(
        datatime_teorico) - hora_a_segundos(fecha_hora_real_string)
    if desviacion > 900 or desviacion < -300:
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

# key = codigo_parada, values = [contador,calle 1, calle 2]
lista_paradas_contador = {}

# Recorremos las paradas y nos quedamos con las que pertenecen a las calles elegidas
archivo_paradas = open(ruta_archivo_paradas)
paradas = archivo_paradas.readlines()
paradas = paradas[1:]
for _parada in paradas:
    parada = _parada.split(",")
    nombre_avenida = parada[4]
    calle_2 = parada[5]
    if nombre_avenida in lista_avenidas:
        lista_paradas_contador[int(parada[0])] = [0, nombre_avenida, calle_2]
archivo_paradas.close()

del paradas

# Recorremos los viajes y le sumamos uno al contador de cada parada
archivo_viajes = open(ruta_archivo_viajes)
viajes = archivo_viajes.readlines()
viajes = viajes[1:]
for _viaje in viajes:
    viaje = _viaje.split(",")
    cod_parada = int(viaje[11])
    if cod_parada in lista_paradas_contador.keys():
        lista_paradas_contador[cod_parada][0] += 1
archivo_viajes.close()

del viajes

# key = calle1, values = [contador, calle 2, codigo_parada, desviacion, cantidad_viajes]
lista_paradas_avenida = {}

# Hacer un diccionario donde la key sea la avenida
for parada in lista_paradas_contador.items():
    nombre_avenida = parada[1][1]
    cant_boletos_vendidos = parada[1][0]
    calle_2 = parada[1][2]
    cod_parada = parada[0]
    if nombre_avenida in lista_paradas_avenida:
        lista_paradas_avenida[nombre_avenida].append(
            [cant_boletos_vendidos, calle_2, cod_parada, 0, 0])
    else:
        lista_paradas_avenida[nombre_avenida] = [
            [cant_boletos_vendidos, calle_2, cod_parada, 0, 0]]

del lista_paradas_contador

# Ordenar las paradas por cantidad de boletos vendidos(descendente) y quedarnos con las 15 primeras paradas por cada avenida
for avenida in lista_paradas_avenida.items():
    paradas_en_orden = sorted(avenida[1], key=lambda x: x[0], reverse=True)
    nombre_avenida = avenida[0]
    lista_paradas_avenida[nombre_avenida] = paradas_en_orden[0:15]

# key = codigo_parada, values = [tipo_dia,codigo_omnibus,hora_teorica,calle 1]
lista_horarios_teoricos_parada = {}

# Recorrer los horarios teóricos y quedarnos solo con aquellos que pertenezcan a las paradas relevantes
contador_ceros = 0
cant_horarios_teoricos = 0
archivo_horarios_teoricos = open(ruta_archivo_horarios_teoricos)
horarios_teoricos = archivo_horarios_teoricos.readlines()
horarios_teoricos = horarios_teoricos[1:]
for _horario_teorico in horarios_teoricos:
    horario_teorico = _horario_teorico.split(";")
    if int(horario_teorico[0]) == 0:
        contador_ceros += 1
    cant_horarios_teoricos += 1
    for avenida in lista_paradas_avenida.items():
        paradas_por_avenida = avenida[1]
        for parada in paradas_por_avenida:
            cod_parada = int(horario_teorico[3])
            if cod_parada == parada[2]:
                tipo_dia_teorico = int(horario_teorico[0])
                cod_variante = int(horario_teorico[1])
                horario_teorico = int(horario_teorico[5])
                nombre_avenida = avenida[0]
                if cod_parada in lista_horarios_teoricos_parada:
                    if cod_variante in lista_horarios_teoricos_parada[cod_parada]:
                        lista_horarios_teoricos_parada[cod_parada][cod_variante].append(
                            [tipo_dia_teorico, horario_teorico, nombre_avenida])
                    else:
                        lista_horarios_teoricos_parada[cod_parada][cod_variante] = [
                            [tipo_dia_teorico, horario_teorico, nombre_avenida]]
                else:
                    lista_horarios_teoricos_parada[cod_parada] = {}
                    lista_horarios_teoricos_parada[cod_parada][cod_variante] = [
                        [tipo_dia_teorico, horario_teorico, nombre_avenida]]
                break
archivo_horarios_teoricos.close()

print(contador_ceros)
print(cant_horarios_teoricos)

del horarios_teoricos

archivo_viajes = open(ruta_archivo_viajes)
viajes = archivo_viajes.readlines()
viajes = viajes[1:]
for _viaje in viajes:
    viaje = _viaje.split(",")
    cod_parada = int(viaje[11])
    cod_variante = int(viaje[16])
    if cod_parada in lista_horarios_teoricos_parada:
        if cod_variante in lista_horarios_teoricos_parada[cod_parada]:
            for horario_teorico in lista_horarios_teoricos_parada[cod_parada][cod_variante]:
                horario_real = viaje[2]
                desviacion = comparar_horarios(horario_real, horario_teorico)
                if desviacion != None:
                    for parada in lista_paradas_avenida[lista_horarios_teoricos_parada[cod_parada][cod_variante][0][2]]:
                        if parada[2] == cod_parada:
                            # aca estamos contando todos los boletos que se emiten en una parada
                            parada[3] = (parada[3] * parada[4] +
                                         desviacion) / (parada[4] + 1)
                            parada[4] += 1
                    break
        else:
            print(cod_variante)
archivo_viajes.close()


final = time.time()
print(lista_paradas_avenida)
print(final-comienzo)

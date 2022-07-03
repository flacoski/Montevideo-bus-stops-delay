from ctypes.util import find_library
import multiprocessing as mp
import time
import pdb
import funciones_auxiliares as func

comienzo_tiempo = time.time()
numero_de_procesos = 1
ruta_archivo_viajes = "datos/viajes/viajes_stm_052022.csv"
ruta_archivo_horarios_teoricos = "datos/horariosOmnibus.csv"
ruta_archivo_horarios_teoricos_circulares = "datos/horariosOmnibusCirculares.csv"
ruta_archivo_paradas = "datos/ubicacionParadas/paradas.csv"
ruta_archivo_avenidas = "lista_avenidas"

cola_res = mp.Queue()

lista_avenidas = ["AV GRAL RIVERA"]

# archivo_avenidas=open(ruta_archivo_avenidas)
# filas_avenidas=archivo_avenidas.readlines()
# filas_avenidas=filas_avenidas[1:]
# for fila in filas_avenidas:
#     lista_avenidas.append(fila.rstrip('\n'))
# archivo_avenidas.close()

# key = codigo_parada, values = [contador_viajes,calle 1, calle 2]
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
            [cant_boletos_vendidos, calle_2, cod_parada, 0, 0]
        )
    else:
        lista_paradas_avenida[nombre_avenida] = [
            [cant_boletos_vendidos, calle_2, cod_parada, 0, 0]
        ]

del lista_paradas_contador

# Ordenar las paradas por cantidad de boletos vendidos(descendente) y quedarnos con las 15 primeras paradas por cada avenida
for avenida in lista_paradas_avenida.items():
    paradas_en_orden = sorted(avenida[1], key=lambda x: x[0], reverse=True)
    nombre_avenida = avenida[0]
    lista_paradas_avenida[nombre_avenida] = paradas_en_orden[0:15]

# key = codigo_parada, value = diccionario_parada
# diccionario_parada: key = cod_parada, values = [tipo_dia_teorico, horario_teorico, nombre_avenida]
lista_horarios_teoricos_parada = {}

# Recorrer los horarios teóricos y quedarnos solo con aquellos que pertenezcan a las paradas relevantes
archivo_horarios_teoricos = open(ruta_archivo_horarios_teoricos)
horarios_teoricos = archivo_horarios_teoricos.readlines()
horarios_teoricos = horarios_teoricos[1:]
for _horario_teorico in horarios_teoricos:
    horario_teorico = _horario_teorico.split(";")
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
                            [tipo_dia_teorico, horario_teorico, nombre_avenida]
                        )
                    else:
                        lista_horarios_teoricos_parada[cod_parada][cod_variante] = [
                            [tipo_dia_teorico, horario_teorico, nombre_avenida]
                        ]
                else:
                    lista_horarios_teoricos_parada[cod_parada] = {}
                    lista_horarios_teoricos_parada[cod_parada][cod_variante] = [
                        [tipo_dia_teorico, horario_teorico, nombre_avenida]
                    ]
                break
archivo_horarios_teoricos.close()
del horarios_teoricos

# # Recorrer los horarios teóricos circulares y quedarnos solo con aquellos que pertenezcan a las paradas relevantes
# archivo_horarios_teoricos_circulares = open(ruta_archivo_horarios_teoricos_circulares)
# horarios_teoricos_circulares = archivo_horarios_teoricos_circulares.readlines()
# horarios_teoricos_circulares = horarios_teoricos_circulares[1:]
# for _horario_teorico_circular in horarios_teoricos_circulares:
#     horario_teorico = _horario_teorico_circular.split(";")
#     for avenida in lista_paradas_avenida.items():
#         paradas_por_avenida = avenida[1]
#         for parada in paradas_por_avenida:
#             cod_parada = int(horario_teorico[3])
#             if cod_parada == parada[2]:
#                 tipo_dia_teorico = int(horario_teorico[0])
#                 cod_variante = int(horario_teorico[4])
#                 horario_teorico = int(horario_teorico[7])
#                 nombre_avenida = avenida[0]
#                 if cod_parada in lista_horarios_teoricos_parada:
#                     if cod_variante in lista_horarios_teoricos_parada[cod_parada]:
#                         lista_horarios_teoricos_parada[cod_parada][cod_variante].append(
#                             [tipo_dia_teorico, horario_teorico, nombre_avenida])
#                     else:
#                         lista_horarios_teoricos_parada[cod_parada][cod_variante] = [
#                             [tipo_dia_teorico, horario_teorico, nombre_avenida]]
#                 else:
#                     lista_horarios_teoricos_parada[cod_parada] = {}
#                     lista_horarios_teoricos_parada[cod_parada][cod_variante] = [
#                         [tipo_dia_teorico, horario_teorico, nombre_avenida]]
# archivo_horarios_teoricos.close()
# del horarios_teoricos_circulares


def agregar_desviacion(res_parcial_avenida, nombre_avenida, cod_parada, cod_variante, desviacion, linea_empresa):
    if nombre_avenida in res_parcial_avenida:
        if cod_parada in res_parcial_avenida[nombre_avenida]:
            if (
                cod_variante
                in res_parcial_avenida[nombre_avenida][cod_parada]
            ):
                res_parcial_avenida[nombre_avenida][cod_parada][
                    cod_variante
                ][0] = (
                    res_parcial_avenida[nombre_avenida][cod_parada][
                        cod_variante
                    ][0]
                    * res_parcial_avenida[nombre_avenida][
                        cod_parada
                    ][cod_variante][1]
                    + desviacion
                ) / (
                    res_parcial_avenida[nombre_avenida][cod_parada][
                        cod_variante
                    ][1]
                    + 1
                )
                res_parcial_avenida[nombre_avenida][cod_parada][
                    cod_variante
                ][1] += 1
            else:
                res_parcial_avenida[nombre_avenida][cod_parada][
                    cod_variante
                ] = [
                    desviacion,
                    1,
                    linea_empresa,
                ]  # desviacion,cantidad,linea y empresa
        else:
            res_parcial_avenida[nombre_avenida][cod_parada] = {
            }
            res_parcial_avenida[nombre_avenida][cod_parada][
                cod_variante
            ] = [
                desviacion,
                1,
                linea_empresa,
            ]  # desviacion,cantidad,linea y empresa
    else:
        res_parcial_avenida[nombre_avenida] = {}
        res_parcial_avenida[nombre_avenida][cod_parada] = {
        }
        res_parcial_avenida[nombre_avenida][cod_parada][
            cod_variante
        ] = [
            desviacion,
            1,
            linea_empresa,
        ]  # desviacion,cantidad,linea y empresa


def calcular_frecuencia(horario_teorico, index_horario, lista_horarios):
    print(lista_horarios)
    print(horario_teorico)
    print(index_horario)
    cant_horarios_posteriores = 0
    horarios_cercanos_posteriores = []
    idx_proximo_horario = (index_horario+1) % len(lista_horarios)
    for horario_posterior in lista_horarios[idx_proximo_horario:]:
        if horario_posterior[0] == horario_teorico[0]:
            cant_horarios_posteriores += 1
            horarios_cercanos_posteriores.append(
                func.hora_int_a_datetime(horario_posterior[1]))
        if cant_horarios_posteriores == 2:
            break

    horarios_cercanos_anteriores = []
    cant_horarios_anteriores = 0
    idx_anterior_horario = ((index_horario-1) % len(lista_horarios)) + 1
    for horario_anterior in reversed(lista_horarios[:idx_anterior_horario]):
        if horario_anterior[0] == horario_teorico[0]:
            cant_horarios_anteriores += 1
            horarios_cercanos_anteriores.append(
                func.hora_int_a_datetime(horario_anterior[1]))
            if cant_horarios_anteriores == 1:
                break

    print("cant_horarios_anteriores: ")
    print(cant_horarios_anteriores)
    print("cant_horarios_posteriores: ")
    print(cant_horarios_posteriores)
    print("horarios cercanos: ")
    print(horarios_cercanos)

    return


def calcular_desviacion(viajes, cola):
    res_parcial_avenida = {}
    for _viaje in viajes:
        viaje = _viaje.split(",")
        cod_parada = int(viaje[11])
        cod_variante = int(viaje[16])
        if cod_parada in lista_horarios_teoricos_parada:
            if cod_variante in lista_horarios_teoricos_parada[cod_parada]:
                lista_horarios_teoricos_parada[cod_parada][cod_variante].sort()
                horarios_teoricos_ordenados = sorted(
                    lista_horarios_teoricos_parada[cod_parada][cod_variante], key=lambda x: x[1])
                for index_horario, horario_teorico in enumerate(horarios_teoricos_ordenados):
                    frecuencia = calcular_frecuencia(
                        horario_teorico, index_horario, horarios_teoricos_ordenados)
                    horario_real = viaje[2]
                    desviacion = func.comparar_horarios(
                        horario_real, horario_teorico, frecuencia)
                    if desviacion != None:
                        nombre_avenida = lista_horarios_teoricos_parada[cod_parada][
                            cod_variante
                        ][0][2]
                        linea_empresa = viaje[13] + " " + viaje[15]
                        agregar_desviacion(res_parcial_avenida, nombre_avenida,
                                           cod_parada, cod_variante, desviacion, linea_empresa)
    cola.put(res_parcial_avenida)


archivo_viajes = open(ruta_archivo_viajes)
viajes = archivo_viajes.readlines()
viajes = viajes[1:]
cant_viajes_por_proceso = int(len(viajes) / numero_de_procesos)
procesos = []
for nro_proceso in range(numero_de_procesos):
    comienzo = nro_proceso * cant_viajes_por_proceso
    fin = comienzo + cant_viajes_por_proceso if nro_proceso != numero_de_procesos - \
        1 else len(viajes)
    procesos.append(
        mp.Process(target=calcular_desviacion, args=(
            viajes[comienzo:fin], cola_res))
    )

for p in procesos:
    p.start()

for p in procesos:
    p.join()

archivo_viajes.close()


final_tiempo = time.time()

print(final_tiempo - comienzo_tiempo)

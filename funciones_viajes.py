from itertools import islice, cycle
import funciones_horarios as func_h
from config import *

UNA_HORA = 3600
UN_DIA_EN_SEGUNDOS = 86400
RUTA_ARCHIVO_HORARIOS_TEORICOS_CIRCULARES = "datos/horariosOmnibusCirculares.csv"
RUTA_ARCHIVO_PARADAS = "datos/ubicacionParadas/paradas.csv"
RUTA_ARCHIVO_AVENIDAS = "listaAvenidas"
RUTA_ARCHIVO_HORARIOS_TEORICOS = "datos/horariosOmnibus.csv"
RUTA_ARCHIVO_VIAJES = "datos/viajes/viajes_stm_052022.csv"


def eliminar_outliers(
    horarios_cercanos, cant_horarios_anteriores, cant_horarios_posteriores
):
    index_eliminar = []
    index_horario_original = cant_horarios_anteriores
    horario_original = func_h.hora_a_segundos(horarios_cercanos[index_horario_original])
    if cant_horarios_anteriores > 0:
        for index in range(0, cant_horarios_anteriores):
            actual = func_h.hora_a_segundos(horarios_cercanos[index])
            diferencia = abs(index_horario_original - index)
            if horario_original < actual:
                actual = actual - UN_DIA_EN_SEGUNDOS
            if abs(horario_original - actual) > (UNA_HORA * diferencia):
                index_eliminar.append(index)
    if cant_horarios_posteriores > 0:
        for index in range(cant_horarios_anteriores, len(horarios_cercanos) - 1):
            actual = func_h.hora_a_segundos(horarios_cercanos[index])
            siguiente = func_h.hora_a_segundos(horarios_cercanos[index + 1])
            if actual > siguiente:
                siguiente = siguiente + UN_DIA_EN_SEGUNDOS
            if siguiente - actual > UNA_HORA:
                for index_a_eliminar in range(index + 1, len(horarios_cercanos)):
                    index_eliminar.append(index_a_eliminar)
                break

    index_eliminar.sort()

    for index in reversed(index_eliminar):
        del horarios_cercanos[index]

    return horarios_cercanos


def calcular_frecuencia(horario_teorico, index_horario, lista_horarios):
    horarios_cercanos = []
    largo_lista_horarios = len(lista_horarios)
    tipo_dia_actual = horario_teorico[0]

    cant_horarios_anteriores = 0
    for index, horario_anterior in enumerate(
        islice(
            cycle(reversed(lista_horarios)), largo_lista_horarios - index_horario, None
        )
    ):
        horario_anterior_datetime = func_h.hora_int_a_datetime(horario_anterior[1])
        tipo_dia_anterior = horario_anterior[0]
        if (
            tipo_dia_anterior == tipo_dia_actual
            and horario_anterior_datetime not in horarios_cercanos
            and horario_anterior_datetime
            != func_h.hora_int_a_datetime(horario_teorico[1])
        ):
            cant_horarios_anteriores += 1
            horarios_cercanos.append(horario_anterior_datetime)
        if cant_horarios_anteriores == 1 or index >= largo_lista_horarios:
            break

    horarios_cercanos.append(func_h.hora_int_a_datetime(horario_teorico[1]))

    cant_horarios_posteriores = 0
    for index, horario_posterior in enumerate(
        islice(cycle(lista_horarios), index_horario + 1, None)
    ):
        horario_posterior_datetime = func_h.hora_int_a_datetime(horario_posterior[1])
        tipo_dia_posterior = horario_posterior[0]
        if (
            tipo_dia_posterior == tipo_dia_actual
            and horario_posterior_datetime not in horarios_cercanos
        ):
            cant_horarios_posteriores += 1
            horarios_cercanos.append(horario_posterior_datetime)
        if cant_horarios_posteriores == 2 or index >= largo_lista_horarios - 2:
            break
    horarios_cercanos = eliminar_outliers(
        horarios_cercanos, cant_horarios_anteriores, cant_horarios_posteriores
    )
    return (
        func_h.calcular_promedio_diferencias(horarios_cercanos)
        if len(horarios_cercanos) > 1
        else DEFAULT_FRECUENCIA_EN_SEGUNDOS
    )


def agregar_desviacion_dia_hora(
    res_parcial_avenida,
    nombre_avenida,
    cod_parada,
    desviacion,
    linea_empresa,
    cantidad_viajes,
    dia_de_la_semana,
    franja_horaria,
):
    if nombre_avenida in res_parcial_avenida:
        if (
            cod_parada
            in res_parcial_avenida[nombre_avenida][dia_de_la_semana][franja_horaria]
        ):
            if (
                linea_empresa
                in res_parcial_avenida[nombre_avenida][dia_de_la_semana][
                    franja_horaria
                ][cod_parada]
            ):
                res_parcial_avenida[nombre_avenida][dia_de_la_semana][franja_horaria][
                    cod_parada
                ][linea_empresa][0] = (
                    res_parcial_avenida[nombre_avenida][dia_de_la_semana][
                        franja_horaria
                    ][cod_parada][linea_empresa][0]
                    * res_parcial_avenida[nombre_avenida][dia_de_la_semana][
                        franja_horaria
                    ][cod_parada][linea_empresa][1]
                    + desviacion * cantidad_viajes
                ) / (
                    res_parcial_avenida[nombre_avenida][dia_de_la_semana][
                        franja_horaria
                    ][cod_parada][linea_empresa][1]
                    + cantidad_viajes
                )
                res_parcial_avenida[nombre_avenida][dia_de_la_semana][franja_horaria][
                    cod_parada
                ][linea_empresa][1] += cantidad_viajes
            else:
                res_parcial_avenida[nombre_avenida][dia_de_la_semana][franja_horaria][
                    cod_parada
                ][linea_empresa] = [
                    desviacion,
                    cantidad_viajes,
                ]  # desviacion,cantidad viajes,nombre interseccion
        else:
            res_parcial_avenida[nombre_avenida][dia_de_la_semana][franja_horaria][
                cod_parada
            ] = {}
            res_parcial_avenida[nombre_avenida][dia_de_la_semana][franja_horaria][
                cod_parada
            ][linea_empresa] = [
                desviacion,
                cantidad_viajes,
            ]  # desviacion,cantidad viajes,nombre interseccion
    else:
        res_parcial_avenida[nombre_avenida] = {}
        dias = [
            "Semana",
            "Fin de Semana",
        ]
        franjas = ["Horas pico 7-9,12-14,16-19", "Horas tranquilas", "Madrugada 0-6"]
        for dia in dias:
            res_parcial_avenida[nombre_avenida][dia] = {}
            for franja in franjas:
                res_parcial_avenida[nombre_avenida][dia][franja] = {}
        res_parcial_avenida[nombre_avenida][dia_de_la_semana][franja_horaria][
            cod_parada
        ] = {}
        res_parcial_avenida[nombre_avenida][dia_de_la_semana][franja_horaria][
            cod_parada
        ][linea_empresa] = [
            desviacion,
            cantidad_viajes,
        ]  # desviacion,cantidad viajes,nombre interseccion
    return res_parcial_avenida


def obtener_avenidas():
    lista_avenidas = []
    archivo_avenidas = open(RUTA_ARCHIVO_AVENIDAS)
    filas_avenidas = archivo_avenidas.readlines()
    for fila in filas_avenidas:
        lista_avenidas.append(fila.rstrip("\n"))
    archivo_avenidas.close()
    return lista_avenidas


def obtener_paradas_avenida(lista_avenidas):
    # key = codigo_parada, values = [contador_viajes,calle 1, calle 2]
    lista_paradas_contador = {}

    # Recorremos las paradas y nos quedamos con las que pertenecen a las calles elegidas
    archivo_paradas = open(RUTA_ARCHIVO_PARADAS)
    paradas = archivo_paradas.readlines()
    paradas = paradas[1:]
    for _parada in paradas:
        parada = _parada.split(",")
        nombre_avenida = parada[4]
        calle_2 = parada[5]
        if nombre_avenida in lista_avenidas:
            lista_paradas_contador[int(parada[0])] = [0, nombre_avenida, calle_2]
    archivo_paradas.close()

    # Recorremos los viajes y le sumamos uno al contador de cada parada
    archivo_viajes = open(RUTA_ARCHIVO_VIAJES)
    viajes = archivo_viajes.readlines()
    viajes = viajes[1:]
    for _viaje in viajes:
        viaje = _viaje.split(",")
        cod_parada = int(viaje[11])
        if cod_parada in lista_paradas_contador.keys():
            lista_paradas_contador[cod_parada][0] += 1
    archivo_viajes.close()

    return lista_paradas_contador

def obtener_paradas_avenida_coordenada(lista_avenidas):
    # key = codigo_parada, values = [contador_viajes,calle 1, calle 2]
    lista_paradas_contador = {}

    # Recorremos las paradas y nos quedamos con las que pertenecen a las calles elegidas
    archivo_paradas = open(RUTA_ARCHIVO_PARADAS)
    paradas = archivo_paradas.readlines()
    paradas = paradas[1:]
    for _parada in paradas:
        parada = _parada.split(",")
        nombre_avenida = parada[4]
        # calle_2 = parada[5]
        coord1 = parada[8]
        coord2 = parada[9].replace("\n", "")
        if nombre_avenida in lista_avenidas:
            lista_paradas_contador[int(parada[0])] = [coord1,coord2]
    archivo_paradas.close()

    return lista_paradas_contador


def obtener_paradas_mas_vendidas(lista_paradas_contador):
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

    # Ordenar las paradas por cantidad de boletos vendidos(descendente) y quedarnos con las NUMERO_PARADAS_MAS_VENDIDAS primeras paradas por cada avenida
    for avenida in lista_paradas_avenida.items():
        paradas_en_orden = sorted(avenida[1], key=lambda x: x[0], reverse=True)
        nombre_avenida = avenida[0]
        lista_paradas_avenida[nombre_avenida] = paradas_en_orden[0:NUMERO_PARADAS_MAS_VENDIDAS]

    return lista_paradas_avenida


def obtener_horarios_teoricos(lista_paradas_avenida):
    # key = codigo_parada, value = diccionario_parada
    # diccionario_parada: key = cod_parada, values = [tipo_dia_teorico, horario_teorico, nombre_avenida, nombre_interseccion]
    lista_horarios_teoricos_parada = {}

    # Recorrer los horarios teóricos y quedarnos solo con aquellos que pertenezcan a las paradas relevantes
    archivo_horarios_teoricos = open(RUTA_ARCHIVO_HORARIOS_TEORICOS)
    horarios_teoricos = archivo_horarios_teoricos.readlines()
    horarios_teoricos = horarios_teoricos[1:]
    for _horario_teorico in horarios_teoricos:
        horario_teorico = _horario_teorico.split(";")
        salir = False
        for avenida in lista_paradas_avenida.items():
            paradas_por_avenida = avenida[1]
            for parada in paradas_por_avenida:
                cod_parada = int(horario_teorico[3])
                if cod_parada == parada[2]:
                    salir = True
                    tipo_dia_teorico = int(horario_teorico[0])
                    cod_variante = int(horario_teorico[1])
                    horario_teorico_aux = int(horario_teorico[5])
                    nombre_avenida = avenida[0]
                    nombre_interseccion = parada[1]
                    if cod_parada in lista_horarios_teoricos_parada:
                        if cod_variante in lista_horarios_teoricos_parada[cod_parada]:
                            lista_horarios_teoricos_parada[cod_parada][
                                cod_variante
                            ].append(
                                [
                                    tipo_dia_teorico,
                                    horario_teorico_aux,
                                    nombre_avenida,
                                    nombre_interseccion,
                                ]
                            )
                        else:
                            lista_horarios_teoricos_parada[cod_parada][cod_variante] = [
                                [
                                    tipo_dia_teorico,
                                    horario_teorico_aux,
                                    nombre_avenida,
                                    nombre_interseccion,
                                ]
                            ]
                    else:
                        lista_horarios_teoricos_parada[cod_parada] = {}
                        lista_horarios_teoricos_parada[cod_parada][cod_variante] = [
                            [
                                tipo_dia_teorico,
                                horario_teorico_aux,
                                nombre_avenida,
                                nombre_interseccion,
                            ]
                        ]
                    break
            if salir:
                break
    archivo_horarios_teoricos.close()

    # Recorrer los horarios teóricos circulares y quedarnos solo con aquellos que pertenezcan a las paradas relevantes
    archivo_horarios_teoricos_circulares = open(
        RUTA_ARCHIVO_HORARIOS_TEORICOS_CIRCULARES
    )
    horarios_teoricos_circulares = archivo_horarios_teoricos_circulares.readlines()
    horarios_teoricos_circulares = horarios_teoricos_circulares[1:]
    for _horario_teorico_circular in horarios_teoricos_circulares:
        horario_teorico = _horario_teorico_circular.split(";")
        salir = False
        for avenida in lista_paradas_avenida.items():
            paradas_por_avenida = avenida[1]
            for parada in paradas_por_avenida:
                cod_parada = int(horario_teorico[3])
                if cod_parada == parada[2]:
                    salir = True
                    tipo_dia_teorico = int(horario_teorico[0])
                    cod_variante = int(horario_teorico[4])
                    horario_teorico_aux = int(horario_teorico[7])
                    nombre_avenida = avenida[0]
                    nombre_interseccion = parada[1]
                    if cod_parada in lista_horarios_teoricos_parada:
                        if cod_variante in lista_horarios_teoricos_parada[cod_parada]:
                            lista_horarios_teoricos_parada[cod_parada][
                                cod_variante
                            ].append(
                                [
                                    tipo_dia_teorico,
                                    horario_teorico_aux,
                                    nombre_avenida,
                                    nombre_interseccion,
                                ]
                            )
                        else:
                            lista_horarios_teoricos_parada[cod_parada][cod_variante] = [
                                [
                                    tipo_dia_teorico,
                                    horario_teorico_aux,
                                    nombre_avenida,
                                    nombre_interseccion,
                                ]
                            ]
                    else:
                        lista_horarios_teoricos_parada[cod_parada] = {}
                        lista_horarios_teoricos_parada[cod_parada][cod_variante] = [
                            [
                                tipo_dia_teorico,
                                horario_teorico_aux,
                                nombre_avenida,
                                nombre_interseccion,
                            ]
                        ]
                    break
        if salir:
            break
    archivo_horarios_teoricos.close()

    return lista_horarios_teoricos_parada


def calcular_frecuencias(lista_horarios_teoricos_parada):
    # calcular la frecuencia para cada horario teórico
    for parada in lista_horarios_teoricos_parada:
        for variante in lista_horarios_teoricos_parada[parada]:
            lista_horarios_teoricos_parada[parada][variante].sort()
            horarios_teoricos_ordenados = sorted(
                lista_horarios_teoricos_parada[parada][variante],
                key=lambda x: x[1],
            )
            for index_horario, horario_teorico in enumerate(
                horarios_teoricos_ordenados
            ):
                frecuencia = calcular_frecuencia(
                    horario_teorico, index_horario, horarios_teoricos_ordenados
                )
                horario_teorico.append(frecuencia)


def calcular_desviacion_por_dia_hora(viajes, lista_horarios_teoricos_parada, cola_res):
    res_parcial = {}
    for _viaje in viajes:
        viaje = _viaje.split(",")
        cod_parada = int(viaje[11])
        cod_variante = int(viaje[16])
        if cod_parada in lista_horarios_teoricos_parada:
            if cod_variante in lista_horarios_teoricos_parada[cod_parada]:
                for horario_teorico in lista_horarios_teoricos_parada[cod_parada][
                    cod_variante
                ]:
                    frecuencia = horario_teorico[4]
                    horario_real = viaje[2]
                    desviacion = func_h.comparar_horarios(
                        horario_real, horario_teorico, frecuencia, DEFAULT_MARGEN
                    )
                    if desviacion != None:
                        nombre_interseccion = horario_teorico[3]
                        dia_de_la_semana = func_h.obtener_dia_semana(horario_real)
                        franja_horaria = func_h.obtener_franja_horaria(horario_real)
                        nombre_avenida = horario_teorico[2]
                        linea_empresa = viaje[13] + " " + viaje[15]
                        res_parcial = agregar_desviacion_dia_hora(
                            res_parcial,
                            nombre_avenida,
                            str(cod_parada) + " " + nombre_interseccion,
                            desviacion,
                            linea_empresa,
                            1,
                            dia_de_la_semana,
                            franja_horaria,
                        )
                        break
    cola_res.put(res_parcial)

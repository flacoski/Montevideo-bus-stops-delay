from ctypes.util import find_library
import multiprocessing as mp
import time
import funciones_auxiliares as func

NUMERO_DE_PROCESOS = 8
RUTA_ARCHIVO_VIAJES = "datos/viajes/viajes_stm_052022.csv"
RUTA_ARCHIVO_HORARIOS_TEORICOS = "datos/horariosOmnibus.csv"
RUTA_ARCHIVO_HORARIOS_TEORICOS_CIRCULARES = "datos/horariosOmnibusCirculares.csv"
RUTA_ARCHIVO_PARADAS = "datos/ubicacionParadas/paradas.csv"
RUTA_ARCHIVO_AVENIDAS = "listaAvenidas"
DEFAULT_MARGEN = 2 / 3


def obtener_avenidas():
    lista_avenidas = []
    archivo_avenidas = open(RUTA_ARCHIVO_AVENIDAS)
    filas_avenidas = archivo_avenidas.readlines()
    filas_avenidas = filas_avenidas[1:]
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

    # Ordenar las paradas por cantidad de boletos vendidos(descendente) y quedarnos con las 15 primeras paradas por cada avenida
    for avenida in lista_paradas_avenida.items():
        paradas_en_orden = sorted(avenida[1], key=lambda x: x[0], reverse=True)
        nombre_avenida = avenida[0]
        lista_paradas_avenida[nombre_avenida] = paradas_en_orden[0:15]

    return lista_paradas_avenida


def obtener_horarios_teoricos(lista_paradas_avenida):
    # key = codigo_parada, value = diccionario_parada
    # diccionario_parada: key = cod_parada, values = [tipo_dia_teorico, horario_teorico, nombre_avenida]
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
                    if cod_parada in lista_horarios_teoricos_parada:
                        if cod_variante in lista_horarios_teoricos_parada[cod_parada]:
                            lista_horarios_teoricos_parada[cod_parada][
                                cod_variante
                            ].append(
                                [tipo_dia_teorico, horario_teorico_aux, nombre_avenida]
                            )
                        else:
                            lista_horarios_teoricos_parada[cod_parada][cod_variante] = [
                                [tipo_dia_teorico, horario_teorico_aux, nombre_avenida]
                            ]
                    else:
                        lista_horarios_teoricos_parada[cod_parada] = {}
                        lista_horarios_teoricos_parada[cod_parada][cod_variante] = [
                            [tipo_dia_teorico, horario_teorico_aux, nombre_avenida]
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
                    if cod_parada in lista_horarios_teoricos_parada:
                        if cod_variante in lista_horarios_teoricos_parada[cod_parada]:
                            lista_horarios_teoricos_parada[cod_parada][
                                cod_variante
                            ].append(
                                [tipo_dia_teorico, horario_teorico_aux, nombre_avenida]
                            )
                        else:
                            lista_horarios_teoricos_parada[cod_parada][cod_variante] = [
                                [tipo_dia_teorico, horario_teorico_aux, nombre_avenida]
                            ]
                    else:
                        lista_horarios_teoricos_parada[cod_parada] = {}
                        lista_horarios_teoricos_parada[cod_parada][cod_variante] = [
                            [tipo_dia_teorico, horario_teorico_aux, nombre_avenida]
                        ]
                    break
        if salir:
            break
    archivo_horarios_teoricos.close()

    return lista_horarios_teoricos_parada


def calcular_frecuencia(lista_horarios_teoricos_parada):
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
                frecuencia = func.calcular_frecuencia(
                    horario_teorico, index_horario, horarios_teoricos_ordenados
                )
                horario_teorico.append(frecuencia)


def calcular_desviacion(viajes, lista_horarios_teoricos_parada, cola_res):
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
                    frecuencia = horario_teorico[3]
                    horario_real = viaje[2]
                    desviacion = func.comparar_horarios(
                        horario_real, horario_teorico, frecuencia, DEFAULT_MARGEN
                    )
                    if desviacion != None:
                        nombre_avenida = lista_horarios_teoricos_parada[cod_parada][
                            cod_variante
                        ][0][2]
                        linea_empresa = viaje[13] + " " + viaje[15]
                        res_parcial = func.agregar_desviacion(
                            res_parcial,
                            nombre_avenida,
                            cod_parada,
                            desviacion,
                            linea_empresa,
                            1,
                        )
                        break
    cola_res.put(res_parcial)


if __name__ == "__main__":
    comienzo_tiempo = time.time()
    lista_avenidas = ["AV GRAL RIVERA"]
    lista_paradas_contador = obtener_paradas_avenida(lista_avenidas)
    lista_paradas_avenida = obtener_paradas_mas_vendidas(lista_paradas_contador)
    del lista_paradas_contador
    lista_horarios_teoricos_parada = obtener_horarios_teoricos(lista_paradas_avenida)
    del lista_paradas_avenida
    calcular_frecuencia(lista_horarios_teoricos_parada)

    archivo_viajes = open(RUTA_ARCHIVO_VIAJES)
    viajes = archivo_viajes.readlines()
    archivo_viajes.close()
    viajes = viajes[1:]
    cant_viajes_por_proceso = int(len(viajes) / NUMERO_DE_PROCESOS)
    procesos = []
    cola_res = mp.Queue()
    for nro_proceso in range(NUMERO_DE_PROCESOS):
        comienzo = nro_proceso * cant_viajes_por_proceso
        fin = (
            comienzo + cant_viajes_por_proceso
            if nro_proceso != NUMERO_DE_PROCESOS - 1
            else len(viajes)
        )
        procesos.append(
            mp.Process(
                target=calcular_desviacion, args=(viajes[comienzo:fin], lista_horarios_teoricos_parada, cola_res)
            )
        )

    for p in procesos:
        p.start()

    resultado_final = {}
    for p in procesos:
        resultado = cola_res.get()
        for avenida in resultado.items():
            nombre_avenida = avenida[0]
            for parada in resultado[nombre_avenida].items():
                cod_parada = parada[0]
                for linea_empresa in resultado[nombre_avenida][cod_parada].items():
                    linea_empresa_id = linea_empresa[0]
                    desviacion = linea_empresa[1][0]
                    cantidad_viajes = linea_empresa[1][1]
                    resultado_final = func.agregar_desviacion(
                        resultado_final,
                        nombre_avenida,
                        cod_parada,
                        desviacion,
                        linea_empresa_id,
                        cantidad_viajes,
                    )

    print(resultado_final)
    final_tiempo = time.time()
    print(final_tiempo - comienzo_tiempo)
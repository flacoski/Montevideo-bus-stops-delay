import multiprocessing as mp
import time
import funciones_viajes as func_v

NUMERO_DE_PROCESOS = 6
RUTA_ARCHIVO_VIAJES = "datos/viajes/viajes_stm_052022.csv"

if __name__ == "__main__":
    comienzo_tiempo = time.time()
    lista_avenidas = ["AV GRAL RIVERA"]
    lista_paradas_contador = func_v.obtener_paradas_avenida(lista_avenidas)
    lista_paradas_avenida = func_v.obtener_paradas_mas_vendidas(
        lista_paradas_contador)
    del lista_paradas_contador
    lista_horarios_teoricos_parada = func_v.obtener_horarios_teoricos(
        lista_paradas_avenida)
    del lista_paradas_avenida
    func_v.calcular_frecuencias(lista_horarios_teoricos_parada)

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
                target=func_v.calcular_desviacion_por_dia_hora,
                args=(viajes[comienzo:fin],
                      lista_horarios_teoricos_parada, cola_res),
            )
        )

    for p in procesos:
        p.start()

    resultado_final = {}
    for p in procesos:
        resultado = cola_res.get()
        for avenida in resultado.items():
            nombre_avenida = avenida[0]
            for dia in resultado[nombre_avenida].items():
                tipo_dia = dia[0]
                for franja in resultado[nombre_avenida][tipo_dia].items():
                    franja_horaria = franja[0]
                    for parada in resultado[nombre_avenida][tipo_dia][
                        franja_horaria
                    ].items():
                        cod_parada = parada[0]
                        for linea_empresa in resultado[nombre_avenida][tipo_dia][
                            franja_horaria
                        ][cod_parada].items():
                            linea_empresa_id = linea_empresa[0]
                            desviacion = linea_empresa[1][0]
                            cantidad_viajes = linea_empresa[1][1]
                            resultado_final = func_v.agregar_desviacion_dia_hora(
                                resultado_final,
                                nombre_avenida,
                                cod_parada,
                                desviacion,
                                linea_empresa_id,
                                cantidad_viajes,
                                tipo_dia,
                                franja_horaria,
                            )

    print(resultado_final)
    final_tiempo = time.time()
    print(final_tiempo - comienzo_tiempo)

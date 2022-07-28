import multiprocessing as mp
import pdb
import time
import funciones_viajes as func_v
import estadisticas
import json
from config import *

RUTAS_ARCHIVO_VIAJES = [
    "datos/viajes/viajes_stm_032022.csv",
    "datos/viajes/viajes_stm_042022.csv",
    "datos/viajes/viajes_stm_052022.csv",
]

if __name__ == "__main__":
    comienzo_tiempo = time.time()
    lista_avenidas = func_v.obtener_avenidas()
    lista_paradas_contador = func_v.obtener_paradas_avenida(lista_avenidas)
    lista_paradas_avenida = func_v.obtener_paradas_mas_vendidas(lista_paradas_contador)
    del lista_paradas_contador
    lista_horarios_teoricos_parada = func_v.obtener_horarios_teoricos(
        lista_paradas_avenida
    )
    del lista_paradas_avenida
    func_v.calcular_frecuencias(lista_horarios_teoricos_parada)

    resultado_final = {}

    viajes =[]

    if NUMERO_DE_PROCESOS >= 8:
        viajes =[]
        for ruta_archivo in RUTAS_ARCHIVO_VIAJES:
            archivo_viajes = open(ruta_archivo)
            viajes_aux = archivo_viajes.readlines()
            archivo_viajes.close()
            viajes_aux = viajes_aux[1:]
            viajes.append(viajes_aux)
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
                    args=(
                        viajes[comienzo:fin],
                        lista_horarios_teoricos_parada,
                        cola_res,
                    ),
                )
            )

        for p in procesos:
            p.start()

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
    else:
        for ruta_archivo in RUTAS_ARCHIVO_VIAJES:
            archivo_viajes = open(ruta_archivo)
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
                        args=(
                            viajes[comienzo:fin],
                            lista_horarios_teoricos_parada,
                            cola_res,
                        ),
                    )
                )

            for p in procesos:
                p.start()

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

    f = open("resultados/resultado_final", "w")
    f.write(json.dumps(resultado_final))
    f.close()

    f = open("resultados/estadisticas", "w")
    f.write("desviaciones promedio horas picos vs horas tranquilas en la semana: \n")
    f.write(
        json.dumps(estadisticas.horas_picos_vs_tranquilas_en_semana(resultado_final))
    )
    f.write("\n")
    f.write("desviaciones promedios semana vs fin de semana: \n")
    f.write(json.dumps(estadisticas.semana_vs_findes(resultado_final)))
    f.write("\n")
    f.write("comparativa de desviaciones de linea en avenidas:\n")
    f.write(
        json.dumps(
            estadisticas.comparativa_linea_avenidas(
                resultado_final, LINEA_OMNIBUS_ANALISIS
            )
        )
    )
    f.write("\n")
    f.write("porcentajes de demoras significativas por avenida: \n")
    f.write(json.dumps(estadisticas.porcentaje_demoras_significativas(resultado_final)))
    f.write("\n")

    final_tiempo = time.time()
    print("El tiempo de ejecución es: ", final_tiempo - comienzo_tiempo, "s")

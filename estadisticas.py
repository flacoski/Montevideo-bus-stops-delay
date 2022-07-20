from config import *


def horas_picos_vs_tranquilas_en_semana(resultado_final):
    resultado = {}
    for avenida in resultado_final.items():
        nombre_avenida = avenida[0]
        resultado[nombre_avenida] = {
            "Horas pico 7-9,12-14,16-19": [0, 0],
            "Horas tranquilas": [0, 0],
        }
        for franja_h in resultado_final[nombre_avenida]["Semana"].items():
            franja = franja_h[0]
            if franja == "Madrugada":
                continue
            for parada in resultado_final[nombre_avenida]["Semana"][franja].items():
                cod_parada = parada[0]
                for linea in resultado_final[nombre_avenida]["Semana"][franja][
                    cod_parada
                ].items():
                    cod_linea = linea[0]
                    actual_desviacion = resultado[nombre_avenida][franja][0]
                    actual_viajes = resultado[nombre_avenida][franja][1]
                    nueva_desviacion = linea[1][0]
                    nuevos_viajes = linea[1][1]
                    resultado[nombre_avenida][franja][0] = (
                        actual_desviacion * actual_viajes
                        + nueva_desviacion * nuevos_viajes
                    ) / (actual_viajes + nuevos_viajes)
                    resultado[nombre_avenida][franja][1] += nuevos_viajes
    return resultado


def semana_vs_findes(resultado_final):
    resultado = {}
    for avenida in resultado_final.items():
        nombre_avenida = avenida[0]
        resultado[nombre_avenida] = {"Semana": [0, 0], "Fin de Semana": [0, 0]}
        for dia in resultado_final[nombre_avenida].items():
            tipo_dia = dia[0]
            for franja_h in resultado_final[nombre_avenida][tipo_dia].items():
                franja = franja_h[0]
                if franja == "Madrugada":
                    continue
                for parada in resultado_final[nombre_avenida][tipo_dia][franja].items():
                    cod_parada = parada[0]
                    for linea in resultado_final[nombre_avenida][tipo_dia][franja][
                        cod_parada
                    ].items():
                        cod_linea = linea[0]
                        actual_desviacion = resultado[nombre_avenida][tipo_dia][0]
                        actual_viajes = resultado[nombre_avenida][tipo_dia][1]
                        nueva_desviacion = linea[1][0]
                        nuevos_viajes = linea[1][1]
                        resultado[nombre_avenida][tipo_dia][0] = (
                            actual_desviacion * actual_viajes
                            + nueva_desviacion * nuevos_viajes
                        ) / (actual_viajes + nuevos_viajes)
                        resultado[nombre_avenida][tipo_dia][1] += nuevos_viajes
    return resultado


def comparativa_linea_avenidas(resultado_final, linea_objetivo):
    resultado = {}
    for avenida in resultado_final.items():
        nombre_avenida = avenida[0]
        resultado[nombre_avenida] = [0, 0]
        for dia in resultado_final[nombre_avenida].items():
            tipo_dia = dia[0]
            for franja_h in resultado_final[nombre_avenida][tipo_dia].items():
                franja = franja_h[0]
                if franja == "Madrugada":
                    continue
                for parada in resultado_final[nombre_avenida][tipo_dia][franja].items():
                    cod_parada = parada[0]
                    for linea in resultado_final[nombre_avenida][tipo_dia][franja][
                        cod_parada
                    ].items():
                        cod_linea = linea[0]
                        if cod_linea == linea_objetivo:
                            actual_desviacion = resultado[nombre_avenida][0]
                            actual_viajes = resultado[nombre_avenida][1]
                            nueva_desviacion = linea[1][0]
                            nuevos_viajes = linea[1][1]
                            resultado[nombre_avenida][0] = (
                                actual_desviacion * actual_viajes
                                + nueva_desviacion * nuevos_viajes
                            ) / (actual_viajes + nuevos_viajes)
                            resultado[nombre_avenida][1] += nuevos_viajes
    return resultado


def porcentaje_demoras_significativas(resultado_final):
    resultado = {}
    for avenida in resultado_final.items():
        nombre_avenida = avenida[0]
        resultado[nombre_avenida] = [0, 0]
        for dia in resultado_final[nombre_avenida].items():
            tipo_dia = dia[0]
            for franja_h in resultado_final[nombre_avenida][tipo_dia].items():
                franja = franja_h[0]
                if franja == "Madrugada":
                    continue
                for parada in resultado_final[nombre_avenida][tipo_dia][franja].items():
                    cod_parada = parada[0]
                    for linea in resultado_final[nombre_avenida][tipo_dia][franja][
                        cod_parada
                    ].items():
                        nueva_desviacion = linea[1][0]
                        nuevos_viajes = linea[1][1]
                        if (
                            nueva_desviacion > DESVIACION_POS_SIGNIFICATIVA_SEGUNDOS
                            or nueva_desviacion < DESVIACION_NEG_SIGNIFICATIVA_SEGUNDOS
                        ):
                            resultado[nombre_avenida][0] += nuevos_viajes
                        resultado[nombre_avenida][1] += nuevos_viajes
    return resultado

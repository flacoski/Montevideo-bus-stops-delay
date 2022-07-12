import datetime
from itertools import islice, cycle

UNA_HORA = 3600
UN_DIA_EN_SEGUNDOS = 86400
DEFAULT_FRECUENCIA_EN_SEGUNDOS = 900
VEINTITRES_HORAS = 82800

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


def comparar_horarios(horario_real, horario_teorico, frecuencia, margen):
    tipo_dia_teorico = horario_teorico[0]
    hora_teorica = horario_teorico[1]
    formato_fecha = "%Y-%m-%dT%H:%M:%S.%f%z"
    fecha_completa = datetime.datetime.strptime(horario_real, formato_fecha)
    # caso borde entre tipos de dia
    if tipo_dia(fecha_completa.date()) != tipo_dia_teorico:
        return None
    return comparar_horas(fecha_completa.time(), hora_teorica, frecuencia, margen)


def comparar_horas(fecha_hora_real_string, hora_completa_teorica, frecuencia, margen):
    hora_teorica_en_segundos = hora_a_segundos(
        hora_int_a_datetime(hora_completa_teorica)
    )
    hora_real_en_segundos = hora_a_segundos(fecha_hora_real_string)
    if hora_real_en_segundos > VEINTITRES_HORAS and hora_teorica_en_segundos < UNA_HORA:
        hora_teorica_en_segundos += UN_DIA_EN_SEGUNDOS
    elif (
        hora_teorica_en_segundos > VEINTITRES_HORAS and hora_real_en_segundos < UNA_HORA
    ):
        hora_real_en_segundos += UN_DIA_EN_SEGUNDOS
    desviacion = hora_real_en_segundos - hora_teorica_en_segundos
    if desviacion > frecuencia * margen or desviacion < -frecuencia * (1 - margen):
        return None
    else:
        return desviacion


def hora_int_a_datetime(hora_int):
    formato_hora = "%H:%M:%S"
    minutos_teoricos = int(hora_int % 100)
    hora_teorica = int((hora_int - minutos_teoricos) / 100)
    return datetime.datetime.strptime(
        str(hora_teorica) + ":" + str(minutos_teoricos) + ":00", formato_hora
    ).time()


def hora_a_segundos(hora_datetime):
    return (hora_datetime.hour * 60 + hora_datetime.minute) * 60 + hora_datetime.second


def calcular_promedio_diferencias(lista_horarios):
    largo_lista_horarios = len(lista_horarios)
    suma_diferencias = 0
    for index in range(0, largo_lista_horarios - 1):
        index_siguiente = index + 1
        actual = hora_a_segundos(lista_horarios[index])
        siguiente = hora_a_segundos(lista_horarios[index_siguiente])
        if siguiente < actual:
            actual = actual - UN_DIA_EN_SEGUNDOS
        suma_diferencias += abs(siguiente - actual)
    return suma_diferencias / (largo_lista_horarios - 1)


def eliminar_outliers(
    horarios_cercanos, cant_horarios_anteriores, cant_horarios_posteriores
):
    index_eliminar = []
    index_horario_original = cant_horarios_anteriores
    horario_original = hora_a_segundos(horarios_cercanos[index_horario_original])
    if cant_horarios_anteriores > 0:
        for index in range(0, cant_horarios_anteriores):
            actual = hora_a_segundos(horarios_cercanos[index])
            diferencia = abs(index_horario_original - index)
            if horario_original < actual:
                actual = actual - UN_DIA_EN_SEGUNDOS
            if abs(horario_original - actual) > (UNA_HORA * diferencia):
                index_eliminar.append(index)
    if cant_horarios_posteriores > 0:
        for index in range(cant_horarios_anteriores, len(horarios_cercanos) - 1):
            actual = hora_a_segundos(horarios_cercanos[index])
            siguiente = hora_a_segundos(horarios_cercanos[index + 1])
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
        horario_anterior_datetime = hora_int_a_datetime(horario_anterior[1])
        tipo_dia_anterior = horario_anterior[0]
        if (
            tipo_dia_anterior == tipo_dia_actual
            and horario_anterior_datetime not in horarios_cercanos
            and horario_anterior_datetime != hora_int_a_datetime(horario_teorico[1])
        ):
            cant_horarios_anteriores += 1
            horarios_cercanos.append(horario_anterior_datetime)
        if cant_horarios_anteriores == 1 or index >= largo_lista_horarios:
            break

    horarios_cercanos.append(hora_int_a_datetime(horario_teorico[1]))

    cant_horarios_posteriores = 0
    for index, horario_posterior in enumerate(
        islice(cycle(lista_horarios), index_horario + 1, None)
    ):
        horario_posterior_datetime = hora_int_a_datetime(horario_posterior[1])
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
        calcular_promedio_diferencias(horarios_cercanos)
        if len(horarios_cercanos) > 1
        else DEFAULT_FRECUENCIA_EN_SEGUNDOS
    )

def agregar_desviacion(
    res_parcial_avenida,
    nombre_avenida,
    cod_parada,
    desviacion,
    linea_empresa,
    cantidad_viajes,
):
    if nombre_avenida in res_parcial_avenida:
        if cod_parada in res_parcial_avenida[nombre_avenida]:
            if linea_empresa in res_parcial_avenida[nombre_avenida][cod_parada]:
                res_parcial_avenida[nombre_avenida][cod_parada][linea_empresa][0] = (
                    res_parcial_avenida[nombre_avenida][cod_parada][linea_empresa][0]
                    * res_parcial_avenida[nombre_avenida][cod_parada][linea_empresa][1]
                    + desviacion
                ) / (
                    res_parcial_avenida[nombre_avenida][cod_parada][linea_empresa][1]
                    + cantidad_viajes
                )
                res_parcial_avenida[nombre_avenida][cod_parada][linea_empresa][
                    1
                ] += cantidad_viajes
            else:
                res_parcial_avenida[nombre_avenida][cod_parada][linea_empresa] = [
                    desviacion,
                    cantidad_viajes,
                ]  # desviacion,cantidad viajes
        else:
            res_parcial_avenida[nombre_avenida][cod_parada] = {}
            res_parcial_avenida[nombre_avenida][cod_parada][linea_empresa] = [
                desviacion,
                cantidad_viajes,
            ]  # desviacion,cantidad viajes
    else:
        res_parcial_avenida[nombre_avenida] = {}
        res_parcial_avenida[nombre_avenida][cod_parada] = {}
        res_parcial_avenida[nombre_avenida][cod_parada][linea_empresa] = [
            desviacion,
            cantidad_viajes,
        ]  # desviacion,cantidad viajes
    return res_parcial_avenida

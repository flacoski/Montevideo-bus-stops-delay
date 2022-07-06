from datetime import datetime
from itertools import islice, cycle

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
    fecha_completa = datetime.strptime(horario_real, formato_fecha)
    # caso borde entre tipos de dia
    if tipo_dia(fecha_completa.date()) != tipo_dia_teorico:
        return None
    return comparar_horas(fecha_completa.time(), hora_teorica, frecuencia, margen)


def comparar_horas(fecha_hora_real_string, hora_completa_teorica, frecuencia, margen):
    teo = hora_a_segundos(hora_int_a_datetime(hora_completa_teorica))
    real = hora_a_segundos(fecha_hora_real_string)
    if teo < real:
        real = real - 86400
    desviacion = teo - real
    if desviacion > frecuencia * margen or desviacion < -frecuencia * (1 - margen):
        return None
    else:
        return desviacion


def hora_int_a_datetime(hora_int):
    formato_hora = "%H:%M:%S"
    minutos_teoricos = int(hora_int % 100)
    hora_teorica = int((hora_int - minutos_teoricos) / 100)
    return datetime.strptime(
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
            actual = actual - 86400
        suma_diferencias += abs(siguiente - actual)
    return suma_diferencias / largo_lista_horarios


def calcular_frecuencia(horario_teorico, index_horario, lista_horarios):
    horarios_cercanos = []
    largo_lista_horarios = len(lista_horarios)

    cant_horarios_anteriores = 0
    idx_anterior_horario = largo_lista_horarios - index_horario
    cont = 0
    for horario_anterior in islice(
        cycle(reversed(lista_horarios)), idx_anterior_horario, None
    ):
        cont += 1
        if horario_anterior[0] == horario_teorico[0]:
            cant_horarios_anteriores += 1
            horarios_cercanos.append(hora_int_a_datetime(horario_anterior[1]))
            if cant_horarios_anteriores == 1 or cont == 10000:
                break

    horarios_cercanos.append(hora_int_a_datetime(horario_teorico[1]))

    cant_horarios_posteriores = 0
    cont = 0
    for horario_posterior in islice(cycle(lista_horarios), index_horario + 1, None):
        cont += 1
        if horario_posterior[0] == horario_teorico[0]:
            cant_horarios_posteriores += 1
            horarios_cercanos.append(hora_int_a_datetime(horario_posterior[1]))
        if cant_horarios_posteriores == 2 or cont == 10000:
            break

    index_eliminar = []

    for index in range(0, len(horarios_cercanos) - 1):
        index_siguiente = index + 1
        actual = hora_a_segundos(horarios_cercanos[index])
        siguiente = hora_a_segundos(horarios_cercanos[index_siguiente])
        if siguiente < actual:
            actual = actual - 86400
        if abs(siguiente - actual) > 5400:
            index_eliminar.append(index)

    for index in reversed(index_eliminar):
        del horarios_cercanos[index]

    return calcular_promedio_diferencias(horarios_cercanos)


def agregar_desviacion(
    res_parcial_avenida,
    nombre_avenida,
    cod_parada,
    cod_variante,
    desviacion,
    linea_empresa,
):
    if nombre_avenida in res_parcial_avenida:
        if cod_parada in res_parcial_avenida[nombre_avenida]:
            if cod_variante in res_parcial_avenida[nombre_avenida][cod_parada]:
                res_parcial_avenida[nombre_avenida][cod_parada][cod_variante][0] = (
                    res_parcial_avenida[nombre_avenida][cod_parada][cod_variante][0]
                    * res_parcial_avenida[nombre_avenida][cod_parada][cod_variante][1]
                    + desviacion
                ) / (
                    res_parcial_avenida[nombre_avenida][cod_parada][cod_variante][1] + 1
                )
                res_parcial_avenida[nombre_avenida][cod_parada][cod_variante][1] += 1
            else:
                res_parcial_avenida[nombre_avenida][cod_parada][cod_variante] = [
                    desviacion,
                    1,
                    linea_empresa,
                ]  # desviacion,cantidad,linea y empresa
        else:
            res_parcial_avenida[nombre_avenida][cod_parada] = {}
            res_parcial_avenida[nombre_avenida][cod_parada][cod_variante] = [
                desviacion,
                1,
                linea_empresa,
            ]  # desviacion,cantidad,linea y empresa
    else:
        res_parcial_avenida[nombre_avenida] = {}
        res_parcial_avenida[nombre_avenida][cod_parada] = {}
        res_parcial_avenida[nombre_avenida][cod_parada][cod_variante] = [
            desviacion,
            1,
            linea_empresa,
        ]  # desviacion,cantidad,linea y empresa

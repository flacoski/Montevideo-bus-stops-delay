import datetime
from config import *

UNA_HORA = 3600
UN_DIA_EN_SEGUNDOS = 86400
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
    if PANDEMIA:
        if tipo_dia_teorico != 0:
            return None
    else:
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


def obtener_dia_semana(horario_real):
    formato_fecha = "%Y-%m-%dT%H:%M:%S.%f%z"
    fecha_completa = datetime.datetime.strptime(horario_real, formato_fecha)
    dia_numero = fecha_completa.date().weekday()
    if dia_numero < 5:
        return "Semana"
    else:
        return "Fin de Semana"


def obtener_franja_horaria(horario_real):
    formato_fecha = "%Y-%m-%dT%H:%M:%S.%f%z"
    fecha_completa = datetime.datetime.strptime(horario_real, formato_fecha)
    hora = fecha_completa.time().hour
    if hora >= 7 and hora < 9 or hora >= 12 and hora < 14 or hora >= 16 and hora < 19:
        return "Horas pico 7-9,12-14,16-19"
    elif hora >= 6 and hora < 24:
        return "Horas tranquilas"
    else:
        return "Madrugada 0-6"

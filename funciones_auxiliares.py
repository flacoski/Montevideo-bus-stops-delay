from datetime import datetime

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


def comparar_horarios(horario_real, horario_teorico, frecuencia):
    tipo_dia_teorico = horario_teorico[0]
    hora_teorica = horario_teorico[1]
    formato_fecha = "%Y-%m-%dT%H:%M:%S.%f%z"
    fecha_completa = datetime.strptime(horario_real, formato_fecha)
    # caso borde entre tipos de dia
    if tipo_dia(fecha_completa.date()) != tipo_dia_teorico:
        return None
    return comparar_horas(fecha_completa.time(), hora_teorica, frecuencia)


def comparar_horas(fecha_hora_real_string, hora_completa_teorica, frecuencia): 
    desviacion = hora_a_segundos(
         hora_int_a_datetime(hora_completa_teorica)) - hora_a_segundos(fecha_hora_real_string)
    if desviacion > frecuencia*2/3 or desviacion < -frecuencia/3:
        return None
    else:
        return desviacion

def hora_int_a_datetime(hora_int):
    formato_hora = "%H:%M:%S"
    minutos_teoricos = int(hora_int % 100)
    hora_teorica = int((hora_int - minutos_teoricos) / 100)
    return datetime.strptime(str(hora_teorica) + ":" + str(minutos_teoricos) + ":00", formato_hora).time()



def hora_a_segundos(hora_datetime):
    return(hora_datetime.hour * 60 + hora_datetime.minute) * 60 + hora_datetime.second
import datetime
import pdb
import numpy as np
import matplotlib.pyplot as plt

RUTAS_ARCHIVO_VIAJES = [
    "datos/viajes/viajes_stm_052022.csv",
]


def obtener_histograma():
    formato_fecha = "%Y-%m-%dT%H:%M:%S.%f%z"
    cantidad_viajes_por_dia = np.zeros((24,), dtype=int)
    for ruta_archivo in RUTAS_ARCHIVO_VIAJES:
        archivo_viajes = open(ruta_archivo)
        viajes = archivo_viajes.readlines()
        archivo_viajes.close()
        viajes = viajes[1:]
        for _viaje in viajes:
            viaje = _viaje.split(",")
            fecha_completa = datetime.datetime.strptime(viaje[2], formato_fecha)
            hora = fecha_completa.time().hour
            cantidad_viajes_por_dia[hora] += 1
        print(cantidad_viajes_por_dia)
    plt.bar(np.arange(len(cantidad_viajes_por_dia)), cantidad_viajes_por_dia)
    plt.savefig("histograma/histograma.png")


if __name__ == "__main__":
    obtener_histograma()

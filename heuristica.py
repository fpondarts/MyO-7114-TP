import csv
from math import radians, cos, sin, asin, sqrt

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def procesarDatos():

 	votantes_procesados = {}
 	
 	votantes_file = open('data/votantes_reducido.csv')
 	centros_file = open('data/centros_reducido.csv')
 	
 	votantes_csv = csv.reader(votantes_file, delimiter=",")
 	centros_csv = csv.reader(centros_file, delimiter=",")
 	next(votantes_csv)

 	for votante_actual in votantes_csv:

 		centros_procesados = []
 		centros_file.seek(1)
 		next(centros_csv)

 		for centro_actual in centros_csv:
 			distancia = haversine(float(votante_actual[1]), float(votante_actual[2]), float(centro_actual[1]), float(centro_actual[2]))
 			tupla=(int(centro_actual[0]), distancia)
 			centros_procesados.append(tupla)

 		votantes_procesados[int(votante_actual[0])] = sorted(centros_procesados, key=lambda x: x[1])

 	return votantes_procesados

def asignarCentrosDeVotacion(diccionario_votantes, ids_votantes):
	centros_asignados = {}

	for id_votante in ids_votantes:
		#Extraigo de la lista el centro mas cercano o sea el primero
		centro_cercano = diccionario_votantes[id_votante].pop(0)
		if centro_cercano[0] not in centros_asignados:
			centros_asignados[centro_cercano[0]] = [id_votante]
		else:
			centros_asignados[centro_cercano[0]].append(id_votante)
		#Vuelo a meter el centro que extraido pero al final de la lista
		diccionario_votantes[id_votante].append(centro_cercano)
	
	return centros_asignados

def filtrarCentrosInvalidos(centros):
	centros_invalidos = {}
	ids_centros = centros.keys()

	for id_centro in ids_centros:
		if len(centros[id_centro]) < 120:
			centros_invalidos[id_centro] = centros[id_centro]
	return centros_invalidos

def filtrarCentrosValidos(centros):
	centros_validos = {}
	ids_centros = centros.keys()

	for id_centro in ids_centros:
		if len(centros[id_centro]) >= 120:
			centros_validos[id_centro] = centros[id_centro]
	return centros_validos


def fusionarVotantesInvalidos(centros_invalidos):
	votantes_ids = []
	ids_centros = centros_invalidos.keys()
	for id_centro in ids_centros:
		votantes_ids += centros_invalidos[id_centro]
	return votantes_ids

def filtrarCentros(centros_del_votante, ids_centros_validos):
	return filter(lambda c: c[0] in ids_centros_validos, centros_del_votante)

def filtrarCentrosInvalidosDeLosVotantes(ids_votantes, ids_centros_validos, diccionario_votantes): 
	for id_votante in ids_votantes:
		diccionario_votantes[id_votante] = list(filtrarCentros(diccionario_votantes[id_votante], list(ids_centros_validos)))


def heuristica():
	centros_abiertos = {}
	centros_invalidos = {}

	diccionario_votantes = procesarDatos()
	ids_votantes = diccionario_votantes.keys()

	for cant_centros in range(1,31):
		centros_invalidos.clear()
		centros_elegidos = asignarCentrosDeVotacion(diccionario_votantes, ids_votantes)
		centros_invalidos.update(filtrarCentrosInvalidos(centros_elegidos))
		centros_abiertos.update(filtrarCentrosValidos(centros_elegidos))
		ids_votantes = fusionarVotantesInvalidos(centros_invalidos)

	filtrarCentrosInvalidosDeLosVotantes(ids_votantes, centros_abiertos.keys(), diccionario_votantes)
	centros_validos_asignados = asignarCentrosDeVotacion(diccionario_votantes, ids_votantes)

	for centro_id in centros_abiertos.keys():
		centros_abiertos[centro_id] += centros_validos_asignados[centro_id] 

	#Se imprimen los resultados finales
	print('Resultados finales\n')
	ids_centros = centros_abiertos.keys()
	for i in ids_centros:
		print("centro", i, "votantes:", len(centros_abiertos[i]), "\n")


heuristica()
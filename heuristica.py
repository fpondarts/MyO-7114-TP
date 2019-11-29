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


def procesarCentros():
 	centros_procesados = {}
 	centros_file = open('data/centros_reducido.csv')
 	centros_csv = csv.reader(centros_file, delimiter=",")
 	next(centros_csv)
 	for centro_actual in centros_csv:
 		centros_procesados[int(centro_actual[0])] = int(centro_actual[3])
 	return centros_procesados


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


def asignarCentrosDeVotacion(diccionario_votantes, ids_votantes, diccionario_centros):
	centros_asignados = {}

	for id_votante in ids_votantes:
		#Extraigo de la lista el centro mas cercano o sea el primero
		centros_votante = diccionario_votantes[id_votante]
		cont = 0
		for centro_actual in centros_votante:
			if centro_actual[0] not in centros_asignados:
				centros_asignados[centro_actual[0]] = [id_votante]
				centros_votante.pop(cont)
				centros_votante.append(centro_actual)
				cont+=1		
				break
			elif len(centros_asignados[centro_actual[0]]) < diccionario_centros[centro_actual[0]]:
				centros_asignados[centro_actual[0]].append(id_votante)
				centros_votante.pop(cont)
				centros_votante.append(centro_actual)
				cont+=1
				break
			else:
				centros_votante.pop(cont)
				cont+=1	
	
	return centros_asignados

def filtrarCentrosInvalidos(centros):
	centros_invalidos = {}
	ids_centros = centros.keys()

	for id_centro in ids_centros:
		if len(centros[id_centro]) < 30:
			centros_invalidos[id_centro] = centros[id_centro]
	return centros_invalidos

def filtrarCentrosValidos(centros):
	centros_validos = {}
	ids_centros = centros.keys()

	for id_centro in ids_centros:
		if len(centros[id_centro]) >= 30:
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

def actualizarDisponibilidadCentrosAbiertos(centros_validos, diccionario_centros):
	centros_ids = centros_validos.keys()
	for id in centros_ids:
		diccionario_centros[id] -= len(centros_validos[id])

def actualizarVotantesDeCentrosAbiertos(centros_abiertos, centros_validos):
	centros_validos_ids = centros_validos.keys()
	for id in centros_validos_ids:
		if id not in centros_abiertos:
			centros_abiertos[id] = centros_validos[id]
		else:
			centros_abiertos[id] += centros_validos[id]

def calcularDistanciaPromedio(diccionario_votantes, centros_abiertos):
	distanciaTotal = 0
	centros_ids = centros_abiertos.keys()
	for id in centros_ids:
		lista_votantes = centros_abiertos[id]
		for votante in lista_votantes:
			centro_votado = list(filter(lambda t: t[0] == id, diccionario_votantes[votante]))
			distanciaTotal += centro_votado[0][1]
	return distanciaTotal/len(diccionario_votantes)

def distanciaMaximaRecorrida(diccionario_votantes, centros_abiertos):
	distanciaMax = 0
	centros_ids = centros_abiertos.keys()
	for id in centros_ids:
		lista_votantes = centros_abiertos[id]
		for votante in lista_votantes:
			centro_votado = list(filter(lambda t: t[0] == id, diccionario_votantes[votante]))
			if distanciaMax < centro_votado[0][1]:
				distanciaMax = centro_votado[0][1]
	return distanciaMax

def centroConMenosVotantes(diccionario_centros):
	minimo = 10000
	centro_min = -1
	for centro in diccionario_centros:
		votantes = len(diccionario_centros[centro])
		if votantes < minimo:
			minimo = votantes
			centro_min = centro
	return centro_min			

def vacantesDisponibles(centros_elegidos,id_centro,diccionario_centros):
	vacantes = 0
	for centro in centros_elegidos:
		if centro == id_centro:
			continue
		vacantes += diccionario_centros[centro]
	return vacantes

def centroDisponibleMasCercano(votante,dict_votantes,id_centro,centros_elegidos,dict_centros):
	elegido = -1
	for tupla in dict_votantes[votante]:
		centro = tupla[0]
		if id_centro == centro:
			continue
		if (centro in centros_elegidos) and dict_centros[centro] > 0:
			elegido = centro
			break
	return elegido

def getDistanciaVotante(votante,diccionario_votantes,centro):
	for tupla_centro in diccionario_votantes[votante]:
		if tupla_centro[0] == centro:
			return tupla_centro[1]

def obtenerMejorReubicacion(diccionario_votantes,centros_elegidos,id_centro,diccionario_centros):
	id_votante = -1
	centro_votante = -1
	minima = 10000
	for centro in centros_elegidos:
		if (centro == id_centro) or (diccionario_centros[centro] == 0): 
			continue
		for votante in centros_elegidos[centro]:
			dist = getDistanciaVotante(votante,diccionario_votantes,centro)
			if dist < minima:
				minima = dist
				id_votante = votante
				centro_votante = centro
	return id_votante, centro_votante

def heuristica():
	centros_abiertos = {}
	centros_invalidos = {}

	diccionario_centros = procesarCentros()
	diccionario_votantes = procesarDatos()
	ids_votantes = diccionario_votantes.keys()

	for cant_centros in range(1,31):
		centros_invalidos.clear()
		centros_elegidos = asignarCentrosDeVotacion(diccionario_votantes, ids_votantes, diccionario_centros)
		centros_invalidos.update(filtrarCentrosInvalidos(centros_elegidos))
		centros_validos = filtrarCentrosValidos(centros_elegidos)
		actualizarDisponibilidadCentrosAbiertos(centros_validos, diccionario_centros)
		actualizarVotantesDeCentrosAbiertos(centros_abiertos, centros_validos)
		ids_votantes = fusionarVotantesInvalidos(centros_invalidos)

	filtrarCentrosInvalidosDeLosVotantes(ids_votantes, centros_abiertos.keys(), diccionario_votantes)
	centros_validos_asignados = asignarCentrosDeVotacion(diccionario_votantes, ids_votantes, diccionario_centros)

	for centro_id in centros_validos_asignados.keys():
		centros_abiertos[centro_id] += centros_validos_asignados[centro_id] 

	#Se imprimen los resultados finales
	print('Resultados finales\n')
	ids_centros = centros_abiertos.keys()
	for i in ids_centros:
		print("centro", i, "votantes:", len(centros_abiertos[i]), "\n")


	distanciaProm = calcularDistanciaPromedio(diccionario_votantes, centros_abiertos)
	distanciaMax = distanciaMaximaRecorrida(diccionario_votantes, centros_abiertos)

	print("distancia promedio:", distanciaProm)
	print("distancia maxima recorrida:", distanciaMax)
	print("Total:", distanciaMax + distanciaProm)


def heuristica_fix():
	centros_abiertos = {}
	centros_invalidos = {}

	caso_particular = False

	diccionario_centros = procesarCentros()
	diccionario_votantes = procesarDatos()
	ids_votantes = diccionario_votantes.keys()

	centros_elegidos = asignarCentrosDeVotacion(diccionario_votantes, ids_votantes, diccionario_centros)

	centros_invalidos.update(filtrarCentrosInvalidos(centros_elegidos))
	actualizarDisponibilidadCentrosAbiertos(centros_elegidos, diccionario_centros)

	while len(centros_invalidos) > 0:
		id_centro = centroConMenosVotantes(centros_invalidos)
		cantidad_de_votantes = len(centros_invalidos[id_centro])
		vacantes_disponibles = vacantesDisponibles(centros_elegidos,id_centro,diccionario_centros)

		if (cantidad_de_votantes > vacantes_disponibles):
			print("Vacantes disponibles: "+str(vacantesDisponibles))
			print("Votantes: " + str(cantidad_de_votantes))
			caso_particular = True
			break

		for votante in centros_invalidos[id_centro]:
			centro = centroDisponibleMasCercano(votante,diccionario_votantes,id_centro,centros_elegidos,diccionario_centros)
			centros_elegidos[centro].append(votante)
			diccionario_centros[centro] -= 1

		centros_invalidos.clear()
		del centros_elegidos[id_centro]
		centros_invalidos.update(filtrarCentrosInvalidos(centros_elegidos))


	if caso_particular:
		while len(centros_elegidos[id_centro]) < 30:
			id_votante,centro_votante = obtenerMejorReubicacion(diccionario_votantes,centros_elegidos,id_centro,diccionario_centros)
			centros_elegidos[id_centro].append(id_votante)
			centros_elegidos[centro_votante].remove(id_votante)
			diccionario_centros[centro_votante]-=1
			diccionario_centros[id_centro]+=1

			

	total = 0
	for centro in centros_elegidos:
		cantidad = len(centros_elegidos[centro])
		print("Centro " +str(centro) + ": "+str(cantidad) +" votantes")
		total+=cantidad
	print("Total votantes " + str(total))

	distanciaProm = calcularDistanciaPromedio(diccionario_votantes, centros_elegidos)
	distanciaMax = distanciaMaximaRecorrida(diccionario_votantes, centros_elegidos)

	print("distancia promedio:", distanciaProm)
	print("distancia maxima recorrida:", distanciaMax)
	print("Total:", distanciaMax + distanciaProm)


heuristica()

print("************FIN HEURISTICA***********")
heuristica_fix()